# Response to the Simulated IJSSC Panel (PEER_REVIEW_SIMULATION_IJSSC.md)

**Date:** 2026-08-25. All 16 required revisions (M1–M16) addressed; suggested revisions S1–S12 largely incorporated. New analyses: `data/16_revision_analyses.py` → `data/revision_results.json`; regenerated/new supplementary tables in `submission_pse/tables/`.

## Required revisions

**M1 — Exit-aligned pull-back analysis (DA CRITICAL). DONE — the title stands, now with direct evidence.**
New analyses (Section 3.5; Supplementary Table S19; Methods 2.5.3; S-M6): (a) exit-aligned trajectories for 1,139 dropouts with final seasons at ages 15–19 — median volume T−3…T = 12 → 10 → 9 → 4 meets; 95% still competing in the penultimate season; among final seasons at 16+ (n = 795), 74% reduced-but-nonzero penultimate season, 6% gap year, only 19% abrupt (exit from personal peak). (b) Contamination-free change model among athletes all still active at 16 (n = 1,075): level-15 OR = 3.04, change 15→16 OR = 1.88, both p < .001 — decline predicts exit where no exit can contaminate the change score. The within-athlete process claim is now demonstrated at the individual level; title, abstract, and §4.4 retained and re-anchored to this evidence.

**M2 — Numeric traceability. DONE.** S3 and S9 were traced to their source: both were computed on the *old* milestone-window specification (vol_milepael HR 0.35; "M2" = old Cox stepwise model 2) — stale artifacts of the pre-reframe pipeline, exactly as R1 suspected. Both regenerated on the primary specification (old CSVs kept as `*_OLD.csv`). Canonical numbers re-derived from a single re-run: volume OR 2.40 [2.08, 2.76]; HHI OR 1.36 [1.17, 1.57]; every in-text statistic harmonized to these. Tables 5 and 7 restored to the compiled manuscript (missing "about here" placeholders — a build artifact — fixed). Table 6 recomputed on one denominator (n = 2,123) with 2,000-rep bootstrap CIs; the old .md table's transcription drift (0.92/0.22) eliminated.

**M3 — Governance. DONE.** New "Governance preconditions" paragraph in §4.8 (legal basis + DPIA before deployment; designated flag recipient, not coaches; informed families with opt-out; retention limit; equity caveat; no-contact framing named a transparency problem). §2.7 adds that the research exemption does not extend to operational use. §4.11 carries the governance qualifier.

**M4 — Prediction→intervention reframe. DONE.** §4.8 now opens: "a *testable targeting rule*, not a finished intervention". Offer-not-pressure made explicit in item (3); §2.2/§4.8 barrier tension reconciled (remedies now target residual and psychological costs); reallocation/benign-exit reading given co-equal standing in §4.4 (Battaglia engaged substantively via the reframe; Espedalen 2025 cited for exit-as-autonomy); the §4.10 pilot promoted to the central next step, with stakeholder consultation; applied limitations added (§4.9, eighth item).

**M5 — Honest screen arithmetic. DONE.** Abstract now carries base rate (84%), sensitivity (0.30), and the absolute contrast (6% vs 20% retention); Table 6 gains flagged/unflagged retention columns and bootstrap CIs; §3.8 interprets NPV ("the flag concentrates risk; it certifies no one's continuation"); §4.8(1) tells federations to prioritize, not substitute for universal provision.

**M6 — E-value on the primary estimate. DONE.** Primary OR 2.40 → RR ≈ 1.55 (common-outcome √OR conversion) → E = 2.5 (CI bound 2.2); baseline-only Cox HR 0.49 → E = 2.6. Milestone-window E-value (5.16) retired with an explicit note (S3; S-M5) that the demoted specification is not an admissible E-value input. §3.10 and §4.7 rewritten accordingly.

**M7 — Missing data and samples. DONE.** Multiple imputation (m = 20, Rubin) as principal sensitivity: volume OR 2.35 [2.08, 2.67] (Table S21). Included-vs-excluded comparison (Table S25: retention 16.5% vs 16.0%). Sample-flow table (Table S12, replacing the deleted RF table) maps every n. Table 4's n resolved: 1,914 = athletes active at 14; fitted complete-case n = 1,549 (Tyrving missingness concentrated among early-inactive: 25.8% vs 19.1%) — table header corrected. Sex-unknown handling stated (S-M3).

**M8 — HHI stress tests. DONE — the finding survives.** HHI–count correlation reported (ρ = −.38); restriction to ≥5/≥8 early results: OR 1.38/1.39; finite-sample-corrected index: OR 1.39 [1.20, 1.60] (Table S20; S-M8). §3.9 retitled descriptively ("Within-sport event concentration and retention"); §4.6 and implication (4) note robustness.

**M9 — TRIPOD-level prediction reporting. DONE.** CV calibration slope 0.96, intercept −0.06, Brier 0.122 (Table S23); Table 6 bootstrap CIs on one denominator; "calibration" renamed "classification performance" where appropriate; random forest deleted from Methods (Table S12 repurposed, Figure S2 removed, S17's RF column dropped; Breiman reference removed); declared-but-unreported variables resolved (tyrving_mean/year_round dropped; res_age retained as the active-season definition; performance *trajectory* added to §3.6: Tyrving Δ13–14 raises performance-only AUC to 0.640 — still well short of volume — with the measurement-asymmetry caveat in §4.2).

**M10 — Citation repair. DONE in text; full audit delegated to the author.** Larson et al. (2019) now cited for its actual finding (specialization markers *not* positively related to burnout/dropout — consistent with our result). Espedalen (2025) re-grounded: the two-tier characterization now rests on Bakken (2019) and the SCM's enthusiastic/constrained distinction; Espedalen (2025) is cited only for exit-as-autonomy. Eime re-scoped to what the review supports; the "half stopped by 17" claim now derived from the paper's own Table 1; DiFiori/Güllich design labels fixed ("position statement"/"meta-analysis" wording removed by rephrasing the sentence). **NB: the author will verify all references against sources before submission (per plan).**

**M11 — Nearest neighbors. DONE.** §1.2 now positions the gap against Back et al. (2022, prospective-dropout meta-analysis) and register/rankings-based *performance*-trajectory work in athletics (Kearney & Hayes, 2018), and claims only the *participation* trajectory as new. Both new references CrossRef-verified this session (DOIs 10.1016/j.psychsport.2022.102205; 10.1080/02640414.2018.1465724). Raedeke (1997) added for the constrained-commitment–burnout link (10.1123/jsep.19.4.396). Lippe/Næsje not added as separate entries (available only via Enoksen's review; left for the author to decide on secondary citation).

**M12 — Injury. DONE.** Injury added as a named alternative explanation in §4.2 (24.3% in Enoksen, 2011; identical register signature) and to the limitations (§4.9, second item).

**M13 — Volume-as-choice documentation + club confounding. DONE.** §2.2 cites the federation's competition regulations (NB: URL/year to be verified by author), adds the regional-team caveat and the venue-coverage statement (no northern Norway). Club ICC = 0.25 (277 clubs); club random-intercept refit: volume OR 2.58 [2.27, 2.93] — the association holds *within* clubs (Table S22; §3.4; S-M7).

**M14 — Scope discipline. DONE.** Abstract opens with withdrawal from youth sport as theory but the study scoped to Norwegian track and field; running title now sport-specific; "independent cohorts" → "adjacent birth cohorts" / internal replication; "formal exit" removed; reallocation co-equal in §4.4; transferability boundary conditions in §4.9 (eighth item); H3 labeled a robustness expectation.

**M15 — Sex reconciliation. DONE.** §4.5 rewritten: KM null and Table 3's significant adjusted female ORs (0.72 → 0.61) presented together and reconciled (higher female early volumes mask a residual gap that appears conditional on behavior); connected to Enoksen's historical female attrition; "above, not through" claim retained — now supported by the contrast.

**M16 — Hygiene bundle. DONE.** §1.1 retitled "Withdrawal as a deliberative, gradual process"; withdrawal/dropout phrasing fixed in §4.4/§4.11; SDT removed from Figure 1 caption; Kretchmar cited as an account, not a named theory; §1.1 SCM determinant list corrected to match §4.4; "engagement balance" defined at first use (§1.2); §3.1 outcome parenthetical fixed; §4.1's HR 0.14 misattribution removed; Table 1 row renamed ("Ever active at age 20+") with note fixed; Methods 2.5.3 cross-reference corrected (Table 4, not S14); Table 5 columns relabeled (years since baseline, approximate ages); C-index 0.735 (not 0.74); S18 stray note deleted; CV ± defined; §2.5.6/§2.7 duplication removed; H1 pre-specifies its two components.

## Suggested revisions

- **S1 fixed-window outcome:** DONE (ages 20–22: prevalence 15.8%, A 15.3% vs B 16.7%; OR 2.43; Table S24) — also answers DA-4's follow-up asymmetry.
- **S2 landmark timing:** documented in S-M1 (clock at 16; ≥1-result rationale; contamination-free logistic analogue named); Table S8 note updated. Full re-landmark at end-of-16 not run (superseded by the cleaner change model).
- **S3 Enoksen re-engagement:** DONE (§4.2 injury share; §4.5 female attrition; age-17 peak noted in §3.2/§4.8(2)).
- **S4 H1 pre-specification:** DONE (§1.3).
- **S5 stakeholder consultation:** DONE (§4.10).
- **S6 code repository at revision:** unchanged ("upon acceptance") — author decision.
- **S7 SIMEX/reliability:** not run; measurement-asymmetry caveat added instead (§4.2), per the panel's "suggested, not required".
- **S8 logistic MDOR:** DONE (≈1.20 per SD by simulation; S-M2).
- **S9 flag routing/multi-sport clubs:** partially (designated recipient per club in §4.10); club-transfer routing left out for space.
- **S10 two-screen timing logic:** DONE (§4.8(2)).
- **S11 "monitoring" vs "surveillance":** DONE — "surveillance" removed from practitioner-facing text ("register-based flagging"/"targeting rule").
- **S12 polish:** abstract restructured; Tyrving anchor reworded; quartile percentages remain in text (space).

## Status

- Main text (Vancouver submission version): **6,023 words** (~limit; "should not normally exceed 6,000").
- References: 37 (all new entries CrossRef-verified; full source audit = author's next step).
- Supplementary tables now S1–S25 (S12 = sample flow; S19–S25 new); supplementary figures renumbered S0–S4 (RF figure removed).
- Rebuilt: MANUSCRIPT_ANONYMIZED.md/.docx, MANUSCRIPT_FULL.md, MANUSCRIPT_IJSSC.md/.docx.
- Outstanding before submission: author's reference audit; preprint-DOI question; 300-dpi figure check; STROBE checklist to supplementary; docx formatting pass in Word.
