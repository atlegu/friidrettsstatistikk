# Supplementary Methods (Extended)

*This material accompanies the main article and expands the condensed Statistical Analysis section. Citations here appear in the supplementary reference list below.*

## S-M1. Time-to-cessation survival analysis: full specification

We modeled time from baseline to last active season using Cox proportional hazards regression with Efron's tie-handling (Efron, 1977), implemented in lifelines (Davidson-Pilon, 2019). The primary Cox specification (Supplementary Table S16) contains a baseline-only predictor set. We additionally estimated (a) a landmark analysis (van Houwelingen, 2007) restricted to athletes active at age 16 (≥1 registered result; n = 1,167, complete-case n = 960; Supplementary Table S8), and (b) a post-baseline Cox specification with ages-15–16 covariates (Table 5 gives the period-specific decomposition; Supplementary Figures S1 and S4 give its calibration and forest plots, and Supplementary Tables S6 and S10 the HHI-stratified and pre-milestone-only variants); the latter is interpreted with caveats about operational overlap between predictor and outcome windows. Two properties of the landmark analysis deserve note. First, the activity criterion at the landmark is ≥1 result (rather than the ≥2 used for active seasons) so that the conditioning event is minimal presence, not the outcome construct itself. Second, follow-up time is measured from age 16, so the age-16 portion of the exposure window (volume at ages 15–16) lies at the very start of the at-risk window; the fully contamination-free version of the same question is therefore the logistic change model of main-text Section 3.5 (level at 15 + change 15→16 among athletes active at 16, outcome at 20+), which involves no overlap at all. Proportional hazards were assessed via scaled Schoenfeld residuals (Grambsch & Therneau, 1994). Pooled hazard ratios from the post-baseline specification average over the strongly time-varying pattern shown in Table 5 and are reported descriptively; no robustness quantity (e.g., E-value) is computed from that specification. Cluster-robust standard errors on club name (Lin & Wei, 1989) and sex-stratified models are reported in Supplementary Tables S2 and S7. Kaplan–Meier curves were stratified by sex, ages-15–16 volume, and pre-17 championship types.

## S-M2. Sample size and detection capacity

Classical hypothesis-testing sample-size power calculations are not directly applicable to population-based register studies where the full cohort is observed; we treat the estimates as descriptions of this population rather than inferences to a hypothetical super-population (Berk & Freedman, 2003), while retaining confidence intervals and p-values as summaries of stochastic (process) variability in who retains. We therefore replace a-priori power with a detection-capacity analysis: given the observed event count, what is the smallest effect size the design could reliably detect, relative to effect sizes in prior dropout research? Following Hsieh & Lavori (2000), our d = 1,570 Cox events at α = .05 and 80% power yield HR_min ≈ 1.07 per SD (≈ 1.15 for a balanced binary covariate); the omitted variance-inflation factor for covariate correlation would move this only trivially (to ≈ 1.08 at ρ ≈ .3–.45). For the primary logistic analysis (n = 1,704, 281 retainers), simulation (300 replicates per grid point, Wald test) gives a minimum detectable odds ratio of ≈ 1.20 per SD at 80% power. Prior prospective work on youth-sport dropout reports small-to-moderate effects (Cohen's d ≈ 0.2–0.5; ORs ≈ 1.4–2.5; Back et al., 2022; Calvo et al., 2010; Espedalen & Seippel, 2024; Sarrazin et al., 2002). Detection capacity is therefore well below typical effect magnitudes, so null findings should be interpreted as substantively small rather than underpowered.

## S-M3. Missing data, sample flow, and clustering

Missing values arose for Tyrving score (~20%, athletes whose baseline events could not be scored against the Tyrving table) and HHI (~10%). Primary analyses used complete-case regression (n = 1,704); a table mapping every analysis sample is Supplementary Table S12, and included and excluded athletes are compared in Supplementary Table S25 (senior retention 16.5% vs 16.0% — near-identical). The principal missing-data sensitivity is multiple imputation: chained-equation imputation of Tyrving and HHI (20 imputations, posterior sampling, outcome and all covariates in the imputation model; the 24 sex-unknown athletes are excluded before imputation and sex is never imputed, n = 2,099), with Rubin-pooled estimates (Supplementary Table S21); the volume coefficient is unchanged (OR 2.34 [2.07, 2.66] vs 2.40 complete-case). Mean imputation (Supplementary Table S5) and cluster-robust standard errors at the club level (Supplementary Table S2) give the same picture. The Table 4 sample is athletes with ≥1 result at age 14 (n = 1,914), of whom 1,549 are complete cases on Tyrving; Tyrving missingness is somewhat concentrated among athletes inactive at 14 (25.8% vs 19.1%). The 24 athletes with unknown sex are excluded from all regression models (which condition on sex) but included in cohort totals and unstratified Kaplan–Meier curves.

## S-M4. Classification performance and calibration of the early-warning thresholds

For the prospective early-warning thresholds (main text Table 6), we computed sensitivity, specificity, positive and negative predictive value, and the absolute senior-retention rates among flagged and unflagged athletes, at candidate thresholds on pre-milestone volume applied at the end of the age-14 season — i.e., implementable before any age-15–16 outcome information exists. All metrics are computed on a single denominator (the full cohort, n = 2,123) with 2,000-replicate bootstrap percentile confidence intervals. Calibration of the primary model itself was assessed on cross-validated (out-of-fold) predicted probabilities via the calibration slope and intercept (logistic recalibration of the outcome on the linear predictor) and the Brier score (Supplementary Table S23): slope 0.96, intercept −0.06, Brier 0.122, indicating well-calibrated predictions.

## S-M5. E-values for unmeasured confounding

E-values (VanderWeele & Ding, 2017) are computed for the primary baseline-window estimates only. Because the outcome is common (16.4%), the primary odds ratio is first converted to an approximate risk ratio via RR ≈ √OR before applying E = RR + √(RR(RR − 1)): OR 2.40 → RR ≈ 1.55 → E ≈ 2.5 (CI bound 2.2). The baseline-only Cox hazard ratio (0.49 per SD) is converted with the common-outcome formula RR ≈ (1 − 0.5^√HR)/(1 − 0.5^√(1/HR)), giving E ≈ 2.6. An earlier version of this analysis computed E-values from the post-baseline (ages-15–16) specification; those values are not reported because that specification both overlaps the outcome window and violates proportional hazards, making a pooled hazard ratio an inappropriate E-value input.

## S-M6. Exit-aligned trajectories and the contamination-free change model

To test the within-athlete pull-back claim at the individual level, each dropout's volume history was aligned to their own final active season (last calendar year with ≥2 results). For dropouts with final seasons at ages 15–19 (n = 1,139; ages outside 13–19 are unobserved in the per-age panel), we report median volumes at T−3, T−2, T−1, and T, the share still competing (>0 meets) in the penultimate season, and — among dropouts with final seasons at 16+ (n = 795), for whom at least one season precedes the penultimate — the share whose penultimate-season volume was reduced but nonzero relative to their earlier personal peak, at their peak (abrupt profile), or zero (gap year). The contamination-free change model is a logistic regression among athletes with ≥2 results at age 16 (n = 1,075): active senior status on sex, volume at age 15 (per SD), and change in volume from 15 to 16 (per SD). All predictors are measured by age 16 and every athlete in the sample is, by construction, still active when measured; the outcome window begins at age 20.

## S-M7. Club-level analyses

The intraclass correlation of pre-milestone volume across baseline clubs was estimated from a random-intercept linear mixed model (ICC = between-club variance / total variance). The primary logistic model was refit with club random intercepts via a Bayesian binomial mixed model (variational approximation), Supplementary Table S22.

## S-M8. HHI count-dependence stress tests

Because HHI ≥ 1/n for an athlete with n results, low result counts mechanically inflate apparent concentration. Three checks (Supplementary Table S20): Spearman correlations of early HHI with early result and meet counts; refits of the primary model restricted to athletes with ≥5 and ≥8 results in their first three active seasons; and a refit replacing HHI with the finite-sample-corrected index HHI* = (HHI − 1/n)/(1 − 1/n).

## Supplementary references

Back, J., Johnson, U., Svedberg, P., McCall, A., & Ivarsson, A. (2022). Drop-out from team sport among adolescents: A systematic review and meta-analysis of prospective studies. *Psychology of Sport and Exercise, 61*, Article 102205.

Berk, R. A., & Freedman, D. A. (2003). Statistical assumptions as empirical commitments. In T. G. Blomberg & S. Cohen (Eds.), *Punishment and social control: Essays in honor of Sheldon L. Messinger* (2nd ed., pp. 235–254). Aldine de Gruyter.

Calvo, T. G., Cervelló, E., Jiménez, R., Iglesias, D., & Murcia, J. A. M. (2010). Using self-determination theory to explain sport persistence and dropout in adolescent athletes. *The Spanish Journal of Psychology, 13*(2), 677–684.

Davidson-Pilon, C. (2019). lifelines: Survival analysis in Python. *Journal of Open Source Software, 4*(40), Article 1317.

Efron, B. (1977). The efficiency of Cox's likelihood function for censored data. *Journal of the American Statistical Association, 72*(359), 557–565.

Espedalen, L. E., & Seippel, Ø. (2024). Dropout and social inequality: Young people's reasons for leaving organized sports. *Annals of Leisure Research, 27*(2), 197–214.

Grambsch, P. M., & Therneau, T. M. (1994). Proportional hazards tests and diagnostics based on weighted residuals. *Biometrika, 81*(3), 515–526.

Hsieh, F. Y., & Lavori, P. W. (2000). Sample-size calculations for the Cox proportional hazards regression model with nonbinary covariates. *Controlled Clinical Trials, 21*(6), 552–560.

Lin, D. Y., & Wei, L. J. (1989). The robust inference for the Cox proportional hazards model. *Journal of the American Statistical Association, 84*(408), 1074–1078.

Sarrazin, P., Vallerand, R. J., Guillet, E., Pelletier, L. G., & Cury, F. (2002). Motivation and dropout in female handballers: A 21-month prospective study. *European Journal of Social Psychology, 32*(3), 395–418.

van Houwelingen, H. C. (2007). Dynamic prediction by landmarking in event history analysis. *Scandinavian Journal of Statistics, 34*(1), 70–85.

VanderWeele, T. J., & Ding, P. (2017). Sensitivity analysis in observational research: Introducing the E-value. *Annals of Internal Medicine, 167*(4), 268–274.
