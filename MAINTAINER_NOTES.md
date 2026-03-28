# Python Project Template - Maintainer Notes

This is an overengineered GitHub template repository for Python projects. Users download it and customize it as a base for their own projects.

## What This Template Provides

- Modern Python setup:
  - Reproducible installs via `uv` and a lockfile
  - `src/`-layout project structure
  - Type hints enforced with `ty`
  - Comprehensive testing with pytest
  - 80%+ coverage enforcement
- Production-ready infrastructure:
  - Type checking with `ty`
  - Code linting and formatting with Ruff
  - Security scanning with Bandit
  - Structured logging (JSON and plain text)
  - Configuration management (env/.env/defaults)
  - Pre-commit hooks
- CI/CD automation:
  - GitHub Actions workflows for lint, type-check, test, docs, and release
  - Multi-platform testing (Linux, Windows, macOS)
  - Multi-version testing (Python 3.11, 3.12, 3.13)
  - Coverage reporting
- Professional documentation:
  - README with quick start and template guidance
  - Architecture overview and design decisions (ADRs)
  - Contributing guidelines with development workflow
  - Customization checklist in `TEMPLATE_TODO.md`
  - MkDocs setup for documentation sites

## Important: This Is Not a Library or CLI Tool

This template includes example code (config, logging, CLI, utilities) to demonstrate how to structure a project. When users download this template, they should:

1. Rename their package
2. Delete or adapt the example code
3. Add their own business logic

The template is not meant to be used directly. It is a starting point.

## Key Files for Template Users

| File | Purpose |
|------|---------|
| `TEMPLATE_TODO.md` | Step-by-step customization checklist |
| `README.md` | Template overview and quick start |
| `CONTRIBUTING.md` | Development and release workflow |
| `docs/architecture.md` | System design reference |
| `docs/adr/` | Architecture Decision Record examples |

## No CLI Entry Point

The `--cli-entry-point` was intentionally removed from `pyproject.toml` because:

- Template users should not accidentally publish a generic CLI tool
- Example CLI code is marked for deletion
- Users should define their own entry points

## Example Code Is Marked for Deletion

All example code includes `[TEMPLATE]` comments:

- `src/python_project_template/utils/basic_ops.py` - Example utility class
- `src/python_project_template/main.py` - Example CLI using Typer
- `tests/test_basic_ops.py` - Example tests

Users should delete or adapt these files to fit their own project.

## For Future Maintenance

### If Updating the Template

1. Keep the same overengineered principles (type safety, testing, CI/CD)
2. Update docs to clarify template-specific guidance
3. Mark any example code clearly with `[TEMPLATE]` comments
4. Run `make check` to verify all quality gates pass
5. Test that `TEMPLATE_TODO.md` is still accurate

### Releasing Template Updates

This template itself does not need semantic versioning or PyPI releases because it is a GitHub template. Fix bugs and push to `main`; template users always get the latest `main` branch.

### Testing the Template

To verify users can customize this:

1. Create a test repo from the template
2. Follow the `TEMPLATE_TODO.md` steps
3. Run `make check` and verify it passes
4. Confirm that deleting the example code does not break workflows

## CI/CD Workflows Included

| Workflow | File | Runs On |
|----------|------|---------|
| Lint and type check | `.github/workflows/lint-test.yml` | Push + PR |
| Multi-version tests | `.github/workflows/lint-test.yml` | Push + PR |
| Coverage report | `.github/workflows/lint-test.yml` | Push + PR |
| Docs build | `.github/workflows/docs-build.yml` | Push + PR |
| Release (optional) | `.github/workflows/release.yml` | Git tags |

Users can disable the release workflow if they do not publish to PyPI or GitHub Releases.

## Common Template Pitfalls for Users

Users might:

1. Try to use this as a library or CLI tool directly.
   Solution: Point them to the "Using This Template" section in `README.md`.
2. Forget to rename the package and end up with `python_project_template` everywhere.
   Solution: Step 1 in `TEMPLATE_TODO.md` covers this.
3. Leave example code in place and wonder why coverage is low.
   Solution: Step 2 in `TEMPLATE_TODO.md` explains what the example code is.
4. Forget to update CI/CD workflows for their Python versions.
   Solution: Step 5 in `TEMPLATE_TODO.md` covers CI/CD customization.

## Summary

This is a professional, overengineered GitHub template that provides:

- Best practices for Python project structure
- Production-ready tooling and automation
- Clear guidance for users to customize it

Users download it, follow `TEMPLATE_TODO.md`, and build their own projects on top.
