"""Data management CLI commands."""

import csv
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any

import click
import duckdb

from gpu_observability.config import data_path
from gpu_observability.core.generator import generate_runs
from gpu_observability.core.queries import summary


def _print_table(rows: list[dict[str, Any]]) -> None:
    if not rows:
        click.echo("No rows.")
        return
    headers = list(rows[0])
    widths = {
        header: max(len(header), *(len(str(row[header])) for row in rows))
        for header in headers
    }
    click.echo("  ".join(header.ljust(widths[header]) for header in headers))
    click.echo("  ".join("-" * widths[header] for header in headers))
    for row in rows:
        values = (str(row[header]).ljust(widths[header]) for header in headers)
        click.echo("  ".join(values))


@click.group()
def data() -> None:
    """Generate, inspect, and export run data."""


@data.command("generate")
@click.option("--rows", type=click.IntRange(min=1), default=500, show_default=True)
@click.option("--path", "path_", type=click.Path(path_type=Path), default=None)
def generate(rows: int, path_: Path | None) -> None:
    """Generate simulated GPU run data."""
    path = generate_runs(rows, path_ or data_path())
    click.echo(f"Generated {rows} runs in {path}")


@data.command("show")
def show() -> None:
    """Print a summary grouped by researcher."""
    try:
        _print_table(summary(data_path()))
    except FileNotFoundError as error:
        raise click.ClickException(str(error)) from error


@data.command("export")
@click.option("format_", "--format", type=click.Choice(["csv", "json"]), required=True)
@click.option("--output", type=click.Path(path_type=Path), default=None)
def export(format_: str, output: Path | None) -> None:
    """Export all generated runs as CSV or JSON."""
    source = data_path()
    if not source.is_file():
        raise click.ClickException(f"Data file not found: {source}")
    destination = output or Path("data") / f"runs-export.{format_}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with duckdb.connect() as connection:
        cursor = connection.execute("SELECT * FROM read_csv_auto(?)", [str(source)])
        headers = [item[0] for item in cursor.description]
        rows = cursor.fetchall()
    if format_ == "csv":
        with destination.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(headers)
            writer.writerows(rows)
    else:
        records = [dict(zip(headers, row, strict=True)) for row in rows]
        destination.write_text(
            json.dumps(records, indent=2, default=_json_default), encoding="utf-8"
        )
    click.echo(f"Exported {len(rows)} runs to {destination}")


def _json_default(value: Any) -> str:
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return str(value)
