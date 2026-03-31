"""Tests for Ralph provider adapters."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

import httpx
import pytest

from python_project_template.ralph.models import ChatMessage
from python_project_template.ralph.provider import (
    CodexCliProvider,
    OpenAICompatibleChatProvider,
    ProviderError,
)


def test_codex_provider_builds_command_and_reads_output(tmp_path) -> None:
    captured: dict[str, Any] = {}

    def run_fn(command, **kwargs):
        captured["command"] = command
        captured["input"] = kwargs["input"]
        captured["cwd"] = kwargs["cwd"]
        output_path = command[command.index("-o") + 1]
        Path(output_path).write_text('{"ok": true}', encoding="utf-8")
        return subprocess.CompletedProcess(command, 0, stdout=b"", stderr=b"")

    provider = CodexCliProvider(
        codex_command="codex",
        working_dir=tmp_path,
        timeout_seconds=30,
        use_oss=True,
        local_provider="ollama",
        run_fn=run_fn,
    )

    response = provider.complete(
        messages=[
            ChatMessage(role="system", content="system rule"),
            ChatMessage(role="user", content='{"phase":"discover"}'),
        ],
        model=None,
        temperature=0.2,
    )

    assert response == '{"ok": true}'
    assert captured["cwd"] == tmp_path
    assert captured["command"][:3] == ["codex", "exec", "-"]
    assert "--oss" in captured["command"]
    assert captured["command"][captured["command"].index("--local-provider") + 1] == "ollama"
    assert "--model" not in captured["command"]
    assert isinstance(captured["input"], bytes)
    assert b"Return only the final JSON object" in captured["input"]


def test_codex_provider_surfaces_cli_failures(tmp_path) -> None:
    def run_fn(command, **kwargs):
        return subprocess.CompletedProcess(command, 1, stdout=b"", stderr=b"not logged in")

    provider = CodexCliProvider(
        codex_command="codex",
        working_dir=tmp_path,
        timeout_seconds=30,
        run_fn=run_fn,
    )

    with pytest.raises(ProviderError) as exc_info:
        provider.complete(
            messages=[ChatMessage(role="user", content='{"phase":"discover"}')],
            model="gpt-5",
            temperature=0.0,
        )

    assert "not logged in" in str(exc_info.value)


def test_codex_provider_decodes_non_utf_console_bytes_with_replacement(tmp_path) -> None:
    def run_fn(command, **kwargs):
        del kwargs
        return subprocess.CompletedProcess(command, 1, stdout=b"", stderr=b"\x9ddecode-problem")

    provider = CodexCliProvider(
        codex_command="codex",
        working_dir=tmp_path,
        timeout_seconds=30,
        run_fn=run_fn,
    )

    with pytest.raises(ProviderError) as exc_info:
        provider.complete(
            messages=[ChatMessage(role="user", content='{"phase":"discover"}')],
            model=None,
            temperature=0.0,
        )

    assert "decode-problem" in str(exc_info.value)


def test_provider_builds_request_payload() -> None:
    captured: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"ok": true}'}}]},
        )

    provider = OpenAICompatibleChatProvider(
        api_base_url="https://example.test/v1",
        api_key="secret",
        timeout_seconds=10,
        transport=httpx.MockTransport(handler),
    )

    response = provider.complete(
        messages=[
            ChatMessage(role="system", content="system"),
            ChatMessage(role="user", content='{"phase":"discover"}'),
        ],
        model="test-model",
        temperature=0.3,
    )

    assert response == '{"ok": true}'
    payload = captured["payload"]
    assert payload["model"] == "test-model"
    assert payload["temperature"] == 0.3
    assert payload["messages"][1]["role"] == "user"
    assert captured["headers"]["authorization"] == "Bearer secret"
    assert captured["url"] == "https://example.test/v1/chat/completions"


def test_provider_retries_request_errors() -> None:
    attempts = {"count": 0}
    sleeps: list[float] = []

    def handler(request: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] == 1:
            raise httpx.ConnectError("temporary", request=request)
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"ok": true}'}}]},
        )

    provider = OpenAICompatibleChatProvider(
        api_base_url="https://example.test/v1",
        api_key="secret",
        timeout_seconds=10,
        retries=1,
        sleep_fn=sleeps.append,
        transport=httpx.MockTransport(handler),
    )

    response = provider.complete(
        messages=[ChatMessage(role="user", content='{"phase":"discover"}')],
        model="test-model",
        temperature=0.0,
    )

    assert response == '{"ok": true}'
    assert attempts["count"] == 2
    assert sleeps == [1.0]


def test_provider_retries_rate_limits_with_retry_after() -> None:
    attempts = {"count": 0}
    sleeps: list[float] = []

    def handler(_: httpx.Request) -> httpx.Response:
        attempts["count"] += 1
        if attempts["count"] == 1:
            return httpx.Response(
                429,
                headers={"Retry-After": "2"},
                json={
                    "error": {
                        "message": "Rate limit exceeded.",
                        "type": "rate_limit_exceeded",
                    }
                },
            )
        return httpx.Response(
            200,
            json={"choices": [{"message": {"content": '{"ok": true}'}}]},
        )

    provider = OpenAICompatibleChatProvider(
        api_base_url="https://example.test/v1",
        api_key="secret",
        timeout_seconds=10,
        retries=1,
        sleep_fn=sleeps.append,
        transport=httpx.MockTransport(handler),
    )

    response = provider.complete(
        messages=[ChatMessage(role="user", content='{"phase":"discover"}')],
        model="test-model",
        temperature=0.0,
    )

    assert response == '{"ok": true}'
    assert attempts["count"] == 2
    assert sleeps == [2.0]


def test_provider_raises_for_malformed_response_body() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": [{"message": {}}]})

    provider = OpenAICompatibleChatProvider(
        api_base_url="https://example.test/v1",
        api_key="secret",
        timeout_seconds=10,
        retries=0,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ProviderError):
        provider.complete(
            messages=[ChatMessage(role="user", content='{"phase":"discover"}')],
            model="test-model",
            temperature=0.0,
        )


def test_provider_surfaces_http_error_details() -> None:
    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429,
            json={
                "error": {
                    "message": "You exceeded your current quota.",
                    "type": "insufficient_quota",
                    "code": "insufficient_quota",
                }
            },
        )

    provider = OpenAICompatibleChatProvider(
        api_base_url="https://example.test/v1",
        api_key="secret",
        timeout_seconds=10,
        retries=0,
        sleep_fn=lambda _: None,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(ProviderError) as exc_info:
        provider.complete(
            messages=[ChatMessage(role="user", content='{"phase":"discover"}')],
            model="test-model",
            temperature=0.0,
        )

    message = str(exc_info.value)
    assert "Status: 429" in message
    assert "insufficient_quota" in message
    assert "You exceeded your current quota." in message
