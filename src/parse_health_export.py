"""
Parse Apple Health XML export → CSV files for sleep & menstrual analysis.

Usage:
    python src/parse_health_export.py <path_to_export.xml>

Outputs (in data/):
    - sleep.csv          Sleep stage records (InBed, Awake, Core, REM, Deep)
    - menstrual.csv      Menstrual flow records with intensity
    - wrist_temp.csv     Sleeping wrist temperature
    - breathing.csv      Sleeping breathing disturbances
"""

import sys
import os
import re
from pathlib import Path
from datetime import datetime

import pandas as pd

# Record types we care about
TYPES = {
    "HKCategoryTypeIdentifierSleepAnalysis": "sleep",
    "HKCategoryTypeIdentifierMenstrualFlow": "menstrual",
    "HKQuantityTypeIdentifierAppleSleepingWristTemperature": "wrist_temp",
    "HKQuantityTypeIdentifierAppleSleepingBreathingDisturbances": "breathing",
}

# Regex to parse Record elements (faster than full XML parsing for 1.7GB)
RECORD_RE = re.compile(
    r'<Record\s+'
    r'type="(?P<type>[^"]+)"\s+'
    r'.*?'
    r'startDate="(?P<start>[^"]+)"\s+'
    r'endDate="(?P<end>[^"]+)"\s+'
    r'value="(?P<value>[^"]+)"'
)

# Also match records with unit + value (quantitative types)
RECORD_QUANT_RE = re.compile(
    r'<Record\s+'
    r'type="(?P<type>[^"]+)"\s+'
    r'.*?'
    r'unit="(?P<unit>[^"]+)"\s+'
    r'.*?'
    r'startDate="(?P<start>[^"]+)"\s+'
    r'endDate="(?P<end>[^"]+)"\s+'
    r'value="(?P<value>[^"]+)"'
)


def parse_datetime(s: str) -> datetime:
    """Parse Apple Health datetime string."""
    return pd.to_datetime(s)


def parse_export(xml_path: str) -> dict[str, list[dict]]:
    """Stream-parse the XML line by line, extracting relevant records."""
    records = {name: [] for name in TYPES.values()}
    type_keys = set(TYPES.keys())

    with open(xml_path, "r", encoding="utf-8") as f:
        for line in f:
            if "<Record" not in line:
                continue

            # Try quantitative match first (has unit field)
            m = RECORD_QUANT_RE.search(line)
            if m and m.group("type") in type_keys:
                name = TYPES[m.group("type")]
                records[name].append({
                    "start": m.group("start"),
                    "end": m.group("end"),
                    "value": m.group("value"),
                    "unit": m.group("unit"),
                })
                continue

            # Then categorical match
            m = RECORD_RE.search(line)
            if m and m.group("type") in type_keys:
                name = TYPES[m.group("type")]
                records[name].append({
                    "start": m.group("start"),
                    "end": m.group("end"),
                    "value": m.group("value"),
                })

    return records


def to_dataframes(records: dict[str, list[dict]]) -> dict[str, pd.DataFrame]:
    """Convert raw records to cleaned DataFrames."""
    dfs = {}

    # --- Sleep ---
    if records["sleep"]:
        df = pd.DataFrame(records["sleep"])
        df["start"] = pd.to_datetime(df["start"])
        df["end"] = pd.to_datetime(df["end"])
        df["duration_min"] = (df["end"] - df["start"]).dt.total_seconds() / 60
        # Clean up value names
        df["stage"] = (
            df["value"]
            .str.replace("HKCategoryValueSleepAnalysis", "")
        )
        df = df.drop(columns=["value"])
        df = df.sort_values("start").reset_index(drop=True)
        dfs["sleep"] = df

    # --- Menstrual ---
    if records["menstrual"]:
        df = pd.DataFrame(records["menstrual"])
        df["date"] = pd.to_datetime(df["start"]).dt.date
        df["flow"] = (
            df["value"]
            .str.replace("HKCategoryValueVaginalBleeding", "")
        )
        df = df[["date", "flow"]].sort_values("date").reset_index(drop=True)
        dfs["menstrual"] = df

    # --- Wrist Temperature ---
    if records["wrist_temp"]:
        df = pd.DataFrame(records["wrist_temp"])
        df["date"] = pd.to_datetime(df["start"]).dt.date
        df["temp_c"] = pd.to_numeric(df["value"])
        df = df[["date", "temp_c"]].sort_values("date").reset_index(drop=True)
        dfs["wrist_temp"] = df

    # --- Breathing Disturbances ---
    if records["breathing"]:
        df = pd.DataFrame(records["breathing"])
        df["date"] = pd.to_datetime(df["start"]).dt.date
        df["disturbances"] = pd.to_numeric(df["value"])
        df = df[["date", "disturbances"]].sort_values("date").reset_index(drop=True)
        dfs["breathing"] = df

    return dfs


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    xml_path = sys.argv[1]
    if not os.path.exists(xml_path):
        print(f"File not found: {xml_path}")
        sys.exit(1)

    data_dir = Path(__file__).resolve().parent.parent / "data"
    data_dir.mkdir(exist_ok=True)

    print(f"Parsing {xml_path}...")
    records = parse_export(xml_path)

    for name, recs in records.items():
        print(f"  {name}: {len(recs)} records")

    print("Converting to DataFrames...")
    dfs = to_dataframes(records)

    for name, df in dfs.items():
        out_path = data_dir / f"{name}.csv"
        df.to_csv(out_path, index=False)
        print(f"  Saved {out_path} ({len(df)} rows)")

    print("Done!")


if __name__ == "__main__":
    main()
