# Simulated peer review, round 1 — "Does starting age predict who stays? Competition debut and long-term participation in youth track and field"

*Scandinavian Journal of Medicine & Science in Sports — simulated referee reports on the draft of 29 Oct 2026 (main.pdf/main.tex). Line numbers refer to the printed line numbers in the PDF.*

---

## Reviewer 1 — Epidemiologist (life-course / survival analysis): 

### Summary

The manuscript uses a national competition registry with no left truncation for the study cohorts to ask whether age at first registered competition predicts senior activity, duration-clock retention, and — among survivors to 17 — anything beyond current engagement. The design is unusually clean for this literature: exposure measured at entry for everyone who ever entered, delayed-entry survival methods used where appropriate, and the authors themselves flag the age-scale Cox blending problem (lines 111–113) rather than leaving it to reviewers. The sample arithmetic is internally consistent in every place I could check (Table 1 sums to 17 496; group ns reconcile with Table 3; the 9 330 birth-date subsample equals the Table 1 percentages exactly; 694 vs 546 events for the two senior outcomes are coherent). That said, there are several points where the construction of the estimands is ambiguous or, in one case, possibly invalid, and a handful of numerical statements that do not match the tables. All are fixable in revision.

### Major comments

1. **The landmark condition at age 17 must be defined precisely — the reported counts suggest it may condition on the future.** Lines 164–165 state that 1 922 athletes were "still active at age 17" and that 546 of these (28.4 %) became active seniors. But 546 is also the *total* number of active seniors in the cohort (lines 91, 142): every single senior is inside the landmark sample. Either (a) "active at 17" was operationalised as "any result at age ≥17", in which case all seniors enter mechanically (their results at ≥20 qualify them) and the landmark conditions on future information — athletes inactive throughout ages 17–19 who returned at 20+ are wrongly classified as "still active at 17", and the sample is not a valid landmark cohort; or (b) it means "≥1 result in the age-17 calendar year", in which case the exact equality 546 = 546 is a striking empirical fact (no senior had a fully idle age-17 season) that should be stated and briefly discussed. Please define the condition explicitly in §2.4 (lines 113–115); if (a), re-estimate H3 on the proper landmark (activity in the age-17 season, covariates measured up to the landmark only). The same ambiguity affects the Table 4 row "Outcome: active at ≥17" (line 240).

2. **"Significantly lower odds" for debuts at 11–14 is not supported for debut at 13.** Line 145–146 claims debuts at 11–14 had *significantly* lower odds than debut at 10 (OR 0.53–0.75), but Table 2 gives debut 13: OR 0.75, 95 % CI 0.55–1.02 — the interval crosses 1. The abstract's phrasing (lines 24–25, "lowest for debuts at 11–14") is fine; the Results sentence is not. Please correct. Relatedly, the "U-shape" is asserted from eyeballing seven categories; since the categorical and linear models are both fitted, please add a formal test of non-linearity (e.g., likelihood-ratio test of categorical vs linear, or a quadratic term) — the U is in the title of §3.2 and in the abstract, so it deserves a test statistic.

3. **The debut-at-17+ sensitivity analysis has an unexplained n and a potential immortal-time/outcome-overlap problem.** Line 87–88 excludes 732 athletes with debut at 17+, but Table 4 (line 244) analyses n = 17 689 = 17 496 + 193. Presumably only the 193 born 2001–2005 were usable; the discrepancy with 732 (which includes the 2006–2008 cohorts) should be stated, otherwise the reader cannot reconcile the flow. More substantively: how late can a "17+" debut be? For cohorts born 2001–2005 followed to 2026, debut at age ≥20 is possible, and a debut at ≥20 with two results in that calendar year *is itself the outcome*. Such athletes contribute outcome-guaranteed exposure time, inflating OR 2.46 (lines 176–178). Please report the debut-age distribution within the 17+ category, and either restrict to debuts at 17–19 or require the outcome to be met after the debut year. The "right arm of the U" claim may survive, but at present it is partly mechanical.

4. **The "retention k years after debut" construction needs denominators and a definition.** Table 3's caption and line 98–99 say k-year retention was "computed only over athlete-years fully observable by 2025", yet the table shows a single n per debut age. A 2005-born athlete debuting at 16 (debut season 2021) has no observable k = 5 by 2025, so the k = 5 denominator cannot be the full 424 at debut 16. Please give per-k denominators (or per-k ns in a footnote) and define "still competing k years after": active in calendar year debut + k exactly (point prevalence), or active at any time ≥ debut + k? These differ when athletes skip seasons. Wilson or similar CIs on Table 3 would also help, since this table "carries the H2 conclusion" (lines 234–235). Finally, consider a covariate-adjusted duration-scale model: the debut groups differ in sex composition (Table 1: 52.2 % vs 42.0 % female), so the descriptive proportions are not compositionally comparable, even if the overall sex HR is null (lines 160–161).

5. **Exit and censoring rules should be stated as an operational definition.** Lines 109–110: events occur at last active age (+0.5), censored if active in 2025–2026. As I read it, an event therefore requires inactivity in both 2025 and 2026, i.e., a ≥2-idle-year confirmation window for everyone with last activity ≤2024 — please say this explicitly, and acknowledge that returns after 2026 are unknowable (an athlete last active 2024 who returns in 2027 is misclassified). Also reconcile "to the end of 2026" (abstract, lines 22–23) with the extract frozen on 29 Oct 2026 (line 78): the 2026 season is partially observed, which slightly disadvantages the senior outcome for the 2005 cohort (senior window 2025 + partial 2026). The cohort covariate and the cohort-halves robustness mitigate this, but it belongs in limitations.

6. **Covariate sets differ across models without justification.** §2.3 (lines 99–102) lists sex, cohort, region, club, log club size, birth quarter, debut-season days, and a COVID flag. The primary H1 model adjusts for sex, cohort, region, club size (lines 104–105; Table 2 caption); H3 adjusts for sex and cohort only (line 114); the COVID flag appears only as an exclusion; baseline club appears only via clustered SEs. Please state, per hypothesis, exactly which covariates enter and why, and consider adding the COVID flag to the primary model (the exclusion robustness at line 173–174 moves the trend to 0.95, 0.90–1.01 — not material, but worth one sentence). Also report the number of region levels and, in a supplement, full model coefficients.

7. **STROBE flow and reporting.** A participant flow diagram is missing and the sample arithmetic requires the reader to infer that 28 339 − 865 − 732 = 26 742 splits into 17 496 (born 2001–2005) + 9 246 (born 2006–2008, descriptive only) (lines 85–92). Please add the diagram, state the 9 246 explicitly, and note what the 116 sub-age-10 rows and 1 526 non-approved rows imply for debut assignment (an athlete whose first-ever appearance was non-approved or below 10 gets a later "debut"; numbers are tiny, but say so). Submit the STROBE checklist.

### Minor comments

- Line 143–144: "fell to 2.0–2.4 % … (bottom: 2.1 % at 12)" — a range whose lower bound (2.0) lies below the stated minimum (2.1) is internally inconsistent; also debut 13 (~2.9 %) is silently skipped in that sentence. Rewrite with the actual values.
- Line 153–154: "17 % against 3–7 %" — on Table 3, debut 11 is 10 % at k = 5; the abstract correctly restricts to 12–16 (lines 27–28), the Results sentence does not. Align.
- Line 188–189: "a quarter to a third of teenage debutants" — debut 13 (a teenager) is 38 % at k = 1. Either define "teenage" as 14–16 or adjust.
- Abstract, lines 29–30: "debut age appeared protective (OR 0.87 per year)" is directionally ambiguous; per Table/text it is *earlier* debut that appears protective (OR 0.87 per year of *later* debut). Say so.
- Table 2: debut 16 rests on 28 events; the CI is honest (1.15–2.59) but a cautionary clause about sparse events would be fair, and the categorical U (not just the linear trend) should be shown for the two cohort halves if feasible.
- Reference [12] (Anderson et al. 1983) is cited at line 109 for "delayed entry" — Anderson et al. is the *landmark-method* paper; it belongs with the landmark analysis (lines 113–115). Delayed-entry/left-truncated, age-as-timescale Cox should be supported by a standard survival-methods source instead.
- Reference [2]: the entry gives Frontiers in Sports and Active Living vol. 3 with year 2022; volume 3 corresponds to 2021 — please verify year/volume (and the Espedalen & Seippel year/volume/pagination, [5]).
- Figure 4 duplicates Table 3; consider moving one to a supplement (4 tables + 4 figures is heavy for ~3 000 words).
- Lines 73–74, 125–127: the version-controlled plan is a strength — consider depositing the time-stamped plan and code in a public archive rather than "available from the author" (lines 256–258).

**Recommendation: Major revision.**

---

## Reviewer 2 — Sport sociologist (youth sport participation and recruitment policy, Nordic context):

### Summary

This is a rare data source used on a question federations actually ask, and the paper is commendably honest that competition debut is not sport start and that selection into debut age is "unmeasured and surely strong" (lines 230–231). My concerns are about what the exposure measures institutionally, about the invisibility of gender in the analysis despite a large gender gradient in the exposure, and about a Perspective section that converts selection effects into recruitment advice and rests one of its key claims on a figure ("halved over a decade") that appears nowhere in the Results.

### Major comments

1. **What "competition debut at 10" measures is partly an institutional artefact, and the paper should analyse it as such.** Registered debut reflects not only family/child behaviour but registration practice: which local meets submit results, how clubs handle the youngest classes, and how the Norwegian children's sport framework regulates competition and results for children. The share debuting at 10 rose from 32.6 % (born 2001) to 43.9 % (born 2008) (lines 130–132, Figure 1) — this may be organisational drift (more complete registration of 10-year-olds after the registry's 2011 digitisation, growth of youth meets) rather than earlier behavioural entry. The 116 excluded sub-age-10 rows (line 85–86) show that the age-10 boundary is administratively enforced, not natural. Please add a paragraph on registration practice as a competing explanation for cohort trends in debut age, and clarify what the age-10 threshold means in the Norwegian regulatory context (lines 79–82 touch this only via performance data).

2. **The van Yperen contrast is not like-for-like and should be softened.** The football study's exposure was starting *organised football* (joining), while yours is first *sanctioned result* (lines 41–44, 70–72). A child who trains for four years before a first meet is a "late debutant" here but an early starter there. The Introduction builds the paper's central antagonism ("the two literatures predict opposite directions", lines 65–66) on constructs that differ exactly where your limitations section says they differ (lines 228–230). Keep the football study, but present the opposition as approximate and the construct gap as a reason your design answers a *different, registry-specific* question.

3. **Gender is a headline feature of the exposure but absent from the results.** Late debutants are much more often male (52.2 % female at 10–11 vs 42.0 % at 14–16, line 133–134, Table 1), and adolescent dropout in Nordic youth sport is strongly gendered. Yet no sex-stratified conversion, no sex × debut-age interaction, and no sex-specific retention are reported anywhere; the only sex result is a null exit HR in the pooled Cox (lines 160–161), which does not address conversion. At minimum: senior conversion by debut age and sex (even descriptively), and a sex × debut-age interaction test for H1, with sparse-data caveats. The Perspective's enthusiasm for teenage recruitment (lines 238–241) needs to say whether the late-entry channel is, in practice, largely a male channel — that changes its policy meaning.

4. **"In a federation whose teenage recruitment has halved over a decade" (lines 245–246) is an unsupported empirical premise.** Figure 1 shows *shares*, not counts; nothing in the manuscript shows teenage debut counts halving. Since this claim motivates the paper's most actionable conclusion, either substantiate it (absolute debut counts by age group and cohort are available for born 2001–2008, descriptively) or cite the companion study if it is established there, or delete it.

5. **The Perspective converts selection into strategy.** The paper's own resolution of the U is self-selection (lines 197–200), yet Perspective reads the 6.6 % late-entry conversion as a reason teenage recruitment is "worth real effort" and late entrants are "disproportionately productive" (lines 238–247). Recruited marginal entrants — adolescents who would *not* have walked in on their own — cannot be assumed to convert like self-selected ones; indeed the paper's logic predicts they will not. Reframe the three "usable facts" as descriptive planning parameters (expected churn and yield under the current entrant mix), not as expected returns to recruitment effort, and add one sentence on the average-vs-marginal distinction.

6. **Structural selection into debut age deserves a theme, even without data.** Debut age plausibly tracks geography (distance to meets, club calendars), club culture, and family resources; the covariates (modal district; study-athletes-per-club as club size, lines 99–101) are coarse, and the club-size proxy is endogenous to the study sample. I am not asking for new data; I am asking the limitations to name socioeconomic and structural access explicitly rather than only "motivation, prior training, or participation in other sports" (lines 203–205).

7. **The parental-decision claim is asserted, not shown.** "Entry at 10 is largely a parental and club decision made for children; entry at 16 is a decision adolescents make for themselves" (lines 197–199) is sociologically plausible and probably right — but it is presented as fact with no evidence or citation. Mark it as interpretation and anchor it in the youth-sport socialisation literature (as a theme), or soften.

### Minor comments

- Line 87: 865 athletes without registered sex are excluded; one sentence on who they are (presumably brief, early participants) and the likely direction of bias.
- Line 230–231: exit from the registry is rightly distinguished from exit from sport; please carry this into the Perspective — "no wrong age to start" (line 238) concerns athletics retention only, and says nothing about overall sport participation or physical activity.
- Keywords include "early specialisation" (line 76) although the exposure is explicitly not specialisation; consider "competition entry age" or "organised sport entry".
- Line 81: "which this study's design renders moot since it needs no marks" — the point is good, the tone is glib; rephrase.
- The ethics framing (lines 122–127, 252–255) is careful and appropriate for Norwegian conditions; stating the Sikt reference number would strengthen it.

**Recommendation: Major revision.**

---

## Reviewer 3 — Talent development / specialisation researcher:

### Summary

The empirical core — a complete national entry cohort of an individual sport, exact entry ages, delayed-entry survival, and a landmark test of history vs current engagement — is sound and genuinely novel; I know of no comparable population test in an individual sport. My difficulties are almost entirely with the framing. The manuscript positions itself as adjudicating between "two camps" (early-specialisation caution vs early-engagement advantage), but the exposure — age at first registered meet, with a median of one competition day — is a thin proxy for either construct. Several conclusions, especially in the Perspective, outrun what a selection-saturated association can carry. Most of my points require rewriting, not re-analysis.

### Major comments

1. **The "neither camp survives" framing tests predictions neither camp quite makes.** The consensus cautions ([1], cited at lines 39–40, 192–193) concern *specialised, high-volume, year-round* involvement — not whether a 10-year-old appears in a sanctioned meet once or twice (median debut-season exposure: one day; Table 1, lines 134–136). Conversely, the early-engagement position concerns accumulated engagement in the sport, which your late debutants may possess invisibly (prior training, other sports — acknowledged at lines 203–205, 228–230). So §4.2's claim that "the population data support neither as stated" (line 194) is true mainly because neither was stated *about this exposure*. Reframe: the study is a direct test of *entry timing into registered competition* — an administrable, policy-relevant variable — and an *indirect* commentary on the specialisation debate. The Introduction (lines 37–44) and §4.2 should be rewritten accordingly; at present the paper knocks down positions it has translated into a form their proponents would not sign.

2. **The U-shape needs mechanism symmetry.** The right arm (15–16, 17+) is persuasively explained by self-selection (lines 197–200, 176–179). The left arm — why debut at 10 beats 11–14 (Table 2: ORs 0.53–0.75) — is left unexplained. Offer candidate mechanisms: families with the strongest athletics attachment enrol at the first eligible age; 11–14 entrants may be samplers arriving from other sports with weaker athletics identity; club pathways (training groups formed at 10) may penalise mid-childhood joiners; relative-age dynamics at entry [8]. And state plainly that the whole U may be compositional — the exposure may carry no behavioural effect at all — which the Discussion gestures at (line 203) but the abstract's "U-shaped" headline does not convey. A formal non-linearity test would help here too.

3. **Policy claims must distinguish average from marginal entrants.** If late entrants convert at 6.6 % *because* they are self-selected, expanding teenage recruitment recruits from a different (less selected) pool, and the Perspective's implication that the late channel is high-yield (lines 238–241, 245–247) does not follow. One honest sentence — "these are yields of self-selected entrants; induced entrants may convert at lower rates, though the first-season support implication is unaffected" — would fix it. (I expect other reviewers to raise this; I want it fixed, not the Perspective deleted — the first-season-support conclusion, lines 241–243, is well supported and genuinely useful.)

4. **"Current engagement dominates history" is partly built into the design — say so.** In the H3 landmark model, competition days at 16–17 are plausibly a *mediator* of debut age (early debut → accumulated engagement → current volume), so attenuation of the debut coefficient when the mediator enters (0.87 → 0.97, lines 165–167) is the expected behaviour of a mediated exposure, not evidence that history "tells none of it" (line 244–245). Moreover, conditioning on survival to 17 invites index-event/collider selection: the "protective" 0.87 that appears only among survivors (and the U in the full cohort) is the classic signature. The prediction framing (lines 68–70) legitimately supports "starting age adds no *predictive* value at 17 given current volume" — but §4.4 and Perspective slide toward an etiological reading ("the system need not hold athletes' histories against them", line 221). Keep the prediction language strictly, and name mediation and index-event bias in limitations.

5. **Retention is not attainment — police the word "productive".** No performance data were used (by design, lines 79–81), so "late entrants are disproportionately productive" (line 246) can only mean productive *of senior participants*, not of performance level. The expertise literature you position against (lines 44–48, 224–226) is about elite attainment; the symmetric caveat — they cannot speak to retention, you cannot speak to attainment — should be explicit, or readers will take the U-shape as a statement about where champions come from.

6. **The duration-clock story is not monotone, and the exception is informative.** "Later starters leave faster" (§3.3 heading, line 150; abstract lines 26–28) is contradicted at debut 16: k = 1 retention 0.35 vs 0.26 at 15 and 0.34 at 14; k = 5: 0.06 vs 0.03–0.04 (Table 3). This reversal *supports* your self-selection account of the right arm and should be reported in §3.3 rather than left to the attentive reader of Figure 4. Relatedly — and here I part company with the manuscript's own emphasis (lines 111–113, 158–160) — I find the age-clock convergence (Figure 3) at least as policy-relevant as the duration table: from ~16 the system cannot tell debut groups apart. Consider giving convergence equal billing in the abstract rather than subordinating it.

### Minor comments

- Line 62–63: "entry age is … the first behavioural fact the registry records" — nice, but it is the first *registered* behavioural fact; prior training is invisible, as you acknowledge. Keep the phrasing honest.
- Engage, as a theme, the developmental-pathways literature on sampling vs specialising years when interpreting mid-childhood entrants (my comment 2) — currently the Discussion's only theoretical anchors are the two "camps".
- References [9] (under review) and [10] (in preparation) carry much of the framing ("third instalment", lines 215–222). Provide both to reviewers with the revision, and add one sentence distinguishing this paper's contribution from theirs — three registry papers with rotating exposures invites a salami question an editor will otherwise ask.
- Table 1: debut-season competition days by debut age are nearly identical (median 1) — worth one sentence: the *dose* at entry is flat, so debut age is not a proxy for entry intensity.
- Figure 3: note in the caption that curve segments before all groups have entered describe only the entered groups (standard delayed-entry caveat), since the visual invites comparison from age 10.

**Recommendation: Major revision** (with the explicit note that the required work is predominantly reframing and reporting, not new analysis; the data and design merit publication in this journal).

---

## Editor synthesis

**Convergent points (all three reviewers, or two with no dissent):**

1. **Define and, if necessary, repair the H3 landmark** (R1-1). The 546 = 546 coincidence must be explained; if the landmark condition is "any result at age ≥17", H3 must be re-estimated on a valid landmark. This is the single most consequential technical point.
2. **Correct overstated inference**: "significantly lower odds" at debut 13 (R1-2); add a formal non-linearity test behind the "U-shaped" headline (R1-2, R3-2).
3. **Substantiate or remove the "teenage recruitment has halved" premise** in Perspective (R2-4), and insert the average-vs-marginal caveat before drawing recruitment implications from self-selected conversion rates (R2-5, R3-3).
4. **Reframe the specialisation antagonism**: the exposure is entry into registered competition, not specialisation, and not the football study's "starting organised sport" (R2-2, R3-1). The Introduction and §4.2 need rewriting; the empirical sections do not.
5. **Tighten the retention-table construction**: per-k denominators, definition of "still competing", CIs (R1-4); report the debut-16 non-monotonicity in the text (R3-6).
6. **Resolve the 17+ sensitivity arithmetic and outcome overlap** (R1-3).
7. **Reporting hygiene**: STROBE flow diagram, covariate sets per model, exit-definition sentence, abstract direction of OR 0.87, the 2.0/2.1 % inconsistency, reference [12] placement (R1).

**Points of disagreement:**

- *Gender*: R2 asks for sex-stratified conversion and an interaction test as a condition; R1 would accept descriptive stratification with sparse-data caveats (546 events limit categorical interactions). The revision should do the descriptive split and the single interaction test, and resist finer stratification.
- *Which clock carries H2*: the manuscript (and R1) treat the duration-clock table as primary; R3 argues the age-clock convergence is equally policy-relevant and should be promoted, not subordinated. Both can be accommodated: keep the duration table as primary evidence, but give convergence parallel standing in abstract and Perspective.
- *Perspective*: R2 wants it rewritten as descriptive planning parameters; R3 wants it largely retained with explicit marginal-entrant and attainment caveats. A middle course — retain the three facts, add the two caveats, delete or substantiate "halved" — should satisfy both.

**Overall assessment:** All three reviewers regard the data source, the no-left-truncation design, and the transparency (pre-committed plan, blending caveat, selection acknowledged) as substantial strengths, and none questions the core descriptive findings. The required revisions are a mix of one potentially substantive re-analysis (landmark definition), several reporting repairs, and a significant reframing of Introduction, §4.2 and Perspective.

**Editorial decision: Major revision.** A detailed point-by-point response is expected; no new data collection is required.
