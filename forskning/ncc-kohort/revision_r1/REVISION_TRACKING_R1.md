# Revision Tracking — SPO-26-1604 (IJSSC), round 1

## Paper Information

| Field | Value |
|-------|-------|
| Paper Title | Pulling back before dropping out: Declining competition participation precedes exit from Norwegian youth track and field — a 14-year register study |
| Revision Round | 1 |
| Date | 2026-10-01 |
| Previous Decision | Revise (one reviewer, Dr Imad Hamri; 15 comments) |
| Target Journal | International Journal of Sports Science & Coaching |
| Original Word Count | 6,036 (main text, journal count) |
| Revised Word Count | 6,558 |

## Revision Tracking Table

| # | Issue | Reviewer | Type | Section | Resolution summary | Location of change | Status | Reason (if not resolved) | Commitment Ledger |
|---|---|---|---|---|---|---|---|---|---|
| 1 | hhi_early used results after age 14 | R1 | Major | Methods | Confirmed error; HHI recomputed from ages 13–14; all models re-run; HHI claims tempered | §2.4.3, S-M8; Tables 3, 5, 7, S1–S2, S5–S11, S13, S16–S18, S20–S22, S25; §3.3, §3.9, §4.1, §4.6 | RESOLVED | | R1-1 |
| 2 | Standardization before CV | R1 | Major | Methods | In-fold standardization; shown identical for unpenalized LR; repeated CV | §2.5.1, S-M4; Tables 3, S23, S26 | RESOLVED | | R1-2 |
| 3 | Club-grouped CV | R1 | Major | Methods | StratifiedGroupKFold by club (287 clubs): AUC 0.746 unchanged | §2.5.1, §3.4, S-M4, S-M7; Tables S22, S26 | RESOLVED | | R1-3 |
| 4 | MI details + predictive performance | R1 | Major | Methods | Root cause found (Tyrving scoring gap) and corrected (missing 19.7% → 1.3%); MI fully specified; MI predictive performance with in-fold imputation | §2.4.2, §2.5.5, S-M3; Tables 1, S12, S21, S25 | RESOLVED | | R1-4 |
| 5 | Unknown sex handling | R1 | Minor | Methods | Stated; sensitivity with separate category | §2.4.5, S-M3; Table S12; Figure S0 | RESOLVED | | R1-5 |
| 6 | Birth-quarter coding | R1 | Minor | Methods | Coding and rationale stated; alternative codings | §2.4.5, §2.5.2, §3.4; Table S13 Panel B | RESOLVED | | R1-6 |
| 7 | Change-score OR direction | R1 | Major | Results | Formula given; ORs per SD increase and per SD decline | §2.5.3, §3.5; Table 4; Tables S14, S19; S-M6 | RESOLVED | | R1-7 |
| 8 | Pull-back wording / formal analysis | R1 | Major | Results | Athlete fixed-effects model added and wording moderated | §2.5.3, §3.5, §4.1, §4.3, §4.4, §4.11; S-M6; Table S28; Figure S5 | RESOLVED | | R1-8 |
| 9 | "Explains more variance" vs AUC | R1 | Minor | Results/Discussion | Discrimination wording | Abstract; §1.3, §3.6, §4.2 | RESOLVED | | R1-9 |
| 10 | Uncertainty on AUC differences | R1 | Major | Results | CIs for every CV-AUC; paired differences with corrected t | §2.5.1, §3.3, §3.6, §4.2; S-M4; Tables 3, S15, S27 | RESOLVED | | R1-10 |
| 11 | Threshold derived and tested in same data | R1 | Major | Results | Candidate wording; derivation in one cohort, validation in the other | §2.5.3, §3.8, §4.8, §4.9; Table 6 note; Table S29; S-M9 | RESOLVED | | R1-11 |
| 12 | Term "behavioral disengagement" | R1 | Major | Interpretation | Terminology changed incl. subtitle and running title; alternative causes stated | Title; running title; Abstract; §1.3, §2.4.4, §3.5, §4.2, §4.3; Figure 1 caption | RESOLVED | | R1-12 |
| 13 | Target population / generalizability | R1 | Major | Interpretation | Target population defined; cohort compared with register population | §2.2, §3.1, §4.9; Table S31; S-M11 | RESOLVED | | R1-13 |
| 14 | Gaps and returns in Cox outcome | R1 | Minor | Interpretation | Handling stated; gap frequencies; alternative event definitions | §2.4.1, §2.5.4, §3.10; Table S30; S-M1, S-M10 | RESOLVED | | R1-14 |
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
| Tyrving scoring omitted all specification-coded events (throws, hurdles, zone jumps, race walk) | Tracing the cause of Tyrving missingness (Comment 4) | Missing 19.7% → 1.3%; n 1,704 → 2,095; Tyrving now OR 1.23 in L4; volume OR 2.33 → 2.25 |
| Table 5 non-volume rows from an earlier model run | Regenerating all tables from code | Table 5 fully regenerated; Figure S4 now drawn from the table |
| Table S2 CIs and Table S4 event counts transcribed inaccurately | Same | Regenerated |
| Citation "(van Houwelingen, 2007; …)" not converted to Vancouver | Citation check in build | Reference 29 now cited by number |
| Figure 1 box cited self-determination theory (not in text or reference list) | Figure review | Replaced by meaning-in-movement accounts (Kretchmar, cited in §1.1) |
| Table 1 note misdefined "active at age 17" | Code review (aktiv_17 = active season at 17 or later) | Note and row label corrected |
| 84 athletes without birth date coded into the birth-quarter reference group | Comment 6 analysis | Disclosed; alternative codings in Table S13 Panel B |

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total items | 15 |
| Resolved | 15 |
| Deliberate Limitation | 0 (generalizability and threshold transfer also stated as limitations, §4.9) |
| Unresolvable | 0 |
| Reviewer Disagree | 0 |
| Word count change | +522 (journal count) |
| New references | 0 main text; 2 supplementary (verified in CrossRef) |
| New tables/figures | 7 supplementary tables (S26–S32), Table S13 Panel B, Figure S5 |

## Revision Completeness Checklist

- [x] Every reviewer comment has a corresponding row in the tracking table
- [x] Every RESOLVED item specifies the exact location of the change
- [x] Limitations updated (§4.9: target population, candidate thresholds, fixed-effects analysis)
- [x] The response letter addresses all comments in order
- [ ] Word count is within the journal's limit after revisions — 6,558 vs. "should not normally exceed 6,000"; flagged to the editor with an offer to shorten
- [x] All new references are added (supplementary list); main-text numbering verified in order of first appearance (1–37)
- [x] No new errors introduced: all tables generated from code; original-data sandbox reproduces every submitted table byte-for-byte
- [x] AI disclosure statement unchanged and still accurate (Acknowledgements)
