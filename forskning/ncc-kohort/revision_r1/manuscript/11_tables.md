# Tables

(Submitted as editable text; in the final Word manuscript, each table on its own page after the references. Supplementary Tables S1–{+S32+} follow as supplementary material.)

---

## Table 1. Cohort characteristics by birth-year cohort

| Characteristic | Cohort A (1998–2000) | Cohort B (2001–2002) | All cohorts |
|---|---|---|---|
| N | {+1,309+} | {+829+} | {+2,138+} |
| Male (n) | {+608+} | {+398+} | {+1,006+} |
| Female (n) | {+700+} | {+430+} | {+1,130+} |
| Sex unknown (n) | {+1+} | {+1+} | {+2+} |
| Median career length (years) | 2.0 | 3.0 | 2.0 |
| {+Active at age 17 or later (%)+} | 41.0 | {+41.3+} | {+41.1+} |
| Ever active at age 20+ (%) | 15.8 | {+17.0+} | {+16.3+} |
| Still active in 2024 or later (%) | {+5.7+} | {+10.5+} | {+7.6+} |
| Mean Tyrving best at baseline | {+816+} | {+836+} | {+824+} |
| Median total meets, ages 13–14 (pre-milestone volume) | {+15+} | {+18+} | 17 |

*Note.* "Active at age {+17 or later"+} indicates {+an active season (≥2+} registered results in {+a+} calendar {+year) at age 17 or later;+} "Ever active at age 20+" is the outcome prevalence (≥2 results in any calendar year at age 20 or later). Tyrving points = the Norwegian Athletics Federation's age-norm score, where 1,000 corresponds to the published reference performance for that event × sex × age {+combination; all baseline events scored with implement- and hurdle-specific norms and the workbook's own formulas (Supplementary Methods S-M3). Meets are counted as competition days (Section 2.4.4). Follow-up through 2025.+}

---
## Table 2. Competition volume trajectory by senior-retention status (median competitions per year and IQR)

| Group | N | Age 13 | Age 14 | Age 15 | Age 16 | Age 17 | Age 18 |
|---|---|---|---|---|---|---|---|
| Senior retainers (active age ≥20) | 348 | {+13 [6–20]+} | {+16.5 [10–24]+} | {+19 [11–26]+} | 18 [10–26] | 17 [10–24] | 14 [7–20] |
| Dropouts (last active age <20) | {+1,790+} | 8 [4–13] | 8 [3–14] | 3 [0–11] | 0 [0–7] | 0 [0–2] | 0 [0–0] |

*Note.* Values are median number of meets {+(competition days)+} per year [IQR]. Future retainers and future dropouts already differ at ages 13–14; the gap widens further across the age-14-to-15 transition.

---
## Table 3. Primary analysis: prospective logistic regression for active senior status (baseline-only predictors, ages 13–14)

| Model | Covariate | OR | 95% CI | p | {+CV-AUC [95% CI]+} | n |
|---|---|---|---|---|---|---|
| L1: Sex only | Female | {+0.75+} | {+[0.60, 0.95]+} | {+.016+} | {+0.535 [0.506, 0.565]+} | {+2,136+} |
| L2: + Performance | Female | {+0.63+} | {+[0.50, 0.80]+} | {+< .001+} | {+0.700 [0.671, 0.730]+} | {+2,136+} |
|  | Tyrving (z) | {+2.54+} | {+[2.14, 3.02]+} | < .001 |  |  |
| {+L3: + Event concentration+} | Female | {+0.63+} | {+[0.50, 0.80]+} | {+< .001+} | {+0.698 [0.668, 0.728]+} | {+2,136+} |
|  | Tyrving (z) | {+2.54+} | {+[2.14, 3.02]+} | < .001 |  |  |
|  | {+HHI, ages 13–14 (z)+} | {+1.00+} | {+[0.89, 1.13]+} | {+.956+} |  |  |
| L4: + Pre-milestone volume | Female | {+0.56+} | {+[0.43, 0.72]+} | < .001 | {+**0.767** [0.737, 0.797]+} | {+2,136+} |
|  | Tyrving (z) | {+1.75+} | {+[1.47, 2.08]+} | {+< .001+} |  |  |
|  | {+HHI, ages 13–14 (z)+} | {+1.18+} | {+[1.04, 1.34]+} | {+.012+} |  |  |
|  | **Pre-milestone volume (z)** | **{+2.04+}** | **{+[1.80, 2.32]+}** | **< .001** |  |  |

*Note.* Logistic regression for binary active senior status (≥2 registered results in any year at age 20+). Predictors are observed during the baseline window (ages 13–14) {+only, including HHI (results at ages 13–14).+} Pre-milestone volume is the {+number+} of meets {+(competition days)+} at ages 13 and 14. Continuous covariates are z-standardized so ORs reflect per-SD effects. {+CV-AUC: mean of fold-level AUCs from stratified 5-fold cross-validation repeated 20 times, with standardization inside the training folds; 95% CI from the corrected resampled t (Supplementary Methods S-M4). Adding volume raised the+} AUC {+by 0.069 (95% CI 0.047 to 0.091; Supplementary Table S27). HHI+} is {+associated with retention only+} once volume is {+entered, does not improve discrimination, and is not robust to performance in+} the {+athlete's main+} event {+category (Supplementary Table S18;+} Discussion 4.6).

---
## Table 4. {+Level+} versus {+within-athlete change:+} volume {+at age 14+} and change {+from 14 to 15+}

| Model | Covariate | {+OR per SD+} | 95% CI | p |
|---|---|---|---|---|
| M1: Volume at age 14 only | Female | {+0.55+} | {+[0.42, 0.71]+} | < .001 |
|  | Tyrving (z) | {+1.79+} | {+[1.50, 2.13]+} | {+< .001+} |
|  | **Volume at age 14 (z)** | **{+2.05+}** | **{+[1.80, 2.33]+}** | **< .001** |
| M2: + Volume change 14→15 | Female | {+0.55+} | {+[0.42, 0.72]+} | < .001 |
|  | Tyrving (z) | {+1.59+} | {+[1.33, 1.91]+} | {+< .001+} |
|  | **Volume at age 14 (z)** | **{+2.51+}** | **{+[2.17, 2.89]+}** | **< .001** |
|  | **Volume change 14→15 (z)** | **{+2.29+}** | **{+[2.00, 2.62]+}** | **< .001** |

*Note.* {+Change = volume at 15 minus volume at 14 (positive = increase; mean −2.2, SD 6.4 meets). The OR of 2.29 per SD increase is equivalent+} to {+OR = 0.44 [0.38, 0.50] per SD of greater decline (about 6.4 fewer meets),+} conditional on {+the+} level at age {+14; per 5 fewer meets, OR = 0.52. Because the model is linear in the logit, it is identical to one with volume at 14 and volume at 15 as separate levels (the per-meet OR for change equals the per-meet OR for volume at 15). Pseudo-R² (McFadden) rose from 0.150 (M1) to 0.245 (M2); CV-AUC 0.763 → 0.833. 1 of the 1,926 athletes with a result at 14 lacks registered sex or a Tyrving score (sample n = 1,925).+} Both baseline level and within-athlete {+decline+} contribute substantially and independently.

---
## Table 5. Time-varying hazard ratios (post-baseline Cox specification, period-specific)

| Covariate | Years 0–3 since baseline (approx. ages 13–17) | Years 3–6 (approx. ages 16–20) | Years 6+ (approx. ages 19+) |
|---|---|---|---|
| Volume at age 15–16 (per SD) | 0.14 [0.11, 0.16] | {+0.70 [0.62, 0.79]+} | {+0.93 [0.77, 1.12]+} |
| Championship types (count) | {+0.79 [0.73, 0.86]+} | {+0.93 [0.81, 1.06]+} | {+0.78 [0.61, 0.99]+} |
| Tyrving (z) | {+0.93 [0.89, 0.98]+} | {+0.84 [0.76, 0.94]+} | {+1.05 [0.86, 1.28]+} |
| {+HHI, ages 13–14 (z)+} | {+1.03 [0.98, 1.09]+} | {+0.90 [0.82, 0.99]+} | {+1.00 [0.86, 1.16]+} |
| Female | {+1.07 [0.96, 1.19]+} | {+1.48 [1.23, 1.78]+} | {+1.03 [0.76, 1.40]+} |
| n at risk in interval | {+2,136+} | {+823+} | {+335+} |
| events in interval | {+1,313+} | {+488+} | {+174+} |
| C-index | {+0.897+} | {+0.660+} | {+0.580+} |

*Note.* Period-specific Cox estimates from the post-baseline specification with covariates measured at ages 15–16 and ≤17. The early-window HR for ages-15–16 volume partly reflects operational overlap between predictor and outcome (low milestone volume is mechanical for athletes who drop out before age 15); this estimate should be read as descriptive of the time-varying association rather than as an independent prospective effect. Substantively, the protective association attenuates across follow-up, consistent with a proximal disengagement-marker interpretation. {+All rows are generated directly from the analysis code (C-index per interval from the same models).+}

---
## Table 6. Prospective early-warning thresholds (pre-milestone volume, ages 13–14)

| Threshold (flag if vol <) | Flagged % | Sensitivity | Specificity | PPV | NPV | Senior retention, flagged | Senior retention, unflagged |
|---|---|---|---|---|---|---|---|
| 5 meets | {+9.5+} | {+0.11 [0.09, 0.12]+} | 0.96 [0.94, 0.98] | **0.93** [0.89, 0.96] | 0.17 [0.16, 0.19] | {+6.9% [3.7, 10.7]+} | {+17.3% [15.6, 18.9]+} |
| 8 meets | {+20.4+} | {+0.23 [0.21, 0.25]+} | 0.93 [0.90, 0.96] | {+**0.95** [0.92, 0.97]+} | 0.19 [0.17, 0.21] | {+5.5% [3.4, 7.8]+} | {+19.0% [17.2, 20.9]+} |
| 10 meets | {+27.3+} | {+0.31 [0.29, 0.33]+} | 0.91 [0.88, 0.94] | {+**0.95** [0.93, 0.96]+} | 0.20 [0.18, 0.22] | {+5.5% [3.7, 7.4]+} | {+20.3% [18.3, 22.4]+} |
| 15 meets | {+44.4+} | {+0.49 [0.47, 0.52]+} | {+0.80 [0.76, 0.85]+} | {+**0.93** [0.91, 0.94]+} | 0.24 [0.21, 0.26] | {+7.2% [5.5, 8.9]+} | 23.5% [21.1, 25.9] |

*Note.* Classification performance of pre-milestone (ages 13–14) competition volume as a prospective early-warning indicator, applicable at the end of an athlete's age-14 season, before the qualification window opens. All metrics are computed on one denominator (full cohort, n = {+2,138);+} brackets are 2,000-replicate bootstrap 95% CIs. PPV is the proportion of flagged athletes who subsequently failed to retain senior activity. The final two columns give the absolute retention contrast: at the < 10 threshold, {+5.5%+} among flagged vs. {+20.3%+} among unflagged athletes (a {+3.7-fold+} difference). The high PPV partly reflects the population's 84% non-retention base rate (the threshold improves precision by {+~11+} percentage points over base-rate prediction), and the NPV of ≈ 0.20 means unflagged athletes are not "safe": roughly four in five of them also fail to retain. {+The thresholds are candidate cut-offs chosen in the pooled data; derivation in one birth cohort and validation in the other are reported in Supplementary Table S29.+} Calibration of the underlying model is reported in Supplementary Table S23.

---
## Table 7. {+Internal cohort+} replication of the primary L4 logistic model

| Cohort | n | Covariate | OR | 95% CI | p |
|---|---|---|---|---|---|
| 1998–2000 | {+1,308+} | Female | {+0.57+} | {+[0.41, 0.79]+} | < .001 |
|  |  | Tyrving (z) | {+1.80+} | {+[1.44, 2.25]+} | {+< .001+} |
|  |  | {+HHI, ages 13–14 (z)+} | {+1.07+} | {+[0.90, 1.28]+} | {+.414+} |
|  |  | **Pre-milestone volume (z)** | **{+2.03+}** | **{+[1.72, 2.38]+}** | **< .001** |
| 2001–2002 | {+828+} | Female | {+0.55+} | {+[0.37, 0.83]+} | {+.005+} |
|  |  | Tyrving (z) | {+1.69+} | {+[1.28, 2.24]+} | {+< .001+} |
|  |  | {+HHI, ages 13–14 (z)+} | {+1.32+} | {+[1.10, 1.60]+} | {+.004+} |
|  |  | **Pre-milestone volume (z)** | **{+2.10+}** | **{+[1.71, 2.58]+}** | **< .001** |

*Note.* The primary baseline-only logistic model re-estimated separately within each birth-year cohort. {+ORs are per SD of the whole cohort, so the two cohorts are on the same scale. Both cohorts come from the same register and national system, so this is an internal replication. The pre-milestone+} volume effect {+and the performance association are reproduced at similar magnitude+} in both {+cohorts; female sex predicts lower retention in both.+} The {+HHI association is clear+} in the {+2001–2002 cohort but not+} significant in the {+1998–2000 cohort (see Section 3.9).+}

---

# Supplementary Tables

## Table S1. Proportional-hazards assumption test for the post-baseline Cox specification (Schoenfeld residuals)

| Covariate | χ²₁ | p |
|---|---|---|
| Female | {+2.52+} | {+.113+} |
| Tyrving (z) | {+0.34+} | {+.560+} |
| {+HHI, ages 13–14 (z)+} | {+14.40+} | < .001 |
| Volume at age 15–16 (z) | {+293.15+} | < .001 |
| Championship types | {+13.52+} | {+< .001+} |



---

## Table S2. Cluster-robust SE Cox (clustered on club)

| Covariate | HR | Robust 95% CI | p (robust) |
|---|---|---|---|
| Female | {+1.15+} | {+[1.02, 1.30]+} | {+.021+} |
| Tyrving (z) | {+0.91+} | {+[0.86, 0.96]+} | {+.001+} |
| {+HHI, ages 13–14 (z)+} | {+0.98+} | {+[0.92, 1.05]+} | {+.583+} |
| Volume at age 15–16 (z) | {+0.45+} | {+[0.41, 0.51]+} | < .001 |
| Championship types | {+0.75+} | {+[0.69, 0.81]+} | < .001 |

*Note.* Post-baseline specification; pooled HRs average over the strongly time-varying pattern shown in Table 5 and are descriptive. {+Club-clustered errors for the primary logistic model are in Supplementary Table S22.+}

---

## Table S3. E-values for the primary baseline-window volume effect (VanderWeele & Ding, 2017)

| Effect | Estimate | {+Approx. RR (common outcome; protective effects inverted)+} | E-value (point) | E-value (CI bound) |
|---|---|---|---|---|
| Pre-milestone volume, primary logistic (per SD) | {+OR 2.04 [1.80, 2.32]+} | {+1.43+} | {+2.21+} | {+2.02+} |
| {+Pre-milestone volume, baseline-only Cox from the end of age 14 (per SD)+} | {+HR 0.65 [0.62, 0.69]+} | {+1.34+} | {+2.02+} | {+1.90+} |

*Note.* Because the outcome is common {+(16.3%),+} the odds ratio is converted to an approximate risk ratio (RR ≈ √OR) before computing E = RR + √(RR(RR − 1)); the hazard ratio uses the common-outcome conversion {+RR ≈ (1 − 0.5^√HR)/(1 − 0.5^√(1/HR)), inverted because the association is protective+} (Supplementary Methods S-M5). E-values are reported for the primary baseline-window specification only; the post-baseline (ages-15–16) specification is not an admissible E-value input because it overlaps the outcome window and violates proportional hazards.

---

## Table S4. Sample-size sensitivity: minimum detectable {+hazard and odds ratios+}

| Cohort | {+N (Cox)+} | Events | {+Min. detectable HR+} | {+n (logistic)+} | {+Retainers+} | {+Min. detectable OR+} |
|---|---|---|---|---|---|---|
| Combined | {+1,908+} | {+1,747+} | {+1.069+} | {+2,136+} | {+347+} | {+1.179+} |
| 1998–2000 | {+1,169+} | {+1,094+} | {+1.088+} | {+1,308+} | {+207+} | {+1.236+} |
| 2001–2002 | {+739+} | {+653+} | {+1.116+} | {+828+} | {+140+} | {+1.297+} |

{+*Note.* 80% power, α = .05, per SD of a standardized covariate. Cox: the baseline-only model with time zero at the end of the age-14 season (Supplementary Table S10); log HR_min = (z₀.₉₇₅ + z₀.₈₀)/√events. Logistic: the primary model; log OR_min = (z₀.₉₇₅ + z₀.₈₀)/√(n·p·(1 − p)), with p the retention rate (normal-covariate approximation). Supplementary Methods S-M2.+}

---

## Table S5. Complete-case vs mean-imputation sensitivity

| Covariate | HR (complete case) | HR (mean imputation) |
|---|---|---|
| Female | {+1.15+} | {+1.15+} |
| Tyrving (z) | {+0.91+} | {+0.91+} |
| {+HHI, ages 13–14 (z)+} | {+0.98+} | {+0.98+} |
| Volume at age 15–16 (z) | {+0.45+} | 0.45 |
| Championship types | {+0.75+} | {+0.75+} |
| n | {+2,136+} | {+2,138+} |

*Note.* Post-baseline Cox specification (descriptive; see Table 5 note). The principal missing-data sensitivity for the primary logistic model is multiple imputation, Supplementary Table S21. {+The mean-imputation model retains all 2,138 athletes; the 2 without registered sex enter with the male reference code.+}

---

## Table S6. Cox model stratified on HHI tercile (sensitivity to PH violation)

| Covariate | HR | p |
|---|---|---|
| Female | {+1.15+} | {+.003+} |
| Tyrving (z) | {+0.91+} | {+< .001+} |
| Volume at age 15–16 (z) | 0.44 | < .001 |
| Championship types | {+0.76+} | < .001 |

{+*Note.* Post-baseline specification. HHI is one of the covariates that violate proportional hazards (Supplementary Table S1); stratifying on it leaves the other estimates unchanged. The dominant violation, ages-15–16 volume, is addressed by the period-specific estimates in Table 5, not by this model.+}

---

## Table S7. Sex-stratified Cox subgroup analyses

| Sex | n | Covariate | HR | 95% CI | p |
|---|---|---|---|---|---|
| Male | {+1,006+} | Tyrving (z) | {+0.97+} | {+[0.91, 1.03]+} | {+.260+} |
|  |  | {+HHI, ages 13–14 (z)+} | {+0.98+} | {+[0.92, 1.04]+} | {+.518+} |
|  |  | Volume at age 15–16 (z) | {+0.46+} | {+[0.41, 0.51]+} | < .001 |
|  |  | Championship types | {+0.64+} | {+[0.58, 0.71]+} | < .001 |
| Female | {+1,130+} | Tyrving (z) | {+0.83+} | {+[0.78, 0.89]+} | {+< .001+} |
|  |  | {+HHI, ages 13–14 (z)+} | {+0.99+} | {+[0.93, 1.05]+} | {+.692+} |
|  |  | Volume at age 15–16 (z) | 0.45 | {+[0.40, 0.50]+} | < .001 |
|  |  | Championship types | {+0.85+} | {+[0.78, 0.93]+} | < .001 |

*Note.* Post-baseline specification (descriptive; see Table 5 note). C-index = {+0.849 (male) and 0.846 (female).+} The dominant behavioral covariate is near-identical across sexes (volume HR {+0.46+} vs {+0.45).+}

---

## Table S8. Landmark analysis at age 16 (post-baseline Cox, n = {+1,148)+}

| Covariate | HR | 95% CI | p |
|---|---|---|---|
| Female | {+1.24+} | {+[1.09, 1.41]+} | < .001 |
| Tyrving (z) | {+0.89+} | {+[0.83, 0.96]+} | {+.002+} |
| {+HHI, ages 13–14 (z)+} | {+0.91+} | {+[0.85, 0.97]+} | {+.004+} |
| **Volume at age 15–16 (z)** | {+0.68+} | {+[0.62, 0.74]+} | < .001 |
| Championship types | {+0.87+} | {+[0.79, 0.96]+} | {+.005+} |
| n complete | {+1,147+} |  |  |
| C-index | {+0.695+} |  |  |

*Note.* Athletes {+still in their career+} at age {+16 (final active season at 16 or later),+} with follow-up time measured from age 16 {+forward (986 events). The earlier entry rule (≥1 result at 16) also admitted 71 athletes whose final active season was earlier, so that their event preceded time zero. The+} age-16 share of the exposure window lies at the start of the at-risk window (see Supplementary Methods S-M1). The fully contamination-free logistic analogue is the change model in main-text Section 3.5 / Supplementary Table S19.

---

## Table S9. Outcome-definition sensitivity (primary L4 specification, baseline-only predictors)

| Outcome | Description | Retainer n (%) | OR (pre-milestone vol per SD) | 95% CI | CV-AUC |
|---|---|---|---|---|---|
| A | ≥1 senior-age (20+) result | {+412 (19.3%)+} | {+1.95+} | {+[1.73, 2.20]+} | {+0.745+} |
| B | ≥2 results in any senior-age year (primary) | {+348 (16.3%)+} | {+2.04+} | {+[1.80, 2.32]+} | {+0.770+} |
| C | ≥2 results in each of two distinct senior-age years | {+255 (11.9%)+} | {+1.87+} | {+[1.64, 2.14]+} | {+0.767+} |

*Note.* All three rows re-estimate the primary L4 model (sex, Tyrving, HHI, pre-milestone volume; n = {+2,136)+} with the alternative outcome definitions. The volume effect is stable across definitions. {+CV-AUC here is from a single stratified 5-fold split, as in the original analysis, so it differs slightly from the repeated cross-validation in Table 3.+}

---

## Table S10. Lagged volume: pre-milestone (ages 13–14) alone (Cox)

| Covariate | HR | 95% CI | p |
|---|---|---|---|
| Female | {+1.21+} | {+[1.10, 1.34]+} | {+< .001+} |
| Tyrving (z) | {+0.82+} | {+[0.79, 0.86]+} | {+< .001+} |
| {+HHI, ages 13–14 (z)+} | {+0.91+} | {+[0.87, 0.96]+} | < .001 |
| **{+Pre-milestone volume (z)+}** | {+0.65+} | {+[0.62, 0.69]+} | < .001 |

*Note.* n = {+1,908 (1,747 events);+} C-index = {+0.690. Time zero is the end of the age-14 season, when the predictor window closes; the 229 athletes whose final active season was at 13 had left before time zero and are not at risk.+}

---

## Table S11. Sensitivity excluding zero-volume athletes (post-baseline Cox)

| Covariate | HR | 95% CI | p |
|---|---|---|---|
| Female | {+1.22+} | {+[1.10, 1.36]+} | {+< .001+} |
| Tyrving (z) | {+0.91+} | {+[0.86, 0.96]+} | {+< .001+} |
| {+HHI, ages 13–14 (z)+} | 0.96 | {+[0.91, 1.01]+} | {+.141+} |
| **Volume at age 15–16 (z)** | {+0.52+} | {+[0.48, 0.56]+} | < .001 |
| Championship types | 0.80 | {+[0.74, 0.87]+} | < .001 |

*Note.* Excludes {+595+} athletes with vol_milestone = 0; remaining n = {+1,541;+} C-index = {+0.790. Follow-up starts at baseline, and having any volume at 15–16 requires remaining active to 15–16, so this restriction does not remove the survival conditioning of the post-baseline specification; descriptive only. The landmark analysis (Supplementary Table S8) is the appropriate check.+}

---

## Table S12. Analysis sample flow

| Analysis | n | Definition |
|---|---|---|
| Total cohort | {+2,138+} | All included athletes |
| Sex known | {+2,136+} | {+Gender M/F registered (2 unknown; excluded from regression models except the mean-imputation check in Table S5, included in cohort totals and unstratified KM curves)+} |
| Primary logistic L1–L4 | {+2,136+} | Complete case on sex, Tyrving, HHI, pre-milestone volume; L1–L3 fitted on the same fixed sample for AUC comparability |
| Level-vs-change (Table 4) | {+1,925+} | {+Of 1,926 athletes with ≥1 result at age 14; complete case on sex and Tyrving+} |
| Contamination-free change model | {+1,088+} | {+Of 1,089 athletes with ≥2 results at age 16; complete case on sex+} |
| {+Baseline-only Cox (Supplementary Tables S10, S16, S30)+} | {+1,908+} | {+Time zero at the end of the age-14 season; excludes the 229 athletes whose final active season was at 13 and 1 without registered sex; the first-inactive-season definition in Table S30 also requires an active season at 14+} |
| {+Landmark Cox at age 16+} | {+1,147+} | {+Of 1,148 athletes still in their career at 16 (final active season at 16 or later); complete case on model covariates+} |
| {+Performance-trajectory comparison (Table S15)+} | {+1,721+} | {+Complete case on Tyrving at both age 13 and age 14+} |
| {+Nested predictor subsets (Table S17)+} | {+1,501+} | {+Complete case on all 22 candidate predictors+} |
| {+Multiple imputation+} | {+2,136+} | {+All athletes with known sex; Tyrving imputed (m = 20)+} |
| {+Within-athlete fixed-effects model (Table S28)+} | {+1,909+} | {+Athletes with ≥2 athlete-seasons at ages 13–19 up to and including the final active season (8,490 athlete-seasons)+} |
| {+Specialization confound models (S18 B/C)+} | {+2,135 / 2,135+} | {+Complete case on primary-category Tyrving+} |

*Note.* One map of every analysis sample in the manuscript; each n is derivable from the row's definition.

---

## Table S13. Primary logistic regression with structural controls {+(Panel A) and birth-quarter coding (Panel B)+}

| Covariate | OR | 95% CI | p |
|---|---|---|---|
| Female | {+0.54+} | {+[0.42, 0.70]+} | < .001 |
| Tyrving (z) | {+1.83+} | {+[1.53, 2.18]+} | {+< .001+} |
| {+HHI, ages 13–14 (z)+} | {+1.16+} | {+[1.02, 1.32]+} | {+.020+} |
| **Pre-milestone volume (z)** | {+2.07+} | {+[1.82, 2.37]+} | < .001 |
| Q1 born | {+0.73+} | {+[0.55, 0.98]+} | {+.036+} |
| Q4 born | {+1.14+} | {+[0.80, 1.64]+} | {+.465+} |
| Region: Østlandet | {+1.29+} | {+[0.96, 1.74]+} | {+.095+} |
| Region: Midt-Norge | {+1.06+} | {+[0.73, 1.53]+} | {+.778+} |
| Club size (z) | {+0.94+} | {+[0.83, 1.07]+} | {+.363+} |

*Note.* n = {+2,136. Panel A (as submitted): Q1 and Q4 indicators against Q2–Q3, the relative-age extremes; the 90 athletes registered with birth year but no birth date (none of whom retained) fall in the reference group.+} Pre-milestone volume effect unchanged: OR {+2.07+} with controls vs. {+2.04 without. Of the+} structural controls {+only Q1 born reached p < .05 (OR 0.73 [0.55, 0.98]). Region could not be determined for 2 athletes, who fall in the reference region (western Norway).+}

**{+Panel B. Birth-quarter specifications (all models include sex, Tyrving, HHI, volume, region and club size)+}**

| Specification | Covariate | OR | 95% CI | p | LR test of quarter terms | n |
|---|---|---|---|---|---|---|
| {+As submitted: Q1 and Q4 indicators vs. Q2–Q3 (unknown quarter coded to the reference)+} | {+Q1 (Jan–Mar)+} | {+0.73+} | {+[0.55, 0.98]+} | {+.036+} | {+χ²(2) = 6.32, p = 0.04+} | {+2,136+} |
|  | {+Q4 (Oct–Dec)+} | {+1.14+} | {+[0.80, 1.64]+} | {+.465+} |  |  |
|  | {+Pre-milestone volume (z)+} | {+2.07+} | {+[1.82, 2.37]+} | {+< .001+} |  |  |
| {+Q1 and Q4 indicators vs. Q2–Q3, known quarter only+} | {+Q1 (Jan–Mar)+} | {+0.70+} | {+[0.53, 0.94]+} | {+.017+} | {+χ²(2) = 7.17, p = 0.03+} | {+2,046+} |
|  | {+Q4 (Oct–Dec)+} | {+1.08+} | {+[0.76, 1.55]+} | {+.659+} |  |  |
|  | {+Pre-milestone volume (z)+} | {+2.02+} | {+[1.77, 2.31]+} | {+< .001+} |  |  |
| {+Full coding: Q2, Q3, Q4 vs. Q1, known quarter only+} | {+Q2 (Apr–Jun)+} | {+1.37+} | {+[0.99, 1.90]+} | {+.061+} | {+χ²(3) = 7.45, p = 0.06+} | {+2,046+} |
|  | {+Q3 (Jul–Sep)+} | {+1.50+} | {+[1.06, 2.13]+} | {+.022+} |  |  |
|  | {+Q4 (Oct–Dec)+} | {+1.55+} | {+[1.04, 2.30]+} | {+.032+} |  |  |
|  | {+Pre-milestone volume (z)+} | {+2.02+} | {+[1.77, 2.30]+} | {+< .001+} |  |  |
| {+Linear trend across quarters 1–4, known quarter only+} | {+Quarter (linear, 1–4)+} | {+1.16+} | {+[1.03, 1.31]+} | {+.013+} | {+χ²(1) = 6.11, p = 0.01+} | {+2,046+} |
|  | {+Pre-milestone volume (z)+} | {+2.01+} | {+[1.76, 2.30]+} | {+< .001+} |  |  |

{+Conditional on performance and volume, relatively younger athletes were somewhat more likely to be retained (linear trend OR 1.16 per quarter [1.03, 1.31], LR p = .013; full coding p = .059); the volume coefficient is unchanged (2.01–2.07).+}

---

## Table S14. {+Level-versus-change+} analysis details (athletes with ≥1 result at age 14; complete-case n = {+1,925)+}

| Model | Covariate | OR | 95% CI | p | Pseudo-*R*² | {+CV-AUC+} |
|---|---|---|---|---|---|---|
| M1: Volume at age 14 only | Female | {+0.55+} | {+[0.42, 0.71]+} | < .001 | {+0.150+} | {+0.763+} |
|  | Tyrving (z) | {+1.79+} | {+[1.50, 2.13]+} | {+< .001+} |  |  |
|  | Volume at age 14 (z) | {+2.05+} | {+[1.80, 2.33]+} | < .001 |  |  |
| M2: + Volume change 14→15 | Female | {+0.55+} | {+[0.42, 0.72]+} | < .001 | {+0.245+} | {+0.833+} |
|  | Tyrving (z) | {+1.59+} | {+[1.33, 1.91]+} | {+< .001+} |  |  |
|  | Volume at age 14 (z) | {+2.51+} | {+[2.17, 2.89]+} | < .001 |  |  |
|  | Volume change 14→15 (z) | {+2.29+} | {+[2.00, 2.62]+} | < .001 |  |  |

*Note.* Full coefficient detail for main-text Table 4, {+with repeated cross-validated AUC. Change = volume at 15 minus volume at 14.+}

---

## Table S15. Time-aligned behavior versus performance {+(repeated 5-fold+} CV-AUC)

| Predictor set (all ages 13–14 measurements) | n | CV-AUC |
|---|---|---|
| Sex + baseline Tyrving | {+2,136+} | {+0.700+} |
| Sex + Tyrving + performance trajectory (Δ13–14) | {+1,721+} | {+0.737+} |
| {+Sex + within-event percentile at the baseline meet+} | {+2,136+} | {+0.689+} |
| {+Sex + pre-milestone volume+} | {+2,136+} | {+0.740+} |
| {+Sex + pre-milestone volume (trajectory subsample)+} | {+1,721+} | {+0.736+} |
| {+Sex + Tyrving + pre-milestone volume+} | {+2,136+} | {+0.763+} |

*Note.* {+Both+} predictors {+are+} observed during the baseline window {+(ages 13–14). Volume versus baseline Tyrving: difference 0.040 (95% CI 0.006 to 0.074); adding+} Tyrving {+to volume: 0.023 (95% CI 0.007 to 0.038); volume versus Tyrving with its within-baseline trajectory (subsample with Tyrving at+} both {+ages): −0.001 (95% CI −0.042 to 0.039); volume versus+} the {+within-event percentile at+} the {+meet: 0.051 (95% CI 0.019 to 0.083). Differences+} with {+corrected 95% CIs: Supplementary Table S27.+}

---

## Table S16. Cox time-to-cessation with structural controls (baseline-only predictors)

| Covariate | HR | 95% CI | p |
|---|---|---|---|
| Female | {+1.23+} | {+[1.12, 1.36]+} | {+< .001+} |
| Tyrving (z) | {+0.81+} | {+[0.77, 0.85]+} | {+< .001+} |
| {+HHI, ages 13–14 (z)+} | {+0.91+} | {+[0.87, 0.96]+} | < .001 |
| **Pre-milestone volume (z)** | {+0.65+} | {+[0.61, 0.69]+} | < .001 |
| Q1 born | {+1.12+} | {+[1.01, 1.24]+} | {+.040+} |
| Q4 born | {+0.86+} | {+[0.75, 0.98]+} | {+.026+} |
| Region: Østlandet | {+0.94+} | {+[0.84, 1.06]+} | {+.310+} |
| Region: Midt-Norge | {+1.01+} | {+[0.88, 1.15]+} | {+.932+} |
| Club size (z) | 1.02 | {+[0.97, 1.08]+} | {+.344+} |

*Note.* n = {+1,908 (1,747 events);+} C-index = {+0.691; time zero at the end of the age-14 season (Supplementary Table S10 note).+} Higher HHI (specialization) associated with lower dropout hazard.

---

## Table S17. Cross-validated AUC for nested predictor subsets predicting senior retention

| Predictor set | n features | n | AUC (logistic) |
|---|---|---|---|
| Baseline only (sex + Tyrving best) | 2 | {+1,501+} | {+0.66 (±0.02)+} |
| Specialization only (sex + HHI + n categories) | 3 | {+1,501+} | {+0.60 (±0.02)+} |
| Volume only (sex + meets ages 13–16) | 5 | {+1,501+} | {+0.83 (±0.01)+} |
| {+Volume + specialization (behavioral, ages 13–16)+} | 8 | {+1,501+} | {+0.82 (±0.02)+} |
| Full model (all 22 predictors) | 22 | {+1,501+} | {+0.83 (±0.02)+} |

*Note.* Descriptive comparison on the subsample with complete data on all 22 candidate predictors (n = {+1,501;+} see Supplementary Table S12). This table includes post-baseline behavioral predictors (ages 15–16) and therefore overlaps with the early portion of the at-risk window; AUCs are descriptive rather than ordinary prospective prediction quantities. {+The complete-case requirement (which includes HHI at age 15) keeps only athletes who competed at 15 (senior retention 22.4% vs. 16.3% in the cohort), so every row, including the baseline-only one, is computed on a sample selected on later participation.+}

---

## Table S18. Specialization-vs-performance confound check: does HHI proxy for performance in the primary event category?

| Model | Covariate | OR | 95% CI | p |
|---|---|---|---|---|
| **A**: Primary L4 (with tyrving_best) | Female | {+0.56+} | {+[0.43, 0.72]+} | < .001 |
| {+n = 2,136+} | {+Tyrving (z)+} | {+1.75+} | {+[1.47, 2.08]+} | {+< .001+} |
|  | **{+HHI, ages 13–14 (z)+}** | **{+1.18+}** | **{+[1.04, 1.34]+}** | **{+.012+}** |
|  | Pre-milestone volume (z) | {+2.04+} | {+[1.80, 2.32]+} | < .001 |
| **B**: + Tyrving in primary category | Female | {+0.56+} | {+[0.43, 0.72]+} | {+< .001+} |
| {+n = 2,135+} | {+Tyrving (z)+} | {+1.17+} | {+[0.92, 1.49]+} | {+.193+} |
|  | **{+HHI, ages 13–14 (z)+}** | **{+1.07+}** | **{+[0.94, 1.23]+}** | **{+.302+}** |
|  | Pre-milestone volume (z) | {+1.84+} | {+[1.61, 2.11]+} | < .001 |
|  | Tyrving main category (z) | {+1.80+} | {+[1.36, 2.38]+} | {+< .001+} |
| **C**: Tyrving main replaces tyrving_best | Female | {+0.56+} | {+[0.44, 0.73]+} | {+< .001+} |
| {+n = 2,135+} | Tyrving main category (z) | {+2.07+} | {+[1.70, 2.51]+} | {+< .001+} |
|  | **{+HHI, ages 13–14 (z)+}** | **{+1.06+}** | **{+[0.93, 1.21]+}** | **{+.390+}** |
|  | Pre-milestone volume (z) | {+1.83+} | {+[1.60, 2.09]+} | < .001 |

*Note.* Correlations: HHI vs. Tyrving best, r = {+0.02;+} HHI vs. Tyrving main category, r = {+0.12;+} Tyrving best vs. Tyrving main, r = {+0.78.+} The HHI {+coefficient+} is {+not stable+} across the three specifications (OR {+1.06–1.18; 1.07 [0.94, 1.23] once main-category+} Tyrving is {+added); main-category Tyrving has an independent+} association {+(OR 1.80–2.07).+}

---

## Table S19. Exit-aligned volume trajectories among dropouts

| Quantity | Value | n |
|---|---|---|
| Aligned volume T−3 (median [IQR]) | 12 [6–18] | {+800+} |
| Aligned volume T−2 (median [IQR]) | 10 [6–16] | {+1,146+} |
| Aligned volume T−1 (median [IQR]) | 9 [5–14] | {+1,146+} |
| Aligned volume T (final season; median [IQR]) | 4 [2–8] | {+1,146+} |
| Active (>0 meets) in penultimate season | 95.2% | {+1,146+} |
| Reduced-but-nonzero penultimate season (final age ≥16) | {+73.9%+} | {+800+} |
| Penultimate season zero (gap year before final) | 6.5% | {+800+} |
| Penultimate at personal peak (abrupt profile) | {+19.6%+} | {+800+} |
| Volume in final season below personal peak | {+93.3%+} | {+1,146+} |
| Change model among active at 16: volume at 15 (per SD) | {+OR 3.04 [2.56, 3.62]+} | {+1,088+} |
| {+Change model among active at 16: change 15→16 (per SD increase)+} | {+OR 1.87 [1.60, 2.19]+} | {+1,088+} |
| {+Change model among active at 16: change 15→16 (per SD decline)+} | {+OR 0.54 [0.46, 0.63]+} | {+1,088+} |

*Note.* Each dropout's volume history aligned to their own final active season (T; last calendar year with ≥2 results); dropouts with final seasons at ages 15–19 (n = {+1,146;+} T−3 observable only where final age ≥16). "Reduced-but-nonzero" = penultimate volume above zero but below the athlete's earlier personal peak. The change model is a logistic regression for senior status among athletes with ≥2 results at age 16 (CV-AUC = {+0.762; change = volume at 16 minus volume at 15);+} all predictors are measured by 16, so neither predictor can be the exit itself. See Supplementary Methods S-M6.

---

## Table S20. HHI count-dependence stress tests

| Model | n | HHI OR [95% CI] | Volume OR |
|---|---|---|---|
| Primary L4 (all) | {+2,136+} | {+1.18 [1.04, 1.34]+} | {+2.04+} |
| {+≥ 5 results at ages 13-14+} | {+2,053+} | {+1.17 [1.04, 1.33]+} | {+2.03+} |
| {+≥ 8 results at ages 13-14+} | {+1,905+} | {+1.17 [1.03, 1.32]+} | {+2.00+} |
| {+Finite-sample-corrected HHI* = (HHI - 1/n)/(1 - 1/n)+} | {+2,124+} | {+1.20 [1.05, 1.35]+} | {+2.01+} |

*Note.* {+HHI computed from results at ages 13–14.+} Spearman correlations: HHI vs. result count {+at ages 13–14+} ρ = {+-0.40;+} HHI vs. pre-milestone volume ρ = {+-0.22.+} The HHI–retention association is unchanged under count restrictions and the corrected index; it is not a small-count artifact. See Supplementary Methods S-M8.

---

## Table S21. {+Missing data: complete-case and multiple-imputation estimates and predictive performance+}

| {+Data / model+} | n | Volume OR [95% CI] | HHI OR [95% CI] | {+Tyrving OR [95% CI]+} | {+CV-AUC+} |
|---|---|---|---|---|---|
| {+Corrected data: complete case (primary)+} | {+2,136+} | {+2.04 [1.80, 2.32]+} | {+1.18 [1.04, 1.34]+} | {+1.75 [1.47, 2.08]+} | {+0.767+} |
| {+Corrected data: multiple imputation (m = 20)+} | {+2,136+} | {+2.04 [1.80, 2.32]+} | {+1.18 [1.04, 1.34]+} | {+1.75 [1.47, 2.08]+} |  |
| {+Submitted data: complete case+} | {+1,704+} | {+2.40 [2.08, 2.76]+} | {+1.36 [1.17, 1.57]+} | {+1.12 [0.96, 1.30]+} | {+0.753+} |
| {+Submitted data: MI (m = 20), outcome in imputation model+} | {+2,099+} | {+2.34 [2.07, 2.66]+} | {+1.32 [1.16, 1.49]+} | {+1.12 [0.97, 1.29]+} | {+0.751 (0.745–0.755)+} |
| {+Submitted data: MI with auxiliary variables (baseline event category, region, cohort, club size, result count)+} | {+2,099+} | {+2.34 [2.06, 2.65]+} | {+1.31 [1.16, 1.49]+} | {+1.14 [0.99, 1.31]+} |  |

*Note.* {+In the corrected data no sex-known athlete lacks a baseline score, so imputation and complete-case analysis coincide. The lower rows repeat the analysis on the submitted analysis file (n = 2,123; Tyrving missing for 395 sex-known athletes, 18.8%): chained-equation imputation (m = 20) with the outcome in the imputation model leaves the estimates essentially unchanged, and predictive performance with imputation fitted inside each training fold (outcome excluded) equals the complete-case CV-AUC. CV-AUCs use 20 cross-validation splits (with imputation, one per imputed dataset), so the submitted complete-case value differs slightly from that of the submission's single split (0.751; Supplementary Table S26). Details: Supplementary Methods S-M3.+}

---

## Table S22. Club-level analyses

| Quantity | Value | n |
|---|---|---|
| ICC of pre-milestone volume across baseline clubs | {+0.27+} | {+2,136 athletes, 287 clubs+} |
| Volume OR, primary (no club terms) | {+2.04+} | {+2,136+} |
| {+Volume OR, club random intercepts (maximum likelihood)+} | {+2.07 [1.80, 2.37]+} | {+2,136+} |
| {+HHI OR, club random intercepts (maximum likelihood)+} | {+1.17 [1.03, 1.34]+} | {+2,136+} |
| {+SD of the club intercepts (log-odds); likelihood-ratio test of no club variation+} | {+0.17; p = .311+} | {+2,136+} |
| {+Volume OR, club-clustered standard errors+} | {+2.04 [1.75, 2.39]+} | {+2,136+} |
| {+Volume OR, population-averaged GEE (exchangeable within club)+} | {+2.03 [1.74, 2.38]; within-club correlation −0.003+} | {+2,136+} |
| {+CV-AUC, folds grouped by club (20 repeats)+} | {+0.766 [0.735, 0.797]+} | {+2,136+} |

*Note.* A quarter of the variance in pre-milestone volume lies between clubs, but the within-club volume effect is, if anything, slightly larger than the pooled {+estimate, club-clustered and population-averaged estimates give the same odds ratio, the clubs differ little in retention itself, and discrimination is unchanged when validation clubs are held out of fitting. The random-intercept model is fitted by maximum likelihood (club intercepts integrated out with 40-node Gauss–Hermite quadrature; Wald intervals); the submission used a variational Bayes approximation, which understates uncertainty:+} the association is not a club-supply artifact. See Supplementary Methods S-M7.

---

## Table S23. Calibration of the primary model (cross-validated)

| Metric | Value |
|---|---|
| Calibration slope | {+0.98+} |
| {+Calibration-in-the-large+} | {+0.00+} |
| Brier score | {+0.117+} |
| n | {+2,136+} |

*Note.* {+Out-of-fold predictions averaged over 20 repeats of stratified 5-fold cross-validation; calibration-in-the-large is the intercept of a logistic model with the linear predictor as offset.+}

---

## Table S24. Fixed-window outcome (ages 20–22)

| Outcome | Prevalence | Cohort A | Cohort B | Volume OR [95% CI] | CV-AUC | n |
|---|---|---|---|---|---|---|
| ≥2 results in any season at ages 20–22 | 0.158 | 0.153 | {+0.165+} | {+2.08 [1.83, 2.37]+} | {+0.773+} | {+2,136+} |

*Note.* This outcome window is fully observable for every athlete in both cohorts, removing the follow-up asymmetry of the open-ended senior definition; results are near-identical to the primary model. {+Prevalences are for all 2,138 athletes; the model uses the 2,136 with complete data. CV-AUC from a single stratified 5-fold split, as in the original analysis.+}

---

## Table S25. Included versus excluded athletes (complete-case comparison)

| Variable | Included (complete case) | Excluded (any missing) |
|---|---|---|
| Senior retention | {+16.2%+} | {+50.0%+} |
| Female | {+52.9%+} | {+— (2 of 2 have no registered sex)+} |
| Pre-milestone volume (mean meets) | 20.5 | {+12.5+} |
| {+HHI, ages 13–14 (mean)+} | {+0.46+} | {+0.40+} |

*Note.* n = {+2,136+} included, {+2 excluded (2 without registered sex, 0 without a baseline Tyrving score). The excluded+} athletes {+are too few to affect+} the {+estimates; multiple imputation gives identical results (Supplementary+} Table {+S21).+}

---

## Table S26. {+Cross-validation procedure: standardization inside folds and club-grouped folds+}

| {+Procedure+} | {+n+} | {+CV-AUC+} | {+Calibration slope+} | {+Calibration-in-the-large+} | {+Brier+} |
|---|---|---|---|---|---|
| {+Submitted data; standardized on full data before CV (as submitted)+} | {+1,704+} | {+0.751+} | {+0.96+} | {+0.00+} | {+0.122+} |
| {+Submitted data; standardized within training folds+} | {+1,704+} | {+0.751+} | {+0.96+} | {+0.00+} | {+0.122+} |
| {+Corrected data; athlete-level stratified 5-fold, 20 repeats+} | {+2,136+} | {+0.767 [0.737, 0.797]; repeat range 0.762–0.769+} | {+0.98+} | {+0.00+} | {+0.117+} |
| {+Corrected data; club-grouped stratified 5-fold, 20 repeats+} | {+2,136+} | {+0.766 [0.735, 0.797]; repeat range 0.761–0.772+} | {+0.97+} | {+0.00+} | {+0.117+} |

{+*Note.* Rows 1–2 use the variables and the single 5-fold split (seed 42) of the original submission. Because the logistic models are unpenalized, standardizing inside the training folds is an affine re-parameterization that leaves out-of-fold predictions unchanged; the two procedures therefore agree to the third decimal. Rows 3–4 use the corrected data and revised variables (HHI from ages 13–14; complete Tyrving scoring) with 20 repeats; club-grouped folds keep every baseline club (287 clubs; largest 65 athletes) entirely in either the training or the validation fold. Calibration-in-the-large is the intercept of a logistic model with the linear predictor as offset; the submitted Table S23 reported instead the intercept estimated jointly with the slope (−0.06), a different quantity.+}

---

## Table S27. {+Differences in cross-validated AUC between models (paired, identical folds)+}

| {+Comparison (B vs. A)+} | {+n+} | {+CV-AUC A+} | {+CV-AUC B+} | {+Difference+} | {+95% CI+} | {+p+} |
|---|---|---|---|---|---|---|
| {+Sex + Tyrving vs. sex+} | {+2,136+} | {+0.535+} | {+0.700+} | {++0.165+} | {+[+0.127, +0.203]+} | {+< .001+} |
| {++ HHI vs. sex + Tyrving+} | {+2,136+} | {+0.700+} | {+0.698+} | {+−0.002+} | {+[−0.005, +0.001]+} | {+.173+} |
| {++ volume vs. sex + Tyrving + HHI (L4 vs. L3)+} | {+2,136+} | {+0.698+} | {+0.767+} | {++0.069+} | {+[+0.047, +0.091]+} | {+< .001+} |
| {+Sex + volume vs. sex + Tyrving (time-aligned)+} | {+2,136+} | {+0.700+} | {+0.740+} | {++0.040+} | {+[+0.006, +0.074]+} | {+.022+} |
| {+Sex + Tyrving + volume vs. sex + volume+} | {+2,136+} | {+0.740+} | {+0.763+} | {++0.023+} | {+[+0.007, +0.038]+} | {+.005+} |
| {+Full L4 vs. sex + volume+} | {+2,136+} | {+0.740+} | {+0.767+} | {++0.026+} | {+[+0.008, +0.044]+} | {+.004+} |
| {+Sex + volume vs. sex + Tyrving + Tyrving change 13–14+} | {+1,721+} | {+0.737+} | {+0.736+} | {+−0.001+} | {+[−0.042, +0.039]+} | {+.943+} |
| {+Sex + volume vs. sex + within-event percentile at the meet+} | {+2,136+} | {+0.689+} | {+0.740+} | {++0.051+} | {+[+0.019, +0.083]+} | {+.002+} |
| {+Sex + percentile + volume vs. sex + volume+} | {+2,136+} | {+0.740+} | {+0.757+} | {++0.017+} | {+[+0.003, +0.031]+} | {+.020+} |
| {+Sex + Tyrving vs. sex + within-event percentile at the meet+} | {+2,136+} | {+0.689+} | {+0.700+} | {++0.011+} | {+[−0.006, +0.028]+} | {+.216+} |
| {++ HHI vs. sex + Tyrving + volume (L4 vs. L4 without HHI)+} | {+2,136+} | {+0.763+} | {+0.767+} | {++0.004+} | {+[−0.003, +0.010]+} | {+.277+} |

{+*Note.* Both models are fitted and validated on the same 100 folds (stratified 5-fold, 20 repeats); the difference is the mean of the 100 fold-level differences, with 95% CI and p from the corrected resampled t-statistic (Nadeau & Bengio, 2003), which inflates the variance for the overlap between training sets.+}

---

## Table S28. {+Within-athlete decline before exit: athlete and age fixed-effects model+}

| {+Outcome / sample+} | {+Season+} | {+Estimate+} | {+95% CI+} | {+Effect+} | {+p+} | {+Athletes+} | {+Athlete-seasons+} |
|---|---|---|---|---|---|---|---|
| {+log(1 + meets), all athletes+} | {+T−3+} | {+−0.069+} | {+[−0.136, −0.002]+} | {+−7%+} | {+.044+} | {+1,909+} | {+8,490+} |
| {+log(1 + meets), all athletes+} | {+T−2+} | {+−0.132+} | {+[−0.214, −0.050]+} | {+−12%+} | {+.002+} | {+1,909+} | {+8,490+} |
| {+log(1 + meets), all athletes+} | {+T−1+} | {+−0.267+} | {+[−0.365, −0.169]+} | {+−23%+} | {+< .001+} | {+1,909+} | {+8,490+} |
| {+log(1 + meets), all athletes+} | {+T+} | {+−0.640+} | {+[−0.751, −0.530]+} | {+−47%+} | {+< .001+} | {+1,909+} | {+8,490+} |
| {+meets (linear), all athletes+} | {+T−3+} | {+−0.432+} | {+[−1.093, 0.229]+} | {+−0.4 meets+} | {+.200+} | {+1,909+} | {+8,490+} |
| {+meets (linear), all athletes+} | {+T−2+} | {+−1.084+} | {+[−1.929, −0.239]+} | {+−1.1 meets+} | {+.012+} | {+1,909+} | {+8,490+} |
| {+meets (linear), all athletes+} | {+T−1+} | {+−2.659+} | {+[−3.696, −1.622]+} | {+−2.7 meets+} | {+< .001+} | {+1,909+} | {+8,490+} |
| {+meets (linear), all athletes+} | {+T+} | {+−6.381+} | {+[−7.594, −5.168]+} | {+−6.4 meets+} | {+< .001+} | {+1,909+} | {+8,490+} |
| {+log(1 + meets), exits at ages 17–19 only (reference seasons observed)+} | {+T−3+} | {+−0.039+} | {+[−0.114, 0.036]+} | {+−4%+} | {+.305+} | {+693+} | {+4,244+} |
| {+log(1 + meets), exits at ages 17–19 only (reference seasons observed)+} | {+T−2+} | {+−0.089+} | {+[−0.189, 0.011]+} | {+−9%+} | {+.081+} | {+693+} | {+4,244+} |
| {+log(1 + meets), exits at ages 17–19 only (reference seasons observed)+} | {+T−1+} | {+−0.296+} | {+[−0.419, −0.172]+} | {+−26%+} | {+< .001+} | {+693+} | {+4,244+} |
| {+log(1 + meets), exits at ages 17–19 only (reference seasons observed)+} | {+T+} | {+−0.590+} | {+[−0.720, −0.459]+} | {+−45%+} | {+< .001+} | {+693+} | {+4,244+} |

{+*Note.* Linear model with athlete fixed effects (within transformation), age fixed effects (ages 13–19), and indicators for the final active season (T) and the three preceding seasons of athletes whose exit was observed (final active season before 2024); seasons after the final active season are excluded, and the seasons of athletes still active, or more than three seasons before exit, form the reference. Estimates are deviations from the athlete's own reference-period volume net of the common age profile; for log(1 + meets) the effect column gives 100 × (exp(β) − 1). Standard errors are cluster-robust by athlete. The decline steepens towards exit (Wald test T−1 = T−3, p < .001). The final-season estimate is partly mechanical (the last season with ≥2 results is often a partial season). See Supplementary Methods S-M6 and Supplementary Figure S5.+}

---

## Table S29. {+Early-warning thresholds derived in one birth cohort and validated in the other+}

| {+Analysis+} | {+Threshold (meets)+} | {+n+} | {+Flagged %+} | {+Sensitivity+} | {+Specificity+} | {+PPV+} | {+Retention, flagged+} | {+Retention, unflagged+} |
|---|---|---|---|---|---|---|---|---|
| {+Lowest-quartile rule derived in Cohort A+} | {+< 10+} | {+1,309+} | {+28.1+} | {+0.31 [0.29, 0.34]+} | {+0.89 [0.85, 0.93]+} | {+0.94 [0.92, 0.96]+} | {+6.0% [3.7, 8.5]+} | {+19.7% [17.1, 22.2]+} |
| {+Cohort-A lowest-quartile cut-off applied to Cohort B (validation)+} | {+< 10+} | {+829+} | {+26.1+} | {+0.30 [0.27, 0.33]+} | {+0.93 [0.89, 0.97]+} | {+0.95 [0.92, 0.98]+} | {+4.6% [2.0, 7.5]+} | {+21.4% [18.2, 24.8]+} |
| {+Lowest-quartile rule derived in Cohort B+} | {+< 10+} | {+829+} | {+26.1+} | {+0.30 [0.27, 0.33]+} | {+0.93 [0.89, 0.97]+} | {+0.95 [0.92, 0.98]+} | {+4.6% [2.0, 7.5]+} | {+21.4% [18.2, 24.8]+} |
| {+Cohort-B lowest-quartile cut-off applied to Cohort A (validation)+} | {+< 10+} | {+1,309+} | {+28.1+} | {+0.31 [0.29, 0.34]+} | {+0.89 [0.85, 0.93]+} | {+0.94 [0.92, 0.96]+} | {+6.0% [3.7, 8.5]+} | {+19.7% [17.1, 22.2]+} |
| {+Derived in Cohort A (Youden’s J)+} | {+< 21+} | {+1,309+} | {+62.0+} | {+0.68 [0.65, 0.71]+} | {+0.70 [0.63, 0.76]+} | {+0.92 [0.90, 0.94]+} | {+7.8% [5.9, 9.6]+} | {+29.0% [25.0, 32.9]+} |
| {+Cohort-A threshold applied to Cohort B (validation)+} | {+< 21+} | {+829+} | {+55.6+} | {+0.61 [0.57, 0.64]+} | {+0.70 [0.63, 0.78]+} | {+0.91 [0.88, 0.93]+} | {+9.1% [6.6, 11.8]+} | {+26.9% [22.5, 31.4]+} |
| {+Derived in Cohort B (Youden’s J)+} | {+< 29+} | {+829+} | {+71.4+} | {+0.77 [0.74, 0.80]+} | {+0.57 [0.49, 0.65]+} | {+0.90 [0.87, 0.92]+} | {+10.3% [7.8, 12.7]+} | {+33.8% [27.5, 39.6]+} |
| {+Cohort-B threshold applied to Cohort A (validation)+} | {+< 29+} | {+1,309+} | {+76.7+} | {+0.82 [0.80, 0.84]+} | {+0.51 [0.45, 0.58]+} | {+0.90 [0.88, 0.92]+} | {+10.1% [8.2, 11.9]+} | {+34.8% [29.6, 40.3]+} |
| {+Candidate < 10 meets, Cohort A+} | {+< 10+} | {+1,309+} | {+28.1+} | {+0.31 [0.29, 0.34]+} | {+0.89 [0.85, 0.93]+} | {+0.94 [0.92, 0.96]+} | {+6.0% [3.7, 8.5]+} | {+19.7% [17.1, 22.2]+} |
| {+Candidate < 10 meets, Cohort B+} | {+< 10+} | {+829+} | {+26.1+} | {+0.30 [0.27, 0.33]+} | {+0.93 [0.89, 0.97]+} | {+0.95 [0.92, 0.98]+} | {+4.6% [2.0, 7.5]+} | {+21.4% [18.2, 24.8]+} |

{+*Note.* Cohort A: births 1998–2000; Cohort B: births 2001–2002. Lowest-quartile rule: flag athletes at or below the 25th percentile of pre-milestone volume in the derivation cohort (≤ 9 meets in Cohort A, i.e. < 10; ≤ 9 in Cohort B, i.e. < 10). Youden’s J maximizes sensitivity + specificity − 1 over cut-offs 2–40. Brackets: 2,000-replicate bootstrap 95% CIs within the evaluation cohort; rows with the same cohort and cut-off are one computation (the lowest-quartile cut-off is < 10 in both cohorts, so the quartile rows and the candidate rows coincide). Sensitivity and PPV refer to identifying athletes who did not retain senior activity.+}

---

## Table S30. {+Temporary gaps, returns, and alternative event definitions (baseline-only Cox model)+}

| {+Event definition+} | {+n+} | {+Events+} | {+Volume HR per SD [95% CI]+} | {+HHI HR per SD+} | {+C-index+} |
|---|---|---|---|---|---|
| {+Final active season (primary; censored if active 2024+)+} | {+1,908+} | {+1,747+} | {+0.65 [0.62, 0.69]+} | {+0.91+} | {+0.690+} |
| {+First sustained exit (active season followed by ≥2 inactive seasons)+} | {+1,908+} | {+1,768+} | {+0.62 [0.59, 0.66]+} | {+0.90+} | {+0.698+} |
| {+First inactive season (any one-season gap ends the spell)+} | {+1,867+} | {+1,792+} | {+0.62 [0.58, 0.66]+} | {+0.92+} | {+0.707+} |

{+*Note.* All models include sex, Tyrving, HHI (ages 13–14), and pre-milestone volume. An active season is a calendar year with ≥2 results. 11.8% of athletes (253) had at least one inactive season followed by a return, 4.4% (95) a gap of two or more seasons followed by a return, and 1.8% a gap of three or more. Of 1,782 athletes with an active season in 2019 or earlier followed by two missed seasons, 4.4% ever returned (at least four later seasons observable). Under the primary definition such returns are part of a continuing career; the alternative definitions instead end the spell at the first two-season gap or at the first inactive season (censored if no such pattern is observed through 2025). The first-inactive-season definition also requires an active season at 14, the season before time zero, which explains its smaller n.+}

---

## Table S31. {+The cohort within the register population of the same birth years+}

| {+Group+} | {+n+} | {+Female %+} | {+Meets at 13–14, median [IQR]+} | {+≥10 meets at 13–14 (%)+} | {+Senior retention %+} | {+Volume OR per 10 meets+} | {+CV-AUC (sex + volume)+} |
|---|---|---|---|---|---|---|---|
| {+Cohort (attended the baseline meet)+} | {+2,138+} | {+52.9+} | {+17 [9–29]+} | {+72.5+} | {+15.9+} | {+1.70 [1.58, 1.84]+} | {+0.740+} |
| {+Not in cohort (same birth years, ≥1 result at 13–14)+} | {+5,128+} | {+52.9+} | {+2 [1–4]+} | {+7.4+} | {+1.7+} | {+2.17 [1.70, 2.77]+} | {+0.680+} |
| {+All athletes born 1998–2002 with ≥1 result at 13–14+} | {+7,266+} | {+52.9+} | {+3 [1–10]+} | {+26.5+} | {+5.8+} | {+2.15 [2.02, 2.29]+} | {+0.835+} |

{+*Note.* All athletes born 1998–2002 with at least one registered result at ages 13–14, from the register as it stood at the data extraction (rows registered by 18 May 2026; results through 2025), with cohort membership defined as in the main analyses. The cohort comprises 29% of these athletes but 80% of those with ten or more meets at 13–14 and 80% of the 424 who later had an active senior season. Meets are competition days, as in the main analyses; for cohort members the register counts reproduce the analysis data closely (mean 20.4 vs. 20.5 meets; senior retention 15.9% vs. 16.3%), the small differences reflecting rows re-registered after the extraction. Senior retention: ≥2 results in a calendar year at age 20 or later.+}

---

## Table S32. {+Senior retention by baseline performance quartile and pre-milestone volume+}

| {+Baseline Tyrving quartile+} | {+Retention, volume above median+} | {+Retention, volume at or below median+} |
|---|---|---|
| {+Q1 (lowest)+} | {+15.8% (n = 152)+} | {+3.9% (n = 382)+} |
| {+Q2+} | {+18.1% (n = 221)+} | {+6.0% (n = 315)+} |
| {+Q3+} | {+20.8% (n = 269)+} | {+10.6% (n = 263)+} |
| {+Q4 (highest)+} | {+38.1% (n = 378)+} | {+13.5% (n = 156)+} |

{+*Note.* Median pre-milestone volume = 17 meets. Above-median volume is associated with higher senior retention in every performance quartile.+}

---
