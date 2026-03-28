# Usage Guide

**[TEMPLATE]** This guide documents the example CLI included in this template. When you customize this project, replace this with your own usage examples.

---

## Installation

```bash
# From source (development)
git clone https://github.com/yourorg/python-project-template
cd python-project-template
make install

# From PyPI (when published)
pip install python-project-template
```

## Using the CLI

The project provides a CLI tool: `python-project-template`

### Prerequisites

Ensure the package is installed:
```bash
make install
```

### Available Commands

#### `calculate` — Perform Math Operations

```bash
# Add numbers
python-project-template calculate add 2 3
# Output: Result: 5.0

# Subtract
python-project-template calculate subtract 10 3
# Output: Result: 7.0

# Multiply
python-project-template calculate multiply 4 5
# Output: Result: 20.0

# Divide
python-project-template calculate divide 10 2
# Output: Result: 5.0

# Power
python-project-template calculate power 2 3
# Output: Result: 8.0
```

#### `diagnose` — Show Application Status

```bash
python-project-template diagnose
# Output:
# === Application Diagnostics ===
#
# Environment: dev
# Debug Mode: False
# Log Level: INFO
# Log Format: plain
#
# ✅ Application is ready to use.
```

#### `demo` — Run Sample Calculations

```bash
python-project-template demo
# Output:
# === Demo Calculations ===
#
# add: 3.0
# subtract: 2.0
# multiply: 6.0
# divide: 3.5
# power: 8.0
#
# ✅ Demo completed successfully.
```

#### Get Help

```bash
python-project-template --help          # Show all commands
python-project-template calculate --help  # Help for specific command
```

## Documentation

### Building Documentation Locally

The project uses MkDocs with Material theme for documentation.

**Setup:** MkDocs is installed with `make install` (included in the `docs` dependency group).

**Build the docs:**
```bash
make docs
# or directly:
cd docs && mkdocs build --strict --site-dir ../site
```

Generated HTML will be in `site/index.html`.

**Serve docs locally (live reload):**
```bash
make docs-serve
# or directly:
cd docs && mkdocs serve
```

Then visit `http://127.0.0.1:8000` in your browser.

### Customizing Docs

1. Edit Markdown files in `docs/`:
   - `docs/index.md` — Landing page
   - `docs/usage.md` — Usage guide (this file)
   - `docs/mkdocs.yml` — MkDocs configuration (theme, navigation)

2. Add new pages:
   ```yaml
   # docs/mkdocs.yml
   nav:
     - Home: index.md
     - Usage: usage.md
     - MyNewPage: my-new-page.md
   ```

## Using as a Library

Import and use the business logic directly in your code:

```python
from python_project_template.utils.basic_ops import BasicOperations

# Create an instance
calc = BasicOperations()

# Use any method
result = calc.add(10, 5)  # 15.0
result = calc.divide(10, 2)  # 5.0
result = calc.mean([1, 2, 3, 4, 5])  # 3.0
```

### Error Handling

```python
from python_project_template.utils.basic_ops import BasicOperations

calc = BasicOperations()

try:
    result = calc.divide(10, 0)
except ZeroDivisionError as e:
    print(f"Error: {e}")

try:
    result = calc.mean([])
except ValueError as e:
    print(f"Error: {e}")
```

## Configuration

All configuration options can be set via environment variables:

```bash
# Enable debug logging
DEBUG=1 python-project-template diagnose

# Use JSON structured logging
LOG_FORMAT=json python-project-template demo

# Set log level to DEBUG
LOG_LEVEL=DEBUG python-project-template calculate add 1 2

# Set environment
ENVIRONMENT=prod python-project-template diagnose
```

### Using .env File

Create a `.env` file in your project root:

```bash
# .env
DEBUG=1
LOG_LEVEL=DEBUG
LOG_FORMAT=json
ENVIRONMENT=dev
```

When you run the application, these values will be automatically loaded:

```bash
python-project-template diagnose
# Uses values from .env
```

## Logging

The application supports two logging formats:

### Plain Text (Default)

```
[INFO    ] __main__                  | Application started
[INFO    ] __main__                  | Running calculations...
[INFO    ] __main__                  | add(1, 2)
```

Human-readable, good for local development.

### JSON (Structured)

```json
{"timestamp": "2026-03-22T22:23:10Z", "level": "INFO", "logger": "__main__", "message": "Application started", "environment": "dev"}
{"timestamp": "2026-03-22T22:23:10Z", "level": "INFO", "logger": "__main__", "message": "Running calculations..."}
{"timestamp": "2026-03-22T22:23:10Z", "level": "INFO", "logger": "__main__", "message": "add(1, 2)", "result": 3.0}
```

Machine-parseable, good for log aggregation systems (ELK, Datadog, CloudWatch).

Enable JSON logging:

```bash
LOG_FORMAT=json python-project-template demo
```

## Programmatic Usage with Config and Logging

```python
from python_project_template.config import get_config
from python_project_template.logging import setup_logging
from python_project_template.utils.basic_ops import BasicOperations

# Get configuration (loads from env, .env, defaults)
config = get_config()

# Set up logger with config
logger = setup_logging(
    __name__,
    level=config.log_level,
    json_format=config.log_format == "json",
)

# Use business logic
calc = BasicOperations()
result = calc.add(5, 3)

# Log with context
logger.info("Calculation completed", extra={"result": result, "operation": "add"})
```

## Examples

### Example 1: Simple Calculator

```bash
$ python-project-template calculate add 10.5 20.3
Result: 30.8

$ python-project-template calculate divide 100 4
Result: 25.0
```

### Example 2: Debug Mode with JSON Logging

```bash
$ DEBUG=1 LOG_FORMAT=json python-project-template calculate multiply 3 4
{"timestamp": "2026-03-22T22:23:10Z", "level": "INFO", "logger": "__main__", "message": "Starting calculation: multiply", "a": 3.0, "b": 4.0}
{"timestamp": "2026-03-22T22:23:10Z", "level": "INFO", "logger": "__main__", "message": "Calculation completed: multiply(3, 4) = 12.0"}
Result: 12.0
```

### Example 3: Production Environment

```bash
$ ENVIRONMENT=prod LOG_LEVEL=WARNING python-project-template demo
# Only warnings and errors will be displayed
```

## Troubleshooting

### Command Not Found

If you get "command not found" for `python-project-template`, ensure:
1. The package is installed: `make install`
2. You're in a virtual environment with the package installed
3. Run via uv if needed: `uv run python-project-template --help`

### Configuration Not Being Loaded

Check that `.env` is in the correct location (project root):

```bash
$ cat .env
DEBUG=1
LOG_FORMAT=json

$ python-project-template diagnose
# Should show Debug Mode: True and Log Format: json
```

### Logs Not Displayed

- Check `LOG_LEVEL` is set appropriately (default is INFO)
- Try running with `DEBUG=1` to enable debug logs
- Check that `LOG_FORMAT` is correct (json or plain)

## Next Steps

- See [Development Guide](CONTRIBUTING.md) for development workflow
- Check [API Reference](#api-reference) for code documentation
