"""CLI for the Ralph loop planning runtime."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import click
import typer

from python_project_template.config import get_config, reset_config
from python_project_template.logging import setup_logging
from python_project_template.ralph.config import RalphConfig, RalphConfigurationError
from python_project_template.ralph.engine import (
    IterationLimitError,
    PhaseValidationError,
    RalphEngine,
)
from python_project_template.ralph.provider import (
    ChatProvider,
    CodexCliProvider,
    OpenAICompatibleChatProvider,
    ProviderError,
)

app = typer.Typer(
    name="ralph",
    help="Autonomous Ralph loop CLI for project planning and prompt-pack generation.",
    no_args_is_help=True,
)


def build_provider(config: RalphConfig) -> ChatProvider:
    """Construct the configured Ralph provider."""
    if config.provider == "codex":
        return CodexCliProvider(
            codex_command=config.codex_command,
            working_dir=Path.cwd(),
            timeout_seconds=config.timeout_seconds,
            use_oss=config.codex_oss,
            local_provider=config.codex_local_provider,
        )
    if config.provider == "openai":
        if not config.api_key:
            raise RalphConfigurationError("RALPH_API_KEY is required for the openai provider.")
        return OpenAICompatibleChatProvider(
            api_base_url=config.api_base_url,
            api_key=config.api_key,
            timeout_seconds=config.timeout_seconds,
        )
    raise RalphConfigurationError(f"Unsupported provider: {config.provider}")


def _resolve_goal(goal: str | None) -> str:
    if goal and goal.strip():
        return goal.strip()

    stdin = click.get_text_stream("stdin")
    if not stdin.isatty():
        streamed = stdin.read().strip()
        if streamed:
            return streamed

    raise typer.BadParameter(
        "Provide --goal or pipe a project brief on stdin.",
        param_hint="--goal",
    )


def _build_ralph_config(
    *,
    model: str | None,
    temperature: float,
    max_iterations: int | None,
    output_dir: Path | None,
) -> RalphConfig:
    base_config = get_config()
    return RalphConfig(
        provider=base_config.ralph_provider,
        codex_command=base_config.ralph_codex_command,
        codex_oss=base_config.ralph_codex_oss,
        codex_local_provider=base_config.ralph_codex_local_provider,
        api_base_url=base_config.ralph_api_base_url,
        api_key=base_config.ralph_api_key,
        model=model or base_config.ralph_model,
        temperature=temperature,
        timeout_seconds=base_config.ralph_timeout_seconds,
        max_iterations=max_iterations or base_config.ralph_max_iterations,
        output_dir=output_dir or base_config.ralph_output_dir,
    )


@app.command()
def run(
    goal: Annotated[
        str | None,
        typer.Option("--goal", help="Free-form project brief."),
    ] = None,
    context_file: Annotated[
        list[Path] | None,
        typer.Option(
            "--context-file",
            help="Additional repo or product context files to include.",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ] = None,
    constraints: Annotated[
        str | None,
        typer.Option(
            "--constraints",
            help="Explicit delivery constraints to enforce during planning.",
        ),
    ] = None,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", help="Root directory for Ralph session outputs."),
    ] = None,
    max_iterations: Annotated[
        int | None,
        typer.Option(
            "--max-iterations",
            min=1,
            help="Maximum number of Ralph refinement retries.",
        ),
    ] = None,
    model: Annotated[
        str | None,
        typer.Option(
            "--model",
            help="Optional model override for the active provider.",
        ),
    ] = None,
    temperature: Annotated[
        float,
        typer.Option(
            "--temperature",
            min=0.0,
            max=2.0,
            help="Sampling temperature for all Ralph phase calls.",
        ),
    ] = 0.2,
    dry_run: Annotated[
        bool,
        typer.Option(
            "--dry-run",
            help="Validate configuration and inputs without contacting the provider.",
        ),
    ] = False,
) -> None:
    """Run the Ralph planning loop and persist the generated prompt pack."""
    reset_config()
    context_files = context_file or []
    resolved_goal = _resolve_goal(goal)
    config = _build_ralph_config(
        model=model,
        temperature=temperature,
        max_iterations=max_iterations,
        output_dir=output_dir,
    )
    try:
        config.validate()
    except RalphConfigurationError as exc:
        typer.echo(f"Configuration error: {exc}", err=True)
        raise typer.Exit(2) from exc

    if dry_run:
        typer.echo("Ralph configuration is valid.")
        typer.echo(f"Provider: {config.provider}")
        typer.echo(f"Goal length: {len(resolved_goal)}")
        typer.echo(f"Output root: {config.output_dir}")
        typer.echo(f"Model: {config.model or '<auto>'}")
        typer.echo(f"Context files: {len(context_files)}")
        raise typer.Exit(0)

    app_config = get_config()
    logger = setup_logging(
        __name__,
        level=app_config.log_level,
        json_format=app_config.log_format == "json",
    )
    engine = RalphEngine(
        provider=build_provider(config),
        config=config,
        logger=logger,
    )
    try:
        session = engine.run(
            goal=resolved_goal,
            constraints=constraints,
            context_files=context_files,
        )
    except (
        IterationLimitError,
        PhaseValidationError,
        ProviderError,
        RalphConfigurationError,
    ) as exc:
        typer.echo(f"Ralph loop failed: {exc}", err=True)
        if engine.latest_output_dir is not None:
            typer.echo(f"Failure artifacts: {engine.latest_output_dir}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"Ralph loop completed: {session.output_dir}")
    typer.echo(f"Tasks: {len(session.tasks)}")
    typer.echo(f"Prompts: {len(session.prompt_artifacts)}")
    typer.echo(f"Summary: {session.executive_summary}")


@app.command()
def resume(
    session_dir: Annotated[
        Path,
        typer.Argument(
            help="Existing Ralph session directory containing session.json.",
            exists=True,
            file_okay=False,
            dir_okay=True,
            readable=True,
        ),
    ],
    max_iterations: Annotated[
        int | None,
        typer.Option(
            "--max-iterations",
            min=1,
            help="Maximum number of Ralph refinement retries for the resumed run.",
        ),
    ] = None,
    model: Annotated[
        str | None,
        typer.Option(
            "--model",
            help="Optional model override for the active provider.",
        ),
    ] = None,
    temperature: Annotated[
        float,
        typer.Option(
            "--temperature",
            min=0.0,
            max=2.0,
            help="Sampling temperature for all Ralph phase calls.",
        ),
    ] = 0.2,
) -> None:
    """Resume a previously failed or interrupted Ralph session."""
    reset_config()
    config = _build_ralph_config(
        model=model,
        temperature=temperature,
        max_iterations=max_iterations,
        output_dir=None,
    )
    try:
        config.validate()
    except RalphConfigurationError as exc:
        typer.echo(f"Configuration error: {exc}", err=True)
        raise typer.Exit(2) from exc

    app_config = get_config()
    logger = setup_logging(
        __name__,
        level=app_config.log_level,
        json_format=app_config.log_format == "json",
    )
    engine = RalphEngine(
        provider=build_provider(config),
        config=config,
        logger=logger,
    )
    try:
        session = engine.resume(session_dir=session_dir)
    except (
        IterationLimitError,
        PhaseValidationError,
        ProviderError,
        RalphConfigurationError,
    ) as exc:
        typer.echo(f"Ralph resume failed: {exc}", err=True)
        typer.echo(f"Failure artifacts: {session_dir}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"Ralph loop resumed: {session.output_dir}")
    typer.echo(f"Tasks: {len(session.tasks)}")
    typer.echo(f"Prompts: {len(session.prompt_artifacts)}")
    typer.echo(f"Summary: {session.executive_summary}")


@app.command()
def diagnose() -> None:
    """Display resolved runtime and Ralph configuration."""
    reset_config()
    config = get_config()
    logger = setup_logging(
        __name__,
        level=config.log_level,
        json_format=config.log_format == "json",
    )

    typer.echo("\n=== Ralph Diagnostics ===\n")
    typer.echo(f"Environment: {config.environment}")
    typer.echo(f"Debug Mode: {config.debug}")
    typer.echo(f"Log Level: {config.log_level}")
    typer.echo(f"Log Format: {config.log_format}")
    typer.echo(f"Ralph Provider: {config.ralph_provider}")
    typer.echo(f"Ralph Codex Command: {config.ralph_codex_command}")
    typer.echo(f"Ralph Codex OSS: {config.ralph_codex_oss}")
    typer.echo(f"Ralph Codex Local Provider: {config.ralph_codex_local_provider or '<unset>'}")
    typer.echo(f"Ralph API Base URL: {config.ralph_api_base_url}")
    typer.echo(f"Ralph API Key Present: {bool(config.ralph_api_key)}")
    typer.echo(f"Ralph Model: {config.ralph_model or '<auto>'}")
    typer.echo(f"Ralph Timeout Seconds: {config.ralph_timeout_seconds}")
    typer.echo(f"Ralph Max Iterations: {config.ralph_max_iterations}")
    typer.echo(f"Ralph Output Dir: {config.ralph_output_dir}")

    logger.info(
        "Diagnostic check completed",
        extra={
            "environment": config.environment,
            "debug": config.debug,
            "model": config.ralph_model or "<unset>",
        },
    )

    typer.echo("\nRalph CLI is ready.\n")


def main() -> None:
    """Entry point for the CLI application."""
    app()


if __name__ == "__main__":
    main()
