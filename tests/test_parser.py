"""Tests for redmoon.parser — XML parsing and validation."""

import tempfile
from pathlib import Path

import pandas as pd
import pytest

from redmoon.parser import parse_export


SAMPLE_XML = """\
<?xml version="1.0" encoding="UTF-8"?>
<HealthData>
 <Record type="HKCategoryTypeIdentifierSleepAnalysis" sourceName="Watch" startDate="2024-01-15 23:30:00 +0100" endDate="2024-01-16 07:00:00 +0100" value="HKCategoryValueSleepAnalysisAsleepCore"/>
 <Record type="HKCategoryTypeIdentifierSleepAnalysis" sourceName="Watch" startDate="2024-01-15 23:30:00 +0100" endDate="2024-01-16 07:00:00 +0100" value="HKCategoryValueSleepAnalysisInBed"/>
 <Record type="HKCategoryTypeIdentifierMenstrualFlow" sourceName="Health" startDate="2024-01-15 00:00:00 +0100" endDate="2024-01-16 00:00:00 +0100" value="HKCategoryValueVaginalBleedingHeavy"/>
 <Record type="HKQuantityTypeIdentifierAppleSleepingWristTemperature" sourceName="Watch" unit="degC" startDate="2024-01-16 02:00:00 +0100" endDate="2024-01-16 06:00:00 +0100" value="36.28"/>
 <Record type="HKQuantityTypeIdentifierHeartRateVariabilitySDNN" sourceName="Watch" unit="ms" startDate="2024-01-15 22:00:00 +0100" endDate="2024-01-15 22:00:00 +0100" value="32.5"/>
 <Record type="HKQuantityTypeIdentifierRestingHeartRate" sourceName="Watch" unit="count/min" startDate="2024-01-15 00:00:00 +0100" endDate="2024-01-15 00:00:00 +0100" value="68"/>
 <Record type="HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances" sourceName="Watch" unit="count/hr" startDate="2024-01-16 02:00:00 +0100" endDate="2024-01-16 06:00:00 +0100" value="0.42"/>
 <Record type="HKQuantityTypeIdentifierStepCount" sourceName="iPhone" unit="count" startDate="2024-01-15 10:00:00 +0100" endDate="2024-01-15 10:05:00 +0100" value="120"/>
</HealthData>
"""


@pytest.fixture()
def xml_file(tmp_path):
    """Write sample XML to a temp file."""
    path = tmp_path / "export.xml"
    path.write_text(SAMPLE_XML, encoding="utf-8")
    return path


class TestParseExport:
    def test_parses_all_types(self, xml_file):
        data = parse_export(xml_file)
        assert "sleep" in data
        assert "menstrual" in data
        assert "wrist_temp" in data
        assert "hrv" in data
        assert "resting_hr" in data
        assert "breathing" in data

    def test_sleep_has_correct_columns(self, xml_file):
        data = parse_export(xml_file)
        sleep = data["sleep"]
        assert "start" in sleep.columns
        assert "end" in sleep.columns
        assert "duration_min" in sleep.columns
        assert "stage" in sleep.columns

    def test_sleep_stage_cleaned(self, xml_file):
        data = parse_export(xml_file)
        stages = data["sleep"]["stage"].tolist()
        assert "AsleepCore" in stages
        assert "InBed" in stages

    def test_menstrual_has_date_and_flow(self, xml_file):
        data = parse_export(xml_file)
        ms = data["menstrual"]
        assert "date" in ms.columns
        assert "flow" in ms.columns
        assert ms.iloc[0]["flow"] == "Heavy"

    def test_wrist_temp_numeric(self, xml_file):
        data = parse_export(xml_file)
        assert data["wrist_temp"]["temp_c"].dtype == float
        assert abs(data["wrist_temp"].iloc[0]["temp_c"] - 36.28) < 0.01

    def test_ignores_unrelated_types(self, xml_file):
        data = parse_export(xml_file)
        # StepCount should not appear in any output
        for key, df in data.items():
            assert "step" not in key.lower()

    def test_progress_callback(self, xml_file):
        calls = []
        parse_export(xml_file, progress_callback=lambda n: calls.append(n))
        # With only 7 records, callback won't fire (fires every 10k)
        assert calls == []

    def test_file_not_found_raises(self):
        with pytest.raises(FileNotFoundError):
            parse_export("/nonexistent/path.xml")

    def test_directory_raises(self, tmp_path):
        with pytest.raises(ValueError, match="not a file"):
            parse_export(tmp_path)

    def test_empty_xml(self, tmp_path):
        path = tmp_path / "empty.xml"
        path.write_text("<?xml version='1.0'?><HealthData></HealthData>")
        data = parse_export(path)
        assert data == {}
