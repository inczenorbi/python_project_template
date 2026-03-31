# Ralph Loop CLI

`python_project_template` now provides a real Ralph loop CLI for turning a project brief into an executable implementation run.

The CLI accepts a free-form goal, runs a multi-phase planning loop, executes the resulting tasks through Codex by default, and writes a complete execution record to `outputs/ralph/<timestamp>-<slug>/`.

## What Ralph Produces

Each successful run creates:

- `brief.md` with the original goal, constraints, and context files
- `session.json` with the full structured session state
- `backlog.json` with discovered requirements and atomic tasks
- `prompts/*.md` with one implementation prompt per task
- `executions/*.md` with one implementation report per executed task
- `summary.md` with the final handoff summary
- `event-log.jsonl` with phase-by-phase execution events

If the loop fails, the same directory still contains the partial artifacts plus the failure reason.

## Requirements

- Python 3.11+
- `uv`
- Codex CLI installed and logged in

Optional:

- OpenAI-compatible API credentials if you explicitly switch to the `openai` provider

## Install

```bash
uv venv
uv sync --all-groups
```

If you prefer editable installs:

```bash
uv pip install -e ".[dev]"
```

## Configure Ralph

Copy `.env.example` to `.env`.

Default setup uses Codex CLI with your existing Codex/ChatGPT login:

```bash
RALPH_PROVIDER=codex
RALPH_CODEX_COMMAND=codex
RALPH_CODEX_OSS=0
RALPH_CODEX_LOCAL_PROVIDER=
RALPH_MODEL=
RALPH_TIMEOUT_SECONDS=300
RALPH_MAX_ITERATIONS=3
RALPH_OUTPUT_DIR=outputs/ralph
```

To run against a local model through Codex CLI, enable OSS mode:

```bash
RALPH_PROVIDER=codex
RALPH_CODEX_OSS=1
RALPH_CODEX_LOCAL_PROVIDER=ollama
```

To use the old direct API backend explicitly:

```bash
RALPH_PROVIDER=openai
RALPH_API_BASE_URL=https://api.openai.com/v1
RALPH_API_KEY=your-api-key
RALPH_MODEL=your-model
```

## Quick Start

Run Ralph with a direct goal:

```bash
uv run ralph run --goal "Plan a SaaS analytics dashboard for small teams"
```

Pipe a brief through stdin:

```bash
echo "Build a developer portal with docs, auth, and deployment flow" | uv run ralph run
```

Include extra context files:

```bash
uv run ralph run \
  --goal "Plan a redesign for our internal admin tool" \
  --context-file docs/usage.md \
  --constraints "Prefer small, reviewable changes"
```

Generate the plan and prompts without modifying the repository:

```bash
uv run ralph run \
  --goal "Plan a redesign for our internal admin tool" \
  --plan-only
```

Validate config without calling the provider:

```bash
uv run ralph run --goal "Plan a support dashboard" --dry-run
```

Inspect resolved config:

```bash
uv run ralph diagnose
```

## CLI Options

`ralph run` supports:

- `--goal`
- `--context-file` (repeatable)
- `--constraints`
- `--output-dir`
- `--max-iterations`
- `--model` (optional override)
- `--temperature`
- `--dry-run`
- `--plan-only`

## Ralph Loop Phases

The engine runs these phases:

1. `discover`
2. `decompose`
3. `refine`
4. `prompt_pack`
5. `implement`
6. `summarize`

The loop enforces these rules:

- tasks must be atomic
- each task must have explicit pass/fail criteria
- dependencies must reference valid task ids
- every requirement must be covered by at least one task
- every task must receive a generated implementation prompt
- Codex-backed runs execute tasks in workspace order unless `--plan-only` is set

The `openai` provider remains planning-only. Use `--plan-only` when you want a handoff pack without repository edits.

## Development

Useful commands:

```bash
make install
make test
make type-check
make lint
make ralph-help
```

Baseline validation:

```bash
make check
```

## Project Layout

Core runtime code lives in:

- `src/python_project_template/main.py`
- `src/python_project_template/config.py`
- `src/python_project_template/ralph/`

Tests live in `tests/`.
