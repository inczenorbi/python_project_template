# Python Project Template

Overengineered Python project template with modern tooling, reproducible installs, and production-ready CI/CD.

**This is a GitHub template repository.** Use it as a foundation for your own Python projects. See [Using This Template](#using-this-template) below to get started.

## Using This Template

### Option 1: Create a New Repository from This Template (Recommended)

1. Click **"Use this template"** button on GitHub (top-right of the repo page)
2. Choose a name for your new repository
3. Clone your new repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/YOUR_PROJECT_NAME
   cd YOUR_PROJECT_NAME
   ```
4. Follow the **Customization Steps** below

### Option 2: Clone and Adapt

```bash
git clone https://github.com/yourorg/python-project-template.git my-project
cd my-project
git remote set-url origin https://github.com/YOUR_USERNAME/YOUR_PROJECT_NAME
```

### Customization Steps

1. **Update project metadata** in `pyproject.toml`:
   ```toml
   [project]
   name = "my-project"                  # Change this
   description = "What your project does"  # Change this
   # Add your name/email under [project]
   ```

2. **Delete example code** (marked with `# [TEMPLATE] Delete this` comments):
   ```bash
   rm src/my_project/utils/basic_ops.py
   rm tests/test_basic_ops.py
   ```
   Then update `src/my_project/main.py` with your own CLI or remove it entirely if you don't need a CLI.

3. **Update Python package name** in code:
   - Rename `src/python_project_template/` to `src/your_project_name/`
   - Update all imports throughout the codebase

4. **Set up your development environment**:
   ```bash
   make install
   make precommit
   ```

5. **Remove or adapt example workflows** in `.github/workflows/`:
   - The `release.yml` workflow assumes PyPI publishing. Delete or modify if not needed.
   - Otherwise, workflows will run on every push.

6. **Update CI for your team**:
   - Modify `.github/workflows/lint-test.yml` if you need different Python versions or OS targets
   - Configure branch protection rules in GitHub (Settings → Branches)

7. **Customize documentation**:
   - Update `README.md` with your project's purpose and usage
   - Update `docs/` with your own guides and documentation
   - Update `CONTRIBUTING.md` with your team's guidelines

8. **Initialize git history** (optional, to start fresh):
   ```bash
   rm -rf .git
   git init
   git add .
   git commit -m "Initial commit from python-project-template"
   ```

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

## Development Setup

### Quick setup

```bash
# Install the package and all dev dependencies
make install

# Set up git hooks for CI enforcement
make precommit
```

### Virtual environment management

- Create a venv: `uv venv`
- Activate on macOS/Linux: `source .venv/bin/activate`
- Activate on Windows: `.venv\Scripts\Activate.ps1` (PowerShell)
- Sync dependencies: `uv sync --all-groups`
- Install tools globally: `uv tool install ruff` (one-time)

## Testing

### Run tests

```bash
make test          # Run pytest
make cov           # Run pytest with coverage report (generates htmlcov/)
open htmlcov/index.html  # View coverage report
```

### Coverage requirements

- Minimum coverage threshold: 80%
- Coverage is enforced in CI/CD pipelines before merge
- View branch coverage: `make cov` → open `htmlcov/index.html`

### Type checking

```bash
make type-check    # Run mypy on src/ and tests/
```

- Mypy config: `pyproject.toml [tool.mypy]`
- Ignores are documented inline in source files

## Quality Gates

### Local validation (before git push)

```bash
make check         # Runs lint + type-check + test (comprehensive check)
```

### Pre-commit hooks

Run automatically on commit:
- Ruff lint + format
- Ruff import sorting

Disable temporarily: `git commit --no-verify`

## Makefile shortcuts

```bash
make install       # Install package + dev deps
make lint          # Run ruff linter
make format        # Run ruff formatter + docformatter
make test          # Run pytest
make type-check    # Run mypy
make cov           # Run pytest with coverage
make check         # Comprehensive validation (lint + type + test)
make clean         # Remove build/test artifacts
```
