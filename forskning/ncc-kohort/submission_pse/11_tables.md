# Tables

(Submitted as editable text; in the final Word manuscript, each table on its own page after the references. Supplementary Tables S1–S25 follow as supplementary material.)

---

## Table 1. Cohort characteristics by birth-year cohort

| Characteristic | Cohort A (1998–2000) | Cohort B (2001–2002) | All cohorts |
|---|---|---|---|
| N | 1,301 | 822 | 2,123 |
| Male (n) | 603 | 393 | 996 |
| Female (n) | 684 | 419 | 1,103 |
| Sex unknown (n) | 14 | 10 | 24 |
| Median career length (years) | 2.0 | 3.0 | 2.0 |
| Active at age 17 (%) | 41.0 | 41.6 | 41.3 |
| Ever active at age 20+ (%) | 15.8 | 17.3 | 16.4 |
| Still active in 2024 or later (%) | 5.8 | 10.8 | 7.7 |
| Mean Tyrving best at baseline | 666 | 666 | 666 |
| Median total meets, ages 13–14 (pre-milestone volume) | 16 | 19 | 17 |

*Note.* "Active at age 17" indicates ≥2 registered competition results in the athlete's age-17 calendar year; "Ever active at age 20+" is the outcome prevalence (≥2 results in any calendar year at age 20 or later). Tyrving points = the Norwegian Athletics Federation's age-norm score, where 1,000 corresponds to the published reference performance for that event × sex × age combination.

---

## Table 2. Competition volume trajectory by senior-retention status (median competitions per year and IQR)

| Group | N | Age 13 | Age 14 | Age 15 | Age 16 | Age 17 | Age 18 |
|---|---|---|---|---|---|---|---|
| Senior retainers (active age ≥20) | 348 | 13 [6–21] | 17 [10–25] | 19 [11–27] | 18 [10–26] | 17 [10–24] | 14 [7–20] |
| Dropouts (last active age <20) | 1,775 | 8 [4–13] | 8 [3–14] | 3 [0–11] | 0 [0–7] | 0 [0–2] | 0 [0–0] |

*Note.* Values are median number of meets per year [IQR]. Future retainers and future dropouts already differ at ages 13–14; the gap widens further across the age-14-to-15 transition.

---

## Table 3. Primary analysis: prospective logistic regression for active senior status (baseline-only predictors, ages 13–14)

| Model | Covariate | OR | 95% CI | p | CV-AUC | n |
|---|---|---|---|---|---|---|
| L1: Sex only | Female | 0.72 | [0.56, 0.93] | .012 | 0.541 (±0.023) | 1,704 |
| L2: + Performance | Female | 0.68 | [0.52, 0.88] | .003 | 0.607 (±0.014) | 1,704 |
|  | Tyrving (z) | 1.41 | [1.22, 1.64] | < .001 |  |  |
| L3: + Specialization | Female | 0.68 | [0.53, 0.88] | .004 | 0.600 (±0.019) | 1,704 |
|  | Tyrving (z) | 1.41 | [1.22, 1.64] | < .001 |  |  |
|  | HHI early (z) | 1.09 | [0.95, 1.24] | .238 |  |  |
| L4: + Pre-milestone volume | Female | 0.60 | [0.46, 0.80] | < .001 | **0.751** (±0.026) | 1,704 |
|  | Tyrving (z) | 1.12 | [0.96, 1.30] | .144 |  |  |
|  | HHI early (z) | 1.36 | [1.17, 1.57] | < .001 |  |  |
|  | **Pre-milestone volume (z)** | **2.40** | **[2.08, 2.76]** | **< .001** |  |  |

*Note.* Logistic regression for binary active senior status (≥2 registered results in any year at age 20+). Predictors are observed during the baseline window (ages 13–14) only. Pre-milestone volume is the sum of distinct meets attended at ages 13 and 14. Continuous covariates are z-standardized so ORs reflect per-SD effects. Cross-validated AUC uses 5-fold stratified resampling. The pre-milestone volume coefficient is the dominant single-step gain (AUC 0.600 → 0.751). HHI becomes significant once volume is entered (mutual adjustment); the direction indicates that higher concentration in fewer event categories is associated with higher retention odds (see also Discussion 4.6).

---

## Table 4. Pull-back versus baseline heterogeneity: volume level and within-athlete change

Athletes still active (≥1 result) at age 14: 1,914; fitted models are complete-case on Tyrving, n = 1,549 (Tyrving missingness is concentrated among early-inactive athletes; see Supplementary Table S12).

| Model | Covariate | OR | 95% CI | p |
|---|---|---|---|---|
| M1: Volume at age 14 only | Female | 0.61 | [0.46, 0.81] | < .001 |
|  | Tyrving (z) | 1.12 | [0.96, 1.30] | .167 |
|  | **Volume at age 14 (z)** | **2.23** | **[1.94, 2.57]** | **< .001** |
| M2: + Volume change 14→15 | Female | 0.60 | [0.44, 0.81] | < .001 |
|  | Tyrving (z) | 1.01 | [0.86, 1.19] | .882 |
|  | **Volume at age 14 (z)** | **2.79** | **[2.37, 3.28]** | **< .001** |
|  | **Volume change 14→15 (z)** | **2.44** | **[2.10, 2.83]** | **< .001** |

*Note.* Pseudo-*R*² rose from 0.113 (M1) to 0.227 (M2) — within-athlete change adds substantial information conditional on baseline level. A one-SD greater decline from age 14 to age 15 was associated with 2.4-times lower retention odds, conditional on level at age 14. Both baseline level and within-athlete pull-back contribute substantially and independently.

---

## Table 5. Time-varying hazard ratios (post-baseline Cox specification, period-specific)

| Covariate | Years 0–3 since baseline (approx. ages 13–17) | Years 3–6 (approx. ages 16–20) | Years 6+ (approx. ages 19+) |
|---|---|---|---|
| Volume at age 15–16 (per SD) | 0.14 [0.11, 0.16] | 0.69 [0.60, 0.79] | 0.96 [0.77, 1.19] |
| Championship types (count) | 0.61 [0.55, 0.69] | 0.88 [0.79, 0.99] | 0.97 [0.78, 1.21] |
| Tyrving (z) | 1.07 [0.99, 1.15] | 0.92 [0.84, 1.01] | 0.94 [0.78, 1.13] |
| HHI early (z) | 0.97 [0.91, 1.05] | 0.93 [0.85, 1.02] | 1.02 [0.85, 1.21] |
| Female | 1.16 [1.02, 1.31] | 1.06 [0.91, 1.23] | 1.09 [0.85, 1.39] |
| n at risk in interval | 1,704 | 669 | 270 |
| events in interval | 1,035 | 399 | 136 |
| C-index | 0.894 | 0.661 | 0.582 |

*Note.* Period-specific Cox estimates from the post-baseline specification with covariates measured at ages 15–16 and ≤17. The early-window HR for ages-15–16 volume partly reflects operational overlap between predictor and outcome (low milestone volume is mechanical for athletes who drop out before age 15); this estimate should be read as descriptive of the time-varying association rather than as an independent prospective effect. Substantively, the protective association attenuates across follow-up — consistent with proximal disengagement-marker interpretation.

---

## Table 6. Prospective early-warning thresholds (pre-milestone volume, ages 13–14)

| Threshold (flag if vol <) | Flagged % | Sensitivity | Specificity | PPV | NPV | Senior retention, flagged | Senior retention, unflagged |
|---|---|---|---|---|---|---|---|
| 5 meets | 9.3 | 0.10 [0.09, 0.12] | 0.96 [0.94, 0.98] | **0.93** [0.89, 0.96] | 0.17 [0.16, 0.19] | 7.1% [3.6, 11.3] | 17.3% [15.7, 19.1] |
| 8 meets | 19.8 | 0.22 [0.20, 0.24] | 0.93 [0.90, 0.96] | **0.94** [0.92, 0.96] | 0.19 [0.17, 0.21] | 5.7% [3.6, 7.9] | 19.0% [17.2, 21.0] |
| 10 meets | 26.4 | 0.30 [0.28, 0.32] | 0.91 [0.88, 0.94] | **0.94** [0.92, 0.96] | 0.20 [0.18, 0.22] | 5.7% [3.9, 7.7] | 20.2% [18.3, 22.2] |
| 15 meets | 43.1 | 0.48 [0.46, 0.50] | 0.82 [0.77, 0.85] | **0.93** [0.91, 0.95] | 0.24 [0.21, 0.26] | 7.0% [5.4, 8.7] | 23.5% [21.1, 25.9] |

*Note.* Classification performance of pre-milestone (ages 13–14) competition volume as a prospective early-warning indicator, applicable at the end of an athlete's age-14 season — before the qualification window opens. All metrics are computed on one denominator (full cohort, n = 2,123); brackets are 2,000-replicate bootstrap 95% CIs. PPV is the proportion of flagged athletes who subsequently failed to retain senior activity. The final two columns give the absolute retention contrast — at the < 10 threshold, 5.7% among flagged vs. 20.2% among unflagged athletes (a 3.5-fold difference). The high PPV partly reflects the population's 84% non-retention base rate (the threshold improves precision by ~10 percentage points over base-rate prediction), and the NPV of ≈ 0.20 means unflagged athletes are not "safe": roughly four in five of them also fail to retain. Calibration of the underlying model is reported in Supplementary Table S23.

---

## Table 7. Cross-cohort replication of the primary L4 logistic model

| Cohort | n | Covariate | OR | 95% CI | p |
|---|---|---|---|---|---|
| 1998–2000 | 1,065 | Female | 0.50 | [0.34, 0.74] | < .001 |
|  |  | Tyrving (z) | 1.14 | [0.94, 1.39] | .179 |
|  |  | HHI early (z) | 1.24 | [1.03, 1.51] | .027 |
|  |  | **Pre-milestone volume (z)** | **2.22** | **[1.86, 2.64]** | **< .001** |
| 2001–2002 | 639 | Female | 0.82 | [0.55, 1.22] | .333 |
|  |  | Tyrving (z) | 1.05 | [0.84, 1.32] | .658 |
|  |  | HHI early (z) | 1.58 | [1.25, 1.99] | < .001 |
|  |  | **Pre-milestone volume (z)** | **2.79** | **[2.17, 3.58]** | **< .001** |

*Note.* The primary baseline-only logistic model re-estimated separately within each birth-year cohort. Pre-milestone volume effect replicates in both cohorts at similar magnitude. The cohort difference in the female coefficient parallels the broader sex-effect pattern discussed in §4.5; HHI is significant in both cohorts in the same direction (higher concentration = higher retention).

---

# Supplementary Tables

## Table S1. Proportional-hazards assumption test for the post-baseline Cox specification (Schoenfeld residuals)

| Covariate | χ²₁ | p |
|---|---|---|
| Female | 2.50 | .114 |
| Tyrving (z) | 0.12 | .728 |
| HHI early (z) | 11.12 | < .001 |
| Volume at age 15–16 (z) | 220.77 | < .001 |
| Championship types | 10.89 | .001 |

## Table S2. Cluster-robust SE Cox (clustered on club)

| Covariate | HR | Robust 95% CI | p (robust) |
|---|---|---|---|
| Female | 1.12 | [0.98, 1.28] | .090 |
| Tyrving (z) | 1.05 | [0.99, 1.12] | .127 |
| HHI early (z) | 0.95 | [0.88, 1.04] | .258 |
| Volume at age 15–16 (z) | 0.44 | [0.40, 0.48] | < .001 |
| Championship types | 0.74 | [0.69, 0.80] | < .001 |

*Note.* Post-baseline specification; pooled HRs average over the strongly time-varying pattern shown in Table 5 and are descriptive.

## Table S3. E-values for the primary baseline-window volume effect (VanderWeele & Ding, 2017)

| Effect | Estimate | Approx. RR (common outcome) | E-value (point) | E-value (CI bound) |
|---|---|---|---|---|
| Pre-milestone volume, primary logistic (per SD) | OR 2.40 [2.08, 2.76] | 1.55 | 2.47 | 2.24 |
| Pre-milestone volume, baseline-only Cox (per SD) | HR 0.49 | 1.63 | 2.63 | — |

*Note.* Because the outcome is common (16.4%), the odds ratio is converted to an approximate risk ratio (RR ≈ √OR) before computing E = RR + √(RR(RR − 1)); the hazard ratio uses the common-outcome conversion (Supplementary Methods S-M5). E-values are reported for the primary baseline-window specification only; the post-baseline (ages-15–16) specification is not an admissible E-value input because it overlaps the outcome window and violates proportional hazards.

## Table S4. Sample-size sensitivity: minimum detectable HR

| Cohort | N | Events | Min. detectable HR (80% power, α = .05) |
|---|---|---|---|
| Combined | 1,704 | 1,570 | 1.07 |
| 1998–2000 | 1,065 | 1,008 | 1.09 |
| 2001–2002 | 639 | 562 | 1.12 |

## Table S5. Complete-case vs mean-imputation sensitivity

| Covariate | HR (complete case) | HR (mean imputation) |
|---|---|---|
| Female | 1.12 | 1.10 |
| Tyrving (z) | 1.05 | 1.05 |
| HHI early (z) | 0.95 | 0.96 |
| Volume at age 15–16 (z) | 0.44 | 0.45 |
| Championship types | 0.74 | 0.73 |
| n | 1,704 | 2,123 |

*Note.* Post-baseline Cox specification (descriptive; see Table 5 note). The principal missing-data sensitivity for the primary logistic model is multiple imputation, Supplementary Table S21.

## Table S6. Cox model stratified on HHI tercile (sensitivity to PH violation)

| Covariate | HR | p |
|---|---|---|
| Female | 1.12 | .026 |
| Tyrving (z) | 1.04 | .093 |
| Volume at age 15–16 (z) | 0.44 | < .001 |
| Championship types | 0.75 | < .001 |

## Table S7. Sex-stratified Cox subgroup analyses

| Sex | n | Covariate | HR | 95% CI | p |
|---|---|---|---|---|---|
| Male | 805 | Tyrving (z) | 1.13 | [1.05, 1.21] | < .001 |
|  |  | HHI early (z) | 0.95 | [0.88, 1.03] | .192 |
|  |  | Volume at age 15–16 (z) | 0.43 | [0.38, 0.50] | < .001 |
|  |  | Championship types | 0.66 | [0.59, 0.74] | < .001 |
| Female | 899 | Tyrving (z) | 0.96 | [0.89, 1.03] | .249 |
|  |  | HHI early (z) | 0.96 | [0.89, 1.03] | .263 |
|  |  | Volume at age 15–16 (z) | 0.45 | [0.39, 0.50] | < .001 |
|  |  | Championship types | 0.81 | [0.73, 0.89] | < .001 |

*Note.* Post-baseline specification (descriptive; see Table 5 note). C-index = 0.843 in both subgroups. The dominant behavioral covariate is near-identical across sexes (volume HR 0.43 vs 0.45); the Tyrving coefficient differs by sex (males 1.13, females 0.96).

## Table S8. Landmark analysis at age 16 (post-baseline Cox, n = 1,167)

| Covariate | HR | 95% CI | p |
|---|---|---|---|
| Female | 1.32 | [1.15, 1.52] | < .001 |
| Tyrving (z) | 1.01 | [0.94, 1.08] | .81 |
| HHI early (z) | 0.95 | [0.88, 1.02] | .17 |
| **Volume at age 15–16 (z)** | **0.60** | **[0.54, 0.66]** | **< .001** |
| Championship types | 0.78 | [0.71, 0.87] | < .001 |
| n complete | 960 |  |  |
| C-index | 0.735 |  |  |

*Note.* Athletes with ≥1 registered result at age 16, with follow-up time measured from age 16 forward; the age-16 share of the exposure window therefore lies at the start of the at-risk window (see Supplementary Methods S-M1). The fully contamination-free logistic analogue is the change model in main-text Section 3.5 / Supplementary Table S19.

## Table S9. Outcome-definition sensitivity (primary L4 specification, baseline-only predictors)

| Outcome | Description | Retainer n (%) | OR (pre-milestone vol per SD) | 95% CI | CV-AUC |
|---|---|---|---|---|---|
| A | ≥1 senior-age (20+) result | 411 (19.4%) | 2.29 | [2.00, 2.63] | 0.732 |
| B | ≥2 results in any senior-age year (primary) | 348 (16.4%) | 2.40 | [2.08, 2.76] | 0.751 |
| C | ≥2 results in each of two distinct senior-age years | 254 (12.0%) | 2.26 | [1.95, 2.63] | 0.753 |

*Note.* All three rows re-estimate the primary L4 model (sex, Tyrving, HHI, pre-milestone volume; n = 1,704) with the alternative outcome definitions. The volume effect is stable across definitions.

## Table S10. Lagged volume — pre-milestone (ages 13–14) alone (Cox)

| Covariate | HR | 95% CI | p |
|---|---|---|---|
| Female | 1.15 | [1.04, 1.27] | .009 |
| Tyrving (z) | 1.00 | [0.95, 1.05] | .833 |
| HHI early (z) | 0.80 | [0.76, 0.85] | < .001 |
| **Pre-milestone volume (z, ages 13–14)** | **0.50** | **[0.46, 0.53]** | **< .001** |

*Note.* n = 1,704; C-index = 0.743.

## Table S11. Sensitivity excluding zero-volume athletes (post-baseline Cox)

| Covariate | HR | 95% CI | p |
|---|---|---|---|
| Female | 1.20 | [1.07, 1.36] | .003 |
| Tyrving (z) | 1.04 | [0.98, 1.10] | .211 |
| HHI early (z) | 0.96 | [0.90, 1.02] | .200 |
| **Volume at age 15–16 (z)** | **0.51** | **[0.46, 0.56]** | **< .001** |
| Championship types | 0.80 | [0.73, 0.87] | < .001 |

*Note.* Excludes 589 athletes with vol_milestone = 0; remaining n = 1,250; C-index = 0.786.

## Table S12. Analysis sample flow

| Analysis | n | Definition |
|---|---|---|
| Total cohort | 2,123 | All included athletes |
| Sex known | 2,099 | Gender M/F registered (24 unknown; excluded from regression models, included in cohort totals and unstratified KM curves) |
| Primary logistic L1–L4 | 1,704 | Complete case on sex, Tyrving, HHI, pre-milestone volume; L1–L3 fitted on the same fixed sample for AUC comparability |
| Level-vs-change (Table 4) | 1,549 | Of 1,914 athletes with ≥1 result at age 14; complete case on Tyrving (missingness concentrated among early-inactive athletes: 25.8% vs 19.1%) |
| Contamination-free change model | 1,075 | Of 1,085 athletes with ≥2 results at age 16; complete case on sex |
| Landmark Cox at age 16 | 960 | Of 1,167 athletes with ≥1 result at age 16; complete case on model covariates |
| Multiple imputation | 2,099 | All athletes with known sex; Tyrving and HHI imputed (m = 20) |
| Specialization confound models (S18 B/C) | 1,521 / 1,632 | Complete case on primary-category Tyrving |

*Note.* One map of every analysis sample in the manuscript; each n is derivable from the row's definition.

## Table S13. Primary logistic regression with structural controls

| Covariate | OR | 95% CI | p |
|---|---|---|---|
| Female | 0.60 | [0.45, 0.79] | < .001 |
| Tyrving (z) | 1.12 | [0.96, 1.31] | .138 |
| HHI early (z) | 1.35 | [1.16, 1.56] | < .001 |
| **Pre-milestone volume (z)** | **2.40** | **[2.08, 2.78]** | **< .001** |
| Q1 born | 0.81 | [0.59, 1.11] | .188 |
| Q4 born | 0.93 | [0.62, 1.40] | .740 |
| Region: Østlandet | 1.27 | [0.92, 1.77] | .149 |
| Region: Midt-Norge | 1.10 | [0.74, 1.64] | .626 |
| Club size (z) | 1.03 | [0.90, 1.18] | .681 |

*Note.* n = 1,704; CV-AUC = 0.740. Pre-milestone volume effect is unchanged: OR 2.40 with controls vs. 2.40 without (≤ 1% change). All structural controls non-significant.

## Table S14. Pull-back analysis details (athletes with ≥1 result at age 14; complete-case n = 1,549)

| Model | Covariate | OR | 95% CI | p | Pseudo-*R*² |
|---|---|---|---|---|---|
| M1: Volume at age 14 only | Female | 0.61 | [0.46, 0.81] | < .001 | 0.113 |
|  | Tyrving (z) | 1.12 | [0.96, 1.30] | .167 |  |
|  | Volume at age 14 (z) | 2.23 | [1.94, 2.57] | < .001 |  |
| M2: + Volume change 14→15 | Female | 0.60 | [0.44, 0.81] | < .001 | 0.227 |
|  | Tyrving (z) | 1.01 | [0.86, 1.19] | .882 |  |
|  | Volume at age 14 (z) | 2.79 | [2.37, 3.28] | < .001 |  |
|  | Volume change 14→15 (z) | 2.44 | [2.10, 2.83] | < .001 |  |

*Note.* Full coefficient detail for main-text Table 4, including per-model pseudo-*R*².

## Table S15. Time-aligned behavior versus performance (5-fold CV-AUC)

| Predictor set (all ages 13–14 measurements) | n | CV-AUC |
|---|---|---|
| Sex + baseline Tyrving | 1,704 | 0.607 (±0.014) |
| Sex + Tyrving + performance trajectory (Δ13–14) | 1,350 | 0.640 |
| Sex + pre-milestone volume | 1,704 | 0.740 (±0.024) |
| Sex + Tyrving + pre-milestone volume | 1,704 | 0.737 (±0.021) |

*Note.* Even in a fully time-aligned comparison (both predictors observed during the baseline window of ages 13–14), behavior substantially out-predicts performance. The performance-trajectory row requires Tyrving scores in both the age-13 and age-14 seasons and is therefore estimated on the smaller subsample with both available (n = 1,350).

## Table S16. Cox time-to-cessation with structural controls (baseline-only predictors)

| Covariate | HR | 95% CI | p |
|---|---|---|---|
| Female | 1.16 | [1.04, 1.28] | .005 |
| Tyrving (z) | 0.99 | [0.94, 1.04] | .749 |
| HHI early (z) | 0.80 | [0.76, 0.85] | < .001 |
| **Pre-milestone volume (z)** | **0.49** | **[0.46, 0.53]** | **< .001** |
| Q1 born | 1.01 | [0.90, 1.13] | .913 |
| Q4 born | 0.88 | [0.76, 1.01] | .074 |
| Region: Østlandet | 0.93 | [0.82, 1.05] | .219 |
| Region: Midt-Norge | 1.02 | [0.89, 1.16] | .785 |
| Club size (z) | 1.02 | [0.97, 1.07] | .517 |

*Note.* n = 1,704; C-index = 0.742. Higher HHI (specialization) associated with lower dropout hazard.

## Table S17. Cross-validated AUC for nested predictor subsets predicting senior retention

| Predictor set | n features | n | AUC (logistic) |
|---|---|---|---|
| Baseline only (sex + Tyrving best) | 2 | 1,217 | 0.59 (±0.04) |
| Specialization only (sex + HHI + n categories) | 3 | 1,217 | 0.60 (±0.06) |
| Volume only (sex + meets ages 13–16) | 5 | 1,217 | 0.82 (±0.03) |
| Volume + specialization (pre-baseline behavioral) | 8 | 1,217 | 0.82 (±0.03) |
| Full model (all 22 predictors) | 22 | 1,217 | 0.81 (±0.03) |

*Note.* Descriptive comparison on the subsample with complete data on all 22 candidate predictors (n = 1,217; see Supplementary Table S12). This table includes post-baseline behavioral predictors (ages 15–16) and therefore overlaps with the early portion of the at-risk window; AUCs are descriptive rather than ordinary prospective prediction quantities.

## Table S18. Specialization-vs-performance confound check: does HHI proxy for performance in the primary event category?

Three logistic-regression specifications for active senior status. Model A is the primary L4 model (using maximum Tyrving across all baseline events). Model B adds the best Tyrving score in the athlete's *primary* baseline event category (tyrving_main). Model C replaces tyrving_best with tyrving_main.

| Model | Covariate | OR | 95% CI | p |
|---|---|---|---|---|
| **A**: Primary L4 (with tyrving_best) | Female | 0.61 | [0.46, 0.80] | < .001 |
| n = 1,704 | Tyrving best (z) | 1.12 | [0.96, 1.30] | .144 |
|  | **HHI early (z)** | **1.36** | **[1.17, 1.57]** | **< .001** |
|  | Pre-milestone volume (z) | 2.40 | [2.08, 2.76] | < .001 |
| **B**: + Tyrving in primary category | Female | 0.62 | [0.47, 0.83] | .001 |
| n = 1,521 | Tyrving best (z) | 1.08 | [0.89, 1.31] | .428 |
|  | **HHI early (z)** | **1.32** | **[1.13, 1.54]** | **< .001** |
|  | Pre-milestone volume (z) | 2.31 | [1.97, 2.71] | < .001 |
|  | Tyrving main category (z) | 1.08 | [0.89, 1.32] | .445 |
| **C**: Tyrving main replaces tyrving_best | Female | 0.62 | [0.47, 0.83] | .001 |
| n = 1,632 | Tyrving main category (z) | 1.13 | [0.96, 1.34] | .128 |
|  | **HHI early (z)** | **1.33** | **[1.15, 1.54]** | **< .001** |
|  | Pre-milestone volume (z) | 2.32 | [1.99, 2.70] | < .001 |

*Note.* Correlations: HHI early vs. Tyrving best, r = –0.07; HHI early vs. Tyrving main category, r = –0.05; Tyrving best vs. Tyrving main, r = 0.63. HHI and performance are essentially uncorrelated. The HHI effect is virtually identical across the three specifications (OR 1.32–1.36), and primary-category Tyrving is itself not a significant predictor of retention in any model. The HHI association is therefore not capturing a hidden main-event performance effect.

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
| Change model among active at 16: volume at 15 (per SD) | OR 3.04 [2.55, 3.62] | 1,075 |
| Change model among active at 16: change 15→16 (per SD) | OR 1.88 [1.60, 2.20] | 1,075 |

*Note.* Each dropout's volume history aligned to their own final active season (T; last calendar year with ≥2 results); dropouts with final seasons at ages 15–19 (n = 1,139; T−3 observable only where final age ≥16). "Reduced-but-nonzero" = penultimate volume above zero but below the athlete's earlier personal peak. The change model is a logistic regression for senior status among athletes with ≥2 results at age 16 (CV-AUC = 0.758); all predictors are measured by 16, so neither predictor can be the exit itself. See Supplementary Methods S-M6.

## Table S20. HHI count-dependence stress tests

| Model | n | HHI OR [95% CI] | Volume OR |
|---|---|---|---|
| Primary L4 (all) | 1,704 | 1.36 [1.17, 1.57] | 2.40 |
| Restricted: ≥5 results in first three seasons | 1,673 | 1.38 [1.20, 1.59] | 2.36 |
| Restricted: ≥8 results in first three seasons | 1,608 | 1.39 [1.20, 1.60] | 2.31 |
| Finite-sample-corrected HHI* = (HHI − 1/n)/(1 − 1/n) | 1,699 | 1.39 [1.20, 1.60] | 2.36 |

*Note.* Spearman correlations: HHI vs. result count in first three seasons ρ = −.38; HHI vs. pre-milestone volume ρ = −.21. The HHI–retention association is unchanged under count restrictions and the corrected index; it is not a small-count artifact. See Supplementary Methods S-M8.

## Table S21. Multiple-imputation sensitivity for the primary model

| Model | n | Volume OR [95% CI] | HHI OR [95% CI] |
|---|---|---|---|
| Complete case (primary) | 1,704 | 2.40 [2.08, 2.76] | 1.36 [1.17, 1.57] |
| Multiple imputation (m = 20, Rubin-pooled) | 2,099 | 2.34 [2.07, 2.66] | 1.32 [1.16, 1.49] |

## Table S22. Club-level analyses

| Quantity | Value | n |
|---|---|---|
| ICC of pre-milestone volume across baseline clubs | 0.25 | 1,704 athletes, 277 clubs |
| Volume OR, primary (no club terms) | 2.40 | 1,704 |
| Volume OR, club random intercepts | 2.58 [2.27, 2.93] | 1,704 |
| HHI OR, club random intercepts | 1.31 | 1,704 |

*Note.* A quarter of the variance in pre-milestone volume lies between clubs, but the within-club volume effect is, if anything, slightly larger than the pooled estimate: the association is not a club-supply artifact. See Supplementary Methods S-M7.

## Table S23. Calibration of the primary model (cross-validated)

| Metric | Value |
|---|---|
| Calibration slope | 0.96 |
| Calibration intercept | −0.06 |
| Brier score | 0.122 |
| n | 1,704 |

## Table S24. Fixed-window outcome (ages 20–22)

| Outcome | Prevalence | Cohort A | Cohort B | Volume OR [95% CI] | CV-AUC | n |
|---|---|---|---|---|---|---|
| ≥2 results in any season at ages 20–22 | 0.158 | 0.153 | 0.167 | 2.43 [2.10, 2.81] | 0.762 | 1,704 |

*Note.* This outcome window is fully observable for every athlete in both cohorts, removing the follow-up asymmetry of the open-ended senior definition; results are near-identical to the primary model.

## Table S25. Included versus excluded athletes (complete-case comparison)

| Variable | Included (complete case) | Excluded (any missing) |
|---|---|---|
| Senior retention | 16.5% | 16.0% |
| Female | 52.8% | 51.6% |
| Pre-milestone volume (mean meets) | 20.5 | 22.4 |
| HHI early (mean) | 0.43 | 0.47 |

*Note.* n = 1,704 included, 419 excluded. Excluded athletes retain at nearly the same rate and compete slightly *more* at baseline; complete-case exclusion is thus unlikely to inflate the volume effect (the multiple-imputation estimate in Table S21 confirms this).
