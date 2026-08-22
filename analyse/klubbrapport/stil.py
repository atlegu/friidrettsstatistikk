"""Felles stilark for klubbrapportene.

Skjermvisning og utskrift i samme fil. Merk fontvalget under @media print:
macOS-systemfonten kan Chrome bare bygge inn som Type 3-font, som rendres
med striper i mange PDF-lesere og ikke lar seg søke i.
"""

STILARK = """
:root { --bg:#fbfbfa; --fg:#1a1a19; --mut:#6b6b68; --line:#e4e4e1;
        --card:#fff; --acc:#0f5c4a; --nest:#8a8a86; --annen:#a8571c; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#151514; --fg:#eeeeec; --mut:#9a9a96; --line:#2c2c2a;
          --card:#1d1d1b; --acc:#63c6ab; --nest:#86867f; --annen:#e0925a; }
}
* { box-sizing:border-box; }
body { margin:0; padding:2rem 1.25rem 4rem; background:var(--bg); color:var(--fg);
  font:15px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif; }
.wrap { max-width:1080px; margin:0 auto; }
h1 { font-size:1.6rem; margin:0 0 .25rem; letter-spacing:-.02em; }
.sub { color:var(--mut); margin:0 0 1.75rem; }
.panel { background:var(--card); border:1px solid var(--line); border-radius:10px;
  padding:1rem 1.25rem; margin-bottom:1.5rem; }
.sumtab { border-collapse:collapse; }
.sumtab th,.sumtab td { padding:.35rem 1.5rem .35rem 0; text-align:left; }
.sumtab thead th { color:var(--mut); font-weight:500; font-size:.82rem;
  text-transform:uppercase; letter-spacing:.04em; }
.tools { display:flex; gap:.75rem; flex-wrap:wrap; align-items:center; margin-bottom:1.25rem; }
input,select { font:inherit; padding:.5rem .7rem; border:1px solid var(--line);
  border-radius:8px; background:var(--card); color:var(--fg); }
input { flex:1; min-width:220px; }
.count { color:var(--mut); font-size:.88rem; }
.ath { background:var(--card); border:1px solid var(--line); border-radius:10px;
  padding:1rem 1.25rem 1.25rem; margin-bottom:1rem; }
.ath h3 { margin:0; font-size:1.05rem; display:inline; }
.meta { display:flex; gap:.9rem; flex-wrap:wrap; color:var(--mut);
  font-size:.85rem; margin:.2rem 0 .5rem; }
.badges { display:flex; gap:.4rem; flex-wrap:wrap; margin-bottom:.75rem; }
.badge { font-size:.78rem; padding:.15rem .5rem; border-radius:999px;
  background:color-mix(in srgb,var(--acc) 14%,transparent); color:var(--acc); }
.badge.null { background:transparent; color:var(--mut); border:1px dashed var(--line); }
.ath table { width:100%; border-collapse:collapse; }
.ath thead th { font-size:.75rem; text-transform:uppercase; letter-spacing:.04em;
  color:var(--mut); font-weight:500; text-align:left; padding:.3rem .5rem;
  border-bottom:1px solid var(--line); }
.ath tbody th { text-align:left; font-weight:500; padding:.45rem .5rem;
  border-bottom:1px solid var(--line); vertical-align:top; width:32%; }
.ath td { padding:.45rem .5rem; border-bottom:1px solid var(--line);
  vertical-align:top; font-variant-numeric:tabular-nums; }
.n { display:inline-block; font-size:.7rem; color:var(--mut); border:1px solid var(--line);
  border-radius:4px; padding:0 .3rem; margin-bottom:.15rem; }
.best { font-weight:600; }
.nest { color:var(--nest); font-size:.88rem; }
.tom { color:var(--nest); }
.v { font-size:.72rem; color:var(--mut); margin-left:.3rem; }
.tabellnote { color:var(--mut); font-size:.83rem; margin-top:.4rem; }
.ath td.annen { background:color-mix(in srgb,var(--annen) 13%,transparent);
  box-shadow:inset 3px 0 0 var(--annen); }
.klubb { font-size:.72rem; color:var(--annen); margin-top:.2rem; font-weight:500; }
.badge.annen { background:color-mix(in srgb,var(--annen) 16%,transparent); color:var(--annen); }
.nykommer { color:var(--annen); font-weight:500; }
.annen-t { color:var(--annen) !important; }
.avgang th { font-weight:500; padding-right:1.5rem; }
.legend { display:flex; gap:1.25rem; flex-wrap:wrap; align-items:center;
  color:var(--mut); font-size:.83rem; margin:.25rem 0 1.25rem; }
.swatch { display:inline-block; width:.85rem; height:.85rem; border-radius:3px;
  vertical-align:-2px; margin-right:.35rem;
  background:color-mix(in srgb,var(--annen) 30%,transparent);
  box-shadow:inset 2px 0 0 var(--annen); }
.stipend { display:inline-block; background:var(--acc); color:var(--bg);
  font-weight:700; font-size:.78rem; border-radius:4px; padding:0 .38rem;
  vertical-align:2px; margin-left:.15rem; }
.stipend-belop { color:var(--acc); font-weight:600; font-size:.92em;
  white-space:nowrap; }
.kat { border:1px solid var(--line); border-radius:4px; padding:0 .35rem;
  font-size:.75rem; }
h2.gruppe { font-size:1rem; margin:1.75rem 0 .6rem; letter-spacing:-.01em;
  display:flex; gap:.6rem; align-items:baseline; flex-wrap:wrap; }
h2.gruppe span { font-weight:400; font-size:.83rem; color:var(--mut); }
.varsel { border-left:3px solid #c98a2b; }
.varsel ul { margin:.5rem 0 0; padding-left:1.2rem; }
.varsel code { font-size:.85em; padding:0 .25rem; border-radius:3px;
  background:color-mix(in srgb,var(--fg) 8%,transparent); }

@media print {
  @page { size:A4 portrait; margin:11mm 10mm; }
  :root { --bg:#fff; --fg:#111; --mut:#555; --line:#ccc; --card:#fff;
          --acc:#0f5c4a; --nest:#666; --annen:#8a4512; }
  /* macOS-systemfonten kan Chrome bare bygge inn som Type 3-font, som rendres
     med striper i mange PDF-lesere. Helvetica Neue blir ordentlig TrueType. */
  body { padding:0; font-size:8.5pt; line-height:1.2;
         font-family:"Helvetica Neue",Helvetica,Arial,sans-serif;
         -webkit-print-color-adjust:exact; print-color-adjust:exact; }
  .wrap { max-width:none; }
  .tools { display:none; }
  .ath, .panel { break-inside:avoid; page-break-inside:avoid; box-shadow:none; }
  .ath { margin-bottom:.3rem; padding:.35rem .55rem .4rem; border-radius:5px; }
  .ath h3 { font-size:.9rem; margin-right:.6rem; }
  h1 { font-size:1.25rem; }
  h2.gruppe { margin:.9rem 0 .35rem; break-after:avoid; page-break-after:avoid; }
  .ath header { display:block; margin-bottom:.15rem; }
  .meta, .badges { display:inline-flex; gap:.55rem; margin:0; vertical-align:middle; }
  .badge { padding:0 .35rem; font-size:.72rem; background:#e6efec; }
  .badge.annen { background:#f6e6d8; }
  /* Hver rute på én linje: starter · beste / nr. 2 / nr. 3 */
  .ath td .n, .ath td .best, .ath td .nest {
    display:inline; margin:0; font-size:inherit; }
  .ath td .n { border:0; color:var(--mut); padding:0; }
  .ath td .n::after { content:' · '; }
  .ath td .nest::before { content:' / '; color:var(--nest); }
  .ath td, .ath tbody th { padding:.1rem .4rem; vertical-align:baseline; }
  .ath thead th { padding:.05rem .4rem; font-size:.68rem; }
  .ath tbody th { width:28%; }
  .v { font-size:.9em; }
  .ath td.annen { background:#f6e6d8; box-shadow:inset 2px 0 0 var(--annen); }
  .swatch { background:#f0d8c2; box-shadow:inset 2px 0 0 var(--annen); }
  .legend { margin:.2rem 0 .6rem; font-size:.75rem; }
}
@media (max-width:640px) { .ath tbody th { width:auto; } body { padding:1rem .75rem 3rem; } }
"""
