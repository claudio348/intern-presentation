# Robbin credit-deck components

Every component below is a live, copyable pattern from `example_deck.py` (the full
generator for the institutional credit/FIDC deck). Charts are hand-built SVG in
Python f-strings — no chart libraries — so they match the monochrome design system
exactly and never pull a runtime dependency. Copy the Python helper + its CSS +
the slide markup together; they're designed as a unit.

Conventions shared by all components:
- Colours: ink `#0C0C0C`, paper `#FAFAFA`, one functional red `#C0143C` (accent /
  deductions), grays `#9a9a9a`/`#5A5A5A`. Never introduce a second hue.
- Fonts: Geist (sans) + Geist Mono. Labels/eyebrows are mono, uppercase, letter-spaced.
- Every content slide is `<section class="slide theme-light vcenter" data-num="NN">`
  with a `.chapter-mark`, a `.slide-head` (kicker + h1 + sub), the body, and a
  bottom `.illus` source line. `data-num` / `chapter-num` are auto-sequenced at build.
- A filling body element uses `flex:1 1 auto; min-height:0` so it grows to the
  footer-safe area (see "Footer safe-area" — critical, easy to get wrong).

---

## Table of contents
1. Build pipeline & file layout
2. Footer safe-area (READ THIS — prevents overlap with page number/source)
3. Business model — 3-stakeholder triangle
4. Cedentes & sacados — logo wall + metric cards
5. KPI board (prazo / taxa / giro / inadimplência)
6. Vintage / safra CDR line chart
7. Economics — NIMAL waterfall
8. Term sheet card (dark slide)
9. WIP placeholder card
10. Carteira bar chart (pre-FIDC vs FIDC-live)
11. Logo manifest

---

## 1. Build pipeline & file layout

The deck is generated, not hand-written:

```
make.py            # emits slides.html (a fragment of <section> slides + a <style> STYLE block)
_intro_*.html      # optional imported slide fragments, spliced at a <!--INTRO--> marker
logos/*.png        # partner logos (see manifest)
build.py           # wraps the fragment into presentation.html + presentation_preview.html
export_pdf.js      # renders each slide to one landscape PDF page (Playwright + pdf-lib)
```

Build + export commands:
```bash
python3 make.py \
  && python3 build.py slides.html --title "..." --out-dir . \
  && node export_pdf.js   # -> presentation.pdf
```
- `presentation.html` references logos by relative path (keep `logos/` beside it).
- `presentation_preview.html` inlines every image as a data URI — a single portable
  file that opens in a browser with animations. Send this one for viewing.
- Fonts load from Google Fonts (Geist) via CDN in `build.py`'s HEAD.

The `STYLE = """<style> ... </style>"""` block at the top of `make.py` holds all the
component CSS below; `SLIDES = STYLE + f"""...sections..."""`.

---

## 2. Footer safe-area — READ THIS

The framework has a `@media (max-width: 1500px)` rule that forces
`.slide { padding: 2.5vh 3.5vw 3.5vh !important; }`. At common viewports (≤1500px,
incl. the PDF render at 1280) that shrinks the bottom padding and full-height content
overlaps the fixed **page counter** (bottom-right) and the **source `.illus`** (bottom-left).

Fix, already in the STYLE block — keep it:
```css
.slide.vcenter { justify-content:flex-start; padding-top:5.5vh !important; padding-bottom:6.5vh !important; }
.slide.vcenter > * { flex-shrink:0; }
```
If a dense page still overflows into the footer, trim that page's content
(card padding, gaps, font clamps) until the filling body ends ≥6.5vh from the bottom —
don't reduce the padding. Verify by rendering and checking the last content child's
`getBoundingClientRect().bottom` clears the counter/illus.

---

## 3. Business model — 3-stakeholder triangle

When to use: explain the model as a relationship between three parties (Robbin, the
Âncora/Indústria, and the PME/sacado) rather than a linear flow. Robbin sits at the
top (dark, the hero), the two market sides at the bottom, connected by an SVG triangle
with labeled edges. Fragment: `_intro_business.html`; CSS class prefix `.biz3-`.

Markup:
```html
<div class="biz3-stage reveal">
  <svg class="biz3-links" viewBox="0 0 1000 520" preserveAspectRatio="none">
    <line x1="500" y1="92" x2="150" y2="446" stroke="#0C0C0C" stroke-width="1.3"/>
    <line x1="500" y1="92" x2="850" y2="446" stroke="#0C0C0C" stroke-width="1.3"/>
    <line x1="150" y1="446" x2="850" y2="446" stroke="#9a9a9a" stroke-width="1.3" stroke-dasharray="6 6"/>
  </svg>
  <div class="biz3-node robbin"><img class="b3-robbin" src="assets/robbin-logo-white.svg" alt="Robbin">
    <span class="b3-tag light">A plataforma de crédito</span><p>Origina, faz <b>underwriting</b> e concede o crédito.</p></div>
  <div class="biz3-node anchor"><div class="b3-ic"><svg viewBox="0 0 24 24"><path d="M3 21h18M6 21V7l6-3 6 3v14M10 21v-4h4v4"/></svg></div>
    <span class="b3-tag">Parceiro · distribuição</span><h4>Âncora / Indústria</h4><p>Traz sua base de <b>PMEs</b> e co-branda o cartão.</p></div>
  <div class="biz3-node pme"><div class="b3-ic"><svg viewBox="0 0 24 24"><path d="M4 9 h16 M4 9 l1.3 -4 h13.4 l1.3 4 M5 9 v11 h14 V9 M10 20 v-6 h4 v6"/></svg></div>
    <span class="b3-tag">Cliente final</span><h4>PME · sacado</h4><p>Toma <b>crédito no PIX Parcelado</b>.</p></div>
  <div class="biz3-edge e-left">co-brand + dados</div>
  <div class="biz3-edge e-right">crédito no PIX Parcelado</div>
  <div class="biz3-edge e-bottom">relação âncora–PME</div>
</div>
```
CSS: copy the block under `/* business model — 3-stakeholder triangle */` in
`example_deck.py`. Nodes are `position:absolute` (robbin top-center, anchor
bottom-left, pme bottom-right); the SVG lines sit behind (`z-index:0`) and the edge
labels are pills centered on each line. The dashed bottom edge signals the pre-existing
âncora↔PME relationship; solid edges are Robbin's active role.

---

## 4. Cedentes & sacados — logo wall + metric cards

When to use: show who originates (partner/anchor brands = cedentes) and who borrows
(PMEs = sacados), with a uniform partner logo wall and a row of borrower KPIs. CSS
prefix `.cs-`. Full-width stacked layout: label + `.cedente-wall` (grid of `.cd`
cards) on top, label + `.cs-metrics` (grid of `.cs-metric`) below.

Uniform logo sizing is essential — brand wordmarks have wildly different aspect
ratios, so fix a box and `object-fit:contain`:
```css
.cedente-wall { display:grid; grid-template-columns:repeat(4,1fr); gap:1.1vw; flex:1 1 auto; min-height:0; }
.cd img { width:clamp(92px,9vw,128px); height:clamp(24px,2.4vw,34px); object-fit:contain; }
```
For a monochrome wall add `filter:grayscale(1); opacity:.6;` on `.cd img`; for a
colour wall drop the filter (colour reads better when logos are the point).
Metric card = `.cs-metric` with `.csm-k` (mono label) / `.csm-v` (big number, with
`<em>` unit) / `.csm-s` (descriptor). Copy the `/* cedentes & sacados */` CSS block.

---

## 5. KPI board (prazo / taxa / giro / inadimplência)

When to use: a page of headline credit KPIs. A short bold lede + a single row of large
numbers, each with a mono label, a big value with a small `<em>` unit, and a
descriptor. No charts, no sparklines — the numbers are the design. CSS prefix `.giro-`.

```python
def _gstat(k, v, u, sub):
    return (f'<div class="giro-stat"><div class="gk">{k}</div>'
            f'<div class="gv">{v}<em>{u}</em></div><div class="gs">{sub}</div></div>')
block = ('<div class="giro-wrap"><div class="giro-lede reveal">Carteira curta, de <span class="accent">giro rápido</span>.</div>'
    '<div class="giro-stats five reveal" data-stagger>'
    + _gstat("Prazo médio","3,5","meses","parcelas médias por contrato")
    + _gstat("Taxa média","38,6%","a.a.","yield ponderado pelo principal")
    + ... + '</div></div>')
```
`.giro-stats` is a grid; add class `five` for a 5-column variant (shrinks the number
font). Each `.giro-stat` has a `border-top:2px solid #0C0C0C`. Keep any rate here equal
to the yield used on the Economics page — inconsistent headline numbers get noticed.

---

## 6. Vintage / safra CDR line chart

When to use: prove underwriting improved over time — one line per origination cohort
(safra), plotted over months-on-book (MOB); newer safras should sit lower. Real data
lives in the `cdr` / `vint_series` dicts; `vintage_chart()` draws it. Endpoint labels
(`Safra · value% · era`) are de-cluttered with a min-gap pass. Copy `vintage_chart()`
and `vint_series` from `example_deck.py`. Monochrome grayscale ramp for the lines
(`#CFCFCF → #0C0C0C`, newest darkest + a dot). Axis is drawn as two lines (no
gridlines). Annotate credit-policy milestones in the legend/eras, not as vertical
lines (policies are origination-time events, not MOB events).

---

## 7. Economics — NIMAL waterfall

When to use: bridge from gross yield down to net margin after losses. A waterfall of
totals (ink bars, `pos="top"`) and deductions (red bars, `pos="bot"`), connected by
thin gray levels. Copy `wf_steps` + `wf_levels` + `waterfall()`.

```python
wf_steps = [("Yield",0,38.6,"#0C0C0C","38,6%","top"),
            ("Funding Costs (All-in)",15.8,38.6,"#C0143C","−22,8%","bot"),
            ("NIM",0,15.8,"#0C0C0C","15,8%","top"),
            ("Credit Losses",11.22,15.8,"#C0143C","−4,58%","bot"),
            ("NIMAL",0,11.22,"#0C0C0C","11,2%","top")]
wf_levels = [38.6,15.8,15.8,11.22]   # connector level between bar i and i+1
```
Each step is `(label, y0, y1, color, value_text, "top"|"bot")`; a deduction spans from
the running level down to the next. Set `ymax` in `waterfall()` a touch above the tallest
bar (~44 here) for label headroom. For a placeholder deck, set the value texts to
`"TBD"` / `"−TBD"` and keep illustrative bar geometry.

---

## 8. Term sheet card (dark slide)

When to use: an indicative term sheet on a closing/Q&A slide. A dark card with a gold
hero band for the headline economics (rate + amount + tenor) and clean rows for the
rest. CSS prefix `.ts-`; gold accent `#E9C75A` / `#C9A227` is the ONE exception to the
monochrome rule (kept small, for the "indicative" tag + rate). Copy the `.ts-*` CSS.

```html
<div class="ts-card reveal">
  <div class="ts-head"><span class="ts-title">Term sheet</span><span class="ts-tag">indicativo · ilustrativo</span></div>
  <div class="ts-sub">Nota comercial garantida pela cota subordinada do FIDC</div>
  <div class="ts-hero">
    <div class="ts-hero-main"><span class="ts-hero-k">Remuneração</span><span class="ts-hero-v">CDI <span>+ 6,5%</span> <i>a.a.</i></span></div>
    <div class="ts-hero-side"><div><span class="k">Montante</span><span class="v">R$ 10M</span></div>
      <div><span class="k">Prazo</span><span class="v">40 meses</span></div></div>
  </div>
  <div class="ts-rows">
    <div class="ts-row"><span class="k">Instrumento</span><span class="v">Nota comercial</span></div>
    <div class="ts-row"><span class="k">Garantia</span><span class="v">Cessão fiduciária da cota subordinada · <b>150% sobre o principal</b></span></div>
    ...
  </div>
  <div class="ts-foot">Termo meramente ilustrativo · não vinculante</div>
</div>
```
Lives on a `theme-dark closing2 has-ts` slide (split layout: Q&A on the left, card on
the right) — see the closing slide in `example_deck.py`.

---

## 9. WIP placeholder card

When to use: a page whose data isn't final yet — keep the title/position in the deck
but show a clean "Work in progress" card instead of half-baked numbers. Never invent
figures to fill a slide; a labeled WIP card is more honest and reads fine to investors.
CSS prefix `.wip-`.
```html
<div class="wip-wrap reveal"><div class="wip-card">
  <div class="wip-badge">Work in progress</div>
  <div class="wip-title">Título da página</div>
  <p class="wip-sub">Uma linha sobre o que está sendo consolidado.</p>
</div></div>
```

---

## 10. Carteira bar chart (pre-FIDC vs FIDC-live)

When to use: monthly outstanding balance where a regime change (e.g. FIDC go-live)
should read at a glance. `portfolio_total_bars()` draws gray bars before the cutoff
index and fully-black bars from it onward, with a dashed divider + "FIDC ativo →"
label and a shaded region. Copy the function + `bnpl_labels`/`bnpl_carteira`/
`BNPL_FIDC_IDX`. Same pattern generalizes to any before/after cutoff.

---

## 11. Logo manifest (`assets/logos/`)

Robbin marks (in `assets/`): `robbin-logo-white.svg` (for dark backgrounds),
`robbin-logo-black.svg`, `robbin-bird-black.svg` (icon).

Partner logos (`assets/logos/`), full-colour PNGs trimmed to their bounding box:
`intelbras.png`, `cantu.png` (CANTU INC — the "pay" badge removed), `chillibeans.png`,
`moura.png`, `gerdau.png`, `malwee.png`, `votorantim.png`, `brinox.png`,
`xp.png`, `itau.png` (Itaú BBA), and `augme.svg` (monochrome wordmark).

Copy the ones you need next to the generated HTML (the example expects a `logos/`
folder beside `make.py`; the Robbin SVGs beside it too). If you add a new brand logo,
trim transparent/white padding first (Pillow: crop to the alpha bbox) so it sizes
uniformly in the wall.
