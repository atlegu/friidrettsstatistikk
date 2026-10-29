# Response to the round-1 panel — "Stagnation before exit"

All new analyses are in `06_revisjon_r1.py` (outputs `tables/modeller/r1_*.csv`). The two analyses the editor marked as required — mediation of the birth-quarter trend, and rank/level heterogeneity — were both run, and both changed the paper's conclusions in the direction of greater precision.

## Reviewer 1 (sport psychology)

**R1-1 (under-theorised, self-referential).** §4.3 now anchors the construct where it lives: mastery experience as the strongest source of self-efficacy (Bandura 1977), perceived competence in self-determination-based models, and task orientation in achievement goal theory (Nicholls 1984) — both added to the references and CrossRef-verified. The section also states what the mastery account predicts beyond generic commitment (heterogeneity by access to other reinforcement) and adds the requested salience passage: athletes most directly observe times, distances and placings, while age-graded points are printed on youth result lists and used for club awards, so the measure is an objective correlate of received signals, not perception itself.

**R1-2 (birth quarter a weak proxy; add rank-based moderation).** Done. The direct test is now reported (§3.2 heterogeneity paragraph): progression × baseline-level interaction OR 1.06 (0.94–1.19), with level-tertile strata 1.63 / 1.86 / 2.37 — present at every level, and the point gradient runs *upward* with level, opposite to the rank-deprivation prediction. "That prediction failed" has been replaced throughout (abstract, Key Points, §3.3, §4.3, Conclusions) by the precise statement: the reinforcement-deprivation form found no support in either tested form, while a mediated form remains open (see R3-1).

**R1-3 ("every level" unsupported).** Now supported by the stratified analysis above; the claim stands with its evidence attached.

**R1-4 (individual-level calibration).** Added: one progression-SD ≈ 115 age-graded points (range 77–176 across cells; level ≈ 173 points; volumes ≈ 17 days), stated in Methods; §4.5 rewritten to give the scale, the dropout-vs-retainer share with negative progression (59.5 vs 33.5 %), and an explicit statement that the −7-point median (≈0.06 SD) is inside normal individual fluctuation — "conversation-starters for coaches, not selection or flagging criteria". The "doubles the odds" sentence is reformulated accordingly, and the normative-sampling sentence (DMSP perspective; Fraser-Thomas et al.; Crane & Temple) added.

**R1-5 (sex-specific association).** Reported: progression × sex interaction OR 0.98 (0.76–1.26); strata 2.25 (women) / 1.90 (men). §4.4 now states the gap is not explained by women responding less to progress.

**Minors.** Keyword changed to "relative age"; the enjoyment–progress connective sentence added to the Background; the "observability" sentence now closes the Conclusions; the disengagement-terminology sentence added to Methods.

## Reviewer 2 (epidemiology/biostatistics)

**R2-1 (flow error; STROBE).** Correct: 43 referred to the landmark sample; within the primary sample the number is 27 (n = 3,781). Fixed, with both numbers stated, a full flow added as Supplementary Table S1 (including the H2, exit-aligned and inclusive-exposure subsamples), and the STROBE checklist noted as accompanying submission.

**R2-2 (CV percentile intervals are not CIs).** Agreed and fixed. Methods now distinguish repetition spread (Monte Carlo variability) from sampling uncertainty; paired DeLong 95 % CIs computed on the out-of-fold predictions are reported for both AUC contrasts: ΔAUC(M2−M1) = 0.009 (0.003–0.015, p = 0.003); H3 difference −0.001 (−0.010 to 0.007, p = 0.75). Tables 2 and 3 are relabelled, and the H3 conclusion now rests on the DeLong interval.

**R2-3 ("as strong as competition volume").** Fixed everywhere it occurred (abstract, Key Points, §4.1, Conclusions): the comparison is now explicitly with the companion study's baseline-volume coefficient, with the number given (2.04 per SD), and every instance adds that concurrent volume (OR 3.15) remains the dominant predictor. The reviewer's suggested "current form, not early rank" sentence has been promoted to the abstract and Conclusions.

**R2-4 (specification check weaker than claimed).** Language downgraded from "indicating" to "consistent with", with the noise/attenuation caveats stated ("supportive rather than decisive").

**R2-5 (E-value not reproducible).** The prevalence conversion is now in Methods (RR = OR/(1 − p₀ + p₀·OR), p₀ = 0.17) with the explicit statement that E-values are on the risk-ratio scale.

**R2-6 (outcome opportunity; 2026).** Methods now justify the primary definition (keeps all follow-up, maximises events), state that 2026 contributes through 29 October, and the fixed-window outcome is reported per cohort half as requested: OR 2.14 (A) and 1.99 (B).

**Minors.** The switcher row was mis-specified in round 1 — the reviewer's n-question exposed that the "switchers included" variant had been run on the primary sample only. It is now estimated on the inclusive sample (n = 4,071; 363 of the 734 recovered; 94 primary athletes not scorable under that definition drop out): OR 1.83 (1.61–2.07), with the flow stated in text and Table 4 corrected. H2's model does include the quarter main effect (now visible in Table 3, with the added mediation rows). Table 3 now carries ns. SDs reported in points/days. The quintile-dummy model confirms monotonicity (ORs 1.22/1.86/2.35/4.47 vs the lowest quintile) and is reported in §3.2. The Table-2-fallacy flag added where covariates are interpreted; Figure 2's tertile bounds stated as half-open intervals; Figure 4's time origin defined in the caption; the exit-aligned selection (1,011 of 3,160) stated in text and caption; "directional" clarified (sign prediction, two-sided test). The time-stamped plan will be deposited with the code.

## Reviewer 3 (talent development / relative age)

**R3-1 (mediation, required).** Both requested analyses were run and are reported in §3.3 and Table 3. (a) Progression rises monotonically across birth quarters: median −16.7 (Q1) to +0.3 points (Q4); +0.07 SD per quarter (95 % CI 0.04–0.10). (b) The birth-quarter retention trend in this sample — OR 1.09 (0.99–1.21), weaker than the companion cohort's 1.16 — attenuates to 1.07 (0.97–1.18) with progression controlled. §4.3 is rewritten: the mediated mastery pathway is open and directionally supported, but the imprecise trend means we present it as open rather than established; the reviewer's observational-equivalence point with maturation is stated in limitations (see R3-3).

**R3-2 (novelty too absolute).** Softened to the suggested defensible form, with "to our knowledge" moved forward: "To our knowledge, no study with complete national coverage has linked objective within-athlete performance trajectories to a prospectively defined exit outcome while adjusting for the behavioural participation signal."

**R3-3 (maturation top billing).** Done: maturation is now the third of four named processes in §4.3 with the direction-of-bias argument spelled out ("on calendar-calibrated tables a late maturer and a disengaging athlete look alike…"), the limitation paragraph states the observational equivalence of mediated-mastery and maturation readings, and both closing triads (abstract; Conclusions) now name maturation and match each other.

**R3-4 (retention vs attainment).** The participation framing is made explicit; we have not added a performance-floor outcome in this revision but flag it as a worthwhile extension — the abstract defines "active senior" precisely, and the Conclusions avoid attainment language. We are happy to add the points-floor sensitivity if the editor wishes.

**R3-5 (slide rhetoric).** All three requests implemented: the negative-Δ shares (59.5 vs 33.5 %) give the individual-level counterpart; "48" is qualified ("partly mechanical") in abstract and Key Points; the §3.5 conclusion now reads "At the group level, stagnation … is visible", and the penultimate-season magnitude is stated in SD terms (≈0.06 SD).

**Minors.** Table 1 note now gives all four quarters among those with birth dates (29.3/27.2/24.7/18.8 %); the companion volume OR (2.04) is given wherever the comparison is made; Figure 1's caption now carries per-age ns for both groups; the children's-sport-regulation sentence for gate-kept readers added to the generalisability passage; companion manuscripts will accompany the revision; "current form, not early rank" promoted as suggested.

## Editor

All four convergent points are implemented (mediation analysis added; volume claim corrected at every occurrence; flow fixed with STROBE materials; individual-level calibration added), and both directions of the discussion were expanded rather than one chosen: motivational theory anchoring (R1) and maturation as leading rival (R3) now coexist in §4.3.
