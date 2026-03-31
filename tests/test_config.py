"""Tests for application configuration loading."""

from __future__ import annotations

import os
from pathlib import Path

from python_project_template.config import AppConfig


def _make_fake_executable(path: Path) -> None:
    path.write_text("", encoding="utf-8")
    if os.name != "nt":
        path.chmod(0o755)


def test_from_env_recovers_from_stale_absolute_codex_path(monkeypatch, tmp_path: Path) -> None:
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    executable_name = "codex.exe" if os.name == "nt" else "codex"
    executable_path = fake_bin / executable_name
    _make_fake_executable(executable_path)

    stale_path = (tmp_path / "missing" / executable_name).resolve()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PATH", str(fake_bin))
    monkeypatch.setenv("RALPH_CODEX_COMMAND", str(stale_path))

    config = AppConfig.from_env()

    assert Path(config.ralph_codex_command) == executable_path


def test_from_env_keeps_missing_relative_codex_path(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("RALPH_CODEX_COMMAND", str(Path("tools") / "codex"))
    monkeypatch.setenv("PATH", "")

    config = AppConfig.from_env()

    assert config.ralph_codex_command == str(Path("tools") / "codex")


def test_from_env_finds_codex_in_vscode_extension_when_path_is_missing(
    monkeypatch, tmp_path: Path
) -> None:
    home_dir = tmp_path / "home"
    extension_dir = (
        home_dir
        / ".vscode"
        / "extensions"
        / "openai.chatgpt-26.325.31654-win32-x64"
        / "bin"
        / "windows-x86_64"
    )
    extension_dir.mkdir(parents=True)
    executable_name = "codex.exe" if os.name == "nt" else "codex"
    executable_path = extension_dir / executable_name
    _make_fake_executable(executable_path)

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("RALPH_CODEX_COMMAND", "codex")
    monkeypatch.setenv("PATH", "")
    monkeypatch.setenv("HOME", str(home_dir))
    monkeypatch.setenv("USERPROFILE", str(home_dir))

    config = AppConfig.from_env()

    assert Path(config.ralph_codex_command) == executable_path
