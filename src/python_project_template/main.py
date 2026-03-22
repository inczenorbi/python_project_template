"""[TEMPLATE] Example CLI using Typer. Edit or delete this file to match your project.

Command-line interface for the project using Typer.
Provides CLI commands for calculations and diagnostics with structured logging and config support.

Usage:
    python-project-template calculate --help
    python-project-template diagnose
    
Environment variables:
    DEBUG=1              Enable debug logging
    LOG_FORMAT=json      Use JSON structured logs (default: plain)
    LOG_LEVEL=DEBUG      Set log level (default: INFO)
"""

from __future__ import annotations

import typer

from python_project_template.config import get_config
from python_project_template.logging import setup_logging
from python_project_template.utils.basic_ops import BasicOperations

app = typer.Typer(
    name="python-project-template",
    help="A sample project with structured logging and config management.",
)

logger = setup_logging(
    __name__,
    level=get_config().log_level,
    json_format=get_config().log_format == "json",
)


@app.command()
def calculate(
    operation: str = typer.Argument(
        ..., help="Operation: add, subtract, multiply, divide, power"
    ),
    a: float = typer.Argument(..., help="First operand"),
    b: float | None = typer.Argument(None, help="Second operand (optional)"),
) -> None:
    """Perform a calculation using BasicOperations.

    Examples:
        python-project-template calculate add 2 3
        python-project-template calculate multiply 4 5
    """
    config = get_config()
    logger = setup_logging(
        __name__,
        level=config.log_level,
        json_format=config.log_format == "json",
    )

    calc = BasicOperations()
    logger.info(f"Starting calculation: {operation}", extra={"a": a, "b": b})

    try:
        if operation == "add":
            result = calc.add(a, b or 0)
        elif operation == "subtract":
            result = calc.subtract(a, b or 0)
        elif operation == "multiply":
            result = calc.multiply(a, b or 1)
        elif operation == "divide":
            if b is None:
                raise typer.BadParameter("divide requires two arguments")
            result = calc.divide(a, b)
        elif operation == "power":
            result = calc.power(a, b or 1)
        else:
            logger.error(f"Unknown operation: {operation}")
            raise typer.BadParameter(
                "Operation must be one of: add, subtract, multiply, divide, power"
            )

        logger.info(f"Calculation completed: {operation}({a}, {b}) = {result}")
        typer.echo(f"Result: {result}")
    except ZeroDivisionError as e:
        logger.error(f"Division by zero error: {e}")
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None
    except ValueError as e:
        logger.error(f"Value error: {e}")
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1) from None


@app.command()
def diagnose() -> None:
    """Display diagnostic information about the environment and configuration.

    Shows current configuration values, logging setup, and environment details.
    """
    config = get_config()
    logger = setup_logging(
        __name__,
        level=config.log_level,
        json_format=config.log_format == "json",
    )

    typer.echo("\n=== Application Diagnostics ===\n")

    typer.echo(f"Environment: {config.environment}")
    typer.echo(f"Debug Mode: {config.debug}")
    typer.echo(f"Log Level: {config.log_level}")
    typer.echo(f"Log Format: {config.log_format}")

    logger.info(
        "Diagnostic check completed",
        extra={"environment": config.environment, "debug": config.debug},
    )

    typer.echo("\n✅ Application is ready to use.\n")


@app.command()
def demo() -> None:
    """Run demo calculations to verify functionality."""
    config = get_config()
    logger = setup_logging(
        __name__,
        level=config.log_level,
        json_format=config.log_format == "json",
    )

    logger.info("Starting demo mode")

    calc = BasicOperations()
    operations = [
        ("add", calc.add(1, 2)),
        ("subtract", calc.subtract(5, 3)),
        ("multiply", calc.multiply(2, 3)),
        ("divide", calc.divide(7, 2)),
        ("power", calc.power(2, 3)),
    ]

    typer.echo("\n=== Demo Calculations ===\n")
    for op_name, result in operations:
        logger.info(f"Demo operation: {op_name}", extra={"result": result})
        typer.echo(f"{op_name}: {result}")

    typer.echo("\n✅ Demo completed successfully.\n")


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()

