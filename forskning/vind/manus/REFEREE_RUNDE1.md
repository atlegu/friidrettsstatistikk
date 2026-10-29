# Simulated peer review, round 1 — "How much is the wind worth? Wind effects on sprint and horizontal-jump performance across age and ability in a national competition registry"

*Journal of Sports Sciences — simulated first-round review of the 29 October 2026 draft (main.pdf, printed line numbers 1–263). Three independent reviewers; line references are to the manuscript's printed line numbers.*

---

## Reviewer 1 — Biomechanics / sprint aerodynamics

### Summary

The manuscript estimates wind effects on sprint and horizontal-jump performance in a national registry spanning ages 10–34, using within athlete × season variation. The headline contributions — that absolute wind effects roughly double from seniors to children, that the elite literature describes the fast end of a gradient, and that the effect scales approximately with race duration — are credible, important, and to my knowledge new at population scale. The senior 100 m estimate (0.071–0.072 s per m/s, ll. 128–129) sits plausibly above the model-based elite values given the sample's ability level, and the headwind–tailwind asymmetry has the correct sign. However, the physical interpretation is in places loose or, in one instance, apparently inverted; the aerodynamically distinct bend events (200 m, 150 m) are treated as if their gauge readings meant the same thing as on the straight; and the asymmetry is oversold as "exactly" what drag physics predicts when the observed magnitudes are far larger than a steady-state v² mechanism yields. These are fixable, and most fixes would strengthen the paper.

### Major comments

1. **The mechanism offered for the declining percentage effect appears to have the wrong sign (ll. 189–191).** The Discussion states that the percentage effect is "still mildly declining [with age], consistent with a growing aerodynamic share at higher speeds." A growing aerodynamic share at higher speeds would make *faster* (older) athletes proportionally *more* wind-sensitive, i.e., it predicts a percentage effect that *rises* with age — the opposite of what you find (0.70 → 0.62 %/m/s on the men's 100 m, ll. 139–141). Your own Introduction sets up the correct candidate mechanisms (ll. 47–52): a fixed 1 m/s wind is a larger *relative* perturbation of airspeed for a slower runner (w/v larger), and children's higher surface-area-to-mass ratio works in the same direction; the growing drag share works against them. The data say the first two win. Please rewrite the mechanism sentence, and ideally go further: evaluate a Linthorne/Mureika-type quasi-physical model at your age-band mean speeds and compare predicted and observed absolute and percentage gradients. That calibration would turn a descriptive regularity into a validated mechanism and would materially elevate the paper.

2. **Bend events: the 200 m (and 150 m) gauge reading does not mean what the 60/100 m reading means, and the manuscript never engages with this.** Under standard protocol the 200 m wind is measured on the home straight only, over a fixed window; roughly half the race (the bend, where the wind vector is partly cross and partly opposing) is unmeasured. Your own numbers show the consequence: per second of race duration the effect is ~0.0062–0.0064 s per m/s per s on 60 m and 100 m, but only ~0.0042–0.0043 on 150 m and 200 m (computed from Tables 1–2). So the claim that effects "scaled approximately with race duration" (ll. 188–189) holds within event across age, but demonstrably *not* across events — the bend events fall ~30 % short, exactly as the gauge protocol predicts. Please (i) report the per-duration comparison explicitly, (ii) discuss what a "+1 m/s" reading operationally means per event, and (iii) state the gauge protocol used in Norway for the non-international distances (60 m, 80 m, 150 m) since these are not covered by the World Athletics measurement rules for 100/200 m.

3. **"Asymmetric in exactly the way drag physics predicts" (l. 223; also ll. 149–150, 191–192) overstates what the physics delivers.** The sign is right, but steady-state quadratic drag implies a head/tail slope ratio of roughly (2v+w)/(2v−w) ≈ 1.1–1.2 at sprint speeds, whereas you observe 1.50 (60 m: 0.072/0.048), 1.65 (100 m: 0.107/0.065) and 2.36 (200 m: 0.184/0.078) (ll. 146–148). A factor-2.4 asymmetry is not a pure drag signature; candidate contributors include wind-correlated selection (cancellations, DNS, who races in bad weather), pacing/technique in adverse conditions, and — on the 200 m, where the asymmetry is largest — the bend/gauge problem in comment 2. Please quantify the model-predicted asymmetry, compare, and soften "exactly" wherever it appears. Relatedly, report the quadratic terms for all events, not only the 200 m (l. 149).

4. **The "lower bound" reading is not valid for the jumps as written (ll. 99–100, 180–181, 213–214).** For sprints, the classical errors-in-variables argument (one gauge reading ≠ athlete-experienced wind → attenuation) is reasonable, though it assumes the measurement error is uncorrelated with the reading, which is an assumption, not a fact — gusting, gauge siting and venue-systematic errors can violate it. For the jumps, your own text establishes an *upward* force: the recorded wind belongs to the measured (best) attempt, and best attempts are more often wind-assisted (ll. 102–104, 150–153) — this is positive selection on the regressor, which inflates, not attenuates. Yet Section 3.7 and 4.3 state that *all* estimates are lower bounds. Please restrict the lower-bound claim to the sprints, state the net direction for jumps as ambiguous, and if possible bound the attenuation (e.g., from within-meet wind variance or a simple simulation with plausible gauge error).

### Minor comments

1. ll. 43–44 vs. ll. 130–131: the elite benchmark is "0.04–0.06 s per m/s" in the Introduction but "0.04–0.05" in Results. Harmonise.
2. l. 98: "a single gauge reading over 10–13 s" — the jump events use a substantially shorter measurement window than the sprints. State the window per event family; the attenuation argument differs accordingly.
3. Figure 1 / Table 3 cover sprints only in absolute units; Figure 2 includes jumps in percent. Add the jumps' absolute (cm) age gradients to a supplement — the contrast (youth jump effects are *smaller* in cm, opposite to sprints) is itself informative about mechanism and deserves a sentence.
4. Hurdles (ll. 155–162): the elevated 100/110 m hurdle point estimates are consistent with their longer race durations relative to flat races of the same distance. Test duration-proportionality here too; it would reinforce your exposure-time story.
5. ll. 58–60: "the only population-scale source of wind-measured sprint data on children" — soften to "to our knowledge" is already there, but consider "we are not aware of another"; other federations do meter some youth sprints.
6. Figures 3 and 4 show bars without confidence intervals; add them.

### Recommendation

**Major revision.** The empirical core looks sound and the question is genuinely new; the physical framing needs to be corrected (comment 1), scoped (comments 2–3) and made quantitative where it is currently rhetorical.

---

## Reviewer 2 — Sports statistics / econometrics

### Summary

This is a well-designed registry study with a sensible identification strategy (athlete × season fixed effects, month and round controls), pre-committed analysis plan, and unusually candid interpretive rules. The scale is impressive and most reported quantities reconcile across text and tables (I verified that the 433,566 analysed rows and 79,330 athlete-seasons match the table sums). However, I found several places where the text misstates its own tables — including the headline monotonicity claim, which is contradicted by one of the six series shown — and two methodological choices (clustering level; the construction of the H5 "legal window" quantity) that need rework or justification before the policy-relevant conclusions can stand. All of my major points are answerable in a response letter.

### Major comments

1. **The monotonicity claim is contradicted by Table 3 and Figure 1 (abstract l. 26; ll. 134–135).** You write that the absolute effect "declined monotonically with age in every sprint and both sexes." For 200 m girls/women, Table 3 reports 0.094 at 10–11 rising to 0.140 at 12–13 before declining — visibly non-monotonic in Figure 1 (right panel). The 10–11 cell is imprecise (CI 0.056–0.131), which is a legitimate defence, but then the claim must be stated as such (e.g., "monotonic from 12–13 onwards; the sparse girls' 10–11 cell is uninformative"). Also, the abstract and text report 0.144 s per m/s for boys 10–11 on 200 m (l. 26, l. 135) while Table 3 says 0.143 (0.095–0.192). Please run a full consistency pass between deposited estimation files, tables, text and abstract.

2. **The hurdles summary misdescribes Table 4 (ll. 157–159).** (a) "the youth 60 m hurdles at 0.062–0.063 s per m/s" — the four youth 60 m hurdle rows span 0.055–0.067; the quoted range covers only the 76.2 cm rows. (b) "point estimates in the 100/110 m hurdles 10–30 % above the flat references" — the actual ratios are −4 % (women's 84 cm), +6 % (boys' 91.4 cm), +20 %, +23 %, +30 % and +32 % (girls' 76.2 cm). Two are below or at the reference and one is above the stated range. Rewrite to match the table.

3. **Clustering level: wind is constant within a race, so the design-relevant cluster is the race (or at least the meet), not the athlete (ll. 86, 95–96).** With athlete clustering, the 60 m CI of ±0.001 s treats heat-mates' outcomes as independent draws against a shared wind reading — a textbook Moulton problem. You report meet clustering as a robustness ("essentially unchanged", l. 175–176), which is reassuring, but given how much of the paper's value lies in the precision of small contrasts (age bands, tertiles, head/tail slopes), please make meet- or race-clustered standard errors primary in Tables 2–4, or report both side by side, and state the p-values for the H4 slope-equality tests under that clustering.

4. **The meet-FE attenuation is framed one-sidedly (ll. 175–181; 213–215).** A 15–40 % drop under meet fixed effects is read entirely as errors-in-variables amplification ("meet effects absorb most between-race wind variation and leave less signal relative to gauge noise"). The observationally equivalent reading is that the month-dummy specification is inflated by between-meet confounding (venue, timing systems, weather-correlated meet composition). "Bracketing" (l. 180) is a fair stance, but it should be earned: report the within-meet share of wind variance per event, compute the implied reliability ratio under your preferred gauge-error assumption, and show it explains the observed attenuation. If it does, the EIV reading stands; if not, the primary estimate needs a more cautious label. Note also that the abstract quotes only the upper (month-dummy) estimates with no reference to the meet-FE range.

5. **H5 (the value of the legal window) is internally inconsistent with H4 and its denominator is under-specified (ll. 91–93, 164–173; Table 5).** (a) Table 5's seconds are exactly 2 × the symmetric slope (e.g., seniors 0.071 → 0.14 s). But H4 shows the tailwind-side slope is materially smaller than the symmetric slope (100 m: 0.065 vs. 0.082), so the advantage of +2.0 m/s over still air — a tailwind-side quantity by construction — is overstated; from the tailwind branch it would be ~0.13 s for senior men, and the curvature shrinks it further. Recompute Table 5 from the tailwind branch (or the quadratic fit) per age band, or justify the symmetric slope. (b) Define the SD denominator precisely: if the within-athlete-season SD includes wind-driven variance, the ratio is partly circular; if it is the residual SD after your model, say so. Also state how it is computed across cells: per-cell SDs at n = 2 are biased low by ~20 % (E[s] = c₄σ, c₄(2) ≈ 0.80), which would overstate SD shares precisely in thin cells — plausibly relevant to the anomalous 60 m 16–17 shares (1.24 and 1.48 SD). (c) Those same 60 m shares peak in the *oldest* band contesting the event, which complicates the abstract's general claim that "uniform wind rules make youth results systematically noisier measures of ability" (ll. 31–33). Scope that sentence to the events where it holds (the 100 m), as the Results text (ll. 171–173) already half-concedes.

6. **Ability tertiles are defined on the outcome (ll. 89–90).** Athlete-season mean performance includes the season's wind draw, so a wind-lucky season sorts an athlete into a better tertile, mechanically coupling the grouping variable to the regressor. Redefine ability on a wind-adjusted season mean or on the previous season's mark, and show the tertile gradient (0.087 vs. 0.078 on 100 m, ll. 142–143) survives.

7. **Selection and heaping diagnostics are incomplete.** (a) 9.5 % exact-zero readings is not "mild digit preference" (ll. 116–117) — under any continuous wind distribution at 0.1 m/s resolution this is several times the expected mass and suggests unoperated gauges recorded as 0.0; your exclusion robustness helps, so reword and lean on it. (b) Because ±2.0 m/s is a salient legality threshold with official discretion, show the density of readings around +2.0 (and around 0.0) and a robustness excluding a window around +2.0. (c) 18,692 outdoor rows lack wind (l. 80): characterise them — if small youth meets lack gauges, the youngest estimates come from systematically larger meets. (d) The period split "2011–2019 vs. 2021–2026" (l. 95) silently drops 2020; say why. (e) The abstract's "433,566 wind-measured results" (l. 21) is the analysed count, but only 315,288 rows lie in estimation cells (Table 1, "In cells ≥2"); make the estimating n explicit where the headline numbers are first quoted.

### Minor comments

1. Tables 3 and 5 overflow the right margin in the compiled PDF; the 18–19 and 20–34 columns are partially unreadable — ironically including the 0.084 that the abstract quotes. Use landscape or `\resizebox`.
2. Table S2 is cited (l. 176) but no supplement accompanied the PDF I reviewed; ensure it is uploaded.
3. Report statsmodels/pandas versions, not only Python 3.13 (ll. 96–97).
4. Figures 3 and 4 lack uncertainty intervals; Figure 2's legend overlaps the series.
5. "available from the author" (ll. 235–237) vs. table notes referring to "deposited" files (Tables 1, 3, 5): deposit code and aggregate estimation files in a public repository with a DOI, and cite it. JSS policy favours this, and your pre-committed plan deserves the visibility.
6. Justify the 20–34 "senior" ceiling given the registry includes masters; a sentence suffices.
7. A STROBE-style flow diagram of the 670,803 → 433,566 exclusions by reason and event would help; the claim that *indoor long jump* dominates exclusions (ll. 79–80) surprised me given the scale of indoor 60 m sprinting in Norway — please verify.
8. State whether month dummies are month or year × month (ll. 85, within-season form trends are the issue you flag at ll. 215–216).

### Recommendation

**Major revision.** Nothing here looks fatal, and the design is fundamentally right, but the monotonicity and hurdles misstatements must be fixed, the clustering and H5 reworked, and the meet-FE framing substantiated before the policy conclusions can be quoted.

---

## Reviewer 3 — Performance analysis, records and statistics governance

### Summary

This paper answers a question every national statistician and age-group records committee has quietly faced: the ±2.0 m/s convention was calibrated on senior elites, and nobody knew what it does lower down. The answer — the legal window is worth up to a full within-season SD for a 12–13-year-old on the 100 m, against half to four-fifths for seniors — is exactly the kind of quantity governance needs, and the recommendations are commendably proportionate (report wind, prefer wind-stratified comparisons, no rule changes demanded, ll. 202–205). The children's-data ethics paragraph is a model of its kind (ll. 106–112, 232–234), and the post-plan hurdles extension is honestly labelled in the text and table note (ll. 66–67; Table 4 note). My main requests are practical: the paper argues for age-graded corrections but does not hand the practitioner the tools, and the fairness claim should be made concrete at the level where it bites — seasonal lists and records.

### Major comments

1. **Deliver the correction apparatus you argue for (ll. 196–198).** The Implications state that "corrections should be age-graded" and that a senior-derived factor understates youth effects by up to half, but the reader cannot implement anything from the manuscript as it stands: Table 3 covers three sprints in symmetric per-m/s terms, head/tail asymmetry is only reported pooled across ages, and the jumps have no age-specific absolute table at all. Please add a supplementary correction table (event × sex × age band, head- and tailwind slopes separately, with CIs) and one worked example (e.g., a 12-year-old's 100 m of 13.80 at +1.8 m/s vs. a teammate's 13.95 at −0.5). Without it, the paper's most-cited artefact will be a number journalists round.

2. **Make H5 concrete where it matters: list and record reshuffling.** The SD-share framing (Table 5) is statistically elegant but abstract for federations. A short empirical illustration would land the fairness point: take one season's U14 and senior 100 m lists, apply your corrections, and report how many top-10/top-50 places change, or how many current age-group bests are wind-dependent in the sense that the correction exceeds the margin to the next mark. You have the registry; this is a day's work and would make Section 4.2 quotable in governance documents. Relatedly, the 60 m SD shares peaking at 16–17 (1.24/1.48, Table 5) show the SD framing is not uniformly "youth-unfavourable"; the list-reshuffling metric would be more robust to that wrinkle.

3. **Resolve the tension between "no rule changes" (l. 202) and "rules calibrated to the athletes least affected by wind" (ll. 224–225).** As written, the Conclusion insinuates more than the Implications are willing to recommend. If class-specific legality windows (e.g., a tighter tailwind limit for youth records) were considered and rejected, say so and say why (comparability, officiating burden, the children's-sport principle of not raising stakes); if they were not considered, the proportionate-scepticism stance should also appear in the Conclusion. As a records person I agree with your restraint — wind-stratified *lists* achieve most of the benefit at no officiating cost — but the paper should own the trade-off explicitly rather than gesture at it.

4. **Age-graded scoring tables are named as a motivation but never revisited (ll. 53–56).** If the wind effect per m/s differs by age while scoring tables treat a mark as wind-free within ±2.0, then scored comparisons across classes (common in youth multi-event and club competitions) inherit an age-dependent wind bias. One paragraph quantifying this — how many table points a +2.0 wind is worth at 12–13 vs. seniors on your estimates — would close the loop on your own motivation.

5. **Ethics and data availability: close two small gaps (ll. 106–112, 232–237).** (a) State the Sikt reference number and, in one sentence, confirm that no under-13 result appears in any ranked, listed or identifiable form in the paper or deposited outputs — this is what the children's-sport regulations actually protect. (b) The table notes cite "deposited" files while the Data availability statement says "available from the author"; for a paper recommending transparency to federations, deposit the aggregates and code publicly and cite the DOI. The hurdles post-plan labelling is exemplary; carry the same flag into the abstract (ll. 29–30), where the extension currently reads as pre-specified.

### Minor comments

1. Figure 5's axis labels are in Norwegian ("60 m hekk 68 cm"); translate for an international readership, and reconcile the figure (pooled sexes, 10 codes) with Table 4 (sex-specific, 12 rows) in the captions.
2. Define "zone" take-off variants at first mention for non-Nordic readers (ll. 72–74 is close; one clause on why youth use zones would do).
3. l. 227: "at no cost to anyone's race" is a nice line; make sure the preceding sentence supports it (corrections change lists, not races — say exactly that).
4. Abstract ll. 30–33: scope the final "systematically noisier" sentence to the 100 m, matching ll. 171–173.
5. Consider a one-sentence note on whether gauge coverage differs by meet level for the youngest classes (ties to the 18,692 missing-wind rows, l. 80), since list fairness depends on who gets measured at all.
6. The self-citation for talent evaluation (l. 56, l. 206) carries the whole talent-ID motivation; a broader anchor in the talent-identification/early-selection literature (as a theme) would be appropriate.

### Recommendation

**Minor revision** — the analysis is credible and the governance stance is sound; my requests are additions and clarifications rather than repairs, though I would regard the correction table (major comment 1) as a condition of acceptance.

---

## Editor synthesis

**Convergent points (raised independently by two or three reviewers):**

1. *Internal numerical consistency.* R2's catches are decisive for credibility: the monotonicity claim vs. the 200 m girls series (Table 3/Figure 1), 0.144 vs. 0.143, and the hurdles text ranges ("0.062–0.063"; "10–30 % above") that do not match Table 4. A full text-vs-deposited-files reconciliation pass is required.
2. *H4–H5 coherence.* R1 and R2 both note that the "+2.0 m/s window" is computed from the symmetric slope although the paper's own asymmetry results imply a smaller tailwind-side slope; Table 5 and the abstract's SD shares must be recomputed or defended, and the SD denominator defined (including small-cell bias).
3. *Scope of the "lower bound" claim.* R1 and R2 agree it cannot cover the jumps, where attempt selection pushes the other way; restrict to sprints and substantiate the attenuation argument quantitatively (within-meet wind variance / reliability ratio), which also addresses the meet-FE framing.
4. *Physics claims need calibration, not assertion.* R1's sign-inverted mechanism sentence (ll. 189–191) and the "exactly as drag physics predicts" asymmetry language (observed ratios 1.5–2.4 vs. ~1.1–1.2 from steady-state drag) require rewording at minimum; a quasi-physical model comparison would satisfy both R1 and R3's desire for authoritative correction factors.
5. *Transparency logistics.* All three reviewers flag the "deposited" vs. "available from the author" mismatch; deposit with DOI. Table 3/5 overflow and missing supplement must be fixed for re-review.

**Disagreements:**

- R2 wants meet-/race-clustered SEs and arguably meet-FE as (co-)primary; R1 is content with the month-dummy primary given the attenuation trade-off, provided the bracketing is quantified. The authors can satisfy both by reporting both specifications with design-consistent clustering side by side in the main tables.
- R3 reads the paper as essentially sound and asks for applied extensions (correction table, list-reshuffling illustration); R2 regards the H5 rework as a precondition for any applied table. Sequencing: fix H5 first, then build R3's deliverables on the corrected quantities.
- R1 would welcome a model-calibration exercise that R2 does not require; the editor considers it strongly desirable but not a condition.

**Overall recommendation: Major revision.** The question is novel, the data unique, and no reviewer doubts the central gradient. The revision must (i) repair the text–table inconsistencies, (ii) recompute or justify H5 with a precisely defined denominator and tailwind-side slopes, (iii) re-scope the lower-bound and monotonicity claims, (iv) fix the mechanism sentence and temper the asymmetry rhetoric, (v) report design-consistent clustering, and (vi) deposit the outputs. A response letter addressing each numbered point is expected; the prospects for acceptance after one serious round are good.
