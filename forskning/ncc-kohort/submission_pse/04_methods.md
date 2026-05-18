# Methods

## 2.1 Design

This was a retrospective longitudinal cohort study of Norwegian youth track-and-field athletes, using the national competition register as the sole data source. The design reports the complete population of athletes meeting the inclusion criterion rather than a sample; consequently we frame statistical estimates as describing that population rather than as inference to a hypothetical super-population (Berk & Freedman, 2003). Reporting follows STROBE guidance for observational studies (von Elm et al., 2007).

## 2.2 Setting and inclusion

The cohort comprises every athlete who participated in any of the five consecutive autumn editions of a regional grassroots youth meet held simultaneously at three venues in eastern, mid, and western Norway between 2011 and 2016: NCC-lekene 2011, NCC-lekene 2012, PEAB-lekene 2013, PEAB-lekene 2014, Bendit-lekene 2015, and Ungdomslekene 2016 (the meet retained an identical format, venue rotation, age-group structure, and event programme while changing sponsor name). Each edition admitted athletes aged 13–14 in the year of the meet. Athletes were free to enter as 13-year-olds, as 14-year-olds, or both; entry was not contingent on selection by coaches or on achieving qualifying performance benchmarks. The meets did, however, involve a *soft form of self-selection*: entering a regional meet typically requires being a registered club member who has trained and competed locally during the season. This selection threshold is a design feature rather than a limitation. It ensures that the baseline cohort consists of adolescents who are already actively engaged in organized track and field — not children who occasionally attended a school physical-education event or accompanied a friend to a single neighbourhood race. The subsequent disengagement trajectories we trace therefore unfold from a baseline state of demonstrable engagement, sharpening the substantive interpretation of any later behavioural decline.

To enable cross-cohort replication, we partitioned participants into two birth-year cohorts: **Cohort A** (birth years 1998–2000, baseline meets 2011–2014; n = 1,301) and **Cohort B** (birth years 2001–2002, baseline meets 2014–2016; n = 822). Cohort B's earliest participants thus had baseline three years after Cohort A's, with no design changes between the two cohorts other than sponsor name.

Athletes were retained in the analysis regardless of subsequent transfers between clubs or events. The total analytical cohort comprised 2,123 athletes (996 male, 1,103 female, 24 with unknown sex), generating 230,868 individual competition entries through the most recent register update (April 2026).

## 2.3 Follow-up window

Each athlete was followed from their baseline meet year through the most recent complete competition season at the time of analysis (2025), yielding a maximum of 14 years of post-baseline observation (for athletes born 1998 and competing as 13-year-olds at the 2011 meet) and a minimum of 9 years (for athletes born 2002 and competing as 14-year-olds at the 2016 meet). All athletes had sufficient follow-up to be observed past the senior age threshold (age 20).

## 2.4 Variables

### 2.4.1 Outcome variables

The primary outcome was **active senior status**: a binary indicator coded 1 if the athlete had at least two registered competition results in any single calendar year at age 20 or later, and 0 otherwise. The two-results threshold was chosen to exclude athletes who returned to the register only sporadically (e.g., for a single charity race) while remaining inclusive of those competing in distinct events within a single meet. Age 20 marks the formal transition to senior competition in Norwegian track and field. To assess sensitivity to operational choices, we re-estimated the central analyses using two alternative outcome definitions: (A) ≥1 senior-age result and (C) ≥2 results in each of two distinct senior-age calendar years (Supplementary Table S9).

For survival analyses, we used time from baseline to the athlete's last *active season* (a calendar year with ≥2 registered results) as duration, with athletes still active in 2024 or later treated as right-censored.

### 2.4.2 Performance variables

Each result was converted to a Tyrving age-norm score, the Norwegian Athletics Federation's official scoring system for youth track and field. Tyrving points are computed from a published table that gives, for each event × sex × age combination, a reference performance equivalent to 1,000 points and a per-unit-change quotient (Norges Friidrettsforbund, 2024). A performance of exactly 1,000 points corresponds to the federation's published "excellent" benchmark for that combination. Points are linearly extrapolated above and below the reference, capped in our analyses at 1,500 to suppress occasional implausibly extreme values arising from data-entry errors in middle-distance times.

For each athlete we computed: **tyrving_best** (the maximum Tyrving score across all events at the baseline meet), **tyrving_mean** (the mean), **tyrving_peak_pre15** (the maximum across all results before age 15), and **tyrving_slope_13_16** (the OLS slope of age-specific maximum Tyrving regressed on age across ages 13–16, indexing performance trajectory).

### 2.4.3 Specialization variables

For each athlete and each calendar year we counted the distinct event categories (sprint, middle-distance, long-distance, hurdles, jumps, throws, combined events, race walking, relay) in which they recorded results, and computed a Herfindahl–Hirschman concentration index

$$HHI = \sum_{i=1}^{k} s_i^2$$

where $s_i$ is the share of that athlete's results falling in category $i$ and $k$ is the number of categories. HHI ranges from 1/k (perfectly diversified across k categories) to 1 (perfect specialization). Key variables were **hhi_early** (HHI computed over the first three active seasons), **hhi_age_15**, and **hhi_change** = hhi_age_15 − hhi_age_13.

### 2.4.4 Behavioral engagement variables

For each athlete and each integer age year from 13 to 18, we counted the number of distinct competition meets attended (**vol_age_X**), the total number of results (**res_age_X**), and a binary year-round indicator (**helaars_age_X** = 1 if the athlete competed in both an outdoor and an indoor meet in that age year, else 0). We derived composite indicators: **vol_pre_milepael** (sum of meets at ages 13–14, the pre-qualification window), **vol_milepael** (sum of meets at ages 15–16, the qualification-milestone window), and **vol_trend_milepael** (vol_milepael − vol_pre_milepael). We also computed **n_msk_typer**, a count of championship *types* (Norwegian Youth Championships, Junior National Championships, National Championships, Regional Championships) in which the athlete competed before age 17.

We treat these variables as *observable behavioral markers* of engagement, not as direct measures of motivation or commitment. Their interpretation as evidence for an underlying engagement-balance mechanism depends on whether their temporal structure is consistent with the predictions of the theoretical accounts described in the Introduction.

### 2.4.5 Control variables

We recorded sex (M/F as registered in the federation's database), birth quarter (Q1–Q4) for relative-age-effect analyses, baseline region (eastern, mid, or western Norway, by venue), and club size in the baseline year (number of registered athletes in the same club).

## 2.5 Statistical analysis

### 2.5.1 Survival analysis

We modelled time from baseline to last active season using Cox (1972) proportional hazards regression, with hazard function $h(t \mid \mathbf{x}) = h_0(t) \exp(\boldsymbol{\beta}^{\top} \mathbf{x})$, where $h(t \mid \mathbf{x})$ is the dropout hazard at follow-up time $t$ for an athlete with covariate vector $\mathbf{x}$, $h_0(t)$ is the unspecified baseline hazard, and $\boldsymbol{\beta}$ is the vector of regression coefficients. Ties were handled with Efron's (1977) method, the lifelines default (Davidson-Pilon, 2024).

Models were fitted in a stepwise sequence to characterize the unique contribution of each variable class: M1 (sex only), M2 (+ performance), M3 (+ specialization), M4 (+ competition volume at milestone), and M5 (+ championship types). The entry order was theoretically driven: starting from the variable most commonly emphasized in prior literature (sex) and ending with the class motivated by our hypothesis (behavioral engagement at the milestone). We did not perform data-driven variable selection, because all candidate predictors were theoretically motivated. Concordance indices (C-index; Harrell et al., 1996) gauged the discriminative gain at each step. Continuous covariates were standardized (z-scored) so that hazard ratios reflect per-SD effects. Throughout, hazard ratios are reported as *descriptive associations within the observed register structure* and should not be interpreted causally; register-based competition behavior reflects both individual choice and contextual factors (selection, injury, family circumstances, parallel sport involvement) that are not observed.

Kaplan–Meier curves were stratified by sex, by total competition volume at age 15–16 (categorized into 0, 1–5, 6–15, 16–30, or 31+ meets), and by number of championship types entered before age 17.

### 2.5.2 Addressing potential measurement-tautology: landmark analysis

Because senior retention is itself defined by registered competitive activity, and the strongest candidate predictor (competition volume at age 15–16) is also a measure of registered competitive activity, the two measurements are operationally related. Specifically, an athlete who has already withdrawn from competition before age 15 has vol_milepael = 0 by construction *and* will not meet the senior-retention criterion. Without explicit treatment, the apparent predictive power of milestone volume could partly reflect this mechanical relationship.

To address this concern, we conducted a **landmark analysis** (van Houwelingen, 2007): we restricted the analysis to athletes who were still demonstrably active at age 16 (defined as having ≥1 registered result at age 16) and re-estimated the full Cox model with follow-up time measured from age 16 rather than from baseline. This analysis tests whether milestone-window volume continues to predict subsequent retention *among athletes who have not yet dropped out*. We additionally re-estimated the full Cox model excluding athletes with vol_milepael = 0 (Supplementary Table S12), and fitted a *lagged-volume* model in which the only behavioral predictor was vol_pre_milepael (ages 13–14), testing whether the signal exists before the milestone window itself (Supplementary Table S10).

### 2.5.3 Proportional-hazards assumption and time-varying effects

We assessed the proportional-hazards assumption using Schoenfeld residuals (Grambsch & Therneau, 1994). Where the assumption was violated, we re-estimated the model stratified on the violating variable (Therneau & Grambsch, 2000) to confirm that remaining effects were robust. To characterize the time-varying nature of the dominant predictor, we fitted period-specific Cox models in three follow-up windows (years 0–3, 3–6, and 6+ post-baseline), reporting HR with 95% confidence intervals separately for each window.

### 2.5.4 Sample size and detection capacity

Although a-priori power calculations are standard in experimental designs, they are less directly applicable to population-based register studies where the full cohort meeting inclusion criteria is observed and there is no sampling step at which the analyst chooses an *N*. We therefore replace the standard a-priori power calculation with a *detection-capacity* analysis: given the observed event count, what is the smallest effect size that the design could reliably detect, and how does this compare to effect sizes reported in prior longitudinal dropout research?

We computed the minimum detectable hazard ratio using Hsieh and Lavori's (2000) formula $|\log HR_{\min}| = (z_{1-\alpha/2} + z_{1-\beta}) / (\sigma \sqrt{d})$, where $d$ is event count and $\sigma$ is the SD of the standardized covariate (= 1 for z-scored covariates). With $d = 1{,}570$ events, $\alpha = .05$, and 80% power, $HR_{\min} \approx 1.07$ per SD — i.e., effects with $HR < 0.93$ or $> 1.07$ are detectable.

Effect sizes in prior prospective youth-sport dropout research are typically *small-to-moderate*: motivational and engagement-based predictors in 12–24-month prospective designs (Sarrazin et al., 2002; Calvo et al., 2010) and in survey-based studies of dropout reasons (Espedalen & Seippel, 2022) generally correspond to standardized effect-size estimates in the small-to-moderate range (Cohen's *d* ≈ 0.2–0.5; comparable odds ratios ≈ 1.4–2.5). The detection capacity of the present design (minimum detectable HR ≈ 1.07) is therefore well below the effect magnitudes typically reported in this literature; null findings reported here (e.g., the unadjusted sex coefficient in M1, or HHI in M3) should be interpreted as substantively small rather than as underpowered.

### 2.5.5 Missing data and clustering

Missing values arose primarily for the Tyrving score (athletes whose only baseline results were in events without an official Tyrving reference, ~20% missing) and for HHI (athletes with fewer than 3 active seasons, ~10%). Our primary analyses used complete-case Cox regression (n = 1,704 for the full model). To assess sensitivity, we re-estimated the full Cox model substituting variable means for missing continuous covariates; estimates were near-identical to the complete-case results (Supplementary Table S5). Because athletes are nested within clubs and might share unobserved club-level characteristics, we additionally re-estimated the model with cluster-robust standard errors clustered on club name (Lin & Wei, 1989); coefficients were unchanged and 95% CIs only marginally wider (Supplementary Table S2).

### 2.5.6 Sensitivity to unmeasured confounding and cross-cohort replication

For the dominant covariate (vol_milepael) and for the championship-types count, we computed the **E-value** (VanderWeele & Ding, 2017), which quantifies the minimum strength of association on the risk-ratio scale that an unmeasured confounder would need to have with both the exposure and the outcome to explain away the observed effect entirely. To assess **cross-cohort replication**, we re-estimated the full Cox model separately within Cohort A (1998–2000) and Cohort B (2001–2002). We additionally fitted subgroup Cox models within each sex stratum.

### 2.5.7 Calibration and practical early-warning thresholds

To inform the practical claim that competition volume can serve as an early-warning indicator, we computed calibration metrics — sensitivity, specificity, positive predictive value (PPV), and negative predictive value (NPV) — at five candidate thresholds for "flagging" an athlete as high-risk (vol_milepael < 1, 5, 10, 15, or 20 meets across ages 15–16). We additionally produced a decile-based calibration plot comparing observed to predicted retention probabilities (Supplementary Figure S1).

### 2.5.8 Variable importance (supplementary)

For non-parametric variable importance, we fit a random forest (Breiman, 2001) with 500 trees and maximum depth 8 to predict active senior status, with class weighting to handle outcome imbalance (16% senior retainers). Variable importance is reported as the mean decrease in Gini impurity. Cross-validated AUCs (5-fold stratified) compared nested subsets of predictors. We treat the random forest as convergent evidence for the Cox findings rather than as an independent main analysis.

### 2.5.9 Software

All analyses used Python 3.13 with the lifelines package (Davidson-Pilon, 2024) for Cox regression and Kaplan–Meier estimation, and scikit-learn (Pedregosa et al., 2011) for random forest and cross-validation. Figures were produced with matplotlib (Hunter, 2007). Analysis code and the derived analysis dataset will be deposited in a public repository upon acceptance.

## 2.6 Sex and gender

Following SAGER guidance (Heidari et al., 2016), we report all primary analyses stratified by sex. We use "sex" throughout because the federation registers a binary sex variable assigned at registration; we have no information on gender identity. Where sex appears as a covariate (`female` = 1 for female, 0 for male, NA for unknown), it indexes biological sex as recorded.

## 2.7 Ethics

The study uses only data that is publicly accessible via the Norwegian Athletics Federation's competition register. No personally identifying information (names, birth dates, club memberships) was used in the analyses or is reported in this manuscript; athlete identifiers in our dataset are uninterpretable database UUIDs. Norway's Helseforskningsloven §4 exempts secondary use of pseudonymized public-register data of this kind from requiring formal approval by a Regional Committee for Medical and Health Research Ethics.
