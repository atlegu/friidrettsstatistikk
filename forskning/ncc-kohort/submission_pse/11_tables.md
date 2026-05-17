# Tables

(Submitted as editable text; in the final Word manuscript, each table on its own page after the references. Supplementary Tables S1–S7 follow as supplementary material.)

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
| Median competitions at age 15–16 | 7 | 9 | 8 |

*Note.* "Active" indicates ≥2 registered competition results in any calendar year at the specified age. Tyrving points = Norwegian Athletics Federation's age-norm score where 1,000 = "excellent" for that event × sex × age combination.

---

## Table 2. Competition volume trajectory by senior-retention status (median competitions per year and IQR)

| Group | N | Age 13 | Age 14 | Age 15 | Age 16 | Age 17 | Age 18 |
|---|---|---|---|---|---|---|---|
| Senior retainers (active age ≥20) | 348 | 13 [6–21] | 17 [10–25] | 19 [11–27] | 18 [10–26] | 17 [10–24] | 14 [7–20] |
| Dropouts (last active age <20) | 1,775 | 8 [4–13] | 8 [3–14] | 3 [0–11] | 0 [0–7] | 0 [0–2] | 0 [0–0] |

*Note.* Values are median number of meets per year [IQR]. Trajectories diverge sharply from age 15.

---

## Table 3. Stepwise Cox proportional hazards models for time to dropout

| Model | Covariate | HR | 95% CI | p | C-index | n |
|---|---|---|---|---|---|---|
| M1: Sex only | Female | 1.04 | [0.95, 1.14] | .352 | 0.498 | 2,123 |
| M2: + Performance | Female | 1.10 | [1.00, 1.22] | .052 | 0.574 | 1,704 |
|  | Tyrving (z) | 0.86 | [0.82, 0.90] | < .001 |  |  |
| M3: + Specialization | Female | 1.10 | [1.00, 1.22] | .059 | 0.573 | 1,704 |
|  | Tyrving (z) | 0.86 | [0.82, 0.90] | < .001 |  |  |
|  | HHI early (z) | 0.98 | [0.93, 1.03] | .455 |  |  |
| M4: + Volume at milestone | Female | 1.09 | [0.98, 1.20] | .109 | **0.846** | 1,704 |
|  | Tyrving (z) | 1.04 | [0.99, 1.09] | .169 |  |  |
|  | HHI early (z) | 0.95 | [0.90, 1.00] | .061 |  |  |
|  | **Volume at age 15–16 (z)** | **0.35** | **[0.33, 0.38]** | **< .001** |  |  |
| M5: + Championship types | Female | 1.12 | [1.02, 1.24] | .025 | 0.842 | 1,704 |
|  | Tyrving (z) | 1.05 | [1.00, 1.10] | .060 |  |  |
|  | HHI early (z) | 0.95 | [0.90, 1.01] | .080 |  |  |
|  | Volume at age 15–16 (z) | 0.44 | [0.40, 0.48] | < .001 |  |  |
|  | Championship types (count, 0–4) | 0.74 | [0.69, 0.80] | < .001 |  |  |

*Note.* HRs are per one-SD increase for standardized covariates and per unit for the count of championship types. The volume-at-milestone covariate produces the largest single-step C-index gain (0.573 → 0.846). Schoenfeld residual tests detected proportional-hazards violations for vol_milepael, HHI early, and championship types; period-specific HRs are given in Table 4.

---

## Table 4. Time-varying hazard ratios across follow-up periods (full Cox model, period-specific)

| Covariate | Years 0–3 (age 13–17) | Years 3–6 (age 16–19) | Years 6+ (age 19+) |
|---|---|---|---|
| **Volume at age 15–16 (per SD)** | **0.14 [0.11, 0.16]** | **0.69 [0.60, 0.79]** | 0.96 [0.77, 1.19] |
| Championship types (count) | 0.61 [0.55, 0.69] | 0.88 [0.79, 0.99] | 0.97 [0.78, 1.21] |
| Tyrving (z) | 1.07 [0.99, 1.15] | 0.92 [0.84, 1.01] | 0.94 [0.78, 1.13] |
| HHI early (z) | 0.97 [0.91, 1.05] | 0.93 [0.85, 1.02] | 1.02 [0.85, 1.21] |
| Female | 1.16 [1.02, 1.31] | 1.06 [0.91, 1.23] | 1.09 [0.85, 1.39] |
| n at risk in interval | 1,704 | 669 | 270 |
| events in interval | 1,035 | 399 | 136 |
| C-index | 0.894 | 0.661 | 0.582 |

*Note.* The dominant predictor — competition volume at age 15–16 — is highly protective in the first three years after baseline (when most dropout occurs), moderately protective in years 3–6 (the transition to junior age), and indistinguishable from null in years 6+ (athletes who have survived the junior transition). This pattern is consistent with the substantive interpretation that the behavioral signal predicts proximal disengagement.

---

## Table 5. Random forest variable importance (top 15) for senior retention

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

*Note.* Importances sum to 1.0 across all 22 features. Volume-based features dominate the top six positions.

---

## Table 6. Cross-validated AUC for nested predictor subsets predicting senior retention

| Predictor set | n features | n | AUC (logistic) | AUC (random forest) |
|---|---|---|---|---|
| Baseline only (sex + Tyrving best) | 2 | 1,217 | 0.59 (±0.04) | 0.58 (±0.02) |
| Specialization only (sex + HHI + n categories) | 3 | 1,217 | 0.60 (±0.06) | 0.57 (±0.05) |
| Volume only (sex + meets ages 13–16) | 5 | 1,217 | **0.82** (±0.03) | 0.80 (±0.03) |
| Volume + specialization (pre-baseline behavioral) | 8 | 1,217 | 0.82 (±0.03) | 0.80 (±0.03) |
| Full model (all 22 predictors) | 22 | 1,217 | 0.81 (±0.03) | 0.82 (±0.03) |

*Note.* AUC is mean ± SD across 5-fold stratified cross-validation. Behavioral volume indicators (Volume-only) achieve performance close to the full predictor set.

---

## Table 7. Cross-cohort replication: full Cox model fit separately in each birth cohort

| Cohort | n | Covariate | HR | 95% CI | p | C-index |
|---|---|---|---|---|---|---|
| 1998–2000 | 1,065 | Female | 1.19 | [1.05, 1.35] | .006 | 0.835 |
|  |  | Tyrving (z) | 1.04 | [0.97, 1.10] | .275 |  |
|  |  | HHI early (z) | 1.00 | [0.94, 1.07] | .966 |  |
|  |  | **Volume at age 15–16 (z)** | **0.49** | **[0.44, 0.55]** | **< .001** |  |
|  |  | Championship types | 0.71 | [0.65, 0.78] | < .001 |  |
| 2001–2002 | 639 | Female | 1.02 | [0.86, 1.21] | .833 | 0.852 |
|  |  | Tyrving (z) | 1.09 | [1.00, 1.19] | .047 |  |
|  |  | HHI early (z) | 0.88 | [0.80, 0.96] | .004 |  |
|  |  | **Volume at age 15–16 (z)** | **0.36** | **[0.31, 0.43]** | **< .001** |  |
|  |  | Championship types | 0.77 | [0.68, 0.87] | < .001 |  |

*Note.* The volume-at-milestone effect replicates in both cohorts at similar magnitude and direction; HHI early (specialization) is significant in Cohort B but not Cohort A; the sex effect is significant in Cohort A but not Cohort B.

---

# Supplementary Tables

## Table S1. Proportional-hazards assumption test (Schoenfeld residuals)

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

## Table S7. Subgroup analysis by sex (full Cox model)

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

*Note.* Effect directions and magnitudes are concordant across sexes; C-index = 0.843 in both subgroups.
