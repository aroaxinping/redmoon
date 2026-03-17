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
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, StratifiedGroupKFold, cross_val_score

from redmoon.constants import (
    PHASE_ORDER, PHASE_COLORS, METRIC_LABELS,
    MIN_SLEEP_MIN, MAX_INBED_MIN, EARLY_MORNING_CUTOFF,
    MIN_CYCLE_DAYS, MAX_CYCLE_DAYS, NEW_PERIOD_GAP_DAYS,
    assign_phase,
)

st.set_page_config(page_title="Cycle & Sleep", layout="wide", page_icon="🌙")

_root = Path(__file__).parent
DATA_DIR = _root / "data" if (_root / "data" / "sleep.csv").exists() else _root / "sample_data"

# ---------------------------------------------------------------------------
# Translations
# ---------------------------------------------------------------------------
# PHASE_ORDER keys ("Menstrual", "Folicular", "Ovulatoria", "Lútea") come from
# redmoon.constants and stay as-is — they're used for real data grouping
# elsewhere in the package. Only *display* labels are translated here.

LANG = {
    "English": {
        "sidebar_title": "Cycle & Sleep",
        "sidebar_subtitle": "Hormonal patterns in sleep quality",
        "nights_analyzed": "Nights analyzed",
        "complete_cycles": "Complete cycles",
        "avg_cycle": "Avg. cycle",
        "days": "days",
        "view_label": "View",
        "views": ["Summary", "Sleep by phase", "Biomarkers", "Premenstrual effect", "Time trend", "Related research"],
        "summary_title": "Cycle & Sleep: Hormonal Patterns in Sleep Quality",
        "avg_sleep": "Avg. sleep",
        "avg_efficiency": "Avg. efficiency",
        "avg_hrv": "Avg. HRV",
        "avg_resting_hr": "Avg. resting HR",
        "stat_significance": "Statistical significance by metric",
        "metric_col": "Metric",
        "p_value_col": "p-value",
        "result_col": "Result",
        "significant": "Significant",
        "not_significant": "Not significant",
        "metric_labels": {
            "total_sleep_min": "Duration", "pct_rem": "% REM", "pct_deep": "% Deep",
            "efficiency": "Efficiency", "n_awakenings": "Awakenings",
            "temp_c": "Temperature", "hrv_ms": "HRV", "resting_hr_bpm": "Resting HR",
            "disturbances": "Breathing disturbances",
        },
        "key_findings_title": "Key findings",
        "key_findings_md": (
            "- **Temperature, HRV and Resting HR** show highly significant differences between phases\n"
            "- **Sleep metrics** (duration, REM, Deep) don't change significantly between phases overall\n"
            "- **Premenstrual effect**: more awakenings in the 5 days before the period"
        ),
        "sleep_by_phase_title": "Sleep metrics by cycle phase",
        "metric_select": "Metric",
        "sleep_metric_labels": {
            "total_sleep_min": "Duration (min)", "pct_rem": "% REM", "pct_deep": "% Deep",
            "efficiency": "Efficiency (%)", "n_awakenings": "Awakenings",
        },
        "cycle_position": "Cycle position",
        "cycle_evolution": "Evolution across the cycle",
        "biomarkers_title": "Physiological biomarkers by phase",
        "biomarker_select": "Biomarker",
        "biomarker_labels": {
            "temp_c": "Wrist temperature (°C)", "hrv_ms": "HRV (ms)", "resting_hr_bpm": "Resting HR (bpm)",
        },
        "premenstrual_title": "Premenstrual effect: last 5 days before the period",
        "premenstrual_metric_labels": {
            "total_sleep_min": "Duration (min)", "n_awakenings": "Awakenings",
            "pct_rem": "% REM", "efficiency": "Efficiency (%)",
        },
        "premenstrual_delta": "Pre: {late:.1f} vs Early: {early:.1f}",
        "trend_title": "Sleep evolution over time",
        "trend_metric_labels": {
            "sleep": "Avg. duration (min)", "rem": "% REM", "deep": "% Deep", "awakenings": "Awakenings",
        },
        "monthly_avg": "Monthly average",
        "trend_label": "Trend: {rate:.2f}/year",
        "phase_labels": {"Menstrual": "Menstrual", "Folicular": "Follicular", "Ovulatoria": "Ovulatory", "Lútea": "Luteal"},
        "research_intro": (
            "This project is N=1, self-tracked, with no hormone-confirmed phase. "
            "Before trusting my own conclusions, I checked them against peer-reviewed "
            "studies and against my own validation methodology. Full write-up in "
            "[RESEARCH.md](https://github.com/aroaxinping/redmoon/blob/main/RESEARCH.md)."
        ),
        "research_leakage_title": "Data leakage I found and fixed in my own ML model",
        "research_leakage_caption": (
            "My Random Forest (luteal vs non-luteal) was validated with `StratifiedKFold`, which "
            "splits individual nights at random — nights from the same cycle could land in both "
            "train and test, so the model was partly recognising a cycle it had already seen. "
            "Fixed with `StratifiedGroupKFold`, grouping by real cycle. The honest F1 is **0.73**, "
            "not the 0.79 originally published."
        ),
        "research_temp_title": "Wrist temperature in luteal phase vs a published study",
        "research_temp_caption": (
            "My +0.375°C is close to the +0.33°C reported by Shilaih et al. (2018, *Bioscience "
            "Reports*, 136 participants / 437 cycles, P<0.001) — same direction, same order of "
            "magnitude, despite my sample being one person tracked for years instead of a cohort."
        ),
        "research_sources_title": "Sources used",
        "research_sources_md": (
            "- Shilaih et al. (2018). [Modern fertility awareness methods: wrist wearables capture temperature changes](https://pmc.ncbi.nlm.nih.gov/articles/PMC6265623/). *Bioscience Reports*.\n"
            "- Schmalenberger et al. (2020). [Menstrual Cycle Changes in Vagally-Mediated HRV Are Associated with Progesterone](https://pmc.ncbi.nlm.nih.gov/articles/PMC7141121/). *J Clin Med*.\n"
            "- Alzueta et al. (2022). [Tracking Sleep, Temperature, Heart Rate and Daily Symptoms with the Oura Ring](https://pubmed.ncbi.nlm.nih.gov/35422659/). *Int J Women's Health*.\n"
            "- Lin et al. (2024). [Understanding wrist skin temperature changes to hormone variations](https://pubmed.ncbi.nlm.nih.gov/39372385/). *npj Women's Health*.\n"
            "- [Machine learning-based menstrual phase identification using wearable device data](https://www.nature.com/articles/s44294-025-00078-8) (2025). *npj Women's Health*.\n"
            "- [The Validity of Apple Watch Series 9 and Ultra 2 for HRV](https://pmc.ncbi.nlm.nih.gov/articles/PMC11478500/) (2024)."
        ),
    },
    "Español": {
        "sidebar_title": "Cycle & Sleep",
        "sidebar_subtitle": "Analisis de patrones hormonales en la calidad del sueño",
        "nights_analyzed": "Noches analizadas",
        "complete_cycles": "Ciclos completos",
        "avg_cycle": "Ciclo medio",
        "days": "dias",
        "view_label": "Vista",
        "views": ["Resumen", "Sueño por fase", "Biomarcadores", "Efecto premenstrual", "Tendencia temporal", "Investigacion relacionada"],
        "summary_title": "Cycle & Sleep: Patrones Hormonales en la Calidad del Sueño",
        "avg_sleep": "Sueño medio",
        "avg_efficiency": "Eficiencia media",
        "avg_hrv": "HRV medio",
        "avg_resting_hr": "Resting HR medio",
        "stat_significance": "Significancia estadistica por metrica",
        "metric_col": "Metrica",
        "p_value_col": "p-valor",
        "result_col": "Resultado",
        "significant": "Significativo",
        "not_significant": "No significativo",
        "metric_labels": {
            "total_sleep_min": "Duracion", "pct_rem": "% REM", "pct_deep": "% Deep",
            "efficiency": "Eficiencia", "n_awakenings": "Despertares",
            "temp_c": "Temperatura", "hrv_ms": "HRV", "resting_hr_bpm": "Resting HR",
            "disturbances": "Pert. respiratorias",
        },
        "key_findings_title": "Hallazgos principales",
        "key_findings_md": (
            "- **Temperatura, HRV y Resting HR** muestran diferencias altamente significativas entre fases\n"
            "- **Las metricas de sueño** (duracion, REM, Deep) no cambian significativamente entre fases a nivel global\n"
            "- **Efecto premenstrual**: mas despertares en los ultimos 5 dias antes del periodo"
        ),
        "sleep_by_phase_title": "Metricas de sueño por fase del ciclo",
        "metric_select": "Metrica",
        "sleep_metric_labels": {
            "total_sleep_min": "Duracion (min)", "pct_rem": "% REM", "pct_deep": "% Deep",
            "efficiency": "Eficiencia (%)", "n_awakenings": "Despertares",
        },
        "cycle_position": "Posicion en el ciclo",
        "cycle_evolution": "Evolucion a lo largo del ciclo",
        "biomarkers_title": "Biomarcadores fisiologicos por fase",
        "biomarker_select": "Biomarcador",
        "biomarker_labels": {
            "temp_c": "Temperatura muneca (°C)", "hrv_ms": "HRV (ms)", "resting_hr_bpm": "Resting HR (bpm)",
        },
        "premenstrual_title": "Efecto premenstrual: ultimos 5 dias antes del periodo",
        "premenstrual_metric_labels": {
            "total_sleep_min": "Duracion (min)", "n_awakenings": "Despertares",
            "pct_rem": "% REM", "efficiency": "Eficiencia (%)",
        },
        "premenstrual_delta": "Pre: {late:.1f} vs Temprana: {early:.1f}",
        "trend_title": "Evolucion del sueño en el tiempo",
        "trend_metric_labels": {
            "sleep": "Duracion media (min)", "rem": "% REM", "deep": "% Deep", "awakenings": "Despertares",
        },
        "monthly_avg": "Media mensual",
        "trend_label": "Tendencia: {rate:.2f}/ano",
        "phase_labels": {"Menstrual": "Menstrual", "Folicular": "Folicular", "Ovulatoria": "Ovulatoria", "Lútea": "Lútea"},
        "research_intro": (
            "Este proyecto es N=1, autoseguimiento, sin fase confirmada por hormona. Antes de "
            "fiarme de mis propias conclusiones, las contraste con estudios revisados por pares "
            "y con mi propia metodologia de validacion. Analisis completo en "
            "[RESEARCH.md](https://github.com/aroaxinping/redmoon/blob/main/RESEARCH.md)."
        ),
        "research_leakage_title": "Fuga de datos que encontre y arregle en mi propio modelo de ML",
        "research_leakage_caption": (
            "Mi Random Forest (lutea vs no-lutea) se validaba con `StratifiedKFold`, que reparte "
            "noches individuales al azar — noches del mismo ciclo podian caer a la vez en train y "
            "test, asi que el modelo reconocia en parte un ciclo que ya habia visto. Arreglado con "
            "`StratifiedGroupKFold`, agrupando por ciclo real. El F1 honesto es **0.73**, no el "
            "0.79 publicado originalmente."
        ),
        "research_temp_title": "Temperatura de muneca en fase lutea vs un estudio publicado",
        "research_temp_caption": (
            "Mi +0.375°C esta cerca del +0.33°C que reportan Shilaih et al. (2018, *Bioscience "
            "Reports*, 136 participantes / 437 ciclos, P<0.001) — misma direccion, mismo orden de "
            "magnitud, aunque mi muestra sea una sola persona seguida durante anos en vez de una "
            "cohorte."
        ),
        "research_sources_title": "Fuentes utilizadas",
        "research_sources_md": (
            "- Shilaih et al. (2018). [Modern fertility awareness methods: wrist wearables capture temperature changes](https://pmc.ncbi.nlm.nih.gov/articles/PMC6265623/). *Bioscience Reports*.\n"
            "- Schmalenberger et al. (2020). [Menstrual Cycle Changes in Vagally-Mediated HRV Are Associated with Progesterone](https://pmc.ncbi.nlm.nih.gov/articles/PMC7141121/). *J Clin Med*.\n"
            "- Alzueta et al. (2022). [Tracking Sleep, Temperature, Heart Rate and Daily Symptoms with the Oura Ring](https://pubmed.ncbi.nlm.nih.gov/35422659/). *Int J Women's Health*.\n"
            "- Lin et al. (2024). [Understanding wrist skin temperature changes to hormone variations](https://pubmed.ncbi.nlm.nih.gov/39372385/). *npj Women's Health*.\n"
            "- [Machine learning-based menstrual phase identification using wearable device data](https://www.nature.com/articles/s44294-025-00078-8) (2025). *npj Women's Health*.\n"
            "- [The Validity of Apple Watch Series 9 and Ultra 2 for HRV](https://pmc.ncbi.nlm.nih.gov/articles/PMC11478500/) (2024)."
        ),
    },
}


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

    # Same period index assign_phase() used to find the match — needed as a
    # group key so nights from one cycle never split across train/test in CV.
    period_bins = periods["start"].tolist() + [pd.Timestamp.max]
    nightly_df["cycle_id"] = pd.cut(nightly_df["night_date"], bins=period_bins, labels=False, right=False)

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


@st.cache_data
def compute_f1_leakage_comparison(cs):
    """Naive row-level CV vs group-aware CV for the luteal/non-luteal classifier.
    See RESEARCH.md section 5 for why the naive number is optimistic."""
    pred_cols = ["temp_c", "hrv_ms", "resting_hr_bpm"]
    pred_data = cs.dropna(subset=pred_cols + ["phase", "cycle_id"])
    if len(pred_data) < 100:
        return None, None

    X = pred_data[pred_cols].values
    y = np.where(pred_data["phase"].values == "Lútea", "Lútea", "No-Lútea")
    groups = pred_data["cycle_id"].values
    clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")

    cv_naive = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    f1_naive = cross_val_score(clf, X, y, cv=cv_naive, scoring="f1_macro").mean()

    cv_group = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    f1_group = cross_val_score(clf, X, y, cv=cv_group, groups=groups, scoring="f1_macro").mean()

    return f1_naive, f1_group


# --- Language selector ---
lang_choice = st.sidebar.selectbox("Language / Idioma", ["English", "Español"])
T = LANG[lang_choice]
phase_display = [T["phase_labels"][p] for p in PHASE_ORDER]

# --- Load data ---
cs, periods = load_and_process()

# --- Sidebar ---
st.sidebar.title(T["sidebar_title"])
st.sidebar.markdown(T["sidebar_subtitle"])
st.sidebar.markdown("---")
st.sidebar.metric(T["nights_analyzed"], len(cs))
st.sidebar.metric(T["complete_cycles"], len(periods) - 1)
valid_cycles = periods.dropna(subset=["cycle_length"])
st.sidebar.metric(T["avg_cycle"], f"{valid_cycles['cycle_length'].mean():.0f} {T['days']}")
st.sidebar.markdown("---")

view = st.sidebar.radio(T["view_label"], T["views"])
views = T["views"]

# --- Main content ---
if view == views[0]:  # Summary
    st.title(T["summary_title"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(T["avg_sleep"], f"{cs['total_sleep_min'].mean()/60:.1f}h")
    col2.metric(T["avg_efficiency"], f"{cs['efficiency'].mean():.0f}%")
    col3.metric(T["avg_hrv"], f"{cs['hrv_ms'].mean():.0f} ms")
    col4.metric(T["avg_resting_hr"], f"{cs['resting_hr_bpm'].mean():.0f} bpm")

    st.markdown(f"### {T['stat_significance']}")
    metrics_all = ["total_sleep_min", "pct_rem", "pct_deep", "efficiency", "n_awakenings",
                   "temp_c", "hrv_ms", "resting_hr_bpm", "disturbances"]

    rows = []
    for m in metrics_all:
        stat, p = kw_test(cs, m)
        if stat is not None:
            sig = T["significant"] if p < 0.05 else T["not_significant"]
            rows.append({T["metric_col"]: T["metric_labels"].get(m, m), "H": f"{stat:.1f}",
                         T["p_value_col"]: f"{p:.6f}", T["result_col"]: sig})
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    st.markdown(f"### {T['key_findings_title']}")
    st.markdown(T["key_findings_md"])

elif view == views[1]:  # Sleep by phase
    st.title(T["sleep_by_phase_title"])

    metric = st.selectbox(T["metric_select"], list(T["sleep_metric_labels"].keys()),
                          format_func=lambda x: T["sleep_metric_labels"][x])

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots(figsize=(8, 5))
        data = [cs[cs["phase"] == p][metric].dropna() for p in PHASE_ORDER]
        bp = ax.boxplot(data, tick_labels=phase_display, patch_artist=True, widths=0.6)
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
        ax.set_xlabel(T["cycle_position"])
        ax.set_title(T["cycle_evolution"])
        st.pyplot(fig)

    # Summary table
    summary = cs.groupby("phase")[metric].agg(["mean", "std", "median", "count"]).round(2)
    summary = summary.reindex(PHASE_ORDER)
    summary.index = phase_display
    st.dataframe(summary, width="stretch")

elif view == views[2]:  # Biomarkers
    st.title(T["biomarkers_title"])

    bio = st.selectbox(T["biomarker_select"], list(T["biomarker_labels"].keys()),
                       format_func=lambda x: T["biomarker_labels"][x])

    bio_data = cs.dropna(subset=[bio])
    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots(figsize=(8, 5))
        data = [bio_data[bio_data["phase"] == p][bio].dropna() for p in PHASE_ORDER]
        bp = ax.boxplot(data, tick_labels=phase_display, patch_artist=True, widths=0.6)
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
        ax.set_xlabel(T["cycle_position"])
        ax.set_title(T["cycle_evolution"])
        st.pyplot(fig)

    summary = bio_data.groupby("phase")[bio].agg(["mean", "std", "count"]).round(3)
    summary = summary.reindex(PHASE_ORDER)
    summary.index = phase_display
    st.dataframe(summary, width="stretch")

elif view == views[3]:  # Premenstrual effect
    st.title(T["premenstrual_title"])

    luteal = cs[cs["phase"] == "Lútea"].copy()
    luteal["days_to_period"] = luteal["cycle_length"] - luteal["cycle_day"]
    luteal["sub"] = np.where(luteal["days_to_period"] <= 5, "late", "early")

    for metric, label in T["premenstrual_metric_labels"].items():
        early = luteal[luteal["sub"] == "early"][metric].dropna()
        late = luteal[luteal["sub"] == "late"][metric].dropna()
        u, p = stats.mannwhitneyu(early, late, alternative="two-sided")
        sig = " *" if p < 0.05 else ""
        st.metric(f"{label}{sig}", T["premenstrual_delta"].format(late=late.mean(), early=early.mean()), f"p={p:.4f}")

elif view == views[4]:  # Time trend
    st.title(T["trend_title"])

    monthly = cs.copy()
    monthly["month"] = monthly["night_date"].dt.to_period("M")
    agg = monthly.groupby("month").agg(
        sleep=("total_sleep_min", "mean"), rem=("pct_rem", "mean"),
        deep=("pct_deep", "mean"), awakenings=("n_awakenings", "mean"),
        n=("night_date", "count")
    ).reset_index()
    agg["month_dt"] = agg["month"].dt.to_timestamp()
    agg = agg[agg["n"] >= 10]

    metric = st.selectbox(T["metric_select"], list(T["trend_metric_labels"].keys()),
                          format_func=lambda x: T["trend_metric_labels"][x])

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(agg["month_dt"], agg[metric], "o-", markersize=3, alpha=0.7, color="steelblue")
    x_num = (agg["month_dt"] - agg["month_dt"].min()).dt.days.values
    valid = ~np.isnan(agg[metric].values)
    if valid.sum() > 5:
        z = np.polyfit(x_num[valid], agg[metric].values[valid], 1)
        ax.plot(agg["month_dt"], np.polyval(z, x_num), "--", color="red", alpha=0.7,
                label=T["trend_label"].format(rate=z[0]*365))
        ax.legend()
    ax.set_title(T["monthly_avg"])
    ax.tick_params(axis="x", rotation=30)
    st.pyplot(fig)

elif view == views[5]:  # Related research
    st.title(T["views"][5])
    st.markdown(T["research_intro"])

    st.markdown(f"### {T['research_leakage_title']}")
    f1_naive, f1_group = compute_f1_leakage_comparison(cs)
    if f1_naive is not None:
        fig, ax = plt.subplots(figsize=(5, 4))
        bars = ax.bar(["StratifiedKFold", "StratifiedGroupKFold"], [f1_naive, f1_group],
                      color=["#e74c3c", "#2ecc71"], alpha=0.75, width=0.5)
        ax.set_ylabel("F1-macro")
        ax.set_ylim(0, 1)
        for bar, val in zip(bars, [f1_naive, f1_group]):
            ax.text(bar.get_x() + bar.get_width() / 2, val + 0.02, f"{val:.3f}",
                    ha="center", fontweight="bold")
        st.pyplot(fig)
    st.caption(T["research_leakage_caption"])

    st.markdown(f"### {T['research_temp_title']}")
    fig, ax = plt.subplots(figsize=(5, 4))
    bars = ax.bar(["redmoon (N=1)", "Shilaih et al. 2018\n(n=136)"], [0.375, 0.33],
                  color=["#f39c12", "#3498db"], alpha=0.75, width=0.5)
    ax.set_ylabel("°C")
    for bar, val in zip(bars, [0.375, 0.33]):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.01, f"+{val:.2f}°C",
                ha="center", fontweight="bold")
    st.pyplot(fig)
    st.caption(T["research_temp_caption"])

    st.markdown(f"### {T['research_sources_title']}")
    st.markdown(T["research_sources_md"])
