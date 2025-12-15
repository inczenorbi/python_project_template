.PHONY: help install precommit lint format test cov check clean


help:
	@echo "Common targets:"
	@echo " install - Install package and dev deps with uv"
	@echo " precommit - Install git hooks"
	@echo " lint - Run ruff lint"
	@echo " format - Run ruff format + docformatter"
	@echo " test - Run pytest"
	@echo " cov - Run pytest with coverage"
	@echo " check - Lint + tests"
	@echo " clean - Remove build/test artifacts"


install:
	uv pip install -e .[dev]
	uvx pre-commit install


precommit:
	uvx pre-commit run --all-files


lint:
	uvx ruff check .


format:
	uvx ruff format .
	uvx docformatter --in-place --recursive src tests


test:
	uv run -m pytest


cov:
	uv run -m pytest --cov=python_project_template --cov-report=term-missing


check: lint test


clean:
	uv run python -c "import shutil, os, sys; \
	[shutil.rmtree(p, ignore_errors=True) for p in ['.pytest_cache','.mypy_cache','.ruff_cache','htmlcov','build','dist','site']]; \
	[os.remove(f) for f in ['.coverage'] if os.path.exists(f)]; \
	[shutil.rmtree(os.path.join(root, d), ignore_errors=True) for root, dirs, files in os.walk('.') for d in dirs if d == '__pycache__']"