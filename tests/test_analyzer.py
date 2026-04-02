"""Tests for redmoon.analyzer — CycleSleepAnalyzer and CycleSleepReport."""

import pandas as pd
import pytest

from redmoon.analyzer import CycleSleepAnalyzer, CycleSleepReport
from redmoon.constants import PHASE_ORDER, MIN_CYCLE_DAYS, MAX_CYCLE_DAYS


class TestCycleSleepAnalyzerValidation:
    def test_missing_sleep_raises(self):
        with pytest.raises(ValueError, match="Sleep data is required"):
            CycleSleepAnalyzer({"menstrual": pd.DataFrame({"date": ["2024-01-01"], "flow": ["Heavy"]})})

    def test_empty_sleep_raises(self):
        with pytest.raises(ValueError, match="Sleep data is required"):
            CycleSleepAnalyzer({
                "sleep": pd.DataFrame(columns=["start", "end", "duration_min", "stage"]),
                "menstrual": pd.DataFrame({"date": ["2024-01-01"], "flow": ["Heavy"]}),
            })

    def test_missing_menstrual_raises(self):
        with pytest.raises(ValueError, match="Menstrual data is required"):
            CycleSleepAnalyzer({
                "sleep": pd.DataFrame({
                    "start": pd.to_datetime(["2024-01-01 23:00"]),
                    "end": pd.to_datetime(["2024-01-02 07:00"]),
                    "duration_min": [480],
                    "stage": ["AsleepCore"],
                }),
            })


class TestCycleSleepAnalyzerPipeline:
    def test_run_with_full_data(self, sample_data):
        analyzer = CycleSleepAnalyzer(sample_data)
        report = analyzer.run()
        assert isinstance(report, CycleSleepReport)
        assert report.n_nights > 0
        assert report.n_cycles >= 2

    def test_run_with_minimal_data(self, minimal_data):
        analyzer = CycleSleepAnalyzer(minimal_data)
        report = analyzer.run()
        assert report.n_nights > 0

    def test_nightly_aggregation(self, sample_data):
        analyzer = CycleSleepAnalyzer(sample_data)
        analyzer._aggregate_nightly()
        nightly = analyzer.nightly
        assert "total_sleep_min" in nightly.columns
        assert "efficiency" in nightly.columns
        assert "n_awakenings" in nightly.columns
        assert "pct_rem" in nightly.columns
        assert (nightly["efficiency"] <= 100).all()
        assert (nightly["total_sleep_min"] > 0).all()

    def test_cycle_detection(self, sample_data):
        analyzer = CycleSleepAnalyzer(sample_data)
        analyzer._aggregate_nightly()
        analyzer._detect_cycles()
        periods = analyzer.periods
        assert len(periods) >= 3
        assert "start" in periods.columns
        assert "cycle_length" in periods.columns

    def test_phase_assignment_produces_all_phases(self, sample_data):
        analyzer = CycleSleepAnalyzer(sample_data)
        report = analyzer.run()
        phases_in_data = set(report.data["phase"].unique())
        assert phases_in_data == set(PHASE_ORDER)

    def test_cycle_length_filtering(self, sample_data):
        analyzer = CycleSleepAnalyzer(sample_data)
        report = analyzer.run()
        lengths = report.data["cycle_length"].unique()
        assert all(MIN_CYCLE_DAYS <= cl <= MAX_CYCLE_DAYS for cl in lengths)

    def test_biometrics_merged(self, sample_data):
        analyzer = CycleSleepAnalyzer(sample_data)
        report = analyzer.run()
        assert "temp_c" in report.data.columns
        assert "hrv_ms" in report.data.columns
        assert "resting_hr_bpm" in report.data.columns


class TestCycleSleepReport:
    @pytest.fixture()
    def report(self, sample_data):
        return CycleSleepAnalyzer(sample_data).run()

    def test_phase_means_shape(self, report):
        means = report.phase_means()
        assert len(means) == 4
        assert list(means.index) == PHASE_ORDER

    def test_statistical_tests_returns_list(self, report):
        results = report.statistical_tests()
        assert isinstance(results, list)
        assert len(results) > 0
        for r in results:
            assert "metric" in r
            assert "p_value" in r
            assert "significant" in r
            assert 0 <= r["p_value"] <= 1

    def test_premenstrual_effect_returns_list(self, report):
        results = report.premenstrual_effect()
        assert isinstance(results, list)
        for r in results:
            assert "early_luteal" in r
            assert "premenstrual" in r
            assert "p_value" in r

    def test_summary_is_string(self, report):
        s = report.summary()
        assert isinstance(s, str)
        assert "Noches analizadas" in s
        assert "Ciclos completos" in s
        assert "Kruskal-Wallis" in s

    def test_n_nights_positive(self, report):
        assert report.n_nights > 0

    def test_mean_cycle_length_in_range(self, report):
        mcl = report.mean_cycle_length
        assert MIN_CYCLE_DAYS <= mcl <= MAX_CYCLE_DAYS

    def test_to_json_structure(self, report):
        j = report.to_json()
        assert "n_nights" in j
        assert "n_cycles" in j
        assert "mean_cycle_length" in j
        assert "phase_distribution" in j
        assert "phase_means" in j
        assert "statistical_tests" in j
        assert "premenstrual_effect" in j
        assert len(j["phase_distribution"]) == 4

    def test_to_json_serializable(self, report):
        """Ensure the JSON output is actually serializable."""
        import json
        j = report.to_json()
        serialized = json.dumps(j)
        assert isinstance(serialized, str)
