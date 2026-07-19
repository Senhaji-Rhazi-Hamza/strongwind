"""DuckDB queries for GPU workload reporting."""

from pathlib import Path
from typing import Any

import duckdb

SUMMARY_SQL = """
    SELECT researcher, COUNT(*) AS runs,
           ROUND(SUM(gpu_hours), 2) AS total_gpu_hours,
           ROUND(AVG(gpu_utilization_pct), 2) AS avg_utilization,
           COUNT(*) FILTER (WHERE status = 'failed') AS failed_runs
    FROM read_csv_auto(?)
    GROUP BY researcher ORDER BY researcher
"""
WASTE_SQL = """
    SELECT * FROM read_csv_auto(?)
    WHERE gpu_utilization_pct < 50
    ORDER BY gpu_hours DESC
"""
BY_MODEL_SQL = """
    SELECT model, COUNT(*) AS runs,
           ROUND(SUM(gpu_hours), 2) AS total_gpu_hours,
           ROUND(AVG(gpu_utilization_pct), 2) AS avg_utilization
    FROM read_csv_auto(?)
    GROUP BY model ORDER BY model
"""
TREND_SQL = """
    SELECT CAST(start_time AS DATE) AS date,
           ROUND(SUM(gpu_hours), 2) AS total_gpu_hours,
           COUNT(*) AS runs
    FROM read_csv_auto(?)
    GROUP BY CAST(start_time AS DATE) ORDER BY date
"""
FAILURE_RATE_SQL = """
    SELECT
        researcher,
        COUNT(*) AS runs,
        COUNT(*) FILTER (WHERE status = 'failed') AS failed_runs,
        ROUND(
            COUNT(*) FILTER (WHERE status = 'failed') * 100.0 / COUNT(*),
            1
        ) AS failure_rate_pct,
        ROUND(
            SUM(gpu_hours * (1 - gpu_utilization_pct / 100.0)),
            1
        ) AS wasted_gpu_hours
    FROM read_csv_auto(?)
    GROUP BY researcher
    ORDER BY failure_rate_pct DESC
"""
BY_EXPERIMENT_SQL = """
    SELECT
        experiment_type,
        COUNT(*) AS runs,
        ROUND(AVG(gpu_utilization_pct), 1) AS avg_utilization,
        ROUND(SUM(gpu_hours), 1) AS total_gpu_hours,
        ROUND(
            SUM(gpu_hours * (1 - gpu_utilization_pct / 100.0)),
            1
        ) AS wasted_gpu_hours
    FROM read_csv_auto(?)
    GROUP BY experiment_type
    ORDER BY total_gpu_hours DESC
"""


def _query(sql: str, path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        message = f"Data file not found: {path}. Run 'gpu-obs data generate'."
        raise FileNotFoundError(message)
    with duckdb.connect() as connection:
        cursor = connection.execute(sql, [str(path)])
        columns = [item[0] for item in cursor.description]
        return [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]


def summary(path: Path) -> list[dict[str, Any]]:
    return _query(SUMMARY_SQL, path)


def waste(path: Path) -> list[dict[str, Any]]:
    return _query(WASTE_SQL, path)


def by_model(path: Path) -> list[dict[str, Any]]:
    return _query(BY_MODEL_SQL, path)


def trend(path: Path) -> list[dict[str, Any]]:
    return _query(TREND_SQL, path)


def failure_rate(path: Path) -> list[dict[str, Any]]:
    return _query(FAILURE_RATE_SQL, path)


def by_experiment(path: Path) -> list[dict[str, Any]]:
    return _query(BY_EXPERIMENT_SQL, path)
