# Changelog

All notable changes to redmoon will be documented in this file.

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
