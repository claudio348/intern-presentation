#!/usr/bin/env python3
"""Generate slides.html for the Robbin credit / FIDC institutional deck (EN).
Loan-tape figures are real; structural / corporate figures are flagged WIP.
Charts are hand-built SVG to match the deck design system."""
import os, re

W, H = 680, 344
L, R, T, B = 46, 14, 16, 40
PW, PH = W - L - R, H - T - B


def x_at(i, xmax): return L + (i / xmax) * PW
def y_at(v, ymax): return T + PH - (v / ymax) * PH


def grid(ymax, yticks, xlabels=None, xmax=None, xfont=10.5, center=False):
    s = []
    for v in yticks:
        y = y_at(v, ymax)
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

# ---------- FPD 30 by month — area + trend (real loan tape) ----------
fpd_labels = ["may/25","jun/25","jul/25","aug/25","sep/25","oct/25","nov/25","dec/25","jan/26","feb/26","mar/26","apr/26"]
fpd_vals = [15.2,7.4,3.1,0.0,2.0,3.9,1.0,3.7,5.8,0.9,5.4,1.4]

def fpd_area():
    ymax = 16; Lx, Rx, Tx, Bx = 46, 16, 22, 34
    pw, ph = W-Lx-Rx, H-Tx-Bx; n = len(fpd_vals)
    xs = [Lx + i/(n-1)*pw for i in range(n)]
    ys = [Tx+ph - v/ymax*ph for v in fpd_vals]
    ybase = Tx+ph
    mean = sum(fpd_vals)/n; ymn = Tx+ph - mean/ymax*ph
    yb5 = Tx+ph - 5/ymax*ph
    s = [f'<svg class="chart" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">']
    s.append('<defs><linearGradient id="fpdG" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#0C0C0C" stop-opacity="0.22"/>'
             '<stop offset="1" stop-color="#0C0C0C" stop-opacity="0.015"/></linearGradient></defs>')
    # healthy band 0–5%
    s.append(f'<rect x="{Lx}" y="{yb5:.1f}" width="{pw:.1f}" height="{ybase-yb5:.1f}" fill="#0C0C0C" opacity="0.04"/>')
    s.append(f'<text x="{Lx+7}" y="{ybase-7:.1f}" font-family="Geist Mono,monospace" font-size="9" fill="#9a9a9a">healthy zone &lt; 5%</text>')
    # gridlines + y labels
    for t in (0,5,10,15):
        y = Tx+ph - t/ymax*ph
        s.append(f'<text x="{Lx-8}" y="{y+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#9a9a9a">{t}</text>')
    # area + line
    d = f"M {xs[0]:.1f},{ybase:.1f} " + " ".join(f"L {x:.1f},{y:.1f}" for x,y in zip(xs,ys)) + f" L {xs[-1]:.1f},{ybase:.1f} Z"
    s.append(f'<path d="{d}" fill="url(#fpdG)"/>')
    s.append('<polyline points="%s" fill="none" stroke="#0C0C0C" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>'
             % " ".join(f"{x:.1f},{y:.1f}" for x,y in zip(xs,ys)))
    # mean line
    s.append(f'<line x1="{Lx}" y1="{ymn:.1f}" x2="{W-Rx}" y2="{ymn:.1f}" stroke="#0C0C0C" stroke-width="1" stroke-dasharray="2 4" opacity="0.5"/>')
    s.append(f'<text x="{W-Rx}" y="{ymn-4:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="9" fill="#6A6A6A">avg {mean:.1f}%</text>')
    # dots
    for x,y in zip(xs,ys):
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.3" fill="#0C0C0C"/>')
    # spike annotation
    s.append(f'<text x="{xs[0]:.1f}" y="{ys[0]-9:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="600" font-size="11" fill="#0C0C0C">{fpd_vals[0]:.1f}%</text>')
    s.append(f'<text x="{xs[0]+9:.1f}" y="{ys[0]+11:.1f}" font-family="Geist Mono,monospace" font-size="8.5" fill="#8a8a8a">isolated cohort</text>')
    # current point highlight
    s.append(f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="8" fill="none" stroke="#0C0C0C" stroke-opacity="0.22"/>')
    s.append(f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="4.3" fill="#0C0C0C"/>')
    s.append(f'<text x="{xs[-1]:.1f}" y="{ys[-1]-11:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="600" font-size="11" fill="#0C0C0C">{fpd_vals[-1]:.1f}%</text>')
    # x labels
    for i,lab in enumerate(fpd_labels):
        s.append(f'<text x="{xs[i]:.1f}" y="{H-13}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="8.5" fill="#5A5A5A">{lab}</text>')
    s.append('</svg>')
    return "\n".join(s)
fpd_svg = fpd_area()

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

# ---------- isometric stacked layers (aligns with the 3 tier rows) ----------
def iso_stack():
    cx, w, hh, t = 162, 96, 31, 24
    ys = [60, 180, 300]                      # slab centers = thirds of the 360 height
    tops = ["#5a5a5a", "#4c4c4c", "#444444"]  # top faces (top slab brightest)
    s = ['<svg class="pyr-svg" viewBox="0 0 324 360" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg">']
    s.append('<defs><filter id="isoSh" x="-40%" y="-40%" width="180%" height="200%"><feGaussianBlur stdDeviation="6"/></filter></defs>')
    s.append(f'<ellipse cx="{cx}" cy="346" rx="120" ry="10" fill="#000" opacity="0.12" filter="url(#isoSh)"/>')
    for y0, topcol in zip(ys, tops):
        s.append(f'<polygon points="{cx+w},{y0} {cx},{y0+hh} {cx},{y0+hh+t} {cx+w},{y0+t}" fill="#161616"/>')   # right face
        s.append(f'<polygon points="{cx-w},{y0} {cx},{y0+hh} {cx},{y0+hh+t} {cx-w},{y0+t}" fill="#2c2c2c"/>')   # left face
        s.append(f'<polygon points="{cx},{y0-hh} {cx+w},{y0} {cx},{y0+hh} {cx-w},{y0}" fill="{topcol}"/>')       # top face
        s.append(f'<polyline points="{cx-w},{y0} {cx},{y0-hh} {cx+w},{y0}" fill="none" stroke="#7a7a7a" stroke-width="1"/>')  # top highlight
    s.append('</svg>')
    return "\n".join(s)
pyramid_svg = iso_stack()


# ---------- anchor composition: generic stacked R$M and stacked % ----------
ANCHOR_ORDER = ["Cantu","Moura","Chilli Beans","Juntos Somos Mais","Malwee","Brinox","Others"]
ANCHOR_COL = {"Cantu":"#5B2E91","Moura":"#2563B0","Chilli Beans":"#E11D48",
              "Juntos Somos Mais":"#8FA31E","Malwee":"#1F7A3D","Brinox":"#0F8C8C","Others":"#B5B5B5"}
anchor_legend = "".join(f'<span><i style="background:{ANCHOR_COL[g]}"></i>{g}</span>' for g in ANCHOR_ORDER)

# off-balance (FIDC) — loan tape balance by anchor (R$M), FIDC live from Dec/25
lt_labels = ["dec/25","jan/26","feb/26","mar/26","apr/26","may/26"]
lt_data = {
  "Cantu":[0.77,0.97,1.08,2.11,2.4,4.4],
  "Moura":[0.38,0.54,1.55,2.12,2.5,2.7],
  "Chilli Beans":[3.12,3.18,3.62,3.93,3.7,3.41],
  "Juntos Somos Mais":[0.96,0.88,1.01,1.31,1.95,2.22],
  "Malwee":[0.98,1.5,1.56,1.73,1.86,1.83],
  "Brinox":[0.27,0.26,0.34,0.34,0.37,0.39],
  "Others":[0,0,0.04,0.11,0.15,0.16],
}

def _xstep(n): return 1 if n <= 14 else (2 if n <= 22 else 3)

def _fidc(s, xd, Tx, ybase, WD, Rx, shade_only=False):
    s.append(f'<rect x="{xd:.1f}" y="{Tx}" width="{WD-Rx-xd:.1f}" height="{ybase-Tx:.1f}" fill="#0C0C0C" opacity="0.05"/>')

def stack_rm(labels, data, ymax, yticks, fidc_idx):
    WD, HD = 1040, 440; Lx, Rx, Tx, Bx = 44, 12, 26, 42
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; n = len(labels); slot = pw/n; bw = slot*0.66
    def Y(v): return Tx+ph - v/ymax*ph
    ybase = Y(0)
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    if fidc_idx is not None:
        xd = Lx+slot*fidc_idx
        s.append(f'<rect x="{xd:.1f}" y="{Tx}" width="{WD-Rx-xd:.1f}" height="{ybase-Tx:.1f}" fill="#0C0C0C" opacity="0.05"/>')
    for t in yticks:
        s.append(f'<text x="{Lx-7}" y="{Y(t)+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#9a9a9a">{t}</text>')
    for i in range(n):
        cx = Lx+slot*i+slot/2; x = cx-bw/2; ytop = ybase
        tot = sum(data[g][i] for g in ANCHOR_ORDER)
        for g in ANCHOR_ORDER:
            v = data[g][i]
            if v <= 0: continue
            hh = v/ymax*ph; y = ytop-hh
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{hh:.1f}" fill="{ANCHOR_COL[g]}"/>')
            if tot and hh >= 14 and v/tot*100 >= 9:
                tc = "#2E2E2E" if g == "Others" else "#fff"
                s.append(f'<text x="{cx:.1f}" y="{y+hh/2+3:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="600" font-size="8" fill="{tc}">{round(v/tot*100)}%</text>')
            ytop = y
        if tot > 0.05:
            last = i == n-1
            s.append(f'<text x="{cx:.1f}" y="{ytop-5:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="{700 if last else 500}" font-size="8" fill="{"#0C0C0C" if last else "#6A6A6A"}">{tot:.1f}</text>')
    if fidc_idx is not None:
        s.append(f'<line x1="{xd:.1f}" y1="{Tx}" x2="{xd:.1f}" y2="{ybase:.1f}" stroke="#0C0C0C" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.55"/>')
        s.append(f'<text x="{xd+7:.1f}" y="{Tx+11:.1f}" font-family="Geist Mono,monospace" font-size="10" letter-spacing="0.08em" fill="#3A3A3A">FIDC raised →</text>')
    for i in range(0, n, _xstep(n)):
        s.append(f'<text x="{Lx+slot*i+slot/2:.1f}" y="{HD-15}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="8.5" fill="#5A5A5A">{labels[i]}</text>')
    s.append('</svg>'); return "\n".join(s)

def stack_pct(labels, data, fidc_idx):
    WD, HD = 1040, 440; Lx, Rx, Tx, Bx = 38, 12, 50, 44
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; n = len(labels); slot = pw/n; bw = slot*0.72
    def Y(v): return Tx+ph - v/100*ph
    ybase = Y(0)
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    if fidc_idx is not None:
        xd = Lx+slot*fidc_idx
        s.append(f'<rect x="{xd:.1f}" y="{Tx}" width="{WD-Rx-xd:.1f}" height="{ybase-Tx:.1f}" fill="#0C0C0C" opacity="0.05"/>')
    for t in (0,25,50,75,100):
        s.append(f'<text x="{Lx-7}" y="{Y(t)+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#9a9a9a">{t}</text>')
    for i in range(n):
        tot = sum(data[g][i] for g in ANCHOR_ORDER) or 1
        cx = Lx+slot*i+slot/2; x = cx-bw/2; ytop = ybase
        for g in ANCHOR_ORDER:
            v = data[g][i]
            if v <= 0: continue
            pct = v/tot*100; hh = pct/100*ph; y = ytop-hh
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{hh:.1f}" fill="{ANCHOR_COL[g]}"/>')
            if pct >= 7:
                tc = "#2E2E2E" if g == "Others" else "#fff"
                s.append(f'<text x="{cx:.1f}" y="{y+hh/2+3:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="600" font-size="8.5" fill="{tc}">{round(pct)}%</text>')
            ytop = y
        if tot > 0.05:
            s.append(f'<text x="{cx:.1f}" y="{Y(100)-9:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="700" font-size="8" fill="#3A3A3A">{tot:.0f}</text>')
        s.append(f'<text x="{cx:.1f}" y="{HD-15}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="8.5" fill="#5A5A5A">{labels[i]}</text>')
    if fidc_idx is not None:
        s.append(f'<line x1="{xd:.1f}" y1="{Tx}" x2="{xd:.1f}" y2="{ybase:.1f}" stroke="#0C0C0C" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.55"/>')
        s.append(f'<text x="{xd+7:.1f}" y="16" font-family="Geist Mono,monospace" font-size="10" letter-spacing="0.06em" fill="#3A3A3A">FIDC raised →</text>')
    s.append('</svg>'); return "\n".join(s)

# off-balance (FIDC) charts — no shading (whole window is post-FIDC)
lb_off_svg  = stack_rm(lt_labels, lt_data, 16, [0,4,8,12,16], None)
div_off_svg = stack_pct(lt_labels, lt_data, None)


def metric(k, v, s, wip=False):
    w = '<div class="wip" style="margin-top:1vh">WIP · to confirm</div>' if wip else ''
    return f'<div class="metric"><div class="k">{k}</div><div class="v">{v}</div><div class="s">{s}</div>{w}</div>'


# ---------- monthly TPV / origination by rail (real) ----------
tpv_months = ["may/24","jun/24","jul/24","aug/24","sep/24","oct/24","nov/24","dec/24","jan/25","feb/25","mar/25","apr/25","may/25","jun/25","jul/25","aug/25","sep/25","oct/25","nov/25","dec/25","jan/26","feb/26","mar/26","apr/26","may/26"]
tpv_order = ["Cartão","PIX Rails"]   # PIX Rails = Boleto + Pix
TPV_COL = {"Cartão":"#CBCBCB","PIX Rails":"#0C0C0C"}
tpv_data = {
  "Cartão":[0.26,0.49,0.91,1.43,4.93,4.54,3.66,3.14,2.8,3.54,5.51,4.95,5.48,6.06,6.63,8.21,12.12,8.31,9.23,8.02,5.99,3.12,3.33,2.34,0.34],
  "PIX Rails":[0.0,0.0,0.0,0.17,0.48,2.25,1.56,2.56,2.26,2.66,2.75,2.23,2.28,1.99,1.72,2.81,3.59,4.59,3.74,3.15,2.57,3.16,5.49,3.45,5.69],
}

def tpv_chart():
    WD, HD = 1040, 440; Lx, Rx, Tx, Bx = 40, 12, 24, 46
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; ymax = 17; n = len(tpv_months); slot = pw/n; bw = slot*0.6
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    for t in (0,4,8,12,16):
        y = Tx+ph - t/ymax*ph
        s.append(f'<text x="{Lx-6}" y="{y+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#9a9a9a">{t}</text>')
    for i in range(n):
        cx = Lx+slot*i+slot/2; x = cx-bw/2; ytop = Tx+ph
        total = sum(tpv_data[r][i] for r in tpv_order) or 0
        for rail in tpv_order:
            v = tpv_data[rail][i]
            if v <= 0: continue
            hh = v/ymax*ph; y = ytop-hh
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{hh:.1f}" fill="{TPV_COL[rail]}"/>')
            if hh >= 16:
                tcol = "#fff" if rail == "PIX Rails" else "#3A3A3A"
                s.append(f'<text x="{cx:.1f}" y="{y+hh/2+3:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="600" font-size="8.5" fill="{tcol}">{round(v/total*100)}%</text>')
            ytop = y
        if total > 0:
            s.append(f'<text x="{cx:.1f}" y="{ytop-6:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="700" font-size="9.5" fill="#0C0C0C">{total:.1f}</text>')
        s.append(f'<text x="{cx:.1f}" y="{HD-16}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="7.8" fill="#5A5A5A">{tpv_months[i]}</text>')
    s.append('</svg>')
    return "\n".join(s)

tpv_svg = tpv_chart()
tpv_legend = "".join(f'<span><i style="background:{TPV_COL[r]}"></i>{r}</span>' for r in tpv_order) + '<span style="color:#8a8a8a">total on top · R$M</span>'


# ---------- credit portfolio (outstanding balance) by source over time (real) ----------
_pm = ['2024-05','2024-06','2024-07','2024-08','2024-09','2024-10','2024-11','2024-12','2025-01','2025-02','2025-03','2025-04','2025-05','2025-06','2025-07','2025-08','2025-09','2025-10','2025-11','2025-12','2026-01','2026-02','2026-03','2026-04','2026-05','2026-06']
_MON = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
port_labels = [f"{_MON[int(m.split('-')[1])-1]}/{m.split('-')[0][2:]}" for m in _pm]
port_order = ANCHOR_ORDER
PORT_COL = ANCHOR_COL
port_data = {
    "Cantu":[0.21,0.59,1.36,2.31,6.47,9.06,10.5,10.87,11.21,11.62,11.99,12.43,13.73,15.05,15.4,15.7,17.28,17.05,15.61,14.29,13.53,12.53,11.64,10.29,10.61,10.33],
    "Moura":[0.0,0.0,0.0,0.0,0.0,0.0,0.01,0.29,0.59,0.92,1.01,1.17,2.04,2.79,4.38,6.42,9.21,10.18,12.05,13.66,13.14,12.33,10.8,9.64,8.46,8.31],
    "Chilli Beans":[0.0,0.0,0.0,0.01,0.08,0.46,2.19,3.41,3.65,4.1,6.57,7.14,6.95,6.73,6.32,6.7,6.78,6.7,6.41,5.76,5.53,5.02,5.52,4.52,3.94,3.92],
    "Juntos Somos Mais":[0.0,0.0,0.0,0.04,0.08,0.73,1.29,1.55,1.73,1.92,2.4,2.35,2.41,2.54,2.5,2.65,4.06,5.44,5.87,5.26,5.04,5.14,5.29,5.31,5.09,5.03],
    "Malwee":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.07,1.01,1.44,1.77,1.87,2.08,2.17,2.06,2.12],
    "Brinox":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.36,0.8,0.57,0.61,0.42,0.51,0.5,0.52,0.32,0.45],
    "Others":[0.04,0.06,0.07,0.18,0.14,0.27,0.24,0.37,0.62,1.08,1.45,1.82,1.9,2.05,2.12,2.38,2.55,2.41,2.39,2.3,2.17,2.12,2.33,2.31,2.21,3.39],
}
FIDC_FROM = "2025-12"   # month the FIDC was raised (shaded region onward)

def portfolio_stack():
    WD, HD = 1040, 426; Lx, Rx, Tx, Bx = 46, 16, 30, 44
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; ymax = 48; n = len(_pm)
    xs = [Lx + i/(n-1)*pw for i in range(n)]
    def Y(v): return Tx+ph - v/ymax*ph
    ybase = Y(0)
    di = _pm.index(FIDC_FROM); xd = xs[di]
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    # FIDC-raised shaded background (from December onward)
    s.append(f'<rect x="{xd:.1f}" y="{Tx}" width="{WD-Rx-xd:.1f}" height="{ybase-Tx:.1f}" fill="#0C0C0C" opacity="0.05"/>')
    # gridlines + y labels
    for t in (0,10,20,30,40):
        y = Y(t)
        s.append(f'<text x="{Lx-7}" y="{y+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#9a9a9a">{t}</text>')
    # stacked areas (bottom -> top)
    bottoms = [0.0]*n
    for layer in port_order:
        tops = [bottoms[i]+port_data[layer][i] for i in range(n)]
        top_pts = " ".join(f"{xs[i]:.1f},{Y(tops[i]):.1f}" for i in range(n))
        bot_pts = " ".join(f"{xs[i]:.1f},{Y(bottoms[i]):.1f}" for i in range(n-1,-1,-1))
        s.append(f'<polygon points="{top_pts} {bot_pts}" fill="{PORT_COL[layer]}" stroke="#FFFFFF" stroke-width="0.6"/>')
        bottoms = tops
    # total outline
    s.append('<polyline points="%s" fill="none" stroke="#0C0C0C" stroke-width="1.4"/>'
             % " ".join(f"{xs[i]:.1f},{Y(bottoms[i]):.1f}" for i in range(n)))
    # FIDC divider + label
    s.append(f'<line x1="{xd:.1f}" y1="{Tx}" x2="{xd:.1f}" y2="{ybase:.1f}" stroke="#0C0C0C" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.55"/>')
    s.append(f'<text x="{xd+7:.1f}" y="{Tx+11:.1f}" font-family="Geist Mono,monospace" font-size="10" letter-spacing="0.08em" fill="#3A3A3A">FIDC raised →</text>')
    # current total label
    s.append(f'<text x="{xs[-1]:.1f}" y="{Y(bottoms[-1])-8:.1f}" text-anchor="end" font-family="Geist,sans-serif" font-weight="700" font-size="11" fill="#0C0C0C">R$ {bottoms[-1]:.1f}M</text>')
    # sparse x labels (every 3 months)
    for i in range(0, n, 3):
        s.append(f'<text x="{xs[i]:.1f}" y="{HD-15}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="9" fill="#5A5A5A">{port_labels[i]}</text>')
    s.append('</svg>')
    return "\n".join(s)

port_svg = portfolio_stack()
port_legend = "".join(f'<span><i style="background:{PORT_COL[g]}"></i>{g}</span>' for g in port_order)

def portfolio_total_bars():
    WD, HD = 1040, 440; Lx, Rx, Tx, Bx = 46, 16, 30, 44
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; ymax = 48; n = len(_pm); slot = pw/n; bw = slot*0.62
    def Y(v): return Tx+ph - v/ymax*ph
    ybase = Y(0)
    di = _pm.index(FIDC_FROM); xd = Lx + slot*di
    totals = [round(sum(port_data[g][i] for g in port_order), 2) for i in range(n)]
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    s.append(f'<rect x="{xd:.1f}" y="{Tx}" width="{WD-Rx-xd:.1f}" height="{ybase-Tx:.1f}" fill="#0C0C0C" opacity="0.05"/>')
    for t in (0,10,20,30,40):
        y = Y(t)
        s.append(f'<text x="{Lx-7}" y="{y+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#9a9a9a">{t}</text>')
    for i in range(n):
        cx = Lx+slot*i+slot/2; x = cx-bw/2; v = totals[i]
        y = Y(v); h = ybase-y
        col = "#0C0C0C" if i >= di else "#B9B9B9"
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{max(h,0):.1f}" rx="2" fill="{col}"/>')
        if v > 0.05:  # label every month
            last = i == n-1
            s.append(f'<text x="{cx:.1f}" y="{y-5:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="{700 if last else 500}" font-size="7.6" fill="{"#0C0C0C" if last else "#6A6A6A"}">{v:.1f}</text>')
    # FIDC divider + label
    s.append(f'<line x1="{xd:.1f}" y1="{Tx}" x2="{xd:.1f}" y2="{ybase:.1f}" stroke="#0C0C0C" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.55"/>')
    s.append(f'<text x="{xd+7:.1f}" y="{Tx+11:.1f}" font-family="Geist Mono,monospace" font-size="10" letter-spacing="0.08em" fill="#3A3A3A">FIDC raised →</text>')
    for i in range(0, n, 3):
        s.append(f'<text x="{Lx+slot*i+slot/2:.1f}" y="{HD-15}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="9" fill="#5A5A5A">{port_labels[i]}</text>')
    s.append('</svg>')
    return "\n".join(s)

port_total_svg = portfolio_total_bars()
port_total_legend = ('<span><i style="background:#B9B9B9"></i>pre-FIDC</span>'
                     '<span><i style="background:#0C0C0C"></i>FIDC-funded (Dec-25 →)</span>'
                     '<span style="color:#8a8a8a">total on book · R$M</span>')

# consolidated (corporate) charts
PORT_FIDC = _pm.index("2025-12")
lb_con_svg  = stack_rm(port_labels, port_data, 48, [0,10,20,30,40], PORT_FIDC)
div_con_svg = stack_pct(port_labels, port_data, PORT_FIDC)

# ---------- cohort loan book per partner (months on book, R$M) ----------
cohort_order = ["Cantu","Moura","Juntos Somos Mais","Chilli Beans","Others","Malwee","Brinox"]
def _cohort(name):
    vals = port_data[name]; i = 0
    while i < len(vals) and vals[i] == 0: i += 1
    return i, vals[i:]
cohort = {n: _cohort(n) for n in cohort_order}
cohort_legend = "".join(
    f'<span><i style="background:{ANCHOR_COL[n]}"></i>{n} ({port_labels[cohort[n][0]]})</span>' for n in cohort_order)

def cohort_lines():
    WD, HD = 1040, 452; Lx, Rx, Tx, Bx = 30, 44, 34, 40
    n = len(port_labels); pw, ph = WD-Lx-Rx, HD-Tx-Bx; ymax = 18
    def X(i): return Lx + i/(n-1)*pw
    def Y(v): return Tx+ph - v/ymax*ph
    base = Tx+ph; di = PORT_FIDC; xd = X(di)
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    # FIDC-live shaded region
    s.append(f'<rect x="{xd:.1f}" y="{Tx}" width="{WD-Rx-xd:.1f}" height="{base-Tx:.1f}" fill="#0C0C0C" opacity="0.05"/>')
    s.append(f'<line x1="{Lx}" y1="{base:.1f}" x2="{WD-Rx}" y2="{base:.1f}" stroke="#C8C8C8" stroke-width="1"/>')
    for i in range(0, n, 3):
        s.append(f'<text x="{X(i):.1f}" y="{HD-14}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="9" fill="#5A5A5A">{port_labels[i]}</text>')
    ends = []
    for name in cohort_order:
        vals = port_data[name]; col = ANCHOR_COL[name]
        f = 0
        while f < n and vals[f] == 0: f += 1
        pts = " ".join(f"{X(i):.1f},{Y(vals[i]):.1f}" for i in range(f, n))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="2.6" stroke-linejoin="round" stroke-linecap="round"/>')
        ends.append({"real": Y(vals[-1]), "y": Y(vals[-1]), "v": vals[-1], "col": col, "dark": name == "Others"})
    # FIDC divider + label
    s.append(f'<line x1="{xd:.1f}" y1="{Tx}" x2="{xd:.1f}" y2="{base:.1f}" stroke="#0C0C0C" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.55"/>')
    s.append(f'<text x="{xd+7:.1f}" y="{Tx-8:.1f}" font-family="Geist Mono,monospace" font-size="10" letter-spacing="0.06em" fill="#3A3A3A">FIDC live →</text>')
    # de-clutter endpoint value pills (min vertical gap)
    ends.sort(key=lambda e: e["y"]); prev = -99
    for e in ends:
        if e["y"] < prev + 15: e["y"] = prev + 15
        prev = e["y"]
    xe = X(n-1)
    for e in ends:
        col = e["col"]; ry = e["real"]; ly = e["y"]
        val = f'{e["v"]:.1f}'.replace(".", ",")
        tc = "#2E2E2E" if e["dark"] else "#fff"
        s.append(f'<circle cx="{xe:.1f}" cy="{ry:.1f}" r="3.2" fill="{col}"/>')
        if abs(ly-ry) > 1.5:
            s.append(f'<line x1="{xe:.1f}" y1="{ry:.1f}" x2="{xe+6:.1f}" y2="{ly:.1f}" stroke="{col}" stroke-width="1"/>')
        s.append(f'<rect x="{xe+6:.1f}" y="{ly-7:.1f}" width="30" height="14" rx="3" fill="{col}"/>')
        s.append(f'<text x="{xe+21:.1f}" y="{ly+3:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="700" font-size="8" fill="{tc}">{val}</text>')
    s.append('</svg>')
    return "\n".join(s)
cohort_svg = cohort_lines()

# ---------- revenue run rate (ARR) ----------
arr_labels = ["3Q24","4Q24","1Q25","2Q25","3Q25","4Q25","1Q26","Apr/26"]
arr_vals = [319,550,1427,1716,2077,2532,2976,3176]
def arr_chart():
    WD, HD = 1040, 452; Lx, Rx, Tx, Bx = 18, 14, 44, 40
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; n = len(arr_vals); slot = pw/n; bw = slot*0.5; ymax = 3500
    def Y(v): return Tx+ph - v/ymax*ph
    base = Y(0)
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    s.append(f'<line x1="{Lx}" y1="{base:.1f}" x2="{WD-Rx}" y2="{base:.1f}" stroke="#C8C8C8" stroke-width="1"/>')
    for i, v in enumerate(arr_vals):
        cx = Lx+slot*i+slot/2; x = cx-bw/2; y = Y(v); h = base-y
        col = "#0C0C0C" if i == n-1 else "#CBCBCB"
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="2" fill="{col}"/>')
        val = f"{v:,}".replace(",", ".")
        s.append(f'<text x="{cx:.1f}" y="{y-9:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="700" font-size="14" fill="#0C0C0C">{val}</text>')
        s.append(f'<text x="{cx:.1f}" y="{HD-14:.1f}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="11" fill="#5A5A5A">{arr_labels[i]}</text>')
    s.append('</svg>')
    return "\n".join(s)
arr_svg = arr_chart()


STYLE = """<style>
.chartframe { padding:1vh 0 0; background:transparent; border:none; }
.chart { width:100%; height:auto; display:block; }
.slide { padding-left:3vw; padding-right:3vw; }
.slide.vcenter { padding-bottom:6.5vh; }
.slide-head .sub { white-space:nowrap; max-width:none; }
.legend { display:flex; gap:1.2vw; flex-wrap:wrap; margin-top:1vh; font-family:var(--font-mono); font-size:11px; color:#2E2E2E; }
.legend span { display:inline-flex; align-items:center; }
.legend i { display:inline-block; width:16px; height:3px; border-radius:2px; margin-right:6px; }
.two-col { display:grid; grid-template-columns:1.85fr 1fr; gap:2vw; align-items:center; margin-top:2vh; }
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
.illus { position:absolute; bottom:2.2vh; left:3vw; z-index:6; font-family:var(--font-mono); font-size:9.5px; letter-spacing:.12em; text-transform:uppercase; color:#9a9a9a; }
.tag-pill { display:inline-flex; align-items:center; gap:6px; font-family:var(--font-mono); font-size:10px; letter-spacing:.14em; text-transform:uppercase; color:var(--ink); border:1px solid rgba(12,12,12,.32); border-radius:100px; padding:3px 12px; margin-top:1.3vh; }
.wip { display:inline-flex; align-items:center; gap:5px; font-family:var(--font-mono); font-size:9.5px; letter-spacing:.1em; text-transform:uppercase; color:#8a5a00; border:1px dashed #C9A227; background:rgba(201,162,39,.12); border-radius:6px; padding:2px 8px; width:fit-content; }
.wip::before { content:''; width:5px; height:5px; border-radius:50%; background:#C9A227; }
.wip-lg { font-size:11px; border-radius:100px; padding:5px 13px; gap:7px; }
.wip-lg::before { width:6px; height:6px; }
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
.pyr-right { display:grid; grid-template-rows:repeat(3,1fr); height:100%; position:relative; }
.pyr-right::before { content:''; position:absolute; left:0; top:8%; bottom:8%; width:1px; background:linear-gradient(to bottom, transparent, rgba(12,12,12,.28), transparent); }
.pyr-tier { position:relative; display:flex; flex-direction:column; justify-content:center; padding:0 2.6vw 0 2vw; }
.pyr-tier::before { content:''; position:absolute; left:-6px; top:50%; width:11px; height:11px; background:var(--ink); transform:translateY(-50%) rotate(45deg); z-index:1; }
.pyr-tier::after { content:''; position:absolute; left:-3vw; top:50%; width:3vw; height:1px; background:linear-gradient(to left, var(--ink), transparent); }
.pyr-idx { position:absolute; right:0; top:50%; transform:translateY(-50%); font-family:var(--font-mono); font-size:12px; letter-spacing:.12em; color:#C4C4C4; }
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

<!-- PORTFOLIO -->
<section class="slide theme-light vcenter" data-num="02">
  <div class="chapter-mark light-mark"><span class="chapter-num">01</span><span class="chapter-divider"></span><span class="chapter-year">Portfolio</span></div>
  <div class="slide-head reveal"><h1>The credit <span class="accent">portfolio.</span></h1>
  <p class="sub">Total outstanding balance (R$M) — peaked at R$ 44M, R$ 34M today.</p></div>
  <div class="blegend reveal">{port_total_legend}</div>
  <div class="chartframe reveal">{port_total_svg}</div>
  <div class="illus">Source: portfolio by month/source · Mar/24–Jun/26</div>
</section>

<!-- ORIGINATION -->
<section class="slide theme-light vcenter" data-num="02">
  <div class="chapter-mark light-mark"><span class="chapter-num">01</span><span class="chapter-divider"></span><span class="chapter-year">Origination</span></div>
  <div class="slide-head reveal"><h1>Origination on the <span class="accent">PIX rail.</span></h1>
  <p class="sub">Monthly TPV by rail (R$M) — scaling on the PIX rail.</p></div>
  <div class="blegend reveal">{tpv_legend}</div>
  <div class="chartframe reveal">{tpv_svg}</div>
  <div class="illus">Source: monthly TPV · Mar/24–May/26 (Jun/26 partial, excluded)</div>
</section>

<!-- WHY WE PERFORM BETTER THAN BANKS (iso stack) -->
<section class="slide theme-light vcenter" data-num="03">
  <div class="chapter-mark light-mark"><span class="chapter-num">02</span><span class="chapter-divider"></span><span class="chapter-year">The edge</span></div>
  <div class="slide-head reveal"><h1>Why we perform better than <span class="accent">banks.</span></h1>
  <p class="sub">Three structural edges — each reinforcing the one above.</p></div>
  <div class="pyr-wrap reveal">
    <div class="pyr-fig">{pyramid_svg}</div>
    <div class="pyr-right" data-stagger>
      <div class="pyr-tier"><span class="pyr-idx">01</span><h3>Data edge</h3><p>Access to the <b>Supplier–SME relationship</b> and <b>transaction data</b>, turning these relationships into better credit insights and solid unit economics.</p></div>
      <div class="pyr-tier"><span class="pyr-idx">02</span><h3>Secured credit <small>Central Bank · CMN 4.734</small></h3><p>Access to SME credit-card receivables data and the ability to use it as <b>collateral</b>, enabling <b>smarter underwriting and collection</b>.</p></div>
      <div class="pyr-tier"><span class="pyr-idx">03</span><h3>Willingness to pay</h3><p>Leveraging the supplier's brand, our co-branded card captures SMEs' <b>willingness to pay, rooted in loyalty and dependence</b>.</p></div>
    </div>
  </div>
</section>

<!-- 4 — CDR BY VINTAGE -->
<section class="slide theme-light vcenter" data-num="04">
  <div class="chapter-mark light-mark"><span class="chapter-num">03</span><span class="chapter-divider"></span><span class="chapter-year">Risk · vintages</span></div>
  <div class="slide-head reveal"><h1>CDR by <span class="accent">vintage.</span></h1>
  <p class="sub">Cumulative over90 loss ÷ originated, by months on book (MOB).</p></div>
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
  <div class="illus">Source: PIX/boleto loan tape · Jan/26–May/26 (FIDC)</div>
</section>

<!-- 5 — FPD -->
<section class="slide theme-light vcenter" data-num="05">
  <div class="chapter-mark light-mark"><span class="chapter-num">04</span><span class="chapter-divider"></span><span class="chapter-year">Risk · origination</span></div>
  <div class="slide-head reveal"><h1>FPD 30 <span class="accent">by month.</span></h1>
  <p class="sub">First-payment default — value late on the 1st installment ÷ total.</p></div>
  <div class="two-col reveal">
    <div class="chartframe">{fpd_svg}
      <div class="legend"><span><i style="background:#0C0C0C"></i>FPD 30 (monthly)</span><span style="color:#8a8a8a">shaded = healthy &lt; 5% · dashed = average</span></div>
    </div>
    <ul class="readlist">
      <li>The <b>May-25 spike (~15%)</b> was an isolated cohort; FPD normalized to <b>low single digits</b> since.</li>
      <li>Last 12 months <b>average ~4%</b>, with recent months at <b>~1–5%</b>.</li>
      <li>FPD is the <b>earliest read</b> on origination quality — now stable.</li>
    </ul>
  </div>
  <div class="illus">Source: PIX/boleto loan tape · MOB-1 snapshot</div>
</section>

<!-- CREDIT PORTFOLIO PER PARTNER -->
<section class="slide theme-light vcenter" data-num="06">
  <div class="chapter-mark light-mark"><span class="chapter-num">05</span><span class="chapter-divider"></span><span class="chapter-year">Credit portfolio · per partner</span></div>
  <div class="slide-head reveal"><h1>Credit portfolio <span class="accent">per partner.</span></h1>
  <p class="sub">Outstanding loan book by partner (R$M) — FIDC live from Dec-25 · total R$ 33.5M.</p></div>
  <div class="blegend reveal">{cohort_legend}</div>
  <div class="chartframe reveal">{cohort_svg}</div>
  <div class="illus">Source: cohort — credit portfolio · balance by vintage</div>
</section>

<!-- INCREASING DIVERSIFICATION — CONSOLIDATED -->
<section class="slide theme-light vcenter" data-num="06">
  <div class="chapter-mark light-mark"><span class="chapter-num">05</span><span class="chapter-divider"></span><span class="chapter-year">Diversification · consolidated</span></div>
  <div class="slide-head reveal"><h1>Increasing <span class="accent">diversification.</span></h1>
  <p class="sub">Anchor as % of the credit portfolio — total R$M on top.</p>
  <span class="tag-pill">Corporate consolidated</span></div>
  <div class="blegend reveal">{anchor_legend}</div>
  <div class="chartframe reveal">{div_con_svg}</div>
  <div class="illus">Source: portfolio by month/source · May/24–Jun/26</div>
</section>

<!-- INCREASING DIVERSIFICATION — OFF-BALANCE FIDC -->
<section class="slide theme-light vcenter" data-num="07">
  <div class="chapter-mark light-mark"><span class="chapter-num">06</span><span class="chapter-divider"></span><span class="chapter-year">Diversification · off-balance</span></div>
  <div class="slide-head reveal"><h1>Increasing <span class="accent">diversification.</span></h1>
  <p class="sub">Anchor as % of the credit portfolio — FIDC carve-out.</p>
  <span class="tag-pill">Off-balance · FIDC</span></div>
  <div class="blegend reveal">{anchor_legend}</div>
  <div class="chartframe reveal">{div_off_svg}</div>
  <div class="illus">Source: PIX/boleto loan tape · Dec/25–May/26 (FIDC)</div>
</section>

<!-- 8 — TENOR & DURATION -->
<section class="slide theme-light vcenter" data-num="08">
  <div class="chapter-mark light-mark"><span class="chapter-num">07</span><span class="chapter-divider"></span><span class="chapter-year">Portfolio · tenor</span></div>
  <div class="slide-head reveal"><h1>Average tenor and <span class="accent">duration.</span></h1>
  <p class="sub">A short, fast-rotating book — quick recomposition.</p></div>
  <div class="metrics reveal" data-stagger>
    {metric("Avg. tenor","3.5 <span style='font-size:.5em'>months</span>","mean installments")}
    {metric("Duration","~2.1 <span style='font-size:.5em'>months</span>","balance-weighted")}
    {metric("Avg. rate","44.6% <span style='font-size:.5em'>/yr</span>","principal-weighted")}
    {metric("Origination","R$ 4.9M <span style='font-size:.5em'>/mo</span>","last-3-month run-rate")}
    {metric("Current book","R$ 15.1M","outstanding balance")}
    {metric("Turnover","~3.4×","per year")}
  </div>
  <div class="illus">Source: PIX/boleto loan tape · Jan/26–May/26 (FIDC)</div>
</section>

<!-- 9 — Jr TRANCHE -->
<section class="slide theme-light vcenter" data-num="09">
  <div class="chapter-mark light-mark"><span class="chapter-num">08</span><span class="chapter-divider"></span><span class="chapter-year">FIDC · Jr tranche</span></div>
  <div class="slide-head reveal"><h1>The Jr shields the <span class="accent">seniors.</span></h1>
  <p class="sub">Over90 stabilizing; subordination + excess spread absorb losses before seniors.</p></div>
  <div class="two-col reveal">
    <div class="chartframe">{jr_svg}
      <div class="legend"><span><i style="background:#0C0C0C"></i>trend (smoothed)</span><span><i style="background:#C0C0C0"></i>portfolio over90 (observed)</span></div>
    </div>
    <div style="display:flex; flex-direction:column; gap:1.2vh;">
      {metric("Subordination","22%","structure · cushion for seniors", wip=True)}
      {metric("Excess spread","~14% <span style='font-size:.45em'>/yr</span>","structure · above senior cost", wip=True)}
    </div>
  </div>
  <div class="callout reveal">The over90 ramp reflects <b>book seasoning</b> and the <b>2025-Q1 cohort</b> now rolling off — over90 is <b>down from ~25% to ~18%</b> as recent vintages dominate. The Jr's subordination + excess spread absorb these losses, keeping the <b>senior shares protected</b> (ex-contributions).</div>
  <div class="illus">Over90: PIX/boleto loan tape · subordination / excess spread = structure (to confirm)</div>
</section>

<!-- 10 — CORPORATE / RUNWAY -->
<section class="slide theme-light vcenter" data-num="10">
  <div class="chapter-mark light-mark"><span class="chapter-num">09</span><span class="chapter-divider"></span><span class="chapter-year">Company</span></div>
  <div class="slide-head reveal"><h1>Corporate backing of the <span class="accent">leverage.</span></h1>
  <p class="sub">Leverage of the subordinated tranche — the company underpins it.</p>
  <div class="wip wip-lg" style="margin-top:1.4vh">WIP · placeholder figures — to confirm</div></div>
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

<!-- REVENUE RUN RATE -->
<section class="slide theme-light vcenter" data-num="11">
  <div class="chapter-mark light-mark"><span class="chapter-num">10</span><span class="chapter-divider"></span><span class="chapter-year">Company · ARR</span></div>
  <div class="slide-head reveal"><h1>Revenue run <span class="accent">rate.</span></h1>
  <p class="sub">Revenue run rate in US$ thousands · FX R$ 5.00 / US$.</p></div>
  <div class="chartframe reveal">{arr_svg}</div>
  <div class="illus">Source: company figures · revenue run-rate</div>
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

# auto-number slides (data-num) and chapter marks (chapter-num) in document order
def _seq(tmpl):
    c = [0]
    def r(m):
        c[0] += 1; return tmpl.format(c[0])
    return r
SLIDES = re.sub(r'data-num="\d+"', _seq('data-num="{:02d}"'), SLIDES)
SLIDES = re.sub(r'<span class="chapter-num">\d+</span>', _seq('<span class="chapter-num">{:02d}</span>'), SLIDES)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slides.html")
open(out, "w", encoding="utf-8").write(SLIDES)
print("wrote", out, len(SLIDES), "bytes")
