# redmoon

[![CI](https://github.com/aroaxinping/redmoon/actions/workflows/ci.yml/badge.svg)](https://github.com/aroaxinping/redmoon/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/redmoon)](https://pypi.org/project/redmoon/)
[![Python](https://img.shields.io/pypi/pyversions/redmoon)](https://pypi.org/project/redmoon/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

Herramienta de analisis que cruza datos del ciclo menstrual con metricas de sueno, HRV y frecuencia cardiaca a partir de tu exportacion de Apple Health.

Una sola linea y obtienes un informe con tests estadisticos, correlaciones y deteccion de patrones hormonales en tu sueno.

```bash
pip install redmoon
redmoon analyze exportacion.xml
```

No tienes datos de Apple Health? El repo incluye **datos sinteticos de ejemplo** para probar todo sin necesitar un iPhone:

```bash
git clone https://github.com/aroaxinping/redmoon.git
cd redmoon
pip install -e ".[all]"
pytest tests/ -v          # 48 tests
redmoon dashboard         # abre el dashboard con datos de ejemplo
```

---

## Que encuentra redmoon

Resultados reales con ~6 anos de datos de Apple Health (76 ciclos, 1,153 noches):

| Metrica | Cambia con el ciclo? | Detalle |
|---|---|---|
| Temperatura de muneca | Si (p < 0.000001) | +0.375 C en fase lutea vs folicular |
| HRV | Si (p < 0.000001) | -3ms en fase lutea |
| Frecuencia cardiaca en reposo | Si (p < 0.000001) | +2bpm en fase lutea |
| Despertares premenstruales | Si (p = 0.034) | +1.1 despertares/noche los ultimos 5 dias |
| Duracion del sueno | No (p = 0.28) | Sin diferencia entre fases |
| % REM / % Deep | No (p > 0.7) | Sin diferencia entre fases |
| Eficiencia del sueno | No (p = 0.21) | Sin diferencia entre fases |

**Conclusion**: las hormonas cambian tu fisiologia nocturna de forma muy clara (temperatura, HRV, frecuencia cardiaca), pero el sueno en si solo se ve afectado justo antes del periodo, con mas despertares.

---

## Como usar redmoon con tus datos

### 1. Exportar datos de Apple Health

En tu iPhone: Salud → foto de perfil → Exportar datos de salud → te genera un zip con `exportacion.xml`.

### 2. Instalar

```bash
pip install redmoon
```

Con extras opcionales:

```bash
pip install redmoon[all]    # incluye visualizaciones, ML y dashboard
pip install redmoon[viz]    # solo matplotlib + seaborn
pip install redmoon[ml]     # solo scikit-learn
```

### 3. Ejecutar analisis

**Desde terminal:**

```bash
# Analisis completo con report en consola
redmoon analyze exportacion.xml

# Guardar report a archivo + CSVs intermedios
redmoon analyze exportacion.xml --output report.txt --csv-dir data/

# Exportar como JSON (para integraciones o procesado posterior)
redmoon analyze exportacion.xml --json --output report.json

# Modo verbose para ver logs detallados
redmoon -v analyze exportacion.xml
```

**Como libreria Python:**

```python
from redmoon import parse_export, CycleSleepAnalyzer

data = parse_export("exportacion.xml")
analyzer = CycleSleepAnalyzer(data)
report = analyzer.run()

# Report completo en texto
print(report.summary())

# Medias por fase como DataFrame
report.phase_means()

# Tests estadisticos
report.statistical_tests()

# Efecto premenstrual
report.premenstrual_effect()

# Exportar como diccionario JSON-serializable
report.to_json()
```

### 4. Dashboard interactivo (opcional)

```bash
pip install redmoon[all]
redmoon dashboard
```

5 vistas: resumen, sueno por fase, biomarcadores, efecto premenstrual, tendencia temporal.

Si no tienes datos propios en `data/`, el dashboard usa automaticamente los datos sinteticos de `sample_data/`.

### 5. Notebook de analisis (opcional)

```bash
jupyter notebook notebooks/analysis.ipynb
```

16 secciones con visualizaciones completas, tests estadisticos, prediccion ML, y correlaciones.

---

## Que datos necesitas

redmoon extrae automaticamente del XML de Apple Health:

| Dato | Fuente | Registros tipicos |
|---|---|---|
| Fases de sueno (Core, REM, Deep, Awake) | Apple Watch | Miles |
| Flujo menstrual | App Salud / tracker | Cientos |
| Temperatura de muneca nocturna | Apple Watch Ultra / Series 8+ | Cientos |
| HRV (SDNN) | Apple Watch | Miles |
| Frecuencia cardiaca en reposo | Apple Watch | Miles |
| Perturbaciones respiratorias | Apple Watch | Cientos |

No necesitas todos. El minimo es **sueno + periodo**. Los biomarcadores (temperatura, HRV, HR) enriquecen el analisis pero son opcionales.

---

## Metodologia

### Agregacion nocturna

Cada noche se asigna a la fecha en que empieza el sueno. Si te duermes a las 2:00, esa noche cuenta como el dia anterior. Se filtran noches con <2h de sueno o >16h en cama.

### Deteccion de ciclos

Los dias de sangrado consecutivos se agrupan en periodos. Un nuevo periodo empieza cuando hay >5 dias sin sangrado. Ciclos de <21 o >45 dias se excluyen.

### Asignacion de fases

Cada ciclo se divide en 4 fases proporcionalmente a su duracion real:

| Fase | Dias tipicos | Que pasa hormonalmente |
|---|---|---|
| **Menstrual** | 1-5 | Estrogeno y progesterona en minimo. Sangrado. Fatiga. |
| **Folicular** | 6-13 | Estrogeno sube. Mas energia y claridad mental. |
| **Ovulatoria** | 14-16 | Pico de estrogeno y LH. Liberacion del ovulo. Temperatura empieza a subir. |
| **Lutea** | 17-28+ | Progesterona alta. Temperatura +0.3-0.5 C. Al final, caida hormonal → PMS. |

La fase lutea se subdivide en **lutea temprana** y **premenstrual** (ultimos 5 dias) para aislar el efecto PMS.

### Tests estadisticos

- **Kruskal-Wallis**: test no parametrico para comparar las 4 fases
- **Mann-Whitney U con correccion de Bonferroni**: comparaciones post-hoc por pares
- **Spearman**: correlaciones entre metricas
- **Random Forest**: prediccion de fase lutea vs no-lutea (F1 = 0.79 con temperatura + HRV + HR)

### Limpieza de outliers

- **Eficiencia > 100%**: Apple Health puede registrar InBed desde el iPhone y las fases desde el Watch, causando inconsistencias. Se usa `max(InBed, sleep+awake)` como denominador y se capea al 100%.
- **Ciclos anormales**: <21 o >45 dias se excluyen.
- **Noches pre-2020**: solo tienen InBed sin desglose en fases (el Watch no lo soportaba).

---

## Estructura del proyecto

```
redmoon/
├── redmoon/               # Paquete Python (PyPI)
│   ├── __init__.py        #   Exports: parse_export, CycleSleepAnalyzer
│   ├── parser.py          #   XML → DataFrames
│   ├── analyzer.py        #   Analisis + report + JSON export
│   ├── constants.py       #   Constantes, umbrales y logica de fases
│   └── cli.py             #   CLI: redmoon analyze / redmoon dashboard
├── tests/                 # Tests (pytest, 48 tests)
│   ├── test_parser.py     #   Parser: tipos, columnas, validacion, edge cases
│   ├── test_analyzer.py   #   Analyzer: pipeline, report, JSON serialization
│   └── test_constants.py  #   Asignacion de fases, ciclos limite (21/45d)
├── sample_data/           # Datos sinteticos (3 ciclos, ~85 noches)
├── notebooks/
│   └── analysis.ipynb     # Analisis completo con graficas
├── dashboard.py           # Dashboard Streamlit (5 vistas)
├── .github/workflows/     # CI: tests en Python 3.9-3.12
├── data/                  # (gitignored) tus datos privados
├── pyproject.toml
└── LICENSE                # MIT
```

## Desarrollo local

```bash
git clone https://github.com/aroaxinping/redmoon.git
cd redmoon
pip install -e ".[all]"
pip install pytest
```

```bash
# Ejecutar tests
pytest tests/ -v

# Probar con datos de ejemplo
python -c "
import pandas as pd
from redmoon import CycleSleepAnalyzer

data = {
    k: pd.read_csv(
        f'sample_data/{k}.csv',
        parse_dates=['start', 'end'] if k == 'sleep' else None,
    )
    for k in ['sleep', 'menstrual', 'wrist_temp', 'hrv', 'resting_hr', 'breathing']
}
print(CycleSleepAnalyzer(data).run().summary())
"
```

## Privacidad

Los datos de salud estan en `.gitignore`. El repo solo contiene codigo y datos sinteticos de ejemplo. Ningun dato personal se sube.

## Licencia

MIT
