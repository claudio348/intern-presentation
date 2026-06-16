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

# ---------- FPD 30 by month — deviation-from-threshold lollipops (real loan tape) ----------
fpd_labels = ["may/25","jun/25","jul/25","aug/25","sep/25","oct/25","nov/25","dec/25","jan/26","feb/26","mar/26","apr/26"]
fpd_vals = [15.2,7.4,3.1,0.0,2.0,3.9,1.0,3.7,5.8,0.9,5.4,1.4]
FPD_THR = 5.0            # underwriting target — FPD healthy below this
FPD_RED = "#D11A2A"      # breach accent

def fpd_area():
    ymax = 16; Lx, Rx, Tx, Bx = 46, 18, 40, 40
    pw, ph = W-Lx-Rx, H-Tx-Bx; n = len(fpd_vals)
    slot = pw/n; bw = slot*0.52
    def cx(i): return Lx + slot*i + slot/2
    def Y(v): return Tx+ph - v/ymax*ph
    ybase = Tx+ph; ythr = Y(FPD_THR)
    mean = sum(fpd_vals)/n; ymn = Y(mean)
    s = [f'<svg class="chart" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">']
    # y labels (no gridlines)
    for t in (0,5,10,15):
        s.append(f'<text x="{Lx-8}" y="{Y(t)+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#9a9a9a">{t}</text>')
    # columns — in target (ink) vs breach (red)
    for i,v in enumerate(fpd_vals):
        x = cx(i)-bw/2; yv = Y(v); breach = v > FPD_THR
        col = FPD_RED if breach else "#0C0C0C"
        s.append(f'<rect x="{x:.1f}" y="{yv:.1f}" width="{bw:.1f}" height="{ybase-yv:.1f}" rx="2.5" fill="{col}" opacity="{1 if (breach or i==n-1) else 0.86}"/>')
        vc = FPD_RED if breach else ("#0C0C0C" if i==n-1 else "#6A6A6A")
        fw = 700 if (breach or i==n-1) else 500
        s.append(f'<text x="{cx(i):.1f}" y="{yv-5:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="{fw}" font-size="9" fill="{vc}">{v:.1f}</text>')
    # underwriting target line (drawn over bars) — label sits in the empty mid gap
    s.append(f'<line x1="{Lx}" y1="{ythr:.1f}" x2="{W-Rx}" y2="{ythr:.1f}" stroke="#0C0C0C" stroke-width="1.5" stroke-dasharray="5 4"/>')
    s.append(f'<text x="{cx(4):.1f}" y="{ythr-8:.1f}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="9.5" letter-spacing="0.04em" fill="#5A5A5A">underwriting target &le; 5%</text>')
    # spike annotation
    s.append(f'<text x="{cx(0)+bw/2+6:.1f}" y="{Y(fpd_vals[0])+14:.1f}" font-family="Geist Mono,monospace" font-size="8.5" fill="#9a9a9a">isolated cohort</text>')
    # x labels
    for i,lab in enumerate(fpd_labels):
        s.append(f'<text x="{cx(i):.1f}" y="{H-13}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="8.5" fill="#5A5A5A">{lab}</text>')
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
ANCHOR_ORDER = ["Cantu","Moura","Chilli Beans","Juntos Somos Mais","Malwee","Brinox","iFood","Intelbras","Others"]
ANCHOR_COL = {"Cantu":"#5B2E91","Moura":"#2563B0","Chilli Beans":"#E11D48",
              "Juntos Somos Mais":"#8FA31E","Malwee":"#1F7A3D","Brinox":"#0F8C8C",
              "iFood":"#EA1D2C","Intelbras":"#5DB85C","Others":"#B5B5B5"}
anchor_legend = ("".join(f'<span><i style="background:{ANCHOR_COL[g]}"></i>{g}</span>' for g in ANCHOR_ORDER)
                 + '<span style="color:#8a8a8a">Others = app / beta testers & users</span>')

# off-balance (FIDC) — loan tape balance by anchor (R$M), FIDC live from Dec/25
lt_labels = ["dec/25","jan/26","feb/26","mar/26","apr/26","may/26"]
lt_data = {
  "Cantu":[0.77,0.97,1.08,2.11,2.4,4.4],
  "Moura":[0.38,0.54,1.55,2.12,2.5,2.7],
  "Chilli Beans":[3.12,3.18,3.62,3.93,3.7,3.41],
  "Juntos Somos Mais":[0.96,0.88,1.01,1.31,1.95,2.22],
  "Malwee":[0.98,1.5,1.56,1.73,1.86,1.83],
  "Brinox":[0.27,0.26,0.34,0.34,0.37,0.39],
  "iFood":[0.0,0.0,0.03,0.11,0.15,0.14],
  "Intelbras":[0,0,0,0,0,0],
  "Others":[0,0,0,0,0,0.01],   # incl. Truss + app / beta users
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
tpv_order = ["Legacy rail","PIX Rails"]   # Legacy rail = Cartão · PIX Rails = Boleto + Pix
TPV_COL = {"Legacy rail":"#CBCBCB","PIX Rails":"#0C0C0C"}
tpv_data = {
  "Legacy rail":[0.26,0.49,0.91,1.43,4.93,4.54,3.66,3.14,2.8,3.54,5.51,4.95,5.48,6.06,6.63,8.21,12.12,8.31,9.23,8.02,5.99,3.12,3.33,2.34,0.34],
  "PIX Rails":[0.0,0.0,0.0,0.17,0.48,2.25,1.56,2.56,2.26,2.66,2.75,2.23,2.28,1.99,1.72,2.81,3.59,4.59,3.74,3.15,2.57,3.16,5.49,3.45,5.69],
}

def tpv_chart():
    WD, HD = 1040, 440; Lx, Rx, Tx, Bx = 40, 12, 24, 46
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; ymax = 17; n = len(tpv_months); slot = pw/n; bw = slot*0.6
    base = Tx+ph; di = tpv_months.index("dec/25"); xd = Lx+slot*di
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    s.append(f'<rect x="{xd:.1f}" y="{Tx}" width="{WD-Rx-xd:.1f}" height="{base-Tx:.1f}" fill="#0C0C0C" opacity="0.05"/>')
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
    s.append(f'<line x1="{xd:.1f}" y1="{Tx}" x2="{xd:.1f}" y2="{base:.1f}" stroke="#0C0C0C" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.55"/>')
    s.append(f'<text x="{xd+7:.1f}" y="{Tx+10:.1f}" font-family="Geist Mono,monospace" font-size="10" letter-spacing="0.06em" fill="#3A3A3A">FIDC live →</text>')
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
    "iFood":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.04,0.12,0.15,0.15,0.15],
    "Intelbras":[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0.05],
    # Others = Truss + app / beta users (no individual anchor)
    "Others":[0.04,0.06,0.07,0.18,0.14,0.27,0.23,0.37,0.61,1.08,1.45,1.81,1.9,2.06,2.12,2.38,2.54,2.41,2.39,2.3,2.17,2.08,2.21,2.17,2.05,3.18],
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

# ---------- delinquency (90+) over time, by partner (calendar) ----------
# Point-in-time 90+ ratio (over90 balance / total balance) per CALENDAR month.
dq_labels = ["jan/25","feb/25","mar/25","apr/25","may/25","jun/25","jul/25","aug/25",
             "sep/25","oct/25","nov/25","dec/25","jan/26","feb/26","mar/26","apr/26","may/26"]
dq_order = ["Chilli Beans","Juntos Somos Mais","Cantu","Brinox","Malwee","Moura","iFood"]
N = None
dq_data = {
    "Cantu":            [0.0,0.0,0.0,0.6,0.4,3.8,12.5,14.4,21.1,26.4,25.6,33.3,40.6,37.6,17.9,16.6,8.9],
    "Moura":            [N,N,N,N,15.7,6.9,0.8,0.7,0.3,0.3,0.3,0.4,0.3,0.5,1.2,0.9,1.3],
    "Chilli Beans":     [0.0,0.0,0.0,0.2,0.0,2.7,9.2,9.0,20.1,27.1,30.0,31.7,34.3,30.4,28.7,36.3,41.1],
    "Juntos Somos Mais":[0.0,0.0,3.9,1.9,1.7,16.7,24.4,53.9,38.4,23.3,24.5,37.7,41.7,52.8,52.1,37.4,32.8],
    "Malwee":           [N,N,N,N,N,N,N,N,N,N,0.0,0.0,0.0,0.0,1.5,4.2,4.1],
    "Brinox":           [N,N,N,N,N,N,N,N,0.0,0.0,0.0,0.0,0.0,2.7,5.8,5.5,5.1],
    "iFood":            [N,N,N,N,N,N,N,N,N,N,N,N,N,0.0,0.0,0.0,0.0],
}
# company-wide point-in-time 90+ ratio
dq_agg = [0.0,0.0,0.4,0.4,0.3,4.2,10.9,13.8,21.4,23.7,22.6,24.9,25.3,22.4,19.4,20.1,17.5]
DQ_FIDC = dq_labels.index("dec/25")  # FIDC went live Dec/25
dq_legend = ('<span><i style="background:#0C0C0C;height:3px;border-radius:2px"></i>Company aggregate</span>'
             + "".join(f'<span><i style="background:{ANCHOR_COL[g]}"></i>{g}</span>' for g in dq_order))
def dq_lines():
    WD, HD = 1040, 452; Lx, Rx, Tx, Bx = 46, 60, 30, 44
    n = len(dq_labels); pw, ph = WD-Lx-Rx, HD-Tx-Bx; ymax = 60
    def X(j): return Lx + j/(n-1)*pw
    def Y(v): return Tx+ph - v/ymax*ph
    base = Y(0)
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    # FIDC-live shaded region (from Dec/25 onward)
    fx = X(DQ_FIDC)
    s.append(f'<rect x="{fx:.1f}" y="{Tx}" width="{WD-Rx-fx:.1f}" height="{ph:.1f}" fill="#0C0C0C" opacity="0.035"/>')
    s.append(f'<line x1="{fx:.1f}" y1="{Tx}" x2="{fx:.1f}" y2="{base:.1f}" stroke="#0C0C0C" stroke-width="1" stroke-dasharray="3 3" stroke-opacity="0.4"/>')
    s.append(f'<text x="{fx+5:.1f}" y="{Tx+11:.1f}" font-family="Geist Mono,monospace" font-size="8.5" fill="#6A6A6A">FIDC live</text>')
    for t in (0,20,40,60):
        s.append(f'<text x="{Lx-7}" y="{Y(t)+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="9" fill="#9a9a9a">{t}%</text>')
    s.append(f'<line x1="{Lx}" y1="{base:.1f}" x2="{WD-Rx}" y2="{base:.1f}" stroke="#C8C8C8" stroke-width="1"/>')
    for j in range(n):
        s.append(f'<text x="{X(j):.1f}" y="{HD-14}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="8" fill="#5A5A5A">{dq_labels[j]}</text>')
    # partner lines (muted context) — break across None gaps
    ends = []
    for g in dq_order:
        vals = dq_data[g]; col = ANCHOR_COL[g]
        seg = []
        for j, v in enumerate(vals):
            if v is None:
                if len(seg) >= 2:
                    s.append(f'<polyline points="{" ".join(seg)}" fill="none" stroke="{col}" stroke-width="1.7" stroke-opacity="0.5" stroke-linejoin="round" stroke-linecap="round"/>')
                seg = []
            else:
                seg.append(f"{X(j):.1f},{Y(v):.1f}")
        if len(seg) >= 2:
            s.append(f'<polyline points="{" ".join(seg)}" fill="none" stroke="{col}" stroke-width="1.7" stroke-opacity="0.5" stroke-linejoin="round" stroke-linecap="round"/>')
        je = max(j for j, v in enumerate(vals) if v is not None)
        ends.append({"x": X(je), "real": Y(vals[je]), "y": Y(vals[je]), "v": vals[je], "col": col, "hero": False})
    # company aggregate (hero)
    apts = " ".join(f"{X(j):.1f},{Y(v):.1f}" for j, v in enumerate(dq_agg))
    s.append(f'<polyline points="{apts}" fill="none" stroke="#0C0C0C" stroke-width="3.4" stroke-linejoin="round" stroke-linecap="round"/>')
    last = len(dq_agg)-1
    for j in (4,8,12,last):
        s.append(f'<circle cx="{X(j):.1f}" cy="{Y(dq_agg[j]):.1f}" r="3.6" fill="#0C0C0C"/>')
        s.append(f'<text x="{X(j):.1f}" y="{Y(dq_agg[j])-9:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="700" font-size="11" fill="#0C0C0C">{dq_agg[j]:.0f}%</text>')
    ends.append({"x": X(last), "real": Y(dq_agg[last]), "y": Y(dq_agg[last]), "v": dq_agg[last], "col": "#0C0C0C", "hero": True})
    # de-clutter end labels
    ends.sort(key=lambda e: e["y"]); prev = -99
    for e in ends:
        if e["y"] < prev+15: e["y"] = prev+15
        prev = e["y"]
    for e in ends:
        xe = e["x"]; col = e["col"]; ry = e["real"]; ly = e["y"]; val = f'{e["v"]:.0f}%'
        if e["hero"]:
            continue  # aggregate already labelled along the line
        s.append(f'<circle cx="{xe:.1f}" cy="{ry:.1f}" r="2.8" fill="{col}"/>')
        if abs(ly-ry) > 1.5:
            s.append(f'<line x1="{xe:.1f}" y1="{ry:.1f}" x2="{xe+6:.1f}" y2="{ly:.1f}" stroke="{col}" stroke-width="1" stroke-opacity="0.6"/>')
        s.append(f'<rect x="{xe+6:.1f}" y="{ly-6.5:.1f}" width="28" height="13" rx="3" fill="{col}" opacity="0.85"/>')
        s.append(f'<text x="{xe+20:.1f}" y="{ly+3:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="700" font-size="7.5" fill="#fff">{val}</text>')
    s.append('</svg>')
    return "\n".join(s)
dq_svg = dq_lines()

# ---------- revenue run rate (ARR) ----------
arr_labels = ["3Q24","4Q24","1Q25","2Q25","3Q25","4Q25","1Q26","Apr/26","May/26"]
arr_vals = [319,550,1427,1716,2077,2532,2976,3176,3721]
def arr_chart():
    WD, HD = 1040, 452; Lx, Rx, Tx, Bx = 30, 20, 58, 42
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; n = len(arr_vals); ymax = 4100
    xs = [Lx + i/(n-1)*pw for i in range(n)]
    def Y(v): return Tx+ph - v/ymax*ph
    base = Y(0); ys = [Y(v) for v in arr_vals]
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    s.append('<defs><linearGradient id="arrG" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#0C0C0C" stop-opacity="0.20"/>'
             '<stop offset="1" stop-color="#0C0C0C" stop-opacity="0.02"/></linearGradient></defs>')
    s.append(f'<line x1="{Lx}" y1="{base:.1f}" x2="{WD-Rx}" y2="{base:.1f}" stroke="#C8C8C8" stroke-width="1"/>')
    # area + growth line
    d = f"M {xs[0]:.1f},{base:.1f} " + " ".join(f"L {x:.1f},{y:.1f}" for x,y in zip(xs,ys)) + f" L {xs[-1]:.1f},{base:.1f} Z"
    s.append(f'<path d="{d}" fill="url(#arrG)"/>')
    s.append('<polyline points="%s" fill="none" stroke="#0C0C0C" stroke-width="2.8" stroke-linejoin="round" stroke-linecap="round"/>'
             % " ".join(f"{x:.1f},{y:.1f}" for x,y in zip(xs,ys)))
    # growth-multiple callout in the empty upper-left
    mult = arr_vals[-1]/arr_vals[0]
    s.append(f'<text x="{Lx+4:.1f}" y="{Tx-26:.1f}" font-family="Geist,sans-serif" font-weight="800" font-size="34" fill="#0C0C0C">{mult:.0f}×</text>')
    s.append(f'<text x="{Lx+5:.1f}" y="{Tx-10:.1f}" font-family="Geist Mono,monospace" font-size="10" letter-spacing="0.08em" fill="#8a8a8a">ARR GROWTH SINCE 3Q24</text>')
    # dots + value labels
    for i,(x,y,v) in enumerate(zip(xs,ys,arr_vals)):
        last = i == n-1
        val = f"{v:,}".replace(",", ".")
        if last:
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="none" stroke="#0C0C0C" stroke-opacity="0.18"/>')
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#0C0C0C"/>')
            s.append(f'<text x="{x:.1f}" y="{y-13:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="800" font-size="16" fill="#0C0C0C">{val}</text>')
        else:
            s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.1" fill="#0C0C0C"/>')
            s.append(f'<text x="{x:.1f}" y="{y-10:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="600" font-size="12" fill="#3A3A3A">{val}</text>')
        s.append(f'<text x="{x:.1f}" y="{HD-14:.1f}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="11" fill="#5A5A5A">{arr_labels[i]}</text>')
    s.append('</svg>')
    return "\n".join(s)
arr_svg = arr_chart()

# ---------- amortization run-off curve (real loan tape) ----------
# avg outstanding balance as % of original principal, by months on book
ro_mob  = [0,1,2,3,4,5,6,7,8]
ro_out  = [90.5,61.1,42.0,27.9,20.3,15.2,12.8,12.4,12.0]
RO_TENOR = 3.5   # mean installments
RO_DUR   = 2.1   # balance-weighted duration
def runoff_chart():
    WD, HD = 1000, 440; Lx, Rx, Tx, Bx = 40, 22, 46, 46
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; n = len(ro_mob); ymax = 100
    def X(i): return Lx + i/(n-1)*pw
    def Xv(m): return Lx + m/(n-1)*pw
    def Y(v): return Tx+ph - v/ymax*ph
    base = Y(0); xs=[X(i) for i in range(n)]; ys=[Y(v) for v in ro_out]
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    s.append('<defs><linearGradient id="roG" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#0C0C0C" stop-opacity="0.18"/>'
             '<stop offset="1" stop-color="#0C0C0C" stop-opacity="0.02"/></linearGradient></defs>')
    for t in (0,25,50,75,100):
        s.append(f'<text x="{Lx-8}" y="{Y(t)+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#9a9a9a">{t}</text>')
    s.append(f'<text x="{Lx-7:.1f}" y="{Tx-6:.1f}" text-anchor="start" font-family="Geist Mono,monospace" font-size="8.5" fill="#9a9a9a">% of principal outstanding</text>')
    s.append(f'<line x1="{Lx}" y1="{base:.1f}" x2="{WD-Rx}" y2="{base:.1f}" stroke="#C8C8C8" stroke-width="1"/>')
    # area + curve
    d = f"M {xs[0]:.1f},{base:.1f} " + " ".join(f"L {x:.1f},{y:.1f}" for x,y in zip(xs,ys)) + f" L {xs[-1]:.1f},{base:.1f} Z"
    s.append(f'<path d="{d}" fill="url(#roG)"/>')
    s.append('<polyline points="%s" fill="none" stroke="#0C0C0C" stroke-width="2.8" stroke-linejoin="round" stroke-linecap="round"/>'
             % " ".join(f"{x:.1f},{y:.1f}" for x,y in zip(xs,ys)))
    # single headline callout
    rp = 100-ro_out[2]
    s.append(f'<text x="{X(4):.1f}" y="{Y(66):.1f}" font-family="Geist,sans-serif" font-weight="800" font-size="32" fill="#0C0C0C">~{rp:.0f}%</text>')
    s.append(f'<text x="{X(4):.1f}" y="{Y(66)+18:.1f}" font-family="Geist Mono,monospace" font-size="10.5" letter-spacing="0.03em" fill="#8a8a8a">repaid by month 2</text>')
    # points + value labels
    for i,(x,y,v) in enumerate(zip(xs,ys,ro_out)):
        s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#0C0C0C"/>')
        s.append(f'<text x="{x:.1f}" y="{y-9:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="600" font-size="10.5" fill="#3A3A3A">{v:.0f}</text>')
    # x labels
    for i,m in enumerate(ro_mob):
        s.append(f'<text x="{X(i):.1f}" y="{HD-15}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="9.5" fill="#5A5A5A">M{m}</text>')
    s.append('</svg>')
    return "\n".join(s)
runoff_svg = runoff_chart()

# ---------- KPI history: tenor / duration / rate / turnover (real loan tape) ----------
kpi_labels = ["jan/25","feb/25","mar/25","apr/25","may/25","jun/25","jul/25","aug/25","sep/25","oct/25","nov/25","dec/25","jan/26","feb/26","mar/26","apr/26","may/26"]
kpi_tenor = [3.19,3.45,3.44,3.62,3.52,3.46,3.40,3.33,3.18,3.11,3.05,3.12,3.33,3.38,3.42,3.42,3.45]
kpi_dur   = [2.41,2.49,2.28,2.18,2.09,2.15,2.18,2.08,2.09,1.97,1.97,1.93,2.07,2.20,2.30,2.22,2.34]
kpi_rate  = [41.0,41.9,41.7,44.8,47.3,46.1,46.6,46.1,46.6,47.4,48.7,47.8,46.5,45.9,45.5,45.1,44.6]
kpi_turn  = [3.76,3.48,3.49,3.31,3.40,3.47,3.53,3.60,3.77,3.86,3.93,3.84,3.60,3.55,3.51,3.51,3.48]

def spark(vals):
    W, H = 480, 150; L, R, T, B = 10, 12, 16, 22
    pw, ph = W-L-R, H-T-B; n = len(vals)
    lo, hi = min(vals), max(vals); rng = (hi-lo) or 1
    ymin, ymax = lo-rng*0.40, hi+rng*0.40
    X = lambda i: L + i/(n-1)*pw
    Y = lambda v: T+ph - (v-ymin)/(ymax-ymin)*ph
    xs = [X(i) for i in range(n)]; ys = [Y(v) for v in vals]; base = T+ph
    gid = f"sp{abs(hash(tuple(vals)))%100000}"
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none">']
    s.append(f'<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
             f'<stop offset="0" stop-color="#0C0C0C" stop-opacity="0.16"/>'
             f'<stop offset="1" stop-color="#0C0C0C" stop-opacity="0.015"/></linearGradient></defs>')
    d = f"M {xs[0]:.1f},{base:.1f} " + " ".join(f"L {x:.1f},{y:.1f}" for x,y in zip(xs,ys)) + f" L {xs[-1]:.1f},{base:.1f} Z"
    s.append(f'<path d="{d}" fill="url(#{gid})"/>')
    s.append('<polyline points="%s" fill="none" stroke="#0C0C0C" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>'
             % " ".join(f"{x:.1f},{y:.1f}" for x,y in zip(xs,ys)))
    s.append(f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="7" fill="none" stroke="#0C0C0C" stroke-opacity="0.18"/>')
    s.append(f'<circle cx="{xs[-1]:.1f}" cy="{ys[-1]:.1f}" r="4" fill="#0C0C0C"/>')
    s.append(f'<text x="{xs[0]:.1f}" y="{H-6}" font-family="Geist Mono,monospace" font-size="10" fill="#9a9a9a">{kpi_labels[0]}</text>')
    s.append(f'<text x="{xs[-1]:.1f}" y="{H-6}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#9a9a9a">{kpi_labels[-1]}</text>')
    s.append('</svg>')
    return "".join(s)

def kpi_card(k, v, sub, vals):
    return (f'<div class="spark-card"><div class="k">{k}</div>'
            f'<div class="v">{v}</div><div class="s">{sub}</div>{spark(vals)}</div>')

kpi_grid = ('<div class="sparks reveal" data-stagger>'
    + kpi_card("Avg. tenor","3.5 <span style='font-size:.5em'>months</span>","mean installments", kpi_tenor)
    + kpi_card("Duration","~2.3 <span style='font-size:.5em'>months</span>","balance-weighted avg life", kpi_dur)
    + kpi_card("Avg. rate","44.6% <span style='font-size:.5em'>/yr</span>","principal-weighted", kpi_rate)
    + kpi_card("Turnover","~3.5× <span style='font-size:.5em'>/yr</span>","book recycles fast", kpi_turn)
    + '</div>')

# ---------- delinquency composition: balance by days-past-due bucket (real loan tape) ----------
ag_labels = ['nov/24','dec/24','jan/25','feb/25','mar/25','apr/25','may/25','jun/25','jul/25','aug/25','sep/25','oct/25','nov/25','dec/25','jan/26','feb/26','mar/26','apr/26','may/26']
ag_buckets = ["Em dia","1-30","31-60","61-90","91-180","181-360","360+"]
ag_data = {
  "Em dia":  [0.339,0.788,1.697,2.204,3.441,3.627,3.818,4.093,3.425,4.135,3.996,4.281,4.546,3.92,4.433,6.225,7.852,9.203,11.313],
  "1-30":    [0.0,0.015,0.012,0.368,0.21,0.55,0.585,0.198,0.529,0.326,0.408,0.61,0.6,0.329,0.56,0.299,1.112,0.777,0.611],
  "31-60":   [0.0,0.0,0.014,0.011,0.001,0.207,0.362,0.473,0.467,0.616,0.038,0.055,0.16,0.201,0.282,0.463,0.083,0.268,0.289],
  "61-90":   [0.0,0.0,0.0,0.014,0.011,0.001,0.208,0.348,0.268,0.151,0.244,0.022,0.035,0.419,0.203,0.146,0.353,0.084,0.242],
  "91-180":  [0.0,0.0,0.0,0.0,0.014,0.019,0.014,0.214,0.56,0.823,1.047,0.965,0.723,0.334,0.495,0.677,0.898,0.823,0.703],
  "181-360": [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.008,0.013,0.014,0.232,0.575,0.838,1.269,1.347,1.368,1.138,1.27,1.196],
  "360+":    [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.008,0.01,0.011,0.223,0.5,0.751],
}
AG_COL = {"Em dia":"#E4E4E4","1-30":"#F6C6C2","31-60":"#EE9A90","61-90":"#E0685C",
          "91-180":"#D11A2A","181-360":"#A01024","360+":"#6E0A1A"}
ag_pct90 = [0.0,0.0,0.0,0.0,0.4,0.4,0.3,4.2,10.9,13.8,21.4,23.7,22.6,24.9,25.3,22.4,19.4,20.1,17.5]
ag_totals = [round(sum(ag_data[b][i] for b in ag_buckets),3) for i in range(len(ag_labels))]
ag_legend = "".join(f'<span><i style="background:{AG_COL[b]};border-radius:2px;height:11px;width:14px"></i>{b}</span>' for b in ag_buckets) + '<span style="color:#8a8a8a">days past due · share of balance</span>'

def aging_chart():
    WD, HD = 1040, 452; Lx, Rx, Tx, Bx = 40, 50, 34, 44
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; n = len(ag_labels); ymax = 100
    xs = [Lx + i/(n-1)*pw for i in range(n)]
    def Y(v): return Tx+ph - v/ymax*ph
    base = Y(0); di = ag_labels.index("dec/25"); xd = xs[di]
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    # FIDC-live shaded region
    s.append(f'<rect x="{xd:.1f}" y="{Tx}" width="{WD-Rx-xd:.1f}" height="{base-Tx:.1f}" fill="#0C0C0C" opacity="0.05"/>')
    for t in (0,25,50,75,100):
        s.append(f'<text x="{Lx-7}" y="{Y(t)+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#9a9a9a">{t}</text>')
    # 100% stacked areas (bottom = current, top = most severe)
    bottoms = [0.0]*n
    for b in ag_buckets:
        tops = [bottoms[i] + (ag_data[b][i]/ag_totals[i]*100 if ag_totals[i] else 0) for i in range(n)]
        top_pts = " ".join(f"{xs[i]:.1f},{Y(tops[i]):.1f}" for i in range(n))
        bot_pts = " ".join(f"{xs[i]:.1f},{Y(bottoms[i]):.1f}" for i in range(n-1,-1,-1))
        s.append(f'<polygon points="{top_pts} {bot_pts}" fill="{AG_COL[b]}" stroke="#FFFFFF" stroke-width="0.5"/>')
        bottoms = tops
    # 90+ boundary (top of the 61-90 band) — bold line delineating the 90+ region
    bnd = " ".join(f"{xs[i]:.1f},{Y(100-ag_pct90[i]):.1f}" for i in range(n))
    s.append(f'<polyline points="{bnd}" fill="none" stroke="#0C0C0C" stroke-width="2.4" stroke-linejoin="round"/>')
    # current 90+ end pill
    ey = Y(100-ag_pct90[-1])
    s.append(f'<circle cx="{xs[-1]:.1f}" cy="{ey:.1f}" r="3.2" fill="#0C0C0C"/>')
    s.append(f'<rect x="{xs[-1]+5:.1f}" y="{ey-9:.1f}" width="34" height="17" rx="3" fill="#0C0C0C"/>')
    s.append(f'<text x="{xs[-1]+22:.1f}" y="{ey+3:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="700" font-size="9.5" fill="#fff">{ag_pct90[-1]:.0f}%</text>')
    s.append(f'<text x="{xs[-1]+5:.1f}" y="{Tx+10:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="9" fill="#7A1020">90+ region ▲</text>')
    # total book R$ labels along the top
    for i in range(0, n, 3):
        s.append(f'<text x="{xs[i]:.1f}" y="{Tx-6:.1f}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="8" fill="#9a9a9a">{ag_totals[i]:.1f}</text>')
    s.append(f'<text x="{xs[-1]:.1f}" y="{Tx-6:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="700" font-size="9" fill="#0C0C0C">R${ag_totals[-1]:.1f}M</text>')
    # FIDC divider + label
    s.append(f'<line x1="{xd:.1f}" y1="{Tx}" x2="{xd:.1f}" y2="{base:.1f}" stroke="#0C0C0C" stroke-width="1.2" stroke-dasharray="4 4" opacity="0.55"/>')
    s.append(f'<text x="{xd+7:.1f}" y="{base-7:.1f}" font-family="Geist Mono,monospace" font-size="10" letter-spacing="0.06em" fill="#3A3A3A">FIDC live →</text>')
    for i in range(0, n, 3):
        s.append(f'<text x="{xs[i]:.1f}" y="{HD-15}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="9" fill="#5A5A5A">{ag_labels[i]}</text>')
    s.append('</svg>')
    return "\n".join(s)
aging_svg = aging_chart()

# ---------- credit economics waterfall ----------
# (label, y0, y1, color, value, label_pos)
wf_steps = [("Aggregate Yield",0,95.8,"#0C0C0C","95.8%","top"),
            ("Direct Costs",87.8,95.8,"#C0143C","−8.0%","bot"),
            ("Funding Cost",64.8,87.8,"#C0143C","−23.0%","bot"),
            ("NIM",0,64.8,"#0C0C0C","64.8%","top"),
            ("Capital Losses (NPL)",39.8,64.8,"#C0143C","−25.0%","bot"),
            ("Risk-Adjusted NIM",0,39.8,"#0C0C0C","39.8%","top")]
wf_levels = [95.8,87.8,64.8,64.8,39.8]   # connector level between bar i and i+1
def waterfall():
    WD, HD = 1000, 504; Lx, Rx, Tx, Bx = 18, 18, 44, 48
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; ymax = 104; n = len(wf_steps); slot = pw/n; bw = slot*0.54
    def Y(v): return Tx+ph - v/ymax*ph
    def Cx(i): return Lx+slot*i+slot/2
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    # connectors
    for i in range(n-1):
        y = Y(wf_levels[i])
        s.append(f'<line x1="{Cx(i)+bw/2:.1f}" y1="{y:.1f}" x2="{Cx(i+1)-bw/2:.1f}" y2="{y:.1f}" stroke="#C8C8C8" stroke-width="1"/>')
    for i, (lab, y0, y1, col, val, pos) in enumerate(wf_steps):
        cx = Cx(i); x = cx-bw/2; yt = Y(max(y0, y1)); yb = Y(min(y0, y1)); h = yb-yt
        s.append(f'<rect x="{x:.1f}" y="{yt:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="2" fill="{col}"/>')
        if pos == "top":
            s.append(f'<text x="{cx:.1f}" y="{yt-9:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="700" font-size="16" fill="#0C0C0C">{val}</text>')
        else:
            s.append(f'<text x="{cx:.1f}" y="{yb+19:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="600" font-size="13" fill="#2E2E2E">{val}</text>')
        s.append(f'<text x="{cx:.1f}" y="{HD-14}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="9" fill="#5A5A5A">{lab}</text>')
    s.append('</svg>')
    return "\n".join(s)
wf_svg = waterfall()

# ---------- credit economics: yield-allocation bar ----------
def econ_bar():
    WD, HD = 1040, 340; Lx, Rx, Tx, Bx = 22, 22, 74, 96
    pw = WD-Lx-Rx; barH = 66; y = Tx
    segs = [("Risk-adjusted NIM", 39.8, "#0C0C0C", "39.8%"),
            ("Capital losses (NPL)", 25.0, "#C0143C", "−25.0%"),
            ("Funding cost", 23.0, "#8E1024", "−23.0%"),
            ("Direct costs", 8.0, "#C98B96", "−8.0%")]
    total = sum(v for _, v, _, _ in segs)
    def X(v): return Lx + v/total*pw
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    cum = 0
    for name, val, col, lab in segs:
        x0 = X(cum); w = X(cum+val)-x0; cx = x0+w/2
        s.append(f'<rect x="{x0:.1f}" y="{y}" width="{w:.1f}" height="{barH}" fill="{col}"/>')
        s.append(f'<text x="{cx:.1f}" y="{y-22:.1f}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="9.5" fill="#5A5A5A">{name}</text>')
        s.append(f'<text x="{cx:.1f}" y="{y-7:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="700" font-size="15" fill="#0C0C0C">{lab}</text>')
        cum += val
    by = y+barH
    def bracket(a, b, lab, lvl):
        ya = by+12+lvl*30; xa = X(a); xb = X(b)
        return (f'<path d="M {xa:.1f} {ya:.1f} L {xa:.1f} {ya+6:.1f} L {xb:.1f} {ya+6:.1f} L {xb:.1f} {ya:.1f}" fill="none" stroke="#0C0C0C" stroke-width="1.2"/>'
                f'<text x="{(xa+xb)/2:.1f}" y="{ya+22:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="700" font-size="13" fill="#0C0C0C">{lab}</text>')
    s.append(bracket(0, 39.8, "Risk-adjusted NIM · 39.8%", 0))
    s.append(bracket(0, 64.8, "NIM · 64.8%", 1))
    s.append(f'<text x="{Lx}" y="{y-40:.1f}" font-family="Geist Mono,monospace" font-size="11" letter-spacing="0.12em" fill="#8a8a8a">GROSS YIELD · 95.8%</text>')
    s.append('</svg>')
    return "\n".join(s)
econ_svg = econ_bar()

# ---------- 90+ concentration by source ----------
conc90 = [("Chilli Beans",1400985,52.9,7.6),("Juntos Somos Mais",729211,27.5,12.7),
          ("Cantu",390897,14.7,3.8),("Malwee",74723,2.8,1.5),("Moura",34412,1.3,0.6),("Brinox",19981,0.8,1.3)]
def conc_table():
    rows = ""
    for name, saldo, sh, cdr in conc90:
        rows += (f'<tr><td>{name}</td><td>{f"{saldo:,}".replace(",", ".")}</td>'
                 f'<td>{sh:.1f}%</td><td class="cdr">{cdr:.1f}%</td></tr>')
    rows += ('<tr class="total"><td>Total carteira</td><td>2.650.209</td><td>100,0%</td><td class="cdr">5,7%</td></tr>')
    return (f'<table class="ctab"><thead><tr><th>By source</th><th>90+ (R$)</th>'
            f'<th>% of 90+</th><th>CDR</th></tr></thead><tbody>{rows}</tbody></table>')
conc_tbl = conc_table()

def hbar90():
    WD, HD = 1040, 470; Lx, Rx, Tx, Bx = 178, 64, 22, 40
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; xmax = 60; n = len(conc90); rowh = ph/n; bh = 17
    def X(v): return Lx + v/xmax*pw
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    s.append('<defs><linearGradient id="h90g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#CFCFCF"/><stop offset="1" stop-color="#ADADAD"/></linearGradient>'
             '<linearGradient id="h90r" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#D8254A"/><stop offset="1" stop-color="#B30E36"/></linearGradient></defs>')
    s.append(f'<line x1="{Lx}" y1="{Tx}" x2="{Lx}" y2="{Tx+ph:.1f}" stroke="#C8C8C8" stroke-width="1"/>')
    for t in range(0, 61, 10):
        s.append(f'<text x="{X(t):.1f}" y="{HD-14}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="9" fill="#9a9a9a">{t}%</text>')
    for i, (name, saldo, sh, cdr) in enumerate(conc90):
        cy = Tx + rowh*i + rowh/2
        s.append(f'<text x="{Lx-14:.1f}" y="{cy+3:.1f}" text-anchor="end" font-family="Geist,sans-serif" font-weight="600" font-size="12.5" fill="#0C0C0C">{name}</text>')
        gy = cy-bh-2; ry = cy+2
        s.append(f'<rect x="{Lx:.1f}" y="{gy:.1f}" width="{max(X(sh)-Lx,1):.1f}" height="{bh}" rx="3" fill="url(#h90g)"/>')
        s.append(f'<text x="{X(sh)+6:.1f}" y="{gy+bh-4:.1f}" font-family="Geist,sans-serif" font-weight="700" font-size="10.5" fill="#6A6A6A">{round(sh)}%</text>')
        s.append(f'<rect x="{Lx:.1f}" y="{ry:.1f}" width="{max(X(cdr)-Lx,1):.1f}" height="{bh}" rx="3" fill="url(#h90r)"/>')
        s.append(f'<text x="{X(cdr)+6:.1f}" y="{ry+bh-4:.1f}" font-family="Geist,sans-serif" font-weight="700" font-size="10.5" fill="#B30E36">{round(cdr)}%</text>')
    s.append('</svg>')
    return "\n".join(s)
conc_svg = hbar90()
conc_legend = ('<span><i style="background:#B5B5B5"></i>% of 90+</span>'
               '<span><i style="background:#C0143C"></i>CDR (90+ ÷ principal originated)</span>')

def _heat(cdr):
    t = min(cdr/18.0, 1.0); a = (244,166,184); b = (122,10,35)
    return "#%02X%02X%02X" % tuple(round(a[k]+(b[k]-a[k])*t) for k in range(3))

def conc_rows():
    maxsh = max(sh for _, _, sh, _ in conc90)
    out = ['<div class="r90 head"><span>By source</span><span class="r-val">90+ (R$)</span>'
           '<span>Share of 90+</span><span class="r-pct">%</span><span style="text-align:center">CDR</span></div>']
    for name, saldo, sh, cdr in conc90:
        w = sh/maxsh*100; sval = f"{saldo:,}".replace(",", ".")
        out.append(f'<div class="r90"><span class="r-name"><i class="r-dot" style="background:{ANCHOR_COL.get(name,"#999")}"></i>{name}</span><span class="r-val">{sval}</span>'
                   f'<span class="r-track"><span class="r-fill" style="width:{w:.0f}%"></span></span>'
                   f'<span class="r-pct">{sh:.1f}%</span>'
                   f'<span class="r-cdr" style="background:{_heat(cdr)}">{cdr:.1f}%</span></div>')
    out.append('<div class="r90 total"><span class="r-name">Total carteira</span><span class="r-val">2.650.209</span>'
               '<span></span><span class="r-pct">100%</span>'
               f'<span class="r-cdr" style="background:{_heat(5.7)}">5,7%</span></div>')
    return "".join(out)
conc_rows_html = conc_rows()

# ---------- 90+ by vintage (origination month) ----------
vint = [("nov/24",10090,0.4,2.9,0),("dez/24",29297,1.1,4.8,0),("jan/25",60118,2.3,5.0,0),
        ("fev/25",256352,9.7,17.6,1),("mar/25",329536,12.4,17.7,1),("abr/25",129270,4.9,7.0,0),
        ("mai/25",293097,11.1,15.2,1),("jun/25",150226,5.7,8.2,0),("jul/25",66312,2.5,4.6,0),
        ("ago/25",208840,7.9,9.2,0),("set/25",160934,6.1,7.2,0),("out/25",333655,12.6,13.1,1),
        ("nov/25",184933,7.0,7.5,0),("dez/25",193652,7.3,7.2,0),("jan/26",210343,7.9,6.2,0),
        ("fev/26",33555,1.3,0.9,0),("mar/26",None,0.0,0.0,0),("abr/26",None,0.0,0.0,0),("mai/26",None,0.0,0.0,0)]
def vint_table():
    rows = ""
    for m, saldo, sh, cdr, hi in vint:
        sval = f"{saldo:,}".replace(",", ".") if saldo else "–"
        cls = ' class="hi"' if hi else ''
        rows += f'<tr{cls}><td>{m}</td><td>{sval}</td><td>{sh:.1f}%</td><td class="cdr">{cdr:.1f}%</td></tr>'
    rows += '<tr class="total"><td>Total</td><td>2.650.209</td><td>100,0%</td><td class="cdr">5,7%</td></tr>'
    return (f'<table class="ctab sm"><thead><tr><th>By vintage</th><th>90+ (R$)</th>'
            f'<th>% of 90+</th><th>CDR</th></tr></thead><tbody>{rows}</tbody></table>')
vint_tbl = vint_table()
def cdr_vintage_chart():
    WD, HD = 1040, 470; Lx, Rx, Tx, Bx = 40, 16, 34, 46
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; ymax = 20; n = len(vint); slot = pw/n; bw = slot*0.58
    def Y(v): return Tx+ph - v/ymax*ph
    def Cx(i): return Lx+slot*i+slot/2
    base = Y(0)
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    s.append('<defs>'
             '<linearGradient id="cdrN" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E45C74"/><stop offset="1" stop-color="#C0143C"/></linearGradient>'
             '<linearGradient id="cdrW" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#9E1F38"/><stop offset="1" stop-color="#6E0A20"/></linearGradient>'
             '<linearGradient id="cdrArea" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C0143C" stop-opacity="0.16"/><stop offset="1" stop-color="#C0143C" stop-opacity="0"/></linearGradient>'
             '<filter id="cdrSh" x="-25%" y="-25%" width="150%" height="150%"><feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#7A0A23" flood-opacity="0.22"/></filter>'
             '</defs>')
    # soft band behind worst block (fev/25..mai/25 = i 3..6)
    bx0 = Lx + 3*slot; bx1 = Lx + 7*slot
    s.append(f'<rect x="{bx0:.1f}" y="{Tx}" width="{bx1-bx0:.1f}" height="{base-Tx:.1f}" rx="6" fill="#C0143C" opacity="0.05"/>')
    s.append(f'<text x="{(bx0+bx1)/2:.1f}" y="{Tx-6:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="600" font-size="9.5" fill="#8E0E2E">worst vintages</text>')
    for t in (0,5,10,15,20):
        s.append(f'<text x="{Lx-7}" y="{Y(t)+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="9" fill="#9a9a9a">{t}%</text>')
    s.append(f'<line x1="{Lx}" y1="{base:.1f}" x2="{WD-Rx}" y2="{base:.1f}" stroke="#C8C8C8" stroke-width="1"/>')
    # trend area + line over the tops (artistic arc)
    nz = [(Cx(i), Y(c)) for i,(m,sa,sh,c,hi) in enumerate(vint) if c > 0]
    area = f"M {nz[0][0]:.1f},{base:.1f} " + " ".join(f"L {x:.1f},{y:.1f}" for x,y in nz) + f" L {nz[-1][0]:.1f},{base:.1f} Z"
    s.append(f'<path d="{area}" fill="url(#cdrArea)"/>')
    s.append('<polyline points="%s" fill="none" stroke="#8E0E2E" stroke-width="1.5" stroke-opacity="0.35" stroke-linejoin="round"/>' % " ".join(f"{x:.1f},{y:.1f}" for x,y in nz))
    # bars
    for i, (m, saldo, sh, cdr, hi) in enumerate(vint):
        cx = Cx(i); x = cx-bw/2; y = Y(cdr); h = base-y
        grad = "url(#cdrW)" if hi else "url(#cdrN)"
        if cdr > 0:
            s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{h:.1f}" rx="3" fill="{grad}" filter="url(#cdrSh)"/>')
            s.append(f'<text x="{cx:.1f}" y="{y-6:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="700" font-size="8" fill="#0C0C0C">{cdr:.0f}%</text>')
        s.append(f'<text x="{cx:.1f}" y="{HD-13}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="7.5" fill="#5A5A5A">{m}</text>')
    # portfolio average line
    ya = Y(5.7)
    s.append(f'<line x1="{Lx}" y1="{ya:.1f}" x2="{WD-Rx}" y2="{ya:.1f}" stroke="#0C0C0C" stroke-width="1" stroke-dasharray="3 4" opacity="0.5"/>')
    s.append(f'<text x="{WD-Rx:.1f}" y="{ya-5:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="9" fill="#6A6A6A">portfolio avg · 5,7%</text>')
    s.append('</svg>')
    return "\n".join(s)
cdr_vint_svg = cdr_vintage_chart()

def _heat(cdr):
    t = min(cdr/18.0, 1.0); a = (244,166,184); b = (122,10,35)
    return "#%02X%02X%02X" % tuple(round(a[k]+(b[k]-a[k])*t) for k in range(3))

def bubble_vintage():
    WD, HD = 1040, 480; Lx, Rx, Tx, Bx = 44, 28, 48, 50
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; ymax = 20; n = len(vint)
    def X(i): return Lx + (i+0.5)/n*pw
    def Y(v): return Tx+ph - v/ymax*ph
    def R(saldo): return 0.05*(saldo**0.5)
    base = Y(0)
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    # worst-block shading (fev/25 .. mai/25 = i 3..6)
    bx0 = Lx + 3/n*pw; bx1 = Lx + 7/n*pw
    s.append(f'<rect x="{bx0:.1f}" y="{Tx}" width="{bx1-bx0:.1f}" height="{base-Tx:.1f}" fill="#C0143C" opacity="0.05"/>')
    s.append(f'<text x="{(bx0+bx1)/2:.1f}" y="{Tx-6:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="600" font-size="10" fill="#8E0E2E">worst vintages</text>')
    for t in (0,5,10,15,20):
        s.append(f'<text x="{Lx-7}" y="{Y(t)+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="9" fill="#9a9a9a">{t}%</text>')
    s.append(f'<line x1="{Lx}" y1="{base:.1f}" x2="{WD-Rx}" y2="{base:.1f}" stroke="#C8C8C8" stroke-width="1"/>')
    ya = Y(5.7)
    s.append(f'<line x1="{Lx}" y1="{ya:.1f}" x2="{WD-Rx}" y2="{ya:.1f}" stroke="#0C0C0C" stroke-width="1" stroke-dasharray="2 4" opacity="0.45"/>')
    s.append(f'<text x="{WD-Rx:.1f}" y="{ya-5:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="9" fill="#6A6A6A">portfolio avg · 5,7%</text>')
    s.append(f'<text x="{X(16):.1f}" y="{Y(2.6):.1f}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="9" fill="#5A5A5A">recent ↓ improving</text>')
    # size legend (top-left)
    s.append(f'<text x="{Lx+4:.1f}" y="{Tx+8:.1f}" font-family="Geist Mono,monospace" font-size="8.5" fill="#8a8a8a">90+ balance (R$)</text>')
    lx = Lx+14
    for sv, lb in [(50000,"50k"),(150000,"150k"),(330000,"330k")]:
        rr = R(sv); cyl = Tx+30
        s.append(f'<circle cx="{lx+rr:.1f}" cy="{cyl:.1f}" r="{rr:.1f}" fill="none" stroke="#B0B0B0" stroke-width="1"/>')
        s.append(f'<text x="{lx+rr:.1f}" y="{cyl+rr+9:.1f}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="7.5" fill="#9a9a9a">{lb}</text>')
        lx += rr*2 + 18
    # stems + heat bubbles
    for i, (m, saldo, sh, cdr, hi) in enumerate(vint):
        cx = X(i)
        if saldo:
            cy = Y(cdr); r = R(saldo); col = _heat(cdr)
            s.append(f'<line x1="{cx:.1f}" y1="{base:.1f}" x2="{cx:.1f}" y2="{cy:.1f}" stroke="#DADADA" stroke-width="1"/>')
            s.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{col}" stroke="#fff" stroke-width="1"/>')
            s.append(f'<text x="{cx:.1f}" y="{cy-r-4:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="700" font-size="8.5" fill="#0C0C0C">{cdr:.0f}%</text>')
        s.append(f'<text x="{cx:.1f}" y="{HD-14}" text-anchor="middle" font-family="Geist Mono,monospace" font-size="7.5" fill="#5A5A5A">{m}</text>')
    s.append('</svg>')
    return "\n".join(s)
bubble_svg = bubble_vintage()


STYLE = """<style>
.chartframe { padding:1vh 0 0; background:transparent; border:none; }
.chart { width:100%; height:auto; display:block; }
.slide { padding-left:3vw; padding-right:3vw; }
.slide.vcenter { padding-bottom:6.5vh; }
.slide-head .sub { white-space:nowrap; max-width:none; }
.slide-head h1 { max-width:86%; }
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
.metrics.compact { grid-template-columns:1fr 1fr; gap:1vw; margin-top:1.4vh; }
.metrics.compact .metric { padding:1.5vh 1vw; border-radius:12px; }
.metrics.compact .k { font-size:9px; }
.metrics.compact .v { font-size:clamp(18px,1.7vw,28px); }
.sparks { display:grid; grid-template-columns:1fr 1fr; gap:2.2vh 3vw; margin-top:2.6vh; }
.spark-card .k { font-family:var(--font-mono); font-size:10px; letter-spacing:.14em; text-transform:uppercase; color:#5A5A5A; }
.spark-card .v { font-family:var(--font-sans); font-weight:700; font-size:clamp(24px,2.5vw,40px); letter-spacing:-.02em; margin-top:.3vh; line-height:1; }
.spark-card .s { font-family:var(--font-sans); font-size:12.5px; color:#2E2E2E; margin-top:.5vh; }
.spark-card svg { width:100%; height:auto; display:block; margin-top:1vh; }
.bp-badge { display:inline-flex; align-items:center; gap:.5em; background:#0C0C0C; color:#FAFAFA; font-family:var(--font-mono); font-size:10.5px; letter-spacing:.14em; text-transform:uppercase; padding:.9vh 1vw; border-radius:8px; margin-bottom:1.4vh; }
.bp-badge::before { content:''; width:7px; height:7px; border-radius:50%; background:#FAFAFA; }
.metrics.vstack { grid-template-columns:1fr; gap:0; margin-top:1.2vh; }
.metrics.vstack .metric { border:none; border-radius:0; padding:1.9vh 0; border-top:1px solid rgba(12,12,12,.12); }
.metrics.vstack .metric:first-child { border-top:none; }
.metrics.vstack .v { font-size:clamp(24px,2.4vw,38px); margin-top:.4vh; }
.metrics.vstack .s { margin-top:.5vh; }
.metrics.compact .s { font-size:11px; margin-top:.4vh; }
.arr-cap { font-family:var(--font-mono); font-size:10px; letter-spacing:.14em; text-transform:uppercase; color:#8a8a8a; margin-bottom:.6vh; }
.wf-wrap { display:grid; grid-template-columns:1fr 1.55fr; align-items:center; gap:3vw; margin-top:2vh; }
.wf-title { font-family:var(--font-sans); font-weight:500; font-size:clamp(30px,3.6vw,56px); letter-spacing:-.03em; line-height:1.04; color:var(--ink); }
.wf-title b { display:block; font-weight:800; }
.ctab { width:100%; border-collapse:collapse; font-family:var(--font-sans); font-size:clamp(12px,1vw,15px); }
.ctab th { font-family:var(--font-mono); font-size:9px; letter-spacing:.08em; text-transform:uppercase; color:#fff; background:#0C0C0C; padding:.9vh .8vw; text-align:right; }
.ctab th:first-child { text-align:left; }
.ctab td { padding:.85vh .8vw; border-bottom:1px solid rgba(12,12,12,.1); text-align:right; color:#2E2E2E; }
.ctab td:first-child { text-align:left; font-weight:600; color:var(--ink); }
.ctab .cdr { color:#C0143C; font-weight:600; }
.ctab tr.total td { font-weight:700; color:var(--ink); border-top:2px solid #0C0C0C; border-bottom:none; }
.ctab.sm th, .ctab.sm td { padding:.42vh .7vw; font-size:clamp(9.5px,.8vw,12px); }
.ctab tr.hi td { background:rgba(192,20,60,.08); }
.r90 { display:grid; grid-template-columns:170px 112px 1fr 52px 72px; align-items:center; gap:1.4vw; padding:1.55vh 0; border-bottom:1px solid rgba(12,12,12,.1); }
.r90.head { border-bottom:2px solid #0C0C0C; padding:0 0 1vh; }
.r90.head span { font-family:var(--font-mono); font-size:10px; letter-spacing:.12em; text-transform:uppercase; color:#8a8a8a; }
.r90.total { border-top:2px solid #0C0C0C; border-bottom:none; }
.r90 .r-name { display:flex; align-items:center; gap:.8vw; font-family:var(--font-sans); font-weight:600; font-size:clamp(14px,1.25vw,20px); color:var(--ink); }
.r90 .r-dot { width:16px; height:16px; border-radius:5px; flex-shrink:0; }
.r90 .r-val { font-family:var(--font-mono); font-size:clamp(12px,1vw,15px); color:#2E2E2E; text-align:right; }
.r90 .r-track { height:18px; background:rgba(12,12,12,.06); border-radius:100px; overflow:hidden; }
.r90 .r-fill { display:block; height:100%; border-radius:100px; background:linear-gradient(90deg,#C8C8C8,#A6A6A6); }
.r90 .r-pct { font-family:var(--font-sans); font-weight:700; font-size:clamp(12px,1vw,15px); color:#2E2E2E; text-align:right; }
.r90 .r-cdr { font-family:var(--font-sans); font-weight:700; font-size:12.5px; color:#fff; text-align:center; padding:4px 0; border-radius:7px; }
.r90.total .r-name, .r90.total .r-val, .r90.total .r-pct { font-weight:700; color:var(--ink); }
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
  <p class="sub">Monthly TPV by rail (R$M) — migrating from the legacy rail to PIX · FIDC live Dec-25.</p></div>
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

<!-- CREDIT ECONOMICS (yield allocation) -->
<section class="slide theme-light vcenter" data-num="04">
  <div class="chapter-mark light-mark"><span class="chapter-num">03</span><span class="chapter-divider"></span><span class="chapter-year">1Q26</span></div>
  <div class="slide-head reveal"><h1>Credit <span class="accent">economics.</span></h1>
  <p class="sub">NIM bridge — 1Q26, annualized (% of aggregate yield).</p></div>
  <div class="chartframe reveal">{wf_svg}</div>
  <div class="illus">1Q26 annualized · % of aggregate yield · NIM bridge</div>
</section>

<!-- 4 — CDR BY VINTAGE (removed per request) -->

<!-- 5 — FPD -->
<section class="slide theme-light vcenter" data-num="05">
  <div class="chapter-mark light-mark"><span class="chapter-num">04</span><span class="chapter-divider"></span><span class="chapter-year">Risk · origination</span></div>
  <div class="slide-head reveal"><h1>FPD 30 <span class="accent">by month.</span></h1>
  <p class="sub">First-payment default — value late on the 1st installment ÷ total.</p></div>
  <div class="two-col reveal">
    <div class="chartframe">{fpd_svg}
      <div class="legend"><span><i style="background:#0C0C0C"></i>in target (&le; 5%)</span><span><i style="background:#D11A2A"></i>breach (&gt; 5%)</span><span style="color:#8a8a8a">dashed = underwriting target</span></div>
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

<!-- DELINQUENCY OVER TIME, BY PARTNER -->
<section class="slide theme-light vcenter" data-num="07">
  <div class="chapter-mark light-mark"><span class="chapter-num">06</span><span class="chapter-divider"></span><span class="chapter-year">Risk · 90+ over time</span></div>
  <div class="slide-head reveal"><h1>Delinquency <span class="accent">over time.</span></h1>
  <p class="sub">BNPL only · point-in-time 90+ rate by calendar month, per partner — FIDC live from Dec-25.</p></div>
  <div class="blegend reveal">{dq_legend}</div>
  <div class="chartframe reveal">{dq_svg}</div>
  <div class="illus">Source: BNPL loan tape only — 90+ balance ÷ outstanding balance, monthly</div>
</section>

<!-- WHERE DOES 90+ COME FROM -->
<section class="slide theme-light vcenter" data-num="06">
  <div class="chapter-mark light-mark"><span class="chapter-num">05</span><span class="chapter-divider"></span><span class="chapter-year">Risk · concentration</span></div>
  <div class="slide-head reveal"><h1>Where does the <span class="accent">90+ come from?</span></h1>
  <p class="sub">Over90 by source — R$ 2.65M decomposed (May/26). CDR = 90+ ÷ principal originated.</p></div>
  <div class="reveal" style="margin-top:2vh;">{conc_rows_html}</div>
  <div class="blegend reveal" style="margin-top:1.6vh"><span><i style="background:#A6A6A6"></i>bar = share of the 90+ pool</span><span><i style="background:#B30E36"></i>chip = CDR · severity (darker = higher)</span></div>
  <div class="illus">Source: PIX/boleto loan tape · over90 balance May/26</div>
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

<!-- FIDC LOAN BOOK GROWTH (off-balance) -->
<section class="slide theme-light vcenter" data-num="07">
  <div class="chapter-mark light-mark"><span class="chapter-num">06</span><span class="chapter-divider"></span><span class="chapter-year">FIDC · loan book growth</span></div>
  <div class="slide-head reveal"><h1>FIDC loan book <span class="accent">growth.</span></h1>
  <p class="sub">Outstanding balance by anchor (R$M) — FIDC carve-out since Dec-25.</p>
  <span class="tag-pill">Off-balance · FIDC</span></div>
  <div class="blegend reveal">{anchor_legend}</div>
  <div class="chartframe reveal">{lb_off_svg}</div>
  <div class="illus">Source: PIX/boleto loan tape · Dec/25–May/26 (FIDC)</div>
</section>

<!-- 8 — TENOR & DURATION -->
<section class="slide theme-light vcenter" data-num="08">
  <div class="chapter-mark light-mark"><span class="chapter-num">07</span><span class="chapter-divider"></span><span class="chapter-year">Portfolio · tenor</span></div>
  <div class="slide-head reveal"><h1>Tenor, rate & <span class="accent">turnover.</span></h1>
  <p class="sub">A short, fast-rotating book — key portfolio metrics, month by month.</p></div>
  {kpi_grid}
  <div class="illus">Source: PIX/boleto loan tape · monthly · Jan/25–May/26</div>
</section>

<!-- 9 — DELINQUENCY COMPOSITION (aging) -->
<section class="slide theme-light vcenter" data-num="09">
  <div class="chapter-mark light-mark"><span class="chapter-num">08</span><span class="chapter-divider"></span><span class="chapter-year">Risk · aging</span></div>
  <div class="slide-head reveal"><h1>Delinquency <span class="accent">composition.</span></h1>
  <p class="sub">Outstanding balance by days-past-due bucket — share over time, R$M on top.</p></div>
  <div class="blegend reveal">{ag_legend}</div>
  <div class="chartframe reveal">{aging_svg}</div>
  <div class="illus">Source: BNPL loan tape only · balance by DPD bucket · monthly · 90+ region above the bold line</div>
</section>

<!-- COMPANY — RUN RATE + CORPORATE BACKING -->
<section class="slide theme-light vcenter" data-num="10">
  <div class="chapter-mark light-mark"><span class="chapter-num">09</span><span class="chapter-divider"></span><span class="chapter-year">Company</span></div>
  <div class="slide-head reveal"><h1>Corporate-backed <span class="accent">leverage.</span></h1>
  <p class="sub">Revenue run rate (US$k) and the balance sheet behind the leverage.</p></div>
  <div class="two-col reveal" style="grid-template-columns:1.45fr 1fr; align-items:center;">
    <div>
      <div class="arr-cap">Revenue run rate · US$ thousands · FX R$ 5.00/US$</div>
      <div class="chartframe">{arr_svg}</div>
    </div>
    <div>
      <span class="bp-badge">Business Plan assumptions</span>
      <div class="metrics vstack" data-stagger>
        {metric("Runway","18 <span style='font-size:.5em'>mo</span>","at current burn")}
        {metric("Expected TPV","R$ 25M <span style='font-size:.5em'>/mo</span>","by Dec/26")}
        {metric("Credit portfolio","R$ 71M","expected · Dec/26")}
      </div>
    </div>
  </div>
  <div class="illus">Revenue run rate (actual) · forward figures per Business Plan</div>
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
