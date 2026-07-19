"""Generate simulated GPU workload data."""

import csv
import random
from pathlib import Path

from faker import Faker

RESEARCHERS = ("alice", "bob", "carlos", "diana", "eve")
MODELS = ("mistral-7b", "mistral-8x7b", "mistral-large", "codestral")
EXPERIMENT_TYPES = ("pretraining", "finetuning", "eval", "rlhf")
GPU_COUNTS = (1, 2, 4, 8)
FIELDNAMES = (
    "run_id",
    "researcher",
    "model",
    "experiment_type",
    "gpu_count",
    "gpu_utilization_pct",
    "duration_hours",
    "gpu_hours",
    "status",
    "start_time",
)


def generate_runs(rows: int, output_path: Path, seed: int | None = None) -> Path:
    """Generate *rows* simulated runs and write them to a CSV file."""
    if rows < 1:
        raise ValueError("rows must be greater than zero")

    rng = random.Random(seed)
    fake = Faker()
    if seed is not None:
        fake.seed_instance(seed)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDNAMES)
        writer.writeheader()
        for index in range(1, rows + 1):
            duration = round(rng.uniform(0.5, 48), 2)
            gpu_count = rng.choice(GPU_COUNTS)
            writer.writerow(
                {
                    "run_id": index,
                    "researcher": rng.choice(RESEARCHERS),
                    "model": rng.choice(MODELS),
                    "experiment_type": rng.choice(EXPERIMENT_TYPES),
                    "gpu_count": gpu_count,
                    "gpu_utilization_pct": round(rng.uniform(20, 100), 2),
                    "duration_hours": duration,
                    "gpu_hours": round(duration * gpu_count, 2),
                    "status": rng.choices(
                        ("completed", "failed"), weights=(75, 25), k=1
                    )[0],
                    "start_time": fake.date_time_between(
                        start_date="-30d", end_date="now"
                    ).isoformat(sep=" "),
                }
            )
    return output_path
