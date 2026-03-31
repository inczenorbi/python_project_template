"""Core Ralph loop execution engine."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from python_project_template.ralph.config import RalphConfig, RalphConfigurationError
from python_project_template.ralph.models import (
    ExecutionArtifact,
    PromptArtifact,
    RalphSession,
    RalphTask,
    Requirement,
    TaskCriterion,
)
from python_project_template.ralph.prompt_templates import (
    build_decompose_messages,
    build_discover_messages,
    build_execute_messages,
    build_prompt_pack_messages,
    build_refine_messages,
    build_summarize_messages,
)
from python_project_template.ralph.provider import ChatProvider


class RalphEngineError(RuntimeError):
    """Base engine error."""


class PhaseValidationError(RalphEngineError):
    """Raised when a phase returns invalid JSON or invalid semantics."""


class IterationLimitError(RalphEngineError):
    """Raised when refinement or prompt generation exceeds the iteration
    cap."""


@dataclass(slots=True)
class _TaskBundle:
    tasks: list[RalphTask]
    execution_order: list[str]
    learnings: list[str]


def _utc_now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _slugify(value: str, *, fallback: str = "session", limit: int = 48) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return (slug[:limit] or fallback).strip("-") or fallback


def _strip_code_fences(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            return "\n".join(lines[1:-1]).strip()
    return text


def _ensure_list_of_strings(value: Any, *, field_name: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise PhaseValidationError(f"'{field_name}' must be a list of strings.")
    return value


def _atomicity_issues(task: RalphTask) -> list[str]:
    issues: list[str] = []
    if len(task.title.split()) > 12:
        issues.append(f"{task.id} title is too long for an atomic task.")
    if len(task.criteria) > 5:
        issues.append(f"{task.id} has too many pass/fail criteria for a single atomic task.")
    if not task.objective.endswith("."):
        issues.append(f"{task.id} objective should be a single concrete sentence.")
    return issues


class _ArtifactStore:
    """Persist Ralph outputs incrementally so failed runs still leave
    artifacts."""

    def __init__(self, root_dir: Path) -> None:
        self.root_dir = root_dir
        self.prompts_dir = self.root_dir / "prompts"
        self.executions_dir = self.root_dir / "executions"
        self.prompts_dir.mkdir(parents=True, exist_ok=True)
        self.executions_dir.mkdir(parents=True, exist_ok=True)
        self.events_path = self.root_dir / "event-log.jsonl"

    def write_brief(
        self,
        *,
        goal: str,
        constraints: str | None,
        context_documents: list[dict[str, str]],
    ) -> None:
        sections = ["# Ralph Brief", "", "## Goal", goal]
        if constraints:
            sections.extend(["", "## Constraints", constraints])
        if context_documents:
            sections.extend(["", "## Context Files"])
            for document in context_documents:
                sections.append(f"- `{document['path']}`")
        (self.root_dir / "brief.md").write_text("\n".join(sections) + "\n", encoding="utf-8")

    def append_event(
        self,
        *,
        phase: str,
        status: str,
        message: str,
        payload: dict[str, object] | None = None,
    ) -> None:
        entry = {
            "timestamp": _utc_now(),
            "phase": phase,
            "status": status,
            "message": message,
            "payload": payload or {},
        }
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=True) + "\n")

    def write_session(self, session: RalphSession) -> None:
        (self.root_dir / "session.json").write_text(
            json.dumps(session.to_dict(), indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )

    def write_backlog(self, session: RalphSession) -> None:
        payload = {
            "title": session.title,
            "project_type": session.project_type,
            "requirements": [requirement.to_dict() for requirement in session.requirements],
            "tasks": [task.to_dict() for task in session.tasks],
            "execution_order": session.execution_order,
        }
        (self.root_dir / "backlog.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )

    def write_prompts(self, artifacts: list[PromptArtifact]) -> None:
        for artifact in artifacts:
            lines = [
                f"# {artifact.title}",
                "",
                f"- Task ID: `{artifact.task_id}`",
                (
                    "- Dependencies: "
                    f"{', '.join(artifact.dependencies) if artifact.dependencies else 'None'}"
                ),
                "",
                "## Prompt",
                artifact.prompt,
                "",
                "## Success Criteria",
            ]
            lines.extend(f"- {criterion}" for criterion in artifact.success_criteria)
            (self.prompts_dir / artifact.filename).write_text(
                "\n".join(lines) + "\n",
                encoding="utf-8",
            )

    def write_execution_reports(self, artifacts: list[ExecutionArtifact]) -> None:
        for artifact in artifacts:
            lines = [
                f"# {artifact.title}",
                "",
                f"- Task ID: `{artifact.task_id}`",
                "",
                "## Summary",
                artifact.summary,
                "",
                "## Changed Files",
            ]
            lines.extend(f"- `{path}`" for path in artifact.changed_files or ["No files reported."])
            lines.extend(["", "## Tests Run"])
            lines.extend(
                f"- `{command}`" for command in artifact.tests_run or ["No tests reported."]
            )
            if artifact.notes:
                lines.extend(["", "## Notes"])
                lines.extend(f"- {note}" for note in artifact.notes)
            (self.executions_dir / artifact.filename).write_text(
                "\n".join(lines) + "\n",
                encoding="utf-8",
            )

    def write_summary(self, session: RalphSession) -> None:
        lines = [
            f"# {session.title or 'Ralph Summary'}",
            "",
            "## Executive Summary",
            session.executive_summary or "Not available.",
            "",
            "## Implementation Sequence",
        ]
        lines.extend(f"- {item}" for item in session.execution_order or ["Not available."])
        lines.extend(["", "## Risks"])
        lines.extend(f"- {risk}" for risk in session.risks or ["No additional risks recorded."])
        lines.extend(["", "## Handoff Notes"])
        lines.extend(
            f"- {note}" for note in session.handoff_notes or ["No handoff notes recorded."]
        )
        if session.execution_artifacts:
            lines.extend(["", "## Implemented Tasks"])
            lines.extend(
                f"- {artifact.task_id}: {artifact.summary}"
                for artifact in session.execution_artifacts
            )
        if session.failure_reason:
            lines.extend(["", "## Failure", session.failure_reason])
        (self.root_dir / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


class RalphEngine:
    """Autonomous planning loop that produces a project prompt pack."""

    def __init__(self, *, provider: ChatProvider, config: RalphConfig, logger: Any) -> None:
        self._provider = provider
        self._config = config
        self._logger = logger
        self.latest_output_dir: Path | None = None

    def run(
        self,
        *,
        goal: str,
        constraints: str | None = None,
        context_files: list[Path] | None = None,
        execute_tasks: bool = True,
    ) -> RalphSession:
        context_files = context_files or []
        context_documents = self._load_context_documents(context_files)
        session = self._create_session(
            goal=goal,
            constraints=constraints,
            context_files=context_files,
        )
        store = _ArtifactStore(Path(session.output_dir))
        self.latest_output_dir = Path(session.output_dir)
        store.write_brief(goal=goal, constraints=constraints, context_documents=context_documents)
        store.write_session(session)
        store.append_event(phase="bootstrap", status="ok", message="Session created.")

        try:
            self._run_session(
                session=session,
                store=store,
                context_documents=context_documents,
                execute_tasks=execute_tasks,
            )
            return session
        except Exception as exc:
            self._fail_session(session=session, store=store, error=exc)
            raise

    def resume(self, *, session_dir: Path, execute_tasks: bool = True) -> RalphSession:
        session_path = session_dir / "session.json"
        if not session_path.exists():
            raise RalphEngineError(f"Session file not found: {session_path}")

        payload = json.loads(session_path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RalphEngineError("session.json must contain a JSON object.")

        session = RalphSession.from_dict(payload)
        session.output_dir = str(session_dir)
        session.status = "running"
        session.failure_reason = None
        session.completed_at = None

        store = _ArtifactStore(session_dir)
        self.latest_output_dir = session_dir
        context_documents = self._load_existing_context_documents(session)
        store.write_session(session)
        store.append_event(
            phase="resume",
            status="ok",
            message="Resuming Ralph session from saved artifacts.",
            payload={"session_id": session.session_id},
        )

        try:
            self._run_session(
                session=session,
                store=store,
                context_documents=context_documents,
                execute_tasks=execute_tasks,
            )
            return session
        except Exception as exc:
            self._fail_session(session=session, store=store, error=exc)
            raise

    def _create_session(
        self,
        *,
        goal: str,
        constraints: str | None,
        context_files: list[Path],
    ) -> RalphSession:
        started_at = _utc_now()
        session_slug = _slugify(goal)
        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        output_dir = self._config.output_dir / f"{timestamp}-{session_slug}"
        output_dir.mkdir(parents=True, exist_ok=True)

        return RalphSession(
            session_id=f"{timestamp}-{session_slug}",
            started_at=started_at,
            goal=goal,
            constraints=constraints,
            context_files=[str(path) for path in context_files],
            output_dir=str(output_dir),
            status="running",
            model=self._config.model or "",
            temperature=self._config.temperature,
            max_iterations=self._config.max_iterations,
        )

    def _load_context_documents(self, context_files: list[Path]) -> list[dict[str, str]]:
        documents: list[dict[str, str]] = []
        for path in context_files:
            content = path.read_text(encoding="utf-8", errors="replace")
            documents.append({"path": str(path), "content": content[:4000]})
        return documents

    def _load_existing_context_documents(self, session: RalphSession) -> list[dict[str, str]]:
        paths = [Path(path) for path in session.context_files]
        existing_paths = [path for path in paths if path.exists()]
        return self._load_context_documents(existing_paths)

    def _run_session(
        self,
        *,
        session: RalphSession,
        store: _ArtifactStore,
        context_documents: list[dict[str, str]],
        execute_tasks: bool,
    ) -> None:
        if not session.requirements or not session.title or not session.project_type:
            self._run_discover_phase(
                session=session,
                context_documents=context_documents,
                store=store,
            )
        if not session.tasks:
            self._run_decompose_phase(session=session, store=store)
        self._run_refine_loop(session=session, store=store)
        self._run_prompt_pack_loop(session=session, store=store)
        if execute_tasks:
            self._run_implementation_loop(
                session=session,
                store=store,
                context_documents=context_documents,
            )
        self._run_summarize_phase(session=session, store=store)
        session.status = "completed"
        session.completed_at = _utc_now()
        store.write_summary(session)
        store.write_session(session)
        store.append_event(phase="complete", status="ok", message="Ralph loop completed.")

    def _fail_session(
        self,
        *,
        session: RalphSession,
        store: _ArtifactStore,
        error: Exception,
    ) -> None:
        session.status = "failed"
        session.failure_reason = str(error)
        session.completed_at = _utc_now()
        store.write_summary(session)
        store.write_session(session)
        store.append_event(
            phase="failure",
            status="error",
            message="Ralph loop failed.",
            payload={"error": str(error)},
        )

    def _run_discover_phase(
        self,
        *,
        session: RalphSession,
        context_documents: list[dict[str, str]],
        store: _ArtifactStore,
    ) -> None:
        response = self._call_phase(
            phase="discover",
            messages=build_discover_messages(
                goal=session.goal,
                constraints=session.constraints,
                context_documents=context_documents,
            ),
        )
        payload = self._parse_json_payload(response, phase="discover")
        requirements_payload = payload.get("requirements")
        if not isinstance(requirements_payload, list) or not requirements_payload:
            raise PhaseValidationError("discover.requirements must be a non-empty list.")

        session.title = self._require_string(payload, "title", phase="discover")
        session.project_type = self._require_string(payload, "project_type", phase="discover")
        session.requirements = []
        for item in requirements_payload:
            if not isinstance(item, dict):
                raise PhaseValidationError("discover.requirements entries must be objects.")
            session.requirements.append(
                Requirement(
                    id=self._require_string(item, "id", phase="discover.requirements"),
                    title=self._require_string(item, "title", phase="discover.requirements"),
                    description=self._require_string(
                        item,
                        "description",
                        phase="discover.requirements",
                    ),
                )
            )
        session.success_definition = _ensure_list_of_strings(
            payload.get("success_definition"),
            field_name="discover.success_definition",
        )
        session.assumptions = _ensure_list_of_strings(
            payload.get("assumptions"),
            field_name="discover.assumptions",
        )
        session.risks = _ensure_list_of_strings(payload.get("risks"), field_name="discover.risks")
        session.learnings.extend(
            _ensure_list_of_strings(payload.get("learnings"), field_name="discover.learnings")
        )
        self._logger.info(
            "Discover phase completed",
            extra={"requirements": len(session.requirements)},
        )
        store.write_session(session)
        store.append_event(
            phase="discover",
            status="ok",
            message="Discovered project requirements.",
            payload={"requirements": len(session.requirements)},
        )

    def _run_decompose_phase(self, *, session: RalphSession, store: _ArtifactStore) -> None:
        response = self._call_phase(
            phase="decompose",
            messages=build_decompose_messages(
                title=session.title,
                goal=session.goal,
                constraints=session.constraints,
                requirements=session.requirements,
                learnings=session.learnings,
            ),
        )
        bundle = self._parse_task_bundle(
            response=response,
            phase="decompose",
            requirements=session.requirements,
        )
        session.tasks = bundle.tasks
        session.execution_order = bundle.execution_order
        session.learnings.extend(bundle.learnings)
        store.write_backlog(session)
        store.write_session(session)
        store.append_event(
            phase="decompose",
            status="ok",
            message="Created initial task backlog.",
            payload={"tasks": len(session.tasks)},
        )

    def _run_refine_loop(self, *, session: RalphSession, store: _ArtifactStore) -> None:
        uncovered, issues = self._task_validation_issues(session.tasks, session.requirements)
        while uncovered or issues:
            if session.iterations >= session.max_iterations:
                raise IterationLimitError(
                    "Ralph loop hit the iteration cap before producing a valid backlog."
                )

            session.iterations += 1
            response = self._call_phase(
                phase="refine",
                messages=build_refine_messages(
                    goal=session.goal,
                    requirements=session.requirements,
                    tasks=session.tasks,
                    uncovered_requirement_ids=uncovered,
                    issues=issues,
                    learnings=session.learnings,
                ),
            )
            bundle = self._parse_task_bundle(
                response=response,
                phase="refine",
                requirements=session.requirements,
            )
            session.tasks = bundle.tasks
            session.execution_order = bundle.execution_order
            session.learnings.extend(bundle.learnings)
            uncovered, issues = self._task_validation_issues(session.tasks, session.requirements)
            store.write_backlog(session)
            store.write_session(session)
            store.append_event(
                phase="refine",
                status="ok",
                message="Refined task backlog.",
                payload={"iteration": session.iterations, "remaining_issues": len(issues)},
            )

    def _run_prompt_pack_loop(self, *, session: RalphSession, store: _ArtifactStore) -> None:
        artifacts = {artifact.task_id: artifact for artifact in session.prompt_artifacts}
        prompt_attempts = 0
        missing_task_ids = [task.id for task in session.tasks if task.id not in artifacts]

        while missing_task_ids:
            if prompt_attempts >= session.max_iterations:
                raise IterationLimitError(
                    "Ralph loop hit the iteration cap before generating prompts for every task."
                )

            batch_size = min(
                len(missing_task_ids),
                max(2, -(-len(session.tasks) // session.max_iterations)),
            )
            current_batch_ids = set(missing_task_ids[:batch_size])
            missing_tasks = [task for task in session.tasks if task.id in current_batch_ids]
            response = self._call_phase(
                phase="prompt_pack",
                messages=build_prompt_pack_messages(
                    title=session.title,
                    goal=session.goal,
                    tasks=missing_tasks,
                    existing_artifacts=list(artifacts.values()),
                ),
            )
            prompt_attempts += 1
            parsed_artifacts, learnings = self._parse_prompt_artifacts(response, missing_tasks)
            for artifact in parsed_artifacts:
                artifact.filename = self._artifact_filename(
                    task_id=artifact.task_id,
                    tasks=session.tasks,
                )
                artifacts[artifact.task_id] = artifact
            session.learnings.extend(learnings)
            session.prompt_artifacts = sorted(artifacts.values(), key=lambda item: item.filename)
            store.write_prompts(session.prompt_artifacts)
            store.write_session(session)

            missing_task_ids = [task.id for task in session.tasks if task.id not in artifacts]
            store.append_event(
                phase="prompt_pack",
                status="ok",
                message="Generated implementation prompts.",
                payload={
                    "prompt_attempts": prompt_attempts,
                    "batch_size": len(missing_tasks),
                    "generated_prompts": len(parsed_artifacts),
                    "remaining": len(missing_task_ids),
                },
            )

    def _run_implementation_loop(
        self,
        *,
        session: RalphSession,
        store: _ArtifactStore,
        context_documents: list[dict[str, str]],
    ) -> None:
        if not self._provider.supports_task_execution():
            raise RalphConfigurationError(
                "Selected provider cannot execute implementation tasks. "
                "Use the codex provider or rerun Ralph with --plan-only."
            )

        prompt_map = {artifact.task_id: artifact for artifact in session.prompt_artifacts}
        reports = {artifact.task_id: artifact for artifact in session.execution_artifacts}
        task_map = {task.id: task for task in session.tasks}
        ordered_task_ids = self._ordered_task_ids(session)

        for task_id in ordered_task_ids:
            if task_id in reports:
                continue

            task = task_map[task_id]
            if task_id not in prompt_map:
                raise PhaseValidationError(f"Missing prompt artifact for task {task_id}.")

            dependency_reports = [
                reports[dependency] for dependency in task.dependencies if dependency in reports
            ]
            response = self._call_phase(
                phase="implement",
                messages=build_execute_messages(
                    goal=session.goal,
                    constraints=session.constraints,
                    task=task,
                    artifact=prompt_map[task_id],
                    completed_dependencies=dependency_reports,
                    context_documents=context_documents,
                ),
            )
            report = self._parse_execution_artifact(
                response=response,
                task=task,
            )
            report.filename = self._execution_filename(task_id=task.id, tasks=session.tasks)
            reports[task_id] = report
            session.execution_artifacts = [
                reports[ordered_id] for ordered_id in ordered_task_ids if ordered_id in reports
            ]
            store.write_execution_reports(session.execution_artifacts)
            store.write_session(session)
            store.append_event(
                phase="implement",
                status="ok",
                message="Implemented task in workspace.",
                payload={
                    "task_id": task_id,
                    "changed_files": len(report.changed_files),
                    "tests_run": len(report.tests_run),
                },
            )

    def _run_summarize_phase(self, *, session: RalphSession, store: _ArtifactStore) -> None:
        response = self._call_phase(
            phase="summarize",
            messages=build_summarize_messages(
                title=session.title,
                goal=session.goal,
                requirements=session.requirements,
                tasks=session.tasks,
                artifacts=session.prompt_artifacts,
                execution_artifacts=session.execution_artifacts,
                learnings=session.learnings,
            ),
        )
        payload = self._parse_json_payload(response, phase="summarize")
        session.executive_summary = self._require_string(
            payload,
            "executive_summary",
            phase="summarize",
        )
        session.risks = _ensure_list_of_strings(
            payload.get("key_risks"),
            field_name="summarize.key_risks",
        )
        session.execution_order = _ensure_list_of_strings(
            payload.get("implementation_sequence"),
            field_name="summarize.implementation_sequence",
        )
        session.handoff_notes = _ensure_list_of_strings(
            payload.get("handoff_notes"),
            field_name="summarize.handoff_notes",
        )
        store.write_summary(session)
        store.write_session(session)
        store.append_event(
            phase="summarize",
            status="ok",
            message="Created Ralph session summary.",
        )

    def _call_phase(self, *, phase: str, messages: list[Any]) -> str:
        self._logger.info("Calling Ralph phase", extra={"phase": phase})
        return self._provider.complete(
            messages=messages,
            model=self._config.model,
            temperature=self._config.temperature,
        )

    def _parse_json_payload(self, raw_text: str, *, phase: str) -> dict[str, Any]:
        cleaned = _strip_code_fences(raw_text)
        try:
            payload = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise PhaseValidationError(f"{phase} phase returned invalid JSON.") from exc
        if not isinstance(payload, dict):
            raise PhaseValidationError(f"{phase} phase must return a JSON object.")
        return payload

    def _parse_task_bundle(
        self,
        *,
        response: str,
        phase: str,
        requirements: list[Requirement],
    ) -> _TaskBundle:
        payload = self._parse_json_payload(response, phase=phase)
        tasks_payload = payload.get("tasks")
        if not isinstance(tasks_payload, list) or not tasks_payload:
            raise PhaseValidationError(f"{phase}.tasks must be a non-empty list.")

        tasks: list[RalphTask] = []
        for item in tasks_payload:
            if not isinstance(item, dict):
                raise PhaseValidationError(f"{phase}.tasks entries must be objects.")
            criteria_payload = item.get("criteria")
            if not isinstance(criteria_payload, list) or not criteria_payload:
                raise PhaseValidationError(f"{phase}.criteria must be a non-empty list.")

            criteria: list[TaskCriterion] = []
            for criterion in criteria_payload:
                if not isinstance(criterion, dict):
                    raise PhaseValidationError(f"{phase}.criteria entries must be objects.")
                criteria.append(
                    TaskCriterion(
                        id=self._require_string(criterion, "id", phase=f"{phase}.criteria"),
                        description=self._require_string(
                            criterion,
                            "description",
                            phase=f"{phase}.criteria",
                        ),
                    )
                )

            task = RalphTask(
                id=self._require_string(item, "id", phase=phase),
                title=self._require_string(item, "title", phase=phase),
                objective=self._require_string(item, "objective", phase=phase),
                deliverable=self._require_string(item, "deliverable", phase=phase),
                criteria=criteria,
                dependencies=_ensure_list_of_strings(
                    item.get("dependencies"),
                    field_name=f"{phase}.dependencies",
                ),
                covers=_ensure_list_of_strings(item.get("covers"), field_name=f"{phase}.covers"),
            )
            tasks.append(task)

        execution_order = _ensure_list_of_strings(
            payload.get("execution_order"),
            field_name=f"{phase}.execution_order",
        )
        requirement_ids = {requirement.id for requirement in requirements}
        task_ids = {task.id for task in tasks}
        if len(task_ids) != len(tasks):
            raise PhaseValidationError(f"{phase} produced duplicate task ids.")
        for task in tasks:
            unknown_requirements = sorted(set(task.covers) - requirement_ids)
            if unknown_requirements:
                raise PhaseValidationError(
                    f"{phase} task {task.id} covers unknown requirements: {unknown_requirements}"
                )
            unknown_dependencies = sorted(set(task.dependencies) - task_ids)
            if unknown_dependencies:
                raise PhaseValidationError(
                    f"{phase} task {task.id} depends on unknown tasks: {unknown_dependencies}"
                )

        learnings = _ensure_list_of_strings(
            payload.get("learnings"),
            field_name=f"{phase}.learnings",
        )
        return _TaskBundle(tasks=tasks, execution_order=execution_order, learnings=learnings)

    def _parse_prompt_artifacts(
        self,
        response: str,
        tasks: list[RalphTask],
    ) -> tuple[list[PromptArtifact], list[str]]:
        payload = self._parse_json_payload(response, phase="prompt_pack")
        artifacts_payload = payload.get("artifacts")
        if not isinstance(artifacts_payload, list) or not artifacts_payload:
            raise PhaseValidationError("prompt_pack.artifacts must be a non-empty list.")

        task_map = {task.id: task for task in tasks}
        artifacts: list[PromptArtifact] = []
        for item in artifacts_payload:
            if not isinstance(item, dict):
                raise PhaseValidationError("prompt_pack.artifacts entries must be objects.")
            task_id = self._require_string(item, "task_id", phase="prompt_pack")
            if task_id not in task_map:
                raise PhaseValidationError(f"prompt_pack returned unknown task_id {task_id}.")
            filename_index = len(artifacts) + 1
            artifact = PromptArtifact(
                task_id=task_id,
                title=self._require_string(item, "title", phase="prompt_pack"),
                filename=f"{filename_index:02d}-{_slugify(task_map[task_id].title)}.md",
                prompt=self._require_string(item, "prompt", phase="prompt_pack"),
                success_criteria=_ensure_list_of_strings(
                    item.get("success_criteria"),
                    field_name="prompt_pack.success_criteria",
                ),
                dependencies=_ensure_list_of_strings(
                    item.get("dependencies"),
                    field_name="prompt_pack.dependencies",
                ),
            )
            artifacts.append(artifact)

        learnings = _ensure_list_of_strings(
            payload.get("learnings"),
            field_name="prompt_pack.learnings",
        )
        return artifacts, learnings

    def _parse_execution_artifact(
        self,
        *,
        response: str,
        task: RalphTask,
    ) -> ExecutionArtifact:
        payload = self._parse_json_payload(response, phase="implement")
        task_id = self._require_string(payload, "task_id", phase="implement")
        if task_id != task.id:
            raise PhaseValidationError(
                f"implement returned task_id {task_id} but expected {task.id}."
            )
        title = self._require_string(payload, "title", phase="implement")
        summary = self._require_string(payload, "summary", phase="implement")
        return ExecutionArtifact(
            task_id=task_id,
            title=title,
            filename="",
            summary=summary,
            changed_files=_ensure_list_of_strings(
                payload.get("changed_files"),
                field_name="implement.changed_files",
            ),
            tests_run=_ensure_list_of_strings(
                payload.get("tests_run"),
                field_name="implement.tests_run",
            ),
            notes=_ensure_list_of_strings(
                payload.get("notes"),
                field_name="implement.notes",
            ),
        )

    def _task_validation_issues(
        self,
        tasks: list[RalphTask],
        requirements: list[Requirement],
    ) -> tuple[list[str], list[str]]:
        coverage_map = {requirement.id: False for requirement in requirements}
        issues: list[str] = []
        for task in tasks:
            if not task.covers:
                issues.append(f"{task.id} does not cover any requirement.")
            issues.extend(_atomicity_issues(task))
            for requirement_id in task.covers:
                if requirement_id in coverage_map:
                    coverage_map[requirement_id] = True
        uncovered = [
            requirement_id for requirement_id, covered in coverage_map.items() if not covered
        ]
        return uncovered, issues

    def _require_string(self, payload: dict[str, Any], key: str, *, phase: str) -> str:
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            raise PhaseValidationError(f"{phase}.{key} must be a non-empty string.")
        return value.strip()

    def _ordered_task_ids(self, session: RalphSession) -> list[str]:
        seen: set[str] = set()
        ordered_ids: list[str] = []
        for task_id in session.execution_order + [task.id for task in session.tasks]:
            if task_id in seen:
                continue
            if any(task.id == task_id for task in session.tasks):
                ordered_ids.append(task_id)
                seen.add(task_id)
        return ordered_ids

    def _artifact_filename(self, *, task_id: str, tasks: list[RalphTask]) -> str:
        for index, task in enumerate(tasks, start=1):
            if task.id == task_id:
                return f"{index:02d}-{_slugify(task.title)}.md"
        raise PhaseValidationError(f"Unknown task id for prompt artifact filename: {task_id}")

    def _execution_filename(self, *, task_id: str, tasks: list[RalphTask]) -> str:
        for index, task in enumerate(tasks, start=1):
            if task.id == task_id:
                return f"{index:02d}-{_slugify(task.title)}-execution.md"
        raise PhaseValidationError(f"Unknown task id for execution artifact filename: {task_id}")
