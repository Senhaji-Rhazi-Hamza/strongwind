"""Application configuration."""

import os
from pathlib import Path


def data_path() -> Path:
    """Return the configured CSV data path."""
    return Path(os.getenv("DATA_PATH", "data/runs.csv"))
