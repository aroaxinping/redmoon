# Related research

`redmoon` analyzes my own data to answer a personal question: does my nighttime
physiology change with the cycle? This is **not a study** — it's N=1, self-tracked,
with no control group and no hormone-confirmed phase. Before trusting my own
conclusions, I wanted to cross-check them against studies done with stricter,
more standardized methodology: do they agree? Where don't they? Why might they not?

This is that exercise, finding by finding.

---

## 1. Wrist temperature in luteal phase

**My finding:** +0.375°C in luteal vs follicular phase (p < 0.000001, Kruskal-Wallis,
1,153 nights / 76 cycles).

**Study 1 (mechanism):** Lin, G., Li, J. Y., Christofferson, K., Patel, S. N.,
Truong, K. N., & Mariakakis, A. (2024). [Understanding wrist skin temperature changes to
hormone variations across the menstrual cycle](https://pubmed.ncbi.nlm.nih.gov/39372385/).
*npj Women's Health*, 2(1), 35. 50 participants. Negative correlation between wrist
temperature and E3G/LH levels measured directly in urine — confirms the hormonal
mechanism, but the abstract doesn't report a °C figure comparable to mine.

**Study 2 (magnitude):** Shilaih, M., Goodale, B. M., Falco, L., Kübler, F., De Clerck,
V., & Leeners, B. (2018). [Modern fertility awareness methods: wrist wearables capture
the changes in temperature associated with the menstrual cycle](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6265623/).
*Bioscience Reports*, 38(6), BSR20171279. 136 participants, 437 cycles. Average
temperature in early luteal phase **0.33°C higher** than in the fertile window
(P<0.001).

**Comparison:** my +0.375°C is practically in line with the +0.33°C reported by
Shilaih et al., with a sample 136 times larger than mine in number of people (though
with fewer nights per person). It's the closest quantitative match in the whole
document — not just the same direction, the same order of magnitude.

**Where I might be biased:** both reference studies confirm phase with hormone
measured directly (urine or blood). I assign phase by cycle day, proportionally to
each cycle's actual length — without confirming ovulation with an LH test or
measuring real progesterone. My "luteal" nights near the boundaries (right after
ovulation, or right before the period) may be misclassified. That my number still
matches Shilaih et al.'s so closely suggests that classification noise isn't
distorting the result too much.

---

## 2. HRV in luteal phase

**My finding:** −3ms of HRV (SDNN) in luteal phase (p < 0.000001).

**Study:** Schmalenberger, K. M., Eisenlohr-Moul, T. A., Jarczok, M. N., et al. (2020).
[Menstrual Cycle Changes in Vagally-Mediated Heart Rate Variability Are Associated with
Progesterone](https://pmc.ncbi.nlm.nih.gov/articles/PMC7141121/). *Journal of Clinical
Medicine*, 9(3), 617. Two within-person cohorts: US (40 participants, 105 visits)
and Germany (50 participants, 112 visits). HF-HRV significantly lower in mid-luteal
phase than in mid-follicular (β=0.55, p<0.05) and ovulatory (β=0.60, p<0.05) phases.
Progesterone predicts lower HRV within each person (β=−0.036, p<0.001 in the US
cohort; β=−0.024, p<0.05 in the German one). Neither cohort found a significant
effect of estrogen.

**Comparison:** matches in direction and design (within-person, like mine —
comparing each person to themselves across the cycle, not averages across
different people). I can't compare magnitude directly: they use log-transformed
HF-HRV (arbitrary frequency-domain units), I use SDNN in milliseconds — different
HRV metrics, not the same scale. It would be wrong to say my −3ms "matches in
size" their β=0.55; I can only say the direction and mechanism (progesterone →
lower HRV) agree.

**Where I might be biased:** my "luteal phase" is one wide block (day 17 to the
end of the cycle), while the study distinguishes early/mid/late luteal by real
progesterone level. If I'm mixing sub-phases with very different progesterone
within the same "luteal" group, my average effect might be diluted — the true
mid-luteal effect could be larger than what I see.

---

## 3. Resting heart rate

**My finding:** +2bpm in luteal phase (p < 0.000001).

**Study:** Alzueta, E., de Zambotti, M., Javitz, H., et al. (2022). [Tracking sleep,
temperature, heart rate, and daily symptoms across the menstrual cycle with the Oura
Ring in healthy women](https://pubmed.ncbi.nlm.nih.gov/35422659/). *International
Journal of Women's Health*, 14, 491–503. 26 women. Heart rate significantly higher
in mid- and late-luteal phase versus menstruation and ovulation (p<0.03) — but the
abstract doesn't give a bpm figure, only the p-value.

**Comparison:** direction matches (luteal higher), but I can't compare magnitude —
I didn't find any peer-reviewed study reporting an exact bpm delta for RHR by
cycle phase. I did find a +2-3bpm figure cited by several secondary sources, but
traced back to its origin it turned out to be a pilot study with 6 people,
presented as a conference poster (ESHRE 2018) and never published in a
peer-reviewed journal — and even that original source doesn't give the exact
figure the secondary sources attributed to it. I'd rather leave this comparison
at "direction matches, no reliable magnitude data" than cite a number I couldn't
verify at the primary source.

---

## 4. Sleep: the part where I found NO difference — and neither did anyone else

**My finding:** sleep duration (p = 0.28), % REM / % Deep (p > 0.7), efficiency
(p = 0.21) — **none change significantly with phase**. Only awakenings in the
last 5 days before the period go up (+1.1/night, p = 0.034).

**Study:** [Tracking Sleep, Temperature, Heart Rate and Daily Symptoms Across the
Menstrual Cycle with the Oura Ring](https://pubmed.ncbi.nlm.nih.gov/35422659/) —
same type of consumer wearable, and they find the same thing: objectively measured
sleep continuity and stages **don't vary** with the cycle, even though temperature
and heart rate do show a clear biphasic pattern.

**Comparison:** this is the corroboration that convinces me most out of the whole
project, precisely because it's a *negative* finding replicated independently.
It's easy for a positive finding (p<0.05) to be chance when enough metrics are
tested; two different studies, with different data, finding the same "this
doesn't change" is harder to explain by chance.

**Where I might be biased:** the premenstrual awakenings finding has the weakest
p-value of all the significant ones (0.034, versus p<0.000001 for the rest) — it's
the one I'd treat with the most caution and the first I'd expect not to replicate
with more data.

---

## 5. Phase prediction with Random Forest

**My original finding:** F1 = 0.79 classifying luteal vs non-luteal (binary), using
temperature + HRV + heart rate as features, validated with 5-fold `StratifiedKFold`.

**The problem I found while reviewing it:** `StratifiedKFold` splits individual
*nights* between train and test at random — but my nights aren't independent of
each other. Many consecutive nights belong to the same cycle, and that cycle has
its own hormonal signature (baseline temperature, baseline HRV) that repeats night
after night. If nights from the same cycle land in both train and test at once,
the model isn't predicting a cycle it's never seen — it's recognizing a cycle it
already saw part of. That inflates the metric. It's called *data leakage* or
*pseudoreplication*, and it's an easy mistake to make with longitudinal data from
a single person.

**The fix:** I switched to `StratifiedGroupKFold`, grouping by `cycle_id` (the
real cycle, not the day), so all nights from the same cycle always land together
in train or in test — never split. With genuinely unseen data:

| Validation | F1-macro (luteal vs non-luteal) |
|---|---|
| `StratifiedKFold` (with leakage) | 0.791 ± 0.054 |
| `StratifiedGroupKFold` (by cycle) | **0.729 ± 0.058** |

A real drop of 0.06 — not a nuance, it's the difference between a model that
looks very good and one that's simply good. The honest number for this project
is **0.73**, not 0.79. With all 4 phases (a harder task), the corrected F1-macro
drops to 0.373 — leakage was probably inflating the original number there even
more, though that 4-class figure was never published, so there was nothing to
correct in the README for that case.

**Study:** [Machine learning-based menstrual phase identification using wearable
device data](https://www.nature.com/articles/s44294-025-00078-8) (npj Women's
Health, 2025) — Random Forest with temperature + electrodermal activity (EDA) +
inter-beat interval (IBI) + heart rate, classifying 3 phases (period, ovulation,
luteal): 87% accuracy, AUC-ROC 0.96.

**Comparison:** with the corrected number (0.73) the gap with the paper's 87% is
bigger than it looked. It's also not directly comparable — my task is binary and
theirs is 3-class, with one extra feature (EDA, which Apple Watch doesn't expose)
— but I can no longer attribute the whole gap to that: part of it was simply
that my original 0.79 wasn't a real number.

**Where I might be biased:** my HRV input comes from Apple Watch — see section 6.
If the instrument feeding the model has noise, that noise puts a ceiling on how
well the model can predict, no matter how good the algorithm is. And now I also
know that my own validation process can introduce bias if I'm not careful about
how I group the data — this finding is as relevant as any of the ones above.

---

## 6. How much can I trust the instrument? (Apple Watch)

Everything above assumes the raw data is reliable. Here's what independent
validation studies say about the Apple Watch itself:

**Heart rate:** good correlation at rest, excellent correlation at high
intensity, moderate at moderate intensity, compared to ECG —
[Accuracy of Apple Watch to Measure Cardiovascular Indices](https://globalheartjournal.com/articles/10.5334/gh.1456).
For my data (always at rest/asleep) this is reassuring.

**HRV — the most important point:** at rest it correlates well with ECG
(0.85–1.00), but the most recent validation study (Apple Watch Series 9 / Ultra
2) found that HRV measurements **do not meet the pre-specified equivalence
margins** against the clinical reference standard —
[The Validity of Apple Watch Series 9 and Ultra 2 for HRV](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11478500/).
The authors themselves conclude that HRV algorithms in consumer wearables still
need improvement. This is a real limitation of my input data, not just of my
statistical analysis — any measurement noise in HRV propagates to my tests and
my model.

**Wrist temperature:** Apple claims ±0.1°C accuracy for nightly readings. That's
the manufacturer's own spec — I explicitly looked for an independent,
peer-reviewed validation study specific to the Apple Watch Series 8/Ultra
temperature sensor, and didn't find one. I'd rather say this plainly (it's a
real gap in the public literature) than fill it in with a made-up number.

---

## Honest conclusion

The three clearest physiological metrics in this project (temperature, HRV, RHR)
point in the same direction as the published literature, with the same hormonal
mechanism behind them. The negative finding (sleep itself doesn't change) also
matches at least one independent study using the same type of wearable. The
weakest finding (premenstrual awakenings) is the one I'd treat with the most
skepticism.

Where I'm most cautious is in assigning phase by calendar instead of by
confirmed hormone, and in the reliability of the Apple Watch's HRV sensor, which
validation studies themselves flag as imperfect. Neither of these invalidates
the direction of the results — but they probably add noise that dilutes the real
effect size and puts a ceiling on how much the predictive model can improve.
