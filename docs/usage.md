# Usage Guide

## Run Ralph

Basic usage:

```bash
uv run ralph run --goal "Plan a team knowledge base with search and admin tools"
```

With extra context:

```bash
uv run ralph run \
  --goal "Plan a customer portal for account management" \
  --context-file README.md \
  --context-file docs/usage.md \
  --constraints "Prefer small, reviewable changes"
```

From stdin:

```bash
cat brief.txt | uv run ralph run
```

## Configure the Provider

Default setup uses Codex CLI:

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

For local OSS models through Codex CLI:

```bash
RALPH_PROVIDER=codex
RALPH_CODEX_OSS=1
RALPH_CODEX_LOCAL_PROVIDER=ollama
```

For the optional direct API fallback:

```bash
RALPH_PROVIDER=openai
RALPH_API_BASE_URL=https://api.openai.com/v1
RALPH_API_KEY=your-api-key
RALPH_MODEL=your-model
```

Use `uv run ralph diagnose` to confirm the resolved configuration.

If you want planning and prompt generation without repository edits, add `--plan-only`:

```bash
uv run ralph run --goal "Plan a reporting portal" --plan-only
```

## Output Structure

Each run creates a timestamped session directory:

```text
outputs/ralph/20260328T120000Z-plan-a-customer-portal/
```

Inside that directory:

```text
brief.md
session.json
backlog.json
summary.md
event-log.jsonl
prompts/
  01-define-information-architecture.md
  02-draft-deployment-workflow.md
executions/
  01-define-information-architecture-execution.md
  02-draft-deployment-workflow-execution.md
```

## Phase Behavior

Ralph always runs these phases in order:

1. `discover` extracts requirements, assumptions, risks, and success criteria.
2. `decompose` creates an initial atomic task backlog.
3. `refine` loops until every requirement is covered and the task list passes validation.
4. `prompt_pack` creates one implementation prompt per task.
5. `implement` executes each task in repository order and writes an execution report.
6. `summarize` writes the final summary and implementation order.

## Dry Run

Use `--dry-run` to validate the goal and resolved configuration without calling the provider:

```bash
uv run ralph run --goal "Plan a reporting portal" --dry-run
```

## Makefile Helpers

```bash
make ralph-help
make test
make type-check
make lint
```
