# Supplementary Methods (Extended)

*This material accompanies the main article and expands the condensed Statistical Analysis section. Citations here appear in the supplementary reference list below.*

## S-M1. Time-to-cessation survival analysis: full specification

We modeled time from baseline to last active season using Cox proportional hazards regression with Efron's tie-handling (Efron, 1977), implemented in lifelines (Davidson-Pilon, 2019). The primary Cox specification (Supplementary Table S16) contains a baseline-only predictor set. We additionally estimated (a) a landmark analysis (van Houwelingen, 2007) restricted to athletes active at age 16 (n = 1,167), and (b) a post-baseline Cox specification with ages-15–16 covariates (Supplementary Table S8; Table 5 gives the period-specific decomposition); the latter is interpreted with caveats about operational overlap between predictor and outcome windows. Proportional hazards were assessed via scaled Schoenfeld residuals (Grambsch & Therneau, 1994). For the dominant covariate we computed E-values (VanderWeele & Ding, 2017), period-specific estimates, cluster-robust standard errors on club name (Lin & Wei, 1989), and sex-stratified models. Kaplan–Meier curves were stratified by sex, ages-15–16 volume, and pre-17 championship types.

## S-M2. Sample size and detection capacity

Classical hypothesis-testing sample-size power calculations are not directly applicable to population-based register studies where the full cohort is observed; we treat the estimates as descriptions of this population rather than inferences to a hypothetical super-population (Berk & Freedman, 2003). We therefore replace a-priori power with a detection-capacity analysis: given the observed event count, what is the smallest effect size the design could reliably detect, relative to effect sizes in prior dropout research? Following Hsieh & Lavori (2000), our d = 1,570 Cox events at α = .05 and 80% power yield HR_min ≈ 1.07 per SD (≈ 1.15 for a balanced binary covariate). Prior prospective work on youth-sport dropout reports small-to-moderate effects (Cohen's d ≈ 0.2–0.5; ORs ≈ 1.4–2.5; Calvo et al., 2010; Espedalen & Seippel, 2024; Sarrazin et al., 2002). Detection capacity is therefore well below typical effect magnitudes, so null findings should be interpreted as substantively small rather than underpowered.

## S-M3. Missing data and clustering

Missing values arose for Tyrving score (~20%, athletes whose baseline events could not be scored against the Tyrving table) and HHI (~10%). Primary analyses used complete-case regression (n = 1,704). Mean-imputation produced near-identical estimates (Supplementary Table S5). Cluster-robust standard errors at the club level left coefficients unchanged with marginally wider confidence intervals (Supplementary Table S2).

## S-M4. Calibration and threshold construction

For the prospective early-warning thresholds (main text Table 6), we computed sensitivity, specificity, positive predictive value, and negative predictive value at five candidate thresholds on pre-milestone volume, applied at the end of the age-14 season — i.e., implementable before any age-15–16 outcome information exists.

## Supplementary references

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
