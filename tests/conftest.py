"""Shared fixtures for redmoon tests."""

from pathlib import Path

import pandas as pd
import pytest

SAMPLE_DIR = Path(__file__).resolve().parent.parent / "sample_data"


@pytest.fixture()
def sample_data() -> dict[str, pd.DataFrame]:
    """Load sample CSVs into the dict format expected by CycleSleepAnalyzer."""
    return {
        "sleep": pd.read_csv(SAMPLE_DIR / "sleep.csv", parse_dates=["start", "end"]),
        "menstrual": pd.read_csv(SAMPLE_DIR / "menstrual.csv"),
        "wrist_temp": pd.read_csv(SAMPLE_DIR / "wrist_temp.csv"),
        "hrv": pd.read_csv(SAMPLE_DIR / "hrv.csv"),
        "resting_hr": pd.read_csv(SAMPLE_DIR / "resting_hr.csv"),
        "breathing": pd.read_csv(SAMPLE_DIR / "breathing.csv"),
    }


@pytest.fixture()
def minimal_data() -> dict[str, pd.DataFrame]:
    """Minimal dataset with only the required keys (sleep + menstrual)."""
    return {
        "sleep": pd.read_csv(SAMPLE_DIR / "sleep.csv", parse_dates=["start", "end"]),
        "menstrual": pd.read_csv(SAMPLE_DIR / "menstrual.csv"),
    }
