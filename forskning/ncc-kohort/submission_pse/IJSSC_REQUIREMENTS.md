# IJSSC (International Journal of Sports Science & Coaching, SAGE) — Submission Requirements

## Article type & length
- **Original Research: should not normally exceed 6,000 words** (Research Notes 3,000)
- Word format preferred (no template needed); LaTeX accepted

## Abstract & keywords
- **Unstructured** abstract between title and main body: purpose, major findings, conclusions. Concise.
- **Minimum 5 keywords**, as specific as possible

## Reference style
- **Sage Vancouver** — numbered in order of appearance (superscript in text), NOT author–year
- Every in-text citation must match reference list exactly and vice versa
- EndNote output style available; preprint citations discouraged

## Required end-matter: "Statements and Declarations" section (after Acknowledgements)
Each subheading REQUIRED even if "Not applicable":
1. **Ethical considerations** — explicit statement even if approval not required (state that it was not required and why); include committee name + approval number when applicable; mirror in Methods
2. **Consent to participate** — written/verbal, or waived, or "Not applicable"
3. **Consent for publication** — "Not applicable" if no individual-person data
4. **Declaration of conflicting interest** — exact wording if none: "The author(s) declared no potential conflicts of interest with respect to the research, authorship, and/or publication of this article."
5. **Funding statement** — required even if no funding
6. **Data availability** — share in repository if possible; if not, statement explaining why; cite data

## Acknowledgements
- Third-party writing/editing assistance MUST be declared in Acknowledgements AND cover letter
- (AI use → keep our generative-AI declaration; SAGE requires disclosure)

## Figures
- Color free online; SAGE artwork guidelines; permissions author's responsibility

## Supplemental material
- Hosted online; accepted file types per SAGE guidelines (our S-tables/extended methods go here)

## Scope notes (Aims & Scope)
- Coaching-relevant sport science; youth development, talent pathways, participation
- Emphasize practical/coaching implications (behavioral surveillance thresholds, volume monitoring)

## Word-budget plan — EXECUTED 2026-08-25
| Section | From | Final |
|---|---|---|
| Intro | 1,068 | 994 |
| Methods | 2,084 | 1,529 (extended detail → 15_supplementary_methods.md) |
| Results | 1,526 | 1,279 (old §3.3 KM folded into §3.2; §§ renumbered 3.3–3.10) |
| Discussion | 2,702 | 2,041 (SDT paragraph dropped; §4.6/§4.7 compressed) |
| Refs | 48 items | 35 items (6 moved to supplementary-only list; 7 dropped: Baker 2026, Heale & Forbes, Peringa, Ryan & Deci, Schacter, Standage, Vallerand) |
| **Main text (Intro–Discussion)** | 7,484 | **5,843 APA / 5,680 Vancouver — under 6,000** ✓ |

## Build pipeline
1. `compile_manuscript.py` → MANUSCRIPT_ANONYMIZED.md (APA working copy; incl. Acknowledgements + Statements and Declarations before References)
2. `build_reading_copy.py` → MANUSCRIPT_FULL.md (tables/figures inline, for author review)
3. `convert_to_vancouver.py` → **MANUSCRIPT_IJSSC.md** (Sage Vancouver superscripts, numbered refs — the submission text). Rerun all three after any section edit; if citations are added/removed/reordered, update the mapping tables in convert_to_vancouver.py.

## Done 2026-08-25
- Unstructured abstract (~215 w) in 02_abstract.md; 7 keywords in compile_manuscript.py META
- Statements and Declarations with all six SAGE subheadings + exact no-conflict wording (09_declarations.md)
- Acknowledgements with AI writing-assistance declaration (also in cover letter, per SAGE policy)
- IJSSC cover letter (10_cover_letter.md): suitability + AI declaration + compliance
- Sage Vancouver conversion (35 numbered refs, 46 in-text superscripts, zero APA leftovers)

## Open before submission
- **Preprint question (user):** is Research Square preprint 10.21203/rs.3.rs-9785334/v1 this manuscript or a sibling paper? If this one → supply DOI in Sage Track field
- Convert MANUSCRIPT_IJSSC.md → .docx (pandoc) + assemble 300-dpi figure files
- Sage Track entry data: author/affiliation must match title page; word/table/figure counts; ORCID 0000-0003-0188-8462

Untouchable (referee-critical): §2.2 Norwegian context, §3.7 volume–performance correlations, §4.4 Ebaugh integration, §4.6 construct distinction core, co-occurrence limitation, Battaglia definitions, Enoksen anchoring, hypothesis justifications.

## Submission process (Sage Track / ScholarOne: mc.manuscriptcentral.com/spo)
- **Cover letter required** — must indicate why suitable for the journal; must also declare any third-party writing assistance
- **ORCID for submitting author**: 0000-0003-0188-8462
- Enter at submission: author list + affiliations (must match title page exactly), keywords, word/figure/table counts, funder info, conflict declaration
- **Preprint policy**: accepted; supply preprint DOI in designated field if posted; do not update preprint during review; NB check whether related Research Square preprint (10.21203/rs.3.rs-9785334/v1) is this manuscript or a sibling paper
- Figures: 300 dpi, numbered consecutively
- AI chatbots must not be authors (our AI-use declaration stands)
