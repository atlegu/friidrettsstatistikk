# Results

## 3.1 Cohort characteristics

The full cohort comprised 2,123 athletes (52.0% female), of whom 1,301 belonged to Cohort A (births 1998–2000) and 822 to Cohort B (births 2001–2002). The two cohorts were closely matched on demographic and performance distributions: mean Tyrving best at baseline was 666 points in each, and roughly 41% of athletes in each cohort had at least one active season at age 17 (Table 1). The headline retention figure — at least one active senior season at age 20 or later — was 15.8% in Cohort A and 17.3% in Cohort B; combined, 16.4% of the 2,123 athletes met this criterion. The proportion still actively competing in 2024 or later was 5.8% (Cohort A) and 10.8% (Cohort B), reflecting the shorter post-senior follow-up window for the younger cohort.

[**Table 1 about here**]

## 3.2 Competition-volume trajectories diverge by ages 13–14

Figure 2 presents the central behavioral observation. (Figure 1 shows the conceptual model that motivates this test.) Median competitions per year are plotted by age (13–18) separately for athletes who eventually retained senior activity (n = 348) and those who did not (n = 1,775). The two groups already differ at baseline: at age 13, future retainers competed in a median of 13 meets versus 8 for future dropouts; at age 14 this widens to 17 versus 8. From age 15 onwards the trajectories diverge further. Retainers peak at 19 meets at age 15 and sustain near that level through age 17. Future dropouts decline from 8 meets at age 14 to a median of 3 at age 15, 0 at age 16, and 0 thereafter. Two complementary patterns are therefore visible in the same data: (i) substantial baseline differences between the eventual retainer and dropout groups by ages 13–14, and (ii) a progressive within-athlete pull-back among future dropouts that becomes most visible across the age-14-to-15 transition. We test these two patterns separately below.

[**Figures 1 and 2 about here**]

[**Table 2 about here**]

## 3.3 Survival visualization

Overall Kaplan–Meier retention (Supplementary Figure S3A) shows that half of the cohort had ceased active competition within 3 years of baseline; 75% had ceased within 5 years. The age-17 floor (the transition from youth to junior competition) marks the steepest acceleration in dropout. Sex-stratified retention curves (Supplementary Figure S3B) overlap throughout the follow-up window: a log-rank test detected no overall sex difference (χ² = 0.95, p = 0.33). When the cohort is stratified by competition volume across ages 15–16 (Figure 3), retention curves separate clearly and monotonically: athletes who competed in 31 or more meets across ages 15–16 retained 71% senior activity, while athletes who competed in none retained only 4%. (Note: this stratification is descriptive only; the formal effect estimates use baseline-only predictors, below.) Stratifying by number of championship types entered before age 17 (Supplementary Figure S4) reveals the same pattern.

[**Figure 3 about here**]

## 3.4 Primary analysis: prospective logistic regression for senior retention

To avoid look-ahead between predictors and outcome, the primary analysis is a logistic regression for the binary outcome *active senior status* (≥2 registered competitions in any calendar year at age ≥20) using only baseline-window predictors (ages 13–14, measured before the qualification-milestone window). Models were fitted in a nested stepwise sequence (Table 3) and evaluated with 5-fold cross-validated AUC.

Sex alone produced a near-chance discrimination (CV-AUC = 0.541). Adding baseline Tyrving performance increased AUC modestly to 0.607; adding early specialization (HHI) added nothing further (AUC = 0.600). Adding pre-milestone competition volume (sum of meets at ages 13–14) raised AUC substantially to **0.751**, with an odds ratio of 2.40 per SD (95% CI [2.07, 2.78], *p* < .001). Higher baseline competition volume was therefore associated with 2.4-times higher odds of senior retention per one-SD increase. Specialization (HHI) became significantly associated with retention once volume was entered (OR = 1.35 per SD; *p* < .001) — *higher* baseline HHI (more concentration in fewer event categories) predicted *higher* retention, a finding we return to in §3.10 and the Discussion.

[**Table 3 about here**]

## 3.5 Structural controls do not change the picture

Reviewers of register-based research reasonably ask whether structural factors — region, relative age effects, club size — might confound apparent behavioral effects. Adding region (3-level), birth-quarter (Q1- and Q4-born indicators for relative-age effects), and standardized club-size to the full Table 3 model produced no material change in the volume coefficient (OR = 2.40 with controls vs. 2.40 without; +0.4%) and none of the structural covariates was significantly associated with retention (all p > .14; Supplementary Table S13). The substantive findings are therefore robust to plausible structural confounders.

## 3.6 Progressive pull-back versus baseline heterogeneity

The trajectories in Figure 2 are consistent with two interpretations: (i) future retainers and future dropouts represent distinct *behavioral typologies* visible already at ages 13–14, or (ii) future dropouts undergo a *within-athlete pull-back* between ages 14 and 15 that distinguishes them from athletes whose level is preserved. We tested these two interpretations directly by entering both the baseline level (volume at age 14) and the within-athlete change (volume at age 15 minus volume at age 14) into a logistic regression, restricted to athletes still active at age 14 (n = 1,914) to avoid pre-baseline dropout (Table 4 / Supplementary Table S14).

Both predictors contributed substantially and independently. The age-14 volume level was strongly associated with retention (OR = 2.79 per SD, 95% CI [2.37, 3.28], *p* < .001). The within-athlete change from age 14 to age 15 was *almost as strongly* associated (OR = 2.44 per SD, 95% CI [2.10, 2.83], *p* < .001) — that is, a one-SD greater decline between ages 14 and 15 was associated with 2.4-times *lower* retention odds. Adding the change variable to the level-only model more than doubled pseudo-*R*² (0.113 → 0.227). Both early behavioral heterogeneity and a within-athlete pull-back are present in our data; they are not substitutes.

[**Table 4 about here**]

## 3.7 Time-aligned behavior vs. performance

A reviewer concern with our earlier framing was that "behavior beats performance" compared post-baseline volume (ages 15–16) with baseline performance (ages 13–14), giving the behavioral predictor a temporal advantage. In a fully time-aligned comparison — both predictors measured during the baseline window of ages 13–14 — behavior still substantially out-predicts performance: AUC = 0.607 for sex + baseline Tyrving, AUC = 0.740 for sex + ages-13–14 volume, AUC = 0.737 for both combined (Supplementary Table S15). The performance variable adds essentially nothing once early competition volume is known. The substantive direction of our earlier finding survives the time-aligned comparison.

## 3.8 Landmark analysis: post-baseline behavior among continuing athletes

For readers interested in the question "given that an athlete reaches age 16 actively, what predicts subsequent retention?", we re-fit the full model in athletes with at least one registered result at age 16 (n = 1,167), with follow-up measured from age 16 forward (Supplementary Table S8). Competition volume across ages 15–16 remained the dominant predictor (HR = 0.60 per SD in Cox, 95% CI [0.54, 0.66], C-index = 0.74). A complementary analysis excluding athletes with vol_milestone = 0 produced HR = 0.51 (Supplementary Table S12). The Cox model fitted from baseline using post-baseline behavioral covariates is reported in Supplementary Table S17; we have not used it as the primary estimate because the predictor and the early portion of the at-risk window overlap in time.

## 3.9 Prospective early-warning thresholds

Because the primary analysis uses only baseline-window data, we can compute calibration metrics for a prospective early-warning rule applied at the end of the baseline window (i.e., for federation use after each athlete's age-14 season). Table 6 reports sensitivity, specificity, PPV, and NPV at five candidate thresholds on pre-milestone competition volume. At a moderate threshold (vol < 10 meets across ages 13–14, flagging 26.4% of the cohort), PPV is 0.94 — among flagged athletes, 94% subsequently failed to retain senior activity. Sensitivity is 0.30 at this threshold (i.e., the rule identifies 30% of all eventual non-retainers). Lower thresholds (vol < 5) suit highly targeted intervention (PPV 0.93, 9% flagged); higher thresholds (vol < 15) broaden the screen (PPV 0.93, 43% flagged). The high PPV partly reflects the high base rate of non-retention (84%); an unsophisticated "everyone drops out" rule already achieves PPV = 0.84. The behavioral threshold improves precision by 9–10 percentage points over base-rate prediction while providing graduated sensitivity that base-rate prediction cannot.

[**Table 6 about here**]

## 3.10 Specialization is protective in our data

The HHI coefficient in our primary model indicated that higher baseline event-category concentration (HHI) is associated with *higher* senior retention. The combined-cohort estimate was OR = 1.35 per SD of HHI (95% CI [1.16, 1.57], *p* < .001 in the primary baseline-only logistic regression; HR = 0.80 in the time-to-cessation Cox model, Supplementary Table S16). The effect was present in both cohorts (Cohort A OR = 1.24, Cohort B OR = 1.58). Within our data, athletes whose ages-13–14 results were more concentrated in fewer event categories — that is, those who specialized earlier — were *more* likely to retain senior activity, not less. This is contrary to the international diversification literature for *peak performance* (Côté & Hancock, 2016; Güllich et al., 2022), and we discuss possible reasons in §4.6.

## 3.11 Cross-cohort replication and sensitivity

The primary baseline-only logistic regression was re-estimated separately in each birth-year cohort. The pre-milestone volume effect replicated: Cohort A OR = 2.22 (95% CI [1.86, 2.64]); Cohort B OR = 2.79 [2.17, 3.58]; both *p* < .001 (see Supplementary Table S17). All other effects replicated in direction; sex was significant in Cohort A but not Cohort B, as previously reported. The volume effect was robust to outcome-definition sensitivity (Supplementary Table S9): odds ratios were 2.79, 3.08, and 2.94 for outcomes ≥1, ≥2, and ≥2-in-two-years respectively. The cluster-robust SE estimator at the club level preserved coefficient estimates (Supplementary Table S2). The E-value for the milestone-window volume effect (HR = 0.35 in the post-baseline Cox specification, Supplementary Table S17) was 5.16, with a corresponding lower-CI E-value of 4.70 (VanderWeele & Ding, 2017): an unmeasured confounder would need a risk-ratio association exceeding 5 with both predictor and outcome to nullify the effect, well above any observed covariate.

In summary: across two independent birth-year cohorts spanning a 5-year window, baseline-window competition volume (ages 13–14) was the dominant prospective predictor of senior retention (OR 2.40 per SD, AUC 0.751). The effect is robust to structural controls, to outcome definition, to clustering, to missing-data treatment, and to alternative model specifications. Both early behavioral heterogeneity and within-athlete pull-back across the age-14-to-15 transition contribute substantially and independently. Specialization (higher HHI in baseline events) is protective in our data, a finding that runs against the international diversification literature for elite peak performance.
