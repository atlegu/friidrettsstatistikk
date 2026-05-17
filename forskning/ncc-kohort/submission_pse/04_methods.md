# Methods

## Design

This was a retrospective longitudinal cohort study of Norwegian youth track-and-field athletes, using the national competition register as the sole data source. The design reports the complete population of athletes meeting the inclusion criterion rather than a sample, and we therefore frame statistical inference as descriptive of that population rather than as inference to a hypothetical superpopulation (Berk & Freedman, 2003). Reporting follows STROBE guidance for observational studies (von Elm et al., 2007).

## Setting and inclusion

The cohort comprises every athlete who participated in any of the five consecutive autumn editions of a regional grassroots youth meet held simultaneously at three venues in eastern, mid, and western Norway between 2011 and 2016: NCC-lekene 2011, NCC-lekene 2012, PEAB-lekene 2013, PEAB-lekene 2014, Bendit-lekene 2015, and Ungdomslekene 2016 (the meet retained an identical format and venue rotation while changing sponsor name). Each edition admitted athletes aged 13–14 in the year of the meet. Athletes were free to enter as 13-year-olds, as 14-year-olds, or both; participation was not contingent on selection or qualifying performance.

To enable cross-cohort replication, we partitioned participants into two birth-year cohorts: **Cohort A** (birth years 1998–2000, baseline meets 2011–2014; n = 1,301) and **Cohort B** (birth years 2001–2002, baseline meets 2014–2016; n = 822). Cohort B's earliest participants thus had baseline 3 years after Cohort A's, with no design changes between the two cohorts other than sponsor name.

Athletes were retained in the analysis regardless of subsequent transfers between clubs or events. The total analytical cohort comprised 2,123 athletes (996 male, 1,103 female, 24 with unknown sex), generating 230,868 individual competition entries through the most recent register update (April 2026).

## Follow-up window

Each athlete was followed from their baseline meet year through the most recent complete competition season at the time of analysis (2025), yielding a maximum of 14 years of post-baseline observation (for athletes born 1998 and competing as 13-year-olds at the 2011 meet) and a minimum of 9 years (for athletes born 2002 and competing as 14-year-olds at the 2016 meet). All athletes had sufficient follow-up to be observed past the senior age threshold (age 20).

## Variables

### Outcome variables

The primary outcome was **active senior status**: a binary indicator coded 1 if the athlete had at least two registered competition results in any single calendar year at age 20 or later, and 0 otherwise. Secondary outcomes were *active age 17*, *active age 18*, and *continued activity in 2024 or later*. An *active season* was operationalized as a calendar year with ≥2 registered results, to exclude athletes who returned to the register only sporadically.

For survival analyses, we used **time to last active season** as duration and the absence of activity in 2024+ as the event indicator, with athletes still competing in 2024+ treated as right-censored.

### Performance variables

Each result was converted to a Tyrving age-norm score, the Norwegian Athletics Federation's official scoring system for youth track and field. Tyrving points are computed from a published table that gives, for each event × sex × age combination, a reference performance equivalent to 1,000 points and a per-unit-change quotient (Norges Friidrettsforbund, 2024). A performance of exactly 1,000 points corresponds to the federation's published "excellent" benchmark for that combination. Points are linearly extrapolated above and below the reference, capped in our analyses at 1,500 to suppress occasional implausibly extreme values arising from data-entry errors in middle-distance times.

For each athlete we computed: **tyrving_best** (the maximum Tyrving score across all events at the baseline meet), **tyrving_mean** (the mean), **tyrving_peak_pre15** (the maximum across all results before age 15), and **tyrving_slope_13_16** (the OLS slope of age-specific maximum Tyrving regressed on age across ages 13–16, indexing performance trajectory). We also derived a within-event, within-sex, within-meet percentile rank at baseline to give a complementary relative-performance measure that is robust to age-norm idiosyncrasies in the Tyrving table.

### Specialization variables

For each athlete and each calendar year we counted the distinct event categories (sprint, middle-distance, long-distance, hurdles, jumps, throws, combined events, race walking, relay) in which they recorded results, and computed a Herfindahl-Hirschman concentration index HHI = Σ(s²ᵢ), where sᵢ is the share of that athlete's results falling in category *i*. HHI ranges from 1/k (perfectly diversified across k categories) to 1 (perfect specialization). Key variables were **hhi_early** (HHI computed over the first three active seasons), **hhi_age_15**, and **hhi_change** = hhi_age_15 − hhi_age_13.

### Behavioral engagement variables

For each athlete and each integer age year from 13 to 18, we counted the number of distinct competition meets attended (**vol_age_X**), the total number of results (**res_age_X**), and a binary year-round indicator (**helaars_age_X** = 1 if the athlete competed in both an outdoor and an indoor meet in that age year, else 0). We derived composite indicators including **vol_pre_milepael** (sum of meets at ages 13–14), **vol_milepael** (sum of meets at ages 15–16, the qualification milestone window), and **vol_trend_milepael** (vol_milepael − vol_pre_milepael), as well as **n_msk_typer**, a count of championship *types* (Norwegian Youth Championships, Junior National Championships, National Championships, Regional Championships) in which the athlete competed before age 17.

### Control variables

We recorded sex (M/F as registered in the federation's database), birth quarter (Q1–Q4) for relative-age-effect analyses, baseline region (eastern, mid, or western Norway, by venue), and club size in the baseline year (number of registered athletes in the same club).

## Statistical analysis

Survival analysis used Kaplan–Meier estimators stratified by sex, competition-volume strata at age 15–16, and number of championship types. Cox proportional hazards models were fitted in a stepwise sequence to characterize the unique contribution of each variable class: M1 (sex only), M2 (+ performance), M3 (+ specialization), M4 (+ competition volume at milestone), and M5 (+ championship types). Concordance indices (C-index) gauged the discriminative gain at each step. Continuous covariates were standardized (z-scored) so that hazard ratios reflect per-SD effects.

For non-parametric variable importance, we fit a random forest with 500 trees and maximum depth 8 to predict active senior status, with class weighting to handle outcome imbalance. Cross-validated AUCs (5-fold stratified) compared nested subsets of predictors: baseline-only (sex + Tyrving), specialization-only, competition-volume-only, pre-baseline behavioral combined, and the full predictor set.

To assess **cross-cohort replication**, we re-estimated the full Cox model separately within Cohort A (1998–2000) and Cohort B (2001–2002).

All analyses used Python 3.13 with the lifelines package (Davidson-Pilon, 2024) for survival analysis and scikit-learn (Pedregosa et al., 2011) for random forests.

## Sex and gender

Following SAGER guidance (Heidari et al., 2016), we report all primary analyses stratified by sex. We use "sex" throughout because the federation registers a binary sex variable assigned at registration; we have no information on gender identity. Where sex appears as a covariate (`female` = 1 for female, 0 for male, NA for unknown), it indexes biological sex as recorded.

## Ethics and data availability

The study uses only data that is publicly accessible via the Norwegian Athletics Federation's competition register. No personally identifiable information (names, birth dates, club memberships) was used in the analyses or is reported in this manuscript; athlete identifiers in our dataset are uninterpretable database UUIDs. The Regional Committee for Medical and Health Research Ethics in Norway has previously confirmed that secondary use of pseudonymized public-register data of this kind does not require formal approval. Analysis code is available at [URL withheld for double-blind review].
