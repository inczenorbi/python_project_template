"""Test doubles and canned Ralph responses."""

from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from python_project_template.ralph.models import ChatMessage


class SequencedProvider:
    """Return phase responses from an in-memory queue."""

    def __init__(self, responses: dict[str, list[dict[str, Any] | str]]) -> None:
        self._responses = {
            phase: [
                json.dumps(item) if isinstance(item, dict) else item for item in phase_responses
            ]
            for phase, phase_responses in deepcopy(responses).items()
        }
        self.calls: list[str] = []

    def complete(
        self,
        *,
        messages: list[ChatMessage],
        model: str | None,
        temperature: float,
    ) -> str:
        del model, temperature
        phase = json.loads(messages[-1].content)["phase"]
        self.calls.append(phase)
        phase_responses = self._responses.get(phase, [])
        if not phase_responses:
            raise AssertionError(f"No fake response configured for phase {phase}.")
        return phase_responses.pop(0)


def success_responses() -> dict[str, list[dict[str, Any] | str]]:
    """Return a fully valid Ralph loop response set."""
    return {
        "discover": [
            {
                "title": "B2B Dashboard Planner",
                "project_type": "web application",
                "requirements": [
                    {
                        "id": "REQ-1",
                        "title": "Plan the user experience",
                        "description": "Define the pages, states, and core user interactions.",
                    },
                    {
                        "id": "REQ-2",
                        "title": "Plan delivery mechanics",
                        "description": "Define deployment, release, and validation flow.",
                    },
                ],
                "success_definition": [
                    "The project brief is implementation-ready.",
                    "Each task has measurable pass/fail criteria.",
                ],
                "assumptions": ["The team already has product context."],
                "risks": ["Deployment assumptions may differ across environments."],
                "learnings": ["The project needs both UX and delivery coverage."],
            }
        ],
        "decompose": [
            {
                "tasks": [
                    {
                        "id": "TASK-1",
                        "title": "Define information architecture",
                        "objective": "Map the pages and user paths.",
                        "deliverable": "A page and user-flow brief.",
                        "covers": ["REQ-1"],
                        "dependencies": [],
                        "criteria": [
                            {
                                "id": "CRIT-1",
                                "description": "Lists every primary page and state.",
                            },
                            {
                                "id": "CRIT-2",
                                "description": "Defines the main user journey end to end.",
                            },
                        ],
                    },
                    {
                        "id": "TASK-2",
                        "title": "Draft deployment workflow",
                        "objective": "Specify hosting and release automation.",
                        "deliverable": "A deployment-ready release plan.",
                        "covers": ["REQ-2"],
                        "dependencies": ["TASK-1"],
                        "criteria": [
                            {
                                "id": "CRIT-3",
                                "description": "Identifies the target hosting model.",
                            },
                            {
                                "id": "CRIT-4",
                                "description": "Lists release validation steps before deploy.",
                            },
                        ],
                    },
                ],
                "execution_order": ["TASK-1", "TASK-2"],
                "learnings": ["Two atomic tasks are enough for the first pass."],
            }
        ],
        "prompt_pack": [
            {
                "artifacts": [
                    {
                        "task_id": "TASK-1",
                        "title": "Implementation Prompt: Information Architecture",
                        "prompt": (
                            "Create the information architecture for the dashboard. "
                            "Define pages, states, and user paths before any UI build."
                        ),
                        "success_criteria": [
                            "Every primary page is listed.",
                            "The critical user path is explicit.",
                        ],
                        "dependencies": [],
                    },
                    {
                        "task_id": "TASK-2",
                        "title": "Implementation Prompt: Deployment Workflow",
                        "prompt": (
                            "Design the deployment workflow. "
                            "Describe hosting, release validation, and rollout sequencing."
                        ),
                        "success_criteria": [
                            "Hosting and release automation are specified.",
                            "Pre-release validation steps are included.",
                        ],
                        "dependencies": ["TASK-1"],
                    },
                ],
                "learnings": ["Prompt pack is ready for handoff."],
            }
        ],
        "summarize": [
            {
                "executive_summary": (
                    "The project is decomposed into two implementation-ready prompts."
                ),
                "key_risks": ["Release assumptions need validation in the target environment."],
                "implementation_sequence": ["TASK-1", "TASK-2"],
                "handoff_notes": ["Start with the architecture prompt before delivery planning."],
            }
        ],
    }


def refinement_needed_responses() -> dict[str, list[dict[str, Any] | str]]:
    """Return responses that require one refine pass before succeeding."""
    responses = success_responses()
    responses["decompose"] = [
        {
            "tasks": [
                {
                    "id": "TASK-1",
                    "title": "Design app and api",
                    "objective": "Cover the full product scope.",
                    "deliverable": "One broad project plan.",
                    "covers": ["REQ-1"],
                    "dependencies": [],
                    "criteria": [
                        {
                            "id": "CRIT-1",
                            "description": "Mentions the product scope.",
                        }
                    ],
                }
            ],
            "execution_order": ["TASK-1"],
            "learnings": ["The first pass is too broad."],
        }
    ]
    responses["refine"] = success_responses()["decompose"]
    return responses


def stuck_refinement_responses() -> dict[str, list[dict[str, Any] | str]]:
    """Return responses that remain invalid after refinement."""
    invalid_backlog = {
        "tasks": [
            {
                "id": "TASK-1",
                "title": "Design app and api",
                "objective": "Cover the full product scope.",
                "deliverable": "One broad project plan.",
                "covers": ["REQ-1"],
                "dependencies": [],
                "criteria": [
                    {
                        "id": "CRIT-1",
                        "description": "Mentions the product scope.",
                    }
                ],
            }
        ],
        "execution_order": ["TASK-1"],
        "learnings": ["The backlog is still broad."],
    }
    return {
        "discover": success_responses()["discover"],
        "decompose": [invalid_backlog],
        "refine": [invalid_backlog],
    }
