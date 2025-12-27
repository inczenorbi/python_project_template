# Python Project Template

Overengineered Python project template with modern tooling, reproducible installs, and a src layout.

## Requirements
- Python 3.11+ (see `.python-version`)
- uv (https://github.com/astral-sh/uv)

## Quick start (uv, lockfile first)

```bash
uv venv
uv sync --all-groups
uv run -m pytest
```

If you prefer pip-style editable installs (less lockfile focused):

```bash
uv pip install -e ".[dev]"
```

## uv workflow (recommended)

- Add dependencies: `uv add requests`, `uv add --dev pytest`, or `uv add --group test pytest`.
- Remove dependencies: `uv remove requests`.
- Update the lockfile: `uv lock`.
- Upgrade all locked deps: `uv lock -U`.
- Upgrade a single package: `uv lock -P requests`.
- Sync the environment: `uv sync`.
- Validate lockfile is current: `uv lock --check`.
- Inspect the tree: `uv tree`.

## Dependency groups vs extras

This repo supports both patterns:

- Extras in `[project.optional-dependencies]`:
  - Install with `uv pip install -e ".[dev]"` or `uv sync --extra dev`.
- Dependency groups in `[dependency-groups]`:
  - Install with `uv sync --group dev` or `uv sync --all-groups`.

Pick one approach per team and stick with it. For uv-native workflows, groups are recommended.

## Running tools and scripts

- Run project commands in the env: `uv run -m pytest`, `uv run python -m python_project_template.main`.
- Run tools in isolated envs: `uv tool run ruff check .` (or `uvx ruff check .`).
- Install tools globally: `uv tool install ruff`.

Note: `uvx` is a shortcut for `uv tool run`.

## Makefile shortcuts

```bash
make install
make lint
make format
make test
```

## Python version management

- `.python-version` pins 3.11 for toolchains.
- Install uv-managed Python: `uv python install 3.11`.
- Pin it: `uv python pin 3.11`.
- Create a venv with a specific interpreter: `uv venv -p 3.11`.

## CI guidance

- Check lockfile: `uv lock --check`.
- Sync in CI: `uv sync --frozen --no-dev` (or add `--all-groups` if running tests).
- Disable Python downloads: `UV_PYTHON_DOWNLOADS=never`.
- Offline runs: `UV_OFFLINE=1`.

## Cache and link mode

- Cache location: `uv cache dir`.
- Clean cache: `uv cache clean` (or `uv cache prune`).
- Windows hardlink warning: set `UV_LINK_MODE=copy` or pass `--link-mode=copy`.

## Build and publish

- Build artifacts: `uv build`.
- Publish to an index: `uv publish`.

## Export requirements (interop)

- `uv export --format requirements.txt -o requirements.txt`

## Environment variables

Copy `.env.example` to `.env` and fill values for local runs. Config loading will be implemented in `config.py`.

## Docs

MkDocs config and a starter page exist in `docs/`.

## Project layout

```
src/python_project_template/
tests/
docs/
```
