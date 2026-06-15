#!/usr/bin/env python3
"""Generate slides.html for the Robbin credit / FIDC institutional deck (EN).
All figures are ILLUSTRATIVE placeholders — replace with the real loan tape.
Charts are hand-built monochrome SVG to match the deck design system."""
import os

W, H = 680, 300
L, R, T, B = 54, 18, 16, 36
PW, PH = W - L - R, H - T - B


def x_at(i, xmax): return L + (i / xmax) * PW
def y_at(v, ymax): return T + PH - (v / ymax) * PH


def grid(ymax, yticks, xlabels=None, xmax=None):
    s = []
    for v in yticks:
        y = y_at(v, ymax)
        s.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="#E6E6E6" stroke-width="1"/>')
        s.append(f'<text x="{L-8}" y="{y+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="11" fill="#5A5A5A">{v:g}</text>')
    if xlabels:
        n = len(xlabels)
        for i, lab in enumerate(xlabels):
            x = x_at(i, xmax if xmax else (n - 1))
            s.append(f'<text x="{x:.1f}" y="{H-14}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="10.5" fill="#5A5A5A">{lab}</text>')
    return "\n".join(s)


def polyline(vals, ymax, xmax, color, width, dash=False, dots=False):
    pts = " ".join(f"{x_at(i,xmax):.1f},{y_at(v,ymax):.1f}" for i, v in enumerate(vals))
    d = ' stroke-dasharray="5 5"' if dash else ""
    out = [f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round"{d}/>']
    if dots:
        for i, v in enumerate(vals):
            out.append(f'<circle cx="{x_at(i,xmax):.1f}" cy="{y_at(v,ymax):.1f}" r="2.6" fill="{color}"/>')
    return "\n".join(out)


def chart(inner):
    return (f'<svg class="chart" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">\n'
            f'<line x1="{L}" y1="{T}" x2="{L}" y2="{T+PH}" stroke="#C8C8C8" stroke-width="1"/>'
            f'<line x1="{L}" y1="{T+PH}" x2="{W-R}" y2="{T+PH}" stroke="#C8C8C8" stroke-width="1"/>\n'
            + inner + '\n</svg>')


# ---------- CDR by vintage ----------
cdr = {
    "Vintage 2024-Q2": [0,.1,.35,.8,1.3,1.8,2.2,2.5,2.7,2.85,2.95,3.0,3.05],
    "Vintage 2024-Q3": [0,.08,.3,.7,1.1,1.5,1.85,2.1,2.3,2.45,2.55],
    "Vintage 2024-Q4": [0,.08,.28,.6,1.0,1.35,1.65,1.9,2.05],
    "Vintage 2025-Q1": [0,.07,.25,.55,.9,1.2,1.45],
}
cdr_colors = ["#BDBDBD", "#9A9A9A", "#6E6E6E", "#0C0C0C"]
cdr_inner = [grid(4, [0,1,2,3,4], [str(i) for i in range(0,13)], xmax=12)]
for (name, vals), col in zip(cdr.items(), cdr_colors):
    hl = col == "#0C0C0C"
    cdr_inner.append(polyline(vals, 4, 12, col, 2.6 if hl else 1.8, dots=hl))
cdr_inner.append(f'<text x="{W-R}" y="{T-2}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#8a8a8a">% / MOB</text>')
cdr_svg = chart("\n".join(cdr_inner))
cdr_legend = "".join(
    f'<span><i style="background:{c}"></i>{n}</span>' for n, c in zip(cdr.keys(), cdr_colors))

# ---------- FPD by month ----------
fpd_months = ["jul","aug","sep","oct","nov","dec","jan","feb","mar","apr","may","jun"]
fpd_vals = [2.8,2.7,2.55,2.5,2.4,2.35,2.2,2.1,2.05,1.95,1.85,1.8]
fbars = [grid(3.5, [0,1,2,3], None)]
bw = PW / len(fpd_vals) * 0.62
for i, v in enumerate(fpd_vals):
    cx = x_at(i + 0.5, len(fpd_vals))
    x = cx - bw/2
    y = y_at(v, 3.5); h = (T+PH) - y
    col = "#0C0C0C" if i >= len(fpd_vals)-3 else "#B5B5B5"
    fbars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="2" fill="{col}"/>')
    fbars.append(f'<text x="{cx:.1f}" y="{y-5:.1f}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="9.5" fill="#2E2E2E">{v:.1f}</text>')
    fbars.append(f'<text x="{cx:.1f}" y="{H-14}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="10" fill="#5A5A5A">{fpd_months[i]}</text>')
fpd_svg = chart("\n".join(fbars))

# ---------- Jr tranche: raw vs smoothed ----------
jr_raw  = [1.7,1.9,0.8,1.8,2.0,2.5,1.6,0.9,1.9,2.1,1.8,1.85]
jr_smooth=[1.70,1.74,1.72,1.76,1.80,1.83,1.82,1.80,1.82,1.84,1.85,1.86]
jr = [grid(3, [0,1,2,3], fpd_months, xmax=len(fpd_months)-1)]
jr.append(polyline(jr_raw, 3, len(jr_raw)-1, "#C0C0C0", 1.6, dash=True))
jr.append(polyline(jr_smooth, 3, len(jr_smooth)-1, "#0C0C0C", 2.6, dots=True))
jr.append(f'<text x="{W-R}" y="{T-2}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#8a8a8a">% / mo</text>')
jr_svg = chart("\n".join(jr))

# ---------- pyramid (granularity concept) ----------
pyramid_svg = ('<svg class="pyr-svg" viewBox="0 0 300 380" xmlns="http://www.w3.org/2000/svg">'
  '<polygon points="150,10 104.89,126 150,126" fill="#3a3a3a"/>'
  '<polygon points="150,10 150,126 195.11,126" fill="#181818"/>'
  '<polygon points="150,134 101.78,134 58.22,246 150,246" fill="#3a3a3a"/>'
  '<polygon points="150,134 150,246 241.78,246 198.22,134" fill="#181818"/>'
  '<polygon points="150,254 55.11,254 10,370 150,370" fill="#3a3a3a"/>'
  '<polygon points="150,254 150,370 290,370 244.89,254" fill="#181818"/>'
  '</svg>')


def metric(k, v, s):
    return f'<div class="metric"><div class="k">{k}</div><div class="v">{v}</div><div class="s">{s}</div></div>'


STYLE = """<style>
.chartframe { border:1px solid rgba(12,12,12,.13); border-radius:14px; padding:1.8vh 1.4vw; background:#fff; }
.chart { width:100%; height:auto; display:block; }
.legend { display:flex; gap:1.2vw; flex-wrap:wrap; margin-top:1vh; font-family:var(--font-mono); font-size:11px; color:#2E2E2E; }
.legend span { display:inline-flex; align-items:center; }
.legend i { display:inline-block; width:16px; height:3px; border-radius:2px; margin-right:6px; }
.two-col { display:grid; grid-template-columns:1.55fr 1fr; gap:2vw; align-items:center; margin-top:2vh; }
.readlist { list-style:none; display:flex; flex-direction:column; gap:1.4vh; }
.readlist li { font-family:var(--font-sans); font-size:clamp(13px,1.02vw,16px); color:#2E2E2E; line-height:1.5; padding-left:1.1em; position:relative; }
.readlist li::before { content:'—'; position:absolute; left:0; color:#8a8a8a; }
.readlist li b { color:var(--ink); font-weight:600; }
.metrics { display:grid; grid-template-columns:repeat(3,1fr); gap:1.2vw; margin-top:2.4vh; }
.metric { border:1px solid rgba(12,12,12,.13); border-radius:14px; padding:2.2vh 1.4vw; }
.metric .k { font-family:var(--font-mono); font-size:10px; letter-spacing:.14em; text-transform:uppercase; color:#5A5A5A; }
.metric .v { font-family:var(--font-sans); font-weight:700; font-size:clamp(26px,2.8vw,42px); letter-spacing:-.02em; margin-top:.6vh; line-height:1; }
.metric .s { font-family:var(--font-sans); font-size:12.5px; color:#2E2E2E; margin-top:.8vh; line-height:1.4; }
.callout { border:1px solid rgba(12,12,12,.18); border-left:3px solid var(--ink); border-radius:10px; padding:1.6vh 1.4vw; margin-top:2vh; font-family:var(--font-sans); font-size:clamp(13px,1.02vw,16px); color:#2E2E2E; line-height:1.55; }
.callout b { color:var(--ink); font-weight:600; }
.illus { position:absolute; bottom:4.4vh; left:4vw; z-index:6; font-family:var(--font-mono); font-size:9.5px; letter-spacing:.12em; text-transform:uppercase; color:#9a9a9a; }
/* pyramid concept */
.pyr-wrap { display:grid; grid-template-columns:clamp(170px,19vw,250px) 1fr; gap:3vw; align-items:center; margin-top:2vh; }
.pyr-svg { width:100%; height:auto; display:block; filter:drop-shadow(0 14px 28px rgba(0,0,0,.18)); }
.pyr-right { display:flex; flex-direction:column; gap:3.2vh; }
.pyr-tier { position:relative; border-top:2px solid var(--ink); padding-top:1.2vh; }
.pyr-tier::before { content:''; position:absolute; left:-7px; top:-7px; width:12px; height:12px; background:var(--ink); border-radius:2px; }
.pyr-tier h3 { font-family:var(--font-sans); font-weight:700; letter-spacing:-.02em; font-size:clamp(18px,1.9vw,30px); }
.pyr-tier p { font-family:var(--font-sans); font-size:clamp(13px,1.05vw,17px); color:#2E2E2E; line-height:1.5; margin-top:.6vh; }
.pyr-tier p b { color:var(--ink); font-weight:600; }
</style>"""

SLIDES = STYLE + f"""
<!-- 1 — COVER -->
<section class="slide cover5 active" id="cover" data-num="01">
  <div class="cover5-badge">São Paulo · 2026</div>
  <div class="cover5-center">
    <img class="cover5-logo" src="robbin-logo-black.svg" alt="Robbin">
    <div class="cover5-tag">Credit performance.</div>
  </div>
  <div class="cover5-meta">Confidential · Institutional material</div>
</section>

<!-- 2 — SCOPE & METHOD -->
<section class="slide theme-light vcenter" data-num="02">
  <div class="chapter-mark light-mark"><span class="chapter-num">01</span><span class="chapter-divider"></span><span class="chapter-year">Scope</span></div>
  <div class="slide-head reveal"><h1>How to read these <span class="accent">numbers.</span></h1>
  <p class="sub">Coverage, data source and metric definitions.</p></div>
  <div class="layers reveal" data-stagger>
    <div class="layer hi"><span class="layer-num">01</span><div><h3>PIX / boleto only</h3><p>The entire loan tape and every chart consider only PIX/boleto-settled operations. Card data is out of this view.</p></div><span class="layer-badge strong">loan tape</span></div>
    <div class="layer"><span class="layer-num">02</span><div><h3>FIDC carve-out</h3><p>We use the FIDC portfolio as a proxy for credit performance — the most recent, auditable snapshot of our ability to originate and collect.</p></div><span class="layer-badge">recent snapshot</span></div>
    <div class="layer"><span class="layer-num">03</span><div><h3>Definitions</h3><p><b>CDR by vintage</b> = cumulative loss (over90 outstanding) ÷ amount originated in the vintage. <b>FPD 15/30</b> = value that missed the first installment ÷ total of the month's first installments.</p></div><span class="layer-badge">metrics</span></div>
  </div>
  <div class="illus">Illustrative data — replace with the loan tape</div>
</section>

<!-- 3 — CDR BY VINTAGE -->
<section class="slide theme-light vcenter" data-num="03">
  <div class="chapter-mark light-mark"><span class="chapter-num">02</span><span class="chapter-divider"></span><span class="chapter-year">Risk · vintages</span></div>
  <div class="slide-head reveal"><h1>CDR by <span class="accent">vintage.</span></h1>
  <p class="sub">Cumulative loss (over90) over amount originated, by months on book (MOB).</p></div>
  <div class="two-col reveal">
    <div class="chartframe">{cdr_svg}
      <div class="legend">{cdr_legend}</div>
    </div>
    <ul class="readlist">
      <li>More recent vintages <b>perform better</b>: the 2025-Q1 curve runs below the earlier ones at the same MOB.</li>
      <li>Loss <b>stabilizes around MOB 9–10</b>, a sign of consistent maturation across vintages.</li>
      <li>Terminal level converging to <b>~2.5–3.0%</b> — within risk appetite.</li>
    </ul>
  </div>
  <div class="illus">Illustrative data — replace with the loan tape (PIX/boleto)</div>
</section>

<!-- 4 — FPD -->
<section class="slide theme-light vcenter" data-num="04">
  <div class="chapter-mark light-mark"><span class="chapter-num">03</span><span class="chapter-divider"></span><span class="chapter-year">Risk · origination</span></div>
  <div class="slide-head reveal"><h1>FPD 30 <span class="accent">by month.</span></h1>
  <p class="sub">Value that missed the first installment ÷ total of first installments — quality at the entry of the vintage.</p></div>
  <div class="two-col reveal">
    <div class="chartframe">{fpd_svg}
      <div class="legend"><span><i style="background:#0C0C0C"></i>last 3 months</span><span><i style="background:#B5B5B5"></i>history</span></div>
    </div>
    <ul class="readlist">
      <li>Consistent <b>downward trend</b>: from ~2.8% to <b>~1.8%</b> over the last 12 months.</li>
      <li>Improvement driven by <b>credit-policy tuning</b> and anchor sell-out data.</li>
      <li>Low, stable FPD <b>anticipates</b> healthier vintages in the CDR.</li>
    </ul>
  </div>
  <div class="illus">Illustrative data — replace with the loan tape (PIX/boleto)</div>
</section>

<!-- 5 — GRANULARITY (pyramid) -->
<section class="slide theme-light vcenter" data-num="05">
  <div class="chapter-mark light-mark"><span class="chapter-num">04</span><span class="chapter-divider"></span><span class="chapter-year">Portfolio · granularity</span></div>
  <div class="slide-head reveal"><h1>Granular and <span class="accent">diversified.</span></h1>
  <p class="sub">Why the book's risk is spread — concentration from the ground up.</p></div>
  <div class="pyr-wrap reveal">
    <div>{pyramid_svg}</div>
    <div class="pyr-right" data-stagger>
      <div class="pyr-tier"><h3>Low concentration</h3><p>Top-10 obligors are just <b>9%</b> of the book; the largest single name stays <b>under 2%</b>.</p></div>
      <div class="pyr-tier"><h3>Diversified by industry</h3><p>Spread across <b>retail, industry, services, construction and agro</b> — no single sector dominates.</p></div>
      <div class="pyr-tier"><h3>Highly granular</h3><p><b>12.4k active positions</b> at a ~<b>R$ 18k</b> average ticket — risk diluted across thousands of small exposures.</p></div>
    </div>
  </div>
  <div class="illus">Illustrative data — replace with the loan tape (PIX/boleto)</div>
</section>

<!-- 6 — TENOR & DURATION -->
<section class="slide theme-light vcenter" data-num="06">
  <div class="chapter-mark light-mark"><span class="chapter-num">05</span><span class="chapter-divider"></span><span class="chapter-year">Portfolio · tenor</span></div>
  <div class="slide-head reveal"><h1>Average tenor and <span class="accent">duration.</span></h1>
  <p class="sub">A short, fast-rotating book — quick recomposition and risk adjustment.</p></div>
  <div class="metrics reveal" data-stagger>
    {metric("Avg. tenor","7.2 <span style='font-size:.5em'>months</span>","weighted contractual term")}
    {metric("Duration","5.1 <span style='font-size:.5em'>months</span>","balance-weighted")}
    {metric("Avg. rate","3.4% <span style='font-size:.5em'>/mo</span>","PIX/boleto book")}
    {metric("Origination","R$ 42M <span style='font-size:.5em'>/mo</span>","current run-rate")}
    {metric("Over90","2.7%","balance >90d past due")}
    {metric("Turnover","~1.7×","per year")}
  </div>
  <div class="illus">Illustrative data — replace with the loan tape (PIX/boleto)</div>
</section>

<!-- 7 — Jr TRANCHE -->
<section class="slide theme-light vcenter" data-num="07">
  <div class="chapter-mark light-mark"><span class="chapter-num">06</span><span class="chapter-divider"></span><span class="chapter-year">FIDC · Jr tranche</span></div>
  <div class="slide-head reveal"><h1>The Jr shields the <span class="accent">seniors.</span></h1>
  <p class="sub">Excess spread + subordination provide the safety cushion to senior shares (ex-contributions).</p></div>
  <div class="two-col reveal">
    <div class="chartframe">{jr_svg}
      <div class="legend"><span><i style="background:#0C0C0C"></i>credit performance (smoothed)</span><span><i style="background:#C0C0C0"></i>observed Jr quota</span></div>
    </div>
    <div style="display:flex; flex-direction:column; gap:1.2vh;">
      {metric("Subordination","22%","cushion for seniors")}
      {metric("Excess spread","~14% <span style='font-size:.45em'>/yr</span>","above senior cost")}
    </div>
  </div>
  <div class="callout reveal">The <b>volatility seen in the Jr quota</b> came from <b>isolated operational errors</b>, not credit deterioration. Normalizing those events, the portfolio's performance is <b>stable</b> — and the subordination + excess-spread cushion was never touched by the seniors.</div>
  <div class="illus">Illustrative data — replace with the loan tape (PIX/boleto)</div>
</section>

<!-- 8 — CORPORATE / RUNWAY -->
<section class="slide theme-light vcenter" data-num="08">
  <div class="chapter-mark light-mark"><span class="chapter-num">07</span><span class="chapter-divider"></span><span class="chapter-year">Company</span></div>
  <div class="slide-head reveal"><h1>Corporate backing of the <span class="accent">leverage.</span></h1>
  <p class="sub">Since this is a leverage of the subordinated tranche, the company's health underpins the structure.</p></div>
  <div class="metrics reveal" data-stagger>
    {metric("Cash","R$ 32M","current position")}
    {metric("Monthly burn","R$ 2.1M","net")}
    {metric("Runway","15+ <span style='font-size:.5em'>months</span>","at current burn")}
    {metric("Origination target","R$ 80M <span style='font-size:.5em'>/mo</span>","year exit")}
    {metric("FIDC capacity","R$ 500M","senior share")}
    {metric("Target subordination","≥ 20%","structural floor")}
  </div>
  <div class="callout reveal">Corporate targets, cash and runway sized to <b>sustain the subordinated share</b> through the cycle — aligning shareholder risk with the senior shareholders'.</div>
  <div class="illus">Illustrative data — replace with the company's real figures</div>
</section>

<!-- 9 — Q&A -->
<section class="slide theme-dark closing2" data-num="09">
  <div class="closing2-bg"><div class="closing2-grid"></div><div class="closing2-glow"></div></div>
  <div class="closing2-inner">
    <div class="closing2-eyebrow reveal"><span>—</span><span>Discussion</span></div>
    <h2 class="closing2-line reveal"><span class="cl-row hi">Q&amp;A</span></h2>
    <div class="closing2-divider reveal"></div>
    <div class="closing2-logo reveal"><img src="robbin-logo-white.svg" alt="Robbin" style="height:46px;width:auto;"></div>
  </div>
</section>
"""

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slides.html")
open(out, "w", encoding="utf-8").write(SLIDES)
print("wrote", out, len(SLIDES), "bytes")
