# Related research

`redmoon` analiza mis propios datos para responder una pregunta personal: ¿cambia mi
fisiología nocturna con el ciclo? Esto **no es un estudio** — es N=1, autoseguimiento,
sin grupo de control ni confirmación hormonal de fase. Antes de quedarme con mis propias
conclusiones, quería cruzarlas con estudios hechos con metodología más estricta y
estandarizada: ¿coinciden? ¿dónde no? ¿por qué podría no coincidir?

Esto es ese ejercicio, hallazgo por hallazgo.

---

## 1. Temperatura de muñeca en fase lútea

**Mi hallazgo:** +0.375°C en fase lútea vs folicular (p < 0.000001, Kruskal-Wallis,
1.153 noches / 76 ciclos).

**Estudio 1 (mecanismo):** Lin, G., Li, J. Y., Christofferson, K., Patel, S. N.,
Truong, K. N., & Mariakakis, A. (2024). [Understanding wrist skin temperature changes to
hormone variations across the menstrual cycle](https://pubmed.ncbi.nlm.nih.gov/39372385/).
*npj Women's Health*, 2(1), 35. 50 participantes. Correlación negativa entre temperatura
de muñeca y niveles de E3G/LH medidos directamente en orina — confirma el mecanismo
hormonal, pero el abstract no reporta una cifra en °C comparable a la mía.

**Estudio 2 (magnitud):** Shilaih, M., Goodale, B. M., Falco, L., Kübler, F., De Clerck,
V., & Leeners, B. (2018). [Modern fertility awareness methods: wrist wearables capture
the changes in temperature associated with the menstrual cycle](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6265623/).
*Bioscience Reports*, 38(6), BSR20171279. 136 participantes, 437 ciclos. Temperatura
media en fase lútea temprana **0.33°C más alta** que en la ventana fértil (P<0.001).

**Comparación:** mi +0.375°C está prácticamente en línea con el +0.33°C que reporta
Shilaih et al. con una muestra 136 veces mayor que la mía en número de personas (aunque
con menos noches por persona). Es la coincidencia cuantitativa más ajustada de todo el
documento — no solo la misma dirección, el mismo orden de magnitud.

**Dónde puedo estar sesgada:** ambos estudios de referencia confirman fase con hormona
medida directamente (orina o sangre). Yo asigno fase por día del ciclo, de forma
proporcional a la duración de cada ciclo — sin confirmar ovulación con test de LH ni
medir progesterona real. Mis noches "lúteas" cerca de los bordes (justo tras ovulación,
o justo antes del periodo) pueden estar mal clasificadas. Que aun así mi número
coincida tan de cerca con el de Shilaih et al. sugiere que ese ruido de clasificación no
está distorsionando demasiado el resultado.

---

## 2. HRV en fase lútea

**Mi hallazgo:** −3ms de HRV (SDNN) en fase lútea (p < 0.000001).

**Estudio:** Schmalenberger, K. M., Eisenlohr-Moul, T. A., Jarczok, M. N., et al. (2020).
[Menstrual Cycle Changes in Vagally-Mediated Heart Rate Variability Are Associated with
Progesterone](https://pmc.ncbi.nlm.nih.gov/articles/PMC7141121/). *Journal of Clinical
Medicine*, 9(3), 617. Dos cohortes within-person: EE.UU. (40 participantes, 105 visitas)
y Alemania (50 participantes, 112 visitas). HF-HRV significativamente más baja en fase
lútea media que en folicular media (β=0.55, p<0.05) y que en ovulatoria (β=0.60, p<0.05).
La progesterona predice HRV más baja dentro de cada persona (β=−0.036, p<0.001 en la
cohorte de EE.UU.; β=−0.024, p<0.05 en la alemana). Ni en un cohorte ni en el otro el
estrógeno tuvo efecto significativo.

**Comparación:** coincide en dirección y en el diseño (within-person, como el mío,
comparando a cada persona consigo misma a lo largo del ciclo — no promedios entre
personas distintas). No puedo comparar la magnitud directamente: ellos usan HF-HRV
log-transformada (unidades arbitrarias del dominio de frecuencia), yo uso SDNN en
milisegundos — son métricas de HRV distintas, no la misma escala. Sería incorrecto decir
que mi −3ms "coincide en tamaño" con su β=0.55; solo puedo decir que la dirección y el
mecanismo (progesterona → HRV más baja) coinciden.

**Dónde puedo estar sesgada:** mi "fase lútea" es un bloque ancho (día 17 al final del
ciclo), mientras que el estudio distingue lútea temprana/media/tardía por nivel de
progesterona real. Si mezclo sub-fases con progesterona muy distinta dentro de un mismo
grupo "lútea", mi efecto medio podría estar diluido — el verdadero efecto en lútea media
podría ser mayor de lo que veo.

---

## 3. Frecuencia cardiaca en reposo

**Mi hallazgo:** +2bpm en fase lútea (p < 0.000001).

**Estudio:** Alzueta, E., de Zambotti, M., Javitz, H., et al. (2022). [Tracking sleep,
temperature, heart rate, and daily symptoms across the menstrual cycle with the Oura
Ring in healthy women](https://pubmed.ncbi.nlm.nih.gov/35422659/). *International
Journal of Women's Health*, 14, 491–503. 26 mujeres. Frecuencia cardiaca
significativamente más alta en fase lútea media y tardía frente a menstruación y
ovulación (p<0.03) — pero el abstract no da una cifra en bpm, solo el p-valor.

**Comparación:** dirección coincide (lútea más alta), pero no puedo comparar magnitud —
no encontré ningún estudio revisado por pares que reporte un delta exacto en bpm para
RHR por fase del ciclo. Sí encontré un dato de +2-3bpm citado por varias fuentes
secundarias, pero rastreado hasta su origen resultó ser un estudio piloto con 6
personas, presentado como póster en un congreso (ESHRE 2018) y nunca publicado en
revista revisada por pares — y ni siquiera esa fuente original da la cifra exacta que
las fuentes secundarias le atribuían. Prefiero dejar esta comparación en "coincide en
dirección, sin dato de magnitud fiable" a citar un número que no pude verificar en la
fuente primaria.

---

## 4. Sueño: la parte donde NO encontré diferencia — y tampoco la encontró nadie más

**Mi hallazgo:** duración del sueño (p = 0.28), % REM / % Deep (p > 0.7), eficiencia
(p = 0.21) — **ninguno cambia significativamente con la fase**. Solo los despertares en
los últimos 5 días antes del periodo suben (+1.1/noche, p = 0.034).

**Estudio:** [Tracking Sleep, Temperature, Heart Rate and Daily Symptoms Across the
Menstrual Cycle with the Oura Ring](https://pubmed.ncbi.nlm.nih.gov/35422659/) —
mismo tipo de wearable de consumo, y encuentran lo mismo: la continuidad y las fases de
sueño medidas objetivamente **no varían** con el ciclo, aunque temperatura y frecuencia
cardiaca sí muestran el patrón bifásico claro.

**Comparación:** esta es la corroboración que más me convence de todo el proyecto,
precisamente porque es un hallazgo *negativo* replicado de forma independiente. Es fácil
que un hallazgo positivo (p<0.05) sea casualidad con suficientes métricas probadas; que
dos estudios distintos, con datos distintos, encuentren el mismo "esto no cambia" es más
difícil de explicar por azar.

**Dónde puedo estar sesgada:** el hallazgo de despertares premenstruales tiene el p-valor
más débil de todos los significativos (0.034, frente a p<0.000001 del resto) — es el que
trataría con más cautela y el primero que esperaría que no replicase con más datos.

---

## 5. Predicción de fase con Random Forest

**Mi hallazgo original:** F1 = 0.79 clasificando lútea vs no-lútea (binario), usando
temperatura + HRV + frecuencia cardiaca como features, validado con `StratifiedKFold`
de 5 folds.

**El problema que encontré al revisarlo:** `StratifiedKFold` reparte *noches*
individuales entre train y test de forma aleatoria — pero mis noches no son
independientes entre sí. Muchas noches seguidas pertenecen al mismo ciclo, y ese ciclo
tiene una firma hormonal propia (temperatura basal, línea de base de HRV) que se repite
noche tras noche. Si noches del mismo ciclo caen a la vez en train y en test, el modelo
no está prediciendo un ciclo que nunca ha visto — está reconociendo un ciclo del que ya
vio parte. Eso infla la métrica. Se llama *fuga de datos* (data leakage) o
*pseudorreplicación*, y es un error fácil de cometer con datos longitudinales de una
sola persona.

**El fix:** cambié a `StratifiedGroupKFold`, agrupando por `cycle_id` (el ciclo real, no
el día), para que todas las noches de un mismo ciclo caigan siempre juntas en train o en
test — nunca repartidas. Con datos genuinamente no vistos:

| Validación | F1-macro (lútea vs no-lútea) |
|---|---|
| `StratifiedKFold` (con fuga) | 0.791 ± 0.054 |
| `StratifiedGroupKFold` (por ciclo) | **0.729 ± 0.058** |

Una caída real de 0.06 — no es un matiz, es la diferencia entre un modelo que parece muy
bueno y uno que es simplemente bueno. El número honesto del proyecto es **0.73**, no
0.79. Con las 4 fases (tarea más difícil) el F1-macro correcto baja a 0.373 — ahí la
fuga probablemente inflaba aún más el número original, aunque esa cifra de 4 clases
nunca se publicó, así que no había nada que corregir en el README para ese caso.

**Estudio:** [Machine learning-based menstrual phase identification using wearable
device data](https://www.nature.com/articles/s44294-025-00078-8) (npj Women's Health,
2025) — Random Forest con temperatura + actividad electrodérmica (EDA) + intervalo
entre latidos (IBI) + frecuencia cardiaca, clasificando 3 fases (periodo, ovulación,
lútea): 87% accuracy, AUC-ROC 0.96.

**Comparación:** con el número corregido (0.73) la distancia con el 87% del paper es
mayor de lo que parecía. Tampoco es directamente comparable — mi tarea es binaria y la
suya de 3 clases, con una feature más (EDA, que Apple Watch no expone) — pero ya no
puedo atribuir toda la diferencia a eso: parte era simplemente que mi 0.79 original no
era un número real.

**Dónde puedo estar sesgada:** mi input de HRV viene de Apple Watch — ver sección 6.
Si el instrumento que alimenta al modelo tiene ruido, ese ruido pone un techo a lo bien
que puede predecir el modelo, por bueno que sea el algoritmo. Y ahora sé, además, que mi
propio proceso de validación puede introducir sesgo si no tengo cuidado con cómo agrupo
los datos — este hallazgo es tan relevante como cualquiera de los de arriba.

---

## 6. ¿Cuánto puedo fiarme del instrumento? (Apple Watch)

Todo lo anterior asume que los datos crudos son fiables. Esto es lo que dicen los
estudios de validación independientes sobre el propio Apple Watch:

**Frecuencia cardiaca:** correlación buena en reposo, correlación excelente en
intensidad alta, moderada en intensidad media, comparado con ECG —
[Accuracy of Apple Watch to Measure Cardiovascular Indices](https://globalheartjournal.com/articles/10.5334/gh.1456).
Para mis datos (siempre en reposo/dormida) esto es tranquilizador.

**HRV — el punto más importante:** en reposo correlaciona bien con ECG (0.85–1.00), pero
el estudio de validación más reciente (Apple Watch Series 9 / Ultra 2) encontró que las
medidas de HRV **no cumplen los márgenes de equivalencia preespecificados** frente al
patrón de referencia clínico —
[The Validity of Apple Watch Series 9 and Ultra 2 for HRV](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11478500/).
Los propios autores concluyen que los algoritmos de HRV en wearables de consumo todavía
necesitan mejorar. Esto es una limitación real de mis datos de entrada, no solo de mi
análisis estadístico — cualquier ruido de medición en HRV se propaga a mis tests y a mi
modelo.

**Temperatura de muñeca:** Apple declara ±0.1°C de precisión para lecturas nocturnas.
Es el spec del propio fabricante — busqué explícitamente un estudio de validación
independiente y revisado por pares, específico del sensor de temperatura de Apple Watch
Series 8/Ultra, y no lo encontré. Prefiero decir esto tal cual (es un hueco real en la
literatura pública) a rellenarlo con una cifra inventada.

---

## Conclusión honesta

Las tres métricas fisiológicas más claras del proyecto (temperatura, HRV, RHR) apuntan
en la misma dirección que la literatura publicada, con el mismo mecanismo hormonal
detrás. El hallazgo negativo (el sueño en sí no cambia) también coincide con al menos
un estudio independiente usando el mismo tipo de wearable. El hallazgo más débil
(despertares premenstruales) es el que trataría con más escepticismo.

Donde soy más cautelosa es en la asignación de fase por calendario en vez de por
hormona confirmada, y en la fiabilidad del sensor de HRV de Apple Watch, que los propios
estudios de validación señalan como imperfecto. Ninguna de las dos cosas invalida la
dirección de los resultados — pero sí probablemente añade ruido que diluye el tamaño
real del efecto y pone un techo a cuánto puede mejorar el modelo predictivo.
