"""Tests for Ralph engine orchestration and artifact persistence."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import cast

import pytest

from python_project_template.ralph.config import RalphConfig
from python_project_template.ralph.engine import IterationLimitError, RalphEngine, _atomicity_issues
from python_project_template.ralph.models import (
    PromptArtifact,
    RalphSession,
    RalphTask,
    Requirement,
    TaskCriterion,
)
from tests.fakes import (
    SequencedProvider,
    refinement_needed_responses,
    stuck_refinement_responses,
    success_responses,
)


def _logger() -> logging.Logger:
    logger = logging.getLogger("ralph-test")
    logger.handlers = []
    logger.addHandler(logging.NullHandler())
    return logger


def _config(output_dir: Path, *, max_iterations: int = 3) -> RalphConfig:
    return RalphConfig(
        provider="codex",
        codex_command="codex",
        codex_oss=False,
        codex_local_provider=None,
        api_base_url="https://example.test/v1",
        api_key="test-key",
        model="test-model",
        temperature=0.2,
        timeout_seconds=30,
        max_iterations=max_iterations,
        output_dir=output_dir,
    )


def _seed_failed_session(session_dir: Path, *, include_first_prompt: bool = False) -> Path:
    responses = success_responses()
    discover_payload = cast(dict[str, object], responses["discover"][0])
    decompose_payload = cast(dict[str, object], responses["decompose"][0])
    prompt_pack_payload = cast(dict[str, object], responses["prompt_pack"][0])

    requirements = [
        Requirement.from_dict(item)
        for item in cast(list[dict[str, str]], discover_payload["requirements"])
    ]
    tasks = [
        RalphTask.from_dict(item)
        for item in cast(list[dict[str, object]], decompose_payload["tasks"])
    ]
    prompt_artifacts: list[PromptArtifact] = []
    if include_first_prompt:
        first_artifact = PromptArtifact.from_dict(
            cast(list[dict[str, object]], prompt_pack_payload["artifacts"])[0]
        )
        first_artifact.filename = "01-define-information-architecture.md"
        prompt_artifacts.append(first_artifact)

    session = RalphSession(
        session_id="saved-session",
        started_at="2026-03-28T21:35:34Z",
        goal="Plan a B2B dashboard",
        constraints="Use reusable prompts only.",
        context_files=[],
        output_dir=str(session_dir),
        status="failed",
        model="",
        temperature=0.2,
        max_iterations=3,
        title=str(discover_payload["title"]),
        project_type=str(discover_payload["project_type"]),
        success_definition=[
            str(item) for item in cast(list[str], discover_payload["success_definition"])
        ],
        assumptions=[str(item) for item in cast(list[str], discover_payload["assumptions"])],
        risks=[str(item) for item in cast(list[str], discover_payload["risks"])],
        requirements=requirements,
        tasks=tasks,
        prompt_artifacts=prompt_artifacts,
        learnings=[str(item) for item in cast(list[str], discover_payload["learnings"])],
        execution_order=[
            str(item) for item in cast(list[str], decompose_payload["execution_order"])
        ],
        iterations=1,
        failure_reason="Codex CLI timed out while generating a Ralph phase response.",
    )
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "session.json").write_text(
        json.dumps(session.to_dict(), indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return session_dir


def test_engine_refines_and_persists_artifacts(tmp_path: Path) -> None:
    context_file = tmp_path / "context.md"
    context_file.write_text("Existing constraints and context.", encoding="utf-8")
    engine = RalphEngine(
        provider=SequencedProvider(refinement_needed_responses()),
        config=_config(tmp_path / "runs"),
        logger=_logger(),
    )

    session = engine.run(
        goal="Plan a B2B dashboard",
        constraints="Use reusable prompts only.",
        context_files=[context_file],
    )

    run_dir = Path(session.output_dir)
    assert session.status == "completed"
    assert session.iterations == 1
    assert (run_dir / "brief.md").exists()
    assert (run_dir / "summary.md").exists()
    assert (run_dir / "backlog.json").exists()
    assert (run_dir / "event-log.jsonl").exists()
    prompt_files = sorted((run_dir / "prompts").glob("*.md"))
    assert len(prompt_files) == 2

    backlog = json.loads((run_dir / "backlog.json").read_text(encoding="utf-8"))
    assert [task["id"] for task in backlog["tasks"]] == ["TASK-1", "TASK-2"]
    events = (run_dir / "event-log.jsonl").read_text(encoding="utf-8")
    assert '"phase": "refine"' in events


def test_engine_writes_failure_artifacts_on_iteration_cap(tmp_path: Path) -> None:
    engine = RalphEngine(
        provider=SequencedProvider(stuck_refinement_responses()),
        config=_config(tmp_path / "runs", max_iterations=1),
        logger=_logger(),
    )

    with pytest.raises(IterationLimitError):
        engine.run(goal="Plan a B2B dashboard")

    assert engine.latest_output_dir is not None
    run_dir = engine.latest_output_dir
    session_data = json.loads((run_dir / "session.json").read_text(encoding="utf-8"))
    assert session_data["status"] == "failed"
    assert "iteration cap" in session_data["failure_reason"]
    assert (run_dir / "summary.md").exists()


def test_atomicity_check_allows_compound_titles_when_scope_is_still_atomic() -> None:
    task = RalphTask(
        id="TASK-9",
        title="Strengthen Security and Dependency Hygiene",
        objective="Add practical security checks for the template.",
        deliverable="A hardened default security workflow.",
        criteria=[
            TaskCriterion(
                id="CRIT-1",
                description="Adds baseline security scanning to local and CI workflows.",
            )
        ],
        dependencies=[],
        covers=["REQ-12"],
    )

    assert _atomicity_issues(task) == []


def test_engine_resume_continues_from_saved_session(tmp_path: Path) -> None:
    session_dir = _seed_failed_session(tmp_path / "runs" / "saved-session")
    responses = success_responses()
    engine = RalphEngine(
        provider=SequencedProvider(
            {
                "prompt_pack": responses["prompt_pack"],
                "summarize": responses["summarize"],
            }
        ),
        config=_config(tmp_path / "runs"),
        logger=_logger(),
    )

    session = engine.resume(session_dir=session_dir)

    assert session.status == "completed"
    assert [artifact.task_id for artifact in session.prompt_artifacts] == ["TASK-1", "TASK-2"]
    assert session.executive_summary


def test_engine_resume_reuses_existing_prompt_artifacts(tmp_path: Path) -> None:
    session_dir = _seed_failed_session(
        tmp_path / "runs" / "saved-session-with-prompts",
        include_first_prompt=True,
    )
    responses = success_responses()
    engine = RalphEngine(
        provider=SequencedProvider(
            {
                "prompt_pack": [
                    {
                        "artifacts": [
                            cast(
                                list[dict[str, object]],
                                cast(dict[str, object], responses["prompt_pack"][0])["artifacts"],
                            )[1]
                        ],
                        "learnings": ["Completed the missing prompt only."],
                    }
                ],
                "summarize": responses["summarize"],
            }
        ),
        config=_config(tmp_path / "runs"),
        logger=_logger(),
    )

    session = engine.resume(session_dir=session_dir)

    assert session.status == "completed"
    assert [artifact.task_id for artifact in session.prompt_artifacts] == ["TASK-1", "TASK-2"]
