"""
Parse Apple Health XML export into structured DataFrames.

Handles the ~1.7GB XML file via line-by-line regex matching (no full DOM parsing).
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Callable, Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

TYPES = {
    "HKCategoryTypeIdentifierSleepAnalysis": "sleep",
    "HKCategoryTypeIdentifierMenstrualFlow": "menstrual",
    "HKQuantityTypeIdentifierAppleSleepingWristTemperature": "wrist_temp",
    "HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances": "breathing",
    "HKQuantityTypeIdentifierHeartRateVariabilitySDNN": "hrv",
    "HKQuantityTypeIdentifierRestingHeartRate": "resting_hr",
}

RECORD_RE = re.compile(
    r'<Record\s+type="(?P<type>[^"]+)"\s+.*?'
    r'startDate="(?P<start>[^"]+)"\s+endDate="(?P<end>[^"]+)"\s+'
    r'value="(?P<value>[^"]+)"'
)

RECORD_QUANT_RE = re.compile(
    r'<Record\s+type="(?P<type>[^"]+)"\s+.*?'
    r'unit="(?P<unit>[^"]+)"\s+.*?'
    r'startDate="(?P<start>[^"]+)"\s+endDate="(?P<end>[^"]+)"\s+'
    r'value="(?P<value>[^"]+)"'
)


def parse_export(
    xml_path: str | Path,
    progress_callback: Optional[Callable[[int], None]] = None,
) -> dict[str, pd.DataFrame]:
    """
    Parse an Apple Health XML export file.

    Parameters
    ----------
    xml_path : str
        Path to the exportación.xml file.
    progress_callback : callable, optional
        Function called with (records_found: int) periodically.

    Returns
    -------
    dict[str, pd.DataFrame]
        Dictionary with keys: sleep, menstrual, wrist_temp, breathing, hrv, resting_hr
    """
    xml_path = Path(xml_path)
    if not xml_path.exists():
        raise FileNotFoundError(f"XML file not found: {xml_path}")
    if not xml_path.is_file():
        raise ValueError(f"Path is not a file: {xml_path}")

    records: dict[str, list[dict]] = {name: [] for name in TYPES.values()}
    type_keys = set(TYPES.keys())
    count = 0

    logger.info("Parsing %s", xml_path)
    with open(xml_path, "r", encoding="utf-8") as f:
        for line in f:
            if "<Record" not in line:
                continue

            m = RECORD_QUANT_RE.search(line)
            if m and m.group("type") in type_keys:
                name = TYPES[m.group("type")]
                records[name].append({
                    "start": m.group("start"),
                    "end": m.group("end"),
                    "value": m.group("value"),
                })
                count += 1
                if progress_callback and count % 10000 == 0:
                    progress_callback(count)
                continue

            m = RECORD_RE.search(line)
            if m and m.group("type") in type_keys:
                name = TYPES[m.group("type")]
                records[name].append({
                    "start": m.group("start"),
                    "end": m.group("end"),
                    "value": m.group("value"),
                })
                count += 1
                if progress_callback and count % 10000 == 0:
                    progress_callback(count)

    logger.info("Parsed %d records total", count)
    return _to_dataframes(records)


def _to_dataframes(records: dict) -> dict[str, pd.DataFrame]:
    """Convert raw record dicts to cleaned DataFrames."""
    dfs = {}

    if records["sleep"]:
        df = pd.DataFrame(records["sleep"])
        df["start"] = pd.to_datetime(df["start"])
        df["end"] = pd.to_datetime(df["end"])
        df["duration_min"] = (df["end"] - df["start"]).dt.total_seconds() / 60
        df["stage"] = df["value"].str.replace("HKCategoryValueSleepAnalysis", "")
        df = df.drop(columns=["value"]).sort_values("start").reset_index(drop=True)
        dfs["sleep"] = df

    if records["menstrual"]:
        df = pd.DataFrame(records["menstrual"])
        df["date"] = pd.to_datetime(df["start"]).dt.date
        df["flow"] = df["value"].str.replace("HKCategoryValueVaginalBleeding", "")
        dfs["menstrual"] = df[["date", "flow"]].sort_values("date").reset_index(drop=True)

    if records["wrist_temp"]:
        df = pd.DataFrame(records["wrist_temp"])
        df["date"] = pd.to_datetime(df["start"]).dt.date
        df["temp_c"] = pd.to_numeric(df["value"])
        dfs["wrist_temp"] = df[["date", "temp_c"]].sort_values("date").reset_index(drop=True)

    if records["breathing"]:
        df = pd.DataFrame(records["breathing"])
        df["date"] = pd.to_datetime(df["start"]).dt.date
        df["disturbances"] = pd.to_numeric(df["value"])
        dfs["breathing"] = df[["date", "disturbances"]].sort_values("date").reset_index(drop=True)

    if records["hrv"]:
        df = pd.DataFrame(records["hrv"])
        df["datetime"] = pd.to_datetime(df["start"])
        df["date"] = df["datetime"].dt.date
        df["hrv_ms"] = pd.to_numeric(df["value"])
        dfs["hrv"] = df[["date", "datetime", "hrv_ms"]].sort_values("datetime").reset_index(drop=True)

    if records["resting_hr"]:
        df = pd.DataFrame(records["resting_hr"])
        df["date"] = pd.to_datetime(df["start"]).dt.date
        df["resting_hr_bpm"] = pd.to_numeric(df["value"])
        dfs["resting_hr"] = df[["date", "resting_hr_bpm"]].sort_values("date").reset_index(drop=True)

    return dfs
