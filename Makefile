.PHONY: help install precommit lint format test type-check cov check clean version docs docs-serve ralph-help

UV = uv --cache-dir .uv-cache
UV_TOOL = $(UV) tool run

help:
	@echo "Common targets:"
	@echo " install - Install package and dev deps with uv"
	@echo " precommit - Install git hooks"
	@echo " lint - Run ruff lint"
	@echo " format - Run ruff format + docformatter"
	@echo " test - Run pytest"
	@echo " type-check - Run ty type checker"
	@echo " cov - Run pytest with coverage report"
	@echo " check - Lint + type-check + tests"
	@echo " docs - Build MkDocs documentation (generates site/)"
	@echo " docs-serve - Serve MkDocs locally (http://127.0.0.1:8000)"
	@echo " ralph-help - Show Ralph CLI help"
	@echo " version - Show current version"
	@echo " clean - Remove build/test artifacts"


install:
	$(UV) sync --all-groups
	$(UV_TOOL) pre-commit install


precommit:
	$(UV_TOOL) pre-commit run --all-files


lint:
	$(UV) run ruff check .


format:
	$(UV) run ruff format .
	$(UV) run docformatter --in-place --recursive src tests


test:
	$(UV) run -m pytest


type-check:
	$(UV) run ty check src tests


cov:
	$(UV) run -m pytest --cov=src/python_project_template --cov-report=term-missing --cov-report=html
	@echo "Coverage HTML report generated: htmlcov/index.html"


check: lint type-check test


docs:
	cd docs && mkdocs build --strict --site-dir ../site
	@echo "Documentation built: site/index.html"


docs-serve:
	cd docs && mkdocs serve


ralph-help:
	@$(UV) run ralph --help


version:
	@$(UV) run python -c "from python_project_template import __version__; print(__version__)"


clean:
	$(UV) run python -c "import shutil, os, sys; \
	[shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache','.ruff_cache','htmlcov','build','dist','site']]; \
	[os.remove(f) for f in ['.coverage'] if os.path.exists(f)]; \
	[shutil.rmtree(os.path.join(root, d), ignore_errors=True) for root, dirs, files in os.walk('.') for d in dirs if d == '__pycache__']"
