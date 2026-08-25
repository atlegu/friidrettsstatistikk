# Pulling back before dropping out: Behavioral disengagement precedes exit from Norwegian youth track and field — a 14-year register study

**Running title:** Behavioral disengagement precedes exit from youth track and field

**Keywords:** youth sport, dropout, athlete retention, longitudinal, track and field, behavioral indicators, sport commitment

---

## Abstract

Withdrawal from youth sport is theorized as a gradual process, but its longitudinal behavioral signature has been hard to observe directly. We used Norway's national competition register to follow 2,123 athletes who competed as 13–14-year-olds in a regional youth track-and-field meet (birth years 1998–2002) for up to 14 years. In a prospective logistic regression for active senior status (≥2 registered results in a calendar year at age 20+) using only ages-13–14 predictors, competition volume was the dominant predictor (OR = 2.40 per SD, 95% CI [2.08, 2.76]; cross-validated AUC = 0.751; calibration slope 0.96), outperformed age-normed performance measured in the same window, was robust to structural controls and club random effects, and replicated across two adjacent birth cohorts. Exit-aligned trajectories showed that withdrawal was gradual for most athletes: median volume fell 12 → 10 → 9 → 4 meets across dropouts' last four seasons, 74% of those leaving at 16 or later had a reduced-but-nonzero season before their final season, and among athletes still active at 16, both earlier volume (OR = 3.04) and decline across ages 15–16 (OR = 1.88) predicted senior status. Higher within-sport event concentration predicted higher retention, robust to count-dependence checks, a construct distinct from multisport diversification. A register-based flag at the end of the age-14 season (< 10 meets) identifies the 26% of athletes whose senior retention is 6%, versus 20% among the unflagged (PPV = 0.94 against an 84% base rate; sensitivity 0.30): a testable targeting rule for retention-supporting outreach in open-entry systems.

---

## 1. Introduction


Organized youth sport is widely promoted for its benefits for physical health, psychosocial development, and social connection (Eime et al., 2013), benefits that presuppose that young people stay involved. Attrition from organized competition during adolescence is substantial across countries and sports (Crane & Temple, 2015), and track and field is no exception: in a 25-year Norwegian follow-up, roughly 82% of promising track and field athletes identified in adolescence had left the sport within 14 years (Enoksen, 2011), and in the broad-participation cohort studied here, fewer than half of those competing at ages 13–14 were still competing at 17 (Section 3).

Terminology in this literature is often ambiguous, so we fix ours at the outset. Following Battaglia et al. (2024), we distinguish *withdrawal*, the gradual process of disengaging from a sport, from *dropout*, the state of no longer participating. Our outcome is dropout from organized track and field competition specifically, not from sport or physical activity in general: an athlete who leaves track and field for another sport is, from the register's perspective, a dropout, a boundary we return to in the limitations. When and how these withdrawals unfold has been difficult to determine with existing methods.

## 1.1 Withdrawal as a deliberative, gradual process

Qualitative research indicates that *withdrawal is a process* rather than a discrete event (Eliasson & Johansson, 2021), so some form of decline over a period of time should be expected. The Sport Commitment Model (Scanlan et al., 1993, 2016) describes how the desire and resolve to continue are shaped by enjoyment, personal investments, involvement opportunities, attractive alternatives, and social constraints; Kretchmar's (2000) account of meaning in movement similarly ties sustained participation to the meaningfulness individuals assign to the activity, not necessarily to success.

The most developed account of this process view comes from sociology. Eliasson and Johansson (2021) applied Ebaugh's (1988) role-exit framework, in which leaving a social role proceeds through stages of first doubts, seeking and weighing alternatives, a turning point, and the construction of an ex-role identity, to youth sport, interviewing adolescent girls and their parents. Withdrawal resulted from interacting changes in the sport organization, the athletes' broader lives, and the expectations attached to the young-athlete role; the process could be long, emotionally demanding, and decreasingly reversible. Survey evidence from Norwegian youth complements this picture: stated reasons for leaving organized sport are diverse and patterned by social background, with sport expenses cited more often by minority youth from less-resourced families (Espedalen & Seippel, 2024).

Groups of athletes also appear to differ in how they respond when competitive demands increase. Norwegian participation research documents strong variation in involvement: training investment varies widely (Bakken, 2019), and a significant minority hold "heavy" involvement motives (intense love of the game or career pursuits), while the larger group appreciate "lighter" involvement built on fun, exercise, and belonging, quitting more readily when sport becomes too demanding alongside everything else (Espedalen, 2025). The Sport Commitment Model's distinction between enthusiastic and constrained commitment gives such divergent responses a theoretical basis (Scanlan et al., 2016). Consistent with the idea that such differences leave behavioral traces well before exit, retrospective comparisons of developmental activities show that youth ice-hockey players who later dropped out already differed from persisting peers in their earlier training patterns, for example taking up intense sport-specific off-ice training at younger ages (Wall & Côté, 2007). We therefore expect casually engaged participants to show declining participation through the teenage years, while deeply committed participants sustain theirs.

## 1.2 The quantitative gap

These theories indicate what might happen over time as participants continue or withdraw from their sport(s), but none provides direct longitudinal behavioral evidence. Withdrawn athletes are systematically harder to recruit into surveys (Eime et al., 2013), and the hypothesized timescale (1–3 years) exceeds most prospective follow-up windows: Sarrazin et al.'s (2002) 21-month handball study is unusually long and still does not bridge the adolescent-to-junior transition. A separate quantitative tradition studies correlates of dropout and development, such as relative age effects (Cobley et al., 2009) and specialization (DiFiori et al., 2014; Jayanthi et al., 2015; Côté & Hancock, 2016; Güllich et al., 2022), and studies of proximal psychological constructs such as burnout, motivation, and peer relations (Kuokkanen et al., 2026; Worley & Smith, 2026; Zhong et al., 2026); prospective predictors of adolescent team-sport dropout have been meta-analyzed (Back et al., 2022), and in athletics, rankings databases have been used to study *performance* trajectories across the youth-to-senior transition (Kearney & Hayes, 2018). The *participation* trajectory itself, competition behavior recorded entry by entry, has not, to our knowledge, been examined: an observable proxy for the engagement balance (the net of enjoyment and investment against constraint in the Sport Commitment Model) whose course the qualitative literature describes but cannot measure.

## 1.3 The present study

Track and field suits such a test: participation choices are visible event by event, entries are individually chosen rather than coach-selected (Section 2.2), performances are objectively measured, and a single national register captures every sanctioned result. We studied 2,123 Norwegian youth athletes longitudinally for up to 14 years using the federation's competition register (see Figure 1) and tested three hypotheses. First, because withdrawal is described as a protracted, deliberative process (Ebaugh, 1988; Eliasson & Johansson, 2021) and because heavily and lightly involved participants are expected to respond differently to rising competitive demands (Espedalen, 2025; Scanlan et al., 2016), we predicted that the *participation trajectories* of future retainers and future dropouts would diverge before the final registered season, in two separable forms that we test separately: early between-athlete differences in level, and within-athlete decline. Second, because the determinants of sport commitment are experiential and volitional (enjoyment, investment, alternatives, constraint) rather than ability-based (Scanlan et al., 1993, 2016), we predicted that *behavioral engagement indicators* would predict subsequent senior retention better than *baseline performance* would. Third, as a robustness expectation rather than a theory-derived prediction, the pattern should *replicate* internally across two adjacent birth-year cohorts. Throughout, *competition behavior* is an observable behavioral indicator, not a direct measure of motivation, whose temporal structure can be compared with process accounts; convergence between register patterns and the qualitative literature strengthens both.


---

## 2. Method


## 2.1 Design

This retrospective longitudinal cohort study uses the national competition register as its only data source; the cohort is the entire population satisfying the inclusion criterion, so estimates describe that population. We follow the Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) guideline where relevant (von Elm et al., 2007).

## 2.2 Setting and inclusion

Norwegian youth track and field is organized as a low-threshold, open-entry system. Up to age 15, essentially all meets are open to all club-registered athletes: there are no qualifying standards, no roster selection, and no coach-controlled gatekeeping (Norges Friidrettsforbund, 2026). (The exception, occasional invitational regional-team matches for 14–15-year-olds, does not gate ordinary competition.) Athletes and their families decide which meets and events to enter; entry fees are ordinarily paid by the club, participation is actively encouraged, and travel distances are typically short. The first genuinely selective competition is the national youth championship (Ungdomsmesterskapet, UM), open from the calendar year athletes turn 15, with event-specific qualifying standards. Two design consequences follow: before age 15, meet counts primarily express the athlete's own choice rather than selection or entry costs, which licenses interpreting ages-13–14 volume as a behavioral indicator of engagement; and the ages-15–16 window coincides with the first selective gate (UM), which is why the pre-milestone (13–14) and milestone (15–16) windows are analyzed separately.

The cohort comprises all athletes who competed in any of six consecutive autumn editions (2011–2016) of a regional grassroots youth meet held simultaneously at three venues in eastern, western, and mid Norway (the last also serving the northern districts). Athletes were 13–14 and were entered by their district federations under district quotas, with no qualifying performance standard and no entry fee; this soft selection into the baseline meet is a design feature: disengagement trajectories arise from a baseline of demonstrable engagement. Birth years were restricted to 1998–2002 (boundary years 1997 and 2003 had only one eligible edition), and athletes appearing in both a 13- and a 14-year-old edition were de-duplicated to the earlier one (Supplementary Figure S0). For cross-cohort replication, participants were partitioned into Cohort A (births 1998–2000, baseline meets 2011–2014; n = 1,301) and Cohort B (births 2001–2002, baseline meets 2014–2016; n = 822). Athletes were retained regardless of club transfers (27.8% recorded results for two or more clubs), so changing club does not register as dropout. The total cohort comprised 2,123 athletes (996 male, 1,103 female, 24 with unknown sex), generating 230,868 competition entries through the most recent register update (April 2026).

## 2.3 Follow-up window

Each athlete was followed from baseline through the most recent complete competition season (2025): maximum 14 years (births 1998), minimum 9 years (births 2002). All athletes had follow-up past the senior age threshold (age 20).

## 2.4 Variables

### 2.4.1 Outcome

Active senior status was coded 1 if the athlete had ≥2 registered results in any calendar year at age 20+ (the senior age), and 0 otherwise; two results exclude sporadic returners while capturing athletes entering separate events at one meet. Sensitivity to this definition was tested with two alternatives (≥1 senior-age result; ≥2 results in each of two distinct senior-age years; Supplementary Table S9). A secondary time-to-event outcome (time to last active season, right-censoring athletes active in 2024+) supports Kaplan–Meier and Cox analyses (Section 2.5.4).

### 2.4.2 Performance

Each result was scored in Tyrving points, the Norwegian federation's age-norm system (Norges Friidrettsforbund, 2024): a published table gives, per event × sex × age, a reference performance worth 1,000 points and a per-unit quotient (values capped at 1,500 to suppress data-entry errors). We computed tyrving_best (baseline maximum), tyrving_peak_pre15, and per-age scores (yielding a baseline performance trajectory, age-14 minus age-13).

### 2.4.3 Specialization

For every athlete-year we counted the event categories entered (sprint, middle-distance, long-distance, hurdles, jumps, throws, combined events, race walking, relay) and computed a Herfindahl-Hirschman concentration index, $HHI = \sum_{i=1}^{k} s_i^2$, where $s_i$ is the share of the athlete's results in category $i$. HHI ranges from 1/k (fully diversified) to 1 (single category). Key variables: hhi_early (first three active seasons), hhi_age_15, and their change. Combined events appear in the register both as a total and as separate constituent results; constituents are counted in their natural categories (multi-event athletes register as diversified; stand-alone combined rows <0.1%). Categories co-occur unevenly (sprints and hurdles share training demands; throws transfer little); the HHI treats them symmetrically (see the limitations).

### 2.4.4 Behavioral engagement

For each athlete and age-year from 13 to 18 we counted distinct meets attended (vol_age_X; a multi-event competition counts as one meet) and total results (res_age_X, which also define active seasons: ≥2 results in a calendar year). Composites: vol_pre_milestone (meets at 13–14), vol_milestone (15–16), their difference, and n_champ_types (championship types before 17). These are observable behavioral markers, not direct measures of motivation or commitment.

### 2.4.5 Controls

Sex (M/F as registered), birth quarter (Q1–Q4), baseline region (eastern, mid, or western Norway, by venue), and club size in the baseline year (registered athletes in the same club).

## 2.5 Statistical analysis

### 2.5.1 Primary analysis: prospective logistic regression

The principal inferential model is a logistic regression for active senior status using only baseline-window predictors (ages 13–14): sex, baseline Tyrving, early HHI, and pre-milestone volume, fitted in a nested sequence (L1: sex; L2: + Tyrving; L3: + HHI; L4: + volume) to characterize each variable class's unique contribution. Continuous covariates were z-standardized (per-SD effects; standardization preceded cross-validation), all nested models were fitted on the fixed L4 complete-case sample, and discrimination was assessed by 5-fold stratified CV-AUC (± = SD across folds), with calibration slope and intercept computed on the cross-validated predictions. Restricting predictors to ages 13–14 keeps the primary estimate unambiguously prospective, avoiding the mechanical zero-volume overlap that post-baseline predictors carry.

### 2.5.2 Structural controls

The full model was refit adding region, birth-quarter indicators (Q1, Q4), and standardized club size, comparing the stability of the volume coefficient with and without controls (Supplementary Table S13).

### 2.5.3 Within-athlete pull-back vs. baseline heterogeneity

To disentangle early behavioral heterogeneity from within-athlete pull-back, we fit a logistic regression on athletes still active at age 14 (1,914; complete-case model n = 1,549) including both the volume level at age 14 and the change from 14 to 15 (Table 4). Because a change score can span the exit itself, two analyses probe the within-athlete claim directly: exit-aligned trajectories (volume one to three seasons before each dropout's own final active season) and a contamination-free change model among athletes still active at 16 (level at 15 plus change 15→16 predicting senior status; Supplementary Table S19). Prospective early-warning thresholds on pre-milestone volume (classification performance at candidate cut-offs at the end of the age-14 season, with bootstrap CIs) are reported in Table 6.

### 2.5.4 Time-to-cessation survival analysis (secondary)

Time from baseline to last active season was modeled with Cox proportional hazards regression (Cox, 1972), with a baseline-only primary specification (Supplementary Table S16), a landmark analysis among athletes active at age 16 (van Houwelingen, 2007; Supplementary Table S8), and a post-baseline specification interpreted with overlap caveats (Table 5). Proportional-hazards checks, E-values (VanderWeele & Ding, 2017), cluster-robust errors, and period- and sex-specific estimates are in the Supplementary Methods; hazard ratios are descriptive, not causal.

### 2.5.5 Sample size, missing data, and replication

Because the design observes the full eligible population, classical a-priori power analysis does not apply; a detection-capacity analysis (Supplementary Methods; Supplementary Table S4) shows the design could detect hazard ratios ≥1.07 and odds ratios ≥1.20 per SD, well below effect sizes typical of prior dropout research (Back et al., 2022). Missing values (Tyrving ~20%, HHI ~10%) were handled by complete-case analysis (n = 1,704), with multiple imputation (m = 20, Rubin-pooled) as the principal sensitivity plus included-versus-excluded comparison, mean imputation, and club-clustered standard errors (Supplementary Tables S21, S25, S5, S2; sample flow: Supplementary Table S12). Club-level confounding was probed via the intraclass correlation of volume across baseline clubs and a refit with club random intercepts (Supplementary Table S22). The primary and secondary models were re-estimated separately by birth cohort.

### 2.5.6 Software

Analyses used Python 3.13 with lifelines (Davidson-Pilon, 2019) and scikit-learn (Pedregosa et al., 2011); figures used matplotlib (Hunter, 2007). All stochastic steps used fixed random seeds; exact package versions accompany the code, to be deposited in a public repository upon acceptance. Data availability is described in Section 2.7.

## 2.6 Sex and gender

Following SAGER guidance (Heidari et al., 2016), all primary analyses include sex as a covariate, with sex-stratified analyses in Supplementary Table S7; "sex" reflects the federation's binary registration variable; the register holds no gender-identity information.

## 2.7 Ethics

The competition records analyzed are publicly accessible via the Norwegian Athletics Federation's online register; the derived dataset links them to dates of birth and is therefore not redistributed (GDPR). No personally identifying information appears in this manuscript. Norway's Health Research Act (Helseforskningsloven §4) exempts secondary use of register data of this kind from formal approval by a Regional Committee for Medical and Health Research Ethics. This exemption concerns the research use of the register; it does not extend to operational uses of similar data by sport organizations, which would require their own legal basis (see Section 4.8).


---

## 3. Results


## 3.1 Cohort characteristics

The cohort comprised 2,123 athletes (52.0% female): 1,301 in Cohort A and 822 in Cohort B, closely matched at baseline (mean Tyrving 666 and ~41% active at 17 in each; Table 1). Senior retention (≥1 season with ≥2 results at age 20+) was 15.8% in Cohort A and 17.3% in Cohort B (combined 16.4%). The proportion still active in 2024+ was 5.8% (A) and 10.8% (B), reflecting Cohort B's shorter follow-up (fixed-window outcome at ages 20–22: 15.3% vs 16.7%; Supplementary Table S24).


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


## 3.2 Competition-volume trajectories diverge by ages 13–14

Figure 2 presents the central behavioral observation (Figure 1 shows the conceptual model): median competitions per year by age, plotted separately for eventual retainers (n = 348) and non-retainers (n = 1,775). The groups already differ at baseline (medians of 13 vs. 8 meets at age 13, and 17 vs. 8 at age 14), and from age 15 they diverge sharply: retainers peak at 19 meets and sustain that level through 17, while future dropouts fall from 8 to 3 to 0. Baseline differences and within-athlete pull-back are separated formally in Section 3.5.

Kaplan–Meier curves summarize the attrition (medians in Table 2): half the cohort ceased active competition within 3 years, 75% within 5, steepest at age 17, the youth-to-junior transition (Supplementary Figure S2). Sex-stratified curves overlap (log-rank χ² = 0.95, *p* = .33). Stratifying descriptively by ages-15–16 volume yields monotonically separated curves, 71% senior retention with ≥31 meets vs. 4% with none (Figure 3), and stratifying by pre-17 championship types shows the same pattern (Supplementary Figure S3). Formal estimates use baseline-only predictors below.


![Figure 1](figures/fig1_conceptual_model.png)

**Figure 1.** A behavioral-marker model of youth-sport disengagement. The diagram shows the relationship being tested: theoretical mechanisms hypothesized by the Sport Commitment Model and the role-exit / withdrawal-as-process tradition (left) are not directly observed, but are predicted to leave a footprint in measurable competition behavior (centre), which precedes the outcome of active senior retention (right).

![Figure 2](figures/fig2_volume_trajectory.png)

**Figure 2.** Competition volume trajectory by senior-retention status. Median competitions per year (with interquartile range as shaded band) plotted by athlete age (13–18), separately for athletes who retained active senior status (≥2 results in any year at age ≥20; n = 348) and those who did not (n = 1,775). The dashed vertical line at age 15 marks the first qualification milestone (Norwegian Youth Championships). Future retainers and future dropouts already differ at ages 13–14; the gap widens further across the age-14-to-15 transition.



## Table 2. Competition volume trajectory by senior-retention status (median competitions per year and IQR)

| Group | N | Age 13 | Age 14 | Age 15 | Age 16 | Age 17 | Age 18 |
|---|---|---|---|---|---|---|---|
| Senior retainers (active age ≥20) | 348 | 13 [6–21] | 17 [10–25] | 19 [11–27] | 18 [10–26] | 17 [10–24] | 14 [7–20] |
| Dropouts (last active age <20) | 1,775 | 8 [4–13] | 8 [3–14] | 3 [0–11] | 0 [0–7] | 0 [0–2] | 0 [0–0] |

*Note.* Values are median number of meets per year [IQR]. Future retainers and future dropouts already differ at ages 13–14; the gap widens further across the age-14-to-15 transition.

---



![Figure 3](figures/fig3_km_vol_quintile.png)

**Figure 3.** Kaplan–Meier retention curves stratified by total competition volume across ages 15 and 16 (descriptive). Strata are: 0 meets, 1–5 meets, 6–15 meets, 16–30 meets, and 31+ meets. Athletes in the highest stratum retained 71% senior activity at follow-up year 14; athletes in the lowest stratum retained 4%. (Note: this descriptive stratification uses post-baseline measurement; primary effect estimates in Table 3 use only baseline-window predictors.)


## 3.3 Primary analysis: prospective logistic regression for senior retention

**Among baseline-window predictors (ages 13–14), competition volume provided the largest incremental contribution to prospective discrimination of senior retention 6–14 years later: OR = 2.40 per SD (95% CI [2.08, 2.76], *p* < .001), cross-validated AUC = 0.751.** Models for *active senior status* were fitted stepwise with baseline-only predictors (avoiding look-ahead; Table 3): CV-AUC rose 0.541 (sex) → 0.607 (+ Tyrving) → 0.600 (+ HHI) → 0.751 (+ volume), with well-calibrated predictions (calibration slope 0.96, Brier 0.122; Supplementary Table S23). Once volume was entered, HHI became significantly associated with retention (OR = 1.36 per SD, 95% CI [1.17, 1.57], *p* < .001): *higher* concentration in fewer event categories predicted *higher* retention (§3.9; §4.6).


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


## 3.4 Structural and club-level controls do not change the picture

Adding region, birth quarter (Q1/Q4), and club size left the volume coefficient unchanged (OR = 2.40 both ways); no structural covariate was significant (*p* > .14; Supplementary Table S13). A quarter of volume variance lies between clubs (ICC = 0.25, 277 clubs), but with club random intercepts the coefficient was, if anything, larger (OR = 2.58, 95% CI [2.27, 2.93]; Supplementary Table S22): the association holds within clubs.

## 3.5 Progressive pull-back versus baseline heterogeneity

**Early behavioral heterogeneity and within-athlete pull-back contribute independently; they are not substitutes.** Three analyses separate the two readings of Figure 2.

First, level and change. Among athletes still active at age 14 (1,914; complete-case model n = 1,549), the age-14 volume level (OR = 2.79 per SD, 95% CI [2.37, 3.28]) and the change from age 14 to 15 (OR = 2.44, 95% CI [2.10, 2.83]; both *p* < .001) contributed independently; adding change more than doubled pseudo-*R*² (0.113 → 0.227; Table 4).

Second, because a change score spanning the exit could conflate pull-back with the exit itself, we repeated the test where no exit can contaminate it: among athletes still competing at age 16 (≥2 results; n = 1,075), volume at 15 (OR = 3.04, 95% CI [2.55, 3.62]) and change from 15 to 16 (OR = 1.88, 95% CI [1.60, 2.20]; both *p* < .001) predicted senior status four or more years later (CV-AUC = 0.758): decline predicts exit among athletes who are all, at measurement, still active.

Third, exit-aligned trajectories. Aligned to each dropout's own final active season (n = 1,139 with final seasons at ages 15–19), median volumes at T−3, T−2, T−1, and T were 12, 10, 9, and 4 meets, a within-athlete taper rather than a cliff. 95% were still competing in their penultimate season; among final seasons at 16+ (n = 795), 74% showed a *reduced-but-nonzero* penultimate season relative to their earlier personal peak, 6.5% a gap year, and only 19% exited directly from peak volume (Supplementary Table S19).


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

*Note.* Pseudo-*R*² rose from 0.113 (M1) to 0.227 (M2): within-athlete change adds substantial information conditional on baseline level. A one-SD greater decline from age 14 to age 15 was associated with 2.4-times lower retention odds, conditional on level at age 14. Both baseline level and within-athlete pull-back contribute substantially and independently.

---


## 3.6 Time-aligned behavior vs. performance

In a fully time-aligned comparison, with behavior and performance both measured at ages 13–14 to remove any temporal advantage, behavior still discriminates better: AUC = 0.607 for sex + baseline Tyrving, 0.740 for sex + ages-13–14 volume, 0.737 for both combined (Supplementary Table S15). A within-baseline performance *trajectory* (Tyrving change from 13 to 14) raised the performance-only AUC only to 0.640 (n = 1,350), still well short of volume.

Volume and performance were moderately correlated (Spearman ρ = .29 with baseline Tyrving; .45 with pre-15 peak; .48 for milestone volume vs. age-15 Tyrving). The volume–retention association also held *within* performance strata: splitting the cohort by baseline-Tyrving quartile and pre-milestone volume (above/below median), above-median volume was associated with higher senior retention in every quartile: 16.3% vs. 10.0% in the lowest-performing quartile, then 18.0% vs. 4.2%, 25.8% vs. 4.7%, and 34.1% vs. 13.2% in the highest. Volume is related to, but clearly not reducible to, performance level.

## 3.7 Landmark analysis: post-baseline behavior among continuing athletes

Conditioning on athletes active at age 16 (≥1 result; n = 1,167), volume across ages 15–16 was the largest contributor to subsequent cessation risk (HR = 0.60 per SD, 95% CI [0.54, 0.66], C-index = 0.735; complete-case n = 960; Supplementary Table S8); excluding athletes with milestone volume = 0 gave HR = 0.51 (Supplementary Table S11). The baseline-only Cox model is in Supplementary Table S16 and a period-specific decomposition in Table 5 (diagnostics and descriptive companions: Supplementary Tables S1, S6, S10, S17; Supplementary Figures S1, S4). The baseline-start Cox model with post-baseline covariates is not a primary estimate (predictor and at-risk window overlap); its contamination-free analogue is the change model in Section 3.5.


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

*Note.* Period-specific Cox estimates from the post-baseline specification with covariates measured at ages 15–16 and ≤17. The early-window HR for ages-15–16 volume partly reflects operational overlap between predictor and outcome (low milestone volume is mechanical for athletes who drop out before age 15); this estimate should be read as descriptive of the time-varying association rather than as an independent prospective effect. Substantively, the protective association attenuates across follow-up, consistent with a proximal disengagement-marker interpretation.

---


## 3.8 Prospective early-warning thresholds

Because the primary analysis uses only baseline-window data, a prospective rule can be evaluated at the end of the age-14 season (Table 6, with bootstrap CIs). At a moderate threshold (vol < 10 meets across ages 13–14, flagging 26.4%), senior retention was 5.7% among flagged athletes versus 20.2% among unflagged, a 3.5-fold difference in retention prospects (PPV = 0.94, sensitivity = 0.30). Lower thresholds (< 5; 9.3% flagged) suit targeted outreach, higher (< 15; 43.1%) broaden the screen. Two properties discipline use: PPV partly reflects the 84% base rate (~10-point precision gain), and NPV = 0.20 means unflagged athletes are *not* "safe": four in five also fail to retain. The flag concentrates risk; it certifies no one's continuation.


## Table 6. Prospective early-warning thresholds (pre-milestone volume, ages 13–14)

| Threshold (flag if vol <) | Flagged % | Sensitivity | Specificity | PPV | NPV | Senior retention, flagged | Senior retention, unflagged |
|---|---|---|---|---|---|---|---|
| 5 meets | 9.3 | 0.10 [0.09, 0.12] | 0.96 [0.94, 0.98] | **0.93** [0.89, 0.96] | 0.17 [0.16, 0.19] | 7.1% [3.6, 11.3] | 17.3% [15.7, 19.1] |
| 8 meets | 19.8 | 0.22 [0.20, 0.24] | 0.93 [0.90, 0.96] | **0.94** [0.92, 0.96] | 0.19 [0.17, 0.21] | 5.7% [3.6, 7.9] | 19.0% [17.2, 21.0] |
| 10 meets | 26.4 | 0.30 [0.28, 0.32] | 0.91 [0.88, 0.94] | **0.94** [0.92, 0.96] | 0.20 [0.18, 0.22] | 5.7% [3.9, 7.7] | 20.2% [18.3, 22.2] |
| 15 meets | 43.1 | 0.48 [0.46, 0.50] | 0.82 [0.77, 0.85] | **0.93** [0.91, 0.95] | 0.24 [0.21, 0.26] | 7.0% [5.4, 8.7] | 23.5% [21.1, 25.9] |

*Note.* Classification performance of pre-milestone (ages 13–14) competition volume as a prospective early-warning indicator, applicable at the end of an athlete's age-14 season, before the qualification window opens. All metrics are computed on one denominator (full cohort, n = 2,123); brackets are 2,000-replicate bootstrap 95% CIs. PPV is the proportion of flagged athletes who subsequently failed to retain senior activity. The final two columns give the absolute retention contrast: at the < 10 threshold, 5.7% among flagged vs. 20.2% among unflagged athletes (a 3.5-fold difference). The high PPV partly reflects the population's 84% non-retention base rate (the threshold improves precision by ~10 percentage points over base-rate prediction), and the NPV of ≈ 0.20 means unflagged athletes are not "safe": roughly four in five of them also fail to retain. Calibration of the underlying model is reported in Supplementary Table S23.

---


## 3.9 Within-sport event concentration and retention

Higher baseline HHI (more event-category concentration) predicted *higher* senior retention: OR = 1.36 per SD (95% CI [1.17, 1.57], *p* < .001) in the primary regression, HR = 0.80 in the Cox model, and present in both cohorts (A OR = 1.24, B OR = 1.58). Because HHI is bounded below by 1/(result count), we stress-tested for count-dependence; the association survived every check: restriction to ≥5 and ≥8 early results (OR = 1.38, 1.39) and a finite-sample-corrected index (OR = 1.39, 95% CI [1.20, 1.60]; Supplementary Table S20). It is not a small-count artifact. The index captures concentration *within* track and field, a different construct from multisport diversification; the distinction is developed in §4.6.

## 3.10 Cross-cohort replication and sensitivity

Re-estimated by cohort, the pre-milestone volume effect replicated: Cohort A OR = 2.22 (95% CI [1.86, 2.64]), Cohort B OR = 2.79 (95% CI [2.17, 3.58]), both *p* < .001 (Table 7); sex was significant only in Cohort A.


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


On the primary specification, the effect was robust to outcome definition (OR = 2.29, 2.40, 2.26 across the three definitions; Supplementary Table S9), to the fixed-window outcome (ages 20–22: OR = 2.43; Supplementary Table S24), to multiple imputation (OR = 2.34, 95% CI [2.07, 2.66]; Supplementary Table S21), and to cluster-robust standard errors (Supplementary Table S2). For unmeasured confounding, converting the primary odds ratio for this common outcome to a risk ratio (≈1.55) gives an E-value of 2.5 (baseline-only Cox: 2.6; Supplementary Table S3): a confounder would need risk-ratio associations of ≈2.5 with both early volume and retention, stronger than any measured covariate, to fully explain the association.


---

## 4. Discussion


## 4.1 Summary of findings

Four findings emerge from this 14-year follow-up of 2,123 young athletes. First, competition volume at ages 13–14 was strongly and prospectively associated with retaining senior competition. Second, the association replicated across both birth cohorts and withstood structural controls, club random effects, and multiple imputation. Third, the dropout signal decomposed into two independent components: early behavioral heterogeneity visible at 13–14, and a genuine within-athlete pull-back. Exit-aligned trajectories showed most dropouts tapering (median 12 → 10 → 9 → 4 meets across their last four seasons), and decline predicted exit even among athletes all still active at 16. Fourth, higher event-category concentration within track and field was associated with higher retention, robust to count-dependence checks; this is a different construct from, not a contradiction of, multisport diversification (§4.6).

## 4.2 Behavior explains more variance in retention than performance

Behavior (competitions entered) explained more variance in senior retention than performance (Tyrving score) even when both were measured in the same window (Section 3.6): sex + Tyrving gave AUC = 0.607, sex + volume 0.740, both combined 0.737, and a baseline performance *trajectory* closed the gap only slightly (0.640). Performance reflects capability; volume reflects the athlete's own choices about taking part (licensed by the open-entry structure of Section 2.2), and those choices matter more for disengagement than capability does. Two caveats: volume is a near-noiseless count while Tyrving is a scored maximum with ~20% missingness, so part of the gap could be measurement precision (the within-stratum effects argue not all of it); and predictor and outcome both index registered activity, so "behavior outperforms performance" describes when disengagement becomes observable, not a causal mechanism.

Low or declining volume can also have causes unrelated to waning engagement. *Cost:* sport expenses are cited as a dropout reason more often by Norwegian minority youth from less-resourced families (Espedalen & Seippel, 2024); the channel is attenuated here (clubs pay entry fees, travel is short) but not eliminated, and the register holds no socioeconomic data. *Injury:* injuries were the most frequently mentioned dropout reason in the 25-year Norwegian track-and-field follow-up (24.3%; Enoksen, 2011), and an injured 14-year-old produces the same register signature as a disengaging one, so part of the pull-back is plausibly enforced rather than chosen. *Periodization*, competing less in order to peak later, is unlikely: the decline spans successive calendar years and ends in exit, not a peak.

## 4.3 Pull-back is real at the individual level, and so is early heterogeneity

Is the divergence in Figure 2 genuine within-athlete pull-back, or early differentiation only, or an artifact of averaging abrupt exits at heterogeneous ages? The exit-aligned analyses answer at the individual level: 95% of dropouts were still competing in their penultimate season, 74% had a reduced-but-nonzero penultimate season, and only 19% exited directly from peak volume. The typical exit is a two-to-three-season taper, not a cliff. Both components are nonetheless real: level and change carried independent information (Table 4), the pattern held in the contamination-free window (level OR = 3.04; change OR = 1.88), and future dropouts already differed at 13–14, consistent with retrospective evidence that dropouts' developmental activities differ years before exit (Wall & Côté, 2007).

## 4.4 Consistent with process accounts of withdrawal

We assess behavior, not motivational processes, so no single framework is confirmed; but the footprint is consistent with the main process accounts. In the Sport Commitment Model (Scanlan et al., 1993, 2016), the resolve to continue is shaped by enjoyment, investments, involvement opportunities, alternatives, and social constraints, and *enthusiastic* commitment is distinguished from *constrained* commitment, the latter less sustainable and linked to burnout (Raedeke, 1997). Declining volume years before exit fits an eroding commitment balance, though the register cannot distinguish waning enthusiasm from accumulating constraint. Withdrawal-as-process accounts (Ebaugh, 1988; Eliasson & Johansson, 2021) describe leaving as a gradual deliberative passage (first doubts, weighing of alternatives, a turning point) among athletes who remain formally involved: precisely what the exit-aligned trajectories show, a typical future dropout still competing, at reduced volume, for two to three seasons before the final exit. The register cannot observe the deliberation, but it can now observe its behavioral shape, two to three thinning seasons, at the individual level.

Two readings of the same footprint deserve equal standing. Declining volume may mark *disengagement from sport*, the commitment-erosion reading. It may also mark *engagement reallocation*: ages 14–16 are precisely when Norwegian multi-sport youth consolidate into one sport, so for some athletes declining track-and-field volume signals rising commitment to handball or football rather than to nothing: the developmentally appropriate transitions that Battaglia et al. (2024) argue the dropout-as-crisis framing wrongly pathologizes. The register cannot separate the two, and the reallocation share is unbounded in our data. Norwegian participation research is compatible with both: involvement is strongly stratified, from heavy to light (Bakken, 2019; Espedalen, 2025), and exit from organized sport can itself reclaim time and autonomy rather than mark a loss (Espedalen, 2025). What the register demonstrates is that *some* mechanism (erosion, reallocation, or constraint) leaves a footprint readable in registered activity years before exit.

## 4.5 Sex effect

The sex pattern differs by specification, informatively. Unadjusted, Kaplan–Meier curves showed no clear sex difference (log-rank *p* = .33); adjusted, females retained at significantly lower odds in every layer of the primary model (OR = 0.72 sex-only, 0.60 full model; Table 3): *conditional on the same early volume, concentration, and performance*, girls were less likely to remain, their higher early volumes partially masking the gap in unadjusted comparisons. The behavioral mechanism itself was similar across sexes (Supplementary Table S7): milestone-window volume reduced cessation hazard similarly for males (HR = 0.43) and females (HR = 0.45), C-index 0.843 for each, so the residual sex effect operates *above*, not *through*, the behavioral pathway. This complements survey reports of higher female dropout (Bakken, 2019) and the clearly higher female attrition in Enoksen's (2011) historical cohort.

## 4.6 Within-sport event concentration is a different construct from multisport diversification

Event-category concentration at ages 13–14 predicted *greater* senior retention (OR = 1.36 per SD), consistently across cohorts, in the Cox model (HR = 0.80), and across all count-dependence stress tests (Section 3.9). That finding should not be read against the diversification literature, which concerns diversification *across sports*: sampling versus single-sport specialization and its consequences for elite performance and health (Côté & Hancock, 2016; Güllich et al., 2022). Our HHI measures concentration *within* one sport, conditional on already participating in it, and the register says nothing about other sports: an athlete concentrated within track and field may simultaneously be a multisport sampler. The constructs are related but not interchangeable, and the across-sport evidence is itself less settled than often assumed: in youth swimming, early-specialization markers were, contrary to expectation, *not* positively related to burnout and dropout (Larson et al., 2019), and blanket condemnation of early specialization has been argued to outrun the evidence (Baker et al., 2021). Both findings are consistent with our within-sport result. The outcome also differs (retention at 20, not elite performance), and HHI is not a proxy for main-event performance (r = −0.05; coefficient unchanged when primary-category Tyrving is added; Supplementary Table S18). Governing bodies should read this neither as a license to push early specialization nor as grounds for forced diversification among motivated adolescents.

## 4.7 What registers bring

Registers address two structural problems in dropout research: withdrawn athletes are hard to recruit, and retrospective accounts compress a continuous process into a remembered decision. Registration records provide a complete population and continuous rather than reconstructed behavioral sequences. Registers bring no new theory; they bring a longitudinal behavioral test of theories built largely on cross-sectional or short-prospective evidence: here a well-calibrated baseline-only signal (AUC = 0.751), internal replication, robustness across structural, club-level, and missing-data checks, and an E-value of ≈2.5.

## 4.8 Implications for practitioners

The practical deliverable is a *testable targeting rule*, not a finished intervention: the register can say precisely *whom* retention support would reach and how early; whether such support works is the pilot question in §4.10. Four implications follow.

**(1) Register-based flagging at the end of the age-14 season.** Flag athletes whose ages-13–14 competition count falls below a threshold. At < 10 meets, the flag captures 26% of the cohort whose senior retention is 5.7%, versus 20.2% among the unflagged, a 3.5-fold difference computed automatically from data the federation already holds (Table 6). Every flagged athlete is low-but-active (cohort entry guarantees a baseline meet), so the flag list is an outreach list, and the same threshold behaves similarly against an activity-at-17 outcome (14% vs 51% still active), so it serves the adolescent-exit target as well as the senior one. Two numbers discipline its use: sensitivity is 0.30, so most future dropouts are *not* flagged, and unflagged athletes' own retention is only ~20%. A flag concentrates risk; its absence reassures no one. Flagging should therefore *prioritize* outreach where risk is densest, not substitute for population-wide provision.

**(2) Flag again after age 15 using within-athlete change.** Level and change carry independent information (Section 3.5): screen on level at end of age 14 and on change at end of age 15, the latter just after the first selective gate and ahead of the steepest attrition at 17.

**(3) Lower the cost side of the next competition cycle, as an offer and never as pressure.** With entry fees club-paid and travel short (Section 2.2), the remaining levers are residual and psychological costs: membership and equipment support, coach-accompanied transport, low-stakes practice meets, and an explicit signal that participation is welcome regardless of performance, each acting on the cost side of the engagement balance (Scanlan et al., 1993, 2016). The register cannot distinguish athletes who are blocked from athletes choosing other priorities, and for the latter, a large group by design in a low-threshold system, retention pressure would be misplaced. Flags identify *whom* to reach; understanding *why* still requires conversation, for which commitment instruments such as the SCQ-2 complement the register.

**(4) Be cautious about prescribing event diversification for retention.** Within-sport concentration predicted *higher* retention, robustly (§4.6); federations should not assume diversification pressure aids retention in this age group.

**Governance preconditions.** Operational flagging means algorithmic risk-profiling of minors, and the research-ethics exemption this study relies on (Section 2.7) licenses none of it. Deployment would require a federation's own legal basis and a data-protection impact assessment; flags visible to a designated officer rather than routinely to coaches (avoiding expectancy and labeling effects); informed families with an opt-out; a retention limit for flag data; and attention to equity, which the register cannot audit for lack of socioeconomic data. That the screen runs without athlete contact is a transparency problem to solve, not a feature. And the flag must be support-only: the same list that identifies whom to help could identify whom a stretched club quietly deprioritizes, and deployment must rule that use out. These preconditions, and the untested intervention effect, are why the next step is the pilot of §4.10 rather than adoption.

## 4.9 Limitations

First, the outcome indexes *attrition from track-and-field competition*, not from sport: a sport-switcher counts as a dropout, and the reallocation share is unbounded (§4.4). Second, the register records official results, not subjective experience, nor injury, a leading cause of attrition in this sport (Enoksen, 2011); part of the pull-back is therefore plausibly non-volitional, and the qualitative literature remains essential for *why* volume declines. Third, the population is soft-selected through club membership and district entry, and the three venues cover eastern, western, and mid Norway, with northern districts served by the mid-Norway venue. Fourth, predictor and outcome share a measurement scale; despite the baseline-only model, the contamination-free change model, exit-aligned trajectories, and landmark and zero-volume sensitivities, structural overlap remains a conceptual limitation of register-only designs. Fifth, the post-baseline Cox specification violated proportional hazards (Schoenfeld χ² = 220.77); its estimates are descriptive only. Sixth, the HHI treats event categories symmetrically although they co-occur unevenly (98% of hurdlers also sprinted), so identical values can represent different combination patterns; the direction of the association was nonetheless robust. Seventh, the youngest cohort has at most four post-senior years of observation, though the fixed-window outcome gives near-identical results. Eighth, on the applied side: the thresholds are calibrated to a complete-register, open-entry, club-pays system and do not transfer to coach-gated or pay-to-play systems without re-derivation, and no intervention effect has been demonstrated: §4.8 is targeting logic, not evaluated policy.

## 4.10 Future directions

The central next step is a quasi-experimental pilot: federation outreach to athletes with low but non-zero pre-milestone volume (1 ≤ vol < 10), a designated flag recipient per club, pre-registered outcomes, and stakeholder consultation (athletes' councils, parents, club volunteers). Further extensions: linking the behavioral signal to commitment instruments in active athletes, and cross-sport generalization where registers are less complete.

## 4.11 Conclusion

Senior retention in Norwegian youth track and field is prospectively associated with baseline-window competition behavior: athletes who already compete more at ages 13–14 retain at substantially higher rates, and those who decline retain at substantially lower rates. The decline is visible within athletes, years before exit, and is no averaging artifact. The effect withstands structural, club-level, missing-data, and outcome-definition checks and replicates across cohorts; early heterogeneity and pull-back contribute independently. The findings are consistent with, though do not by themselves confirm, accounts of withdrawal as a gradual deliberative process, and they yield a register-implementable targeting rule whose intervention value, under the governance preconditions above, is now a testable question.


---

## Acknowledgements

During the preparation of this work the author used Claude Code (Anthropic), an AI-assisted writing and analysis tool, to assist with implementing statistical analyses in Python, generating figures using matplotlib, and editing the manuscript text for clarity and consistency. After using this tool, the author reviewed and edited the content as needed and takes full responsibility for the content of the published article. All scientific decisions, interpretations, and conclusions are the author's own. This use is also declared in the cover letter, per journal policy.

## Statements and Declarations

### Ethical considerations

Ethics committee approval was not required for this study. The competition records analyzed are publicly accessible via the Norwegian Athletics Federation's online register, and Norway's Health Research Act (Helseforskningsloven §4) exempts secondary use of register-based data of this kind from formal approval by a Regional Committee for Medical and Health Research Ethics (see Methods, Section 2.7). The derived analysis dataset links the public records to athlete dates of birth and is therefore handled as personal data under the EU General Data Protection Regulation (GDPR); it is not redistributed, and no personally identifying information about individual athletes is reported in this manuscript.

### Consent to participate

Not applicable. The study is a secondary analysis of publicly accessible competition records; no participants were contacted or recruited.

### Consent for publication

Not applicable. The manuscript contains no identifiable data relating to any individual person.

### Declaration of conflicting interest

The author(s) declared no potential conflicts of interest with respect to the research, authorship, and/or publication of this article.

### Funding statement

The author(s) received no financial support for the research, authorship, and/or publication of this article.

### Data availability

The competition records used in this study are publicly accessible via the Norwegian Athletics Federation's online register. The derived analysis dataset cannot be publicly shared because it contains personal data (athlete dates of birth) under the EU GDPR. The full analysis code will be deposited in a public repository upon acceptance.

---

## References


(APA 7th edition format)

Baker, J., Mosher, A., & Fraser-Thomas, J. (2021). Is it too early to condemn early sport specialisation? *British Journal of Sports Medicine, 55*(3), 179–180. https://doi.org/10.1136/bjsports-2020-102053

Back, J., Johnson, U., Svedberg, P., McCall, A., & Ivarsson, A. (2022). Drop-out from team sport among adolescents: A systematic review and meta-analysis of prospective studies. *Psychology of Sport and Exercise, 61*, Article 102205. https://doi.org/10.1016/j.psychsport.2022.102205

Bakken, A. (2019). *Idrettens posisjon i ungdomstida: Hvem deltar og hvem slutter i ungdomsidretten?* [The position of sport in adolescence: Who participates and who drops out of youth sport?] (NOVA Rapport 2/2019). Oslo Metropolitan University.

Battaglia, A., Kerr, G., & Tamminen, K. (2024). The dropout from youth sport crisis: Not as simple as it appears. *Kinesiology Review, 13*(3), 345–356. https://doi.org/10.1123/kr.2023-0024

Cobley, S., Baker, J., Wattie, N., & McKenna, J. (2009). Annual age-grouping and athlete development: A meta-analytical review of relative age effects in sport. *Sports Medicine, 39*(3), 235–256. https://doi.org/10.2165/00007256-200939030-00005

Côté, J., & Hancock, D. J. (2016). Evidence-based policies for youth sport programmes. *International Journal of Sport Policy and Politics, 8*(1), 51–65. https://doi.org/10.1080/19406940.2014.919338

Cox, D. R. (1972). Regression models and life-tables. *Journal of the Royal Statistical Society: Series B (Methodological), 34*(2), 187–202. https://doi.org/10.1111/j.2517-6161.1972.tb00899.x

Crane, J., & Temple, V. (2015). A systematic review of dropout from organized sport among children and youth. *European Physical Education Review, 21*(1), 114–131. https://doi.org/10.1177/1356336X14555294

Davidson-Pilon, C. (2019). lifelines: Survival analysis in Python. *Journal of Open Source Software, 4*(40), Article 1317. https://doi.org/10.21105/joss.01317

DiFiori, J. P., Benjamin, H. J., Brenner, J. S., Gregory, A., Jayanthi, N., Landry, G. L., & Luke, A. (2014). Overuse injuries and burnout in youth sports: A position statement from the American Medical Society for Sports Medicine. *Clinical Journal of Sport Medicine, 24*(1), 3–20. https://doi.org/10.1097/JSM.0000000000000060

Ebaugh, H. R. F. (1988). *Becoming an ex: The process of role exit*. University of Chicago Press.

Eime, R. M., Young, J. A., Harvey, J. T., Charity, M. J., & Payne, W. R. (2013). A systematic review of the psychological and social benefits of participation in sport for children and adolescents: Informing development of a conceptual model of health through sport. *International Journal of Behavioral Nutrition and Physical Activity, 10*, Article 98. https://doi.org/10.1186/1479-5868-10-98

Eliasson, I., & Johansson, A. (2021). The disengagement process among young athletes when withdrawing from sport: A new research approach. *International Review for the Sociology of Sport, 56*(4), 537–557. https://doi.org/10.1177/1012690219899614

Enoksen, E. (2011). Drop-out rate and drop-out reasons among promising Norwegian track and field athletes: A 25 year study. *Scandinavian Sport Studies Forum, 2*, 19–43.

Espedalen, L. E. (2025). *Organized sport in the lives of young Norwegians: Participation, exit, and social inequality* [Doctoral dissertation, Norwegian School of Sport Sciences].

Espedalen, L. E., & Seippel, Ø. (2024). Dropout and social inequality: Young people's reasons for leaving organized sports. *Annals of Leisure Research, 27*(2), 197–214. https://doi.org/10.1080/11745398.2022.2070512

Güllich, A., Macnamara, B. N., & Hambrick, D. Z. (2022). What makes a champion? Early multidisciplinary practice, not early specialization, predicts world-class performance. *Perspectives on Psychological Science, 17*(1), 6–29. https://doi.org/10.1177/1745691620974772

Heidari, S., Babor, T. F., De Castro, P., Tort, S., & Curno, M. (2016). Sex and Gender Equity in Research: Rationale for the SAGER guidelines and recommended use. *Research Integrity and Peer Review, 1*, Article 2. https://doi.org/10.1186/s41073-016-0007-6

Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science & Engineering, 9*(3), 90–95. https://doi.org/10.1109/MCSE.2007.55

Jayanthi, N. A., LaBella, C. R., Fischer, D., Pasulka, J., & Dugas, L. R. (2015). Sports-specialized intensive training and the risk of injury in young athletes: A clinical case-control study. *American Journal of Sports Medicine, 43*(4), 794–801. https://doi.org/10.1177/0363546514567298

Kearney, P. E., & Hayes, P. R. (2018). Excelling at youth level in competitive track and field athletics is not a prerequisite for later success. *Journal of Sports Sciences, 36*(21), 2502–2509. https://doi.org/10.1080/02640414.2018.1465724

Kretchmar, R. S. (2000). Movement subcultures: Sites for meaning. *Journal of Physical Education, Recreation & Dance, 71*(5), 19–25. https://doi.org/10.1080/07303084.2000.10605140

Kuokkanen, J., Phipps, D. J., Saarinen, M., Korhonen, J., Romar, J.-E., & Gustafsson, H. (2026). Trajectories of sport exhaustion, cynicism and inadequacy among adolescent student-athletes: A three-year longitudinal study of social influences in the Finnish dual career context. *Psychology of Sport and Exercise, 82*, Article 103015. https://doi.org/10.1016/j.psychsport.2025.103015

Larson, H. K., Young, B. W., McHugh, T.-L. F., & Rodgers, W. M. (2019). Markers of early specialization and their relationships with burnout and dropout in swimming. *Journal of Sport and Exercise Psychology, 41*(1), 46–54. https://doi.org/10.1123/jsep.2018-0305

Norges Friidrettsforbund. (2024). *Tyrvingtabellen: Poengtabell for ungdomsfriidrett* [Tyrving table: Scoring table for youth athletics]. https://www.friidrett.no/arrangement/arrangementshjelp/poengtabeller/tyrvingtabellen/

Norges Friidrettsforbund. (2026). *Lover og regler* [Laws and regulations]. https://www.friidrett.no/om-nfif/lover/

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, E. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830.

Raedeke, T. D. (1997). Is athlete burnout more than just stress? A sport commitment perspective. *Journal of Sport & Exercise Psychology, 19*(4), 396–417. https://doi.org/10.1123/jsep.19.4.396

Sarrazin, P., Vallerand, R. J., Guillet, E., Pelletier, L. G., & Cury, F. (2002). Motivation and dropout in female handballers: A 21-month prospective study. *European Journal of Social Psychology, 32*(3), 395–418. https://doi.org/10.1002/ejsp.98

Scanlan, T. K., Carpenter, P. J., Simons, J. P., Schmidt, G. W., & Keeler, B. (1993). An introduction to the sport commitment model. *Journal of Sport & Exercise Psychology, 15*(1), 1–15. https://doi.org/10.1123/jsep.15.1.1

Scanlan, T. K., Chow, G. M., Sousa, C., Scanlan, L. A., & Knifsend, C. A. (2016). The development of the Sport Commitment Questionnaire-2 (English version). *Psychology of Sport and Exercise, 22*, 233–246. https://doi.org/10.1016/j.psychsport.2015.08.002

van Houwelingen, H. C. (2007). Dynamic prediction by landmarking in event history analysis. *Scandinavian Journal of Statistics, 34*(1), 70–85. https://doi.org/10.1111/j.1467-9469.2006.00529.x

VanderWeele, T. J., & Ding, P. (2017). Sensitivity analysis in observational research: Introducing the E-value. *Annals of Internal Medicine, 167*(4), 268–274. https://doi.org/10.7326/M16-2607

von Elm, E., Altman, D. G., Egger, M., Pocock, S. J., Gøtzsche, P. C., & Vandenbroucke, J. P. (2007). The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: Guidelines for reporting observational studies. *Annals of Internal Medicine, 147*(8), 573–577. https://doi.org/10.7326/0003-4819-147-8-200710160-00010

Wall, M., & Côté, J. (2007). Developmental activities that lead to dropout and investment in sport. *Physical Education and Sport Pedagogy, 12*(1), 77–87. https://doi.org/10.1080/17408980601060358

Worley, J. T., & Smith, A. L. (2026). Positive peer relationships, social identity, and adaptive sport motivation in youth athletes. *Psychology of Sport and Exercise, 82*, Article 102996. https://doi.org/10.1016/j.psychsport.2025.102996

Zhong, J., Wang, Q., Bao, H., Wang, Y., & Guo, S. (2026). Effects of basic psychological needs on Chinese youth athlete burnout under coach burnout: Using hierarchical linear modeling. *Psychology of Sport and Exercise, 85*, Article 103099. https://doi.org/10.1016/j.psychsport.2026.103099

