"""Configuration loading for runtime logging and Ralph loop settings."""

from __future__ import annotations

import os
import shutil
from collections.abc import Iterator
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


def _iter_codex_install_candidates(command_name: str) -> Iterator[Path]:
    """Yield likely Codex CLI install paths from VS Code extension directories."""

    executable_names = [command_name]
    if os.name == "nt" and not command_name.lower().endswith(".exe"):
        executable_names.insert(0, f"{command_name}.exe")

    roots = [
        Path.home() / ".vscode" / "extensions",
        Path.home() / ".vscode-insiders" / "extensions",
    ]
    for root in roots:
        if not root.exists():
            continue
        extension_dirs = sorted(
            root.glob("openai.chatgpt-*"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        for extension_dir in extension_dirs:
            bin_dir = extension_dir / "bin"
            if not bin_dir.exists():
                continue
            for executable_name in executable_names:
                for candidate in bin_dir.rglob(executable_name):
                    if candidate.is_file():
                        yield candidate


def _resolve_codex_command(value: str) -> str:
    """Resolve the codex command, recovering from stale absolute executable paths."""

    candidate = value.strip() or "codex"
    resolved = shutil.which(candidate)
    if resolved:
        return resolved

    candidate_path = Path(candidate)
    if candidate_path.exists():
        return str(candidate_path)

    if candidate_path.is_absolute():
        fallback = shutil.which(candidate_path.name)
        if fallback:
            return fallback
        discovered = next(_iter_codex_install_candidates(candidate_path.name), None)
        if discovered is not None:
            return str(discovered)
        return candidate

    if len(candidate_path.parts) == 1:
        discovered = next(_iter_codex_install_candidates(candidate_path.name), None)
        if discovered is not None:
            return str(discovered)

    return candidate


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
            ralph_codex_command=_resolve_codex_command(
                env_vars.get("RALPH_CODEX_COMMAND", "codex")
            ),
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
