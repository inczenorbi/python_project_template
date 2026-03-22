# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-03-22

### Added
- Initial release of python-project-template
- **Config Management**: Environment variable and .env file support with typed configuration
- **Structured Logging**: Plain text and JSON formatted logging with context support
- **CLI Interface**: Typer-based command-line interface with `calculate`, `diagnose`, and `demo` commands
- **Utilities**: BasicOperations class with mathematical operations (add, subtract, multiply, divide, power, mean)
- **Testing**: Comprehensive test suite with pytest and coverage reporting (80%+ coverage requirement)
- **Type Safety**: Mypy strict mode enforced across codebase
- **CI/CD**: GitHub Actions workflows for linting, testing, type checking, and coverage validation
- **Documentation**: Architecture overview, usage guide, and Architecture Decision Records (ADRs)
- **Pre-commit Hooks**: Ruff and Bandit hooks for code quality and security
- **Versioning**: Bumpversion configuration for semantic versioning

### Project Features
- Type hints on all public functions
- Comprehensive docstrings
- CLI entry point: `python-project-template` command
- Configurable via environment variables: DEBUG, LOG_LEVEL, LOG_FORMAT, ENVIRONMENT
- Support for .env files for local configuration
- JSON structured logging for production observability
- Cross-platform CI testing (Linux, Windows, macOS)
- Multi-version Python testing (3.11, 3.12, 3.13)
- Coverage reporting with HTML output
- Security scanning via Bandit

---

## How to Update This Changelog

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` for vulnerability fixes.

For versions, use semantic versioning:
- **MAJOR** (X.0.0): Breaking changes
- **MINOR** (x.Y.0): New features (backward compatible)
- **PATCH** (x.y.Z): Bug fixes (backward compatible)

Example:
```bash
# After making changes, update version
uv pip install bumpversion
bumpversion patch  # 0.1.0 -> 0.1.1
bumpversion minor  # 0.1.0 -> 0.2.0
bumpversion major  # 0.1.0 -> 1.0.0
```

Then update CHANGELOG.md following the format above and commit both files.
