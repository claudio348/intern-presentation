---
name: robbin-deck
description: Build a Robbin-style presentation/pitch deck — full-screen HTML slides in the Robbin design system (Geist fonts, monochrome black & white, keyboard navigation, reveal animations). Use whenever the user wants to create, build, or restyle a Robbin presentation, deck, pitch, or slides.
---

# Robbin deck builder

Builds a single-file, full-screen HTML presentation in Robbin's house style:
black & white (monochrome), **Geist / Geist Mono** fonts, one slide per screen,
arrow-key navigation, progress bar, and staggered `reveal` entrance animations.

## How to build a deck

1. **Author the slides.** Create a `slides.html` fragment containing only the
   `<section class="slide ...">…</section>` blocks (no `<html>/<head>/<body>` —
   `build.py` adds those). Use the component snippets below. The first slide is
   the cover and must be `class="slide cover5 active" id="cover"`.
2. **Drop in assets.** Put any images the slides reference (logos, photos, card
   mockups) next to `slides.html`. The Robbin logos/bird already live in
   `assets/` and resolve automatically (`robbin-logo-black.svg`,
   `robbin-logo-white.svg`, `robbin-bird-black.svg`).
3. **Build:**
   ```
   python .claude/skills/robbin-deck/build.py slides.html --title "Robbin — Tema"
   ```
   This writes `presentation.html` (relative asset paths) and
   `presentation_preview.html` (single file, all images inlined as data URIs —
   send this one to the user to view).
4. **Present:** open in a browser. Navigate with ← / → (or PageUp/Down, Space,
   Home/End). It's full-screen 100vh; export to PDF via the browser print dialog
   (one slide per page).

## Design rules

- **Themes** (set on each `<section>`): `theme-light` (white bg / dark text),
  `theme-dark` (black bg / white text). Light slides already use darkened grays
  for readability — keep body copy in the provided component classes.
- Add **`vcenter`** to a slide to center its content vertically (recommended for
  most content slides).
- Keep prose in Portuguese or English consistently. Technical/proper terms
  (vibe code, skills, rules, Kafka, Landing/Prepared/Trusted/Delivery, role
  titles) are usually left untranslated.
- `chapter-num` is the section counter shown top-right; keep it sequential.
- Accent emphasis: wrap words in `<span class="accent">…</span>` (ink) or
  `<span class="muted">…</span>` (gray, light weight) inside an `<h1>`.

## Component snippets

**Cover** (animated black↔white flip, driven by nav.js):
```html
<section class="slide cover5 active" id="cover" data-num="01">
  <div class="cover5-badge">São Paulo · 2026</div>
  <div class="cover5-center">
    <img class="cover5-logo" src="robbin-logo-black.svg" alt="Robbin">
    <!-- optional: <div class="cover5-tag">Sua frase aqui.</div> -->
  </div>
  <div class="cover5-meta">Confidencial</div>
</section>
```

**Section header** (use at the top of any content slide):
```html
<div class="chapter-mark light-mark"><!-- drop "light-mark" on theme-dark slides -->
  <span class="chapter-num">01</span><span class="chapter-divider"></span><span class="chapter-year">Rótulo</span>
</div>
<div class="slide-head reveal">
  <h1>Título com <span class="accent">destaque.</span></h1>
  <p class="sub">Subtítulo opcional.</p>
</div>
```

**Feature / layer list** (numbered rows + optional badge; great for "who does what", architecture layers):
```html
<div class="layers reveal" data-stagger>
  <div class="layer"><!-- add class "hi" to highlight a row -->
    <span class="layer-num">01</span>
    <div>
      <h3>Título da camada</h3>
      <p>Descrição curta.</p>
      <div class="chips"><span>tag</span><span>tag</span></div><!-- optional -->
    </div>
    <span class="layer-badge">rótulo</span><!-- add class "strong" to invert -->
  </div>
</div>
```

**Card fan** (animated fanned product cards — put card images in your assets):
```html
<div class="pix-body reveal">
  <div class="pixfan">
    <!-- --rot = angle, --d = entrance delay, z-index = stacking (center highest) -->
    <div class="pcard" style="--rot:-40deg; --d:.15s; z-index:1;"><img src="CardA.png" alt=""></div>
    <div class="pcard" style="--rot:-20deg; --d:.30s; z-index:3;"><img src="CardB.png" alt=""></div>
    <div class="pcard" style="--rot:0deg;   --d:.45s; z-index:10;"><img src="CenterCard.png" alt=""></div>
    <div class="pcard" style="--rot:20deg;  --d:.40s; z-index:3;"><img src="CardC.png" alt=""></div>
    <div class="pcard" style="--rot:40deg;  --d:.55s; z-index:1;"><img src="CardD.png" alt=""></div>
  </div>
  <div class="pix-points" data-stagger>
    <div class="pix-point"><div class="pp-num">— 01</div><div class="pp-title">Ponto</div><div class="pp-desc">Texto.</div></div>
    <div class="pix-point"><div class="pp-num">— 02</div><div class="pp-title">Ponto</div><div class="pp-desc">Texto.</div></div>
  </div>
</div>
```

**Presenters** (two columns; round grayscale photos + experience logos):
```html
<div class="pres-grid reveal" data-stagger>
  <div class="pres">
    <div class="pres-top">
      <img class="pres-photo" src="Pessoa.jpeg" alt="">
      <div><div class="pres-name">Nome</div><div class="pres-role">Cargo</div></div>
    </div>
    <p class="pres-bio">Bio com <b>destaques</b>.</p>
    <div class="pres-exp"><span class="lbl">ex—</span><img src="logoA.png" alt=""><span class="lbl" style="margin-left:.5vw">now—</span><img src="robbin-logo-black.svg" alt="Robbin"></div>
  </div>
  <!-- segunda pessoa idem -->
</div>
```

**Vertical flow** (steps with a spine; on a `theme-dark` slide):
```html
<div class="flow reveal" data-stagger>
  <div class="flow-row">
    <div class="flow-spine"><div class="flow-dot"></div><div class="flow-line"></div></div>
    <div class="flow-card">
      <div class="flow-label">Você</div>
      <div class="flow-title">Faz algo</div>
      <div class="flow-bubble"><span class="flow-pill-inline">"frase"</span></div>
    </div>
  </div>
  <!-- claude step: use .flow-claude > .pill + .flow-steps > .flow-step (<b>n</b> label) -->
  <!-- final step: .flow-done with a .ic check icon -->
</div>
```

**3-column data flow** (sources → transformation → consumption):
```html
<div class="dataflow reveal">
  <div class="df-band"><span class="df-band-cell">Faixa A</span><span class="df-band-cell">Faixa B</span></div>
  <div class="df-cols">
    <div class="df-col"><div class="df-stage">Estágio</div><div class="df-item">Item</div></div>
    <div class="df-arrow">→</div>
    <div class="df-col"><div class="df-stage">Estágio</div><div class="df-layer"><b>Camada</b><i>nota</i></div></div>
    <div class="df-arrow">→</div>
    <div class="df-col"><div class="df-stage">Estágio</div><div class="df-item">Item</div></div>
  </div>
  <p class="df-note">Legenda em itálico.</p>
</div>
```

**Closing / Q&A** (dark, with grid + glow background):
```html
<section class="slide theme-dark closing2" data-num="08">
  <div class="closing2-bg"><div class="closing2-grid"></div><div class="closing2-glow"></div></div>
  <div class="closing2-inner">
    <div class="closing2-eyebrow reveal"><span>—</span><span>Discussão</span></div>
    <h2 class="closing2-line reveal"><span class="cl-row hi">Q&amp;A</span></h2>
    <div class="closing2-divider reveal"></div>
    <div class="closing2-logo reveal"><img src="robbin-logo-white.svg" alt="Robbin" style="height:46px;width:auto;"></div>
  </div>
</section>
```

**Jobs / grid** (2×N cards):
```html
<div class="vagas-grid reveal" data-stagger>
  <div class="vaga"><span class="vaga-num">01</span><div><h3>Cargo</h3><div class="vaga-meta">Linha 1<br>Linha 2</div><div class="vaga-tags"><span>tag</span></div></div></div>
</div>
<div class="vagas-cta reveal"><span class="pill">email@robbin.com.br</span><span class="dim">— chamada</span></div>
```

**Pyramid concept** (elegant 3D pyramid + tiered connectors). The pyramid is **3 equal bands** that line up with **3 equal tier rows** on the right (the `.pyr-wrap` is a fixed-height grid; the SVG and the `repeat(3,1fr)` rows share that height, so each connector sits at a band boundary). Faces use gradients (`url(#pyrL)` lit-left, `url(#pyrR)` dark-right) plus a soft ground shadow; `<small>` in `<h3>` gives a mono sub-label:
```html
<div class="pyr-wrap reveal">
  <div class="pyr-fig"><svg class="pyr-svg" viewBox="0 0 300 360" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="pyrL" x1="0" y1="0" x2="0.3" y2="1"><stop offset="0" stop-color="#5c5c5c"/><stop offset="1" stop-color="#2b2b2b"/></linearGradient>
      <linearGradient id="pyrR" x1="1" y1="0" x2="0.7" y2="1"><stop offset="0" stop-color="#2a2a2a"/><stop offset="1" stop-color="#0b0b0b"/></linearGradient>
      <filter id="pyrSh" x="-40%" y="-20%" width="180%" height="160%"><feGaussianBlur stdDeviation="6"/></filter>
    </defs>
    <ellipse cx="150" cy="356" rx="140" ry="9" fill="#000" opacity="0.12" filter="url(#pyrSh)"/>
    <polygon points="150,8 102.61,119 150,119" fill="url(#pyrL)"/><polygon points="150,8 150,119 197.39,119" fill="url(#pyrR)"/>
    <polygon points="150,125 100.05,125 53.95,233 150,233" fill="url(#pyrL)"/><polygon points="150,125 150,233 246.05,233 199.95,125" fill="url(#pyrR)"/>
    <polygon points="150,239 51.39,239 4,350 150,350" fill="url(#pyrL)"/><polygon points="150,239 150,350 296,350 248.61,239" fill="url(#pyrR)"/>
    <line x1="150" y1="8" x2="150" y2="350" stroke="#fff" stroke-opacity="0.05" stroke-width="1"/>
  </svg></div>
  <div class="pyr-right" data-stagger>
    <div class="pyr-tier"><h3>Top tier</h3><p>Description with <b>highlights</b>.</p></div>
    <div class="pyr-tier"><h3>Middle tier <small>optional sub-label</small></h3><p>Description.</p></div>
    <div class="pyr-tier"><h3>Base tier</h3><p>Description.</p></div>
  </div>
</div>
```

## Brand palette & logos

The deck is monochrome, **but charts/segments that encode anchor brands MUST use the
brand colours**, and brand slides use the brand **logos** (the card mockups in
`examples/`). Always reuse these — don't invent new colours per deck.

| Brand | Colour | Logo asset (card) |
|---|---|---|
| Cantu | `#5B2E91` | `Cantu.png` |
| Chilli Beans | `#E11D48` | `Chilli.png` |
| Juntos Somos Mais | `#8FA31E` | `JSM.png` |
| Moura | `#2563B0` | — |
| Malwee | `#1F7A3D` | `Malwee.png` |
| Brinox | `#0F8C8C` | `Brinox.png` |
| CredMoura | `#2B6FC0` | `Credmoura.png` |
| Robbin (card) | `#0C0C0C` | `Robbin.png` |
| Others / residual | `#0C2340` | — |

**Stacked share-over-time** (e.g. "Increasing diversification"): build an SVG of
stacked `<rect>` columns (one column per month, segments bottom→top in a fixed
brand order, heights = brand ÷ total × 100), label segments ≥ ~6.5% in white, and
pair it with a `.blegend` (brand colour chip + name). x-labels include the year
(`nov/24 … may/26`). See `examples/`-style charts generated in Python for the
exact geometry.

## Files in this skill

- `assets/framework_css.css` — Robbin pitch-deck design system (do not edit lightly).
- `assets/custom_css.css` — the reusable component styles above.
- `assets/nav.js` — keyboard/touch navigation, progress, cover flip, dark/light chrome.
- `assets/robbin-logo-black.svg`, `robbin-logo-white.svg`, `robbin-bird-black.svg`.
- `build.py` — assembles + inlines. Run it; don't hand-concatenate.
- `examples/slides.html` — a full 9-slide reference deck (cover, presenters,
  PIX card fan, architecture, Robbin Tools, two data slides, Q&A, jobs). Its
  card/photo images live in `examples/`. Build it to see everything working:
  ```
  python .claude/skills/robbin-deck/build.py .claude/skills/robbin-deck/examples/slides.html
  ```
  Copy a `<section>` from here as a starting point for new slides.

## Notes
- Slides are sized in `vh`/`vw`, so they scale to any screen; verify the tallest
  slides fit ~16:9 without clipping.
- The card fan uses real card images at a ~0.63 portrait ratio; keep them uniform.
- There's no headless browser in most sessions — review geometry in code and
  hand the user `presentation_preview.html` to eyeball.
