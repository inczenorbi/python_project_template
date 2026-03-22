# Template Customization Checklist

This template has been set up with overengineered best practices for production Python projects. Use this checklist to customize it for your project.

## Before You Start

- [ ] Create a new GitHub repository from this template (or clone and customize)
- [ ] Decide on your project name and update it consistently

## 1. Project Metadata (Required)

- [ ] Update `pyproject.toml`:
  - [ ] `name` — Your project name (e.g., `my-awesome-project`)
  - [ ] `description` — What your project does
  - [ ] `requires-python` — Minimum Python version (currently `>=3.11`)
  - [ ] Add your name and email under `[project]` if needed

- [ ] Update `src/python_project_template/` folder:
  - [ ] Rename to match your project name (e.g., `src/my_awesome_project/`)
  - [ ] Update all imports in code

- [ ] Update `.python-version` if needed:
  - [ ] Current pin is 3.11; adjust if your project targets different versions

## 2. Example Code (Choose One Approach)

### Option A: Keep and Adapt Example Code
- [ ] Rename `src/python_project_template/utils/basic_ops.py` to your domain
- [ ] Replace the `BasicOperations` class with your actual business logic
- [ ] Update `tests/test_basic_ops.py` to test your code
- [ ] Update `main.py` to use your logic instead of the calculator example

### Option B: Delete Example Code Entirely
```bash
rm src/python_project_template/utils/basic_ops.py
rm tests/test_basic_ops.py
# Clear or remove main.py
```
- [ ] Delete the files listed above
- [ ] Remove example imports from `__init__.py` and other modules
- [ ] Update `main.py` to provide your own entry point (or delete if not needed)

## 3. Configuration & Logging

- [ ] Review `src/python_project_template/config.py` — adjust settings for your needs
- [ ] Review `src/python_project_template/logging.py` — customize if needed
- [ ] Update `.env.example` with your configuration options

## 4. Documentation

- [ ] Update `README.md`:
  - [ ] Replace project description with yours
  - [ ] Update quickstart examples
  - [ ] Update features and architecture sections
  - [ ] Update development/testing instructions
  - [ ] Remove "Using This Template" section once you've customized

- [ ] Update `docs/index.md`:
  - [ ] Write your project's landing page

- [ ] Update `docs/architecture.md`:
  - [ ] Replace system architecture diagram with yours
  - [ ] Update module descriptions
  - [ ] Document your design decisions

- [ ] Update `docs/usage.md`:
  - [ ] Replace with usage examples for your project

- [ ] Architecture Decision Records (ADRs):
  - [ ] Delete example ADRs in `docs/adr/`
  - [ ] Add your own ADRs as you make important decisions

- [ ] Update `CONTRIBUTING.md`:
  - [ ] Customize development workflow guidance
  - [ ] Adjust standards for your team
  - [ ] Keep or remove the release process section based on your publishing strategy

## 5. CI/CD Configuration

- [ ] Review `.github/workflows/lint-test.yml`:
  - [ ] Adjust Python version matrix if needed (currently 3.11, 3.12, 3.13)
  - [ ] Adjust OS matrix if needed (currently Ubuntu, Windows, macOS)
  - [ ] Modify coverage threshold if needed (currently 80%)

- [ ] Review `.github/workflows/docs-build.yml`:
  - [ ] Verify MkDocs build strategy

- [ ] `.github/workflows/release.yml`:
  - [ ] **If you're publishing to PyPI**: Set up `PYPI_API_TOKEN` secret in GitHub and uncomment the publish step
  - [ ] **If you're not publishing**: Delete this workflow or just use it for GitHub Releases
  - [ ] Configure branch protection rules in GitHub (Settings → Branches → Add Rule)

## 6. Version Control & Releases

- [ ] Choose versioning strategy:
  - [ ] Use `bumpversion` for semantic versioning (configured in `pyproject.toml`)
  - [ ] Or manage versions manually
  - [ ] Or remove version management entirely if not needed

- [ ] Update `CHANGELOG.md`:
  - [ ] Delete example entries
  - [ ] Start fresh with your first release

## 7. Code Quality Tools

Review and customize if needed:
- [ ] `ruff.toml` — Linting and formatting rules
- [ ] `pyproject.toml` — Mypy, coverage, and bandit configurations
- [ ] `.pre-commit-config.yaml` — Git hooks

## 8. Repository Setup

- [ ] Create a `.github/CODEOWNERS` file for your team
- [ ] Set up branch protection rules:
  - [ ] Require PR reviews
  - [ ] Require status checks to pass
  - [ ] Restrict who can push to main

- [ ] Update issue/PR templates in `.github/`:
  - [ ] Create `.github/ISSUE_TEMPLATE/` directory
  - [ ] Create `.github/PULL_REQUEST_TEMPLATE.md`

## 9. Optional: Advanced Setup

- [ ] **Dockerfile** — Add if deploying in containers
- [ ] **Devcontainer** — Add `.devcontainer/devcontainer.json` for VS Code remote dev
- [ ] **Publishing** — Set up PyPI/TestPyPI publishing if distributing as a library
- [ ] **API Documentation** — Add mkdocstrings plugin for auto-generated API docs
- [ ] **Performance Benchmarks** — Add pytest-benchmark for performance testing

## 10. Final Steps

- [ ] Run `make check` to verify everything passes locally
- [ ] Commit your changes: `git add . && git commit -m "Customize template for my-project"`
- [ ] Push to GitHub: `git push origin main`
- [ ] Verify CI/CD workflows pass on GitHub
- [ ] Add your first feature! 🚀

---

## After Customization: What You Have

A production-ready Python project with:
- ✅ Type-safe code (mypy strict mode)
- ✅ Structured logging (JSON + plain text)
- ✅ Configuration management (env/.env/defaults)
- ✅ Comprehensive testing (pytest, 80%+ coverage)
- ✅ Cross-platform CI/CD (GitHub Actions)
- ✅ Security scanning (Bandit)
- ✅ Code quality enforcement (Ruff, type checking)
- ✅ Professional documentation (MkDocs, ADRs)
- ✅ Version management (Bumpversion)

## Troubleshooting

### I deleted example code but tests still fail
- Delete `tests/test_basic_ops.py`
- Update `tests/` with your own tests

### I renamed my package but imports are broken
- Update all imports in code to use new package name
- Run `make check` to find any remaining references

### My CI/CD workflows are failing
- Check GitHub Actions logs (Actions tab in your repo)
- Verify Python version and dependency installation
- Run `make check` locally first to debug

---

**Questions?** Refer to the [Architecture Overview](docs/architecture.md) and [Development Guide](CONTRIBUTING.md) for more details.
