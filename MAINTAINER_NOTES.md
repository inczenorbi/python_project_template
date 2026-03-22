# Python Project Template — Maintainer Notes

This is an overengineered GitHub template repository for Python projects. Users download it and customize it as a base for their own projects.

## What This Template Provides

✅ **Modern Python Setup**
- Reproducible installs via `uv` + lockfile
- src-layout project structure
- Type hints with mypy strict mode
- Comprehensive testing with pytest
- 80%+ coverage enforcement

✅ **Production-Ready Infrastructure**
- Type checking (mypy)
- Code linting & formatting (Ruff)
- Security scanning (Bandit)
- Structured logging (JSON + plain text)
- Configuration management (env/.env/defaults)
- Pre-commit hooks

✅ **CI/CD Automation**
- GitHub Actions workflows (lint, test, docs, release)
- Multi-platform testing (Linux, Windows, macOS)
- Multi-version testing (Python 3.11, 3.12, 3.13)
- Coverage reporting

✅ **Professional Documentation**
- README with quick start and template guidance
- Architecture overview and design decisions (ADRs)
- Contributing guidelines with development workflow
- Customization checklist (TEMPLATE_TODO.md)
- MkDocs setup for documentation sites

## Important: This Is NOT a Library or CLI Tool

This template includes example code (config, logging, CLI, utilities) to demonstrate how to structure a project. When users download this template, they should:
1. Rename their package
2. Delete or adapt the example code
3. Add their own business logic

**The template is not meant to be used directly** — it's a starting point.

## Key Files for Template Users

| File | Purpose |
|------|---------|
| **TEMPLATE_TODO.md** | Step-by-step customization checklist (10 steps) |
| **README.md** | Updated with "Using This Template" section |
| **CONTRIBUTING.md** | Development and release workflow |
| **docs/architecture.md** | System design reference |
| **docs/adr/** | Architecture Decision Records examples |

## No CLI Entry Point

The `--cli-entry-point` was **intentionally removed** from `pyproject.toml` because:
- Template users won't accidentally publish a generic CLI tool
- Example CLI code is marked for deletion
- Users define their own entry points

## Example Code is Marked for Deletion

All example code includes `[TEMPLATE]` comments:
- `src/python_project_template/utils/basic_ops.py` — Example utility class
- `src/python_project_template/main.py` — Example CLI using Typer
- `tests/test_basic_ops.py` — Example tests

Users should delete or adapt these to their needs.

## For Future Maintenance

### If Updating the Template
1. Keep the same overengineered principles (type safety, testing, CI/CD)
2. Update docs to clarify template-specific guidance
3. Mark any example code clearly with `[TEMPLATE]` comments
4. Run `make check` to verify all quality gates pass
5. Test the customization checklist (TEMPLATE_TODO.md) is still accurate

### Releasing Template Updates
This template itself doesn't need semantic versioning / PyPI releases because it's a GitHub template. Just fix bugs and push to `main`. GitHub templates always use the latest `main` branch.

### Testing the Template
To verify users can customize this:
1. Create a test repo from the template
2. Follow TEMPLATE_TODO.md steps
3. Run `make check` and verify it passes
4. Confirm example code deletion doesn't break workflows

## CI/CD Workflows Included

| Workflow | File | Runs On |
|----------|------|---------|
| Lint & Format Check | `.github/workflows/lint-test.yml` | Push + PR |
| Multi-version Tests | Same as above | Push + PR |
| Coverage Report | Same as above | Push + PR |
| Docs Build | `.github/workflows/docs-build.yml` | Push + PR |
| Release (optional) | `.github/workflows/release.yml` | Git tags |

Users can disable the release workflow if they don't publish to PyPI/GitHub Releases.

## Common Template Pitfalls for Users (Document This)

Users might:
1. ❌ Try to use this as a library/CLI tool directly
   - ✅ Solution: Remind them to read "Using This Template" in README

2. ❌ Not rename the package and end up with `python_project_template` everywhere
   - ✅ Solution: Step 3 in TEMPLATE_TODO.md covers this

3. ❌ Leave example code and wonder why coverage is low
   - ✅ Solution: TEMPLATE_TODO.md Step 2 explains what example code is

4. ❌ Forget to update CI/CD workflows for their Python versions
   - ✅ Solution: TEMPLATE_TODO.md Step 5 covers CI/CD customization

---

## Summary

This is a **professional, overengineered GitHub template** that provides:
- Best practices for Python project structure
- Production-ready tooling and automation
- Clear guidance for users to customize it

Users download it, follow TEMPLATE_TODO.md, and build their own projects on top.
