# Changelog

All notable changes to redmoon will be documented in this file.

## [Unreleased]

### Added

- Summary comparison chart ("How my findings compare to published research")
  covering all 6 findings from `RESEARCH.md` in one view — color-coded by match
  type (direction+magnitude / direction-only / replicated null / weakest finding
  / gap vs benchmark), not by a made-up numeric score. Added as a static image
  in `RESEARCH.md`'s conclusion and as a live, bilingual chart in the
  dashboard's "Related research" view.

## [0.3.1] - 2026-07-26

### Changed

- Translated all Spanish-only content to English for consistency across the
  project: `README.md`, `RESEARCH.md`, `CHANGELOG.md`, `notebooks/analysis.ipynb`
  (all 16 sections — headers, prints, chart titles and labels), and the
  package's own console/library output — `CycleSleepAnalyzer.summary()`,
  `METRIC_LABELS`, docstrings and CLI help text. `report.phase_means()` and
  `report.statistical_tests()` now return English metric labels instead of
  Spanish ones.
- `dashboard.py`: renamed the ad-hoc "No-Lútea" classification label to
  "Non-Luteal" for the same reason.

Left untouched, on purpose: `PHASE_ORDER`'s literal values (`Menstrual`,
`Folicular`, `Ovulatoria`, `Lútea`) — they're real data grouping keys used
throughout the codebase, not display text.

## [0.3.0] - 2026-07-26

### Added

- `RESEARCH.md`: finding-by-finding comparison of redmoon's results against
  peer-reviewed published studies (wrist temperature, HRV, resting HR, sleep
  architecture, ML prediction), plus a section on how reliable the Apple Watch is
  as a measurement instrument
- `cycle_id` in `CycleSleepAnalyzer`: identifies which real cycle each night
  belongs to, needed as a group key for correct cross-validation
- Test: `test_cycle_id_groups_nights_by_cycle`
- "Related research" view in the Streamlit dashboard (bilingual): a chart of the
  data-leakage fix (F1 before/after) and a chart comparing wrist temperature
  against Shilaih et al. 2018, plus the sources cited in `RESEARCH.md` with links

### Fixed

- **Data leakage in the Random Forest validation**: the phase-prediction model
  (luteal vs non-luteal) used `StratifiedKFold`, which splits individual nights
  between train/test without accounting for the fact that nights from the same
  cycle aren't independent of each other. This inflated the published metric
  (F1=0.79). Fixed to `StratifiedGroupKFold` grouping by `cycle_id` — the real,
  correctly validated number is F1=0.73. Full detail in `RESEARCH.md`, section 5.
- `notebooks/analysis.ipynb`: the variable `phase_order` was used in 9 cells
  without being defined anywhere — it only "worked" if someone had left it in
  memory from a previous manual Jupyter session. The notebook didn't run
  end-to-end from a clean kernel. Added `phase_order = PHASE_ORDER` in the
  imports cell; verified end-to-end with `jupyter nbconvert --execute` on real
  data.

## [0.2.0] - 2026-04-02

### Added

- Anonymized sample data for testing without a real Apple Health export
- Unit tests for parser, analyzer and phase-assignment logic (edge cases included)
- `report.to_json()` and CLI `--json` flag for JSON export
- `redmoon dashboard` CLI subcommand
- Type hints, logging and input validation across the package
- GitHub Actions CI running tests on Python 3.9-3.12
- CI, PyPI, Python and license badges in README

### Changed

- Dashboard falls back to `sample_data/` when `data/` is missing
- Extracted constants and de-duplicated phase-assignment logic
- Rewrote README with clearer structure for both users and portfolio readers

### Fixed

- Removed real data CSVs from version control, `data/` fully gitignored
- Removed deprecated license classifier from `pyproject.toml`
- Added explicit packages config for setuptools build

### Removed

- Legacy standalone parser (superseded by the packaged version)

---

## [0.1.0] - 2026-04-02

### Added

- Apple Health XML parser for sleep and menstrual cycle data
- Cycle phase detection and sleep metrics analysis
- HRV and resting heart rate extraction and analysis by cycle phase
- Random Forest model for phase prediction
- Interactive Streamlit dashboard with 5 views
- CLI entry point (`redmoon analyze <export.xml>`)
- Packaging for PyPI distribution (originally named `cyclesleep`, renamed to `redmoon`)

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
