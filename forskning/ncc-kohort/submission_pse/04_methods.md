# Methods

## 2.1 Design

This was a retrospective longitudinal cohort study of Norwegian youth track-and-field athletes, using the national competition register as the sole data source. The design reports the complete population of athletes meeting the inclusion criterion rather than a sample; consequently we frame statistical estimates as describing that population rather than as inference to a hypothetical super-population (Berk & Freedman, 2003). Reporting follows STROBE guidance for observational studies (von Elm et al., 2007).

## 2.2 Setting and inclusion

The cohort comprises every athlete who participated in any of six consecutive autumn editions of a regional grassroots youth meet held simultaneously at three venues in eastern, mid, and western Norway between 2011 and 2016: NCC-lekene 2011, NCC-lekene 2012, PEAB-lekene 2013, PEAB-lekene 2014, Bendit-lekene 2015, and Ungdomslekene 2016 (the meet retained an identical format, venue rotation, age-group structure, and event program while changing sponsor name). Each edition admitted athletes aged 13–14 in the year of the meet, who entered by registering interest through their regional club federation; in practice nearly all active club athletes who applied were included (in some districts all of them), with no qualifying performance threshold. This soft self-selection is a design feature: the baseline cohort consists of adolescents already engaged with organized track and field through a registered club, not children who happened to attend a school race or accompanied a friend to a single local meet. Disengagement trajectories therefore unfold from a baseline of demonstrable engagement.

We restricted the eligible-birth-year window to athletes who were 13 or 14 *in the year of their first eligible edition* and who had a recorded date of birth in 1998–2002. Athletes born in 1997 would have been 14 in the 2011 edition only (with no 13-year-old participation in the cohort window) and similarly athletes born in 2003 would have been 13 in the 2016 edition only; we excluded these boundary birth cohorts to ensure that all retained athletes had at least one full possible two-edition exposure window. Athletes who participated in both a 13-year-old and a 14-year-old edition were deduplicated to a single record, with the *earlier* edition used as the baseline meet. A flow diagram of cohort construction is provided in Supplementary Figure S0.

To enable cross-cohort replication, we partitioned participants into two birth-year cohorts: **Cohort A** (birth years 1998–2000, baseline meets 2011–2014; n = 1,301) and **Cohort B** (birth years 2001–2002, baseline meets 2014–2016; n = 822). Cohort B's earliest participants thus had baseline three years after Cohort A's, with no design changes between the two cohorts other than sponsor name.

Athletes were retained in the analysis regardless of subsequent transfers between clubs or events. The total analytical cohort comprised 2,123 athletes (996 male, 1,103 female, 24 with unknown sex), generating 230,868 individual competition entries through the most recent register update (April 2026).

## 2.3 Follow-up window

Each athlete was followed from their baseline meet year through the most recent complete competition season at the time of analysis (2025), yielding a maximum of 14 years of post-baseline observation (for athletes born 1998 and competing as 13-year-olds at the 2011 meet) and a minimum of 9 years (for athletes born 2002 and competing as 14-year-olds at the 2016 meet). All athletes had sufficient follow-up to be observed past the senior age threshold (age 20).

## 2.4 Variables

### 2.4.1 Outcome variables

The primary outcome is **active senior status**, a *binary* indicator coded 1 if the athlete had at least two registered competition results in any single calendar year at age 20 or later, and 0 otherwise. The two-results threshold was chosen to exclude athletes who returned to the register only sporadically (e.g., for a single charity race) while remaining inclusive of those competing in distinct events within a single meet. Age 20 marks the formal transition to senior competition in Norwegian track and field. To assess sensitivity to operational choices, we re-estimated the central effect using two alternative outcome definitions: (A) ≥1 senior-age result and (C) ≥2 results in each of two distinct senior-age calendar years (Supplementary Table S9).

A *secondary* time-to-event outcome was used for survival visualization and supplementary Cox modelling: **time to last active season**, where an active season is a calendar year with ≥2 registered results, with athletes still active in 2024 or later treated as right-censored. We distinguish these two outcomes throughout: the binary senior-status outcome is estimated with logistic regression as the primary inferential model (Section 2.5.1); the time-to-cessation outcome supports Kaplan–Meier visualization and Cox-based sensitivity analyses (Section 2.5.4).

### 2.4.2 Performance variables

Each result was converted to a Tyrving age-norm score, the Norwegian Athletics Federation's official scoring system for youth track and field. Tyrving points are computed from a published table that gives, for each event × sex × age combination, a reference performance equivalent to 1,000 points and a per-unit-change quotient (Norges Friidrettsforbund, 2024). A performance of exactly 1,000 points corresponds to the federation's published "excellent" benchmark for that combination. Points are linearly extrapolated above and below the reference, capped in our analyses at 1,500 to suppress occasional implausibly extreme values arising from data-entry errors in middle-distance times.

For each athlete we computed: **tyrving_best** (the maximum Tyrving score across all events at the baseline meet), **tyrving_mean** (the mean), **tyrving_peak_pre15** (the maximum across all results before age 15), and **tyrving_slope_13_16** (the OLS slope of age-specific maximum Tyrving regressed on age across ages 13–16, indexing performance trajectory).

### 2.4.3 Specialization variables

For each athlete and each calendar year we counted the distinct event categories (sprint, middle-distance, long-distance, hurdles, jumps, throws, combined events, race walking, relay) in which they recorded results, and computed a Herfindahl–Hirschman concentration index

$$HHI = \sum_{i=1}^{k} s_i^2$$

where $s_i$ is the share of that athlete's results falling in category $i$ and $k$ is the number of categories. HHI ranges from 1/k (perfectly diversified across k categories) to 1 (perfect specialization). Key variables were **hhi_early** (HHI computed over the first three active seasons), **hhi_age_15**, and **hhi_change** = hhi_age_15 − hhi_age_13.

### 2.4.4 Behavioral engagement variables

For each athlete and each integer age year from 13 to 18, we counted the number of distinct competition meets attended (**vol_age_X**), the total number of results (**res_age_X**), and a binary year-round indicator (**year_round_age_X** = 1 if the athlete competed in both an outdoor and an indoor meet in that age year, else 0). We derived composite indicators: **vol_pre_milestone** (sum of meets at ages 13–14, the pre-qualification window), **vol_milestone** (sum of meets at ages 15–16, the qualification-milestone window), and **vol_trend_milestone** (vol_milestone − vol_pre_milestone). We also computed **n_champ_types**, a count of championship *types* (Norwegian Youth Championships, Junior National Championships, National Championships, Regional Championships) in which the athlete competed before age 17.

We treat these variables as *observable behavioral markers* of engagement, not as direct measures of motivation or commitment. Their interpretation as evidence for an underlying engagement-balance mechanism depends on whether their temporal structure is consistent with the predictions of the theoretical accounts described in the Introduction.

### 2.4.5 Control variables

We recorded sex (M/F as registered in the federation's database), birth quarter (Q1–Q4) for relative-age-effect analyses, baseline region (eastern, mid, or western Norway, by venue), and club size in the baseline year (number of registered athletes in the same club).

## 2.5 Statistical analysis

### 2.5.1 Primary analysis: prospective logistic regression

The primary inferential model is a logistic regression for binary *active senior status*, using only **baseline-window predictors** measured during ages 13–14 (before the qualification-milestone window): sex, baseline Tyrving performance, Herfindahl–Hirschman event-category concentration (HHI early), and the count of distinct competition meets at ages 13 and 14 combined (*pre-milestone volume*). Models were fitted in a nested stepwise sequence (L1: sex only; L2: + Tyrving; L3: + HHI; L4: + pre-milestone volume) to characterize the unique discriminative contribution of each variable class. Continuous covariates were z-standardized so that odds ratios reflect per-SD effects. Discriminative accuracy was assessed by 5-fold stratified cross-validated AUC.

Restricting primary predictors to the baseline window avoids measurement overlap with the outcome process: an athlete who drops out before age 15 has milestone-window volume = 0 by construction *and* will not retain senior activity, which would inflate apparent discrimination through measurement overlap rather than prospective prediction. Using only ages-13–14 data, the primary estimate is unambiguously prospective.

### 2.5.2 Structural controls

We assessed sensitivity of the primary model to plausible structural confounders by re-fitting the full L4 model with three additional covariates: region (3-level: Vestlandet [reference], Østlandet, Midt-Norge); birth quarter (Q1- and Q4-indicator variables for relative-age effects); and standardized club size at baseline (number of athletes registered to the same club in the baseline year). Coefficient stability of the pre-milestone volume effect was compared with and without controls (Supplementary Table S13).

### 2.5.3 Within-athlete pull-back vs baseline heterogeneity

Future retainers and future dropouts already differ in competition volume at ages 13–14 (Figure 2, Table 2). To distinguish between (i) early behavioral heterogeneity and (ii) within-athlete pull-back across the age-14-to-15 transition, we fitted a logistic regression in athletes still active at age 14 (≥1 result at age 14, n = 1,914) including both the *level* of volume at age 14 and the *change* in volume from age 14 to age 15. If decline conditional on baseline level predicts retention, both coefficients should be significant; if separation is purely typological, only baseline level should matter (Supplementary Table S14).

### 2.5.4 Time-to-cessation survival analysis (secondary)

As a secondary effect-size representation we modeled *time from baseline to last active season* using Cox (1972) proportional hazards regression, with tied event times handled by Efron's (1977) method (Davidson-Pilon, 2024). The primary Cox specification (Supplementary Table S16) uses the same baseline-only predictor set as the primary logistic regression. A *landmark analysis* (van Houwelingen, 2007) restricted to athletes with ≥1 result at age 16 (n = 1,167) and a *post-baseline Cox specification* with ages-15–16 covariates are reported in Supplementary Tables S8 and as period-specific decomposition in Table 5; the latter is interpreted with explicit caveats given operational overlap with the at-risk window.

We assessed proportional hazards using Schoenfeld residuals (Grambsch & Therneau, 1994) and re-estimated the model stratified on violating variables (Therneau & Grambsch, 2000). For the dominant covariate we also computed the **E-value** (VanderWeele & Ding, 2017), period-specific estimates across three follow-up windows, cluster-robust standard errors clustered on club name (Lin & Wei, 1989), and sex-stratified subgroup Cox models. Hazard ratios are reported as descriptive associations within the observed register structure and should not be interpreted causally. Kaplan–Meier curves were stratified by sex, by competition volume at age 15–16, and by number of pre-17 championship types.

### 2.5.5 Sample size and detection capacity

Classical a-priori power calculations are less directly applicable to population-based register studies where the full cohort is observed and there is no sampling step at which the analyst chooses an *N*. We therefore replace power with a *detection-capacity* analysis: given the observed event count, what is the smallest effect size the design could reliably detect, and how does it compare to effect sizes in prior longitudinal dropout research?

Using Hsieh and Lavori's (2000) formula, $d = 1{,}570$ Cox events at $\alpha = .05$ and 80% power yields $HR_{\min} \approx 1.07$ per SD for a standardized covariate (for a balanced binary covariate, closer to 1.15). Prior prospective youth-sport dropout research reports small-to-moderate effects (Cohen's *d* ≈ 0.2–0.5; ORs ≈ 1.4–2.5; Sarrazin et al., 2002; Calvo et al., 2010; Espedalen & Seippel, 2022). Our detection capacity is therefore well below typical effect magnitudes; null findings for standardized covariates should be interpreted as substantively small rather than underpowered.

### 2.5.6 Missing data and clustering

Missing values arose primarily for the Tyrving score (~20% missing) and for HHI (~10% missing for athletes with fewer than 3 active seasons). Primary analyses used complete-case regression (n = 1,704). Mean-imputation produced near-identical estimates (Supplementary Table S5). Cluster-robust standard errors at the club level left coefficients unchanged with marginally wider CIs (Supplementary Table S2).

### 2.5.7 Calibration and prospective early-warning thresholds

We computed sensitivity, specificity, PPV, and NPV at five candidate thresholds for "flagging" an athlete on *pre-milestone* (ages 13–14) competition volume, applied at the end of an athlete's age-14 season — implementable before any age-15–16 outcome data exist (Table 6).

### 2.5.8 Cross-cohort replication and variable importance

The primary L4 logistic regression and the secondary Cox specifications were re-estimated separately within each birth cohort. As convergent evidence, we fit a random forest (Breiman, 2001) with 500 trees and maximum depth 8 to predict active senior status; variable importance is reported as the mean decrease in Gini impurity.

### 2.5.9 Software

All analyses used Python 3.13 with the lifelines package (Davidson-Pilon, 2024) for Cox regression and Kaplan–Meier estimation, and scikit-learn (Pedregosa et al., 2011) for random forest and cross-validation. Figures were produced with matplotlib (Hunter, 2007). Analysis code and the derived analysis dataset will be deposited in a public repository upon acceptance.

## 2.6 Sex and gender

Following SAGER guidance (Heidari et al., 2016), all primary analyses include sex as a covariate, and we additionally report sex-stratified subgroup analyses in supplementary material (Supplementary Table S7) so that potential sex-specific patterns are visible. We use "sex" throughout because the federation registers a binary sex variable assigned at registration; we have no information on gender identity. Where sex appears as a covariate (`female` = 1 for female, 0 for male, NA for unknown), it indexes biological sex as recorded.

## 2.7 Ethics

The study uses only data that is publicly accessible via the Norwegian Athletics Federation's competition register. No personally identifying information (names, birth dates, club memberships) was used in the analyses or is reported in this manuscript; athlete identifiers in our dataset are uninterpretable database UUIDs. Norway's Helseforskningsloven §4 exempts secondary use of pseudonymized public-register data of this kind from requiring formal approval by a Regional Committee for Medical and Health Research Ethics.
