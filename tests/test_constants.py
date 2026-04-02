"""Tests for redmoon.constants — phase assignment logic."""

import pandas as pd
import pytest

from redmoon.constants import (
    PHASE_ORDER,
    FOLLICULAR_END_FRAC,
    OVULATORY_END_FRAC,
    MIN_CYCLE_DAYS,
    MAX_CYCLE_DAYS,
    assign_phase,
)


@pytest.fixture()
def periods_28d():
    """Two periods 28 days apart (5-day bleed)."""
    return pd.DataFrame({
        "start": pd.to_datetime(["2024-01-01", "2024-01-29"]),
        "end": pd.to_datetime(["2024-01-05", "2024-02-02"]),
    })


class TestAssignPhase:
    def test_menstrual_day1(self, periods_28d):
        phase, day, cl = assign_phase(pd.Timestamp("2024-01-01"), periods_28d)
        assert phase == "Menstrual"
        assert day == 1
        assert cl == 28

    def test_menstrual_last_bleed_day(self, periods_28d):
        phase, day, cl = assign_phase(pd.Timestamp("2024-01-05"), periods_28d)
        assert phase == "Menstrual"
        assert day == 5

    def test_follicular(self, periods_28d):
        phase, day, cl = assign_phase(pd.Timestamp("2024-01-08"), periods_28d)
        assert phase == "Folicular"

    def test_ovulatory(self, periods_28d):
        # Day 14 of 28-day cycle: int(28 * 0.46) = 12, int(28 * 0.57) = 15
        phase, day, cl = assign_phase(pd.Timestamp("2024-01-14"), periods_28d)
        assert phase == "Ovulatoria"

    def test_luteal(self, periods_28d):
        phase, day, cl = assign_phase(pd.Timestamp("2024-01-20"), periods_28d)
        assert phase == "Lútea"

    def test_outside_cycle_returns_none(self, periods_28d):
        phase, day, cl = assign_phase(pd.Timestamp("2023-12-01"), periods_28d)
        assert phase is None
        assert day is None
        assert cl is None

    def test_after_last_period_returns_none(self, periods_28d):
        phase, day, cl = assign_phase(pd.Timestamp("2024-03-01"), periods_28d)
        assert phase is None

    def test_all_phases_present_in_full_cycle(self, periods_28d):
        """Every day in the cycle should be assigned to exactly one phase."""
        phases_seen = set()
        for d in range(28):
            date = pd.Timestamp("2024-01-01") + pd.Timedelta(days=d)
            phase, _, _ = assign_phase(date, periods_28d)
            assert phase is not None, f"Day {d+1} got None"
            phases_seen.add(phase)
        assert phases_seen == set(PHASE_ORDER)


class TestConstants:
    def test_phase_order_has_four(self):
        assert len(PHASE_ORDER) == 4

    def test_fractions_are_ordered(self):
        assert 0 < FOLLICULAR_END_FRAC < OVULATORY_END_FRAC < 1

    def test_cycle_bounds(self):
        assert MIN_CYCLE_DAYS < MAX_CYCLE_DAYS
