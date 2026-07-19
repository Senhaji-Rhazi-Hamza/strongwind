"""Top-level CLI commands."""

import platform

import click

from gpu_observability import __version__
from gpu_observability.cli.data import data
from gpu_observability.config import data_path


@click.group()
@click.version_option(__version__)
def cli() -> None:
    """Inspect simulated GPU workloads."""


@cli.command()
def info() -> None:
    """Print stack and data source information."""
    click.echo(f"gpu-observability {__version__}")
    click.echo(f"Python {platform.python_version()} | DuckDB | Sanic | Grafana")
    click.echo(f"Data source: {data_path()}")


cli.add_command(data)
