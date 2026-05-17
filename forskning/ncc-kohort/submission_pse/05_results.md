# Results

## Cohort characteristics

The full cohort comprised 2,123 athletes (52.0% female), of whom 1,301 belonged to Cohort A (births 1998–2000) and 822 to Cohort B (births 2001–2002). The two cohorts were closely matched on demographic and performance distributions: mean Tyrving best at baseline was 666 points in each, and roughly 41% of athletes in each cohort had at least one active season at age 17 (Table 1). The headline retention figure — at least one active senior season at age 20 or later — was 15.8% in Cohort A and 17.3% in Cohort B; combined, 16.4% of the 2,123 athletes met this criterion. The proportion still actively competing in 2024 or later was 5.8% (Cohort A) and 10.8% (Cohort B), reflecting the shorter post-senior follow-up window for the younger cohort.

[**Table 1 about here**]

## Competition-volume trajectories diverge at the milestone year

Figure 1 presents the central behavioral observation. Median competitions per year are plotted by age (13–18) separately for athletes who eventually retained senior activity (n = 348) and those who did not (n = 1,775). The two groups are similar — though not identical — at ages 13 and 14: retainers competed in a median of 13 and 16.5 meets respectively, dropouts in 8 and 8. From age 15 onwards the trajectories diverge sharply. Retainers increased their participation to a peak of 19 meets at age 15 and sustained it through age 17 (18 and 17 meets at ages 16 and 17 respectively). Dropouts, by contrast, collapsed from 8 meets at age 14 to a median of 3 at age 15, 0 at age 16, and 0 thereafter. This divergence is visible *before* most dropouts had left competition entirely; the interquartile range for dropouts at age 15 (0–11 meets) shows that many were still competing while pulling back, consistent with a gradual rather than abrupt withdrawal process.

[**Figure 1 about here**]

## Survival to active senior age

Overall Kaplan-Meier retention is shown in Figure 2A. Half of the cohort had ceased active competition within 3 years of baseline; 75% had ceased within 5 years. The age-17 floor (corresponding to the transition from youth to junior competition) marks the steepest acceleration in dropout. The sex-stratified retention curves (Figure 2B) overlap throughout the follow-up window: a log-rank test detected no overall sex difference (χ² = 0.95, p = 0.33).

[**Figure 2 about here**]

When the cohort is stratified by competition volume at age 15–16 (Figure 3), retention curves separate clearly and monotonically: athletes who competed in 31 or more meets across ages 15–16 retained 71% senior activity, while athletes who competed in none retained only 4%. Stratifying instead by number of championship types entered before age 17 (Figure 4) reveals the same pattern: athletes who competed in all four championship types (UM, JrNM, NM, KM) retained 91% senior activity, while athletes who entered zero championship types retained 5%.

[**Figures 3 and 4 about here**]

## Stepwise Cox regression: volume dominates

Cox proportional hazards models were fitted in five nested specifications (Table 3). Sex alone produced a near-chance C-index of 0.498 (HR for female = 1.04, p = 0.35). Adding standardized Tyrving baseline performance raised the C-index to 0.574 (HR per SD = 0.86, p < .001), showing a modest protective effect of higher performance. Adding early specialization (HHI) did not improve discrimination (M3 C = 0.573; HHI HR = 0.98, p = 0.46).

Adding standardized competition volume at age 15–16 in M4 produced a substantial jump in C-index from 0.573 to 0.846 — the largest gain at any step in the sequence. In this model, vol_milepael had a hazard ratio of 0.352 per SD (95% CI: 0.327–0.380, p < .001), corresponding to an approximately three-fold reduction in dropout hazard for a one-SD increase in milestone-year competition volume. Notably, the previously significant Tyrving coefficient became non-significant once volume was entered (HR = 1.04, p = 0.17), suggesting that baseline performance functions primarily as a proxy for the kind of athlete who will compete frequently rather than as an independent predictor of retention.

Adding count of championship types in M5 did not improve C-index further (0.842), but the championship variable itself was strongly associated with retention (HR = 0.74 per type, p < .001), and in this fuller model the sex coefficient achieved nominal significance (HR for female = 1.12, p = 0.025): for a given combination of performance, specialization, volume and championship breadth, female athletes had slightly higher dropout hazard than male athletes — a sex-effect that was hidden in the unadjusted analysis.

[**Table 3 about here**]

## Random forest: volume features dominate variable importance

Random-forest variable importances (Figure 5; Table 4) confirm the Cox findings using a non-parametric, interaction-tolerant procedure. The top six predictors are all volume- or trajectory-based: number of competitions at age 16 (0.133), composite volume at milestone (0.126), competitions at age 15 (0.083), Tyrving performance slope from age 13 to 16 (0.075), volume trend across the milestone (0.071), and peak Tyrving before age 15 (0.048). Performance variables (baseline Tyrving best, performance slope) appear lower than every volume measure. Sex enters the model near the bottom of the importance ranking (0.010), consistent with the Cox results.

[**Figure 5 about here**]

[**Table 4 about here**]

## How much of retention can pre-baseline information classify?

Table 5 contrasts cross-validated AUCs for nested predictor subsets. A purely performance-based classifier (sex + Tyrving best) achieves AUC = 0.59 in 5-fold logistic regression. Adding specialization (HHI + number of event categories) raises AUC modestly to 0.60. A pure volume-based classifier using only competitions counted at ages 13–16 achieves AUC = 0.82, a 23-point gain. Combining volume with specialization adds nothing further (AUC = 0.82), and including the full 22-feature set produces an AUC near that of volume alone (logistic AUC = 0.81; random forest AUC = 0.82). In short, behavioral indicators available by approximately age 16 classify eventual senior retention nearly as well as a maximally informative model.

[**Table 5 about here**]

## Cross-cohort replication

Replication across the two birth-year cohorts is presented in Table 6. The volume-at-milestone effect replicated in both cohorts at similar magnitude (Cohort A HR = 0.49 per SD, p < .001; Cohort B HR = 0.36 per SD, p < .001). Championship-types also replicated (Cohort A HR = 0.71, p < .001; Cohort B HR = 0.77, p < .001). Both cohorts produced very similar C-indices (Cohort A 0.835; Cohort B 0.852). The sex coefficient differed between cohorts: it was elevated and statistically significant in Cohort A (HR = 1.19, p = 0.006) but not in Cohort B (HR = 1.02, p = 0.83). Performance and specialization coefficients varied in sign and significance but were always small in magnitude relative to volume.

[**Table 6 about here**]

In summary: across two independent birth-year cohorts spanning a 5-year window, the same behavioral pattern — competition volume at the qualification-milestone year as the dominant retention predictor — appeared with concordant magnitude and direction. Performance and specialization remained weak predictors. Future-dropout trajectories were visibly distinguishable from future-retainer trajectories from age 15 onward.
