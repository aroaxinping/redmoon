"""
Core analysis engine for cycle-sleep relationships.

Takes parsed DataFrames and produces nightly aggregation, cycle phase assignment,
statistical tests, and a structured report.
"""

from datetime import timedelta

import numpy as np
import pandas as pd
from scipy import stats


class CycleSleepAnalyzer:
    """
    Analyze the relationship between menstrual cycle phases and sleep quality.

    Usage
    -----
    >>> from cyclesleep import parse_export, CycleSleepAnalyzer
    >>> data = parse_export("exportación.xml")
    >>> analyzer = CycleSleepAnalyzer(data)
    >>> report = analyzer.run()
    >>> print(report.summary())
    """

    PHASE_ORDER = ["Menstrual", "Folicular", "Ovulatoria", "Lútea"]

    def __init__(self, data: dict[str, pd.DataFrame]):
        self.raw = data
        self.nightly = None
        self.periods = None
        self.cycle_sleep = None

    def run(self) -> "CycleSleepReport":
        """Execute the full analysis pipeline."""
        self._aggregate_nightly()
        self._detect_cycles()
        self._assign_phases()
        self._merge_biometrics()
        return CycleSleepReport(self.cycle_sleep, self.periods, self.PHASE_ORDER)

    def _aggregate_nightly(self):
        sleep = self.raw["sleep"].copy()
        sleep["hour"] = sleep["start"].dt.hour
        sleep["night_date"] = sleep["start"].dt.date
        mask_early = sleep["hour"] < 6
        sleep.loc[mask_early, "night_date"] = (
            sleep.loc[mask_early, "start"] - timedelta(days=1)
        ).dt.date
        sleep["night_date"] = pd.to_datetime(sleep["night_date"])

        rows = []
        for night, group in sleep.groupby("night_date"):
            row = {"night_date": night}
            for stage in ["AsleepCore", "AsleepREM", "AsleepDeep", "Awake", "InBed"]:
                row[f"{stage}_min"] = group[group["stage"] == stage]["duration_min"].sum()

            unspec = group[group["stage"] == "AsleepUnspecified"]["duration_min"].sum()
            row["total_sleep_min"] = (
                row["AsleepCore_min"] + row["AsleepREM_min"] + row["AsleepDeep_min"] + unspec
            )
            total_all = row["total_sleep_min"] + row["Awake_min"]
            row["total_inbed_min"] = (
                row["InBed_min"] if row["InBed_min"] >= total_all else total_all
            )

            if row["total_sleep_min"] > 0:
                row["pct_rem"] = row["AsleepREM_min"] / row["total_sleep_min"] * 100
                row["pct_deep"] = row["AsleepDeep_min"] / row["total_sleep_min"] * 100
                row["pct_core"] = row["AsleepCore_min"] / row["total_sleep_min"] * 100
            else:
                row["pct_rem"] = row["pct_deep"] = row["pct_core"] = np.nan

            if row["total_inbed_min"] > 0:
                row["efficiency"] = min(
                    row["total_sleep_min"] / row["total_inbed_min"] * 100, 100.0
                )
            else:
                row["efficiency"] = np.nan

            row["n_awakenings"] = len(group[group["stage"] == "Awake"])
            row["sleep_start"] = group["start"].min()
            row["sleep_end"] = group["end"].max()
            rows.append(row)

        df = pd.DataFrame(rows)
        self.nightly = df[
            (df["total_sleep_min"] > 120) & (df["total_inbed_min"] < 960)
        ].reset_index(drop=True)

    def _detect_cycles(self):
        ms = self.raw["menstrual"].copy()
        ms["date_dt"] = pd.to_datetime(ms["date"])
        ms = ms.sort_values("date_dt").reset_index(drop=True)
        ms["gap"] = ms["date_dt"].diff().dt.days
        ms["new_period"] = (ms["gap"] > 5) | (ms["gap"].isna())
        ms["period_id"] = ms["new_period"].cumsum()

        self.periods = (
            ms.groupby("period_id")
            .agg(start=("date_dt", "min"), end=("date_dt", "max"), n_days=("date_dt", "count"))
            .reset_index()
        )
        self.periods["cycle_length"] = self.periods["start"].diff().dt.days

    def _assign_phases(self):
        periods = self.periods

        def assign(date):
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
                    if d <= int(cl * 0.46):
                        return "Folicular", d, cl
                    if d <= int(cl * 0.57):
                        return "Ovulatoria", d, cl
                    return "Lútea", d, cl
            return None, None, None

        phases = self.nightly["night_date"].apply(assign)
        self.nightly["phase"] = phases.apply(lambda x: x[0])
        self.nightly["cycle_day"] = phases.apply(lambda x: x[1])
        self.nightly["cycle_length"] = phases.apply(lambda x: x[2])

        cs = self.nightly.dropna(subset=["phase"]).copy()
        self.cycle_sleep = cs[
            (cs["cycle_length"] >= 21) & (cs["cycle_length"] <= 45)
        ].reset_index(drop=True)

    def _merge_biometrics(self):
        cs = self.cycle_sleep

        for name, col, agg_col in [
            ("wrist_temp", "temp_c", None),
            ("breathing", "disturbances", None),
            ("resting_hr", "resting_hr_bpm", None),
        ]:
            if name in self.raw:
                df = self.raw[name].copy()
                df["night_date"] = pd.to_datetime(df["date"])
                cs = cs.merge(df[["night_date", col]], on="night_date", how="left")

        if "hrv" in self.raw:
            hrv = self.raw["hrv"].copy()
            hrv["date"] = pd.to_datetime(hrv["datetime"]).dt.date
            hrv_daily = hrv.groupby("date")["hrv_ms"].mean().reset_index()
            hrv_daily["night_date"] = pd.to_datetime(hrv_daily["date"])
            cs = cs.merge(hrv_daily[["night_date", "hrv_ms"]], on="night_date", how="left")

        self.cycle_sleep = cs


class CycleSleepReport:
    """Structured report with statistical results and summaries."""

    SLEEP_METRICS = ["total_sleep_min", "pct_rem", "pct_deep", "efficiency", "n_awakenings"]
    BIO_METRICS = ["temp_c", "hrv_ms", "resting_hr_bpm", "disturbances"]
    LABELS = {
        "total_sleep_min": "Duracion (min)",
        "pct_rem": "% REM",
        "pct_deep": "% Deep",
        "efficiency": "Eficiencia (%)",
        "n_awakenings": "Despertares",
        "temp_c": "Temperatura muneca (C)",
        "hrv_ms": "HRV (ms)",
        "resting_hr_bpm": "Resting HR (bpm)",
        "disturbances": "Pert. respiratorias",
    }

    def __init__(self, cycle_sleep, periods, phase_order):
        self.data = cycle_sleep
        self.periods = periods
        self.phase_order = phase_order
        self._stats_cache = {}

    @property
    def n_nights(self):
        return len(self.data)

    @property
    def n_cycles(self):
        return len(self.periods) - 1

    @property
    def mean_cycle_length(self):
        valid = self.periods["cycle_length"].dropna()
        valid = valid[(valid >= 21) & (valid <= 45)]
        return valid.mean()

    def phase_means(self) -> pd.DataFrame:
        """Mean of all metrics by cycle phase."""
        all_metrics = self.SLEEP_METRICS + self.BIO_METRICS
        available = [m for m in all_metrics if m in self.data.columns]
        df = self.data.groupby("phase")[available].mean().round(2)
        df = df.reindex(self.phase_order)
        df.columns = [self.LABELS.get(c, c) for c in df.columns]
        return df

    def statistical_tests(self) -> list[dict]:
        """Kruskal-Wallis test for each metric across phases."""
        results = []
        all_metrics = self.SLEEP_METRICS + self.BIO_METRICS
        for metric in all_metrics:
            if metric not in self.data.columns:
                continue
            groups = [
                self.data[self.data["phase"] == p][metric].dropna()
                for p in self.phase_order
            ]
            valid = [g for g in groups if len(g) > 5]
            if len(valid) < 2:
                continue
            h, p = stats.kruskal(*valid)
            results.append({
                "metric": self.LABELS.get(metric, metric),
                "H": round(h, 3),
                "p_value": p,
                "significant": p < 0.05,
            })
        return results

    def premenstrual_effect(self) -> list[dict]:
        """Compare late luteal (last 5 days) vs early luteal sleep."""
        luteal = self.data[self.data["phase"] == "Lútea"].copy()
        luteal["days_to_period"] = luteal["cycle_length"] - luteal["cycle_day"]

        results = []
        for metric in self.SLEEP_METRICS:
            early = luteal[luteal["days_to_period"] > 5][metric].dropna()
            late = luteal[luteal["days_to_period"] <= 5][metric].dropna()
            if len(early) > 5 and len(late) > 5:
                u, p = stats.mannwhitneyu(early, late, alternative="two-sided")
                results.append({
                    "metric": self.LABELS.get(metric, metric),
                    "early_luteal": round(early.mean(), 2),
                    "premenstrual": round(late.mean(), 2),
                    "p_value": p,
                    "significant": p < 0.05,
                })
        return results

    def summary(self) -> str:
        """Generate a text summary of key findings."""
        lines = [
            f"Cycle & Sleep Analysis Report",
            f"{'=' * 50}",
            f"Noches analizadas: {self.n_nights}",
            f"Ciclos completos: {self.n_cycles}",
            f"Duracion media del ciclo: {self.mean_cycle_length:.1f} dias",
            "",
            "Distribucion por fase:",
        ]
        for p in self.phase_order:
            n = len(self.data[self.data["phase"] == p])
            lines.append(f"  {p}: {n} noches ({n/self.n_nights*100:.1f}%)")

        lines.append("")
        lines.append("Tests estadisticos (Kruskal-Wallis):")
        lines.append("-" * 50)
        for t in self.statistical_tests():
            sig = "***" if t["p_value"] < 0.001 else "**" if t["p_value"] < 0.01 else "*" if t["p_value"] < 0.05 else "ns"
            lines.append(f"  {t['metric']:30s}: p={t['p_value']:.6f} [{sig}]")

        pms = self.premenstrual_effect()
        if pms:
            lines.append("")
            lines.append("Efecto premenstrual (ultimos 5 dias vs resto lutea):")
            lines.append("-" * 50)
            for r in pms:
                sig = "*" if r["significant"] else "ns"
                lines.append(
                    f"  {r['metric']:30s}: early={r['early_luteal']:.1f} vs pre={r['premenstrual']:.1f} (p={r['p_value']:.4f}) [{sig}]"
                )

        return "\n".join(lines)
