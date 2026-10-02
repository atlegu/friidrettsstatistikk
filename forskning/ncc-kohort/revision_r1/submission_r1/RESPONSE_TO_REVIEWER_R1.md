# Response to the Editor and Reviewer

**Manuscript SPO-26-1604.R1** — "Pulling back before dropping out: Declining competition participation precedes exit from Norwegian youth track and field — a 14-year register study"

Dear Dr Jenkins,

Thank you for the opportunity to revise the manuscript, and thank you to Dr Hamri for a careful and constructive review. All fifteen comments have been addressed; the point-by-point responses follow. Changes are shown in blue text in the highlighted manuscript and supplement, and all section, table and figure numbers below refer to the revised version.

## Summary of the main changes

1. **Strictly baseline-only specialization index (Comment 1).** The reviewer was right that the index used in the primary model included information after age 14. It is now computed from ages 13–14 only, and every model containing it has been re-estimated.
2. **Corrected performance scoring (prompted by Comment 4).** Tracing the 20% missingness in Tyrving scores, we found that our scoring routine had not matched specification-coded events (throws with age-specific implements, hurdles at youth heights, take-off-zone jumps, race walking) to the Tyrving table, and that it applied the wrong formula to middle-distance races, throws and pole vault. With corrected scoring, 99.1% of baseline results are scored, Tyrving is missing for 2 athletes (0.1%) instead of 419 (19.7%), and the primary sample increases from 1,704 to 2,136.
3. **Audit of the data pipeline.** Because these errors had passed unnoticed, we audited the pipeline from register extraction to analysis file and corrected the further errors it found (Supplementary Methods S-M12).
4. **Cross-validation as requested (Comments 2, 3, 10):** standardization within training folds, club-grouped folds, 20 repeats with confidence intervals, and paired comparisons of discrimination on identical folds.
5. **New analyses:** a formal within-athlete fixed-effects model of decline before exit (Table S28, Figure S5); thresholds derived in one birth cohort and validated in the other (Table S29); temporary gaps and alternative event definitions (Table S30); the cohort compared with the register population (Table S31); alternative birth-quarter codings (Table S13, Panel B); predictive performance under multiple imputation (Table S21).
6. **Terminology:** "behavioral disengagement" is replaced by "declining competition participation" or "behavioral marker of disengagement" (including the subtitle and running title); "explains more variance" by discrimination wording; and "replication" by "internal cohort replication".

**Effect on the findings.** The central results hold. Pre-milestone competition volume has OR = 2.04 per SD (95% CI 1.80–2.32; submitted 2.40) and cross-validated AUC = 0.767 (0.737–0.797; submitted 0.751), unchanged with club-grouped folds, and it is reproduced in both birth cohorts. The within-athlete decline before exit is unchanged. Two conclusions have changed, and we have revised the text accordingly:

- **Performance matters more than we reported.** With correct scoring, baseline Tyrving has a substantial independent association with retention (OR 1.75 [1.47, 2.08]; submitted 1.12, not significant). Volume still discriminates somewhat better than performance measured in the same window (AUC difference 0.040 [0.006, 0.074]), but the two are complementary, and with its within-baseline trajectory performance matches volume. Section 4.2 and the Abstract now say this, and Hypothesis 2 is described as partially supported.
- **Specialization.** The HHI association is small (OR 1.18 [1.04, 1.34]; submitted 1.36), present only once volume is in the model and only in Cohort B, adds no discrimination, and is no longer significant once performance in the athlete's main event is controlled. The Abstract now says only that event concentration was not robustly associated with retention.

**Other corrections.** All tables and figures are now generated directly from the analysis code. In doing so, and in the audit, we found and corrected several data-handling errors (an incomplete extraction, the identification of the baseline meet, results after the end of follow-up, register corrections of sex, the coding of region and club, and double-counted meet records), errors in two secondary Cox analyses and in the calibration figure, and some errors of transcription and presentation (Tables 5, S2 and S4, the Figure 3 caption and the Kaplan–Meier summary in Section 3.2, the title inside Figure 2, one unconverted citation, a box in Figure 1, the Table 1 note, and rounding in a few supplementary table cells). The data and analysis corrections are listed in Supplementary Methods S-M12. Apart from the changes in the role of performance and specialization described above, none alters the conclusions.

**Length.** We have kept the main text close to its submitted length (about 6,200 words, against 6,036 at submission) by placing most new detail in the Supplementary Methods (S-M3, S-M4, S-M6, S-M9 to S-M12) and new Supplementary Tables S26–S32, and by shortening the Introduction and Discussion.

---

## Response to Reviewer 1 (Dr Imad Hamri)

### Methods

**Comment 1.** *Please clarify exactly how hhi_early is calculated. In the Methods it is defined using the first three active seasons, but the main model is described as using only data from ages 13–14. If hhi_early includes information after age 14, then the primary model is not fully baseline-only.*

**Response.** Thank you; the reviewer is correct, and this was an error rather than a design choice. The submitted index pooled every result up to the end of the second calendar year after the baseline meet, so depending on baseline age it covered ages 11–16 (about 35,000 of its results came from ages 15–16). The primary model was therefore not strictly baseline-only. The index is now computed from results in the age-13 and age-14 calendar years only, the same window as the volume predictor, and every model containing HHI has been re-estimated.

On the submitted data, the correction changes the volume estimate little (OR 2.40 → 2.33) and reduces the HHI association (1.36 → 1.24). In the final revised model, HHI has OR 1.18 [1.04, 1.34]. This association is clear in Cohort B (1.32) but not in Cohort A (1.07 [0.90, 1.28]), and adding HHI does not improve discrimination (ΔAUC −0.002 [−0.005, 0.001]). With performance now correctly scored, it is also no longer significant once performance in the athlete's main event category is controlled (1.07 [0.94, 1.23]; Table S18). The Abstract therefore now states only that event concentration was not robustly associated with retention, and Sections 3.9, 4.1, 4.6 and 4.8 are revised accordingly.

*Changes:* Abstract; Section 2.4.3; Supplementary Methods S-M8; all HHI-containing tables (Tables 3, 5, 7, S1–S2, S5–S11, S13, S16–S18, S20–S22, S25); Sections 3.3, 3.9, 4.1, 4.6, 4.8.

**Comment 2.** *Continuous variables were standardized before cross-validation. The standardization should be done inside each training fold and then applied to the validation fold. Please rerun the cross-validation this way and check whether AUC, calibration and Brier score change.*

**Response.** Agreed. Standardization is now refitted within each training fold and applied to the held-out fold (a pipeline; Section 2.5.1, Supplementary Methods S-M4). As expected for an unpenalized logistic regression, the results did not change. Standardizing on the full data uses no outcome information and is an affine re-parameterization, which leaves out-of-fold predictions unchanged. Re-running the submitted analysis with in-fold standardization reproduced its AUC (0.751), calibration slope (0.96) and Brier score (0.122) to the third decimal (Table S26, rows 1–2).

The primary and all new cross-validations use in-fold standardization and 20 repeats of stratified 5-fold cross-validation (Tables S9, S17 and S24, re-runs of the original scripts, keep the single split and say so). For the revised primary model, CV-AUC = 0.767 (95% CI 0.737–0.797), with calibration slope 0.98, calibration-in-the-large 0.00 and Brier score 0.117 (Table 3; Table S23; Figure S1).

*Changes:* Sections 2.5.1 and 3.3; Supplementary Methods S-M4; Tables 3, S23, S26; Figure S1.

**Comment 3.** *There is a clear club structure in the data, with an ICC of 0.25 for competition volume. However, the cross-validation seems to be done at athlete level. A grouped cross-validation by club would be useful to check whether predictive performance remains similar.*

**Response.** Thank you; this is a useful check. We repeated the cross-validation with stratified group folds by baseline club: all 287 clubs are kept entirely in either the training or the validation fold, over 20 repeats. Discrimination and calibration were unchanged:

- club-grouped folds: CV-AUC 0.766 (0.735–0.797), slope 0.97, Brier 0.117;
- athlete-level folds: 0.767 (0.737–0.797), 0.98, 0.117.

Together with the club random-intercept model (volume OR 2.10) and club-clustered standard errors (2.04 [1.75, 2.39]), this shows that the association holds within clubs and carries over to clubs not used for fitting. (The ICC of volume is 0.27 in the corrected data.)

*Changes:* Abstract; Sections 2.5.1, 2.5.5, 3.4, 4.1 and 4.7; Supplementary Methods S-M4 and S-M7; Tables S22 and S26.

**Comment 4.** *Missing data are not negligible, especially for Tyrving. Please give more details on the multiple imputation procedure: which variables were included, whether the outcome was included, and how the variables were imputed. It would also be useful to know whether the predictive performance remains similar after imputation, not only the ORs.*

**Response.** Thank you. Following up this comment led us to the source of the missingness. Our scoring routine matched only generic event codes to the Tyrving table, whereas the register codes throws, hurdles, take-off-zone jumps and race walking with their implement or hurdle specification (e.g., "shot put 3 kg", "60 m hurdles 76.2 cm"). These events were therefore never scored, and athletes who competed only in them at the baseline meet had no score. The missingness was structural, driven by event choice rather than performance level. Checked against the federation's scoring workbook, the routine also used wrong formulas for races of 600 m and longer, race walking, throws and pole vault.

We corrected the scoring so that every result is scored against the table row for its event, specification, sex and age, with the workbook's formulas (Section 2.4.2; Supplementary Methods S-M3).

- 99.1% of baseline results are now scored (previously 50.5%);
- baseline Tyrving is missing for 2 athletes (0.1%), both without registered sex, instead of 419 (19.7%);
- the primary complete-case sample increases from 1,704 to 2,136.

The corrected scores are on average higher (mean 824 vs. 666), because each athlete's best event is now included. Baseline performance now has a substantial independent association with retention (OR 1.75 [1.47, 2.08]); we discuss the consequences under Comments 9 and 10.

As requested, Supplementary Methods S-M3 now details the imputation:

- **Method:** chained equations with Bayesian ridge conditional models, draws from the posterior predictive distribution, 15 iterations, and m = 20.
- **Imputation model:** the outcome, sex, Tyrving, HHI and volume; a sensitivity analysis adds baseline event category, region, cohort, club size and result count.
- **Sex** is never imputed, and estimates are pooled with Rubin's rules.

Because no sex-known athlete now lacks a score, imputation and complete-case results coincide. To answer the question where it matters, Table S21 also repeats the analysis on the submitted analysis file (Tyrving missing for 18.8% of sex-known athletes):

- pooled estimates were essentially unchanged (volume OR 2.34 [2.07, 2.66] vs. 2.40 complete-case);
- predictive performance was the same as complete-case (CV-AUC 0.751, range 0.745–0.755 across imputations, vs. 0.753; both over 20 cross-validation splits). Here the imputation model was fitted inside each training fold without the outcome, so no outcome information reached the validation fold.

*Changes:* Sections 2.4.2 and 2.5.5; Supplementary Methods S-M3 and S-M12; Tables 1, S12, S21, S25; all tables containing Tyrving.

**Comment 5.** *Please clarify how the 24 athletes with unknown sex were handled in the regression models.*

**Response.** They are excluded from all regression models (complete-case on sex), apart from a mean-imputation check of the post-baseline Cox model (Table S5) that keeps every athlete, and are included only in cohort totals and unstratified Kaplan–Meier curves; they cannot receive Tyrving scores, because the norms are sex-specific (Section 2.4.5; Supplementary Methods S-M3). Since our extraction, a register-wide correction of sex coding has resolved 22 of the 24, and the revised analyses use the corrected values (where these athletes' sex-specific implements indicate a sex, 24 athletes, they agree with the corrected values), so only 2 athletes remain without registered sex. In the submitted data, a sensitivity model retaining the 24 as a separate category gave the same volume OR as excluding them (2.37 vs. 2.36).

*Changes:* Section 2.4.5; Supplementary Methods S-M3 and S-M12; Tables 1, S5, S12, S25; Figure S0.

**Comment 6.** *Please explain the coding of birth quarter. Why are Q1 and Q4 specifically mentioned in the structural controls?*

**Response.** Birth quarter is defined from the birth month within the calendar-year age group: Q1 = January–March (the relatively oldest) to Q4 = October–December (the relatively youngest) (Section 2.4.5). The structural model used Q1 and Q4 indicators against Q2–Q3, because relative-age research predicts the largest differences at the extremes (Section 2.5.2). In re-analysis we found that the 90 athletes registered with birth year but no birth date (none of whom retained) had been coded into the reference group; this is now stated. Table S13, Panel B, adds three alternative codings:

- Q1/Q4 indicators among athletes with known quarter;
- full coding (Q2, Q3, Q4 vs. Q1);
- a linear trend.

With performance correctly scored, a modest pattern emerged: conditional on performance and volume, relatively younger athletes were retained somewhat more often (linear trend OR 1.16 per quarter [1.03, 1.31]; full coding, likelihood-ratio χ²(3) = 7.45, p = .06). The volume OR was unchanged under every coding (2.01–2.07), and Section 3.4 now reports the pattern.

*Changes:* Sections 2.4.5, 2.5.2 and 3.4; Table S13 (Panel B).

### Results

**Comment 7.** *The direction of the change-score ORs is not easy to understand… Please give the exact formula used for the change variable and make the interpretation of the OR consistent with its direction. The same applies to the age 15–16 change.*

**Response.** Thank you; the formula was not stated. Change is the later minus the earlier volume (volume at 15 − volume at 14; positive = increase), so the reported OR (2.44 in the submission, 2.29 in the revision) is per SD of increase. Conditional on the level at 14, this is equivalent to:

- OR = 0.44 [0.38, 0.50] for a one-SD (about 6.4 meets) greater decline;
- OR = 0.52 for 5 fewer meets.

The text now states the formula and reports both directions (Sections 2.5.3 and 3.5; Table 4 note). The same applies to the 15→16 change: OR 1.87 per SD increase equals 0.54 [0.46, 0.63] per SD decline (Table S19). Because the model is linear in the logit, it is a re-parameterization of a model with the two levels; the per-meet OR for change equals that for the later level (Table 4 note).

*Changes:* Abstract; Sections 2.5.3 and 3.5; Table 4 and note; Tables S14 and S19; Supplementary Methods S-M6.

**Comment 8.** *The within-athlete pull-back result is interesting, but the conclusion may be slightly too strong… I would either moderate the wording around "genuine within-athlete pull-back" or add a formal longitudinal analysis of competition volume before exit.*

**Response.** We did both.

**Formal longitudinal analysis.** We added an athlete fixed-effects model of log(1 + meets) at ages 13–19, with age fixed effects and indicators for each athlete's final active season and the three preceding seasons (Section 2.5.3; Supplementary Methods S-M6; Table S28; Figure S5). Each athlete serves as their own control, so the estimates measure change relative to the athlete's own earlier volume, net of the common age profile. Volume was below each athlete's own earlier level by:

- 7% (95% CI 0–13%) three seasons before the final active season;
- 12% (5–19%) two seasons before;
- 23% (16–31%) one season before.

The decline steepened towards exit (T−1 vs. T−3, p < .001) and was confirmed on the linear scale. It was also reproduced among exits at ages 17–19, for whom earlier reference seasons are observed (T−1: −26%; T−3: −4%, not significant).

**Moderated wording.** "Genuine within-athlete pull-back" is replaced by "within-athlete decline in competition participation". The typical exit is now described as "preceded by declining participation" over one or two seasons, rather than as a "two-to-three-season taper". We also state that the register establishes the timing of the decline, not its reasons (Sections 3.5, 4.1, 4.3, 4.4 and 4.11).

*Changes:* Abstract; Sections 2.5.3, 3.5, 4.1, 4.3, 4.4, 4.9, 4.11; Supplementary Methods S-M6; Tables S12 and S28; Figure S5.

**Comment 9.** *The manuscript says that behavior "explains more variance" than performance, but the main comparison is based on AUC… I suggest using wording such as "competition volume showed better discrimination of later retention than Tyrving performance."*

**Response.** Agreed. The text, the Abstract and Hypothesis 2 (Section 1.3) now refer to discrimination; the only variance-type quantity left is McFadden's pseudo-R² for the level-and-change models (Section 3.5, Table 4, Table S14), labelled as such. With performance correctly scored (Comment 4), the comparison has also changed in substance. Volume still discriminates somewhat better than performance measured in the same window, but the two carry complementary information, and with its within-baseline trajectory performance matches volume (Comment 10). Section 4.2 is therefore retitled "Competition volume and performance carry complementary information", and Hypothesis 2 is described as partially supported: behavior discriminates at least as well as performance, not instead of it.

*Changes:* Abstract; Sections 1.3, 3.6, 4.1, 4.2.

**Comment 10.** *The AUC comparisons should be interpreted carefully. Small differences such as 0.740 versus 0.737 should not be discussed as meaningful without uncertainty around the difference.*

**Response.** We now report a 95% CI for the CV-AUC of every model in Table 3 and for every difference between models. Differences between models are estimated on identical folds, with CIs and p-values from the corrected resampled t-statistic for repeated cross-validation (Nadeau & Bengio, 2003; Supplementary Methods S-M4; Table S27).

- **The reviewer's example (adding Tyrving to volume)** now shows a small but clear gain once performance is scored correctly: +0.023 (0.007 to 0.038).
- **Volume versus Tyrving measured in the same window:** +0.040 (0.006 to 0.074), a modest advantage for volume.
- **Adding volume to sex + Tyrving + HHI:** +0.069 (0.047 to 0.091).
- **Performance with its within-baseline trajectory** matches volume: −0.001 (−0.042 to 0.039).
- **A within-event rank at the baseline meet**, which removes Tyrving's unequal demands across event groups, discriminates no better than Tyrving (0.689 vs. 0.700; difference 0.011 [−0.006, 0.028]); volume again discriminates better (+0.051 [0.019, 0.083]).

The text now interprets only differences whose intervals exclude zero, and describes performance and volume as complementary.

*Changes:* Sections 2.5.1, 3.3, 3.6, 4.2; Tables 3, S15, S27.

**Comment 11.** *The <10 meets threshold is interesting, but it seems to be developed and evaluated in the same dataset. I would present it as a candidate threshold, not as a validated rule. If possible, one cohort could be used to define the threshold and the second cohort to test it.*

**Response.** Agreed on both points. The threshold is now presented throughout as a candidate rule (Sections 3.8, 4.8 and 4.9; Table 6 note), and, as suggested, we derived thresholds in one birth cohort and evaluated them in the other (Table S29; Supplementary Methods S-M9).

- **Capacity rule** (fixed before the cohorts were compared: flag the lowest volume quartile). Derived in either cohort, the cut-off is exactly < 10 meets. Applied unchanged to Cohort B, it flagged 26.1% of athletes, whose senior retention was 4.6%, against 21.4% among the unflagged (PPV 0.95, sensitivity 0.30). Applied to Cohort A, it gave 6.0% against 19.7%.
- **Youden-optimal cut-offs** also transferred, but select much broader screens (< 21 and < 29 meets, flagging 56–77% of athletes).

Because both cohorts come from the same register, we describe this as temporal validation within one setting and state that the thresholds have not been externally validated (Section 4.9; Supplementary Methods S-M9).

*Changes:* Abstract; Sections 2.5.3, 3.8, 4.8, 4.9; Table 6 note; Table S29; Supplementary Methods S-M9.

### Interpretation

**Comment 12.** *I would be more careful with the term "behavioral disengagement". The register measures competition participation, not motivation or disengagement directly… I suggest using "declining competition participation" or "behavioral marker of disengagement" when possible.*

**Response.** We agree and have changed the terminology throughout.

- **Title:** the subtitle now reads "Declining competition participation precedes exit", and the running title "Declining participation precedes exit from youth track and field".
- **Text:** "declining competition participation" is used for the observed behavior, and "behavioral marker of disengagement" where the theoretical construct is meant.
- **Alternative causes:** we state explicitly that a decline can also reflect injury, a move to another sport, or school and other time constraints (Sections 2.4.4 and 4.2; Figure 1 and its caption).

*Changes:* Title; running title; Abstract; Sections 1.3, 2.4.4, 3.5, 4.2, 4.3; Figure 1 and its caption.

**Comment 13.** *Please clarify the target population. The cohort includes athletes who participated in a specific regional youth competition and were entered by district federations. This is not the full population of Norwegian youth track and field athletes, so the generalizability of the results should be discussed more clearly.*

**Response.** We now define the target population explicitly (Section 2.2) and describe how it relates to the register population (Section 3.1; Table S31; Supplementary Methods S-M11). Among the 7,266 register athletes born 1998–2002 with at least one result at ages 13–14:

- the cohort comprises 29% of all athletes;
- but 80% of those with ten or more meets at those ages, and 80% of all who later competed as seniors;
- the other 5,128 had a median of 2 meets at 13–14 and 1.7% senior retention.

The cohort is thus the engaged core of the age group, not all youth athletes. Among athletes outside the cohort, volume was also associated with retention (OR 2.17 per 10 meets), but the thresholds and absolute rates apply to the engaged core. This is now the third limitation (Section 4.9).

*Changes:* Sections 2.2, 3.1, 4.9; Table S31; Supplementary Methods S-M11.

**Comment 14.** *For the Cox analysis, please clarify how temporary gaps and later returns to competition were handled. The outcome is based on the last active season, which is different from a standard first-event survival outcome.*

**Response.** The outcome is the final active season observed through 2025 (≥2 results in a calendar year). A gap followed by a return is therefore part of a continuing career, not an event. Athletes active in 2024–2025 are censored, because their final season cannot yet be distinguished from a gap (Sections 2.4.1 and 2.5.4; Supplementary Methods S-M10). Temporary gaps were uncommon:

- 11.8% of athletes had an inactive season followed by a return;
- 4.4% had a gap of two or more seasons followed by a return;
- of athletes who missed two consecutive seasons (before 2020), 4.4% ever returned.

Re-estimating the baseline-only Cox model with definitions that do not use later returns gave the same result. With the clock starting at the end of the age-14 season, the volume HR per SD was 0.65 for the final active season, 0.62 for the first two-season gap, and 0.62 for the first inactive season (Table S30).

*Changes:* Sections 2.4.1, 2.5.4, 3.10; Table S30; Supplementary Methods S-M1 and S-M10.

**Comment 15.** *I would use "internal cohort replication" rather than simply "replication", because both cohorts come from the same register and the same national system.*

**Response.** Agreed. We now use "internal cohort replication" (or "reproduced in both birth cohorts") throughout, and state that both cohorts come from the same register and national system.

*Changes:* Abstract; Sections 1.3, 2.2, 2.5.5, 3.10, 4.1, 4.7, 4.11; Table 7 title and note.

---

## Summary of changes

| Item | Count |
|---|---|
| Reviewer comments addressed | 15 of 15 |
| Main-text word count | 6,036 → about 6,200 |
| New main-text references | 0 (reference list unchanged, 37 items) |
| New supplementary references | 2 (Nadeau & Bengio, 2003; van Buuren & Groothuis-Oudshoorn, 2011) |
| New supplementary tables | 7 (S26–S32) and a new Panel B in Table S13 |
| New or replaced supplementary figures | 1 new (S5); S1 replaced |
| Revised main tables | Tables 1–7 |
| Data audit | Supplementary Methods S-M12 |

We believe these revisions have substantially strengthened the manuscript, and we thank you and the reviewer again for your time.

Sincerely,

Atle Guttormsen
School of Economics and Business, Norwegian University of Life Sciences (NMBU)
