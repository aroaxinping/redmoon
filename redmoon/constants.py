"""
Shared constants and phase-assignment logic for redmoon.

All magic numbers are documented here so they can be tuned in one place.
"""

from __future__ import annotations

import pandas as pd

# ---------------------------------------------------------------------------
# Cycle phase configuration
# ---------------------------------------------------------------------------

PHASE_ORDER: list[str] = ["Menstrual", "Folicular", "Ovulatoria", "Lútea"]

PHASE_COLORS: dict[str, str] = {
    "Menstrual": "#e74c3c",
    "Folicular": "#3498db",
    "Ovulatoria": "#2ecc71",
    "Lútea": "#f39c12",
}

# Proportional boundaries within a cycle (fraction of cycle length).
# Based on a textbook 28-day cycle:
#   Follicular ≈ days 6-13  → ends at ~46% of the cycle
#   Ovulatory  ≈ days 14-16 → ends at ~57% of the cycle
#   Luteal     = remainder
FOLLICULAR_END_FRAC: float = 0.46
OVULATORY_END_FRAC: float = 0.57

# ---------------------------------------------------------------------------
# Sleep filtering thresholds
# ---------------------------------------------------------------------------

# Minimum total sleep (minutes) to consider a night valid.
MIN_SLEEP_MIN: int = 120  # 2 hours

# Maximum time in bed (minutes) — nights longer than this are likely errors.
MAX_INBED_MIN: int = 960  # 16 hours

# Hour threshold: sleep records before this hour belong to the previous night.
EARLY_MORNING_CUTOFF: int = 6

# ---------------------------------------------------------------------------
# Cycle filtering
# ---------------------------------------------------------------------------

# Cycles shorter or longer than these bounds are excluded as anomalous.
MIN_CYCLE_DAYS: int = 21
MAX_CYCLE_DAYS: int = 45

# Days between bleeding records to consider a new period started.
NEW_PERIOD_GAP_DAYS: int = 5

# Days before period start that count as "premenstrual" within the luteal phase.
PREMENSTRUAL_WINDOW_DAYS: int = 5

# ---------------------------------------------------------------------------
# Metric labels (Spanish)
# ---------------------------------------------------------------------------

METRIC_LABELS: dict[str, str] = {
    "total_sleep_min": "Duracion (min)",
    "pct_rem": "% REM",
    "pct_deep": "% Deep",
    "pct_core": "% Core",
    "efficiency": "Eficiencia (%)",
    "n_awakenings": "Despertares",
    "temp_c": "Temperatura muneca (C)",
    "hrv_ms": "HRV (ms)",
    "resting_hr_bpm": "Resting HR (bpm)",
    "disturbances": "Pert. respiratorias",
}

SLEEP_METRICS: list[str] = [
    "total_sleep_min", "pct_rem", "pct_deep", "efficiency", "n_awakenings",
]

BIO_METRICS: list[str] = [
    "temp_c", "hrv_ms", "resting_hr_bpm", "disturbances",
]

# ---------------------------------------------------------------------------
# Shared phase-assignment function
# ---------------------------------------------------------------------------


def assign_phase(
    date: pd.Timestamp,
    periods: pd.DataFrame,
) -> tuple[str | None, int | None, int | None]:
    """
    Assign a cycle phase to a given date.

    Parameters
    ----------
    date : pd.Timestamp
        The night date to classify.
    periods : pd.DataFrame
        Must have columns ``start``, ``end`` (Timestamps) with one row per
        detected period, sorted chronologically.

    Returns
    -------
    (phase, cycle_day, cycle_length) or (None, None, None) if the date
    falls outside any detected cycle.
    """
    date = pd.Timestamp(date)
    for i in range(len(periods) - 1):
        ps = periods.iloc[i]["start"]
        pe = periods.iloc[i]["end"]
        nps = periods.iloc[i + 1]["start"]
        cl = (nps - ps).days
        if ps <= date < nps:
            d = (date - ps).days + 1
            bd = (pe - ps).days + 1
            if d <= bd:
                return "Menstrual", d, cl
            if d <= int(cl * FOLLICULAR_END_FRAC):
                return "Folicular", d, cl
            if d <= int(cl * OVULATORY_END_FRAC):
                return "Ovulatoria", d, cl
            return "Lútea", d, cl
    return None, None, None
