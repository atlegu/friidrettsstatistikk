# Results

## 3.1 Cohort characteristics

The full cohort comprised 2,123 athletes (52.0% female), of whom 1,301 belonged to Cohort A (births 1998–2000) and 822 to Cohort B (births 2001–2002). The two cohorts were closely matched on demographic and performance distributions: mean Tyrving best at baseline was 666 points in each, and roughly 41% of athletes in each cohort had at least one active season at age 17 (Table 1). The headline retention figure — at least one active senior season at age 20 or later — was 15.8% in Cohort A and 17.3% in Cohort B; combined, 16.4% of the 2,123 athletes met this criterion. The proportion still actively competing in 2024 or later was 5.8% (Cohort A) and 10.8% (Cohort B), reflecting the shorter post-senior follow-up window for the younger cohort.

[**Table 1 about here**]

## 3.2 Competition-volume trajectories diverge before formal exit

Figure 2 presents the central behavioral observation. (Figure 1 shows the conceptual model that motivates this test.) Median competitions per year are plotted by age (13–18) separately for athletes who eventually retained senior activity (n = 348) and those who did not (n = 1,775). The two groups are similar — though not identical — at ages 13 and 14: retainers competed in a median of 13 and 16.5 meets respectively, dropouts in 8 and 8. From age 15 onwards the trajectories diverge sharply. Retainers increased their participation to a peak of 19 meets at age 15 and sustained it through age 17 (18 and 17 meets at ages 16 and 17 respectively). Dropouts collapsed from 8 meets at age 14 to a median of 3 at age 15, 0 at age 16, and 0 thereafter. Critically, the divergence is visible *before* most dropouts had left competition entirely; the interquartile range for dropouts at age 15 (0–11 meets) shows that many were still nominally competing while pulling back, consistent with the gradual withdrawal pattern described in the qualitative literature.

[**Figures 1 and 2 about here**]

[**Table 2 about here**]

## 3.3 Survival to active senior age

Overall Kaplan–Meier retention (Supplementary Figure S3A) shows that half of the cohort had ceased active competition within 3 years of baseline; 75% had ceased within 5 years. The age-17 floor (the transition from youth to junior competition) marks the steepest acceleration in dropout. Sex-stratified retention curves (Supplementary Figure S3B) overlap throughout the follow-up window: a log-rank test detected no overall sex difference (χ² = 0.95, p = 0.33).

When the cohort is stratified by competition volume at age 15–16 (Figure 3), retention curves separate clearly and monotonically: athletes who competed in 31 or more meets across ages 15–16 retained 71% senior activity, while athletes who competed in none retained only 4%. Stratifying instead by number of championship types entered before age 17 (Supplementary Figure S4) reveals the same pattern: athletes who competed in all four championship types (UM, JrNM, NM, KM) retained 91% senior activity, while athletes who entered zero retained 5%.

[**Figure 3 about here**]

## 3.4 Stepwise Cox regression

Cox proportional hazards models were fitted in five nested specifications (Table 3). Sex alone produced a near-chance C-index of 0.498 (HR for female = 1.04, p = 0.35). Adding standardized Tyrving baseline performance raised the C-index to 0.574 (HR per SD = 0.86, p < .001), showing a modest protective effect of higher performance. Adding early specialization (HHI) did not improve discrimination (M3 C = 0.573; HHI HR = 0.98, p = 0.46).

Adding standardized competition volume at age 15–16 in M4 produced a substantial jump in C-index from 0.573 to 0.846. In this model, vol_milepael was associated with a hazard ratio of 0.352 per SD (95% CI: 0.327–0.380, p < .001), corresponding to a substantially lower observed dropout hazard at higher milestone-window competition volume. The previously significant Tyrving coefficient became non-significant once volume was entered (HR = 1.04, p = 0.17): once an athlete's behavioral engagement at the milestone is known, knowing their baseline performance adds little additional discrimination. **Because both predictor and outcome are derived from registered competition behavior, the large gain in classification accuracy should be interpreted as capturing the temporal unfolding of disengagement rather than as independent predictive power; the landmark analysis in Section 3.5 addresses this directly.**

Adding the count of championship types in M5 did not improve discrimination further (C = 0.842) but the championship variable itself was strongly associated with retention (HR = 0.74 per type, p < .001). In the fuller model the sex coefficient achieved nominal significance (HR for female = 1.12, p = 0.025): for given combinations of performance, specialization, volume, and championship breadth, female athletes had slightly higher dropout hazard than male athletes — an adjusted sex effect that was hidden in the unadjusted analysis.

The minimum detectable hazard ratio under Hsieh and Lavori (2000) with 1,570 events and 80% power was HR = 1.07; all reported null findings (e.g., baseline-only sex coefficient) were therefore well-powered to detect substantively meaningful effects.

[**Table 3 about here**]

## 3.5 Landmark analysis: the volume signal is not measurement-tautology

Because senior retention is itself defined by registered competitive activity, the apparent predictive power of milestone-window volume could partly reflect a mechanical relationship: athletes who dropped out *before* age 15 have vol_milepael = 0 by construction. To address this, we restricted the analysis to athletes still demonstrably active at age 16 (n = 1,167 of the original 2,123) and re-fit the full Cox model with follow-up time measured from age 16.

Among continuing athletes, milestone-window volume remained the dominant predictor of subsequent senior retention (HR = 0.60 per SD, 95% CI [0.54, 0.66], p < .001; C-index = 0.735). Championship-types breadth also retained its effect (HR = 0.78, p < .001). The behavioral signal is therefore not an artefact of athletes who had already dropped out before the milestone window. As a complementary check, re-estimating the full Cox model excluding athletes with vol_milepael = 0 produced HR = 0.51 for vol_milepael (95% CI [0.46, 0.56], p < .001; n = 1,250; Supplementary Table S12) — a slight attenuation but a substantively unchanged effect.

More importantly, a second check used the *pre-milestone* (ages 13–14) volume alone as the only behavioral predictor (Supplementary Table S10). Pre-milestone volume — measured during the baseline window itself, three years before the qualification milestone — was associated with senior retention almost as strongly as the milestone-window variable (HR = 0.50 per SD, 95% CI [0.46, 0.53], p < .001). The behavioral signal is therefore detectable *before* the age 15–16 window, indicating that progressive disengagement is observable at the very onset of organized competitive participation rather than being a reaction to qualification-window outcomes. This is consistent with the qualitative literature's characterization of dropout as a long deliberative process rather than a response to a specific selection event (Eliasson & Johansson, 2021; Espedalen & Seippel, 2022).

[**Table 4 about here**]

## 3.6 Time-varying effects

Schoenfeld residual tests indicated that the proportional-hazards assumption was satisfied for sex (χ²₁ = 2.50, p = .11) and for baseline Tyrving performance (χ²₁ = 0.12, p = .73), but violated for the specialization (χ²₁ = 11.12, p < .001), championship-types (χ²₁ = 10.89, p = .001), and milestone-window volume (χ²₁ = 220.77, p < .001) covariates (Supplementary Table S1). To verify that the violations did not change substantive conclusions, we re-fit the model stratified on the most-violating discrete covariate (HHI tercile); remaining effects retained their direction, magnitude, and significance (Supplementary Table S6).

To characterize the time-varying nature of the dominant predictor, we fit period-specific Cox models in three follow-up windows (Figure 4, Table 5). The protective effect of milestone-window volume was strongest in the first three years post-baseline (HR = 0.14, 95% CI: 0.11–0.16), moderate in years 3–6 (HR = 0.69, 95% CI: 0.60–0.79), and absent in years 6+ (HR = 0.96, 95% CI: 0.77–1.19). This pattern indicates that the behavioral signal predicts *proximal* (within 3 years) retention strongly and *late* retention (after the junior transition) weakly. Effect sizes for the other covariates were stable across windows.

[**Figure 4 about here**]

[**Table 5 about here**]

## 3.7 Robustness to outcome definition

To assess sensitivity to how senior retention is operationalized, we re-estimated the central effect using three outcome definitions: (A) ≥1 senior-age result, (B) ≥2 results in any senior-age year (the primary outcome), and (C) ≥2 results in each of two distinct senior-age years (Supplementary Table S9). The odds ratio for vol_milepael in a logistic-regression analogue of the full model was 2.79 (definition A), 3.08 (B), and 2.94 (C); AUC was 0.83, 0.86, and 0.87 respectively. The choice of outcome threshold has essentially no effect on the substantive finding.

## 3.8 Calibration and practical early-warning thresholds

Table 6 presents calibration metrics for using milestone-window competition volume as a behavioral early-warning indicator. With a threshold of vol_milepael < 10 meets (flagging 53.7% of the cohort), the positive predictive value (PPV) is 0.97 — among flagged athletes, 97% subsequently dropped out before senior age. The negative predictive value is 0.32, sensitivity 0.63, and specificity 0.91. Lower thresholds (vol < 1) trade sensitivity for specificity (PPV = 0.99, sensitivity = 0.33, 27.7% flagged); higher thresholds (vol < 20) trade specificity for sensitivity (PPV = 0.95, sensitivity = 0.77, 67.1% flagged). The high PPVs partly reflect the high dropout base rate in this population (84%); an unsophisticated rule "predict that everyone drops out" would already achieve PPV = 0.84. The behavioral threshold therefore improves precision by 11–15 percentage points over base-rate prediction, while also providing graduated sensitivity that base-rate prediction cannot. The decile-based calibration plot for the full Cox model (Supplementary Figure S1) shows close agreement between predicted and observed retention probabilities across the distribution.

[**Table 6 about here**]

## 3.9 Random forest variable importance (convergent evidence)

As a non-parametric convergent check, a random forest fit to predict senior retention identified volume-based features as the most important predictors (Supplementary Figure S2; Supplementary Table S12): the top six positions are all volume- or trajectory-based, with sex appearing near the bottom (importance 0.010). The pattern is consistent with the Cox findings and confirms that the ranking is not an artefact of linearity assumptions. Cross-validated AUCs for nested predictor subsets (Supplementary Table S8) show that a model using only competition-volume features at ages 13–16 achieves AUC = 0.82, essentially identical to the full 22-predictor model (AUC = 0.82) — performance and specialization information add nothing once volume is observed.

## 3.10 Cross-cohort replication

The full Cox model was re-estimated separately in each birth-year cohort (Table 7). The volume-at-milestone effect replicated in both cohorts at similar magnitude (Cohort A HR = 0.49 per SD, p < .001; Cohort B HR = 0.36 per SD, p < .001). Championship-types also replicated (Cohort A HR = 0.71, p < .001; Cohort B HR = 0.77, p < .001). The C-indices were similar (Cohort A 0.835; Cohort B 0.852). The sex coefficient differed between cohorts: elevated and significant in Cohort A (HR = 1.19, p = 0.006) but not in Cohort B (HR = 1.02, p = 0.83). HHI-early reached significance in Cohort B (HR = 0.88, p = 0.004) but not Cohort A.

[**Table 7 about here**]

## 3.11 Sensitivity to confounding and clustering

The *E-value* for the milestone-window volume effect (HR = 0.35) was 5.16, with a corresponding lower-CI E-value of 4.70 (VanderWeele & Ding, 2017). An unmeasured confounder would therefore need to be associated with both baseline competition volume and senior retention by a risk ratio of at least 5.16 — substantially stronger than any observed covariate — to explain away the protective effect (Supplementary Table S3). Re-estimating the full Cox model with cluster-robust standard errors at the club level (Lin & Wei, 1989) left point estimates unchanged (Supplementary Table S2). Substituting variable means for missing covariates produced near-identical estimates to the complete-case results (e.g., vol_milepael HR = 0.45 imputed vs. 0.44 complete-case; Supplementary Table S5). Fitting the full Cox model separately in male and female athletes produced identical C-indices (0.843) and concordant effect directions (Supplementary Table S7).

In summary: across two independent birth-year cohorts spanning a 5-year window, competition volume at the qualification-milestone year is the dominant predictor of subsequent senior retention. The effect is not an artefact of mechanical zero-values, replicates among athletes who remained active at age 16, is detectable using only pre-milestone data, withstands an E-value sensitivity exceeding 5, and is robust to outcome definition, missing-data treatment, club clustering, and sex stratification.
