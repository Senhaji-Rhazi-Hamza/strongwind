"""Tests for every reporting query."""

from pathlib import Path

import pytest

from gpu_observability.core.generator import generate_runs
from gpu_observability.core.queries import by_model, summary, trend, waste


@pytest.fixture
def runs_file(tmp_path: Path) -> Path:
    return generate_runs(100, tmp_path / "runs.csv", seed=42)


def test_summary_groups_by_researcher(runs_file: Path) -> None:
    rows = summary(runs_file)
    assert sum(row["runs"] for row in rows) == 100
    assert {row["researcher"] for row in rows} <= {
        "alice",
        "bob",
        "carlos",
        "diana",
        "eve",
    }
    assert all("failed_runs" in row for row in rows)


def test_waste_only_contains_low_utilization(runs_file: Path) -> None:
    rows = waste(runs_file)
    assert rows
    assert all(row["gpu_utilization_pct"] < 50 for row in rows)
    assert [row["gpu_hours"] for row in rows] == sorted(
        (row["gpu_hours"] for row in rows), reverse=True
    )


def test_by_model_groups_all_runs(runs_file: Path) -> None:
    rows = by_model(runs_file)
    assert sum(row["runs"] for row in rows) == 100
    assert {row["model"] for row in rows} <= {
        "mistral-7b",
        "mistral-8x7b",
        "mistral-large",
        "codestral",
    }


def test_trend_groups_all_runs_by_date(runs_file: Path) -> None:
    rows = trend(runs_file)
    assert sum(row["runs"] for row in rows) == 100
    assert rows == sorted(rows, key=lambda row: row["date"])
