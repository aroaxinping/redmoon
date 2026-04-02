# Cycle & Sleep: Hormonal Patterns in Sleep Quality

Análisis de datos reales de Apple Health para investigar si existe una relación entre el ciclo menstrual y la calidad del sueño.

## Hipótesis

> El ciclo hormonal influye en la duración, estructura y calidad del sueño de forma predecible a lo largo de sus fases (menstrual, folicular, ovulatoria, lútea).

## Datos

Exportación de Apple Health (~6 años de datos) con:
- **Sueño**: fases detalladas (Core, REM, Deep, Awake), duración total, eficiencia
- **Periodo**: flujo menstrual con intensidad (light/medium/heavy)
- **Temperatura de muñeca** durante el sueño
- **Perturbaciones respiratorias** nocturnas

## Limpieza de datos y tratamiento de outliers

Los datos crudos de Apple Health contienen inconsistencias que hay que aislar antes de analizar:

### Eficiencia del sueño > 100%

Apple Health a veces registra el tiempo "InBed" desde una fuente (ej. iPhone) y las fases de sueño desde otra (ej. Apple Watch). Cuando el Watch detecta más tiempo dormido del que el iPhone registró como "en cama", la eficiencia calculada (`sleep / in_bed * 100`) supera el 100%, llegando a valores absurdos como 3600%.

**Solución**: Usamos `max(InBed, sleep + awake)` como denominador, y se capea la eficiencia al 100%. Esto elimina los falsos positivos sin perder noches reales.

### Ciclos anormales

Ciclos de <21 o >45 días se excluyen del análisis de fases. Pueden representar datos de periodo mal registrados, periodos perdidos, o condiciones médicas que alterarían la asignación de fases.

### Noches sin datos de fases

Las noches anteriores a 2020 solo tienen datos "InBed" sin desglose en Core/REM/Deep (Apple Watch no soportaba sleep stages). Se filtran noches con <2h de sueño total y >16h en cama para eliminar registros erróneos.

## Métricas analizadas por fase del ciclo

| Métrica | Descripción |
|---------|-------------|
| Duración total de sueño | Horas dormidas por noche |
| % sueño REM | Proporción de sueño REM sobre total |
| % sueño profundo (Deep) | Proporción de sueño profundo sobre total |
| Eficiencia del sueño | Tiempo dormida / tiempo en cama |
| Despertares nocturnos | Número de interrupciones por noche |
| Temperatura de muñeca | Variación térmica nocturna |
| Perturbaciones respiratorias | Eventos respiratorios por noche |

## Fases del ciclo

El análisis divide cada ciclo en 4 fases estimadas de forma proporcional a la duración real de cada ciclo:
1. **Menstrual** (días 1-5): días de sangrado registrados
2. **Folicular** (días 6-13): post-menstruación hasta ovulación estimada
3. **Ovulatoria** (días 14-16): ventana de ovulación estimada
4. **Lútea** (días 17-28+): post-ovulación hasta siguiente menstruación

Adicionalmente, la fase lútea se subdivide en **lútea temprana** y **premenstrual** (últimos 5 días antes del periodo) para analizar el efecto PMS en el sueño.

## Estructura

```
├── src/
│   └── parse_health_export.py   # Parser XML → CSV
├── notebooks/
│   └── analysis.ipynb           # Análisis completo
├── data/                        # (gitignored) datos privados
│   ├── sleep.csv
│   ├── menstrual.csv
│   ├── wrist_temp.csv
│   └── breathing.csv
└── requirements.txt
```

## Uso

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Colocar exportación de Apple Health en data/
cp ~/Downloads/exportación.zip data/

# 3. Parsear datos
python src/parse_health_export.py data/exportación.xml

# 4. Abrir notebook
jupyter notebook notebooks/analysis.ipynb
```

## Privacidad

Los datos de salud están en `.gitignore`. Solo se comparten los scripts de análisis y los resultados agregados/anonimizados.
