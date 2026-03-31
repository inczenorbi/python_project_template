"""Prompt templates for the Ralph loop phases."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from python_project_template.ralph.models import ChatMessage, PromptArtifact, RalphTask, Requirement

_RALPH_SYSTEM_PROMPT = """You are Ralph, an autonomous project-planning engine.
Return JSON only with no markdown fences.
Follow the Ralph loop rules:
- Break work into atomic, single-purpose tasks.
- Every task must have explicit pass/fail criteria.
- Declare task dependencies by task id.
- Ensure every discovered requirement is covered by at least one task.
- Prefer concrete, implementation-ready output over general advice.
"""


def _to_pretty_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=True)


def _compact_artifact(artifact: PromptArtifact) -> dict[str, object]:
    return {
        "task_id": artifact.task_id,
        "title": artifact.title,
        "filename": artifact.filename,
        "success_criteria": artifact.success_criteria,
        "dependencies": artifact.dependencies,
    }


def build_discover_messages(
    *,
    goal: str,
    constraints: str | None,
    context_documents: list[dict[str, str]],
) -> list[ChatMessage]:
    """Create the discover phase prompt."""
    user_payload = {
        "phase": "discover",
        "goal": goal,
        "constraints": constraints or "",
        "context_documents": context_documents,
        "expected_schema": {
            "title": "string",
            "project_type": "string",
            "requirements": [{"id": "REQ-1", "title": "string", "description": "string"}],
            "success_definition": ["string"],
            "assumptions": ["string"],
            "risks": ["string"],
            "learnings": ["string"],
        },
    }
    return [
        ChatMessage(role="system", content=_RALPH_SYSTEM_PROMPT),
        ChatMessage(role="user", content=_to_pretty_json(user_payload)),
    ]


def build_decompose_messages(
    *,
    title: str,
    goal: str,
    constraints: str | None,
    requirements: list[Requirement],
    learnings: list[str],
) -> list[ChatMessage]:
    """Create the decompose phase prompt."""
    user_payload = {
        "phase": "decompose",
        "title": title,
        "goal": goal,
        "constraints": constraints or "",
        "requirements": [requirement.to_dict() for requirement in requirements],
        "learnings": learnings,
        "expected_schema": {
            "tasks": [
                {
                    "id": "TASK-1",
                    "title": "string",
                    "objective": "string",
                    "deliverable": "string",
                    "covers": ["REQ-1"],
                    "dependencies": ["TASK-0"],
                    "criteria": [{"id": "CRIT-1", "description": "string"}],
                }
            ],
            "execution_order": ["TASK-1"],
            "learnings": ["string"],
        },
    }
    return [
        ChatMessage(role="system", content=_RALPH_SYSTEM_PROMPT),
        ChatMessage(role="user", content=_to_pretty_json(user_payload)),
    ]


def build_refine_messages(
    *,
    goal: str,
    requirements: list[Requirement],
    tasks: list[RalphTask],
    uncovered_requirement_ids: list[str],
    issues: list[str],
    learnings: list[str],
) -> list[ChatMessage]:
    """Create the refine phase prompt."""
    user_payload = {
        "phase": "refine",
        "goal": goal,
        "requirements": [requirement.to_dict() for requirement in requirements],
        "tasks": [task.to_dict() for task in tasks],
        "uncovered_requirement_ids": uncovered_requirement_ids,
        "issues": issues,
        "learnings": learnings,
        "instruction": (
            "Rewrite the entire task list so all requirements are covered, all tasks are atomic, "
            "and all dependencies refer to valid task ids."
        ),
        "expected_schema": {
            "tasks": [
                {
                    "id": "TASK-1",
                    "title": "string",
                    "objective": "string",
                    "deliverable": "string",
                    "covers": ["REQ-1"],
                    "dependencies": ["TASK-0"],
                    "criteria": [{"id": "CRIT-1", "description": "string"}],
                }
            ],
            "execution_order": ["TASK-1"],
            "learnings": ["string"],
        },
    }
    return [
        ChatMessage(role="system", content=_RALPH_SYSTEM_PROMPT),
        ChatMessage(role="user", content=_to_pretty_json(user_payload)),
    ]


def build_prompt_pack_messages(
    *,
    title: str,
    goal: str,
    tasks: list[RalphTask],
    existing_artifacts: list[PromptArtifact],
) -> list[ChatMessage]:
    """Create the prompt-pack phase prompt."""
    user_payload = {
        "phase": "prompt_pack",
        "title": title,
        "goal": goal,
        "tasks": [task.to_dict() for task in tasks],
        "existing_artifacts": [artifact.task_id for artifact in existing_artifacts],
        "instruction": (
            "Produce one implementation prompt per task. "
            "Each prompt must include the task objective, "
            "deliverable, dependencies, and pass/fail criteria."
        ),
        "expected_schema": {
            "artifacts": [
                {
                    "task_id": "TASK-1",
                    "title": "string",
                    "prompt": "string",
                    "success_criteria": ["string"],
                    "dependencies": ["TASK-0"],
                }
            ],
            "learnings": ["string"],
        },
    }
    return [
        ChatMessage(role="system", content=_RALPH_SYSTEM_PROMPT),
        ChatMessage(role="user", content=_to_pretty_json(user_payload)),
    ]


def build_summarize_messages(
    *,
    title: str,
    goal: str,
    requirements: list[Requirement],
    tasks: list[RalphTask],
    artifacts: list[PromptArtifact],
    learnings: list[str],
) -> list[ChatMessage]:
    """Create the summarize phase prompt."""
    user_payload = {
        "phase": "summarize",
        "title": title,
        "goal": goal,
        "requirements": [requirement.to_dict() for requirement in requirements],
        "tasks": [task.to_dict() for task in tasks],
        "artifacts": [_compact_artifact(artifact) for artifact in artifacts],
        "learnings": learnings,
        "expected_schema": {
            "executive_summary": "string",
            "key_risks": ["string"],
            "implementation_sequence": ["TASK-1"],
            "handoff_notes": ["string"],
        },
    }
    return [
        ChatMessage(role="system", content=_RALPH_SYSTEM_PROMPT),
        ChatMessage(role="user", content=_to_pretty_json(user_payload)),
    ]
