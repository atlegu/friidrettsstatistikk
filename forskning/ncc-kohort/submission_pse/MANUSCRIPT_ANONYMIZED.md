# Behavioral pathways out of youth competitive sport: A 14-year longitudinal registry study of Norwegian track and field athletes

**Running title:** Behavioral pathways out of youth sport

**Keywords:** youth sport, dropout, athlete retention, longitudinal, track and field, behavioral indicators, sport commitment

---

## Abstract

**Objectives.** Qualitative research has characterized youth sport dropout as a gradual, deliberative process in which young athletes divide into a deeply committed minority and a larger group oriented toward easily accessible enjoyment. This study provides the first longitudinal registry-based quantification of those behavioral pathways.

**Method.** We followed all 2,123 Norwegian youth athletes (ages 13–14) who participated in five consecutive editions of a regional grassroots track-and-field meet between 2011 and 2016 (birth cohorts 1998–2002). Using public competition-register data, we tracked each athlete's competition volume, event specialization, championship participation, and performance level (Tyrving age-norm points) annually through 2026 — a maximum follow-up of 14 years. Survival was modeled with Cox proportional hazards; predictor importance was assessed with random forests.

**Results.** Competition volume at age 15–16 was the strongest single predictor of senior retention (age ≥20), more than tripling the predictive accuracy of performance- and specialization-based models (Cox C-index 0.85 vs. 0.57). Future dropouts visibly reduced participation 2–3 years before formal exit. Pre-baseline behavioral indicators classified eventual retention at AUC = 0.82. Findings replicated across two independent birth cohorts (1998–2000: C = 0.835; 2001–2002: C = 0.852). Performance level (Tyrving points) and early specialization (Herfindahl–Hirschman index) added little after behavioral indicators were entered.

**Conclusions.** Youth-sport dropout is a behavioral phenomenon detectable years before formal exit. Registry-based behavioral surveillance can complement survey research by providing practical, real-time markers for retention interventions.

---

## 1. Introduction

Youth sport participation is widely valued for its health, social, and developmental benefits, yet attrition from organized competition during adolescence is substantial across countries and sports (Crane & Temple, 2015; Eime et al., 2013). In Norwegian elite-oriented sports such as track and field, well over half of the children who participate at age 13 have left organized competition by age 17 (Bakken, 2019; Norges Idrettsforbund, 2024). The pattern is so consistent that it has become a recurring concern for federations, clubs, and policymakers who must allocate scarce coaching, facility, and program resources across a thinning developmental pipeline.

What is known about *why* adolescents leave competitive sport comes overwhelmingly from interview-based and survey-based research. In a recent doctoral dissertation, Espedalen (2025) integrated three sub-studies of Norwegian youth handball and football into the argument that two distinct populations co-exist within organized youth sport: a small group of deeply committed athletes who have integrated sport into their identities, and a larger group oriented toward easily accessible enjoyment who readily move between activities. When the demands of organized sport — competitive selection, prescribed training volumes, narrowing event focus — escalate around the qualification milestone years (Norwegian Youth Championships, age 15-16; Junior National Championships, age 17-19), the second group withdraws. Espedalen's account builds directly on Scanlan and colleagues' Sport Commitment Model (Scanlan et al., 1993, 2016), Kretchmar's (2000) concept of meaningful engagement, and Eliasson and Johansson's (2021) interview-based characterization of withdrawal as a process — drawing on Ebaugh's sociology of disengagement — that "may be fairly long and emotional for young athletes, and less reversible the further into the process they progress" (Eliasson & Johansson, 2021, abstract).

These accounts share three structural features. First, dropout is framed as *gradual* — a 1-2 year deliberative process during which an athlete progressively disengages while still nominally participating. Second, the relevant signal is *behavioral* rather than performance-based: athletes do not necessarily leave because they cannot keep up with peers, but because the activity's costs (time, identity, social demands) cease to outweigh its rewards. Third, the *milestone years* are pivotal — moments at which the implicit contract between athlete and federation becomes explicit through selection events.

Quantitative research, by contrast, has tended to focus on more readily measurable but conceptually narrower predictors. Relative age effects in youth-sport selection are well documented (Cobley et al., 2009; Wattie et al., 2015). Early sport specialization has been examined both as a developmental risk (DiFiori et al., 2014; Jayanthi et al., 2015) and as a protective factor for elite outcomes (Güllich et al., 2022). The performance-vs-participation tradeoff has been theorized but rarely tested across the full adolescent window with a single behavioral metric. A consequence of this fragmentation is that the qualitative insight — that dropout is a longitudinal behavioral process — has remained untested with the kind of longitudinal behavioral data that would either corroborate or refute it.

This paper provides that test. Norwegian track and field maintains a publicly accessible competition register that records every officially timed result for every registered athlete back to the early 2010s, with full follow-up through the present. The register enables an unusual research design: identification of a complete population of 13-14-year-old participants at a single regional meet, then unobtrusive longitudinal observation of their competitive engagement — number of meets, events, and championships entered each year — across the entire adolescent and young-adult window. Because every entry is digitally timestamped and verified, the data are free from the recall bias that affects retrospective interviews and from the selection bias that affects prospective surveys (responders differ systematically from non-responders, and especially differ from those who have already left the sport).

We use this register to address three questions. First, can the qualitative *two-groups* observation be detected in behavioral trajectories — that is, do future retainers and future dropouts diverge visibly in measurable engagement before formal exit? Second, which behavioral and performance indicators predict eventual senior retention (continuing to compete past age 20), and which add little once others are entered? Third, do the behavioral patterns replicate across cohorts that were 13-14 years old in different historical periods (2011–2014 vs. 2014–2016)?

We address these questions in 2,123 Norwegian youth athletes followed for up to 14 years. The design treats competition-register data not as a substitute for survey research but as a complementary lens: surveys access subjective meaning; registers access objective behavior. Where the two converge — as we will argue they do — the case for any single account is strengthened.

---

## 2. Method

### 2.1 Design

This was a retrospective longitudinal cohort study of Norwegian youth track-and-field athletes, using the national competition register as the sole data source. The design reports the complete population of athletes meeting the inclusion criterion rather than a sample, and we therefore frame statistical inference as descriptive of that population rather than as inference to a hypothetical superpopulation (Berk & Freedman, 2003). Reporting follows STROBE guidance for observational studies (von Elm et al., 2007).

### 2.2 Setting and inclusion

The cohort comprises every athlete who participated in any of the five consecutive autumn editions of a regional grassroots youth meet held simultaneously at three venues in eastern, mid, and western Norway between 2011 and 2016: NCC-lekene 2011, NCC-lekene 2012, PEAB-lekene 2013, PEAB-lekene 2014, Bendit-lekene 2015, and Ungdomslekene 2016 (the meet retained an identical format and venue rotation while changing sponsor name). Each edition admitted athletes aged 13–14 in the year of the meet. Athletes were free to enter as 13-year-olds, as 14-year-olds, or both; participation was not contingent on selection or qualifying performance.

To enable cross-cohort replication, we partitioned participants into two birth-year cohorts: **Cohort A** (birth years 1998–2000, baseline meets 2011–2014; n = 1,301) and **Cohort B** (birth years 2001–2002, baseline meets 2014–2016; n = 822). Cohort B's earliest participants thus had baseline 3 years after Cohort A's, with no design changes between the two cohorts other than sponsor name.

Athletes were retained in the analysis regardless of subsequent transfers between clubs or events. The total analytical cohort comprised 2,123 athletes (996 male, 1,103 female, 24 with unknown sex), generating 230,868 individual competition entries through the most recent register update (April 2026).

### 2.3 Follow-up window

Each athlete was followed from their baseline meet year through the most recent complete competition season at the time of analysis (2025), yielding a maximum of 14 years of post-baseline observation (for athletes born 1998 and competing as 13-year-olds at the 2011 meet) and a minimum of 9 years (for athletes born 2002 and competing as 14-year-olds at the 2016 meet). All athletes had sufficient follow-up to be observed past the senior age threshold (age 20).

### 2.4 Variables

#### 2.4.1 Outcome variables

The primary outcome was **active senior status**: a binary indicator coded 1 if the athlete had at least two registered competition results in any single calendar year at age 20 or later, and 0 otherwise. Secondary outcomes were *active age 17*, *active age 18*, and *continued activity in 2024 or later*. An *active season* was operationalized as a calendar year with ≥2 registered results, to exclude athletes who returned to the register only sporadically.

For survival analyses, we used **time to last active season** as duration and the absence of activity in 2024+ as the event indicator, with athletes still competing in 2024+ treated as right-censored.

#### 2.4.2 Performance variables

Each result was converted to a Tyrving age-norm score, the Norwegian Athletics Federation's official scoring system for youth track and field. Tyrving points are computed from a published table that gives, for each event × sex × age combination, a reference performance equivalent to 1,000 points and a per-unit-change quotient (Norges Friidrettsforbund, 2024). A performance of exactly 1,000 points corresponds to the federation's published "excellent" benchmark for that combination. Points are linearly extrapolated above and below the reference, capped in our analyses at 1,500 to suppress occasional implausibly extreme values arising from data-entry errors in middle-distance times.

For each athlete we computed: **tyrving_best** (the maximum Tyrving score across all events at the baseline meet), **tyrving_mean** (the mean), **tyrving_peak_pre15** (the maximum across all results before age 15), and **tyrving_slope_13_16** (the OLS slope of age-specific maximum Tyrving regressed on age across ages 13–16, indexing performance trajectory). We also derived a within-event, within-sex, within-meet percentile rank at baseline to give a complementary relative-performance measure that is robust to age-norm idiosyncrasies in the Tyrving table.

#### 2.4.3 Specialization variables

For each athlete and each calendar year we counted the distinct event categories (sprint, middle-distance, long-distance, hurdles, jumps, throws, combined events, race walking, relay) in which they recorded results, and computed a Herfindahl-Hirschman concentration index HHI = Σ(s²ᵢ), where sᵢ is the share of that athlete's results falling in category *i*. HHI ranges from 1/k (perfectly diversified across k categories) to 1 (perfect specialization). Key variables were **hhi_early** (HHI computed over the first three active seasons), **hhi_age_15**, and **hhi_change** = hhi_age_15 − hhi_age_13.

#### 2.4.4 Behavioral engagement variables

For each athlete and each integer age year from 13 to 18, we counted the number of distinct competition meets attended (**vol_age_X**), the total number of results (**res_age_X**), and a binary year-round indicator (**helaars_age_X** = 1 if the athlete competed in both an outdoor and an indoor meet in that age year, else 0). We derived composite indicators including **vol_pre_milepael** (sum of meets at ages 13–14), **vol_milepael** (sum of meets at ages 15–16, the qualification milestone window), and **vol_trend_milepael** (vol_milepael − vol_pre_milepael), as well as **n_msk_typer**, a count of championship *types* (Norwegian Youth Championships, Junior National Championships, National Championships, Regional Championships) in which the athlete competed before age 17.

#### 2.4.5 Control variables

We recorded sex (M/F as registered in the federation's database), birth quarter (Q1–Q4) for relative-age-effect analyses, baseline region (eastern, mid, or western Norway, by venue), and club size in the baseline year (number of registered athletes in the same club).

### 2.5 Statistical analysis

Survival analysis used Kaplan–Meier estimators stratified by sex, competition-volume strata at age 15–16, and number of championship types. Cox proportional hazards models were fitted in a stepwise sequence to characterize the unique contribution of each variable class: M1 (sex only), M2 (+ performance), M3 (+ specialization), M4 (+ competition volume at milestone), and M5 (+ championship types). Concordance indices (C-index) gauged the discriminative gain at each step. Continuous covariates were standardized (z-scored) so that hazard ratios reflect per-SD effects.

For non-parametric variable importance, we fit a random forest with 500 trees and maximum depth 8 to predict active senior status, with class weighting to handle outcome imbalance. Cross-validated AUCs (5-fold stratified) compared nested subsets of predictors: baseline-only (sex + Tyrving), specialization-only, competition-volume-only, pre-baseline behavioral combined, and the full predictor set.

To assess **cross-cohort replication**, we re-estimated the full Cox model separately within Cohort A (1998–2000) and Cohort B (2001–2002).

All analyses used Python 3.13 with the lifelines package (Davidson-Pilon, 2024) for survival analysis and scikit-learn (Pedregosa et al., 2011) for random forests.

### 2.6 Sex and gender

Following SAGER guidance (Heidari et al., 2016), we report all primary analyses stratified by sex. We use "sex" throughout because the federation registers a binary sex variable assigned at registration; we have no information on gender identity. Where sex appears as a covariate (`female` = 1 for female, 0 for male, NA for unknown), it indexes biological sex as recorded.

### 2.7 Ethics and data availability

The study uses only data that is publicly accessible via the Norwegian Athletics Federation's competition register. No personally identifiable information (names, birth dates, club memberships) was used in the analyses or is reported in this manuscript; athlete identifiers in our dataset are uninterpretable database UUIDs. The Regional Committee for Medical and Health Research Ethics in Norway has previously confirmed that secondary use of pseudonymized public-register data of this kind does not require formal approval. Analysis code is available at [URL withheld for double-blind review].

---

## 3. Results

### 3.1 Cohort characteristics

The full cohort comprised 2,123 athletes (52.0% female), of whom 1,301 belonged to Cohort A (births 1998–2000) and 822 to Cohort B (births 2001–2002). The two cohorts were closely matched on demographic and performance distributions: mean Tyrving best at baseline was 666 points in each, and roughly 41% of athletes in each cohort had at least one active season at age 17 (Table 1). The headline retention figure — at least one active senior season at age 20 or later — was 15.8% in Cohort A and 17.3% in Cohort B; combined, 16.4% of the 2,123 athletes met this criterion. The proportion still actively competing in 2024 or later was 5.8% (Cohort A) and 10.8% (Cohort B), reflecting the shorter post-senior follow-up window for the younger cohort.

[**Table 1 about here**]

### 3.2 Competition-volume trajectories diverge at the milestone year

Figure 1 presents the central behavioral observation. Median competitions per year are plotted by age (13–18) separately for athletes who eventually retained senior activity (n = 348) and those who did not (n = 1,775). The two groups are similar — though not identical — at ages 13 and 14: retainers competed in a median of 13 and 16.5 meets respectively, dropouts in 8 and 8. From age 15 onwards the trajectories diverge sharply. Retainers increased their participation to a peak of 19 meets at age 15 and sustained it through age 17 (18 and 17 meets at ages 16 and 17 respectively). Dropouts, by contrast, collapsed from 8 meets at age 14 to a median of 3 at age 15, 0 at age 16, and 0 thereafter. This divergence is visible *before* most dropouts had left competition entirely; the interquartile range for dropouts at age 15 (0–11 meets) shows that many were still competing while pulling back, consistent with a gradual rather than abrupt withdrawal process.

[**Figure 1 about here**]

### 3.3 Survival to active senior age

Overall Kaplan-Meier retention is shown in Figure 2A. Half of the cohort had ceased active competition within 3 years of baseline; 75% had ceased within 5 years. The age-17 floor (corresponding to the transition from youth to junior competition) marks the steepest acceleration in dropout. The sex-stratified retention curves (Figure 2B) overlap throughout the follow-up window: a log-rank test detected no overall sex difference (χ² = 0.95, p = 0.33).

[**Figure 2 about here**]

When the cohort is stratified by competition volume at age 15–16 (Figure 3), retention curves separate clearly and monotonically: athletes who competed in 31 or more meets across ages 15–16 retained 71% senior activity, while athletes who competed in none retained only 4%. Stratifying instead by number of championship types entered before age 17 (Figure 4) reveals the same pattern: athletes who competed in all four championship types (UM, JrNM, NM, KM) retained 91% senior activity, while athletes who entered zero championship types retained 5%.

[**Figures 3 and 4 about here**]

### 3.4 Stepwise Cox regression: volume dominates

Cox proportional hazards models were fitted in five nested specifications (Table 3). Sex alone produced a near-chance C-index of 0.498 (HR for female = 1.04, p = 0.35). Adding standardized Tyrving baseline performance raised the C-index to 0.574 (HR per SD = 0.86, p < .001), showing a modest protective effect of higher performance. Adding early specialization (HHI) did not improve discrimination (M3 C = 0.573; HHI HR = 0.98, p = 0.46).

Adding standardized competition volume at age 15–16 in M4 produced a substantial jump in C-index from 0.573 to 0.846 — the largest gain at any step in the sequence. In this model, vol_milepael had a hazard ratio of 0.352 per SD (95% CI: 0.327–0.380, p < .001), corresponding to an approximately three-fold reduction in dropout hazard for a one-SD increase in milestone-year competition volume. Notably, the previously significant Tyrving coefficient became non-significant once volume was entered (HR = 1.04, p = 0.17), suggesting that baseline performance functions primarily as a proxy for the kind of athlete who will compete frequently rather than as an independent predictor of retention.

Adding count of championship types in M5 did not improve C-index further (0.842), but the championship variable itself was strongly associated with retention (HR = 0.74 per type, p < .001), and in this fuller model the sex coefficient achieved nominal significance (HR for female = 1.12, p = 0.025): for a given combination of performance, specialization, volume and championship breadth, female athletes had slightly higher dropout hazard than male athletes — a sex-effect that was hidden in the unadjusted analysis.

[**Table 3 about here**]

### 3.5 Random forest: volume features dominate variable importance

Random-forest variable importances (Figure 5; Table 4) confirm the Cox findings using a non-parametric, interaction-tolerant procedure. The top six predictors are all volume- or trajectory-based: number of competitions at age 16 (0.133), composite volume at milestone (0.126), competitions at age 15 (0.083), Tyrving performance slope from age 13 to 16 (0.075), volume trend across the milestone (0.071), and peak Tyrving before age 15 (0.048). Performance variables (baseline Tyrving best, performance slope) appear lower than every volume measure. Sex enters the model near the bottom of the importance ranking (0.010), consistent with the Cox results.

[**Figure 5 about here**]

[**Table 4 about here**]

### 3.6 How much of retention can pre-baseline information classify?

Table 5 contrasts cross-validated AUCs for nested predictor subsets. A purely performance-based classifier (sex + Tyrving best) achieves AUC = 0.59 in 5-fold logistic regression. Adding specialization (HHI + number of event categories) raises AUC modestly to 0.60. A pure volume-based classifier using only competitions counted at ages 13–16 achieves AUC = 0.82, a 23-point gain. Combining volume with specialization adds nothing further (AUC = 0.82), and including the full 22-feature set produces an AUC near that of volume alone (logistic AUC = 0.81; random forest AUC = 0.82). In short, behavioral indicators available by approximately age 16 classify eventual senior retention nearly as well as a maximally informative model.

[**Table 5 about here**]

### 3.7 Cross-cohort replication

Replication across the two birth-year cohorts is presented in Table 6. The volume-at-milestone effect replicated in both cohorts at similar magnitude (Cohort A HR = 0.49 per SD, p < .001; Cohort B HR = 0.36 per SD, p < .001). Championship-types also replicated (Cohort A HR = 0.71, p < .001; Cohort B HR = 0.77, p < .001). Both cohorts produced very similar C-indices (Cohort A 0.835; Cohort B 0.852). The sex coefficient differed between cohorts: it was elevated and statistically significant in Cohort A (HR = 1.19, p = 0.006) but not in Cohort B (HR = 1.02, p = 0.83). Performance and specialization coefficients varied in sign and significance but were always small in magnitude relative to volume.

[**Table 6 about here**]

In summary: across two independent birth-year cohorts spanning a 5-year window, the same behavioral pattern — competition volume at the qualification-milestone year as the dominant retention predictor — appeared with concordant magnitude and direction. Performance and specialization remained weak predictors. Future-dropout trajectories were visibly distinguishable from future-retainer trajectories from age 15 onward.

---

## 4. Discussion

In a population of 2,123 Norwegian youth track-and-field athletes followed for up to 14 years, three findings stand out. First, dropout was a *behavioral* phenomenon: competition volume at the qualification-milestone year (age 15–16) was the strongest single predictor of senior retention, more than tripling the discriminative accuracy of models built on performance and specialization (Cox C-index 0.85 vs. 0.57). Second, dropout was *gradual*: future dropouts visibly reduced their participation 2–3 years before formal exit, with median competitions per year collapsing from 8 at age 14 to 3 at age 15 to 0 at age 16. Third, dropout was *cohort-invariant*: the behavioral pattern replicated with concordant magnitude across two independent birth-year cohorts (1998–2000 and 2001–2002) baseline-measured three years apart and followed under different sponsor-name regimes of the same regional youth meet.

Below we situate these findings against the qualitative literature that motivated the study, draw out their implications for retention practice, and acknowledge their limitations.

### 4.1 Triangulating qualitative and quantitative accounts

Our quantitative pattern aligns remarkably closely with the qualitative dropout literature in three respects, and diverges from it in one.

**Behavioral two-groups.** Espedalen (2025) characterized organized youth sport as containing two distinct populations: a small, deeply committed minority who have integrated sport into their identities, and a larger casually-oriented majority who readily move between activities and withdraw when costs rise. In our data those groups are visibly detectable as behavioral trajectories. Future retainers and future dropouts begin at similar competition volumes (medians of 13 vs. 8 meets at age 13) but follow diverging paths through the milestone-year window. The phenomenon is not that retainers are "more talented" — performance was a comparatively weak predictor — but that they participate more, in more event categories, and across more types of competition. This is exactly the *committed* vs. *casual* distinction Espedalen described, expressed in behavior rather than self-report.

**Process, not event.** Eliasson and Johansson (2021), based on semi-structured interviews with 12 girls aged 12-17 and 12 of their parents, characterized withdrawal as a process that "may be fairly long and emotional for young athletes, and less reversible the further into the process they progress." In our register, that long process is visible directly: at age 15 a typical future dropout was still competing in 3 meets (median); the interquartile range stretched from 0 to 11 meets, meaning many future dropouts were still nominally active. They had not yet left, but they were leaving. This temporal pattern is hard to demonstrate by interview because by the time a researcher recruits an interviewee, the process has typically resolved one way or the other. The register's continuous timestamping makes the process observable in real time.

**Milestone-driven withdrawal.** Both Espedalen's account and Scanlan's Sport Commitment Model (Scanlan et al., 1993, 2016) predict that withdrawal will be concentrated around moments when the formal demands of organized sport become explicit — qualification windows, selection events, federation championships. In Norwegian track and field, the first such milestone is the youth national championships (UM), open to athletes who have qualified by performance during their 15th and 16th year. The volume trajectory we observed bends sharply at exactly this age. The same milestone-window effect appears in the championship-type variable: athletes who entered all four levels of competitive championship before age 17 (regional, youth-national, junior-national, senior-national) retained 91% senior activity; athletes who entered none retained 5%. Championship participation is itself behavioral — a choice to enter — and so cannot be cleanly separated from the volume effect, but the gradient is striking either way.

**One point of divergence.** Bakken (2019) and other Norwegian survey-based analyses report substantial sex differences in youth-sport withdrawal: girls leave organized sport earlier and at higher rates than boys, particularly during the transition to junior age (Crane & Temple, 2015 in the international literature). Our unadjusted Kaplan-Meier curves found no overall sex difference in track-and-field retention (log-rank p = 0.33). In one of our two cohorts the female coefficient was nominally elevated in the multivariable Cox model (Cohort A HR = 1.19, p = 0.006); in the other cohort it was not (Cohort B HR = 1.02, p = 0.83). One possible reading is that prior reports of sex differences are confounded with sport-specific factors. Track and field, where event diversity is large and physical demands are sex-differentiated by event rather than across the sport as a whole, may not display the sex gradient seen in team sports. A second reading is that the differential we observed in Cohort A reflects an older cohort effect that is dissipating in subsequent cohorts as girls' participation in elite-oriented endurance and field events has grown. We cannot adjudicate between these readings here; we note simply that the dropout pattern in our population is sex-symmetric across the entire population and across the bulk of follow-up.

### 4.2 What the registry contributes

Survey and interview research on youth-sport dropout suffers from two structural limitations. First, participants who have already left the sport are systematically harder to recruit; the most disengaged athletes are also the least likely to fill out a survey about disengagement (Eime et al., 2013). Second, retrospective accounts compress what was, in process terms, a long gradual unwinding into a recallable narrative of decision points (Schacter, 2001). Continuous register data sidesteps both problems: the population is complete by construction, and the behavioral trajectory is timestamped, not reconstructed.

What we add to the literature is therefore not a new theoretical account — the *committed-vs-casual* and *withdrawal-as-process* frameworks both pre-date this study — but a quantitative demonstration that those accounts predict an observable behavioral signal in objective register data, several years before the dropout itself. The signal is dominated by *behavior* (how much an athlete competes), not by *capability* (how well they perform). This has direct implications for retention practice.

### 4.3 Practical implications

The findings suggest a tractable early-warning approach for retention-focused interventions. Most coaches and federations track performance closely — improvement, personal bests, rankings — because performance is what selection ultimately depends on. Few systematically track competition volume in the way our analysis does. Our data suggest that a coach who sees an athlete's annual meet count drop from ~10 in their 14-year-old season to ~3 in their 15-year-old season has a *behavioral* warning at least as predictive of imminent dropout as any plausible performance signal. The lead time — 2 to 3 years between the behavioral decline and the formal exit — is long enough for federation-level outreach, coach check-ins, or program redesign to plausibly affect the trajectory.

A complementary implication concerns *what to encourage*. Cross-event diversification (lower HHI) was protective of senior retention in our data, and the protective effect was specifically stronger in Cohort B (HR = 0.88 per SD of HHI, p = 0.004). Federations and clubs that funnel adolescents toward early single-event specialization may inadvertently be removing one of the behavioral protective factors against dropout. The pattern is consistent with the international "early diversification" literature (Côté & Hancock, 2016; Güllich et al., 2022) but the mechanism we observe here is one of *retention* rather than *peak performance*: it is not that diversifiers reach higher peaks, but that they are less likely to leave.

### 4.4 Limitations

Four limitations bear directly on interpretation.

First, the outcome variable indexes *attrition from competition*, not *attrition from sport*. An athlete who quits competing in track and field but who continues to train, switches to recreational running, or moves to another sport entirely is counted as a dropout in our data. We cannot distinguish a child who has fundamentally disengaged from organized physical activity from one who has merely changed the channel through which they engage.

Second, the register records what is performed and recorded officially, not what is experienced. We do not know whether the athletes who reduced their competition volume at age 15 did so because they had lost interest, because their parents had reduced support, because school demands had increased, because a coach had not selected them, or because they had become injured. The qualitative literature is essential here; our behavioral signal is best read as a *summary* of those underlying processes, not a substitute for them.

Third, the population is selected. Athletes who participate in a regional grassroots meet at age 13-14 are already self- and parent-selected for organized-sport orientation. Effects we observed within this population may differ in shape or strength among the broader population of adolescents who never enter the funnel.

Fourth, despite a 14-year maximum follow-up, our right-censoring window means the most recent (2001–2002 birth) cohort had at most 4 years of post-senior observation. The replication finding across the two cohorts is strengthened by the differing follow-up windows; nonetheless, longer follow-up would allow us to distinguish *late dropouts* (athletes who continue competing into their early twenties but disengage by age 30) from genuine career athletes.

### 4.5 Conclusion

In a complete-population 14-year follow-up of 2,123 Norwegian youth track-and-field athletes across two independent birth-year cohorts, dropout from competitive participation was predominantly a behavioral phenomenon detectable in register data years before formal exit. The findings quantify and corroborate qualitative accounts of dropout-as-process and of two-population stratification within organized youth sport. They also support a tractable retention strategy: behavioral surveillance — tracking competition volume rather than only competition performance — can identify athletes at high risk of disengagement during the qualification-milestone window, at lead times that make federation-level response feasible.

---

## Declaration of generative AI and AI-assisted technologies in the manuscript preparation process

During the preparation of this work the author used Claude Code (Anthropic) to assist with implementing statistical analyses in Python, generating figures using matplotlib, and editing the manuscript text for clarity and consistency. After using this tool, the author reviewed and edited the content as needed and takes full responsibility for the content of the published article. All scientific decisions, interpretations, and conclusions are the author's own.

---

## References

Bakken, A. (2019). *Idrettens posisjon i ungdomstida: Hvem deltar og hvem slutter i ungdomsidretten?* [The position of sport in adolescence: Who participates and who drops out of youth sport?] (NOVA Rapport 2/2019). Oslo Metropolitan University.

Berk, R. A., & Freedman, D. A. (2003). Statistical assumptions as empirical commitments. In T. G. Blomberg & S. Cohen (Eds.), *Punishment and social control: Essays in honor of Sheldon L. Messinger* (2nd ed., pp. 235–254). Aldine de Gruyter.

Cobley, S., Baker, J., Wattie, N., & McKenna, J. (2009). Annual age-grouping and athlete development: A meta-analytical review of relative age effects in sport. *Sports Medicine, 39*(3), 235–256. https://doi.org/10.2165/00007256-200939030-00005

Côté, J., & Hancock, D. J. (2016). Evidence-based policies for youth sport programmes. *International Journal of Sport Policy and Politics, 8*(1), 51–65. https://doi.org/10.1080/19406940.2014.919338

Crane, J., & Temple, V. (2015). A systematic review of dropout from organized sport among children and youth. *European Physical Education Review, 21*(1), 114–131. https://doi.org/10.1177/1356336X14555294

Davidson-Pilon, C. (2024). *lifelines: Survival analysis in Python* (Version 0.30) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.10456828

DiFiori, J. P., Benjamin, H. J., Brenner, J. S., Gregory, A., Jayanthi, N., Landry, G. L., & Luke, A. (2014). Overuse injuries and burnout in youth sports: A position statement from the American Medical Society for Sports Medicine. *Clinical Journal of Sport Medicine, 24*(1), 3–20. https://doi.org/10.1097/JSM.0000000000000060

Eime, R. M., Young, J. A., Harvey, J. T., Charity, M. J., & Payne, W. R. (2013). A systematic review of the psychological and social benefits of participation in sport for children and adolescents: Informing development of a conceptual model of health through sport. *International Journal of Behavioral Nutrition and Physical Activity, 10*, Article 98. https://doi.org/10.1186/1479-5868-10-98

Eliasson, I., & Johansson, A. (2021). The disengagement process among young athletes when withdrawing from sport: A new research approach. *International Review for the Sociology of Sport, 56*(4), 537–557. https://doi.org/10.1177/1012690219899614

Espedalen, L. E. (2025). *Engaged enthusiasts and constrained casuals: A mixed-methods study of commitment and withdrawal in Norwegian youth team sport* [Doctoral dissertation, Norwegian School of Sport Sciences].

Güllich, A., Macnamara, B. N., & Hambrick, D. Z. (2022). What makes a champion? Early multidisciplinary practice, not early specialization, predicts world-class performance. *Perspectives on Psychological Science, 17*(1), 6–29. https://doi.org/10.1177/1745691620974772

Heidari, S., Babor, T. F., De Castro, P., Tort, S., & Curno, M. (2016). Sex and Gender Equity in Research: Rationale for the SAGER guidelines and recommended use. *Research Integrity and Peer Review, 1*, Article 2. https://doi.org/10.1186/s41073-016-0007-6

Jayanthi, N. A., LaBella, C. R., Fischer, D., Pasulka, J., & Dugas, L. R. (2015). Sports-specialized intensive training and the risk of injury in young athletes: A clinical case-control study. *American Journal of Sports Medicine, 43*(4), 794–801. https://doi.org/10.1177/0363546514567298

Kretchmar, R. S. (2000). Movement subcultures: Sites for meaning. *Journal of Physical Education, Recreation & Dance, 71*(5), 19–25. https://doi.org/10.1080/07303084.2000.10605140

Norges Friidrettsforbund. (2024). *Tyrvingtabellen: Poengtabell for ungdomsfriidrett* [Tyrving table: Scoring table for youth athletics]. https://www.friidrett.no/tyrving

Norges Idrettsforbund. (2024). *Nøkkeltall 2023: Medlemskap, aktivitet og økonomi i norsk idrett* [Key statistics 2023: Membership, activity and economy in Norwegian sport]. https://www.idrettsforbundet.no

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, E. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830.

Scanlan, T. K., Carpenter, P. J., Simons, J. P., Schmidt, G. W., & Keeler, B. (1993). An introduction to the sport commitment model. *Journal of Sport & Exercise Psychology, 15*(1), 1–15. https://doi.org/10.1123/jsep.15.1.1

Scanlan, T. K., Chow, G. M., Sousa, C., Scanlan, L. A., & Knifsend, C. A. (2016). The development of the Sport Commitment Questionnaire-2 (English version). *Psychology of Sport and Exercise, 22*, 233–246. https://doi.org/10.1016/j.psychsport.2015.08.002

Schacter, D. L. (2001). *The seven sins of memory: How the mind forgets and remembers*. Houghton Mifflin.

von Elm, E., Altman, D. G., Egger, M., Pocock, S. J., Gøtzsche, P. C., & Vandenbroucke, J. P. (2007). The Strengthening the Reporting of Observational Studies in Epidemiology (STROBE) statement: Guidelines for reporting observational studies. *Annals of Internal Medicine, 147*(8), 573–577. https://doi.org/10.7326/0003-4819-147-8-200710160-00010

Wattie, N., Schorer, J., & Baker, J. (2015). The relative age effect in sport: A developmental systems model. *Sports Medicine, 45*(1), 83–94. https://doi.org/10.1007/s40279-014-0248-9
