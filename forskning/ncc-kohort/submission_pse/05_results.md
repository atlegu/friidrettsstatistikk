# Results

## 3.1 Cohort characteristics

The full cohort comprised 2,123 athletes (52.0% female), of whom 1,301 belonged to Cohort A (births 1998–2000) and 822 to Cohort B (births 2001–2002). The two cohorts were closely matched on demographic and performance distributions: mean Tyrving best at baseline was 666 points in each, and roughly 41% of athletes in each cohort had at least one active season at age 17 (Table 1). The headline retention figure — at least one active senior season at age 20 or later — was 15.8% in Cohort A and 17.3% in Cohort B; combined, 16.4% of the 2,123 athletes met this criterion. The proportion still actively competing in 2024 or later was 5.8% (Cohort A) and 10.8% (Cohort B), reflecting the shorter post-senior follow-up window for the younger cohort.

[**Table 1 about here**]

## 3.2 Competition-volume trajectories diverge at the milestone year

Figure 1 presents the central behavioral observation. Median competitions per year are plotted by age (13–18) separately for athletes who eventually retained senior activity (n = 348) and those who did not (n = 1,775). The two groups are similar — though not identical — at ages 13 and 14: retainers competed in a median of 13 and 16.5 meets respectively, dropouts in 8 and 8. From age 15 onwards the trajectories diverge sharply. Retainers increased their participation to a peak of 19 meets at age 15 and sustained it through age 17 (18 and 17 meets at ages 16 and 17 respectively). Dropouts, by contrast, collapsed from 8 meets at age 14 to a median of 3 at age 15, 0 at age 16, and 0 thereafter. This divergence is visible *before* most dropouts had left competition entirely; the interquartile range for dropouts at age 15 (0–11 meets) shows that many were still nominally competing while pulling back, consistent with a gradual rather than abrupt withdrawal process.

[**Figure 1 about here**]

[**Table 2 about here**]

## 3.3 Survival to active senior age

Overall Kaplan-Meier retention is shown in Figure 2A. Half of the cohort had ceased active competition within 3 years of baseline; 75% had ceased within 5 years. The age-17 floor (corresponding to the transition from youth to junior competition) marks the steepest acceleration in dropout. The sex-stratified retention curves (Figure 2B) overlap throughout the follow-up window: a log-rank test detected no overall sex difference (χ² = 0.95, p = 0.33).

[**Figure 2 about here**]

When the cohort is stratified by competition volume at age 15–16 (Figure 3), retention curves separate clearly and monotonically: athletes who competed in 31 or more meets across ages 15–16 retained 71% senior activity, while athletes who competed in none retained only 4%. Stratifying instead by number of championship types entered before age 17 (Figure 4) reveals the same pattern: athletes who competed in all four championship types (UM, JrNM, NM, KM) retained 91% senior activity, while athletes who entered zero championship types retained 5%.

[**Figures 3 and 4 about here**]

## 3.4 Stepwise Cox regression: volume dominates

Cox proportional hazards models were fitted in five nested specifications (Table 3). Sex alone produced a near-chance C-index of 0.498 (HR for female = 1.04, p = 0.35). Adding standardized Tyrving baseline performance raised the C-index to 0.574 (HR per SD = 0.86, p < .001), showing a modest protective effect of higher performance. Adding early specialization (HHI) did not improve discrimination (M3 C = 0.573; HHI HR = 0.98, p = 0.46).

Adding standardized competition volume at age 15–16 in M4 produced a substantial jump in C-index from 0.573 to 0.846 — the largest gain at any step in the sequence. In this model, vol_milepael had a hazard ratio of 0.352 per SD (95% CI: 0.327–0.380, p < .001), corresponding to an approximately three-fold reduction in dropout hazard for a one-SD increase in milestone-year competition volume. Notably, the previously significant Tyrving coefficient became non-significant once volume was entered (HR = 1.04, p = 0.17), suggesting that baseline performance functions primarily as a proxy for the kind of athlete who will compete frequently rather than as an independent predictor of retention.

Adding count of championship types in M5 did not improve C-index further (0.842), but the championship variable itself was strongly associated with retention (HR = 0.74 per type, p < .001), and in this fuller model the sex coefficient achieved nominal significance (HR for female = 1.12, p = 0.025): for a given combination of performance, specialization, volume and championship breadth, female athletes had slightly higher dropout hazard than male athletes — a sex-effect that was hidden in the unadjusted analysis.

The minimum detectable hazard ratio under Hsieh and Lavori's (2000) formula with 1,570 events and 80% power was HR = 1.07 (or 0.93 for protective effects); all reported null findings were therefore well-powered to detect the smallest plausibly meaningful effect.

[**Table 3 about here**]

## 3.5 Proportional-hazards assumption and time-varying effects

Schoenfeld residual tests indicated that the proportional-hazards assumption was satisfied for sex (χ²₁ = 2.50, p = .11) and for baseline Tyrving performance (χ²₁ = 0.12, p = .73), but violated for the specialization (χ²₁ = 11.12, p < .001), championship-types (χ²₁ = 10.89, p = .001), and competition-volume (χ²₁ = 220.77, p < .001) covariates (Supplementary Table S1). To verify that the violations did not change substantive conclusions, we re-fit M5 stratified on the most-violating discrete covariate (HHI tercile); all remaining effects retained their direction, magnitude, and significance level (Supplementary Table S6).

To characterize the time-varying nature of the dominant predictor, we fit period-specific Cox models in three follow-up windows (Table 4). The protective effect of milestone-year competition volume was strongest in the first three years post-baseline (HR = 0.14, 95% CI: 0.11–0.16), moderate in years 3–6 (HR = 0.69, 95% CI: 0.60–0.79), and absent in years 6+ (HR = 0.96, 95% CI: 0.77–1.19). This pattern is consistent with the substantive interpretation that competition volume at the qualification milestone is most predictive of *immediate* (within 3 years) retention and matters less for *late dropouts* (athletes who continue past the junior transition and disengage in their early twenties). Effect sizes for the other covariates were stable across windows (Table 4).

[**Table 4 about here**]

## 3.6 Random forest: volume features dominate variable importance

Random-forest variable importances (Figure 5; Table 5) confirm the Cox findings using a non-parametric, interaction-tolerant procedure. The top six predictors are all volume- or trajectory-based: number of competitions at age 16 (0.133), composite volume at milestone (0.126), competitions at age 15 (0.083), Tyrving performance slope from age 13 to 16 (0.075), volume trend across the milestone (0.071), and peak Tyrving before age 15 (0.048). Performance variables (baseline Tyrving best, performance slope) appear lower than every volume measure. Sex enters the model near the bottom of the importance ranking (0.010), consistent with the Cox results.

[**Figure 5 about here**]

[**Table 5 about here**]

## 3.7 How much of retention can pre-baseline information classify?

Table 6 contrasts cross-validated AUCs for nested predictor subsets. A purely performance-based classifier (sex + Tyrving best) achieves AUC = 0.59 in 5-fold logistic regression. Adding specialization (HHI + number of event categories) raises AUC modestly to 0.60. A pure volume-based classifier using only competitions counted at ages 13–16 achieves AUC = 0.82, a 23-point gain. Combining volume with specialization adds nothing further (AUC = 0.82), and including the full 22-feature set produces an AUC near that of volume alone (logistic AUC = 0.81; random forest AUC = 0.82). In short, behavioral indicators available by approximately age 16 classify eventual senior retention nearly as well as a maximally informative model.

[**Table 6 about here**]

## 3.8 Cross-cohort replication

Replication across the two birth-year cohorts is presented in Table 7. The volume-at-milestone effect replicated in both cohorts at similar magnitude (Cohort A HR = 0.49 per SD, p < .001; Cohort B HR = 0.36 per SD, p < .001). Championship-types also replicated (Cohort A HR = 0.71, p < .001; Cohort B HR = 0.77, p < .001). Both cohorts produced very similar C-indices (Cohort A 0.835; Cohort B 0.852). The sex coefficient differed between cohorts: it was elevated and statistically significant in Cohort A (HR = 1.19, p = 0.006) but not in Cohort B (HR = 1.02, p = 0.83). Performance and specialization coefficients varied in sign and significance but were always small in magnitude relative to volume.

[**Table 7 about here**]

## 3.9 Sensitivity analyses

To assess the robustness of the volume-at-milestone effect to plausible threats to validity, we computed four additional sensitivity analyses (Supplementary Tables S2–S5).

**Unmeasured confounding.** The *E-value* for the volume-at-milestone effect (HR = 0.35) was 5.16, with a corresponding lower-CI E-value of 4.70 (VanderWeele & Ding, 2017). An unmeasured confounder would therefore need to be associated with both baseline competition volume and senior retention by a risk ratio of at least 5.16 — substantially stronger than the most predictive observed covariate in our data — to explain away the protective effect. E-values for championship-types (HR = 0.74; E = 2.04) and Tyrving baseline performance (HR = 0.86 in M2; E = 1.60) were correspondingly lower, indicating that those secondary effects could in principle be undermined by moderately strong unmeasured confounding, though the volume effect could not.

**Clustering by club.** Re-estimating the full Cox model with cluster-robust standard errors at the club level (Lin & Wei, 1989) left point estimates unchanged and 95% confidence intervals only marginally wider (Supplementary Table S2). The substantive conclusions were unaffected.

**Missing data.** Substituting variable means for missing covariates and re-estimating the full Cox model produced near-identical estimates to the complete-case results (e.g., vol_milepael HR = 0.45 imputed vs. 0.44 complete-case; Supplementary Table S5).

**Sex stratification.** Fitting the full Cox model separately in male and female athletes produced identical C-indices (0.843 in each) and concordant effect directions (Supplementary Table S7), confirming that the behavioral pattern is not sex-specific.

[**Tables 4 and 7 about here**]

In summary: across two independent birth-year cohorts spanning a 5-year window, the same behavioral pattern — competition volume at the qualification-milestone year as the dominant retention predictor — appeared with concordant magnitude and direction. Performance and specialization remained weak predictors. Future-dropout trajectories were visibly distinguishable from future-retainer trajectories from age 15 onward. Sensitivity analyses confirmed that the volume effect is robust to unmeasured confounding (E = 5.16), club-level clustering, missing-data treatment, and sex stratification, and that its protective magnitude is concentrated in the years immediately following the qualification milestone.
