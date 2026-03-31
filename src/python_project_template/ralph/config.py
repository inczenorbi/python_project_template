"""Configuration types for the Ralph loop runtime."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class RalphConfigurationError(ValueError):
    """Raised when Ralph runtime configuration is invalid."""


@dataclass(slots=True)
class RalphConfig:
    """Resolved runtime configuration for a Ralph loop session."""

    provider: str
    codex_command: str
    codex_oss: bool
    codex_local_provider: str | None
    api_base_url: str
    api_key: str | None
    model: str | None
    temperature: float
    timeout_seconds: int
    max_iterations: int
    output_dir: Path

    def validate(self) -> None:
        """Validate configuration required to execute the loop."""
        errors: list[str] = []
        if self.provider not in {"codex", "openai"}:
            errors.append("RALPH_PROVIDER must be either 'codex' or 'openai'.")
        if self.provider == "codex":
            if not self.codex_command:
                errors.append("RALPH_CODEX_COMMAND is required for the codex provider.")
        if self.provider == "openai":
            if not self.api_base_url:
                errors.append("RALPH_API_BASE_URL is required.")
            if not self.api_key:
                errors.append("RALPH_API_KEY is required.")
            if not self.model:
                errors.append("Provide --model or set RALPH_MODEL for the openai provider.")
        if self.timeout_seconds <= 0:
            errors.append("RALPH_TIMEOUT_SECONDS must be a positive integer.")
        if self.max_iterations <= 0:
            errors.append("RALPH_MAX_ITERATIONS must be a positive integer.")
        if not 0.0 <= self.temperature <= 2.0:
            errors.append("Temperature must be between 0.0 and 2.0.")

        if errors:
            raise RalphConfigurationError(" ".join(errors))

    def masked_dict(self) -> dict[str, object]:
        """Return config values safe to print or persist."""
        return {
            "provider": self.provider,
            "codex_command": self.codex_command,
            "codex_oss": self.codex_oss,
            "codex_local_provider": self.codex_local_provider,
            "api_base_url": self.api_base_url,
            "api_key_present": bool(self.api_key),
            "model": self.model,
            "temperature": self.temperature,
            "timeout_seconds": self.timeout_seconds,
            "max_iterations": self.max_iterations,
            "output_dir": str(self.output_dir),
        }
