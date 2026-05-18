# Tables

(Submitted as editable text; in the final Word manuscript, each table on its own page after the references. Supplementary Tables S1–S17 follow as supplementary material.)

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
| Active at age 20 (%) | 15.8 | 17.3 | 16.4 |
| Still active in 2024 or later (%) | 5.8 | 10.8 | 7.7 |
| Mean Tyrving best at baseline | 666 | 666 | 666 |
| Median competitions at ages 13–14 | 8 | 9 | 8 |

*Note.* "Active" indicates ≥2 registered competition results in any calendar year at the specified age. Tyrving points = Norwegian Athletics Federation's age-norm score where 1,000 = "excellent" for that event × sex × age combination.

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
| L4: + Pre-milestone volume | Female | 0.61 | [0.46, 0.80] | < .001 | **0.751** (±0.026) | 1,704 |
|  | Tyrving (z) | 1.12 | [0.96, 1.30] | .144 |  |  |
|  | HHI early (z) | 1.36 | [1.17, 1.57] | < .001 |  |  |
|  | **Pre-milestone volume (z)** | **2.40** | **[2.08, 2.76]** | **< .001** |  |  |

*Note.* Logistic regression for binary active senior status (≥2 registered results in any year at age 20+). Predictors are observed during the baseline window (ages 13–14) only. Pre-milestone volume is the sum of distinct meets attended at ages 13 and 14. Continuous covariates are z-standardized so ORs reflect per-SD effects. Cross-validated AUC uses 5-fold stratified resampling. The pre-milestone volume coefficient is the dominant single-step gain (AUC 0.600 → 0.751). HHI becomes significant once volume is entered (mutual adjustment); the direction indicates that higher concentration in fewer event categories is associated with higher retention odds (see also Discussion 4.6).

---

## Table 4. Pull-back versus baseline heterogeneity: volume level and within-athlete change

Athletes still active at age 14 (n = 1,914).

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

| Covariate | Years 0–3 (age 13–17) | Years 3–6 (age 16–19) | Years 6+ (age 19+) |
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

| Threshold (athletes flagged if vol < ) | Flagged % | Sensitivity | Specificity | PPV | NPV |
|---|---|---|---|---|---|
| 3 meets | 2.3 | 0.03 | 1.00 | **0.96** | 0.17 |
| 5 meets | 9.3 | 0.10 | 0.97 | **0.93** | 0.18 |
| 8 meets | 19.8 | 0.22 | 0.94 | **0.94** | 0.20 |
| 10 meets | 26.4 | 0.30 | 0.92 | **0.94** | 0.22 |
| 15 meets | 43.1 | 0.48 | 0.84 | **0.93** | 0.25 |

*Note.* Calibration of pre-milestone (ages 13–14) competition volume as a prospective early-warning indicator, applicable at the end of an athlete's age-14 season — before the qualification window opens. PPV is the proportion of flagged athletes who subsequently failed to retain senior activity. PPV remains ≥ 0.93 across thresholds; the choice trades sensitivity for cohort coverage. The high PPV partly reflects the population's high base-rate of non-retention (84%); the behavioral threshold improves precision by 9–12 percentage points over base-rate prediction while providing graduated sensitivity that base-rate prediction does not.

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

## Table S3. E-values for key effects (VanderWeele & Ding, 2017)

| Effect | HR | 95% CI | E-value (point) | E-value (CI bound) |
|---|---|---|---|---|
| Volume at age 15–16 (per SD) | 0.35 | [0.33, 0.38] | 5.16 | 4.70 |
| Championship types (per type) | 0.74 | [0.69, 0.80] | 2.04 | 1.81 |
| Tyrving at baseline (per SD, M2) | 0.86 | [0.82, 0.90] | 1.60 | 1.46 |

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
| Male | 805 | Tyrving (z) | 1.07 | [0.99, 1.15] | .074 |
|  |  | HHI early (z) | 0.93 | [0.85, 1.01] | .083 |
|  |  | Volume at age 15–16 (z) | 0.42 | [0.37, 0.48] | < .001 |
|  |  | Championship types | 0.74 | [0.66, 0.83] | < .001 |
| Female | 899 | Tyrving (z) | 1.04 | [0.97, 1.11] | .306 |
|  |  | HHI early (z) | 0.99 | [0.92, 1.06] | .770 |
|  |  | Volume at age 15–16 (z) | 0.46 | [0.40, 0.52] | < .001 |
|  |  | Championship types | 0.75 | [0.67, 0.83] | < .001 |

*Note.* C-index = 0.843 in both subgroups.

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

*Note.* Athletes with ≥1 registered result at age 16, with follow-up time measured from age 16 forward.

## Table S9. Outcome-definition sensitivity (logistic regression, full model)

| Outcome | Description | Retainer n (%) | OR (pre-milestone vol per SD) | AUC |
|---|---|---|---|---|
| A | ≥1 senior-age (20+) result | 411 (19.4%) | 2.79 | 0.83 |
| B | ≥2 results in any senior-age year (primary) | 348 (16.4%) | 3.08 | 0.86 |
| C | ≥2 results in each of two distinct senior-age years | 254 (12.0%) | 2.94 | 0.87 |

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

## Table S12. Random forest variable importance (top 15) for senior retention

| Rank | Feature | Importance |
|---|---|---|
| 1 | Volume at age 16 | 0.133 |
| 2 | Composite volume at milestone (ages 15–16) | 0.126 |
| 3 | Volume at age 15 | 0.083 |
| 4 | Tyrving performance slope (ages 13–16) | 0.075 |
| 5 | Volume trend across milestone | 0.071 |
| 6 | Peak Tyrving before age 15 | 0.048 |
| 7 | HHI change (age 13–14 to 15–16) | 0.044 |
| 8 | Mean meets per year early career | 0.042 |
| 9 | Tyrving best at baseline | 0.040 |
| 10 | HHI early | 0.040 |
| 11 | Volume pre-milestone (ages 13–14) | 0.039 |
| 12 | Year-round participation sum (ages 13–16) | 0.039 |
| 13 | Volume at age 14 | 0.036 |
| 14 | Number of championship types | 0.031 |
| 15 | HHI at age 15 | 0.030 |

## Table S13. Primary logistic regression with structural controls

| Covariate | OR | 95% CI | p |
|---|---|---|---|
| Female | 0.59 | [0.45, 0.79] | < .001 |
| Tyrving (z) | 1.12 | [0.96, 1.31] | .138 |
| HHI early (z) | 1.35 | [1.16, 1.56] | < .001 |
| **Pre-milestone volume (z)** | **2.40** | **[2.08, 2.78]** | **< .001** |
| Q1 born | 0.81 | [0.59, 1.11] | .188 |
| Q4 born | 0.93 | [0.62, 1.40] | .740 |
| Region: Østlandet | 1.27 | [0.92, 1.77] | .149 |
| Region: Midt-Norge | 1.10 | [0.74, 1.64] | .626 |
| Club size (z) | 1.03 | [0.90, 1.18] | .681 |

*Note.* n = 1,704; CV-AUC = 0.740. Pre-milestone volume effect is unchanged: OR 2.40 with controls vs. 2.40 without (≤ 1% change). All structural controls non-significant.

## Table S14. Pull-back analysis details (logistic regression in athletes still active at age 14, n = 1,914)

(Same content as Table 4 above with full coefficient detail; provided as supplementary for completeness.)

## Table S15. Time-aligned behavior versus performance (5-fold CV-AUC)

| Predictor set (all ages 13–14 measurements) | n | CV-AUC |
|---|---|---|
| Sex + baseline Tyrving | 1,704 | 0.607 (±0.014) |
| Sex + pre-milestone volume | 1,704 | 0.740 (±0.024) |
| Sex + Tyrving + pre-milestone volume | 1,704 | 0.737 (±0.021) |

*Note.* Even in a fully time-aligned comparison (both predictors observed during the baseline window of ages 13–14), behavior substantially out-predicts performance.

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

| Predictor set | n features | n | AUC (logistic) | AUC (random forest) |
|---|---|---|---|---|
| Baseline only (sex + Tyrving best) | 2 | 1,217 | 0.59 (±0.04) | 0.58 (±0.02) |
| Specialization only (sex + HHI + n categories) | 3 | 1,217 | 0.60 (±0.06) | 0.57 (±0.05) |
| Volume only (sex + meets ages 13–16) | 5 | 1,217 | 0.82 (±0.03) | 0.80 (±0.03) |
| Volume + specialization (pre-baseline behavioral) | 8 | 1,217 | 0.82 (±0.03) | 0.80 (±0.03) |
| Full model (all 22 predictors) | 22 | 1,217 | 0.81 (±0.03) | 0.82 (±0.03) |

*Note.* This table includes post-baseline behavioral predictors (ages 15–16) and therefore overlaps with the early portion of the at-risk window; AUCs are descriptive rather than ordinary prospective prediction quantities.

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

*Note.* This table includes post-baseline behavioral predictors (ages 15–16) and therefore overlaps with the early portion of the at-risk window; AUCs are descriptive rather than ordinary prospective prediction quantities.
