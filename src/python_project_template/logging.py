"""Structured logging configuration with JSON and plain text formatters.

Provides setup functions to configure the standard library logging module with:
- Configurable log level from environment (DEBUG, INFO, WARNING, ERROR)
- Optional JSON formatter for structured logs
- Optional plain text formatter with timestamps

Example:
    from python_project_template.logging import setup_logging
    logger = setup_logging(__name__)
    logger.info("Application started", extra={"version": "1.0.0"})
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Any


def setup_logging(
    name: str,
    level: str = "INFO",
    json_format: bool = False,
) -> logging.Logger:
    """Configure and return a logger with optional JSON formatting.

    Args:
        name: Logger name (typically __name__ of the module).
        level: Log level as string: "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL".
        json_format: If True, use JSON formatter; else use plain text.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level.upper())

    # Remove existing handlers to avoid duplication
    logger.handlers = []

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level.upper())

    # Choose formatter
    if json_format:
        formatter = _JSONFormatter()
    else:
        formatter = _PlainFormatter()

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


class _PlainFormatter(logging.Formatter):
    """Plain text formatter with timestamp and level."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as plain text.

        Args:
            record: LogRecord instance.

        Returns:
            Formatted log message.
        """
        return (
            f"[{record.levelname:8s}] {record.name:25s} | "
            f"{record.getMessage()}"
        )


class _JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging.

    Outputs logs as single-line JSON for easy parsing by log aggregation systems.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: LogRecord instance.

        Returns:
            JSON-formatted log message.
        """
        log_obj: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        # Add any extra fields from the record
        for key, value in record.__dict__.items():
            if (
                key not in (
                    "name",
                    "msg",
                    "args",
                    "created",
                    "levelname",
                    "levelno",
                    "pathname",
                    "filename",
                    "module",
                    "lineno",
                    "funcName",
                    "process",
                    "processName",
                    "thread",
                    "threadName",
                    "exc_info",
                    "exc_text",
                    "stack_info",
                    "relativeCreated",
                    "getMessage",
                    "message",
                )
                and not key.startswith("_")
            ):
                log_obj[key] = value

        return json.dumps(log_obj)

