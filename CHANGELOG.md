# Changelog

All notable changes to redmoon will be documented in this file.

## [0.3.0] - 2026-07-26

### Added

- `RESEARCH.md`: comparación hallazgo-por-hallazgo de los resultados de redmoon con
  estudios publicados revisados por pares (temperatura de muñeca, HRV, resting HR,
  arquitectura del sueño, predicción ML), más una sección sobre fiabilidad del Apple
  Watch como instrumento de medida
- `cycle_id` en `CycleSleepAnalyzer`: identifica a qué ciclo real pertenece cada noche,
  necesario como group key para cross-validation correcta
- Test: `test_cycle_id_groups_nights_by_cycle`
- Vista "Related research" en el dashboard Streamlit (bilingüe): gráfico del fix de
  fuga de datos (F1 antes/después) y gráfico comparando temperatura de muñeca con
  Shilaih et al. 2018, más las fuentes citadas en `RESEARCH.md` con enlaces

### Fixed

- **Fuga de datos en la validación del Random Forest**: el modelo de predicción de fase
  (lútea vs no-lútea) usaba `StratifiedKFold`, que reparte noches individuales entre
  train/test sin tener en cuenta que noches del mismo ciclo no son independientes entre
  sí. Esto inflaba la métrica publicada (F1=0.79). Corregido a `StratifiedGroupKFold`
  agrupando por `cycle_id` — el número real y validado correctamente es F1=0.73. Detalle
  completo en `RESEARCH.md`, sección 5.
- `notebooks/analysis.ipynb`: la variable `phase_order` se usaba en 9 celdas sin estar
  definida en ningún sitio — solo funcionaba si alguien la había dejado en memoria de una
  sesión manual anterior de Jupyter. El notebook no se ejecutaba de principio a fin desde
  un kernel limpio. Añadido `phase_order = PHASE_ORDER` en la celda de imports; verificado
  con `jupyter nbconvert --execute` de principio a fin sobre datos reales.

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
