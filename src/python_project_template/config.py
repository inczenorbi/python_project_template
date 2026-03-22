"""Configuration loader supporting environment variables, .env files, and defaults.

Configuration is loaded once on startup in priority order:
1. Environment variables
2. .env file (if present)
3. Hardcoded defaults

Example:
    config = AppConfig.from_env()
    print(config.debug)  # True if DEBUG=1 in env, .env, or default
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    """Application configuration with environment variable support.

    Attributes:
        debug: Enable debug mode (defaults to False).
        log_level: Logging level such as "DEBUG", "INFO", "WARNING", "ERROR".
        log_format: Format for structured logs: "json" or "plain" (defaults to "plain").
        environment: Deployment environment: "dev", "test", "prod" (defaults to "dev").
    """

    debug: bool = False
    log_level: str = "INFO"
    log_format: str = "plain"
    environment: str = "dev"

    @classmethod
    def from_env(cls) -> AppConfig:
        """Load configuration from environment variables and .env file.

        Priority (highest to lowest):
        1. Environment variables (e.g., DEBUG=1)
        2. .env file in project root (if present)
        3. Hardcoded defaults in this method

        Returns:
            Populated AppConfig instance.
        """
        # Load .env if present (manual parsing to avoid external deps in core)
        env_vars: dict[str, str] = {}
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, value = line.split("=", 1)
                        env_vars[key.strip()] = value.strip()

        # Environment variables override .env
        env_vars.update(os.environ)

        return cls(
            debug=env_vars.get("DEBUG", "").lower() in ("1", "true", "yes"),
            log_level=env_vars.get("LOG_LEVEL", "INFO").upper(),
            log_format=env_vars.get("LOG_FORMAT", "plain").lower(),
            environment=env_vars.get("ENVIRONMENT", "dev").lower(),
        )


# Global config instance (loaded once on module import)
config: AppConfig | None = None


def get_config() -> AppConfig:
    """Get or create the global application config.

    Returns:
        Cached AppConfig instance.
    """
    global config
    if config is None:
        config = AppConfig.from_env()
    return config

