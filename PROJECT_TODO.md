# Overengineered Python Project Template Plan

This document tracks what is already in place and what remains to make this template fully overengineered for professional use.

## Overengineering Principles
- Everything is automated (lint/test/format/docs/release) and enforced via CI gates.
- Settings are validated, typed, and layered (defaults -> .env -> OS env -> CLI).
- Reproducible builds are mandatory (lockfiles, pinned tools, deterministic outputs).
- Observability is default-ready (structured logs, metrics stubs, trace hooks).
- Security is continuous (SAST, dependency audits, secrets scanning).
- Documentation is part of the product (docs site, ADRs, changelog, runbooks).

## Definition of Done
- CI matrix green on Linux/Windows/macOS and Python 3.11-3.13.
- Linting, formatting, typing, and tests are enforced as merge gates.
- Coverage threshold enforced with reports (XML/HTML) and badges.
- Release pipeline builds artifacts, generates SBOM, and publishes docs.
- Config and logging are implemented with clear env contracts.

## Done
- Project metadata: `pyproject.toml` with hatchling backend, `src/` layout, `requires-python>=3.11`, dev extra for ruff/pytest.
- Dev tooling: Ruff lint/format config (`ruff.toml`), Makefile targets for install/lint/format/test/cov/check/clean, `uv.lock` for reproducible installs, pre-commit hook config (ruff + ruff-format).
- Testing: pytest dependency and sample test suite (`tests/test_basic_ops.py`), simple manual runner (`src/python_project_template/main.py`).
- Code structure: package namespace with `__version__` placeholder, example utility class (`BasicOperations`), placeholder config/logging modules (currently empty).
- Docs skeleton: MkDocs config (`docs/mkdocs.yml`) and landing page (`docs/index.md`).
- Repo hygiene: `.gitignore`, `.python-version`, `LICENSE`, placeholder `.env.example`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`.

## To Do

### Packaging and versioning
- Add semantic versioning workflow (bumpversion or hatch version hook) and changelog automation (Keep a Changelog + towncrier).
- Publish-ready configs: `pyproject` classifiers, license, authors, homepage, keywords, optional extras (lint, test, docs, ci), and console_scripts entry points.
- Build matrix validation (Linux/Windows/macOS, Python 3.11-3.13) in CI.

### Code quality and typing
- Introduce strict type checking (mypy or pyright) with config and Makefile target.
- Enforce docstring style (pydocstyle) and formatting (docformatter) with pre-commit hooks.
- Add safety checks: `pip-audit`/`pipdeptree` or `uvx safety`, `bandit` for security linting.
- Configure import sorting (already via ruff) with per-module allowlists if needed.

### Testing and coverage
- Coverage tooling: `coverage.py` config, XML/HTML outputs, enforce min coverage in CI.
- Property-based tests with hypothesis for core utilities.
- Add integration tests or smoke tests for CLI entry points when added.
- Test matrix in CI (platforms + Python versions).

### Logging, config, and runtime
- Implement structured logging helpers in `src/python_project_template/logging.py` (std lib logging config, JSON formatter option, log levels from env).
- Implement `config.py` to load settings from env/.env files with pydantic or dynaconf fallback, plus validation and defaults.
- Add runtime feature flags and configuration layering (env > .env > defaults).

### CLI and UX
- Provide a CLI entry point (e.g., `python-project-template` command) using `typer` or `click`, wired to sample operations.
- Add rich/typer-based diagnostics (progress, tables) for demo commands.

### Documentation
- Expand MkDocs site: usage guide, development guide, architecture overview, API reference (mkdocstrings), changelog page.
- Add ADRs folder for architectural decisions.
- Auto-publish docs via CI to GitHub Pages.

### CI/CD
- Add GitHub Actions workflows: lint/format, tests with coverage, security scans, docs build, release tagging, and artifact upload.
- Cache dependencies (uv cache) and test results to speed CI.
- Require status checks before merge; add branch protection guidance.

### Release and distribution
- Add release workflow to build wheels/sdists and (optionally) publish to PyPI/TestPyPI.
- Provide Dockerfile and devcontainer for consistent environments; include docker-compose for services if needed.
- Supply SBOM generation (e.g., `cyclonedx-py`).

### Dev experience
- Editor settings: `.editorconfig`, recommended VS Code settings/extensions.
- Task automation: `justfile` or `tox`/`nox` session definitions mirroring Make targets.
- Add git hooks for commit-msg/lint staged (pre-commit CI compatibility).

### Observability and quality gates
- Add metrics/tracing shims (noop by default) to show how to integrate OpenTelemetry.
- Add runtime health checks and structured error handling patterns.
- Include performance benchmarking scaffold (pytest-benchmark).

### Security and compliance
- Secrets scanning (gitleaks/trufflehog) in pre-commit and CI.
- License scanning and dependency policy checks.
- Supply SECURITY.md and update CODE_OF_CONDUCT/CONTRIBUTING with triage process.

### Examples and templates
- Provide sample service layout (handlers, domain, adapters) and dependency injection pattern.
- Add sample data fixtures and factory helpers for tests.
- Include templates for issues/PRs and CODEOWNERS.

### Housekeeping
- Fill in README with quickstart, Dev setup, Testing, Release, and Contributing sections.
- Keep `.env.example` populated with all relevant config keys and defaults.
- Add automation to clean build artifacts more aggressively (e.g., cache dirs in user tmp).
