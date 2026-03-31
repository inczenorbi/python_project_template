"""Data models used across Ralph loop execution."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import cast


def _string_list(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _dict_list(value: object) -> list[dict[str, object]]:
    if not isinstance(value, list):
        return []
    return [cast(dict[str, object], item) for item in value if isinstance(item, dict)]


def _optional_string(value: object) -> str | None:
    if value is None:
        return None
    return str(value)


def _float_value(value: object, *, default: float = 0.0) -> float:
    if isinstance(value, bool):
        return float(default)
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        return float(value)
    return float(default)


def _int_value(value: object, *, default: int = 0) -> int:
    if isinstance(value, bool):
        return int(default)
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        return int(value)
    return int(default)


@dataclass(slots=True)
class ChatMessage:
    """A single chat message for a provider request."""

    role: str
    content: str


@dataclass(slots=True)
class Requirement:
    """A project requirement discovered from the brief."""

    id: str
    title: str
    description: str

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> Requirement:
        return cls(
            id=str(payload["id"]),
            title=str(payload["title"]),
            description=str(payload["description"]),
        )


@dataclass(slots=True)
class TaskCriterion:
    """A measurable pass/fail criterion for a Ralph task."""

    id: str
    description: str

    def to_dict(self) -> dict[str, str]:
        return {
            "id": self.id,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, payload: Mapping[str, object]) -> TaskCriterion:
        return cls(
            id=str(payload["id"]),
            description=str(payload["description"]),
        )


@dataclass(slots=True)
class RalphTask:
    """A single atomic implementation task."""

    id: str
    title: str
    objective: str
    deliverable: str
    criteria: list[TaskCriterion]
    dependencies: list[str] = field(default_factory=list)
    covers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "title": self.title,
            "objective": self.objective,
            "deliverable": self.deliverable,
            "criteria": [criterion.to_dict() for criterion in self.criteria],
            "dependencies": list(self.dependencies),
            "covers": list(self.covers),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> RalphTask:
        return cls(
            id=str(payload["id"]),
            title=str(payload["title"]),
            objective=str(payload["objective"]),
            deliverable=str(payload["deliverable"]),
            criteria=[
                TaskCriterion.from_dict(criterion)
                for criterion in _dict_list(payload.get("criteria"))
            ],
            dependencies=_string_list(payload.get("dependencies")),
            covers=_string_list(payload.get("covers")),
        )


@dataclass(slots=True)
class PromptArtifact:
    """A generated implementation prompt for a task."""

    task_id: str
    title: str
    filename: str
    prompt: str
    success_criteria: list[str]
    dependencies: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "filename": self.filename,
            "prompt": self.prompt,
            "success_criteria": list(self.success_criteria),
            "dependencies": list(self.dependencies),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> PromptArtifact:
        return cls(
            task_id=str(payload["task_id"]),
            title=str(payload["title"]),
            filename=str(payload.get("filename", "")),
            prompt=str(payload["prompt"]),
            success_criteria=_string_list(payload.get("success_criteria")),
            dependencies=_string_list(payload.get("dependencies")),
        )


@dataclass(slots=True)
class ExecutionArtifact:
    """A persisted implementation report for an executed task."""

    task_id: str
    title: str
    filename: str
    summary: str
    changed_files: list[str] = field(default_factory=list)
    tests_run: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "task_id": self.task_id,
            "title": self.title,
            "filename": self.filename,
            "summary": self.summary,
            "changed_files": list(self.changed_files),
            "tests_run": list(self.tests_run),
            "notes": list(self.notes),
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> ExecutionArtifact:
        return cls(
            task_id=str(payload["task_id"]),
            title=str(payload["title"]),
            filename=str(payload.get("filename", "")),
            summary=str(payload["summary"]),
            changed_files=_string_list(payload.get("changed_files")),
            tests_run=_string_list(payload.get("tests_run")),
            notes=_string_list(payload.get("notes")),
        )


@dataclass(slots=True)
class RalphSession:
    """Execution state and persisted results for a Ralph run."""

    session_id: str
    started_at: str
    goal: str
    constraints: str | None
    context_files: list[str]
    output_dir: str
    status: str
    model: str
    temperature: float
    max_iterations: int
    title: str = ""
    project_type: str = ""
    success_definition: list[str] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    requirements: list[Requirement] = field(default_factory=list)
    tasks: list[RalphTask] = field(default_factory=list)
    prompt_artifacts: list[PromptArtifact] = field(default_factory=list)
    execution_artifacts: list[ExecutionArtifact] = field(default_factory=list)
    learnings: list[str] = field(default_factory=list)
    execution_order: list[str] = field(default_factory=list)
    executive_summary: str = ""
    handoff_notes: list[str] = field(default_factory=list)
    iterations: int = 0
    completed_at: str | None = None
    failure_reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "goal": self.goal,
            "constraints": self.constraints,
            "context_files": list(self.context_files),
            "output_dir": self.output_dir,
            "status": self.status,
            "model": self.model,
            "temperature": self.temperature,
            "max_iterations": self.max_iterations,
            "title": self.title,
            "project_type": self.project_type,
            "success_definition": list(self.success_definition),
            "assumptions": list(self.assumptions),
            "risks": list(self.risks),
            "requirements": [requirement.to_dict() for requirement in self.requirements],
            "tasks": [task.to_dict() for task in self.tasks],
            "prompt_artifacts": [artifact.to_dict() for artifact in self.prompt_artifacts],
            "execution_artifacts": [artifact.to_dict() for artifact in self.execution_artifacts],
            "learnings": list(self.learnings),
            "execution_order": list(self.execution_order),
            "executive_summary": self.executive_summary,
            "handoff_notes": list(self.handoff_notes),
            "iterations": self.iterations,
            "failure_reason": self.failure_reason,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, object]) -> RalphSession:
        return cls(
            session_id=str(payload["session_id"]),
            started_at=str(payload["started_at"]),
            goal=str(payload["goal"]),
            constraints=_optional_string(payload.get("constraints")),
            context_files=_string_list(payload.get("context_files")),
            output_dir=str(payload["output_dir"]),
            status=str(payload["status"]),
            model=str(payload.get("model", "")),
            temperature=_float_value(payload.get("temperature"), default=0.2),
            max_iterations=_int_value(payload.get("max_iterations"), default=1),
            title=str(payload.get("title", "")),
            project_type=str(payload.get("project_type", "")),
            success_definition=_string_list(payload.get("success_definition")),
            assumptions=_string_list(payload.get("assumptions")),
            risks=_string_list(payload.get("risks")),
            requirements=[
                Requirement.from_dict(item) for item in _dict_list(payload.get("requirements"))
            ],
            tasks=[RalphTask.from_dict(item) for item in _dict_list(payload.get("tasks"))],
            prompt_artifacts=[
                PromptArtifact.from_dict(item)
                for item in _dict_list(payload.get("prompt_artifacts"))
            ],
            execution_artifacts=[
                ExecutionArtifact.from_dict(item)
                for item in _dict_list(payload.get("execution_artifacts"))
            ],
            learnings=_string_list(payload.get("learnings")),
            execution_order=_string_list(payload.get("execution_order")),
            executive_summary=str(payload.get("executive_summary", "")),
            handoff_notes=_string_list(payload.get("handoff_notes")),
            iterations=_int_value(payload.get("iterations"), default=0),
            completed_at=_optional_string(payload.get("completed_at")),
            failure_reason=_optional_string(payload.get("failure_reason")),
        )
