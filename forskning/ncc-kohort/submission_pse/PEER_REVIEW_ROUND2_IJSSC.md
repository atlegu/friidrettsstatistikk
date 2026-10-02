# Verification Review Report — Round 2 (Re-Review)

**Manuscript:** Pulling back before dropping out: Behavioral disengagement precedes exit from Norwegian youth track and field — a 14-year register study
**Round:** 2 (verification re-review of the Round-1 Major Revision; protocol: academic-paper-reviewer `re-review` mode — EIC traceability check of every roadmap item + new-issue detection, then editorial synthesis)
**Date:** 2026-08-25
**Inputs:** Round-1 package (PEER_REVIEW_SIMULATION_IJSSC.md), response letter (RESPONSE_TO_PANEL.md), revised manuscript builds, supplementary methods, source-verification audit (REFERENCE_VERIFICATION.md), analysis outputs (revision_results.json) and table CSVs.

---

## Decision

### At audit: **Minor Revision** → After same-day fix pass (addendum below): **all Round-1 acceptance criteria met**

Eleven of sixteen required revisions were verified FULLY_ADDRESSED at audit; five were PARTIALLY_ADDRESSED (M2, M3, M4, M9, M16), none NOT_ADDRESSED or MADE_WORSE, and the Round-1 Devil's-Advocate CRITICAL is confirmed neutralized by the exit-aligned evidence. The new-issue scan found no substantive faults — every headline number reconciles with the authoritative pipeline output and the Vancouver conversion is clean — but caught two Major mechanical defects (Tables 5/7 again missing from the compiled builds because the placeholders were never added, contradicting the response letter; a corrupted Table 1 row) and ten smaller seams. All findings were fixed and re-verified the same day (addendum).

---

## Part A — Traceability Report (verbatim, EIC verification pass)

**Verification basis:** RESPONSE_TO_PANEL.md claims checked against MANUSCRIPT_FULL.md, 11_tables.md, 15_supplementary_methods.md, 12_figure_captions.md, REFERENCE_VERIFICATION.md, the compiled builds (MANUSCRIPT_IJSSC/ANONYMIZED), `data/revision_results.json`, and the CSVs in `submission_pse/tables/`. All spot-checked statistics were independently recomputed or matched to pipeline output; Table 6 row arithmetic was re-derived by hand for all four thresholds.

### Priority 1 — Required Revisions (M1–M16)

| # | Original requirement (short) | Author's claim (short) | Response Status | Revision Location | Verified? | Quality assessment |
|---|---|---|---|---|---|---|
| M1 | Exit-aligned pull-back analysis; title/abstract/§4.4 contingent on result (DA CRITICAL) | Done; title stands on new direct evidence | **FULLY_ADDRESSED** | §2.5.3, §3.5, §4.3–4.4, Abstract, Table S19, S-M6 | ✅ Yes | Every number verified against JSON (1,139; 12→10→9→4; 95.2%; 74.2/6.5/19.2%; n=1,075; OR 3.04/1.88; AUC 0.758); acceptance criterion met |
| M2 | Single-pipeline regeneration; trace S3/S9; complete package (Tables 5/7, figures, STROBE) | Done; Tables 5/7 "restored", build artifact "fixed" | **PARTIALLY_ADDRESSED** | All results; Tables S3/S9/S12; Table 6 | ⚠️ Partial | Numeric harmonization and S3/S9 recomputation fully verified; the Tables-5/7 "restored" claim is **contradicted by the files**; STROBE outstanding |
| M3 | Governance preconditions; ethics-scope sentence; anti-triage warning | Done | **PARTIALLY_ADDRESSED** | §4.8 governance para, §2.7, §4.11 | ⚠️ Partial | All named preconditions present and well-drafted except the explicitly required warning against triage use |
| M4 | Prediction→intervention reframe; Battaglia engaged substantively; pilot promoted | Done | **PARTIALLY_ADDRESSED** | §4.8–4.11, §4.4 | ⚠️ Partial | Reframe, offer-not-pressure, barrier reconciliation, pilot, applied limitations all verified; Battaglia remains cited only in §1 terminology |
| M5 | Honest screen arithmetic on all practitioner surfaces | Done | **FULLY_ADDRESSED** | Abstract, Table 6, §3.8, §4.8(1) | ✅ Yes | Base rate 84%, sensitivity 0.30, 5.7% vs 20.2% contrast, NPV interpreted, false-reassurance and targeted-vs-universal sentences all present; matches CSV/JSON |
| M6 | E-value on the primary estimate; retire milestone 5.16 | Done (E=2.5, CI 2.2; Cox 2.6) | **FULLY_ADDRESSED** | §3.10, §4.7, Table S3, S-M5, S-M1 | ✅ Yes | Arithmetic independently recomputed and correct; inadmissibility note on the old spec in three places |
| M7 | MI; incl/excl comparison; sample-flow table; Table 4 n; sex-unknown | Done | **FULLY_ADDRESSED** | §2.5.5, S-M3, Tables S12/S21/S25, Table 4 header | ✅ Yes | MI OR, 16.5% vs 16.0%, 1,914→1,549 with mechanism, sex-unknown rule, fixed-L4-sample statement — all verified to JSON |
| M8 | HHI count-dependence stress tests; descriptive retitle | Done — finding survives | **FULLY_ADDRESSED** | §3.9, §4.6, Table S20, S-M8 | ✅ Yes | ρ=−.38/−.21; restricted ORs 1.38/1.39; corrected-index 1.39 [1.20, 1.60] all match; heading descriptive; sign flip discussed |
| M9 | TRIPOD reporting: calibration, Table 6 CIs, RF report-or-delete, declared variables | Done | **PARTIALLY_ADDRESSED** | §2.5.1/2.5.3, §3.3, §3.6, Tables 6/S23, S-M4 | ⚠️ Partial | Calibration and Table 6 verified; RF fully excised; Δ13–14 added — but `tyrving_slope_13_16` still declared in §2.4.2 and reported nowhere |
| M10 | Citation repair + full audit | Done; audit delivered | **FULLY_ADDRESSED** | §1, §1.1, §4.6; REFERENCE_VERIFICATION.md | ✅ Yes | Audit exceeds the claim: page-anchored verification of every substantive attribution, 8 further corrections; Larson verbatim-verified; Espedalen pinpointed |
| M11 | Nearest-neighbor literatures; sharpened novelty claim | Done | **FULLY_ADDRESSED** | §1.2, §4.4, S-M2 | ✅ Yes | Gap reformulated exactly as R2 specified |
| M12 | Injury as rival explanation | Done | **FULLY_ADDRESSED** | §4.2, §4.9 | ✅ Yes | Named co-equal alternative with Enoksen's 24.3% (audit-verified) |
| M13 | Regs citation; regional-team caveat; venue coverage; club ICC + random intercepts | Done | **FULLY_ADDRESSED** | §2.2, §3.4, §4.9, Table S22, S-M7 | ✅ Yes | ICC 0.25 (277 clubs), RE OR 2.58 [2.27, 2.93] match JSON; effect larger within clubs |
| M14 | Scope discipline | Done | **FULLY_ADDRESSED** | Title page, Abstract, §1.3, §4.4, §4.9 | ✅ Yes | "Independent cohorts"/"formal exit" gone; reallocation co-equal; transfer conditions explicit |
| M15 | Sex-effect reconciliation | Done | **FULLY_ADDRESSED** | §4.5 | ✅ Yes | KM null and Table 3 ORs presented together; masking mechanism coherent; Enoksen connection added |
| M16 | Hygiene bundle | Done (line-item list) | **PARTIALLY_ADDRESSED** | Throughout | ⚠️ Partial | 16 of 17 micro-fixes verified; seeds and package versions absent and unclaimed |

**M1 acceptance decision:** The title's process claim is retained, and the new evidence justifies it. Aligned to each dropout's own final season, the median taper is 12→10→9→4 meets, 95% still competed in the penultimate season, only 19% fit the abrupt profile (74% reduced-but-nonzero), and the fully contamination-free model (all athletes active at 16) shows within-athlete decline predicting senior status (OR 1.88 [1.60, 2.20]) independent of level (3.04). This is individual-level pull-back, not an averaging artifact. Minor blemish: the abstract's "74%" silently inherited the final-age-≥16 restriction (fixed in the addendum).

**M2 details:** The numeric core is impeccable — OR 2.40 [2.08, 2.76] and HHI 1.36 [1.17, 1.57] appear identically everywhere; S9 regenerated on the primary specification (2.29/2.40/2.26); S3 regenerated with the admissibility note; Table 6 recomputed on n = 2,123 with bootstrap CIs, all rows mutually consistent (re-derived by hand). But the package-completeness half failed at audit: the `[Table 5/7 about here]` placeholders were never added to 05_results.md, so Tables 5 and 7 were again absent from all three compiled builds — the verbatim Round-1 defect, and the response letter's "restored… fixed" claim was false as of that build. STROBE checklist did not exist. Supplementary figure PNGs and pipeline CSVs were misnumbered against their captions/S-numbers.

**M3/M4/M9/M16 details:** anti-triage warning missing (M3); Battaglia engaged in substance but not by citation in §4.4 (M4); `tyrving_slope_13_16` declared-but-unreported (M9); seeds/versions absent (M16). All one-to-two-sentence fixes.

### Priority 2 — Suggested Revisions (S1–S12)

12/12 have a response on record: S1, S3, S4, S5, S8, S10, S11 DONE (verified); S12 largely done; S2, S9 partial with explanations on record; S6, S7 not done with author explanations on record. Threshold (≥80% response) met.

### Author Questions (Q1–Q8)

Q1–Q5, Q7 answered adequately (verified); Q6 partial (injury share not estimable from the register — residual limitation; the tyrving_slope sub-question resolved in the addendum by deleting the declaration); Q8 unanswered at audit (resolved in the addendum: 0% of flagged athletes have zero meets — cohort entry guarantees ≥1 baseline meet, so the entire flag list is reachable; against an activity-at-17 outcome the <10 threshold gives 14.4% vs 50.9% still active, PPV 0.86, sensitivity 0.38).

### Traceability verdict (verbatim)

Eleven of sixteen required revisions fully addressed, five partially; none unaddressed or made worse; no Cannot-verify items — every spot-checked statistic reproduced exactly from `revision_results.json` and the regenerated tables, the single strongest change from Round 1, where the pipeline leaked stale estimates. The Round-1 DA CRITICAL is neutralized. What blocked a clean sign-off: the response letter's Tables-5/7 claim contradicted by the files, the missing STROBE checklist, the anti-triage sentence, a cited Battaglia engagement, the tyrving_slope declaration, seeds/versions, and the misnumbered supplementary files — all sub-day text-and-build fixes requiring no new analysis.

---

## Part B — New-Issue Scan (summary of the 12 findings)

| # | Severity | Finding | Status after fix pass |
|---|---|---|---|
| 1 | Major | Tables 5/7 cited but placeholders never added → absent from all compiled builds | **Fixed** — placeholders added in §3.7/§3.10; grep-verified embedded in MANUSCRIPT_FULL |
| 2 | Major | Table 1 last row relabeled away from source ("Median competitions 13–14: 8/9/8" vs CSV "15–16: 7/9/8"); invited false contradiction with Table 6 | **Fixed** — row recomputed from data as the headline predictor: "Median total meets, ages 13–14 (pre-milestone volume): 16 / 19 / 17" |
| 3 | Minor | Stale S8 pointer: Methods/S-M1 attached S8 to the post-baseline spec; new S8 is the landmark | **Fixed** — S8 moved onto the landmark item in §2.5.4 and S-M1 |
| 4 | Minor | §3.6 mixed two analysis runs; Δ13–14 row absent from Table S15 | **Fixed** — trajectory row added to S15 with n = 1,350 and a subsample note |
| 5 | Minor | MI sample: manuscript said n = 2,099 but the script had imputed sex and run on 2,123 | **Fixed** — script corrected (sex-unknown excluded before imputation, sex never imputed), rerun: OR 2.34 [2.07, 2.66], n = 2,099; S21, §3.10, S-M3 updated |
| 6 | Minor | Table S7 (.md) did not match its deposited CSV (male Tyrving significance flipped) | **Fixed** — S7 rebuilt from the CSV (male Tyrving 1.13, p < .001; volume 0.43/0.45); §4.5 updated |
| 7 | Minor | Orphaned supplementary items (S1, S4, S6, S10, S14 stub, S17, Figs S1/S4); stale RF figure file; captions off-by-one vs PNG filenames | **Fixed** — citations added (§2.5.5, §3.7, S-M1); S14 filled with real content; Fig S1 caption updated; PNGs renamed S2–S4, RF figure retired; CSV filenames aligned to submitted S-numbers |
| 8 | Minor | Table 2 never cited in running text | **Fixed** — cited in §3.2 |
| 9 | Minor | Abstract's 74% lacked the final-age-≥16 conditioning | **Fixed** — "74% of those leaving at 16 or later" |
| 10 | Cosmetic | Rounding drift (Female OR 0.61 vs 0.6048; "6%" vs 6.5%; S13 0.59) | **Fixed** — 0.60 / 6.5% / 0.60 |
| 11 | Cosmetic | One Vancouver superscript before a comma ("(24.3%)³,") | **Fixed** — mapping updated to place after the comma |
| 12 | Cosmetic | Abstract "unchanged by … club random effects" overstated invariance | **Fixed** — "robust to" |

**Checks passed at audit (unchanged):** all headline numbers reconcile with `revision_results.json`; Vancouver list 1–37 in strict first-appearance order with all spot-checks resolving; no leftover "surveillance"/"independent cohorts"; declarations complete; abstract 244–246 words.

---

## Addendum — Fix pass executed and re-verified (same day)

All 12 scan findings and all 5 partial M-items were fixed:
- **M2 →** placeholders added (Tables 5/7 embedded in all builds), STROBE checklist created (16_strobe_checklist.md, 22 items mapped to sections), supplementary PNGs/CSVs renamed to match final numbering, response letter corrected for the record.
- **M3 →** anti-triage sentence added to the governance paragraph.
- **M4 →** Battaglia et al. (2024) now cited substantively in §4.4 (reallocation as the developmentally appropriate transitions the dropout-as-crisis framing wrongly pathologizes).
- **M9 →** `tyrving_slope_13_16` declaration deleted; the reported Δ13–14 trajectory stands as the performance-trajectory competitor (now also in Table S15).
- **M16 →** fixed-seeds and package-version statement added to §2.5.6.
- **Q8 →** answered with new computation in §4.8(1): all flagged athletes are low-but-active by construction; the threshold performs similarly against an activity-at-17 outcome.

Post-fix status: main text ≈5,850 words excluding headings (6,099 including; limit 6,000 "should not normally exceed"); 37 references; 50 superscript citations; supplementary tables S1–S25 and figures S0–S4 all cited and internally numbered consistently.

**Editorial closing:** With the fix pass verified, every Round-1 required revision meets its acceptance criterion, both previously overstated response-letter claims are corrected on the record, and the two residuals are properly logged as limitations rather than defects (injury share not estimable from the register; SIMEX measurement-error quantification declined with the caveat in place). The manuscript is, in this panel's judgment, ready for submission pending the author's own final pass (preprint-DOI question, figure dpi check, Word formatting).
