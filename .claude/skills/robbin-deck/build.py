#!/usr/bin/env python3
"""
Robbin deck builder.

Assembles a full-screen presentation from a slides fragment + the shared
design system, then emits two files:
  - presentation.html          (references assets by relative path)
  - presentation_preview.html  (single file; images inlined as data URIs)

Usage:
  python build.py SLIDES.html [--title "..."] [--assets DIR] [--out-dir DIR]

SLIDES.html must contain ONLY the <section class="slide ...">...</section>
blocks (no <html>/<head>/<body>). The first slide should be the cover and
carry `class="slide cover5 active" id="cover"`. See SKILL.md for snippets.
"""
import argparse, base64, mimetypes, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

CHROME = """<div class="deck-mark-mini"><img src="robbin-bird-black.svg" alt="Robbin"></div>
<div class="slide-counter"><span class="current">01</span><span style="opacity:0.4"> / {total:02d}</span></div>
<div class="deck-meta">
  <button class="nav-btn" id="prevBtn">&larr; anterior</button>
  <div class="progress"><div class="progress-fill" id="progressFill"></div></div>
  <button class="nav-btn" id="nextBtn">próximo &rarr;</button>
</div>
<div class="deck" id="deck">
{slides}
</div>"""

HEAD = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800;900&family=Geist+Mono:wght@400;500;600;700&display=swap" rel="stylesheet" />
<style>
{css}
</style>
</head>
<body>
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slides", help="HTML fragment with the <section> slides")
    ap.add_argument("--title", default="Robbin — Apresentação")
    ap.add_argument("--lang", default="pt-BR")
    ap.add_argument("--assets", default=None, help="extra assets dir (logos, photos, cards). Defaults to the slides file's folder")
    ap.add_argument("--out-dir", default=None, help="where to write output (default: slides file folder)")
    a = ap.parse_args()

    slides = open(a.slides, encoding="utf-8").read()
    out_dir = a.out_dir or os.path.dirname(os.path.abspath(a.slides)) or "."
    user_assets = a.assets or os.path.dirname(os.path.abspath(a.slides)) or "."

    framework = open(os.path.join(ASSETS, "framework_css.css"), encoding="utf-8").read()
    custom = open(os.path.join(ASSETS, "custom_css.css"), encoding="utf-8").read()
    nav = open(os.path.join(ASSETS, "nav.js"), encoding="utf-8").read()

    total = slides.count("<section")
    body = CHROME.format(total=max(total, 1), slides=slides)
    html = (HEAD.format(lang=a.lang, title=a.title, css=framework + "\n" + custom)
            + body + "\n<script>\n" + nav + "\n</script>\n</body>\n</html>\n")

    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "presentation.html")
    open(out, "w", encoding="utf-8").write(html)
    print("wrote", out, len(html), "bytes |", total, "slides")

    # --- self-contained preview: inline every src="file" that exists ---
    def datauri(path):
        mime = "image/svg+xml" if path.endswith(".svg") else (mimetypes.guess_type(path)[0] or "application/octet-stream")
        return "data:%s;base64,%s" % (mime, base64.b64encode(open(path, "rb").read()).decode())

    preview = html
    for ref in sorted(set(re.findall(r'src="(?!data:|https?:)([^"]+)"', html))):
        for base in (user_assets, ASSETS, out_dir, "."):
            p = os.path.join(base, ref)
            if os.path.isfile(p):
                preview = preview.replace('src="%s"' % ref, 'src="%s"' % datauri(p))
                break
        else:
            print("  ! asset not found, left as-is:", ref)
    pout = os.path.join(out_dir, "presentation_preview.html")
    open(pout, "w", encoding="utf-8").write(preview)
    print("wrote", pout, len(preview), "bytes")


if __name__ == "__main__":
    main()
