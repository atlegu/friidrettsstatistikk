# Methods

## 2.1 Design

This retrospective longitudinal cohort study uses the national competition register as its only data source; the cohort is the entire population satisfying the inclusion criterion, so estimates describe that population. We follow the Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) guideline where relevant (von Elm et al., 2007).

## 2.2 Setting and inclusion

Norwegian youth track and field is organized as a low-threshold, open-entry system. Up to age 15, essentially all meets are open to all club-registered athletes: there are no qualifying standards, no roster selection, and no coach-controlled gatekeeping (Norges Friidrettsforbund, 2026). (The exception, occasional invitational regional-team matches for 14–15-year-olds, does not gate ordinary competition.) Athletes and their families decide which meets and events to enter; entry fees are ordinarily paid by the club, participation is actively encouraged, and travel distances are typically short. The first genuinely selective competition is the national youth championship (Ungdomsmesterskapet, UM), open from the calendar year athletes turn 15, with event-specific qualifying standards. Two design consequences follow: before age 15, meet counts primarily express the athlete's own choice rather than selection or entry costs, which licenses interpreting ages-13–14 volume as a behavioral indicator of engagement; and the ages-15–16 window coincides with the first selective gate (UM), which is why the pre-milestone (13–14) and milestone (15–16) windows are analyzed separately.

The cohort comprises all athletes who competed in any of six consecutive autumn editions (2011–2016) of a regional grassroots youth meet held simultaneously at three venues in eastern, western, and mid Norway (the last also serving the northern districts). Athletes were 13–14 and were entered by their district federations under district quotas, with no qualifying performance standard and no entry fee; this soft selection into the baseline meet is a design feature: disengagement trajectories arise from a baseline of demonstrable engagement. {+The target population is thus the engaged core of the age group, not every athlete with a registered result (Section 3.1).+} Birth years were restricted to 1998–2002 (boundary years 1997 and 2003 had only one eligible edition), and athletes appearing in both a 13- and a 14-year-old edition were de-duplicated to the earlier one (Supplementary Figure S0). {+Participation was identified by venue and date, because some venue-days are filed under other meet names (Supplementary Methods S-M12).+} For {+an internal cohort replication+}, participants were partitioned into Cohort A (births 1998–2000, baseline meets 2011–2014; n = {+1,309+}) and Cohort B (births 2001–2002, baseline meets 2014–2016; n = {+829+}). Athletes were retained regardless of club transfers ({+27.6%+} recorded results for two or more clubs), so changing club does not register as dropout. The total cohort comprised {+2,138+} athletes ({+1,006+} male, {+1,130+} female, {+2+} with {+no registered+} sex), generating {+231,144+} competition entries {+through 2025 (register extract of May 2026; corrections made after a data audit during revision are listed in Supplementary Methods S-M12).+}

## 2.3 Follow-up window

Each athlete was followed from baseline through the most recent complete competition season (2025): maximum 14 years (births 1998), minimum 9 years (births 2002). All athletes had follow-up past the senior age threshold (age 20).

## 2.4 Variables

### 2.4.1 Outcome

Active senior status was coded 1 if the athlete had ≥2 registered results in any calendar year at age 20+ (the senior age), and 0 otherwise; two results exclude sporadic returners while capturing athletes entering separate events at one meet. Sensitivity to this definition was tested with two alternatives (≥1 senior-age result; ≥2 results in each of two distinct senior-age years; Supplementary Table S9). A secondary time-to-event outcome (time to last active season, right-censoring athletes active in 2024+) supports Kaplan–Meier and Cox analyses (Section 2.5.4). {+Both outcomes refer to the final active season observed through 2025, so a temporary break followed by a return is not an exit.+}

### 2.4.2 Performance

Each result was scored in Tyrving points, the Norwegian federation's age-norm system (Norges Friidrettsforbund, 2024): a published table gives, per event × sex × age, a reference performance worth 1,000 points and a per-unit quotient (values capped at 1,500 to suppress data-entry errors). {+All events at the baseline meet were scored with the implement- and hurdle-specific norms for the athlete's sex and age and the table's own formulas (Supplementary Methods S-M3).+} We computed tyrving_best (baseline maximum), tyrving_peak_pre15, and per-age scores (yielding a baseline performance trajectory, age-14 minus age-13).

### 2.4.3 Specialization

For every athlete-year we counted the event categories entered (sprint, middle-distance, long-distance, hurdles, jumps, throws, combined events, race walking, relay) and computed a Herfindahl-Hirschman concentration index, $HHI = \sum_{i=1}^{k} s_i^2$, where $s_i$ is the share of the athlete's results in category $i$. HHI ranges from 1/k (fully diversified) to 1 (single category). {+The baseline index is computed from results at ages 13–14 only, the window of the volume predictor (combined-event handling: Supplementary Methods S-M8).+} Categories co-occur unevenly (sprints and hurdles share training demands; throws transfer little); the HHI treats them symmetrically (see the limitations).

### 2.4.4 {+Competition participation (behavioral markers)+}

For each athlete and age-year from 13 to 18 we counted {+competition days (vol_age_X: distinct dates with a registered result; the register stores each day of a multi-day meet as a separate meet), called meets for brevity,+} and total results (res_age_X, which also define active seasons: ≥2 results in a calendar year). Composites: vol_pre_milestone (meets at 13–14), vol_milestone (15–16), their difference, and n_champ_types (championship types before 17). These are observable behavioral markers, not direct measures of motivation or commitment{+; because participation can also decline through injury, another sport, or school constraints, we treat declining participation as a marker of disengagement, not disengagement itself+}.

### 2.4.5 Controls

Sex (M/F as registered), birth quarter (Q1–Q4{+; Q1 = January–March, the relatively oldest in the calendar-year age group; unknown for 90 athletes registered without birth date+}), baseline region (eastern, mid, or western Norway, by venue{+; Supplementary Methods S-M12+}), and club size in the baseline year ({+the number of cohort athletes registered for the athlete's baseline club that year+}). {+The 2 athletes without registered sex are excluded from all regression models, which condition on sex (Supplementary Methods S-M3).+}

## 2.5 Statistical analysis

### 2.5.1 Primary analysis: prospective logistic regression

The principal inferential model is a logistic regression for active senior status using only baseline-window predictors (ages 13–14): sex, baseline Tyrving, {+HHI+}, and pre-milestone volume, fitted in a nested sequence (L1: sex; L2: + Tyrving; L3: + HHI; L4: + volume) to characterize each variable class's unique contribution. Continuous covariates were z-standardized (per-SD effects{+; re-estimated within each training fold during cross-validation+}), and all nested models were fitted on the fixed L4 complete-case sample. {+Discrimination was assessed by stratified 5-fold cross-validation repeated 20 times (CV-AUC with 95% CI; model differences on identical folds), and again with folds grouped by baseline club; calibration slope, calibration-in-the-large, and Brier score used out-of-fold predictions (Supplementary Methods S-M4).+} Restricting predictors to ages 13–14 keeps the primary estimate unambiguously prospective, avoiding the mechanical zero-volume overlap that post-baseline predictors carry.

### 2.5.2 Structural controls

The full model was refit adding region, birth-quarter indicators (Q1, Q4{+, the relative-age extremes (Cobley et al., 2009); full coding as sensitivity+}), and standardized club size, comparing the stability of the volume coefficient with and without controls (Supplementary Table S13).

### 2.5.3 {+Level, change, and within-athlete decline before exit+}

To disentangle early behavioral heterogeneity from {+within-athlete decline+}, we fit a logistic regression on athletes still active at age 14 ({+1,926+}; complete-case model n = {+1,925+}) including both the volume level at age 14 and the change from 14 to 15 (Table 4{+; change = later minus earlier volume, so OR > 1 per SD means that decline predicts lower retention+}). Because a change score can span the exit itself, {+three+} analyses probe the within-athlete claim directly: exit-aligned trajectories (volume one to three seasons before each dropout's own final active season), a contamination-free change model among athletes still active at 16 (level at 15 plus change 15→16 predicting senior status; Supplementary Table S19){+, and an athlete fixed-effects model of log(1 + meets) at ages 13–19, with age fixed effects and indicators for the final active season and the three preceding seasons, which estimates each athlete's decline relative to their own earlier volume (Supplementary Methods S-M6)+}. Prospective early-warning thresholds on pre-milestone volume (classification performance at candidate cut-offs at the end of the age-14 season, with bootstrap CIs) are reported in Table 6{+, with cut-offs also derived in one birth cohort and tested in the other (Supplementary Table S29)+}.

### 2.5.4 Time-to-cessation survival analysis (secondary)

Time to the last active season was modeled with Cox proportional hazards regression (Cox, 1972), with a baseline-only primary specification {+whose clock starts at the end of the age-14 season, when the predictor window closes+} (Supplementary {+Tables S10 and+} S16), {+a landmark analysis (van Houwelingen, 2007) among athletes still in their career at age 16 (final active season at 16 or later; Supplementary Table S8)+}, and a post-baseline specification interpreted with overlap caveats (Table 5). {+Temporary gaps followed by a return are not events; definitions ending the spell at the first two-season gap or the first inactive season are reported in Supplementary Table S30.+} Proportional-hazards checks, E-values (VanderWeele & Ding, 2017), cluster-robust errors, and period- and sex-specific estimates are in the Supplementary Methods; hazard ratios are descriptive, not causal.

### 2.5.5 Sample size, missing data, and {+internal cohort replication+}

{+Because the full eligible population is observed, a detection-capacity analysis replaces a-priori power: the design could detect hazard ratios ≥1.07 and odds ratios ≥1.20 per SD (Supplementary Table S4), below typical effects in prior dropout research (Back et al., 2022).+} {+Baseline Tyrving was missing for 2 athletes (0.1%), both without registered sex; other variables were complete. The primary analysis is complete-case (n = 2,136), with multiple imputation (m = 20; Supplementary Methods S-M3) as sensitivity analysis (Supplementary Table S21; sample flow: Supplementary Table S12).+} Club-level confounding was probed via the intraclass correlation of volume across baseline clubs{+, club-clustered standard errors, a population-averaged model,+} and a refit with club random intercepts (Supplementary Table S22). The primary and secondary models were re-estimated separately by birth cohort{+, an internal replication within one register and national system+}.

### 2.5.6 Software

Analyses used Python 3.13 with lifelines (Davidson-Pilon, 2019) and scikit-learn (Pedregosa et al., 2011); figures used matplotlib (Hunter, 2007). All stochastic steps used fixed random seeds; exact package versions accompany the code, to be deposited in a public repository upon acceptance. Data availability is described in Section 2.7.

## 2.6 Sex and gender

Following SAGER guidance (Heidari et al., 2016), all primary analyses include sex as a covariate, with sex-stratified analyses in Supplementary Table S7; "sex" reflects the federation's binary registration variable; the register holds no gender-identity information.

## 2.7 Ethics

The competition records analyzed are publicly accessible via the Norwegian Athletics Federation's online register; the derived dataset links them to dates of birth and is therefore not redistributed (GDPR). No personally identifying information appears in this manuscript. Norway's Health Research Act (Helseforskningsloven §4) exempts secondary use of register data of this kind from formal approval by a Regional Committee for Medical and Health Research Ethics. This exemption concerns the research use of the register; it does not extend to operational uses of similar data by sport organizations, which would require their own legal basis (see Section 4.8).
