"""CLI tests for the Ralph workflow."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from python_project_template import main as main_module
from python_project_template.ralph.models import RalphSession, RalphTask, Requirement, TaskCriterion
from tests.fakes import (
    SequencedProvider,
    refinement_needed_responses,
    stuck_refinement_responses,
    success_responses,
)

runner = CliRunner()


def _set_default_env(monkeypatch, output_dir: Path) -> None:
    monkeypatch.setenv("RALPH_PROVIDER", "codex")
    monkeypatch.setenv("RALPH_OUTPUT_DIR", str(output_dir))


def _write_failed_session(session_dir: Path) -> Path:
    session = RalphSession(
        session_id="saved-session",
        started_at="2026-03-28T21:35:34Z",
        goal="Plan a B2B dashboard",
        constraints=None,
        context_files=[],
        output_dir=str(session_dir),
        status="failed",
        model="",
        temperature=0.2,
        max_iterations=3,
        title="B2B Dashboard Planner",
        project_type="web application",
        success_definition=["The project brief is implementation-ready."],
        assumptions=["The team already has product context."],
        risks=["Deployment assumptions may differ across environments."],
        requirements=[
            Requirement(
                id="REQ-1",
                title="Plan the user experience",
                description="Define the pages, states, and core user interactions.",
            ),
            Requirement(
                id="REQ-2",
                title="Plan delivery mechanics",
                description="Define deployment, release, and validation flow.",
            ),
        ],
        tasks=[
            RalphTask(
                id="TASK-1",
                title="Define information architecture",
                objective="Map the pages and user paths.",
                deliverable="A page and user-flow brief.",
                criteria=[
                    TaskCriterion(
                        id="CRIT-1",
                        description="Lists every primary page and state.",
                    )
                ],
                covers=["REQ-1"],
            ),
            RalphTask(
                id="TASK-2",
                title="Draft deployment workflow",
                objective="Specify hosting and release automation.",
                deliverable="A deployment-ready release plan.",
                criteria=[
                    TaskCriterion(
                        id="CRIT-2",
                        description="Lists release validation steps before deploy.",
                    )
                ],
                dependencies=["TASK-1"],
                covers=["REQ-2"],
            ),
        ],
        learnings=["The project needs both UX and delivery coverage."],
        execution_order=["TASK-1", "TASK-2"],
        iterations=1,
        failure_reason="Codex CLI timed out while generating a Ralph phase response.",
    )
    session_dir.mkdir(parents=True, exist_ok=True)
    (session_dir / "session.json").write_text(
        json.dumps(session.to_dict(), indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return session_dir


def test_cli_run_success(monkeypatch, tmp_path: Path) -> None:
    _set_default_env(monkeypatch, tmp_path / "default-root")
    monkeypatch.setattr(
        main_module,
        "build_provider",
        lambda config: SequencedProvider(success_responses()),
    )

    result = runner.invoke(
        main_module.app,
        ["run", "--goal", "Plan a B2B dashboard", "--output-dir", str(tmp_path / "custom-root")],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Ralph loop completed:" in result.output
    created_dirs = [path for path in (tmp_path / "custom-root").iterdir() if path.is_dir()]
    assert len(created_dirs) == 1
    assert (created_dirs[0] / "session.json").exists()


def test_cli_run_requires_api_config_for_openai_provider(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("RALPH_PROVIDER", "openai")
    monkeypatch.delenv("RALPH_API_KEY", raising=False)
    monkeypatch.delenv("RALPH_MODEL", raising=False)
    monkeypatch.setenv("RALPH_OUTPUT_DIR", str(tmp_path / "default-root"))

    result = runner.invoke(
        main_module.app,
        ["run", "--goal", "Plan a B2B dashboard"],
        catch_exceptions=False,
    )

    assert result.exit_code == 2
    assert "RALPH_API_KEY is required" in result.output


def test_cli_run_handles_malformed_provider_output(monkeypatch, tmp_path: Path) -> None:
    _set_default_env(monkeypatch, tmp_path / "default-root")
    monkeypatch.setattr(
        main_module,
        "build_provider",
        lambda config: SequencedProvider({"discover": ["not json"]}),
    )

    result = runner.invoke(
        main_module.app,
        ["run", "--goal", "Plan a B2B dashboard", "--output-dir", str(tmp_path / "malformed-root")],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "Ralph loop failed" in result.output
    created_dirs = [path for path in (tmp_path / "malformed-root").iterdir() if path.is_dir()]
    assert len(created_dirs) == 1
    session_data = json.loads((created_dirs[0] / "session.json").read_text(encoding="utf-8"))
    assert session_data["status"] == "failed"


def test_cli_run_exits_on_iteration_cap(monkeypatch, tmp_path: Path) -> None:
    _set_default_env(monkeypatch, tmp_path / "default-root")
    monkeypatch.setattr(
        main_module,
        "build_provider",
        lambda config: SequencedProvider(stuck_refinement_responses()),
    )

    result = runner.invoke(
        main_module.app,
        [
            "run",
            "--goal",
            "Plan a B2B dashboard",
            "--output-dir",
            str(tmp_path / "failure-root"),
            "--max-iterations",
            "1",
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 1
    assert "iteration cap" in result.output


def test_cli_run_uses_custom_output_directory(monkeypatch, tmp_path: Path) -> None:
    _set_default_env(monkeypatch, tmp_path / "default-root")
    monkeypatch.setattr(
        main_module,
        "build_provider",
        lambda config: SequencedProvider(refinement_needed_responses()),
    )
    context_file = tmp_path / "context.md"
    context_file.write_text("extra context", encoding="utf-8")
    output_root = tmp_path / "chosen-root"

    result = runner.invoke(
        main_module.app,
        [
            "run",
            "--goal",
            "Plan a B2B dashboard",
            "--output-dir",
            str(output_root),
            "--context-file",
            str(context_file),
        ],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    session_dirs = [path for path in output_root.iterdir() if path.is_dir()]
    assert len(session_dirs) == 1
    assert session_dirs[0].is_relative_to(output_root)


def test_cli_dry_run_defaults_to_codex_without_model(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("RALPH_API_KEY", raising=False)
    monkeypatch.delenv("RALPH_MODEL", raising=False)
    monkeypatch.setenv("RALPH_PROVIDER", "codex")
    monkeypatch.setenv("RALPH_OUTPUT_DIR", str(tmp_path / "default-root"))

    result = runner.invoke(
        main_module.app,
        ["run", "--goal", "Plan a B2B dashboard", "--dry-run"],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Provider: codex" in result.output
    assert "Model: <auto>" in result.output


def test_cli_resume_continues_failed_session(monkeypatch, tmp_path: Path) -> None:
    _set_default_env(monkeypatch, tmp_path / "default-root")
    monkeypatch.setattr(
        main_module,
        "build_provider",
        lambda config: SequencedProvider(
            {
                "prompt_pack": success_responses()["prompt_pack"],
                "summarize": success_responses()["summarize"],
            }
        ),
    )
    session_dir = _write_failed_session(tmp_path / "saved-session")

    result = runner.invoke(
        main_module.app,
        ["resume", str(session_dir)],
        catch_exceptions=False,
    )

    assert result.exit_code == 0
    assert "Ralph loop resumed:" in result.output
    session_data = json.loads((session_dir / "session.json").read_text(encoding="utf-8"))
    assert session_data["status"] == "completed"
