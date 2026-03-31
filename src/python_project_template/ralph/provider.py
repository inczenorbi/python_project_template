"""Provider abstractions for the Ralph loop."""

from __future__ import annotations

# CodexCliProvider intentionally shells out to the local `codex exec` binary.
import subprocess  # nosec B404
import tempfile
import time
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Protocol, cast

import httpx

from python_project_template.ralph.models import ChatMessage


class ProviderError(RuntimeError):
    """Raised when a chat provider call fails."""


class ChatProvider(Protocol):
    """Minimal provider interface used by the Ralph engine."""

    def complete(
        self,
        *,
        messages: list[ChatMessage],
        model: str | None,
        temperature: float,
    ) -> str:
        """Return the raw model response text."""


class CodexCliProvider:
    """Provider that delegates phase execution to `codex exec`."""

    def __init__(
        self,
        *,
        codex_command: str = "codex",
        working_dir: Path,
        timeout_seconds: int,
        use_oss: bool = False,
        local_provider: str | None = None,
        run_fn: Callable[..., subprocess.CompletedProcess[str]] | None = None,
    ) -> None:
        self._codex_command = codex_command
        self._working_dir = working_dir
        self._timeout_seconds = timeout_seconds
        self._use_oss = use_oss
        self._local_provider = local_provider
        self._run_fn = run_fn or subprocess.run

    def complete(
        self,
        *,
        messages: list[ChatMessage],
        model: str | None,
        temperature: float,
    ) -> str:
        del temperature
        prompt = self._build_prompt(messages)
        with tempfile.TemporaryDirectory(prefix="ralph-codex-") as temp_dir:
            output_path = Path(temp_dir) / "last-message.txt"
            command = self._build_command(output_path=output_path, model=model)
            try:
                result = self._run_fn(
                    command,
                    input=prompt.encode("utf-8"),
                    capture_output=True,
                    cwd=self._working_dir,
                    timeout=self._timeout_seconds,
                    check=False,
                )
            except FileNotFoundError as exc:
                raise ProviderError(
                    f"Codex CLI command not found: {self._codex_command}. "
                    "Install Codex CLI or set RALPH_CODEX_COMMAND."
                ) from exc
            except subprocess.TimeoutExpired as exc:
                raise ProviderError(
                    "Codex CLI timed out while generating a Ralph phase response. "
                    f"Timeout: {self._timeout_seconds}s."
                ) from exc

            if result.returncode != 0:
                details = (
                    self._decode_stream(result.stderr)
                    or self._decode_stream(result.stdout)
                    or "No error output."
                )
                raise ProviderError(
                    "Codex CLI failed while generating a Ralph phase response. "
                    f"Command: {' '.join(command)}. Details: {details}"
                )

            if not output_path.exists():
                raise ProviderError("Codex CLI finished without writing the final response file.")

            content = output_path.read_text(encoding="utf-8", errors="replace").strip()
            if not content:
                raise ProviderError("Codex CLI returned an empty final response.")
            return content

    def _build_command(self, *, output_path: Path, model: str | None) -> list[str]:
        command = [
            self._codex_command,
            "exec",
            "-",
            "-C",
            str(self._working_dir),
            "--sandbox",
            "read-only",
            "--color",
            "never",
            "--ephemeral",
            "--skip-git-repo-check",
            "-o",
            str(output_path),
        ]
        if self._use_oss:
            command.append("--oss")
        if self._local_provider:
            command.extend(["--local-provider", self._local_provider])
        if model:
            command.extend(["--model", model])
        return command

    def _build_prompt(self, messages: Sequence[ChatMessage]) -> str:
        sections = [
            "You are executing one Ralph planning phase.",
            "Return only the final JSON object requested by the user message.",
            "Do not wrap the JSON in markdown fences.",
        ]
        for message in messages:
            role_label = message.role.upper()
            sections.append(f"{role_label} MESSAGE:\n{message.content}")
        return "\n\n".join(sections)

    def _decode_stream(self, value: str | bytes | None) -> str:
        if value is None:
            return ""
        if isinstance(value, bytes):
            return value.decode("utf-8", errors="replace").strip()
        return value.strip()


class OpenAICompatibleChatProvider:
    """HTTP client for OpenAI-compatible chat completion endpoints."""

    _RETRIABLE_STATUS_CODES = frozenset({408, 409, 429, 500, 502, 503, 504})

    def __init__(
        self,
        *,
        api_base_url: str,
        api_key: str,
        timeout_seconds: int,
        retries: int = 2,
        sleep_fn: Callable[[float], None] | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self._api_base_url = api_base_url.rstrip("/")
        self._api_key = api_key
        self._timeout_seconds = timeout_seconds
        self._retries = retries
        self._sleep_fn = sleep_fn or time.sleep
        self._transport = transport

    def complete(
        self,
        *,
        messages: list[ChatMessage],
        model: str | None,
        temperature: float,
    ) -> str:
        payload = {
            "model": model,
            "temperature": temperature,
            "messages": [
                {
                    "role": message.role,
                    "content": message.content,
                }
                for message in messages
            ],
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        last_error: Exception | None = None
        with httpx.Client(
            base_url=self._api_base_url,
            headers=headers,
            timeout=self._timeout_seconds,
            transport=self._transport,
        ) as client:
            for attempt in range(1, self._retries + 2):
                try:
                    response = client.post("/chat/completions", json=payload)
                except httpx.RequestError as exc:
                    last_error = exc
                    if attempt <= self._retries:
                        self._sleep_fn(self._retry_delay_seconds(attempt=attempt))
                        continue
                    break

                if response.is_error:
                    last_error = self._build_http_error(response)
                    if (
                        response.status_code in self._RETRIABLE_STATUS_CODES
                        and attempt <= self._retries
                    ):
                        self._sleep_fn(
                            self._retry_delay_seconds(
                                attempt=attempt,
                                response=response,
                            )
                        )
                        continue
                    break

                try:
                    return self._extract_content(response.json())
                except (ValueError, KeyError, TypeError, ProviderError) as exc:
                    raise ProviderError(
                        "OpenAI-compatible response parsing failed. "
                        f"Base URL: {self._api_base_url}. Error: {exc}"
                    ) from exc

        raise ProviderError(
            "OpenAI-compatible request failed after retries. "
            f"Base URL: {self._api_base_url}. Last error: {last_error}"
        ) from last_error

    def _build_http_error(self, response: httpx.Response) -> ProviderError:
        detail = self._error_detail_from_response(response)
        return ProviderError(
            "OpenAI-compatible request failed. "
            f"Status: {response.status_code}. URL: {response.request.url}. "
            f"Details: {detail}"
        )

    def _error_detail_from_response(self, response: httpx.Response) -> str:
        try:
            payload = response.json()
        except ValueError:
            text = response.text.strip()
            return text or response.reason_phrase

        if not isinstance(payload, dict):
            return str(payload)

        error = payload.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            error_type = error.get("type")
            error_code = error.get("code")
            parts = [
                part for part in (message, error_type, error_code) if isinstance(part, str) and part
            ]
            if parts:
                return " | ".join(parts)

        return str(payload)

    def _retry_delay_seconds(
        self,
        *,
        attempt: int,
        response: httpx.Response | None = None,
    ) -> float:
        if response is not None:
            retry_after = self._parse_retry_after(response.headers.get("Retry-After"))
            if retry_after is not None:
                return retry_after
        return min(float(2 ** (attempt - 1)), 8.0)

    def _parse_retry_after(self, value: str | None) -> float | None:
        if not value:
            return None
        try:
            return max(float(value), 0.0)
        except ValueError:
            pass

        try:
            retry_after_dt = parsedate_to_datetime(value)
        except (TypeError, ValueError, IndexError):
            return None

        if retry_after_dt.tzinfo is None:
            retry_after_dt = retry_after_dt.replace(tzinfo=UTC)
        now = datetime.now(UTC)
        return max((retry_after_dt - now).total_seconds(), 0.0)

    def _extract_content(self, payload: dict[str, object]) -> str:
        try:
            choices = payload["choices"]
            if not isinstance(choices, list) or not choices:
                raise ProviderError("Provider response choices must be a non-empty list.")
            first_choice = choices[0]
            if not isinstance(first_choice, dict):
                raise ProviderError("Provider response choices entries must be objects.")
            first_choice_dict = cast(dict[str, object], first_choice)
            message = first_choice_dict["message"]
            if not isinstance(message, dict):
                raise ProviderError("Provider response message must be an object.")
            message_dict = cast(dict[str, object], message)
            content = message_dict["content"]
        except (KeyError, TypeError, ProviderError) as exc:
            raise ProviderError(
                "Provider response did not contain choices[0].message.content."
            ) from exc

        if isinstance(content, str):
            return content
        if isinstance(content, list):
            text_parts: list[str] = []
            for item in content:
                if isinstance(item, dict):
                    item_dict = cast(dict[str, object], item)
                    if item_dict.get("type") != "text":
                        continue
                    text = item_dict.get("text")
                    if isinstance(text, str):
                        text_parts.append(text)
            joined = "\n".join(text_parts).strip()
            if joined:
                return joined

        raise ProviderError("Provider response content was not a string or text-part list.")
