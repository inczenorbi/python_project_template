"""Configuration loading for runtime logging and Ralph loop settings."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _read_env_file() -> dict[str, str]:
    env_vars: dict[str, str] = {}
    env_file = Path(".env")
    if not env_file.exists():
        return env_vars

    with env_file.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            env_vars[key.strip()] = value.strip()

    return env_vars


def _parse_bool(value: str, *, default: bool = False) -> bool:
    if not value:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _parse_int(value: str, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@dataclass
class AppConfig:
    """Application configuration loaded from env vars and optional `.env`."""

    debug: bool = False
    log_level: str = "INFO"
    log_format: str = "plain"
    environment: str = "dev"
    ralph_provider: str = "codex"
    ralph_codex_command: str = "codex"
    ralph_codex_oss: bool = False
    ralph_codex_local_provider: str | None = None
    ralph_api_base_url: str = "https://api.openai.com/v1"
    ralph_api_key: str | None = None
    ralph_model: str | None = None
    ralph_timeout_seconds: int = 300
    ralph_max_iterations: int = 3
    ralph_output_dir: Path = Path("outputs") / "ralph"

    @classmethod
    def from_env(cls) -> AppConfig:
        """Load configuration from defaults, `.env`, and real env vars."""
        env_vars = _read_env_file()
        env_vars.update(os.environ)

        output_dir = env_vars.get("RALPH_OUTPUT_DIR", "outputs/ralph")
        codex_local_provider = env_vars.get("RALPH_CODEX_LOCAL_PROVIDER") or None
        return cls(
            debug=_parse_bool(env_vars.get("DEBUG", ""), default=False),
            log_level=env_vars.get("LOG_LEVEL", "INFO").upper(),
            log_format=env_vars.get("LOG_FORMAT", "plain").lower(),
            environment=env_vars.get("ENVIRONMENT", "dev").lower(),
            ralph_provider=env_vars.get("RALPH_PROVIDER", "codex").lower(),
            ralph_codex_command=env_vars.get("RALPH_CODEX_COMMAND", "codex").strip() or "codex",
            ralph_codex_oss=_parse_bool(env_vars.get("RALPH_CODEX_OSS", ""), default=False)
            or bool(codex_local_provider),
            ralph_codex_local_provider=codex_local_provider,
            ralph_api_base_url=env_vars.get(
                "RALPH_API_BASE_URL",
                "https://api.openai.com/v1",
            ).rstrip("/"),
            ralph_api_key=env_vars.get("RALPH_API_KEY") or None,
            ralph_model=env_vars.get("RALPH_MODEL") or None,
            ralph_timeout_seconds=_parse_int(
                env_vars.get("RALPH_TIMEOUT_SECONDS", ""),
                default=300,
            ),
            ralph_max_iterations=_parse_int(
                env_vars.get("RALPH_MAX_ITERATIONS", ""),
                default=3,
            ),
            ralph_output_dir=Path(output_dir),
        )


config: AppConfig | None = None


def get_config() -> AppConfig:
    """Get or create the cached application config."""
    global config
    if config is None:
        config = AppConfig.from_env()
    return config


def reset_config() -> None:
    """Clear the cached config for tests and CLI invocations."""
    global config
    config = None
