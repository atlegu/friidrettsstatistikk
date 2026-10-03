# Revision Tracking — SPO-26-1604 (IJSSC), round 1

## Paper Information

| Field | Value |
|-------|-------|
| Paper Title | Pulling back before dropping out: Declining competition participation precedes exit from Norwegian youth track and field — a 14-year register study |
| Revision Round | 1 |
| Date | 2026-10-01 (data audit and corrections 2026-10-02) |
| Previous Decision | Revise (one reviewer, Dr Imad Hamri; 15 comments) |
| Target Journal | International Journal of Sports Science & Coaching |
| Original Word Count | 6,036 (main text, journal count) |
| Revised Word Count | 6,352 (same count as 6,036 at submission; shortened from 6,889 after the audit, then +34 words of precision in the final check, 2 Oct 2026, and +134 in the final check of 3 Oct 2026: precision fixes, the author's rewording of four claims, and the final narrow review) |

## Revision Tracking Table

| # | Issue | Reviewer | Type | Section | Resolution summary | Location of change | Status | Reason (if not resolved) | Commitment Ledger |
|---|---|---|---|---|---|---|---|---|---|
| 1 | hhi_early used results after age 14 | R1 | Major | Methods | Confirmed error; HHI recomputed from ages 13–14; all models re-run; HHI claims tempered | §2.4.3, S-M8; Tables 3, 5, 7, S1–S2, S5–S11, S13, S16–S18, S20–S22, S25; §3.3, §3.9, §4.1, §4.6 | RESOLVED | | R1-1 |
| 2 | Standardization before CV | R1 | Major | Methods | In-fold standardization; shown identical for unpenalized LR; repeated CV | §2.5.1, S-M4; Tables 3, S23, S26 | RESOLVED | | R1-2 |
| 3 | Club-grouped CV | R1 | Major | Methods | StratifiedGroupKFold by club (287 clubs): AUC 0.766 vs 0.767 athlete-level; club-clustered SE and GEE added | §2.5.1, §2.5.5, §3.4, S-M4, S-M7; Tables S22, S26 | RESOLVED | | R1-3 |
| 4 | MI details + predictive performance | R1 | Major | Methods | Root cause found (Tyrving mapping gap; also wrong formulas for middle distance, throws, pole vault) and corrected (missing 19.7% → 0.1%); MI fully specified; MI predictive performance with in-fold imputation | §2.4.2, §2.5.5, S-M3, S-M12; Tables 1, S12, S21, S25 | RESOLVED | | R1-4 |
| 5 | Unknown sex handling | R1 | Minor | Methods | Stated; register's July 2026 sex correction adopted (24 unknown → 2; 8 recoded, validated by implements) | §2.4.5, S-M3, S-M12; Table S12; Figure S0 | RESOLVED | | R1-5 |
| 6 | Birth-quarter coding | R1 | Minor | Methods | Coding and rationale stated; alternative codings; modest relative-age pattern now reported (linear trend OR 1.16 per quarter) | §2.4.5, §2.5.2, §3.4; Table S13 Panel B | RESOLVED | | R1-6 |
| 7 | Change-score OR direction | R1 | Major | Results | Formula given; ORs per SD increase and per SD decline | §2.5.3, §3.5; Table 4; Tables S14, S19; S-M6 | RESOLVED | | R1-7 |
| 8 | Pull-back wording / formal analysis | R1 | Major | Results | Athlete fixed-effects model added and wording moderated | §2.5.3, §3.5, §4.1, §4.3, §4.4, §4.11; S-M6; Table S28; Figure S5 | RESOLVED | | R1-8 |
| 9 | "Explains more variance" vs AUC | R1 | Minor | Results/Discussion | Discrimination wording; with correct scoring, volume and performance described as complementary (H2 partially supported) | Abstract; §1.3, §3.6, §4.1, §4.2 | RESOLVED | | R1-9 |
| 10 | Uncertainty on AUC differences | R1 | Major | Results | CIs for every CV-AUC; paired differences with corrected t | §2.5.1, §3.3, §3.6, §4.2; S-M4; Tables 3, S15, S27 | RESOLVED | | R1-10 |
| 11 | Threshold derived and tested in same data | R1 | Major | Results | Candidate wording; derivation in one cohort, validation in the other | §2.5.3, §3.8, §4.8, §4.9; Table 6 note; Table S29; S-M9 | RESOLVED | | R1-11 |
| 12 | Term "behavioral disengagement" | R1 | Major | Interpretation | Terminology changed incl. subtitle and running title; alternative causes stated | Title; running title; Abstract; §1.3, §2.4.4, §3.5, §4.2, §4.3; Figure 1 caption | RESOLVED | | R1-12 |
| 13 | Target population / generalizability | R1 | Major | Interpretation | Target population defined; cohort compared with register population | §2.2, §3.1, §4.9; Table S31; S-M11 | RESOLVED | | R1-13 |
| 14 | Gaps and returns in Cox outcome | R1 | Minor | Interpretation | Handling stated; gap frequencies; alternative event definitions; Cox clock now starts at the end of age 14 | §2.4.1, §2.5.4, §3.10; Table S30; S-M1, S-M10 | RESOLVED | | R1-14 |
| 15 | "Internal cohort replication" | R1 | Editorial | Interpretation | Wording changed throughout | Abstract; §1.3, §2.2, §2.5.5, §3.10, §4.1, §4.7, §4.11; Table 7 | RESOLVED | | R1-15 |

```yaml
- concern_id: R1-1
  commitment_extracted:
    - commitment_text: "Clarify the hhi_early window; make the primary model fully baseline-only"
      commitment_type: add_analysis
      required_evidence_type: methods_paragraph
      fulfillment_status: fulfilled
- concern_id: R1-2
  commitment_extracted:
    - commitment_text: "Standardize inside training folds and report AUC, calibration, Brier"
      commitment_type: add_analysis
      required_evidence_type: new_table
      fulfillment_status: fulfilled
- concern_id: R1-3
  commitment_extracted:
    - commitment_text: "Grouped cross-validation by club"
      commitment_type: add_analysis
      required_evidence_type: new_table
      fulfillment_status: fulfilled
- concern_id: R1-4
  commitment_extracted:
    - commitment_text: "Detail the imputation model (variables, outcome, method)"
      commitment_type: add_clarification
      required_evidence_type: methods_paragraph
      fulfillment_status: fulfilled
    - commitment_text: "Report predictive performance after imputation"
      commitment_type: add_analysis
      required_evidence_type: new_table
      fulfillment_status: fulfilled
- concern_id: R1-5
  commitment_extracted:
    - commitment_text: "State handling of 24 athletes with unknown sex"
      commitment_type: add_clarification
      required_evidence_type: methods_paragraph
      fulfillment_status: fulfilled
- concern_id: R1-6
  commitment_extracted:
    - commitment_text: "Explain birth-quarter coding and the Q1/Q4 choice"
      commitment_type: add_clarification
      required_evidence_type: methods_paragraph
      fulfillment_status: fulfilled
- concern_id: R1-7
  commitment_extracted:
    - commitment_text: "Give the change formula and align OR interpretation with direction (14-15 and 15-16)"
      commitment_type: add_clarification
      required_evidence_type: prose_edit
      fulfillment_status: fulfilled
- concern_id: R1-8
  commitment_extracted:
    - commitment_text: "Moderate 'genuine within-athlete pull-back' wording"
      commitment_type: other
      required_evidence_type: prose_edit
      fulfillment_status: fulfilled
    - commitment_text: "Formal longitudinal analysis of volume before exit"
      commitment_type: add_analysis
      required_evidence_type: new_table
      fulfillment_status: fulfilled
- concern_id: R1-9
  commitment_extracted:
    - commitment_text: "Replace 'explains more variance' with discrimination wording"
      commitment_type: other
      required_evidence_type: prose_edit
      fulfillment_status: fulfilled
- concern_id: R1-10
  commitment_extracted:
    - commitment_text: "Uncertainty for AUC differences (CI or paired bootstrap)"
      commitment_type: add_analysis
      required_evidence_type: new_table
      fulfillment_status: fulfilled
- concern_id: R1-11
  commitment_extracted:
    - commitment_text: "Present <10 as a candidate threshold"
      commitment_type: other
      required_evidence_type: prose_edit
      fulfillment_status: fulfilled
    - commitment_text: "Define threshold in one cohort, test in the other"
      commitment_type: add_analysis
      required_evidence_type: new_table
      fulfillment_status: fulfilled
- concern_id: R1-12
  commitment_extracted:
    - commitment_text: "Use 'declining competition participation' / 'behavioral marker of disengagement'"
      commitment_type: other
      required_evidence_type: prose_edit
      fulfillment_status: fulfilled
- concern_id: R1-13
  commitment_extracted:
    - commitment_text: "Clarify target population and discuss generalizability"
      commitment_type: add_clarification
      required_evidence_type: discussion_paragraph
      fulfillment_status: fulfilled
- concern_id: R1-14
  commitment_extracted:
    - commitment_text: "Clarify handling of temporary gaps and returns in the Cox outcome"
      commitment_type: add_clarification
      required_evidence_type: methods_paragraph
      fulfillment_status: fulfilled
- concern_id: R1-15
  commitment_extracted:
    - commitment_text: "Use 'internal cohort replication'"
      commitment_type: other
      required_evidence_type: prose_edit
      fulfillment_status: fulfilled
```

## Corrections beyond the reviewer's comments (disclosed in the response letter)

| Correction | How found | Effect |
|---|---|---|
| Tyrving scoring omitted all specification-coded events (throws, hurdles, zone jumps, race walk) | Tracing the cause of Tyrving missingness (Comment 4) | Missing 19.7% → 0.1% (with the sex correction); n 1,704 → 2,136 |
| Tyrving formulas wrong for 600 m+ and race walk (hundredths instead of tenths) and for throws/pole vault (steepest rate throughout) | Data audit: workbook formulas read from the hidden columns; implementation validated 1,596/1,596 against LibreOffice-recomputed workbook (audit/audit_03) | Tyrving OR in L4 1.23 → 1.75; L2 AUC 0.641 → 0.700; volume-vs-Tyrving AUC gap 0.098 → 0.040; §4.2 and H2 conclusion revised |
| Career extraction paginated on non-unique key (date): 332 rows duplicated, 334 skipped (240 athletes) | Data audit (audit_01/02: deterministic re-extraction ordered by id, created_at ≤ 2026-05-18) | Rows added/de-duplicated (r1_00) |
| Baseline meet identified by name: 2 venue-days under other names; loose patterns matched other meets | Data audit (audit_04) | Venue-and-date definition; all 2,123 confirmed, 15 added (n 2,138); first edition changed for 5 |
| Partial 2026 season in follow-up | Data audit | Follow-up ends 2025-12-31 (339 rows removed) |
| Sex from May 2026 extract (pre-correction) | Data audit vs current register | Register values after July 2026 correction; implements agree for all 24 changed athletes with implement evidence, and contradict the register for 2 of 1,296 athletes with clear evidence (audit/audit_05) |
| Region misassigned (endurance lists of all venues filed under one venue, 2013–2015) | Data audit | Region from other events (same venue both editions: 100%; club rule 99.9%); 221 athletes changed |
| Cohort A club = club of last result (post-baseline) | Data audit (klubb matched last result's club for 99.8%) | Club = club at the baseline meet for all; club size recomputed |
| Same-day results under two meet records counted as two meets | Data audit | Volume = competition days (1,046 athlete-days affected) |
| Baseline-only Cox clock started at the baseline meet (inside the 13–14 predictor window) | Independent code review of scripts 08–16 | Time zero at end of age 14 (229 not at risk); volume HR 0.56 → 0.65; Tables S3, S10, S16, S30 |
| Age-16 landmark included 71 athletes already exited | Same | At-risk = final active season ≥16; HR 0.68 |
| Figure S1 was the in-sample fit of a post-baseline logistic model, captioned as Cox | Same | Replaced by cross-validated calibration of the primary model |
| Figure 3 caption (71% vs 4%) and §3.2 KM summary (3 years, steepest at 17) did not match the curves | Same / audit | Corrected (KM: 22% at 14 years vs 0.3% at the end of the lowest curve, 11 years; senior 50% vs 0.8%; median 2 years; exit rate peaks at 18–19) |
| Table S31 used the September 2026 register (post-May import had duplicated historical results) | Data audit (DB rows created 2026-08-29 duplicate existing results) | Register state of the extraction; cohort reproduced exactly (2,138) |
| Robustness claims for clustering/mean imputation pointed to the post-baseline Cox (S2, S5) | Independent code review | Club-clustered SE and GEE for the primary model (Table S22); text corrected |
| Detection capacity (S-M2, Table S4) used the old event count and derived values from the submission | Independent number cross-check | Recomputed from the correctly timed Cox model and the primary logistic model (HR_min 1.07, OR_min 1.18) |
| Several quoted numbers had no stored source (KM summary, club changes, hurdlers, submitted-data refits) | Same | Added to r1_04 (tables/r1_text_numbers.json) |
| Table 5 non-volume rows from an earlier model run | Regenerating all tables from code | Table 5 fully regenerated; Figure S4 now drawn from the table |
| Table S2 CIs and Table S4 event counts transcribed inaccurately | Same | Regenerated |
| Citation "(van Houwelingen, 2007; …)" not converted to Vancouver | Citation check in build | Reference 29 now cited by number |
| Figure 1 box cited self-determination theory (not in text or reference list) | Figure review | Replaced by meaning-in-movement accounts (Kretchmar, cited in §1.1) |
| Table 1 note misdefined "active at age 17" | Code review (aktiv_17 = active season at 17 or later) | Note and row label corrected |
| 90 athletes without birth date coded into the birth-quarter reference group | Comment 6 analysis | Disclosed; alternative codings in Table S13 Panel B |
| Figure 2's in-figure title said divergence "emerges at the qualification milestone" (the groups already differ at 13–14) | Final check (figures viewed) | Neutral title; legend moved off the milestone label |
| Figure S0 called the baseline meet "national" (it is regional; reviewer comment 13) | Final check | "Regional"; exclusions shown (631 born 1997/2003; 1,012 in both editions) |
| Response letter said Figure 1 shows the alternative causes of decline (comment 12); it did not | Final check | Dashed box added to Figure 1 and named in its caption |
| STROBE checklist, part of the original supplement, was missing from the R1 supplement; title page still had the old title | Final check | Checklist updated for R1 and appended to the supplement; TITLE_PAGE_R1.docx built |
| Double rounding: the original scripts stored estimates to 3 decimals, which r1_06 rounded again to 2 (12 cells 0.01 off in Tables 5, S11, S13, S17, S18; S18 Model A disagreed with Table 3) | Final check (independent refits at full precision) | r1_02 keeps 6 decimals; all cells re-generated; no main-text number affected |
| Identical computations in Table S29 had different bootstrap CIs | Final check | One bootstrap per cohort and cut-off |
| Highlighting: new tables S26–S32 were blue only in the title; S21 and changed column headers were not highlighted | Final check | New tables highlighted throughout; changed headers and S21 cells highlighted |
| Text claims: "all cross-validation uses 20 repeats" (S9, S17, S24 use the original single split); "CI for every CV-AUC"; external validation; §1.3 and Figure 1 named for alternative causes; unknown sex "excluded from all models" (S5 keeps them); 17–19 replication overstated; Table 1 note pointed to §2.4.3; S-M3 citation without reference; superseded S-M11 sentence | Final check (independent text audit) | All corrected in the manuscript, supplement and response letter; Changes lists completed |
| Acknowledgements say the AI use is declared in the cover letter; the original cover letter carried outdated numbers | Final check | COVER_LETTER_R1 written (10_cover_letter_r1.md) |
| Club random intercepts fitted by variational Bayes (interval too narrow, as our own note admitted) | Final check (comment 3 strengthened) | Maximum likelihood with Gauss–Hermite quadrature (r1_03 `re_logit_ml`; likelihood checked by adaptive integration): volume OR 2.07 [1.80, 2.37], club SD 0.17, LR p = .31; §3.4, S-M7, Table S22, letter |
| Possible reviewer queries on comments 1, 2, 4: changed category list in §2.4.3; submitted calibration intercept (−0.06) vs. calibration-in-the-large; CV-AUC 0.753 vs. 0.751 | Final check | Explained in the letter (comment 1) and the notes to Tables S26 and S21 |
| Championship types (post-baseline covariate): "UM" matched as letters anywhere (Bærum, Brumunddal, Jubileumsstevne: 90 of 116 names); "Junior-NM"/"NM junior" counted as senior; "KM … og NM veteraner", Albuquerque/NM/USA, NM-test, qualification, preparation and unofficial meets, veterans'/school KM and side events at national championships before 15 counted; Nynorsk "Kretsmeisterskap" missed | Final check, 3 Oct 2026 (independent data review; every matched meet name read) | Corrected in r1_00 (count changed for 318 athletes; 360 after the final narrow review, below); independent token-based R classification agrees for all 2,138; Table 5, S1, S2, S5–S8, S11, Figures S3–S4 regenerated; §3.7, §4.5, §4.9 numbers updated; S-M12, Figure S3 caption, letter ("Other corrections") |
| HHI and result count at 13–14 excluded one result of one athlete that failed the sprint-time sanity filter (a scoring filter) | Final check (independent R implementation, 1 mismatch) | HHI from every result; no displayed number changed except one Table S13 cell (1.55 → 1.54) |
| Text precision: FE sentence in the Abstract said "dropouts'" (the model pools all observed exits, 186 at 20+); "only in Cohort B" (cohort difference p = .11); "performance matched volume" without CI; "low-but-active" (29% of flagged athletes had no result at 14); "1 ≤ vol"; "holds within clubs" (random intercepts, not a within-club estimate); §4.5 causal wording; Table S20 n not explained; letter omitted T−2 in the 17–19 replication | Final check (independent claims review) | All corrected; §2.5.1 cites Table 4 M1 for athletes still competing at 14 |
| Final narrow review (independent agent, 3 Oct 2026), championship types: Finnmark's district championship ("FM") and Norwegian "DM" missed; individual results at NM relay meets (100 m side events) and youth classes at "NM Mangekamp inne 2018" counted as senior NM; district championships for ages 11–14 credited to 15–16-year-olds | Final narrow review (verified on the data) | Rules refined in r1_00 and, independently, in the R check (0 mismatches); count changed for 360 athletes in all (after the re-review's indoor-games fix); post-baseline tables and §3.7, §4.5, §4.9 numbers moved by at most 0.01 (χ² 264.3 → 263.1); 10 athletes whose district type rests only on embedded KM events stated in S-M12 |
| Final narrow review, claims and letter: "only in Cohort B" left in the letter (twice); S22 note and letter said "within clubs" without a within-club estimate; §3.9 "Cox models with volume agree" holds only for the baseline-only Cox models; "volume at 14 added nothing" (p = .056); "tapered" (letter says the taper wording was replaced); §4.5 called the sex-only OR adjusted; S19 note; "CI for every difference"; "time-aligned" labels; S6 "unchanged" | Final narrow review | All corrected; club fixed effects (conditional logit) added to Table S22: OR 2.28 [1.93, 2.69] |

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total items | 15 |
| Resolved | 15 |
| Deliberate Limitation | 0 (generalizability and threshold transfer also stated as limitations, §4.9) |
| Unresolvable | 0 |
| Reviewer Disagree | 0 |
| Word count change | +316 (Introduction and Discussion shortened; correction details moved to S-M12) |
| New references | 0 main text; 2 supplementary (verified in CrossRef) |
| New tables/figures | 7 supplementary tables (S26–S32), Table S13 Panel B, Figure S5; Figure S1 replaced; Supplementary Methods S-M12 (data audit) |

## Revision Completeness Checklist

- [x] Every reviewer comment has a corresponding row in the tracking table
- [x] Every RESOLVED item specifies the exact location of the change
- [x] Limitations updated (§4.9: target population, candidate thresholds, fixed-effects analysis)
- [x] The response letter addresses all comments in order
- [ ] Word count is within the journal's limit after revisions — 6,352 vs. "should not normally exceed 6,000" (6,036 at submission); 6,056 without headings and table/figure placeholders
- [x] All new references are added (supplementary list); main-text numbering verified in order of first appearance (1–37)
- [x] No new errors introduced: all tables and figures generated from code; original-data sandbox reproduces every submitted table byte-for-byte; corrected data rebuilt deterministically (r1_00) and audited (audit/)
- [x] AI disclosure statement unchanged and still accurate (Acknowledgements)
