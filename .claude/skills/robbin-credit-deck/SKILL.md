---
name: robbin-credit-deck
description: >-
  Build or edit a Robbin institutional credit / FIDC presentation — the
  monochrome (black & white) Robbin deck system with hand-built SVG charts,
  partner logos, and a set of ready-made credit slides. Use this skill whenever
  the user wants to create, extend, restyle, or add slides to a Robbin credit,
  FIDC, lending, or "operação de crédito" deck/pitch/apresentação — including
  when they ask for any of these specific pieces even without naming a deck:
  a business-model / "como a Robbin funciona" diagram, a cedentes & sacados
  (partners/borrowers) page, a credit KPI board (prazo, taxa, giro,
  inadimplência/PDD), a safra/vintage (CDR) chart, a NIM/NIMAL economics
  waterfall, an indicative term sheet, a portfolio/carteira chart, or when they
  hand over Robbin/partner brand logos (Intelbras, Cantu, Chilli Beans, Moura,
  Gerdau, Malwee, Votorantim, Brinox, XP, Itaú, Augme) to put in a presentation.
  Prefer this skill over generic slide tools for anything Robbin-credit-branded.
---

# Robbin credit-deck

This skill packages the full system used to build Robbin's institutional
credit/FIDC deck so it can be reused in other presentations: the Robbin
monochrome design system + build pipeline, all the brand logos, and a library of
ready-made, on-brand credit slides (business model, cedentes & sacados, KPI
board, safra/vintage chart, economics waterfall, term sheet, WIP card, carteira
chart). Charts are hand-built SVG in Python — no chart libraries — so everything
stays perfectly on-brand and dependency-free.

## What's in here

```
robbin-credit-deck/
├── SKILL.md                     # this file
├── build.py                     # fragment -> presentation.html + presentation_preview.html
├── export_pdf.js                # render each slide to one landscape PDF page
├── assets/
│   ├── framework_css.css        # Robbin design-system CSS (base)
│   ├── custom_css.css           # design-system extensions
│   ├── nav.js                   # keyboard nav + reveal animations
│   ├── robbin-logo-white.svg    # Robbin wordmark (for dark bg)
│   ├── robbin-logo-black.svg    # Robbin wordmark (for light bg)
│   ├── robbin-bird-black.svg    # Robbin icon mark
│   └── logos/                   # partner logos (see references/components.md §11)
└── references/
    ├── components.md            # the component library — READ THIS to build any slide
    └── example_deck.py          # the complete, working deck generator (canonical example)
```

## The mental model

A Robbin credit deck is **generated**, not hand-authored slide by slide. A single
`make.py` script builds an HTML fragment of `<section class="slide">` blocks plus a
`<style>` block, and `build.py` wraps it into the final files. This keeps charts
data-driven, on-brand, and easy to restyle globally. The fastest way to start is to
copy `references/example_deck.py` and edit it.

## How to use

### Building a new deck
1. **Copy the scaffold.** Copy `references/example_deck.py` to the working dir as
   `make.py`, copy `build.py` and `export_pdf.js` next to it, and copy the needed
   files from `assets/` (the `robbin-logo-*.svg` files and the `logos/` folder) so
   relative `src=` paths resolve.
2. **Edit `make.py`.** Keep or remove slides; pull in the components you need from
   `references/components.md` (each entry has the markup + CSS + any Python chart
   helper, copy them as a unit). Put chart CSS in the top `STYLE` block.
3. **Build + verify.**
   ```bash
   python3 make.py \
     && python3 build.py slides.html --title "Robbin — <título>" --out-dir . \
     && node export_pdf.js
   ```
   Then **render and look** before delivering (see Verifying).
4. **Deliver** the PDF (`presentation.pdf`, for reading) and
   `presentation_preview.html` (single self-contained file, opens in a browser with
   animations).

### Editing an existing Robbin credit deck
Find its `make.py` and edit the relevant slide/data in place, then rebuild and
re-export. Data arrays live near the top; slide markup lives in the big `SLIDES`
f-string near the bottom.

## Design rules (non-negotiable — this is the brand)

- **Monochrome.** Ink `#0C0C0C`, paper `#FAFAFA`, one functional red `#C0143C`.
  The only sanctioned extra hue is the small gold on the term-sheet card
  (`#E9C75A`). Partner logos may be full-colour on a "cedentes" wall or grayscale
  for a stricter look — pick one and be consistent.
- **Fonts:** Geist (sans) + Geist Mono. Eyebrows/labels are mono, uppercase, letter-spaced.
- **One line for subtitles.** Charts fill the page; the source `.illus` is pinned
  bottom-left and must never be overlapped — respect the footer safe-area
  (components.md §2, the single easiest thing to get wrong).
- **Titles at a consistent height** across content slides (the `vcenter` head).
- **Never invent numbers.** If data isn't confirmed, use the WIP card or a clearly
  labeled `TBD` — don't fabricate figures for an investor deck.
- Prefer Robbin/Brazilian-credit vocabulary the deck already uses: "PIX Parcelado"
  (not BNPL), "cedentes"/"sacados", "carteira", "safra", "cota subordinada",
  "NIM/NIMAL", "Funding". Say "rail", not "trilho".

## Verifying (do this before sending)

Charts are hand-built SVG, so always render and eyeball the changed slides. Use the
pre-installed Chromium via Playwright: load `presentation.html`, disable animations
(`.reveal,[data-stagger]>*{opacity:1!important;transform:none!important;animation:none!important}`),
activate the target slide by its `<h1>` text, screenshot it, and confirm no overflow
(`scrollHeight <= clientHeight`) and no collision with the bottom page-number/source.
`export_pdf.js` uses the same Chromium + `pdf-lib` (install once:
`npm install pdf-lib`) to merge per-slide pages into `presentation.pdf`.

## Where to go next

`references/components.md` is the working reference — it has a table of contents and,
for every component, the exact markup + CSS class names + Python helper to copy.
`references/example_deck.py` is the complete deck those components were taken from;
when in doubt, read how the example wires a component end-to-end.
