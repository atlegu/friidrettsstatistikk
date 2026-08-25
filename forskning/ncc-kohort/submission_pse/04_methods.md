# Methods

## 2.1 Design

This was a retrospective longitudinal cohort study using the national competition register as the only data source. The cohort is the entire population satisfying the inclusion criterion rather than a sample, so estimates describe that population. We follow the Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) guideline where relevant (von Elm et al., 2007).

## 2.2 Setting and inclusion

Norwegian youth track and field is organized as a low-threshold, open-entry system. Up to age 15, essentially all meets are open to all club-registered athletes: there are no qualifying standards, no roster selection, and no coach-controlled gatekeeping. Athletes — together with their families — decide which meets and events to enter, entry fees are ordinarily paid by the athlete's club rather than by the family, participation is actively encouraged by clubs and the federation, and travel distances to ordinary meets are typically short. The first genuinely selective competition an athlete encounters is the national youth championship (Ungdomsmesterskapet, UM), which athletes may enter in the calendar year they turn 15 and which applies event-specific qualifying standards. Two design-relevant consequences follow. First, before age 15 the number of meets an athlete attends primarily expresses the athlete's own choice rather than selection, team-roster decisions, or entry costs — which is what licenses interpreting competition volume at ages 13–14 as a behavioral indicator of engagement. Second, the ages-15–16 window coincides with the first selective gate (UM), which is why the analyses treat the pre-milestone (13–14) and milestone (15–16) windows separately.

The cohort comprises all athletes who competed in any of six consecutive autumn editions (2011–2016) of a regional grassroots youth meet held simultaneously at three venues in eastern, mid, and western Norway. Athletes were aged 13–14 and entered through their club, with no qualifying threshold; the baseline cohort therefore consists of adolescents already engaged with organized track and field, so disengagement trajectories arise from a baseline of demonstrable engagement. We restricted the birth-year window to 1998–2002; boundary birth years (1997, 2003) were omitted because they had only a single eligible edition, and athletes appearing in both a 13- and a 14-year-old edition were de-duplicated to the earlier one (flow diagram: Supplementary Figure S0). For cross-cohort replication, participants were partitioned into Cohort A (births 1998–2000, baseline meets 2011–2014; n = 1,301) and Cohort B (births 2001–2002, baseline meets 2014–2016; n = 822). Athletes were retained in the cohort regardless of any subsequent transfer between clubs, so a change of club does not register as dropout; such transfers were common (27.8% of athletes recorded results for two or more clubs during follow-up). The total cohort comprised 2,123 athletes (996 male, 1,103 female, 24 with unknown sex), generating 230,868 competition entries through the most recent register update (April 2026).

## 2.3 Follow-up window

Each athlete was followed from baseline through the most recent complete competition season (2025): maximum 14 years (births 1998), minimum 9 years (births 2002). All athletes had follow-up past the senior age threshold (age 20).

## 2.4 Variables

### 2.4.1 Outcome

Active senior status was coded 1 if the athlete had ≥2 registered results in any calendar year at age 20+ (the age from which athletes compete as seniors), and 0 otherwise; requiring two results excludes sporadic returners while capturing athletes who compete in separate events within a single meet. Sensitivity to this definition was tested with two alternatives (≥1 senior-age result; ≥2 results in each of two distinct senior-age years; Supplementary Table S9). A secondary time-to-event outcome — time to last active season (calendar year with ≥2 results), right-censoring athletes active in 2024+ — supports Kaplan–Meier visualization and Cox sensitivity analyses (Section 2.5.4).

### 2.4.2 Performance

Each result was transformed into its age-norm score in Tyrving points, the Norwegian Athletics Federation's youth scoring system (Norges Friidrettsforbund, 2024), computed from a published table giving, for each event × sex × age combination, a reference performance equivalent to 1,000 points and a per-unit-change quotient. Points were capped at 1,500 to suppress data-entry errors. We computed tyrving_best (baseline maximum), tyrving_mean, tyrving_peak_pre15, and tyrving_slope_13_16 (OLS slope across ages 13–16).

### 2.4.3 Specialization

For every athlete-year we counted the event categories entered (sprint, middle-distance, long-distance, hurdles, jumps, throws, combined events, race walking, relay) and computed a Herfindahl-Hirschman concentration index, $HHI = \sum_{i=1}^{k} s_i^2$, where $s_i$ is the share of the athlete's results in category $i$. HHI ranges from 1/k (fully diversified across k categories) to 1 (single category). Key variables: hhi_early (first three active seasons), hhi_age_15, and hhi_change = hhi_age_15 − hhi_age_13. Combined events (e.g., pentathlon) appear in the register both as a combined-event total and as separate results for each constituent discipline; constituent results are counted in their natural categories, so multi-event athletes are represented as diversified, and stand-alone combined-event rows were rare (<0.1% of results). Some categories co-occur more naturally than others (e.g., sprints and hurdles share training demands, whereas throws transfer little to other categories); the HHI treats categories symmetrically, and we return to this in the limitations.

### 2.4.4 Behavioral engagement

For each athlete and age-year from 13 to 18 we counted distinct meets attended (vol_age_X; a multi-event competition counts as one meet), total results (res_age_X), and a year-round indicator (competing both outdoors and indoors; year_round_age_X). Composites: vol_pre_milestone (meets at ages 13–14), vol_milestone (ages 15–16), vol_trend_milestone (their difference), and n_champ_types (championship types entered before age 17). These are observable behavioral markers of engagement, not direct measures of motivation or commitment.

### 2.4.5 Controls

Sex (M/F as registered), birth quarter (Q1–Q4), baseline region (eastern, mid, or western Norway, by venue), and club size in the baseline year (registered athletes in the same club).

## 2.5 Statistical analysis

### 2.5.1 Primary analysis: prospective logistic regression

The principal inferential model is a logistic regression for active senior status using only baseline-window predictors (ages 13–14): sex, baseline Tyrving, early HHI, and pre-milestone volume, fitted in a nested sequence (L1: sex; L2: + Tyrving; L3: + HHI; L4: + volume) to characterize each variable class's unique contribution. Continuous covariates were z-standardized; discrimination was assessed by 5-fold stratified cross-validated AUC. Restricting predictors to ages 13–14 keeps the primary estimate unambiguously prospective: it avoids the measurement overlap that would arise because an athlete who drops out before age 15 has milestone-window volume of zero by construction.

### 2.5.2 Structural controls

The full model was refit adding region, birth-quarter indicators (Q1, Q4), and standardized club size, comparing the stability of the volume coefficient with and without controls (Supplementary Table S13).

### 2.5.3 Within-athlete pull-back vs. baseline heterogeneity

To disentangle early behavioral heterogeneity from within-athlete pull-back, we fit a logistic regression on athletes still active at age 14 (n = 1,914) including both the volume level at age 14 and the change from age 14 to 15: if pull-back conditional on level predicts retention, both coefficients should be significant (Supplementary Table S14). Prospective early-warning thresholds on pre-milestone volume (sensitivity, specificity, and predictive values at five candidate cut-offs, applied at the end of the age-14 season) are reported in Table 6.

### 2.5.4 Time-to-cessation survival analysis (secondary)

Time from baseline to last active season was modeled with Cox proportional hazards regression (Cox, 1972), with a baseline-only primary specification (Supplementary Table S16), a landmark analysis among athletes active at age 16 (van Houwelingen, 2007), and a post-baseline specification interpreted with caveats about operational overlap (Supplementary Table S8; Table 5). Proportional-hazards checks, E-values (VanderWeele & Ding, 2017), cluster-robust standard errors, and period- and sex-specific estimates are detailed in the Supplementary Methods. Hazard ratios are descriptive associations, not causal.

### 2.5.5 Sample size, missing data, and replication

Because the design observes the full eligible population, classical a-priori power analysis does not apply; a detection-capacity analysis (Supplementary Methods) shows the design could detect hazard ratios ≥1.07 per SD — well below effect sizes typical of prior dropout research. Missing values (Tyrving ~20%, HHI ~10%) were handled by complete-case analysis (n = 1,704), with mean-imputation and club-clustered standard errors as sensitivity checks (Supplementary Tables S5, S2). The primary and secondary models were re-estimated separately by birth cohort, and a random forest (Breiman, 2001; 500 trees, maximum depth 8) provided convergent variable-importance evidence.

### 2.5.6 Software

Analyses used Python 3.13 with lifelines (Davidson-Pilon, 2019) and scikit-learn (Pedregosa et al., 2011); figures used matplotlib (Hunter, 2007). Analysis code will be deposited in a public repository upon acceptance. The underlying competition records are publicly accessible via the federation's online register; the derived dataset contains personal data (dates of birth) and cannot be redistributed under the EU General Data Protection Regulation (GDPR).

## 2.6 Sex and gender

Following SAGER guidance (Heidari et al., 2016), all primary analyses include sex as a covariate, with sex-stratified analyses in supplementary material (Supplementary Table S7). We use "sex" because the federation registers a binary sex variable at registration; the register contains no gender-identity information.

## 2.7 Ethics

The competition records analyzed are publicly accessible via the Norwegian Athletics Federation's online register; the derived dataset links them to dates of birth and is therefore not redistributed (GDPR). No personally identifying information appears in this manuscript. Norway's Health Research Act (Helseforskningsloven §4) exempts secondary use of register data of this kind from formal approval by a Regional Committee for Medical and Health Research Ethics.
