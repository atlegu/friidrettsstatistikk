# Tables

(Submitted as editable text; in the final Word manuscript, each table on its own page after the references. Supplementary Tables S1–{+S32+} follow as supplementary material.)

---

## Table 1. Cohort characteristics by birth-year cohort

| Characteristic | Cohort A (1998–2000) | Cohort B (2001–2002) | All cohorts |
|---|---|---|---|
| N | 1,301 | 822 | 2,123 |
| Male (n) | 603 | 393 | 996 |
| Female (n) | 684 | 419 | 1,103 |
| Sex unknown (n) | 14 | 10 | 24 |
| Median career length (years) | 2.0 | 3.0 | 2.0 |
| {+Active at age 17 or later (%)+} | 41.0 | 41.6 | 41.3 |
| Ever active at age 20+ (%) | 15.8 | 17.3 | 16.4 |
| Still active in 2024 or later (%) | 5.8 | 10.8 | 7.7 |
| Mean Tyrving best at baseline | {+712+} | {+715+} | {+713+} |
| Median total meets, ages 13–14 (pre-milestone volume) | 16 | 19 | 17 |

*Note.* {+"Active at age 17 or later" indicates an active season (≥2 registered results in a calendar year) at age 17 or later+}; "Ever active at age 20+" is the outcome prevalence (≥2 results in any calendar year at age 20 or later). Tyrving points = the Norwegian Athletics Federation's age-norm score, where 1,000 corresponds to the published reference performance for that event × sex × age combination{+; all baseline events scored with implement- and hurdle-specific norms (Supplementary Methods S-M3)+}.

---
## Table 2. Competition volume trajectory by senior-retention status (median competitions per year and IQR)

| Group | N | Age 13 | Age 14 | Age 15 | Age 16 | Age 17 | Age 18 |
|---|---|---|---|---|---|---|---|
| Senior retainers (active age ≥20) | 348 | 13 [6–21] | 17 [10–25] | 19 [11–27] | 18 [10–26] | 17 [10–24] | 14 [7–20] |
| Dropouts (last active age <20) | 1,775 | 8 [4–13] | 8 [3–14] | 3 [0–11] | 0 [0–7] | 0 [0–2] | 0 [0–0] |

*Note.* Values are median number of meets per year [IQR]. Future retainers and future dropouts already differ at ages 13–14; the gap widens further across the age-14-to-15 transition.

---

## Table 3. Primary analysis: prospective logistic regression for active senior status (baseline-only predictors, ages 13–14)

| Model | Covariate | OR | 95% CI | p | CV-AUC [95% CI] | n |
|---|---|---|---|---|---|---|
| L1: Sex only | Female | {+0.76+} | {+[0.60, 0.95]+} | {+.019+} | {+0.535 [0.506, 0.564]+} | {+2,095+} |
| L2: + Performance | Female | {+0.69+} | {+[0.54, 0.87]+} | {+.002+} | {+0.641 [0.609, 0.673]+} | {+2,095+} |
|  | Tyrving (z) | {+1.61+} | {+[1.39, 1.87]+} | < .001 |  |  |
| {+L3: + Event concentration+} | Female | {+0.69+} | {+[0.54, 0.87]+} | {+.002+} | {+0.636 [0.602, 0.670]+} | {+2,095+} |
|  | Tyrving (z) | {+1.64+} | {+[1.42, 1.90]+} | < .001 |  |  |
|  | {+HHI, ages 13–14 (z)+} | {+1.12+} | {+[1.00, 1.26]+} | {+.054+} |  |  |
| L4: + Pre-milestone volume | Female | {+0.61+} | {+[0.47, 0.79]+} | < .001 | {+**0.746** [0.716, 0.776]+} | {+2,095+} |
|  | Tyrving (z) | {+1.23+} | {+[1.06, 1.42]+} | {+.006+} |  |  |
|  | {+HHI, ages 13–14 (z)+} | {+1.27+} | {+[1.12, 1.44]+} | < .001 |  |  |
|  | **Pre-milestone volume (z)** | **{+2.25+}** | **{+[1.99, 2.55]+}** | **< .001** |  |  |

*Note.* Logistic regression for binary active senior status (≥2 registered results in any year at age 20+). Predictors are observed during the baseline window (ages 13–14) only{+, including HHI (results at ages 13–14)+}. Pre-milestone volume is the sum of distinct meets attended at ages 13 and 14. Continuous covariates are z-standardized so ORs reflect per-SD effects. {+CV-AUC: mean of fold-level AUCs from stratified 5-fold cross-validation repeated 20 times, with standardization inside the training folds; 95% CI from the corrected resampled t (Supplementary Methods S-M4). Adding volume raised the AUC by 0.110 (95% CI 0.081–0.140; Supplementary Table S27). HHI is associated with retention once volume is entered (mutual adjustment) but does not improve discrimination (see also Discussion 4.6).+}

---
## Table 4. Level versus within-athlete change: volume at age 14 and change from 14 to 15

| Model | Covariate | OR per SD | 95% CI | p |
|---|---|---|---|---|
| M1: Volume at age 14 only | Female | {+0.60+} | {+[0.46, 0.77]+} | < .001 |
|  | Tyrving (z) | {+1.21+} | {+[1.04, 1.41]+} | {+.012+} |
|  | **Volume at age 14 (z)** | **{+2.20+}** | **{+[1.94, 2.50]+}** | **< .001** |
| M2: + Volume change 14→15 | Female | 0.60 | {+[0.45, 0.79]+} | < .001 |
|  | Tyrving (z) | {+1.12+} | {+[0.96, 1.30]+} | {+.140+} |
|  | **Volume at age 14 (z)** | **{+2.70+}** | **{+[2.33, 3.12]+}** | **< .001** |
|  | **Volume change 14→15 (z)** | **{+2.38+}** | **{+[2.08, 2.73]+}** | **< .001** |

*Note.* {+Change = volume at 15 minus volume at 14 (positive = increase; mean −2.3, SD 6.5 meets). The OR of 2.38 per SD increase is equivalent to OR = 0.42 [0.37, 0.48] per SD of greater decline (about 6.5 fewer meets), conditional on the level at age 14; per 5 fewer meets, OR = 0.51. Because the model is linear in the logit, it is identical to one with volume at 14 and volume at 15 as separate levels (the per-meet OR for change equals the per-meet OR for volume at 15). Pseudo-R² (McFadden) rose from 0.122 (M1) to 0.229 (M2); CV-AUC 0.735 → 0.823. 26 of the 1,914 athletes active at 14 lack registered sex or a Tyrving score (sample n = 1,888).+} Both baseline level and within-athlete {+decline+} contribute substantially and independently.

---
## Table 5. Time-varying hazard ratios (post-baseline Cox specification, period-specific)

| Covariate | Years 0–3 since baseline (approx. ages 13–17) | Years 3–6 (approx. ages 16–20) | Years 6+ (approx. ages 19+) |
|---|---|---|---|
| Volume at age 15–16 (per SD) | {+0.13 [0.11, 0.16]+} | {+0.70 [0.62, 0.80]+} | {+0.90 [0.74, 1.09]+} |
| Championship types (count) | {+0.78 [0.72, 0.85]+} | {+0.88 [0.77, 1.00]+} | {+0.78 [0.61, 0.99]+} |
| Tyrving (z) | {+0.99 [0.94, 1.05]+} | {+0.96 [0.88, 1.06]+} | {+1.15 [0.97, 1.36]+} |
| {+HHI, ages 13–14 (z)+} | {+1.02 [0.97, 1.08]+} | {+0.89 [0.81, 0.98]+} | {+1.01 [0.87, 1.17]+} |
| Female | {+1.04 [0.93, 1.16]+} | {+1.40 [1.16, 1.68]+} | {+1.06 [0.78, 1.44]+} |
| n at risk in interval | {+2,095+} | {+812+} | {+331+} |
| events in interval | {+1,283+} | {+481+} | {+170+} |
| C-index | {+0.897+} | {+0.657+} | {+0.581+} |

*Note.* Period-specific Cox estimates from the post-baseline specification with covariates measured at ages 15–16 and ≤17. The early-window HR for ages-15–16 volume partly reflects operational overlap between predictor and outcome (low milestone volume is mechanical for athletes who drop out before age 15); this estimate should be read as descriptive of the time-varying association rather than as an independent prospective effect. Substantively, the protective association attenuates across follow-up, consistent with a proximal disengagement-marker interpretation. {+All rows are generated directly from the analysis code (C-index per interval from the same models).+}

---
## Table 6. Prospective early-warning thresholds (pre-milestone volume, ages 13–14)

| Threshold (flag if vol <) | Flagged % | Sensitivity | Specificity | PPV | NPV | Senior retention, flagged | Senior retention, unflagged |
|---|---|---|---|---|---|---|---|
| 5 meets | 9.3 | 0.10 [0.09, 0.12] | 0.96 [0.94, 0.98] | **0.93** [0.89, 0.96] | 0.17 [0.16, 0.19] | 7.1% [3.6, 11.3] | 17.3% [15.7, 19.1] |
| 8 meets | 19.8 | 0.22 [0.20, 0.24] | 0.93 [0.90, 0.96] | **0.94** [0.92, 0.96] | 0.19 [0.17, 0.21] | 5.7% [3.6, 7.9] | 19.0% [17.2, 21.0] |
| 10 meets | 26.4 | 0.30 [0.28, 0.32] | 0.91 [0.88, 0.94] | **0.94** [0.92, 0.96] | 0.20 [0.18, 0.22] | 5.7% [3.9, 7.7] | 20.2% [18.3, 22.2] |
| 15 meets | 43.1 | 0.48 [0.46, 0.50] | 0.82 [0.77, 0.85] | **0.93** [0.91, 0.95] | 0.24 [0.21, 0.26] | 7.0% [5.4, 8.7] | 23.5% [21.1, 25.9] |

*Note.* Classification performance of pre-milestone (ages 13–14) competition volume as a prospective early-warning indicator, applicable at the end of an athlete's age-14 season, before the qualification window opens. All metrics are computed on one denominator (full cohort, n = 2,123); brackets are 2,000-replicate bootstrap 95% CIs. PPV is the proportion of flagged athletes who subsequently failed to retain senior activity. The final two columns give the absolute retention contrast: at the < 10 threshold, 5.7% among flagged vs. 20.2% among unflagged athletes (a 3.5-fold difference). The high PPV partly reflects the population's 84% non-retention base rate (the threshold improves precision by ~10 percentage points over base-rate prediction), and the NPV of ≈ 0.20 means unflagged athletes are not "safe": roughly four in five of them also fail to retain. {+The thresholds are candidate cut-offs chosen in the pooled data; derivation in one birth cohort and validation in the other are reported in Supplementary Table S29. Calibration of the underlying model is reported in Supplementary Table S23.+}

---

## Table 7. {+Internal cohort replication+} of the primary L4 logistic model

| Cohort | n | Covariate | OR | 95% CI | p |
|---|---|---|---|---|---|
| 1998–2000 | {+1,286+} | Female | {+0.64+} | {+[0.47, 0.89]+} | {+.008+} |
|  |  | Tyrving (z) | {+1.22+} | {+[1.01, 1.48]+} | {+.041+} |
|  |  | {+HHI, ages 13–14 (z)+} | {+1.16+} | {+[0.97, 1.37]+} | {+.096+} |
|  |  | **Pre-milestone volume (z)** | **2.22** | **{+[1.89, 2.60]+}** | **< .001** |
| 2001–2002 | {+809+} | Female | {+0.57+} | {+[0.38, 0.86]+} | {+.007+} |
|  |  | Tyrving (z) | {+1.23+} | {+[0.98, 1.54]+} | {+.075+} |
|  |  | {+HHI, ages 13–14 (z)+} | {+1.44+} | {+[1.19, 1.74]+} | < .001 |
|  |  | **Pre-milestone volume (z)** | **{+2.33+}** | **{+[1.90, 2.87]+}** | **< .001** |

*Note.* The primary baseline-only logistic model re-estimated separately within each birth-year cohort. {+Both cohorts come from the same register and national system, so this is an internal replication. The pre-milestone volume effect is reproduced at similar magnitude in both cohorts; female sex predicts lower retention in both. The HHI association is clear in the 2001–2002 cohort but not significant in the 1998–2000 cohort (see Section 3.9).+}

---

# Supplementary Tables

## Table S1. Proportional-hazards assumption test for the post-baseline Cox specification (Schoenfeld residuals)

| Covariate | χ²₁ | p |
|---|---|---|
| Female | {+3.15+} | {+.076+} |
| Tyrving (z) | {+0.34+} | {+.560+} |
| {+HHI, ages 13–14 (z)+} | {+13.64+} | < .001 |
| Volume at age 15–16 (z) | {+277.09+} | < .001 |
| Championship types | {+13.87+} | {+< .001+} |



---

## Table S2. Cluster-robust SE Cox (clustered on club)

| Covariate | HR | Robust 95% CI | p (robust) |
|---|---|---|---|
| Female | {+1.11+} | {+[0.98, 1.27]+} | {+.109+} |
| Tyrving (z) | {+1.01+} | {+[0.95, 1.08]+} | {+.686+} |
| {+HHI, ages 13–14 (z)+} | {+0.98+} | {+[0.92, 1.04]+} | {+.505+} |
| Volume at age 15–16 (z) | {+0.45+} | {+[0.40, 0.50]+} | < .001 |
| Championship types | {+0.73+} | {+[0.67, 0.80]+} | < .001 |

*Note.* Post-baseline specification; pooled HRs average over the strongly time-varying pattern shown in Table 5 and are descriptive.

---

## Table S3. E-values for the primary baseline-window volume effect (VanderWeele & Ding, 2017)

| Effect | Estimate | Approx. RR (common outcome) | E-value (point) | E-value (CI bound) |
|---|---|---|---|---|
| Pre-milestone volume, primary logistic (per SD) | {+OR 2.25 [1.99, 2.55]+} | {+1.50+} | {+2.37+} | {+2.17+} |
| Pre-milestone volume, baseline-only Cox (per SD) | {+HR 0.54+} | {+1.54+} | {+2.44+} | — |

*Note.* Because the outcome is common (16.4%), the odds ratio is converted to an approximate risk ratio (RR ≈ √OR) before computing E = RR + √(RR(RR − 1)); the hazard ratio uses the common-outcome conversion (Supplementary Methods S-M5). E-values are reported for the primary baseline-window specification only; the post-baseline (ages-15–16) specification is not an admissible E-value input because it overlaps the outcome window and violates proportional hazards.

---

## Table S4. Sample-size sensitivity: minimum detectable HR

| Cohort | N | Events | Min. detectable HR (80% power, α = .05) |
|---|---|---|---|
| Combined | {+2,095+} | {+1,934+} | 1.07 |
| 1998–2000 | {+1,286+} | {+1,212+} | {+1.08+} |
| 2001–2002 | {+809+} | {+722+} | {+1.11+} |



---

## Table S5. Complete-case vs mean-imputation sensitivity

| Covariate | HR (complete case) | HR (mean imputation) |
|---|---|---|
| Female | {+1.11+} | {+1.11+} |
| Tyrving (z) | {+1.01+} | {+1.01+} |
| {+HHI, ages 13–14 (z)+} | {+0.98+} | {+0.98+} |
| Volume at age 15–16 (z) | {+0.45+} | 0.45 |
| Championship types | {+0.73+} | 0.73 |
| n | {+2,095+} | 2,123 |

*Note.* Post-baseline Cox specification (descriptive; see Table 5 note). The principal missing-data sensitivity for the primary logistic model is multiple imputation, Supplementary Table S21.

---

## Table S6. Cox model stratified on HHI tercile (sensitivity to PH violation)

| Covariate | HR | p |
|---|---|---|
| Female | {+1.11+} | {+.025+} |
| Tyrving (z) | {+1.01+} | {+.723+} |
| Volume at age 15–16 (z) | 0.44 | < .001 |
| Championship types | {+0.74+} | < .001 |



---

## Table S7. Sex-stratified Cox subgroup analyses

| Sex | n | Covariate | HR | 95% CI | p |
|---|---|---|---|---|---|
| Male | {+993+} | Tyrving (z) | {+1.06+} | {+[0.99, 1.12]+} | {+.090+} |
|  |  | {+HHI, ages 13–14 (z)+} | {+0.98+} | {+[0.92, 1.05]+} | {+.612+} |
|  |  | Volume at age 15–16 (z) | {+0.44+} | {+[0.39, 0.50]+} | < .001 |
|  |  | Championship types | {+0.64+} | {+[0.58, 0.71]+} | < .001 |
| Female | {+1,102+} | Tyrving (z) | {+0.95+} | {+[0.89, 1.02]+} | {+.137+} |
|  |  | {+HHI, ages 13–14 (z)+} | {+0.97+} | {+[0.91, 1.04]+} | {+.362+} |
|  |  | Volume at age 15–16 (z) | 0.45 | {+[0.41, 0.51]+} | < .001 |
|  |  | Championship types | 0.81 | {+[0.74, 0.89]+} | < .001 |

*Note.* Post-baseline specification (descriptive; see Table 5 note). {+C-index = 0.847 (male) and 0.846 (female).+} The dominant behavioral covariate is near-identical across sexes (volume HR {+0.44 vs 0.45+}).

---

## Table S8. Landmark analysis at age 16 (post-baseline Cox, n = 1,167)

| Covariate | HR | 95% CI | p |
|---|---|---|---|
| Female | {+1.29+} | {+[1.13, 1.46]+} | < .001 |
| Tyrving (z) | {+1.00+} | {+[0.94, 1.07]+} | {+.896+} |
| {+HHI, ages 13–14 (z)+} | {+0.94+} | {+[0.88, 1.00]+} | {+.070+} |
| **Volume at age 15–16 (z)** | 0.60 | {+[0.55, 0.66]+} | < .001 |
| Championship types | 0.78 | {+[0.71, 0.86]+} | < .001 |
| n complete | {+1,153+} |  |  |
| C-index | 0.735 |  |  |

*Note.* Athletes with ≥1 registered result at age 16, with follow-up time measured from age 16 forward; the age-16 share of the exposure window therefore lies at the start of the at-risk window (see Supplementary Methods S-M1). The fully contamination-free logistic analogue is the change model in main-text Section 3.5 / Supplementary Table S19.

---

## Table S9. Outcome-definition sensitivity (primary L4 specification, baseline-only predictors)

| Outcome | Description | Retainer n (%) | OR (pre-milestone vol per SD) | 95% CI | CV-AUC |
|---|---|---|---|---|---|
| A | ≥1 senior-age (20+) result | 411 (19.4%) | {+2.16+} | {+[1.92, 2.44]+} | {+0.727+} |
| B | ≥2 results in any senior-age year (primary) | 348 (16.4%) | {+2.25+} | {+[1.99, 2.55]+} | {+0.747+} |
| C | ≥2 results in each of two distinct senior-age years | 254 (12.0%) | {+2.08+} | {+[1.82, 2.37]+} | {+0.740+} |

*Note.* All three rows re-estimate the primary L4 model (sex, Tyrving, HHI, pre-milestone volume; {+n = 2,095+}) with the alternative outcome definitions. The volume effect is stable across definitions.

---

## Table S10. Lagged volume: pre-milestone (ages 13–14) alone (Cox)

| Covariate | HR | 95% CI | p |
|---|---|---|---|
| Female | 1.15 | {+[1.05, 1.26]+} | {+.002+} |
| Tyrving (z) | {+0.97+} | {+[0.93, 1.01]+} | {+.165+} |
| {+HHI, ages 13–14 (z)+} | {+0.89+} | {+[0.85, 0.94]+} | < .001 |
| **{+Pre-milestone volume (z)+}** | {+0.54+} | {+[0.51, 0.57]+} | < .001 |

*Note.* {+n = 2,095; C-index = 0.743+}.

---

## Table S11. Sensitivity excluding zero-volume athletes (post-baseline Cox)

| Covariate | HR | 95% CI | p |
|---|---|---|---|
| Female | 1.20 | {+[1.08, 1.34]+} | {+< .001+} |
| Tyrving (z) | {+0.99+} | {+[0.94, 1.05]+} | {+.782+} |
| {+HHI, ages 13–14 (z)+} | {+0.95+} | {+[0.90, 1.01]+} | {+.097+} |
| **Volume at age 15–16 (z)** | {+0.52+} | {+[0.47, 0.56]+} | < .001 |
| Championship types | {+0.79+} | {+[0.73, 0.85]+} | < .001 |

*Note.* {+Excludes 581 athletes with vol_milestone = 0; remaining n = 1,514; C-index = 0.789+}.

---

## Table S12. Analysis sample flow

| Analysis | n | Definition |
|---|---|---|
| Total cohort | 2,123 | All included athletes |
| Sex known | 2,099 | Gender M/F registered (24 unknown; excluded from regression models, included in cohort totals and unstratified KM curves) |
| Primary logistic L1–L4 | {+2,095+} | Complete case on sex, Tyrving, HHI, pre-milestone volume; L1–L3 fitted on the same fixed sample for AUC comparability |
| Level-vs-change (Table 4) | {+1,888+} | {+Of 1,914 athletes with ≥1 result at age 14; complete case on sex and Tyrving+} |
| Contamination-free change model | 1,075 | Of 1,085 athletes with ≥2 results at age 16; complete case on sex |
| Landmark Cox at age 16 | {+1,153+} | Of 1,167 athletes with ≥1 result at age 16; complete case on model covariates |
| {+Performance-trajectory comparison (Table S15)+} | {+1,692+} | {+Complete case on Tyrving at both age 13 and age 14+} |
| {+Nested predictor subsets (Table S17)+} | {+1,473+} | {+Complete case on all 22 candidate predictors+} |
| {+Multiple imputation+} | {+2,099+} | {+All athletes with known sex; Tyrving imputed (m = 20)+} |
| {+Within-athlete fixed-effects model (Table S28)+} | {+1,897+} | {+Athletes with ≥2 athlete-seasons at ages 13–19 up to and including the final active season (8,447 athlete-seasons)+} |
| {+Specialization confound models (S18 B/C)+} | {+2,094 / 2,097+} | {+Complete case on primary-category Tyrving+} |

*Note.* One map of every analysis sample in the manuscript; each n is derivable from the row's definition.

---

## Table S13. Primary logistic regression with structural controls (Panel A) and birth-quarter coding (Panel B)

| Covariate | OR | 95% CI | p |
|---|---|---|---|
| Female | 0.60 | {+[0.46, 0.77]+} | < .001 |
| Tyrving (z) | {+1.24+} | {+[1.07, 1.44]+} | {+.004+} |
| {+HHI, ages 13–14 (z)+} | {+1.27+} | {+[1.12, 1.44]+} | < .001 |
| **Pre-milestone volume (z)** | {+2.26+} | {+[1.99, 2.57]+} | < .001 |
| Q1 born | {+0.82+} | {+[0.62, 1.09]+} | {+.178+} |
| Q4 born | {+1.10+} | {+[0.77, 1.57]+} | {+.601+} |
| Region: Østlandet | {+1.17+} | {+[0.87, 1.58]+} | {+.292+} |
| Region: Midt-Norge | {+1.08+} | {+[0.76, 1.54]+} | {+.663+} |
| Club size (z) | {+1.02+} | {+[0.90, 1.16]+} | {+.717+} |

*Note.* {+n = 2,095. Panel A (as submitted): Q1 and Q4 indicators against Q2–Q3, the relative-age extremes; the 84 athletes registered with birth year but no birth date (none of whom retained) fall in the reference group. Pre-milestone volume effect unchanged: OR 2.26 with controls vs. 2.25 without. All structural controls non-significant.+}

**{+Panel B. Birth-quarter specifications (all models include sex, Tyrving, HHI, volume, region and club size)+}**

| Specification | Covariate | OR | 95% CI | p | LR test of quarter terms | n |
|---|---|---|---|---|---|---|
| {+As submitted: Q1 and Q4 indicators vs. Q2–Q3 (unknown quarter coded to the reference)+} | {+Q1 (Jan–Mar)+} | {+0.82+} | {+[0.62, 1.09]+} | {+.178+} | {+χ²(2) = 2.71, p = 0.26+} | {+2,095+} |
|  | {+Q4 (Oct–Dec)+} | {+1.10+} | {+[0.77, 1.57]+} | {+.601+} |  |  |
|  | {+Pre-milestone volume (z)+} | {+2.26+} | {+[1.99, 2.57]+} | {+< .001+} |  |  |
| {+Q1 and Q4 indicators vs. Q2–Q3, known quarter only+} | {+Q1 (Jan–Mar)+} | {+0.79+} | {+[0.59, 1.05]+} | {+.104+} | {+χ²(2) = 3.23, p = 0.20+} | {+2,011+} |
|  | {+Q4 (Oct–Dec)+} | {+1.05+} | {+[0.73, 1.49]+} | {+.806+} |  |  |
|  | {+Pre-milestone volume (z)+} | {+2.21+} | {+[1.94, 2.51]+} | {+< .001+} |  |  |
| {+Full coding: Q2, Q3, Q4 vs. Q1, known quarter only+} | {+Q2 (Apr–Jun)+} | {+1.28+} | {+[0.92, 1.77]+} | {+.141+} | {+χ²(3) = 3.24, p = 0.36+} | {+2,011+} |
|  | {+Q3 (Jul–Sep)+} | {+1.26+} | {+[0.89, 1.77]+} | {+.191+} |  |  |
|  | {+Q4 (Oct–Dec)+} | {+1.33+} | {+[0.90, 1.96]+} | {+.156+} |  |  |
|  | {+Pre-milestone volume (z)+} | {+2.21+} | {+[1.94, 2.51]+} | {+< .001+} |  |  |
| {+Linear trend across quarters 1–4, known quarter only+} | {+Quarter (linear, 1–4)+} | {+1.09+} | {+[0.97, 1.23]+} | {+.134+} | {+χ²(1) = 2.24, p = 0.13+} | {+2,011+} |
|  | {+Pre-milestone volume (z)+} | {+2.20+} | {+[1.94, 2.50]+} | {+< .001+} |  |  |

{+Birth quarter is unrelated to retention under every coding; the volume coefficient is unchanged.+}

---

## Table S14. Level-versus-change analysis details (athletes with ≥1 result at age 14; complete-case n = 1,888)

| Model | Covariate | OR | 95% CI | p | Pseudo-*R*² | CV-AUC |
|---|---|---|---|---|---|---|
| M1: Volume at age 14 only | Female | {+0.60+} | {+[0.46, 0.77]+} | < .001 | {+0.122+} | {+0.735+} |
|  | Tyrving (z) | {+1.21+} | {+[1.04, 1.41]+} | {+.012+} |  |  |
|  | Volume at age 14 (z) | {+2.20+} | {+[1.94, 2.50]+} | < .001 |  |  |
| M2: + Volume change 14→15 | Female | 0.60 | {+[0.45, 0.79]+} | < .001 | {+0.229+} | {+0.823+} |
|  | Tyrving (z) | {+1.12+} | {+[0.96, 1.30]+} | {+.140+} |  |  |
|  | Volume at age 14 (z) | {+2.70+} | {+[2.33, 3.12]+} | < .001 |  |  |
|  | Volume change 14→15 (z) | {+2.38+} | {+[2.08, 2.73]+} | < .001 |  |  |

*Note.* Full coefficient detail for main-text Table 4{+, with repeated cross-validated AUC. Change = volume at 15 minus volume at 14.+}

---

## Table S15. Time-aligned behavior versus performance (repeated 5-fold CV-AUC)

| Predictor set (all ages 13–14 measurements) | n | CV-AUC |
|---|---|---|
| Sex + baseline Tyrving | {+2,095+} | {+0.641+} |
| Sex + Tyrving + performance trajectory (Δ13–14) | {+1,692+} | {+0.701+} |
| Sex + pre-milestone volume | {+2,095+} | {+0.739+} |
| {+Sex + pre-milestone volume (trajectory subsample)+} | {+1,692+} | {+0.734+} |
| {+Sex + Tyrving + pre-milestone volume+} | {+2,095+} | {+0.737+} |

*Note.* {+Both predictors are observed during the baseline window (ages 13–14). Volume discriminates better than baseline performance (difference 0.098 [0.063, 0.133]); adding Tyrving to volume does not change discrimination; the within-baseline performance trajectory narrows the gap (difference 0.033 [−0.003, 0.069] in the subsample with Tyrving at both ages). Differences with corrected 95% CIs: Supplementary Table S27.+}

---

## Table S16. Cox time-to-cessation with structural controls (baseline-only predictors)

| Covariate | HR | 95% CI | p |
|---|---|---|---|
| Female | 1.16 | {+[1.06, 1.27]+} | {+.001+} |
| Tyrving (z) | {+0.96+} | {+[0.92, 1.01]+} | {+.119+} |
| {+HHI, ages 13–14 (z)+} | {+0.89+} | {+[0.85, 0.94]+} | < .001 |
| **Pre-milestone volume (z)** | {+0.54+} | {+[0.50, 0.57]+} | < .001 |
| Q1 born | {+1.00+} | {+[0.91, 1.11]+} | {+.982+} |
| Q4 born | {+0.87+} | {+[0.76, 0.99]+} | {+.032+} |
| Region: Østlandet | {+0.95+} | {+[0.85, 1.06]+} | {+.335+} |
| Region: Midt-Norge | {+1.01+} | {+[0.90, 1.14]+} | {+.862+} |
| Club size (z) | {+1.00+} | {+[0.96, 1.05]+} | {+.895+} |

*Note.* {+n = 2,095; C-index = 0.743+}. Higher HHI (specialization) associated with lower dropout hazard.

---

## Table S17. Cross-validated AUC for nested predictor subsets predicting senior retention

| Predictor set | n features | n | AUC (logistic) |
|---|---|---|---|
| Baseline only (sex + Tyrving best) | 2 | {+1,473+} | {+0.61 (±0.05)+} |
| Specialization only (sex + HHI + n categories) | 3 | {+1,473+} | {+0.59 (±0.01)+} |
| Volume only (sex + meets ages 13–16) | 5 | {+1,473+} | {+0.82 (±0.02)+} |
| Volume + specialization (pre-baseline behavioral) | 8 | {+1,473+} | 0.82 (±0.03) |
| Full model (all 22 predictors) | 22 | {+1,473+} | {+0.82 (±0.03)+} |

*Note.* Descriptive comparison on the subsample with complete data on all 22 candidate predictors ({+n = 1,473+}; see Supplementary Table S12). This table includes post-baseline behavioral predictors (ages 15–16) and therefore overlaps with the early portion of the at-risk window; AUCs are descriptive rather than ordinary prospective prediction quantities.

---

## Table S18. Specialization-vs-performance confound check: does HHI proxy for performance in the primary event category?

| Model | Covariate | OR | 95% CI | p |
|---|---|---|---|---|
| **A**: Primary L4 (with tyrving_best) | Female | 0.61 | {+[0.47, 0.79]+} | < .001 |
| {+n = 2,095+} | {+Tyrving (z)+} | {+1.23+} | {+[1.06, 1.42]+} | {+.006+} |
|  | **{+HHI, ages 13–14 (z)+}** | **{+1.27+}** | **{+[1.12, 1.44]+}** | **< .001** |
|  | Pre-milestone volume (z) | {+2.25+} | {+[1.99, 2.55]+} | < .001 |
| **B**: + Tyrving in primary category | Female | {+0.61+} | {+[0.47, 0.78]+} | {+< .001+} |
| {+n = 2,094+} | {+Tyrving (z)+} | 1.08 | {+[0.90, 1.31]+} | {+.398+} |
|  | **{+HHI, ages 13–14 (z)+}** | **{+1.23+}** | **{+[1.08, 1.41]+}** | **{+.002+}** |
|  | Pre-milestone volume (z) | {+2.16+} | {+[1.90, 2.46]+} | < .001 |
|  | Tyrving main category (z) | {+1.23+} | {+[1.00, 1.50]+} | {+.047+} |
| **C**: Tyrving main replaces tyrving_best | Female | {+0.61+} | {+[0.47, 0.78]+} | {+< .001+} |
| {+n = 2,097+} | Tyrving main category (z) | {+1.30+} | {+[1.11, 1.52]+} | {+.001+} |
|  | **{+HHI, ages 13–14 (z)+}** | **{+1.22+}** | **{+[1.07, 1.38]+}** | **{+.002+}** |
|  | Pre-milestone volume (z) | {+2.16+} | {+[1.89, 2.46]+} | < .001 |

*Note.* {+Correlations: HHI vs. Tyrving best, r = -0.20; HHI vs. Tyrving main category, r = −0.06; Tyrving best vs. Tyrving main, r = 0.71. HHI is essentially uncorrelated with main-category performance and only weakly (negatively) with best performance across events. The HHI coefficient is stable across the three specifications (OR 1.22–1.27); main-category Tyrving has a modest independent association (OR 1.23–1.30).+}

---

## Table S19. Exit-aligned volume trajectories among dropouts

| Quantity | Value | n |
|---|---|---|
| Aligned volume T−3 (median [IQR]) | 12 [6–18] | 795 |
| Aligned volume T−2 (median [IQR]) | 10 [6–16] | 1,139 |
| Aligned volume T−1 (median [IQR]) | 9 [5–14] | 1,139 |
| Aligned volume T (final season; median [IQR]) | 4 [2–8] | 1,139 |
| Active (>0 meets) in penultimate season | 95.2% | 1,139 |
| Reduced-but-nonzero penultimate season (final age ≥16) | 74.2% | 795 |
| Penultimate season zero (gap year before final) | 6.5% | 795 |
| Penultimate at personal peak (abrupt profile) | 19.2% | 795 |
| Volume in final season below personal peak | 93.5% | 1,139 |
| Change model among active at 16: volume at 15 (per SD) | {+OR 3.04 [2.55, 3.63]+} | 1,075 |
| {+Change model among active at 16: change 15→16 (per SD increase)+} | OR 1.88 [1.60, 2.20] | 1,075 |
| {+Change model among active at 16: change 15→16 (per SD decline)+} | {+OR 0.53 [0.45, 0.62]+} | {+1,075+} |

*Note.* Each dropout's volume history aligned to their own final active season (T; last calendar year with ≥2 results); dropouts with final seasons at ages 15–19 (n = 1,139; T−3 observable only where final age ≥16). "Reduced-but-nonzero" = penultimate volume above zero but below the athlete's earlier personal peak. The change model is a logistic regression for senior status among athletes with ≥2 results at age 16 (CV-AUC = {+0.761; change = volume at 16 minus volume at 15+}); all predictors are measured by 16, so neither predictor can be the exit itself. See Supplementary Methods S-M6.

---

## Table S20. HHI count-dependence stress tests

| Model | n | HHI OR [95% CI] | Volume OR |
|---|---|---|---|
| Primary L4 (all) | {+2,095+} | {+1.27 [1.12, 1.44]+} | {+2.25+} |
| {+≥ 5 results at ages 13-14+} | {+2,019+} | {+1.26 [1.11, 1.43]+} | {+2.23+} |
| {+≥ 8 results at ages 13-14+} | {+1,873+} | {+1.24 [1.10, 1.40]+} | {+2.19+} |
| {+Finite-sample-corrected HHI* = (HHI - 1/n)/(1 - 1/n)+} | {+2,085+} | {+1.29 [1.14, 1.46]+} | {+2.21+} |

*Note.* {+HHI computed from results at ages 13–14. Spearman correlations: HHI vs. result count at ages 13–14 ρ = -0.40; HHI vs. pre-milestone volume ρ = -0.23.+} The HHI–retention association is unchanged under count restrictions and the corrected index; it is not a small-count artifact. See Supplementary Methods S-M8.

---

## Table S21. {+Missing data: complete-case and multiple-imputation estimates and predictive performance+}

| Data / model | n | Volume OR [95% CI] | HHI OR [95% CI] | Tyrving OR [95% CI] | CV-AUC |
|---|---|---|---|---|---|
| Revised scoring: complete case (primary) | 2,095 | 2.25 [1.99, 2.55] | 1.27 [1.12, 1.44] | 1.23 [1.06, 1.42] | 0.746 |
| Revised scoring: multiple imputation (m = 20) | 2,099 | 2.25 [1.99, 2.55] | 1.27 [1.12, 1.44] | 1.23 [1.06, 1.42] |  |
| Original (incomplete) scoring: complete case | 1,704 | 2.33 [2.02, 2.68] | 1.24 [1.07, 1.44] | 1.14 [0.98, 1.33] | 0.746 |
| Original (incomplete) scoring: MI (m = 20), outcome in imputation model | 2,099 | 2.31 [2.04, 2.61] | 1.25 [1.10, 1.41] | 1.13 [0.98, 1.31] | 0.746 (0.740-0.749) |
| Original (incomplete) scoring: MI with auxiliary variables (baseline event category, region, cohort, club size, result count) | 2,099 | 2.30 [2.03, 2.60] | 1.25 [1.10, 1.41] | 1.16 [1.01, 1.34] |  |

*Note.* {+With the revised Tyrving scoring only 4 sex-known athletes lack a baseline score, so imputation and complete-case analysis coincide. The lower rows repeat the analysis with the original, incomplete scoring (Tyrving missing for 395 sex-known athletes, 18.8%): chained-equation imputation (m = 20) with the outcome in the imputation model leaves all estimates unchanged, and predictive performance with imputation fitted inside each training fold (outcome excluded) equals the complete-case CV-AUC. Details: Supplementary Methods S-M3.+}

---

## Table S22. Club-level analyses

| Quantity | Value | n |
|---|---|---|
| ICC of pre-milestone volume across baseline clubs | {+0.24+} | {+2,095 athletes, 287 clubs+} |
| Volume OR, primary (no club terms) | {+2.25+} | {+2,095+} |
| Volume OR, club random intercepts | {+2.43 [2.17, 2.72]+} | {+2,095+} |
| HHI OR, club random intercepts | {+1.25+} | {+2,095+} |
| {+CV-AUC, folds grouped by club (20 repeats)+} | {+0.746 [0.709, 0.783]+} | {+2,095+} |

*Note.* A quarter of the variance in pre-milestone volume lies between clubs, but the within-club volume effect is, if anything, slightly larger than the pooled estimate{+, and discrimination is unchanged when validation clubs are held out of fitting+}: the association is not a club-supply artifact. See Supplementary Methods S-M7.

---

## Table S23. Calibration of the primary model (cross-validated)

| Metric | Value |
|---|---|
| Calibration slope | {+0.98+} |
| {+Calibration-in-the-large+} | {+0.00+} |
| Brier score | {+0.120+} |
| n | {+2,095+} |

*Note.* {+Out-of-fold predictions averaged over 20 repeats of stratified 5-fold cross-validation; calibration-in-the-large is the intercept of a logistic model with the linear predictor as offset.+}

---

## Table S24. Fixed-window outcome (ages 20–22)

| Outcome | Prevalence | Cohort A | Cohort B | Volume OR [95% CI] | CV-AUC | n |
|---|---|---|---|---|---|---|
| ≥2 results in any season at ages 20–22 | 0.158 | 0.153 | 0.167 | {+2.28 [2.01, 2.59]+} | {+0.753+} | {+2,095+} |

*Note.* This outcome window is fully observable for every athlete in both cohorts, removing the follow-up asymmetry of the open-ended senior definition; results are near-identical to the primary model.

---

## Table S25. Included versus excluded athletes (complete-case comparison)

| Variable | Included (complete case) | Excluded (any missing) |
|---|---|---|
| Senior retention | {+16.4%+} | {+14.3%+} |
| Female | {+52.6%+} | {+— (24 of 28 have no registered sex)+} |
| Pre-milestone volume (mean meets) | {+20.9+} | {+18.6+} |
| {+HHI, ages 13–14 (mean)+} | {+0.46+} | {+0.42+} |

*Note.* {+n = 2,095 included, 28 excluded (24 without registered sex, 4 without a baseline Tyrving score). The excluded athletes are too few to affect the estimates; multiple imputation gives identical results (Supplementary Table S21).+}

---

## Table S26. {+Cross-validation procedure: standardization inside folds and club-grouped folds+}

| Procedure | n | CV-AUC | Calibration slope | Calibration-in-the-large | Brier |
|---|---|---|---|---|---|
| Submitted variables; standardized on full data before CV (as submitted) | 1,704 | 0.751 | 0.96 | 0.00 | 0.122 |
| Submitted variables; standardized within training folds | 1,704 | 0.751 | 0.96 | 0.00 | 0.122 |
| Revised variables; athlete-level stratified 5-fold, 20 repeats | 2,095 | 0.746 [0.716, 0.776]; repeat range 0.742–0.749 | 0.98 | 0.00 | 0.120 |
| Revised variables; club-grouped stratified 5-fold, 20 repeats | 2,095 | 0.746 [0.709, 0.783]; repeat range 0.743–0.750 | 0.96 | 0.00 | 0.120 |

*Note.* Rows 1–2 use the variables and the single 5-fold split (seed 42) of the original submission. Because the logistic models are unpenalized, standardizing inside the training folds is an affine re-parameterization that leaves out-of-fold predictions unchanged; the two procedures therefore agree to the third decimal. Rows 3–4 use the revised variables (HHI from ages 13–14; complete Tyrving scoring) with 20 repeats; club-grouped folds keep every baseline club (287 clubs; largest 60 athletes) entirely in either the training or the validation fold.

---

## Table S27. {+Differences in cross-validated AUC between models (paired, identical folds)+}

| Comparison (B vs. A) | n | CV-AUC A | CV-AUC B | Difference | 95% CI | p |
|---|---|---|---|---|---|---|
| Sex + Tyrving vs. sex | 2,095 | 0.535 | 0.641 | +0.106 | [+0.072, +0.140] | < .001 |
| + HHI vs. sex + Tyrving | 2,095 | 0.641 | 0.636 | −0.005 | [−0.017, +0.008] | .471 |
| + volume vs. sex + Tyrving + HHI (L4 vs. L3) | 2,095 | 0.636 | 0.746 | +0.110 | [+0.081, +0.140] | < .001 |
| Sex + volume vs. sex + Tyrving (time-aligned) | 2,095 | 0.641 | 0.739 | +0.098 | [+0.063, +0.133] | < .001 |
| Sex + Tyrving + volume vs. sex + volume | 2,095 | 0.739 | 0.737 | −0.002 | [−0.011, +0.007] | .636 |
| Full L4 vs. sex + volume | 2,095 | 0.739 | 0.746 | +0.008 | [−0.006, +0.022] | .281 |
| Sex + volume vs. sex + Tyrving + Tyrving change 13–14 | 1,692 | 0.701 | 0.734 | +0.033 | [−0.003, +0.069] | .070 |

*Note.* Both models are fitted and validated on the same 100 folds (stratified 5-fold, 20 repeats); the difference is the mean of the 100 fold-level differences, with 95% CI and p from the corrected resampled t-statistic (Nadeau & Bengio, 2003), which inflates the variance for the overlap between training sets.

---

## Table S28. {+Within-athlete decline before exit: athlete and age fixed-effects model+}

| Outcome / sample | Season | Estimate | 95% CI | Effect | p | Athletes | Athlete-seasons |
|---|---|---|---|---|---|---|---|
| log(1 + meets), all athletes | T−3 | −0.069 | [−0.137, −0.002] | −7% | .045 | 1,897 | 8,447 |
| log(1 + meets), all athletes | T−2 | −0.131 | [−0.213, −0.049] | −12% | .002 | 1,897 | 8,447 |
| log(1 + meets), all athletes | T−1 | −0.271 | [−0.370, −0.173] | −24% | < .001 | 1,897 | 8,447 |
| log(1 + meets), all athletes | T | −0.646 | [−0.756, −0.535] | −48% | < .001 | 1,897 | 8,447 |
| meets (linear), all athletes | T−3 | −0.396 | [−1.065, 0.274] | −0.4 meets | .247 | 1,897 | 8,447 |
| meets (linear), all athletes | T−2 | −1.087 | [−1.940, −0.233] | −1.1 meets | .013 | 1,897 | 8,447 |
| meets (linear), all athletes | T−1 | −2.700 | [−3.747, −1.654] | −2.7 meets | < .001 | 1,897 | 8,447 |
| meets (linear), all athletes | T | −6.440 | [−7.662, −5.217] | −6.4 meets | < .001 | 1,897 | 8,447 |
| log(1 + meets), exits at ages 17–19 only (reference seasons observed) | T−3 | −0.039 | [−0.114, 0.037] | −4% | .314 | 692 | 4,239 |
| log(1 + meets), exits at ages 17–19 only (reference seasons observed) | T−2 | −0.093 | [−0.194, 0.007] | −9% | .070 | 692 | 4,239 |
| log(1 + meets), exits at ages 17–19 only (reference seasons observed) | T−1 | −0.308 | [−0.432, −0.183] | −26% | < .001 | 692 | 4,239 |
| log(1 + meets), exits at ages 17–19 only (reference seasons observed) | T | −0.603 | [−0.733, −0.472] | −45% | < .001 | 692 | 4,239 |

*Note.* Linear model with athlete fixed effects (within transformation), age fixed effects (ages 13–19), and indicators for the final active season (T) and the three preceding seasons of athletes whose exit was observed (final active season before 2024); seasons after the final active season are excluded, and the seasons of athletes still active, or more than three seasons before exit, form the reference. Estimates are deviations from the athlete's own reference-period volume net of the common age profile; for log(1 + meets) the effect column gives 100 × (exp(β) − 1). Standard errors are cluster-robust by athlete. The decline steepens towards exit (Wald test T−1 = T−3, p < .001). The final-season estimate is partly mechanical (the last season with ≥2 results is often a partial season). See Supplementary Methods S-M6 and Supplementary Figure S5.

---

## Table S29. {+Early-warning thresholds derived in one birth cohort and validated in the other+}

| Analysis | Threshold (meets) | n | Flagged % | Sensitivity | Specificity | PPV | Retention, flagged | Retention, unflagged |
|---|---|---|---|---|---|---|---|---|
| Lowest-quartile rule derived in Cohort A | < 10 | 1,301 | 27.4 | 0.31 [0.28, 0.33] | 0.89 [0.85, 0.93] | 0.94 [0.91, 0.96] | 6.2% [3.8, 8.8] | 19.5% [17.0, 22.0] |
| Cohort-A lowest-quartile cut-off applied to Cohort B (validation) | < 10 | 822 | 24.8 | 0.29 [0.25, 0.32] | 0.93 [0.88, 0.97] | 0.95 [0.92, 0.98] | 4.9% [2.2, 8.1] | 21.4% [18.4, 24.6] |
| Lowest-quartile rule derived in Cohort B | < 11 | 822 | 27.0 | 0.31 [0.27, 0.34] | 0.91 [0.86, 0.95] | 0.94 [0.91, 0.97] | 5.9% [2.9, 9.1] | 21.5% [18.2, 24.8] |
| Cohort-B lowest-quartile cut-off applied to Cohort A (validation) | < 11 | 1,301 | 31.7 | 0.35 [0.33, 0.38] | 0.88 [0.83, 0.92] | 0.94 [0.92, 0.96] | 6.1% [3.9, 8.5] | 20.4% [17.7, 23.1] |
| Derived in Cohort A (Youden’s J) | < 21 | 1,301 | 61.3 | 0.67 [0.64, 0.70] | 0.70 [0.64, 0.76] | 0.92 [0.90, 0.94] | 7.7% [5.9, 9.6] | 28.8% [25.0, 32.7] |
| Cohort-A threshold applied to Cohort B (validation) | < 21 | 822 | 53.6 | 0.59 [0.55, 0.63] | 0.72 [0.64, 0.79] | 0.91 [0.88, 0.93] | 9.1% [6.5, 11.8] | 26.8% [22.3, 31.4] |
| Derived in Cohort B (Youden’s J) | < 29 | 822 | 70.4 | 0.76 [0.73, 0.79] | 0.58 [0.50, 0.66] | 0.90 [0.87, 0.92] | 10.2% [7.7, 12.7] | 34.2% [28.0, 40.2] |
| Cohort-B threshold applied to Cohort A (validation) | < 29 | 1,301 | 76.4 | 0.82 [0.79, 0.84] | 0.52 [0.45, 0.58] | 0.90 [0.88, 0.92] | 10.0% [8.2, 11.9] | 34.9% [29.6, 40.1] |
| Candidate < 10 meets, Cohort A | < 10 | 1,301 | 27.4 | 0.31 [0.28, 0.33] | 0.89 [0.85, 0.93] | 0.94 [0.91, 0.96] | 6.2% [4.0, 8.7] | 19.5% [16.9, 22.0] |
| Candidate < 10 meets, Cohort B | < 10 | 822 | 24.8 | 0.29 [0.25, 0.32] | 0.93 [0.88, 0.97] | 0.95 [0.92, 0.98] | 4.9% [2.3, 8.0] | 21.4% [18.0, 24.6] |

*Note.* Cohort A: births 1998–2000; Cohort B: births 2001–2002. Lowest-quartile rule: flag athletes at or below the 25th percentile of pre-milestone volume in the derivation cohort (≤ 9 meets in Cohort A, i.e. < 10; ≤ 10 in Cohort B, i.e. < 11). Youden’s J maximizes sensitivity + specificity − 1 over cut-offs 2–40. Brackets: 2,000-replicate bootstrap 95% CIs within the evaluation cohort. Sensitivity and PPV refer to identifying athletes who did not retain senior activity.

---

## Table S30. {+Temporary gaps, returns, and alternative event definitions (baseline-only Cox model)+}

| Event definition | n | Events | Volume HR per SD [95% CI] | HHI HR per SD | C-index |
|---|---|---|---|---|---|
| Final active season (primary; censored if active 2024+) | 2,095 | 1,934 | 0.54 [0.50, 0.57] | 0.89 | 0.743 |
| First sustained exit (active season followed by ≥2 inactive seasons) | 2,095 | 1,954 | 0.51 [0.48, 0.54] | 0.89 | 0.755 |
| First inactive season (any one-season gap ends the spell) | 2,095 | 2,022 | 0.50 [0.47, 0.53] | 0.92 | 0.771 |

*Note.* All models include sex, Tyrving, HHI (ages 13–14), and pre-milestone volume. An active season is a calendar year with ≥2 results. 11.8% of athletes (251) had at least one inactive season followed by a return, 4.5% (95) a gap of two or more seasons followed by a return, and 1.8% a gap of three or more. Of 1,770 athletes who at some point (before 2020) missed two consecutive seasons, 4.4% ever returned. Under the primary definition such returns are part of a continuing career; the alternative definitions instead end the spell at the first two-season gap or at the first inactive season (censored if no such pattern is observed through 2025).

---

## Table S31. {+The cohort within the register population of the same birth years+}

| Group | n | Female % | Meets at 13–14, median [IQR] | ≥10 meets at 13–14 (%) | Senior retention % | Volume OR per 10 meets | CV-AUC (sex + volume) |
|---|---|---|---|---|---|---|---|
| Cohort (attended the baseline meet) | 2,123 | 52.9 | 19 [10–33] | 77.2 | 16.7 | 1.62 [1.51, 1.73] | 0.741 |
| Not in cohort (same birth years, ≥1 result at 13–14) | 5,204 | 52.6 | 2 [1–4] | 9.0 | 2.0 | 2.07 [1.70, 2.52] | 0.68 |
| All athletes born 1998–2002 with ≥1 result at 13–14 | 7,327 | 52.7 | 3 [1–12] | 28.8 | 6.3 | 1.97 [1.87, 2.08] | 0.828 |

*Note.* All athletes born 1998–2002 with at least one registered result at ages 13–14, from the register version of September 2026 (the cohort analyses use April 2026). The cohort comprises 29% of these athletes but 78% of those with ten or more meets at 13–14 and 77% of the 458 who later had an active senior season. Meet counts here are taken directly from the register, where the baseline meet is stored in more than one row; for cohort members they therefore average 2.5 meets more than the de-duplicated counts used in the main analyses. Senior retention: ≥2 results in a calendar year at age 20 or later.

---

## Table S32. {+Senior retention by baseline performance quartile and pre-milestone volume+}

| Baseline Tyrving quartile | Retention, volume above median | Retention, volume at or below median |
|---|---|---|
| Q1 (lowest) | 15.4% (n = 156) | 9.5% (n = 368) |
| Q2 | 17.3% (n = 208) | 5.7% (n = 316) |
| Q3 | 23.8% (n = 282) | 4.3% (n = 256) |
| Q4 (highest) | 36.0% (n = 372) | 13.9% (n = 137) |

*Note.* Median pre-milestone volume = 17 meets. Above-median volume is associated with higher senior retention in every performance quartile.

---
