#!/usr/bin/env python3
"""Generate slides.html for the Robbin credit / FIDC institutional deck (EN).
Loan-tape figures are real; structural / corporate figures are flagged WIP.
Charts are hand-built SVG to match the deck design system."""
import os, re

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
        s.append(f'<line x1="{Lx}" y1="{y:.1f}" x2="{W-Rx}" y2="{y:.1f}" stroke="#ECECEC" stroke-width="1"/>')
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


def metric(k, v, s, wip=False):
    w = '<div class="wip" style="margin-top:1vh">WIP · to confirm</div>' if wip else ''
    return f'<div class="metric"><div class="k">{k}</div><div class="v">{v}</div><div class="s">{s}</div>{w}</div>'


# ---------- monthly TPV / origination by rail (real) ----------
tpv_months = ["aug/24","sep/24","oct/24","nov/24","dec/24","jan/25","feb/25","mar/25","apr/25","may/25","jun/25","jul/25","aug/25","sep/25","oct/25","nov/25","dec/25","jan/26","feb/26","mar/26","apr/26","may/26"]
_cartao = [1.43,4.93,4.54,3.66,3.14,2.80,3.54,5.51,4.95,5.48,6.06,6.63,8.21,12.12,8.31,9.23,8.02,5.99,3.12,3.33,2.34,0.34]
_boleto = [0.17,0.48,2.25,1.56,2.56,2.26,2.66,2.75,2.23,2.27,1.97,1.67,2.21,3.32,4.25,3.27,2.89,2.19,1.86,3.11,2.00,1.86]
_pix    = [0,0,0,0,0,0,0,0,0,0.01,0.02,0.05,0.60,0.27,0.34,0.47,0.25,0.38,1.31,2.39,1.46,3.83]
tpv_order = ["Cartão","PIX Rails"]   # PIX Rails = Boleto + Pix
TPV_COL = {"Cartão":"#CBCBCB","PIX Rails":"#0C0C0C"}
tpv_data = {"Cartão":_cartao, "PIX Rails":[b+p for b,p in zip(_boleto,_pix)]}

def tpv_chart():
    WD, HD = 1040, 432; Lx, Rx, Tx, Bx = 40, 12, 24, 46
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; ymax = 17; n = len(tpv_months); slot = pw/n; bw = slot*0.6
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    for t in (0,4,8,12,16):
        y = Tx+ph - t/ymax*ph
        s.append(f'<line x1="{Lx}" y1="{y:.1f}" x2="{WD-Rx}" y2="{y:.1f}" stroke="#ECECEC" stroke-width="1"/>')
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
_pm = ['2024-03','2024-04','2024-05','2024-06','2024-07','2024-08','2024-09','2024-10','2024-11','2024-12','2025-01','2025-02','2025-03','2025-04','2025-05','2025-06','2025-07','2025-08','2025-09','2025-10','2025-11','2025-12','2026-01','2026-02','2026-03','2026-04','2026-05','2026-06']
_MON = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
port_labels = [f"{_MON[int(m.split('-')[1])-1]}/{m.split('-')[0][2:]}" for m in _pm]
port_order = ["Cantu","Moura","Chilli Beans","Juntos Somos Mais","Malwee","Others"]
PORT_COL = {"Cantu":"#5B2E91","Moura":"#2563B0","Chilli Beans":"#E11D48",
            "Juntos Somos Mais":"#8FA31E","Malwee":"#1F7A3D","Others":"#B5B5B5"}
port_data = {
    "Cantu":[0.0,0.0,0.21,0.59,1.36,2.31,6.47,9.06,10.5,10.87,11.21,11.62,11.99,12.43,13.73,15.05,15.4,15.7,17.28,17.05,15.61,14.29,13.53,12.53,11.64,10.29,10.61,10.33],
    "Moura":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.01,0.29,0.59,0.92,1.01,1.17,2.04,2.79,4.38,6.42,9.21,10.18,12.05,13.66,13.14,12.33,10.8,9.64,8.46,8.31],
    "Chilli Beans":[0.0,0.0,0.0,0.0,0.0,0.01,0.08,0.46,2.19,3.41,3.65,4.1,6.57,7.14,6.95,6.73,6.32,6.7,6.78,6.7,6.41,5.76,5.53,5.02,5.52,4.52,3.94,3.92],
    "Juntos Somos Mais":[0.0,0.0,0.0,0.0,0.0,0.04,0.08,0.73,1.29,1.55,1.73,1.92,2.4,2.35,2.41,2.54,2.5,2.65,4.06,5.44,5.87,5.26,5.04,5.14,5.29,5.31,5.09,5.03],
    "Malwee":[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.07,1.01,1.44,1.77,1.87,2.08,2.17,2.06,2.12],
    "Others":[0.0,0.02,0.04,0.06,0.07,0.18,0.14,0.27,0.24,0.37,0.62,1.08,1.45,1.82,1.9,2.05,2.12,2.38,2.9,3.21,2.96,2.9,2.59,2.63,2.83,2.83,2.52,3.83],
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
        s.append(f'<line x1="{Lx}" y1="{y:.1f}" x2="{WD-Rx}" y2="{y:.1f}" stroke="#E2E2E2" stroke-width="1"/>')
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
    WD, HD = 1040, 426; Lx, Rx, Tx, Bx = 46, 16, 30, 44
    pw, ph = WD-Lx-Rx, HD-Tx-Bx; ymax = 48; n = len(_pm); slot = pw/n; bw = slot*0.62
    def Y(v): return Tx+ph - v/ymax*ph
    ybase = Y(0)
    di = _pm.index(FIDC_FROM); xd = Lx + slot*di
    totals = [round(sum(port_data[g][i] for g in port_order), 2) for i in range(n)]
    s = [f'<svg class="chart" viewBox="0 0 {WD} {HD}" xmlns="http://www.w3.org/2000/svg">']
    s.append(f'<rect x="{xd:.1f}" y="{Tx}" width="{WD-Rx-xd:.1f}" height="{ybase-Tx:.1f}" fill="#0C0C0C" opacity="0.05"/>')
    for t in (0,10,20,30,40):
        y = Y(t)
        s.append(f'<line x1="{Lx}" y1="{y:.1f}" x2="{WD-Rx}" y2="{y:.1f}" stroke="#E2E2E2" stroke-width="1"/>')
        s.append(f'<text x="{Lx-7}" y="{y+3:.1f}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#9a9a9a">{t}</text>')
    pk = totals.index(max(totals))
    for i in range(n):
        cx = Lx+slot*i+slot/2; x = cx-bw/2; v = totals[i]
        y = Y(v); h = ybase-y
        col = "#0C0C0C" if i >= di else "#B9B9B9"
        s.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{max(h,0):.1f}" rx="2" fill="{col}"/>')
    # peak + current labels
    s.append(f'<text x="{Lx+slot*pk+slot/2:.1f}" y="{Y(totals[pk])-6:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="700" font-size="10" fill="#0C0C0C">{totals[pk]:.0f}</text>')
    s.append(f'<text x="{Lx+slot*(n-1)+slot/2:.1f}" y="{Y(totals[-1])-6:.1f}" text-anchor="middle" font-family="Geist,sans-serif" font-weight="700" font-size="10" fill="#0C0C0C">{totals[-1]:.1f}</text>')
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

<!-- PORTFOLIO -->
<section class="slide theme-light vcenter" data-num="02">
  <div class="chapter-mark light-mark"><span class="chapter-num">01</span><span class="chapter-divider"></span><span class="chapter-year">Portfolio</span></div>
  <div class="slide-head reveal"><h1>The credit <span class="accent">portfolio.</span></h1>
  <p class="sub">Total outstanding balance (R$M) — scaled to R$ 44M; R$ 34M on book today. FIDC raised in Dec-25.</p></div>
  <div class="blegend reveal">{port_total_legend}</div>
  <div class="chartframe reveal">{port_total_svg}</div>
  <div class="illus">Source: portfolio by month/source · Mar/24–Jun/26</div>
</section>

<!-- ORIGINATION -->
<section class="slide theme-light vcenter" data-num="02">
  <div class="chapter-mark light-mark"><span class="chapter-num">01</span><span class="chapter-divider"></span><span class="chapter-year">Origination</span></div>
  <div class="slide-head reveal"><h1>Origination on the <span class="accent">PIX rail.</span></h1>
  <p class="sub">Monthly TPV by rail (R$M) — R$ 179M since Mar-24, now scaling on PIX.</p></div>
  <div class="blegend reveal">{tpv_legend}</div>
  <div class="chartframe reveal">{tpv_svg}</div>
  <div class="illus">Source: monthly TPV · Mar/24–May/26 (Jun/26 partial, excluded)</div>
</section>

<!-- SCOPE & METHOD -->
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

<!-- PORTFOLIO BY ANCHOR (stacked R$M) -->
<section class="slide theme-light vcenter" data-num="07">
  <div class="chapter-mark light-mark"><span class="chapter-num">06</span><span class="chapter-divider"></span><span class="chapter-year">Portfolio · by anchor</span></div>
  <div class="slide-head reveal"><h1>Portfolio by <span class="accent">anchor.</span></h1>
  <p class="sub">Outstanding balance by anchor (R$M). FIDC raised in Dec-25 (shaded).</p></div>
  <div class="blegend reveal">{port_legend}</div>
  <div class="chartframe reveal">{port_svg}</div>
  <div class="illus">Source: portfolio by month/source · Mar/24–Jun/26</div>
</section>

<!-- INCREASING DIVERSIFICATION -->
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
  <p class="sub">Since this is a leverage of the subordinated tranche, the company's health underpins the structure.</p>
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
