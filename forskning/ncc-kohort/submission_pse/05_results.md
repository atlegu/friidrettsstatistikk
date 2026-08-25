# Results

## 3.1 Cohort characteristics

The cohort comprised 2,123 athletes (52.0% female): 1,301 in Cohort A and 822 in Cohort B, closely matched on demographic and performance distributions (mean Tyrving best 666 in each; ~41% active at age 17 in each; Table 1). Senior retention (≥1 active season at age 20+) was 15.8% in Cohort A and 17.3% in Cohort B (combined 16.4%). The proportion still active in 2024+ was 5.8% (A) and 10.8% (B), reflecting Cohort B's shorter follow-up.

[**Table 1 about here**]

## 3.2 Competition-volume trajectories diverge by ages 13–14

Figure 2 presents the central behavioral observation (Figure 1 shows the conceptual model): median competitions per year by age, plotted separately for eventual retainers (n = 348) and non-retainers (n = 1,775). The groups already differ at baseline — medians of 13 vs. 8 meets at age 13, and 17 vs. 8 at age 14 — and diverge further from age 15: retainers peak at 19 meets at age 15 and sustain that level through age 17, while future dropouts decline from 8 meets at age 14 to 3 at age 15 and 0 thereafter. Two complementary patterns are visible: substantial baseline differences between the groups already at ages 13–14, and a progressive within-athlete pull-back among future dropouts, most visible across the age-14-to-15 transition. We test these separately in Section 3.5.

Kaplan–Meier curves summarize the same attrition in time-to-event form: half the cohort had ceased active competition within 3 years and 75% within 5, with the steepest dropout at age 17, the youth-to-junior transition (Supplementary Figure S3). Sex-stratified curves overlap (log-rank χ² = 0.95, *p* = .33). Stratifying descriptively by competition volume across ages 15–16 yields monotonically separated curves — 71% senior retention among athletes with ≥31 meets vs. 4% among those with none (Figure 3) — and stratifying by pre-17 championship types shows the same pattern (Supplementary Figure S4). Formal estimates use baseline-only predictors below.

[**Figures 1 and 2 about here**]

[**Table 2 about here**]

[**Figure 3 about here**]

## 3.3 Primary analysis: prospective logistic regression for senior retention

**Among baseline-window predictors (ages 13–14), competition volume provided the largest incremental contribution to prospective discrimination of senior retention 6–14 years later: OR = 2.40 per SD (95% CI [2.07, 2.78], *p* < .001), cross-validated AUC = 0.751.** Models for *active senior status* were fitted stepwise with baseline-only predictors (avoiding look-ahead) and 5-fold cross-validated AUC (Table 3). Sex alone discriminated near chance (CV-AUC = 0.541); adding baseline Tyrving performance raised AUC modestly to 0.607; adding early specialization (HHI) added nothing further (0.600); adding pre-milestone volume raised AUC substantially to 0.751. Once volume was entered, HHI became significantly associated with retention (OR = 1.35 per SD, *p* < .001) — *higher* concentration in fewer event categories predicted *higher* retention (§3.9; §4.6).

[**Table 3 about here**]

## 3.4 Structural controls do not change the picture

Adding region (3-level), birth-quarter indicators (Q1/Q4), and standardized club size to the full Table 3 model left the volume coefficient unchanged (OR = 2.40 with and without controls), and no structural covariate was significantly associated with retention (all *p* > .14; Supplementary Table S13).

## 3.5 Progressive pull-back versus baseline heterogeneity

**Early behavioral heterogeneity and within-athlete pull-back contribute independently — they are not substitutes.** The trajectories in Figure 2 are consistent with two readings: future retainers and dropouts as distinct *behavioral typologies* visible already at ages 13–14, or a *within-athlete pull-back* across the age-14-to-15 transition. We entered baseline level (volume at age 14) and within-athlete change (volume at age 15 minus age 14) into one logistic regression, restricted to athletes still active at age 14 (n = 1,914; Table 4). The age-14 level was strongly associated with retention (OR = 2.79 per SD, 95% CI [2.37, 3.28], *p* < .001) and the within-athlete change almost as strongly (OR = 2.44 per SD, 95% CI [2.10, 2.83], *p* < .001) — a one-SD greater decline was associated with 2.4-times lower retention odds. Adding change to the level-only model more than doubled pseudo-*R*² (0.113 → 0.227).

[**Table 4 about here**]

## 3.6 Time-aligned behavior vs. performance

A concern with earlier framings was that post-baseline volume (ages 15–16) versus baseline performance (ages 13–14) gave the behavioral predictor a temporal advantage. In a fully time-aligned comparison — both measured at ages 13–14 — behavior still provides stronger discrimination: AUC = 0.607 for sex + baseline Tyrving, 0.740 for sex + ages-13–14 volume, 0.737 for both combined (Supplementary Table S15). Performance adds little once early volume is known.

Competition volume and performance were positively but moderately correlated (pre-milestone volume vs. baseline Tyrving: Spearman ρ = .29; vs. peak Tyrving before age 15: ρ = .45; milestone-window volume vs. age-15 Tyrving: ρ = .48), sharing at most roughly a fifth of their variance. The volume–retention association also held *within* performance strata: splitting the cohort by baseline-Tyrving quartile and pre-milestone volume (above/below median), above-median volume was associated with higher senior retention in every quartile — 16.3% vs. 10.0% in the lowest-performing quartile, 18.0% vs. 4.2%, 25.8% vs. 4.7%, and 34.1% vs. 13.2% in the highest. Competition volume is thus related to, but clearly not reducible to, performance level.

## 3.7 Landmark analysis: post-baseline behavior among continuing athletes

Conditioning on athletes active at age 16 (≥1 result; n = 1,167), volume across ages 15–16 was the largest contributor to subsequent cessation risk (HR = 0.60 per SD, 95% CI [0.54, 0.66], C-index = 0.74; Supplementary Table S8); excluding athletes with milestone volume = 0 gave HR = 0.51 (Supplementary Table S11). The baseline-only Cox model is in Supplementary Table S16 and a period-specific decomposition in Table 5. The baseline-start Cox model with post-baseline covariates is not used as a primary estimate because predictor and at-risk window overlap.

## 3.8 Prospective early-warning thresholds

Because the primary analysis uses only baseline-window data, calibration metrics can be computed for a prospective rule applied at the end of the age-14 season (Table 6). At a moderate threshold (vol < 10 meets across ages 13–14, flagging 26.4%), PPV = 0.94 and sensitivity = 0.30; lower thresholds (< 5 meets; 9% flagged, PPV = 0.93) suit targeted outreach, higher thresholds (< 15; 43% flagged, PPV = 0.93) broaden the screen. The high PPV partly reflects the 84% non-retention base rate; the behavioral threshold improves precision by ~10 points over base-rate prediction while providing graduated sensitivity that base-rate prediction cannot.

[**Table 6 about here**]

## 3.9 Specialization is protective in our data

Higher baseline HHI (more event-category concentration) predicted *higher* senior retention: OR = 1.35 per SD (95% CI [1.16, 1.57], *p* < .001) in the primary regression, HR = 0.80 in the Cox model, and present in both cohorts (A OR = 1.24, B OR = 1.58). Athletes whose ages-13–14 results were concentrated in fewer event categories were *more* likely to retain. This index captures event-category concentration *within* track and field — a different construct from the multisport diversification studied in the elite-performance literature (Côté & Hancock, 2016; Güllich et al., 2022); we develop the distinction in §4.6.

## 3.10 Cross-cohort replication and sensitivity

Re-estimated by cohort, the pre-milestone volume effect replicated: Cohort A OR = 2.22 (95% CI [1.86, 2.64]), Cohort B OR = 2.79 (95% CI [2.17, 3.58]), both *p* < .001 (Table 7); sex was significant only in Cohort A. The effect was robust to outcome definition (ORs 2.79, 3.08, 2.94 across the three definitions; Supplementary Table S9), to cluster-robust SEs (Supplementary Table S2), and to unmeasured confounding: E-value = 5.16 (lower-CI E-value = 4.70) for the milestone-window volume effect (Supplementary Table S3), meaning an unmeasured confounder would need risk-ratio associations exceeding 5 with both predictor and outcome to nullify it — well above any observed covariate.
