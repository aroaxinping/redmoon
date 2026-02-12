"""
Streamlit dashboard for Cycle & Sleep analysis.

Run: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from datetime import timedelta
from pathlib import Path

from redmoon.constants import (
    PHASE_ORDER, PHASE_COLORS, METRIC_LABELS,
    MIN_SLEEP_MIN, MAX_INBED_MIN, EARLY_MORNING_CUTOFF,
    MIN_CYCLE_DAYS, MAX_CYCLE_DAYS, NEW_PERIOD_GAP_DAYS,
    assign_phase,
)

st.set_page_config(page_title="Cycle & Sleep", layout="wide", page_icon="🌙")

DATA_DIR = Path(__file__).parent / "data"


@st.cache_data
def load_and_process():
    """Load CSVs and compute nightly aggregation + cycle phases."""
    sleep_raw = pd.read_csv(DATA_DIR / "sleep.csv", parse_dates=["start", "end"])
    menstrual = pd.read_csv(DATA_DIR / "menstrual.csv", parse_dates=["date"])
    wrist_temp = pd.read_csv(DATA_DIR / "wrist_temp.csv", parse_dates=["date"])
    breathing = pd.read_csv(DATA_DIR / "breathing.csv", parse_dates=["date"])
    hrv = pd.read_csv(DATA_DIR / "hrv.csv", parse_dates=["datetime"])
    resting_hr = pd.read_csv(DATA_DIR / "resting_hr.csv", parse_dates=["date"])

    # Nightly aggregation
    sleep = sleep_raw.copy()
    sleep["hour"] = sleep["start"].dt.hour
    sleep["night_date"] = sleep["start"].dt.date
    mask_early = sleep["hour"] < EARLY_MORNING_CUTOFF
    sleep.loc[mask_early, "night_date"] = (sleep.loc[mask_early, "start"] - timedelta(days=1)).dt.date
    sleep["night_date"] = pd.to_datetime(sleep["night_date"])

    nightly = []
    for night, group in sleep.groupby("night_date"):
        row = {"night_date": night}
        for stage in ["AsleepCore", "AsleepREM", "AsleepDeep", "Awake", "InBed"]:
            row[f"{stage}_min"] = group[group["stage"] == stage]["duration_min"].sum()
        unspecified = group[group["stage"] == "AsleepUnspecified"]["duration_min"].sum()
        row["total_sleep_min"] = row["AsleepCore_min"] + row["AsleepREM_min"] + row["AsleepDeep_min"] + unspecified
        total_all = row["total_sleep_min"] + row["Awake_min"]
        row["total_inbed_min"] = row["InBed_min"] if row["InBed_min"] >= total_all else total_all
        if row["total_sleep_min"] > 0:
            row["pct_rem"] = row["AsleepREM_min"] / row["total_sleep_min"] * 100
            row["pct_deep"] = row["AsleepDeep_min"] / row["total_sleep_min"] * 100
        else:
            row["pct_rem"] = row["pct_deep"] = np.nan
        if row["total_inbed_min"] > 0:
            row["efficiency"] = min(row["total_sleep_min"] / row["total_inbed_min"] * 100, 100.0)
        else:
            row["efficiency"] = np.nan
        row["n_awakenings"] = len(group[group["stage"] == "Awake"])
        nightly.append(row)

    nightly_df = pd.DataFrame(nightly)
    nightly_df = nightly_df[(nightly_df["total_sleep_min"] > MIN_SLEEP_MIN) & (nightly_df["total_inbed_min"] < MAX_INBED_MIN)]

    # Cycle detection
    ms = menstrual.sort_values("date").reset_index(drop=True)
    ms["date_dt"] = pd.to_datetime(ms["date"])
    ms["gap"] = ms["date_dt"].diff().dt.days
    ms["new_period"] = (ms["gap"] > NEW_PERIOD_GAP_DAYS) | (ms["gap"].isna())
    ms["period_id"] = ms["new_period"].cumsum()
    periods = ms.groupby("period_id").agg(start=("date_dt", "min"), end=("date_dt", "max"), n_days=("date_dt", "count")).reset_index()
    periods["cycle_length"] = periods["start"].diff().dt.days

    # Assign phases (uses shared function from redmoon.constants)
    phases = nightly_df["night_date"].apply(lambda d: assign_phase(d, periods))
    nightly_df["phase"] = phases.apply(lambda x: x[0])
    nightly_df["cycle_day"] = phases.apply(lambda x: x[1])
    nightly_df["cycle_length"] = phases.apply(lambda x: x[2])

    cs = nightly_df.dropna(subset=["phase"]).copy()
    cs = cs[(cs["cycle_length"] >= MIN_CYCLE_DAYS) & (cs["cycle_length"] <= MAX_CYCLE_DAYS)]

    # Merge biometrics
    wrist_temp["night_date"] = pd.to_datetime(wrist_temp["date"])
    cs = cs.merge(wrist_temp[["night_date", "temp_c"]], on="night_date", how="left")
    breathing["night_date"] = pd.to_datetime(breathing["date"])
    cs = cs.merge(breathing[["night_date", "disturbances"]], on="night_date", how="left")
    hrv["date"] = pd.to_datetime(hrv["datetime"]).dt.date
    hrv_daily = hrv.groupby("date")["hrv_ms"].mean().reset_index()
    hrv_daily["night_date"] = pd.to_datetime(hrv_daily["date"])
    cs = cs.merge(hrv_daily[["night_date", "hrv_ms"]], on="night_date", how="left")
    resting_hr["night_date"] = pd.to_datetime(resting_hr["date"])
    cs = cs.merge(resting_hr[["night_date", "resting_hr_bpm"]], on="night_date", how="left")

    return cs, periods


def kw_test(data, metric):
    groups = [data[data["phase"] == p][metric].dropna() for p in PHASE_ORDER]
    valid = [g for g in groups if len(g) > 5]
    if len(valid) < 2:
        return None, None
    return stats.kruskal(*valid)


# --- Load data ---
cs, periods = load_and_process()

# --- Sidebar ---
st.sidebar.title("Cycle & Sleep")
st.sidebar.markdown("Analisis de patrones hormonales en la calidad del sueno")
st.sidebar.markdown("---")
st.sidebar.metric("Noches analizadas", len(cs))
st.sidebar.metric("Ciclos completos", len(periods) - 1)
valid_cycles = periods.dropna(subset=["cycle_length"])
st.sidebar.metric("Ciclo medio", f"{valid_cycles['cycle_length'].mean():.0f} dias")
st.sidebar.markdown("---")

view = st.sidebar.radio("Vista", [
    "Resumen", "Sueno por fase", "Biomarcadores", "Efecto premenstrual", "Tendencia temporal"
])

# --- Main content ---
if view == "Resumen":
    st.title("Cycle & Sleep: Patrones Hormonales en la Calidad del Sueno")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Sueno medio", f"{cs['total_sleep_min'].mean()/60:.1f}h")
    col2.metric("Eficiencia media", f"{cs['efficiency'].mean():.0f}%")
    col3.metric("HRV medio", f"{cs['hrv_ms'].mean():.0f} ms")
    col4.metric("Resting HR medio", f"{cs['resting_hr_bpm'].mean():.0f} bpm")

    st.markdown("### Significancia estadistica por metrica")
    metrics_all = ["total_sleep_min", "pct_rem", "pct_deep", "efficiency", "n_awakenings",
                   "temp_c", "hrv_ms", "resting_hr_bpm", "disturbances"]
    labels = {"total_sleep_min": "Duracion", "pct_rem": "% REM", "pct_deep": "% Deep",
              "efficiency": "Eficiencia", "n_awakenings": "Despertares",
              "temp_c": "Temperatura", "hrv_ms": "HRV", "resting_hr_bpm": "Resting HR",
              "disturbances": "Pert. respiratorias"}

    rows = []
    for m in metrics_all:
        stat, p = kw_test(cs, m)
        if stat is not None:
            sig = "Significativo" if p < 0.05 else "No significativo"
            rows.append({"Metrica": labels.get(m, m), "H": f"{stat:.1f}", "p-valor": f"{p:.6f}", "Resultado": sig})
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    st.markdown("""
    ### Hallazgos principales
    - **Temperatura, HRV y Resting HR** muestran diferencias altamente significativas entre fases
    - **Las metricas de sueno** (duracion, REM, Deep) no cambian significativamente entre fases a nivel global
    - **Efecto premenstrual**: mas despertares en los ultimos 5 dias antes del periodo
    """)

elif view == "Sueno por fase":
    st.title("Metricas de sueno por fase del ciclo")

    metric = st.selectbox("Metrica", ["total_sleep_min", "pct_rem", "pct_deep", "efficiency", "n_awakenings"],
                          format_func=lambda x: {"total_sleep_min": "Duracion (min)", "pct_rem": "% REM",
                                                  "pct_deep": "% Deep", "efficiency": "Eficiencia (%)",
                                                  "n_awakenings": "Despertares"}[x])

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(8, 5))
        data = [cs[cs["phase"] == p][metric].dropna() for p in PHASE_ORDER]
        bp = ax.boxplot(data, tick_labels=PHASE_ORDER, patch_artist=True, widths=0.6)
        for patch, phase in zip(bp["boxes"], PHASE_ORDER):
            patch.set_facecolor(PHASE_COLORS[phase])
            patch.set_alpha(0.6)
        stat, p = kw_test(cs, metric)
        ax.set_title(f"p = {p:.4f}" if p else "")
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(8, 5))
        cs_norm = cs.copy()
        cs_norm["cycle_pos"] = cs_norm["cycle_day"] / cs_norm["cycle_length"]
        temp = cs_norm[["cycle_pos", metric]].dropna()
        temp["bin"] = pd.cut(temp["cycle_pos"], bins=20)
        binned = temp.groupby("bin", observed=True)[metric].agg(["mean", "sem"])
        bc = [iv.mid for iv in binned.index]
        ax.fill_between(bc, binned["mean"] - 1.96*binned["sem"], binned["mean"] + 1.96*binned["sem"],
                        alpha=0.2, color="steelblue")
        ax.plot(bc, binned["mean"], "o-", color="steelblue", linewidth=2, markersize=4)
        ax.axvspan(0, 0.18, alpha=0.08, color="red")
        ax.axvspan(0.57, 1.0, alpha=0.08, color="orange")
        ax.set_xlabel("Posicion en el ciclo")
        ax.set_title("Evolucion a lo largo del ciclo")
        st.pyplot(fig)

    # Summary table
    summary = cs.groupby("phase")[metric].agg(["mean", "std", "median", "count"]).round(2)
    summary = summary.reindex(PHASE_ORDER)
    st.dataframe(summary, use_container_width=True)

elif view == "Biomarcadores":
    st.title("Biomarcadores fisiologicos por fase")

    bio = st.selectbox("Biomarcador", ["temp_c", "hrv_ms", "resting_hr_bpm"],
                       format_func=lambda x: {"temp_c": "Temperatura muneca (C)", "hrv_ms": "HRV (ms)",
                                               "resting_hr_bpm": "Resting HR (bpm)"}[x])

    bio_data = cs.dropna(subset=[bio])
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(8, 5))
        data = [bio_data[bio_data["phase"] == p][bio].dropna() for p in PHASE_ORDER]
        bp = ax.boxplot(data, tick_labels=PHASE_ORDER, patch_artist=True, widths=0.6)
        for patch, phase in zip(bp["boxes"], PHASE_ORDER):
            patch.set_facecolor(PHASE_COLORS[phase])
            patch.set_alpha(0.6)
        stat, p = kw_test(bio_data, bio)
        ax.set_title(f"p = {p:.6f}" if p else "")
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots(figsize=(8, 5))
        bn = bio_data.copy()
        bn["cycle_pos"] = bn["cycle_day"] / bn["cycle_length"]
        bn["bin"] = pd.cut(bn["cycle_pos"], bins=20)
        binned = bn.groupby("bin", observed=True)[bio].agg(["mean", "sem"])
        bc = [iv.mid for iv in binned.index]
        ax.fill_between(bc, binned["mean"] - 1.96*binned["sem"], binned["mean"] + 1.96*binned["sem"],
                        alpha=0.2, color="indianred")
        ax.plot(bc, binned["mean"], "o-", color="indianred", linewidth=2, markersize=4)
        ax.axvspan(0, 0.18, alpha=0.08, color="red")
        ax.axvspan(0.57, 1.0, alpha=0.08, color="orange")
        ax.set_xlabel("Posicion en el ciclo")
        ax.set_title("Evolucion a lo largo del ciclo")
        st.pyplot(fig)

    summary = bio_data.groupby("phase")[bio].agg(["mean", "std", "count"]).round(3)
    summary = summary.reindex(PHASE_ORDER)
    st.dataframe(summary, use_container_width=True)

elif view == "Efecto premenstrual":
    st.title("Efecto premenstrual: ultimos 5 dias antes del periodo")

    luteal = cs[cs["phase"] == "Lútea"].copy()
    luteal["days_to_period"] = luteal["cycle_length"] - luteal["cycle_day"]
    luteal["sub"] = np.where(luteal["days_to_period"] <= 5, "Premenstrual", "Lutea temprana")

    for metric, label in [("total_sleep_min", "Duracion (min)"), ("n_awakenings", "Despertares"),
                          ("pct_rem", "% REM"), ("efficiency", "Eficiencia (%)")]:
        early = luteal[luteal["sub"] == "Lutea temprana"][metric].dropna()
        late = luteal[luteal["sub"] == "Premenstrual"][metric].dropna()
        u, p = stats.mannwhitneyu(early, late, alternative="two-sided")
        sig = " *" if p < 0.05 else ""
        st.metric(f"{label}{sig}", f"Pre: {late.mean():.1f} vs Early: {early.mean():.1f}", f"p={p:.4f}")

elif view == "Tendencia temporal":
    st.title("Evolucion del sueno en el tiempo")

    monthly = cs.copy()
    monthly["month"] = monthly["night_date"].dt.to_period("M")
    agg = monthly.groupby("month").agg(
        sleep=("total_sleep_min", "mean"), rem=("pct_rem", "mean"),
        deep=("pct_deep", "mean"), awakenings=("n_awakenings", "mean"),
        n=("night_date", "count")
    ).reset_index()
    agg["month_dt"] = agg["month"].dt.to_timestamp()
    agg = agg[agg["n"] >= 10]

    metric = st.selectbox("Metrica", ["sleep", "rem", "deep", "awakenings"],
                          format_func=lambda x: {"sleep": "Duracion media (min)", "rem": "% REM",
                                                  "deep": "% Deep", "awakenings": "Despertares"}[x])

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(agg["month_dt"], agg[metric], "o-", markersize=3, alpha=0.7, color="steelblue")
    x_num = (agg["month_dt"] - agg["month_dt"].min()).dt.days.values
    valid = ~np.isnan(agg[metric].values)
    if valid.sum() > 5:
        z = np.polyfit(x_num[valid], agg[metric].values[valid], 1)
        ax.plot(agg["month_dt"], np.polyval(z, x_num), "--", color="red", alpha=0.7,
                label=f"Tendencia: {z[0]*365:.2f}/ano")
        ax.legend()
    ax.set_title("Media mensual")
    ax.tick_params(axis="x", rotation=30)
    st.pyplot(fig)
