# Methods

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
