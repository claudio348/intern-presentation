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


def grid(ymax, yticks, xlabels=None, xmax=None, xfont=10.5, center=False):
    s = []
    for v in yticks:
        y = y_at(v, ymax)
        s.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="#ECECEC" stroke-width="1"/>')
        s.append(f'<text x="{L-8}" y="{y+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="11" fill="#8a8a8a">{v:g}</text>')
    if xlabels:
        n = len(xlabels)
        for i, lab in enumerate(xlabels):
            x = x_at(i + (0.5 if center else 0), len(xlabels) if center else (xmax if xmax else (n - 1)))
            s.append(f'<text x="{x:.1f}" y="{H-13}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="{xfont}" fill="#5A5A5A">{lab}</text>')
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


# ---------- CDR by vintage (real loan tape) ----------
cdr = {
    "Vintage 2025-Q1": [0,0,0,0.63,5.31,10.51,15.28,15.64,16.73],
    "Vintage 2025-Q2": [0,0,0,4.92,9.43,9.85,10.04,10.20,10.31],
    "Vintage 2025-Q3": [0,0,0,0.82,3.72,6.39,6.88,7.60,7.69],
    "Vintage 2025-Q4": [0,0,0.32,2.52,7.43,8.76,6.70,4.33],
}
cdr_colors = ["#C4C4C4", "#9A9A9A", "#6E6E6E", "#0C0C0C"]
cdr_inner = [grid(18, [0,6,12,18], [str(i) for i in range(0,9)], xmax=8)]
for (name, vals), col in zip(cdr.items(), cdr_colors):
    hl = col == "#0C0C0C"
    cdr_inner.append(polyline(vals, 18, 8, col, 2.6 if hl else 1.8, dots=hl))
cdr_inner.append(f'<text x="{W-R}" y="{T-2}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#8a8a8a">% / MOB</text>')
cdr_svg = chart("\n".join(cdr_inner))
cdr_legend = "".join(
    f'<span><i style="background:{c}"></i>{n}</span>' for n, c in zip(cdr.keys(), cdr_colors))

# ---------- FPD 30 by month (real loan tape) ----------
fpd_labels = ["may/25","jun/25","jul/25","aug/25","sep/25","oct/25","nov/25","dec/25","jan/26","feb/26","mar/26","apr/26"]
fpd_vals = [15.2,7.4,3.1,0.0,2.0,3.9,1.0,3.7,5.8,0.9,5.4,1.4]
fpd_ymax = 16
fpd_mean = sum(fpd_vals)/len(fpd_vals)
fbars = [grid(fpd_ymax, [0,5,10,15], fpd_labels, xfont=8.5, center=True)]
bw = PW / len(fpd_vals) * 0.5
for i, v in enumerate(fpd_vals):
    cx = x_at(i + 0.5, len(fpd_vals))
    x = cx - bw/2
    y = y_at(v, fpd_ymax); h = (T+PH) - y
    col = "#0C0C0C" if i >= len(fpd_vals)-3 else "#AEAEAE"
    fbars.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{max(h,0):.1f}" rx="3" fill="{col}"/>')
    fbars.append(f'<text x="{cx:.1f}" y="{y-6:.1f}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="9" fill="#6A6A6A">{v:.1f}</text>')
# mean line
ym = y_at(fpd_mean, fpd_ymax)
fbars.append(f'<line x1="{L}" y1="{ym:.1f}" x2="{W-R}" y2="{ym:.1f}" stroke="#0C0C0C" stroke-width="1" stroke-dasharray="2 4" opacity="0.55"/>')
fbars.append(f'<text x="{W-R}" y="{ym-4:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="9" fill="#6A6A6A">avg {fpd_mean:.1f}%</text>')
fpd_svg = chart("\n".join(fbars))

# ---------- Portfolio over90 vs smoothed trend (real loan tape) ----------
jr_months= ["jun/25","jul/25","aug/25","sep/25","oct/25","nov/25","dec/25","jan/26","feb/26","mar/26","apr/26","may/26"]
jr_obs   = [4.2,10.9,13.8,21.4,23.7,22.6,24.9,25.3,22.4,19.4,20.1,17.6]
jr_trend = [4.2,9.5,14.0,18.5,21.5,23.0,23.8,23.5,22.2,20.6,19.3,18.2]
jr = [grid(30, [0,10,20,30], jr_months, xmax=len(jr_months)-1, xfont=8.5)]
jr.append(polyline(jr_obs, 30, len(jr_obs)-1, "#C0C0C0", 1.6, dash=True))
jr.append(polyline(jr_trend, 30, len(jr_trend)-1, "#0C0C0C", 2.6, dots=True))
jr.append(f'<text x="{W-R}" y="{T-2}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#8a8a8a">over90 %</text>')
jr_svg = chart("\n".join(jr))

# ---------- breakdown by anchor program (real loan tape) ----------
industry = [("Cantu",29),("Chilli Beans",23),("Moura",18),("Juntos Somos Mais",15),("Malwee",12),("Other",3)]
ind_rows = "".join(
    f'<div class="ind-row"><span class="ind-l">{n}</span>'
    f'<span class="ind-track"><span class="ind-fill" style="width:{p*3.2}%"></span></span>'
    f'<span class="ind-v">{p}%</span></div>' for n, p in industry)

# ---------- elegant pyramid (3 equal bands; aligns with tier rows) ----------
pyramid_svg = ('<svg class="pyr-svg" viewBox="0 0 300 360" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">'
  '<defs>'
  '<linearGradient id="pyrL" x1="0" y1="0" x2="0.3" y2="1"><stop offset="0" stop-color="#5c5c5c"/><stop offset="1" stop-color="#2b2b2b"/></linearGradient>'
  '<linearGradient id="pyrR" x1="1" y1="0" x2="0.7" y2="1"><stop offset="0" stop-color="#2a2a2a"/><stop offset="1" stop-color="#0b0b0b"/></linearGradient>'
  '<filter id="pyrSh" x="-40%" y="-20%" width="180%" height="160%"><feGaussianBlur stdDeviation="6"/></filter>'
  '</defs>'
  '<ellipse cx="150" cy="356" rx="140" ry="9" fill="#000" opacity="0.12" filter="url(#pyrSh)"/>'
  '<polygon points="150,8 102.61,119 150,119" fill="url(#pyrL)"/>'
  '<polygon points="150,8 150,119 197.39,119" fill="url(#pyrR)"/>'
  '<polygon points="150,125 100.05,125 53.95,233 150,233" fill="url(#pyrL)"/>'
  '<polygon points="150,125 150,233 246.05,233 199.95,125" fill="url(#pyrR)"/>'
  '<polygon points="150,239 51.39,239 4,350 150,350" fill="url(#pyrL)"/>'
  '<polygon points="150,239 150,350 296,350 248.61,239" fill="url(#pyrR)"/>'
  '<line x1="150" y1="8" x2="150" y2="350" stroke="#ffffff" stroke-opacity="0.05" stroke-width="1"/>'
  '</svg>')


# ---------- partner share over time (stacked, brand colors) ----------
BRAND_COL = {
    "Chilli Beans":"#E11D48", "Cantu":"#5B2E91", "Juntos Somos Mais":"#8FA31E",
    "Moura":"#2563B0", "Malwee":"#1F7A3D", "Brinox":"#0F8C8C", "Others":"#0C2340",
}
div_months = ["nov/24","dec/24","jan/25","feb/25","mar/25","apr/25","may/25","jun/25","jul/25",
              "aug/25","sep/25","oct/25","nov/25","dec/25","jan/26","feb/26","mar/26","apr/26","may/26"]
# stack order bottom -> top
div_order = ["Chilli Beans","Cantu","Juntos Somos Mais","Moura","Malwee","Brinox","Others"]
div_data = {
    "Chilli Beans":[68,76,61,69,71,72,67,71,72,71,64,55,47,48,43,39,34,29,23],
    "Cantu":[19,17,31,26,19,19,23,20,16,17,14,14,14,12,13,12,18,19,29],
    "Juntos Somos Mais":[13,6,8,5,9,10,9,9,9,9,15,22,20,15,12,11,11,15,15],
    "Moura":[0,0,0,0,0,0,0,0,3,3,7,7,6,6,7,17,18,19,18],
    "Malwee":[0,0,0,0,0,0,0,0,0,0,0,0,9,15,20,17,15,14,12],
    "Brinox":[0,0,0,0,0,0,0,0,0,0,1,2,4,4,4,4,3,3,3],
    "Others":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1],
}

def stacked_chart():
    WD, HD = 1040, 432
    Lx, Rx, Tx, Bx = 38, 8, 10, 46
    pw, ph = WD-Lx-Rx, HD-Tx-Bx
    n = len(div_months); slot = pw/n; bw = slot*0.74
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    for t in (0,25,50,75,100):
        y = Tx+ph-(t/100*ph)
        s.append(f'<line x1="{Lx}" y1="{y:.1f}" x2="{WD-Rx}" y2="{y:.1f}" stroke="#ECECEC" stroke-width="1"/>')
        s.append(f'<text x="{Lx-7}" y="{y+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#8a8a8a">{t}</text>')
    for i in range(n):
        tot = sum(div_data[b][i] for b in div_order) or 1
        cx = Lx+slot*i+slot/2; x = cx-bw/2; ytop = Tx+ph
        for b in div_order:
            v = div_data[b][i]
            if v <= 0: continue
            hh = v/tot*ph; y = ytop-hh
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{hh:.1f}" fill="{BRAND_COL[b]}"/>')
            if v/tot*100 >= 6.5:
                s.append(f'<text x="{cx:.1f}" y="{y+hh/2+3:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="600" font-size="9.5" fill="#fff">{v}%</text>')
            ytop = y
        s.append(f'<text x="{cx:.1f}" y="{HD-16}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="9" fill="#5A5A5A">{div_months[i]}</text>')
    s.append('</svg>')
    return "\n".join(s)

div_svg = stacked_chart()
div_legend = "".join(f'<span><i style="background:{BRAND_COL[b]}"></i>{b}</span>'
                     for b in ["Chilli Beans","Cantu","Juntos Somos Mais","Moura","Malwee","Brinox","Others"])


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
.ind-row { display:grid; grid-template-columns:170px 1fr 48px; align-items:center; gap:1vw; margin-bottom:1.4vh; }
.ind-l { font-family:var(--font-sans); font-size:clamp(13px,1vw,16px); color:var(--ink); font-weight:500; }
.ind-track { height:12px; background:rgba(12,12,12,.06); border-radius:100px; overflow:hidden; }
.ind-fill { display:block; height:100%; background:var(--ink); border-radius:100px; }
.ind-v { font-family:var(--font-mono); font-size:12px; color:#2E2E2E; text-align:right; }
.blegend { display:flex; flex-wrap:wrap; gap:1.1vw; margin:1.2vh 0 .6vh; font-family:var(--font-mono); font-size:11px; color:#2E2E2E; }
.blegend span { display:inline-flex; align-items:center; }
.blegend i { width:12px; height:12px; border-radius:3px; margin-right:6px; display:inline-block; }
/* elegant pyramid — 3 equal bands aligned with the tier rows */
.pyr-wrap { display:grid; grid-template-columns:auto 1fr; gap:2.6vw; height:clamp(360px,56vh,520px); align-items:stretch; margin-top:2.5vh; }
.pyr-fig { display:flex; align-items:center; justify-content:center; }
.pyr-svg { height:100%; width:auto; display:block; }
.pyr-right { display:grid; grid-template-rows:repeat(3,1fr); height:100%; }
.pyr-tier { position:relative; border-top:1px solid var(--ink); padding:1.4vh 0 0 1.2vw; }
.pyr-tier::before { content:''; position:absolute; left:-6px; top:-6px; width:11px; height:11px; background:var(--ink); transform:rotate(45deg); }
.pyr-tier h3 { font-family:var(--font-sans); font-weight:700; letter-spacing:-.025em; font-size:clamp(19px,2vw,31px); line-height:1.04; }
.pyr-tier h3 small { display:block; font-family:var(--font-mono); font-weight:500; font-size:11px; letter-spacing:.14em; text-transform:uppercase; color:#8a8a8a; margin-top:.5vh; }
.pyr-tier p { font-family:var(--font-sans); font-size:clamp(13px,1.02vw,16px); color:#3A3A3A; line-height:1.5; margin-top:.7vh; max-width:54ch; }
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
    <div class="layer"><span class="layer-num">02</span><div><h3>FIDC carve-out</h3><p>We use the FIDC portfolio as the proxy for credit performance — the most recent, auditable snapshot. History <b>Nov/24–May/26</b>: <b>R$ 46.8M</b> originated across <b>16.2k</b> contracts.</p></div><span class="layer-badge">recent snapshot</span></div>
    <div class="layer"><span class="layer-num">03</span><div><h3>Definitions</h3><p><b>CDR by vintage</b> = cumulative loss (over90 outstanding) ÷ amount originated in the vintage. <b>FPD 15/30</b> = value that missed the first installment ÷ total of the month's first installments.</p></div><span class="layer-badge">metrics</span></div>
  </div>
  <div class="illus">Illustrative data — replace with the loan tape</div>
</section>

<!-- 3 — WHY WE PERFORM BETTER THAN BANKS (pyramid) -->
<section class="slide theme-light vcenter" data-num="03">
  <div class="chapter-mark light-mark"><span class="chapter-num">02</span><span class="chapter-divider"></span><span class="chapter-year">The edge</span></div>
  <div class="slide-head reveal"><h1>Why we perform better than <span class="accent">banks.</span></h1>
  <p class="sub">Three structural edges, stacked — each reinforcing the one above.</p></div>
  <div class="pyr-wrap reveal">
    <div class="pyr-fig">{pyramid_svg}</div>
    <div class="pyr-right" data-stagger>
      <div class="pyr-tier"><h3>Data edge</h3><p>Access to the <b>Supplier–SME relationship</b> and <b>transaction data</b>, turning these relationships into better credit insights and solid unit economics.</p></div>
      <div class="pyr-tier"><h3>Secured credit <small>Central Bank · CMN 4.734</small></h3><p>Access to SME credit-card receivables data and the ability to use it as <b>collateral</b>, enabling <b>smarter underwriting and collection</b>.</p></div>
      <div class="pyr-tier"><h3>Willingness to pay</h3><p>Leveraging the supplier's brand, our co-branded card captures SMEs' <b>willingness to pay, rooted in loyalty and dependence</b>.</p></div>
    </div>
  </div>
</section>

<!-- 4 — CDR BY VINTAGE -->
<section class="slide theme-light vcenter" data-num="04">
  <div class="chapter-mark light-mark"><span class="chapter-num">03</span><span class="chapter-divider"></span><span class="chapter-year">Risk · vintages</span></div>
  <div class="slide-head reveal"><h1>CDR by <span class="accent">vintage.</span></h1>
  <p class="sub">Cumulative loss (over90) over amount originated, by months on book (MOB).</p></div>
  <div class="two-col reveal">
    <div class="chartframe">{cdr_svg}
      <div class="legend">{cdr_legend}</div>
    </div>
    <ul class="readlist">
      <li><b>2025-Q1 was the weakest cohort</b> (~17% peak over90 / originated).</li>
      <li>Underwriting changes cut peak loss to <b>~8% by 2025-Q4</b> — improving vintage over vintage.</li>
      <li>Short <b>~3.5-month tenor</b>: over90 peaks around MOB 4–6, then rolls off as the book amortizes.</li>
    </ul>
  </div>
  <div class="illus">Source: PIX/boleto loan tape · Nov/24–May/26</div>
</section>

<!-- 5 — FPD -->
<section class="slide theme-light vcenter" data-num="05">
  <div class="chapter-mark light-mark"><span class="chapter-num">04</span><span class="chapter-divider"></span><span class="chapter-year">Risk · origination</span></div>
  <div class="slide-head reveal"><h1>FPD 30 <span class="accent">by month.</span></h1>
  <p class="sub">Value that missed the first installment ÷ total of first installments — quality at the entry of the vintage.</p></div>
  <div class="two-col reveal">
    <div class="chartframe">{fpd_svg}
      <div class="legend"><span><i style="background:#0C0C0C"></i>last 3 months</span><span><i style="background:#B5B5B5"></i>history</span></div>
    </div>
    <ul class="readlist">
      <li>The <b>May-25 spike (~15%)</b> was an isolated cohort; FPD normalized to <b>low single digits</b> since.</li>
      <li>Last 12 months <b>average ~4%</b>, with recent months at <b>~1–5%</b>.</li>
      <li>FPD is the <b>earliest read</b> on origination quality — now stable.</li>
    </ul>
  </div>
  <div class="illus">Source: PIX/boleto loan tape · MOB-1 snapshot</div>
</section>

<!-- 6 — GRANULARITY (bars) -->
<section class="slide theme-light vcenter" data-num="06">
  <div class="chapter-mark light-mark"><span class="chapter-num">05</span><span class="chapter-divider"></span><span class="chapter-year">Portfolio · granularity</span></div>
  <div class="slide-head reveal"><h1>Granular and <span class="accent">diversified.</span></h1>
  <p class="sub">Exposure by anchor program and portfolio concentration.</p></div>
  <div class="two-col reveal">
    <div class="chartframe" style="padding:3vh 2vw;">{ind_rows}</div>
    <div style="display:flex; flex-direction:column; gap:1.4vh;">
      {metric("Avg. ticket","R$ 2.9k","per contract")}
      {metric("Top program","29%","Cantu — largest anchor")}
      {metric("Active positions","6.0k","contracts with balance")}
    </div>
  </div>
  <div class="illus">Source: PIX/boleto loan tape · current balance (May/26)</div>
</section>

<!-- 7 — INCREASING DIVERSIFICATION -->
<section class="slide theme-light vcenter" data-num="07">
  <div class="chapter-mark light-mark"><span class="chapter-num">06</span><span class="chapter-divider"></span><span class="chapter-year">Portfolio · mix</span></div>
  <div class="slide-head reveal"><h1>Increasing <span class="accent">diversification.</span></h1>
  <p class="sub">Partner as % of credit portfolio (by outstanding balance).</p></div>
  <div class="blegend reveal">{div_legend}</div>
  <div class="chartframe reveal">{div_svg}</div>
  <div class="illus">Source: PIX/boleto loan tape · Nov/24–May/26</div>
</section>

<!-- 8 — TENOR & DURATION -->
<section class="slide theme-light vcenter" data-num="08">
  <div class="chapter-mark light-mark"><span class="chapter-num">07</span><span class="chapter-divider"></span><span class="chapter-year">Portfolio · tenor</span></div>
  <div class="slide-head reveal"><h1>Average tenor and <span class="accent">duration.</span></h1>
  <p class="sub">A short, fast-rotating book — quick recomposition and risk adjustment.</p></div>
  <div class="metrics reveal" data-stagger>
    {metric("Avg. tenor","3.5 <span style='font-size:.5em'>months</span>","mean installments")}
    {metric("Duration","~2.1 <span style='font-size:.5em'>months</span>","balance-weighted")}
    {metric("Avg. rate","44.6% <span style='font-size:.5em'>/yr</span>","principal-weighted")}
    {metric("Origination","R$ 4.9M <span style='font-size:.5em'>/mo</span>","last-3-month run-rate")}
    {metric("Current book","R$ 15.1M","outstanding balance")}
    {metric("Turnover","~3.4×","per year")}
  </div>
  <div class="illus">Source: PIX/boleto loan tape · Nov/24–May/26</div>
</section>

<!-- 9 — Jr TRANCHE -->
<section class="slide theme-light vcenter" data-num="09">
  <div class="chapter-mark light-mark"><span class="chapter-num">08</span><span class="chapter-divider"></span><span class="chapter-year">FIDC · Jr tranche</span></div>
  <div class="slide-head reveal"><h1>The Jr shields the <span class="accent">seniors.</span></h1>
  <p class="sub">Portfolio over90 is stabilizing; subordination + excess spread absorb the loss before it reaches seniors.</p></div>
  <div class="two-col reveal">
    <div class="chartframe">{jr_svg}
      <div class="legend"><span><i style="background:#0C0C0C"></i>trend (smoothed)</span><span><i style="background:#C0C0C0"></i>portfolio over90 (observed)</span></div>
    </div>
    <div style="display:flex; flex-direction:column; gap:1.2vh;">
      {metric("Subordination","22%","structure · cushion for seniors")}
      {metric("Excess spread","~14% <span style='font-size:.45em'>/yr</span>","structure · above senior cost")}
    </div>
  </div>
  <div class="callout reveal">The over90 ramp reflects <b>book seasoning</b> and the <b>2025-Q1 cohort</b> now rolling off — over90 is <b>down from ~25% to ~18%</b> as recent vintages dominate. The Jr's subordination + excess spread absorb these losses, keeping the <b>senior shares protected</b> (ex-contributions).</div>
  <div class="illus">Over90: PIX/boleto loan tape · subordination / excess spread = structure (to confirm)</div>
</section>

<!-- 10 — CORPORATE / RUNWAY -->
<section class="slide theme-light vcenter" data-num="10">
  <div class="chapter-mark light-mark"><span class="chapter-num">09</span><span class="chapter-divider"></span><span class="chapter-year">Company</span></div>
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

<!-- 11 — Q&A -->
<section class="slide theme-dark closing2" data-num="11">
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
