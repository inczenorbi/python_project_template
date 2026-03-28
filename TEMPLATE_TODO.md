# Template Customization Checklist

This template has been set up with overengineered best practices for production Python projects. Use this checklist to customize it for your project.

## Before You Start

- [ ] Create a new GitHub repository from this template, or clone and customize it
- [ ] Decide on your project name and update it consistently

## 1. Project Metadata

- [ ] Update `pyproject.toml`
  - [ ] Set `name` to your project name (for example, `my-awesome-project`)
  - [ ] Set `description` to what your project does
  - [ ] Confirm `requires-python` matches your supported version range
  - [ ] Add author information under `[project]` if needed
- [ ] Rename `src/python_project_template/`
  - [ ] Rename it to match your project name
  - [ ] Update imports throughout the codebase
- [ ] Update `.python-version` if needed
  - [ ] The current pin is `3.11`

## 2. Example Code

### Option A: Keep and Adapt the Example Code

- [ ] Rename `src/python_project_template/utils/basic_ops.py` to match your domain
- [ ] Replace `BasicOperations` with your actual business logic
- [ ] Update `tests/test_basic_ops.py` to test your code
- [ ] Update `main.py` to use your own logic instead of the calculator example

### Option B: Delete the Example Code

```bash
rm src/python_project_template/utils/basic_ops.py
rm tests/test_basic_ops.py
# Clear or remove main.py
```

- [ ] Delete the example files
- [ ] Remove example imports from `__init__.py` and other modules
- [ ] Update `main.py` to provide your own entry point, or delete it if you do not need one

## 3. Configuration and Logging

- [ ] Review `src/python_project_template/config.py` and adjust settings for your needs
- [ ] Review `src/python_project_template/logging.py` and customize it if needed
- [ ] Update `.env.example` with your configuration options

## 4. Documentation

- [ ] Update `README.md`
  - [ ] Replace the project description
  - [ ] Update quick-start examples
  - [ ] Update features and architecture sections
  - [ ] Update development and testing instructions
  - [ ] Remove the "Using This Template" section once you are done customizing
- [ ] Update `docs/index.md`
  - [ ] Write your project's landing page
- [ ] Update `docs/architecture.md`
  - [ ] Replace the system architecture diagram
  - [ ] Update module descriptions
  - [ ] Document your design decisions
- [ ] Update `docs/usage.md`
  - [ ] Replace it with usage examples for your project
- [ ] Review Architecture Decision Records in `docs/adr/`
  - [ ] Delete example ADRs
  - [ ] Add your own ADRs as you make important decisions
- [ ] Update `CONTRIBUTING.md`
  - [ ] Customize development workflow guidance
  - [ ] Adjust standards for your team
  - [ ] Keep or remove the release process section based on your publishing strategy

## 5. CI/CD Configuration

- [ ] Review `.github/workflows/lint-test.yml`
  - [ ] Adjust the Python version matrix if needed
  - [ ] Adjust the OS matrix if needed
  - [ ] Modify the coverage threshold if needed
- [ ] Review `.github/workflows/docs-build.yml`
  - [ ] Verify the MkDocs build strategy
- [ ] Review `.github/workflows/release.yml`
  - [ ] If publishing to PyPI, add the `PYPI_API_TOKEN` secret and enable the publish step
  - [ ] If not publishing, delete the workflow or keep it only for GitHub Releases
  - [ ] Configure branch protection rules in GitHub

## 6. Version Control and Releases

- [ ] Choose a versioning strategy
  - [ ] Use `bumpversion` for semantic versioning
  - [ ] Or manage versions manually
  - [ ] Or remove version management entirely if you do not need it
- [ ] Update `CHANGELOG.md`
  - [ ] Delete the example entries
  - [ ] Start fresh with your first release

## 7. Code Quality Tools

Review and customize these files if needed:

- [ ] `ruff.toml` for linting and formatting rules
- [ ] `pyproject.toml` for `ty`, coverage, and Bandit configuration
- [ ] `.pre-commit-config.yaml` for git hooks
- [ ] Adjust `ty` configuration to match your team's type-checking standards

## 8. Repository Setup

- [ ] Create a `.github/CODEOWNERS` file for your team
- [ ] Set up branch protection rules
  - [ ] Require pull request reviews
  - [ ] Require status checks to pass
  - [ ] Restrict who can push to `main`
- [ ] Add issue and pull request templates
  - [ ] Create `.github/ISSUE_TEMPLATE/`
  - [ ] Create `.github/PULL_REQUEST_TEMPLATE.md`

## 9. Optional Advanced Setup

- [ ] Add a `Dockerfile` if you deploy in containers
- [ ] Add a devcontainer if your team uses VS Code remote development
- [ ] Set up PyPI or TestPyPI publishing if you distribute the project
- [ ] Add API documentation generation such as `mkdocstrings`
- [ ] Add performance benchmarking such as `pytest-benchmark`

## 10. Final Steps

- [ ] Run `make check` to verify everything passes locally
- [ ] Commit your changes: `git add . && git commit -m "Customize template for my-project"`
- [ ] Push to GitHub: `git push origin main`
- [ ] Verify CI/CD workflows pass on GitHub
- [ ] Add your first real feature

## After Customization

You should have a production-ready Python project with:

- [ ] Type-safe code checked with `ty`
- [ ] Structured logging
- [ ] Configuration management
- [ ] Comprehensive testing with coverage
- [ ] Cross-platform CI/CD
- [ ] Security scanning
- [ ] Code quality enforcement with Ruff and `ty`
- [ ] Professional documentation
- [ ] Version management

## Troubleshooting

### I deleted example code but tests still fail

- Delete `tests/test_basic_ops.py`
- Update `tests/` with your own tests

### I renamed my package but imports are broken

- Update imports throughout the codebase
- Run `make check` to find remaining references

### My CI/CD workflows are failing

- Check GitHub Actions logs
- Verify Python version and dependency installation
- Run `make check` locally first

For more detail, see `docs/architecture.md` and `CONTRIBUTING.md`.
