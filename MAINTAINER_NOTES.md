# Ralph Loop CLI - Maintainer Notes

This repository now ships a real CLI for autonomous project planning and prompt-pack generation.

## What the Repo Provides

- A Typer-based `ralph` CLI
- Env-driven runtime config in `src/python_project_template/config.py`
- A provider-neutral Ralph engine in `src/python_project_template/ralph/`
- A default Codex CLI backend for ChatGPT/Codex login or local OSS models
- One OpenAI-compatible HTTP adapter backed by `httpx`
- Tests for CLI behavior, engine validation, and provider transport

## Core Behavior

`ralph run` turns a brief into a persisted session under `outputs/ralph/` by default.

Each run executes these phases:

1. `discover`
2. `decompose`
3. `refine`
4. `prompt_pack`
5. `summarize`

The engine enforces:

- atomic tasks
- explicit pass/fail criteria
- valid task dependencies
- full requirement coverage
- one prompt artifact per task

## Key Files

| File | Purpose |
|------|---------|
| `src/python_project_template/main.py` | CLI entrypoint |
| `src/python_project_template/config.py` | Env and `.env` config loader |
| `src/python_project_template/ralph/engine.py` | Loop orchestration and persistence |
| `src/python_project_template/ralph/provider.py` | OpenAI-compatible adapter |
| `tests/test_cli.py` | CLI behavior coverage |
| `tests/test_engine.py` | Loop and artifact persistence coverage |
| `tests/test_provider.py` | Transport adapter coverage |

## Session Outputs

Each Ralph run writes:

- `brief.md`
- `session.json`
- `backlog.json`
- `summary.md`
- `event-log.jsonl`
- `prompts/*.md`

Failed runs should still leave partial artifacts behind.

## Provider Expectations

The default backend is Codex CLI.

Primary env vars:

- `RALPH_PROVIDER=codex`
- `RALPH_CODEX_COMMAND`
- `RALPH_CODEX_OSS`
- `RALPH_CODEX_LOCAL_PROVIDER`

Optional shared env vars:

- `RALPH_MODEL`
- `RALPH_TIMEOUT_SECONDS`
- `RALPH_MAX_ITERATIONS`
- `RALPH_OUTPUT_DIR`

OpenAI HTTP remains an explicit fallback:

- `RALPH_PROVIDER=openai`
- `RALPH_API_BASE_URL`
- `RALPH_API_KEY`
- `RALPH_MODEL`

## Maintenance Checklist

When changing the Ralph flow:

1. Keep phase outputs JSON-only and validation-driven.
2. Preserve artifact persistence on failure.
3. Update README and `docs/usage.md` when CLI flags or output files change.
4. Keep `tests/` aligned with prompt schemas and validation rules.
5. Run `make test` and `make type-check`.
