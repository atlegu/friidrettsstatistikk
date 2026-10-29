# Preregistration: Stagnation before exit? Within-athlete performance progression, relative age, and retention in youth track and field

*Written analysis plan (English), drafted 29 October 2026 from the Norwegian analysis plan (`ANALYSEPLAN.md`, version 1) and committed to version control (367f03f) before any exposure–outcome model was estimated. **Not registered on an external registry** — decision of 29 October 2026, documented in `FRIGITT_FOR_MODELLERING.txt`; this document stands as the timestamped plan of record, and the manuscript will state this.*

## 1. Study information

**Title.** Stagnation before exit? Within-athlete performance progression, relative age, and retention in youth track and field — a population register study.

**Author.** Atle G. Guttormsen (Norwegian University of Life Sciences).

**Background.** Three findings from the Norwegian Athletics Federation results registry motivate one untested question. A population-wide analysis of relative age effects (accepted, *Sports Medicine – Open*) proposed that individual mastery experience — visible personal progress — retains athletes in measurable individual sports, and stated the direct test: whether within-athlete performance *progression*, rather than performance level, predicts retention, among relatively younger athletes specifically. A longitudinal development study (*Journal of Science and Medicine in Sport*, 2026) showed that top-list turnover, not individual trajectories, drives apparent early plateaus, but did not study who exits. A 14-year dropout study (resubmitted, *International Journal of Sports Science & Coaching*) showed that competition volume declines before exit and that performance *level* adds little to volume, but did not measure performance *trajectories*. No population study has linked objective within-athlete progression to subsequent dropout.

**Hypotheses.**
- **H1.** Among athletes still competing at ages 15–16, within-athlete performance progression from ages 13–14 to 15–16 is positively associated with being an active senior (age 20+), beyond sex, performance level, competition volume (level and change), and the number of results the progression measure is computed from. Estimands: odds ratio per SD of progression; increment in cross-validated AUC when progression is added.
- **H2.** The association in H1 is stronger among relatively younger athletes (born later in the calendar year). Estimand: interaction progression × birth-quarter trend (Q1→Q4), expected positive; stratified ORs (Q1–Q2 vs. Q3–Q4) reported alongside.
- **H3 (framing).** Discrimination of (sex + volume + progression) is compared with (sex + volume + level), to assess whether progression rather than level carries the performance-related signal.

**Pre-stated interpretation rules.** A positive H1 and H2 is consistent with the mastery-experience account. A null or weak H1 does **not** falsify it: the registry cannot distinguish disengagement from transfer to another sport in which the athlete is also progressing; this asymmetry is declared in advance. If retention is fully explained by volume with no progression signal and no relative-age interaction, the mastery account loses its most direct observable support. No causal effect of progression is estimated.

## 2. Data and what has already been observed

**Data.** The Norwegian Athletics Federation's complete results registry (all sanctioned meets; electronically complete from 2011), frozen extract of 29 October 2026 (results dated ≤ 2026-10-29; live database state after the October 2026 deduplication). Athletes born 1998–2006; all their results from the calendar year they turned 13.

**Already observed before registration (declared).** (i) Registry coverage counts by age, year, seasons per athlete, and debut age (feasibility queries); (ii) the sample flow below; (iii) distributions of exposure components (progression, level, volume, counts, main event groups) by cohort and sex, *without* any outcome variable; (iv) the marginal number of active seniors in the primary sample (648), with no cross-tabulation against any exposure. **No exposure–outcome association of any kind has been computed.** The analysis scripts for H1–H3 exist but have not been run; a technical guard requires a registration marker file before they execute.

**Sample flow (frozen extract).** 32,447 athletes born 1998–2006 → 12,938 with ≥1 approved result at age 13–14 (calendar-year age) → 4,910 also competing at 15–16 (landmark condition) → 4,909 with known sex → excluding 734 without scorable age-graded points in their main event group in both windows and 3 in sex × event-group cells with <20 athletes → **primary sample 3,808** (born 1998–2005; born 2006 retained only for a secondary outcome), of whom **648 (17.0%)** meet the senior-activity outcome. 43 landmark athletes lack an exact birth date and are excluded from H2 only.

## 3. Variables

**Outcome (primary).** Active senior: ≥2 approved results in the same calendar year at age ≥20. **Secondary outcomes:** ≥1 result at age ≥20; ≥1 result at age ≥18 (allows cohort 2006); ≥2 results in a year at ages 20–21 (fixed window).

**Exposure (primary).** Progression Δ = mean of the 3 best age-graded (Tyrving 2014 table; validated implementation from the IJSSC revision) scores in the athlete's main event group at ages 15–16 minus the same at 13–14; standardized within sex × main event group over the primary sample. Main event group = modal event category of the athlete's results at 13–14 (ties broken alphabetically). Mean-of-3-best (not the maximum) is used because a maximum mechanically increases with the number of attempts; the number of scorable results per window (k13, k15) enters all models as covariates. Electronic timing only. **Exposure variants (sensitivity):** season-best (maximum); mean of all results; wind-legal marks only in wind-affected events; progression measured in the athlete's best event group at 15–16 (captures event-group switchers, who are excluded from the primary definition when they leave the 13–14 main group entirely); within-window progression age 13→14 as a specification check on mechanical overlap with volume/level.

**Covariates.** Sex; birth cohort; performance level (mean-of-3-best at 13–14, standardized within sex × group); competition volume = distinct competition dates at 13–14 and at 15–16 (standardized to the primary-sample SD); k13, k15; region (modal district of meets at 13–14); baseline club (modal club at 13–14), club size proxy (number of study athletes in the club) and club-clustered specifications; birth quarter (H2).

## 4. Analysis plan

Primary model: logistic regression on the primary sample. M0: sex + cohort (+ region + log club size). M1: M0 + level + volume 13–14 + volume 15–16 + k13 + k15. M2: M1 + Δ (**H1**: OR per SD, 95% CI; ΔAUC M2 vs. M1 from stratified 5-fold cross-validation repeated 20 times, percentile interval over repetitions; calibration slope and Brier score). **H2**: M2 + Δ × birth-quarter linear trend; stratified ORs. **H3**: paired comparison of cross-validated AUC between (sex + volumes + Δ + k) and (sex + volumes + level + k). Secondary: Cox model from the landmark (time from age 17 to last active season, censoring at the extract date for athletes active in 2025–2026); exit-aligned descriptive trajectories of standardized points at T−3…T0 seasons before the final season; club random-intercept/cluster-robust specifications; E-values for H1.

**Robustness (pre-specified).** Exposure variants above; exclusion of cohorts whose 15–16 window overlaps 2020–2021 (born 2004–2005) and a COVID-window interaction; k≥2 in both windows; the secondary outcome definitions; replication in cohorts A (born 1998–2001) and B (2002–2005).

**Inference.** Two-sided α = 0.05 for H1; H2 is directional and will be reported with its CI whatever the outcome; no correction across the pre-specified robustness set, which is interpreted as a pattern, not as independent tests.

**Power (approximate).** With n = 3,808 and 648 events, the primary model has >80% power for OR per SD ≈ 1.15; the H2 interaction is powered only for moderate effects and is treated as a directional test with replication across cohorts.

## 5. Ethics and transparency

Public competition results; no performance analysis below age 13 (Norwegian children's sport regulations); no individuals identified; dropout never characterized at the individual level. Same legal basis assessment as the companion IJSSC study (outside the scope of the Health Research Act; Sikt assessment obtained). Extraction and analysis code is version-controlled; athlete-level files are kept outside the repository and are regenerable from the registry. Deviations from this plan will be reported as such in the manuscript.
