#!/usr/bin/env python3
"""Generate slides.html for the Robbin credit / FIDC institutional deck.
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
    "Safra 2024-Q2": [0,.1,.35,.8,1.3,1.8,2.2,2.5,2.7,2.85,2.95,3.0,3.05],
    "Safra 2024-Q3": [0,.08,.3,.7,1.1,1.5,1.85,2.1,2.3,2.45,2.55],
    "Safra 2024-Q4": [0,.08,.28,.6,1.0,1.35,1.65,1.9,2.05],
    "Safra 2025-Q1": [0,.07,.25,.55,.9,1.2,1.45],
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
fpd_months = ["jul","ago","set","out","nov","dez","jan","fev","mar","abr","mai","jun"]
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
jr.append(f'<text x="{W-R}" y="{T-2}" text-anchor="end" font-family="Geist Mono,monospace" font-size="10" fill="#8a8a8a">% a.m.</text>')
jr_svg = chart("\n".join(jr))

# ---------- industry bars (HTML) ----------
industry = [("Varejo / comércio",34),("Indústria",22),("Serviços",18),
            ("Construção",12),("Agro",8),("Outros",6)]
ind_rows = "".join(
    f'<div class="ind-row"><span class="ind-l">{n}</span>'
    f'<span class="ind-track"><span class="ind-fill" style="width:{p*2.6}%"></span></span>'
    f'<span class="ind-v">{p}%</span></div>' for n, p in industry)


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
.ind-row { display:grid; grid-template-columns:180px 1fr 48px; align-items:center; gap:1vw; margin-bottom:1.3vh; }
.ind-l { font-family:var(--font-sans); font-size:clamp(13px,1vw,16px); color:var(--ink); font-weight:500; }
.ind-track { height:12px; background:rgba(12,12,12,.06); border-radius:100px; overflow:hidden; }
.ind-fill { display:block; height:100%; background:var(--ink); border-radius:100px; }
.ind-v { font-family:var(--font-mono); font-size:12px; color:#2E2E2E; text-align:right; }
.callout { border:1px solid rgba(12,12,12,.18); border-left:3px solid var(--ink); border-radius:10px; padding:1.6vh 1.4vw; margin-top:2vh; font-family:var(--font-sans); font-size:clamp(13px,1.02vw,16px); color:#2E2E2E; line-height:1.55; }
.callout b { color:var(--ink); font-weight:600; }
.illus { position:absolute; bottom:4.4vh; left:4vw; z-index:6; font-family:var(--font-mono); font-size:9.5px; letter-spacing:.12em; text-transform:uppercase; color:#9a9a9a; }
.def-grid { display:grid; grid-template-columns:repeat(2,1fr); gap:1.2vw; margin-top:1.5vh; }
</style>"""

SLIDES = STYLE + f"""
<!-- 1 — CAPA -->
<section class="slide cover5 active" id="cover" data-num="01">
  <div class="cover5-badge">São Paulo · 2026</div>
  <div class="cover5-center">
    <img class="cover5-logo" src="robbin-logo-black.svg" alt="Robbin">
    <div class="cover5-tag">Performance de crédito.</div>
  </div>
  <div class="cover5-meta">Confidencial · Material institucional</div>
</section>

<!-- 2 — ESCOPO & METODOLOGIA -->
<section class="slide theme-light vcenter" data-num="02">
  <div class="chapter-mark light-mark"><span class="chapter-num">01</span><span class="chapter-divider"></span><span class="chapter-year">Escopo</span></div>
  <div class="slide-head reveal"><h1>Como ler estes <span class="accent">números.</span></h1>
  <p class="sub">Recorte, base de dados e definições das métricas de crédito.</p></div>
  <div class="layers reveal" data-stagger>
    <div class="layer hi"><span class="layer-num">01</span><div><h3>Apenas PIX / boleto</h3><p>Todo o loan tape e todos os gráficos consideram exclusivamente operações liquidadas via PIX/boleto. Os dados de cartão ficam de fora desta visão.</p></div><span class="layer-badge strong">loan tape</span></div>
    <div class="layer"><span class="layer-num">02</span><div><h3>Carve-out do FIDC</h3><p>Usamos a carteira do FIDC como proxy de performance de crédito — é o retrato mais recente e auditável da nossa capacidade de originar e cobrar.</p></div><span class="layer-badge">retrato recente</span></div>
    <div class="layer"><span class="layer-num">03</span><div><h3>Definições</h3><p><b>CDR por safra</b> = perda acumulada (saldo devedor over90) ÷ valor originado da safra. <b>FPD 15/30</b> = valor que atrasou a 1ª parcela ÷ total das 1ªs parcelas do mês.</p></div><span class="layer-badge">métricas</span></div>
  </div>
  <div class="illus">Dados ilustrativos — substituir pelo loan tape</div>
</section>

<!-- 3 — CDR POR SAFRA -->
<section class="slide theme-light vcenter" data-num="03">
  <div class="chapter-mark light-mark"><span class="chapter-num">02</span><span class="chapter-divider"></span><span class="chapter-year">Risco · safras</span></div>
  <div class="slide-head reveal"><h1>CDR por <span class="accent">safra.</span></h1>
  <p class="sub">Perda acumulada (over90) sobre o valor originado, por meses on book (MOB).</p></div>
  <div class="two-col reveal">
    <div class="chartframe">{cdr_svg}
      <div class="legend">{cdr_legend}</div>
    </div>
    <ul class="readlist">
      <li>Safras <b>mais recentes performam melhor</b>: a curva 2025-Q1 corre abaixo das anteriores no mesmo MOB.</li>
      <li>A perda <b>estabiliza ~MOB 9–10</b>, sinal de maturação consistente entre safras.</li>
      <li>Patamar terminal convergindo para <b>~2,5–3,0%</b> — dentro do apetite de risco.</li>
    </ul>
  </div>
  <div class="illus">Dados ilustrativos — substituir pelo loan tape (PIX/boleto)</div>
</section>

<!-- 4 — FPD -->
<section class="slide theme-light vcenter" data-num="04">
  <div class="chapter-mark light-mark"><span class="chapter-num">03</span><span class="chapter-divider"></span><span class="chapter-year">Risco · originação</span></div>
  <div class="slide-head reveal"><h1>FPD 30 <span class="accent">por mês.</span></h1>
  <p class="sub">Valor que atrasou a 1ª parcela ÷ total das 1ªs parcelas — qualidade na entrada da safra.</p></div>
  <div class="two-col reveal">
    <div class="chartframe">{fpd_svg}
      <div class="legend"><span><i style="background:#0C0C0C"></i>últimos 3 meses</span><span><i style="background:#B5B5B5"></i>histórico</span></div>
    </div>
    <ul class="readlist">
      <li>Tendência <b>consistente de queda</b>: de ~2,8% para <b>~1,8%</b> nos últimos 12 meses.</li>
      <li>Melhora puxada por <b>ajuste de políticas</b> de crédito e dados de sell-out das âncoras.</li>
      <li>FPD baixo e estável <b>antecipa</b> safras mais saudáveis no CDR.</li>
    </ul>
  </div>
  <div class="illus">Dados ilustrativos — substituir pelo loan tape (PIX/boleto)</div>
</section>

<!-- 5 — CONCENTRAÇÃO / PULVERIZAÇÃO -->
<section class="slide theme-light vcenter" data-num="05">
  <div class="chapter-mark light-mark"><span class="chapter-num">04</span><span class="chapter-divider"></span><span class="chapter-year">Carteira · pulverização</span></div>
  <div class="slide-head reveal"><h1>Pulverizada e <span class="accent">diversificada.</span></h1>
  <p class="sub">Exposição por indústria e métricas de concentração da carteira.</p></div>
  <div class="two-col reveal">
    <div class="chartframe" style="padding:3vh 2vw;">{ind_rows}</div>
    <div style="display:flex; flex-direction:column; gap:1.4vh;">
      {metric("Ticket médio","R$ 18k","por operação")}
      {metric("Top-10 sacados","9%","da carteira")}
      {metric("Nº de sacados","12,4k","posições ativas")}
    </div>
  </div>
  <div class="illus">Dados ilustrativos — substituir pelo loan tape (PIX/boleto)</div>
</section>

<!-- 6 — PRAZO & DURATION -->
<section class="slide theme-light vcenter" data-num="06">
  <div class="chapter-mark light-mark"><span class="chapter-num">05</span><span class="chapter-divider"></span><span class="chapter-year">Carteira · prazo</span></div>
  <div class="slide-head reveal"><h1>Prazo médio e <span class="accent">duration.</span></h1>
  <p class="sub">Carteira curta e de giro rápido — recomposição e ajuste de risco velozes.</p></div>
  <div class="metrics reveal" data-stagger>
    {metric("Prazo médio","7,2 <span style='font-size:.5em'>meses</span>","prazo contratual ponderado")}
    {metric("Duration","5,1 <span style='font-size:.5em'>meses</span>","ponderada pelo saldo")}
    {metric("Taxa média","3,4% <span style='font-size:.5em'>a.m.</span>","carteira PIX/boleto")}
    {metric("Originação","R$ 42M <span style='font-size:.5em'>/mês</span>","run-rate atual")}
    {metric("Over90","2,7%","saldo em atraso > 90d")}
    {metric("Giro","~1,7×","ao ano")}
  </div>
  <div class="illus">Dados ilustrativos — substituir pelo loan tape (PIX/boleto)</div>
</section>

<!-- 7 — SUBORDINADA JR -->
<section class="slide theme-light vcenter" data-num="07">
  <div class="chapter-mark light-mark"><span class="chapter-num">06</span><span class="chapter-divider"></span><span class="chapter-year">FIDC · subordinada Jr</span></div>
  <div class="slide-head reveal"><h1>A Jr protege os <span class="accent">seniores.</span></h1>
  <p class="sub">Excesso de spread + subordinação dão o colchão de segurança às cotas superiores (ex-aportes).</p></div>
  <div class="two-col reveal">
    <div class="chartframe">{jr_svg}
      <div class="legend"><span><i style="background:#0C0C0C"></i>performance de crédito (suavizada)</span><span><i style="background:#C0C0C0"></i>cota Jr observada</span></div>
    </div>
    <div style="display:flex; flex-direction:column; gap:1.2vh;">
      {metric("Subordinação","22%","colchão para seniores")}
      {metric("Excesso de spread","~14% <span style='font-size:.45em'>a.a.</span>","acima do custo sênior")}
    </div>
  </div>
  <div class="callout reveal">A <b>vol observada na cota Jr</b> veio de <b>erros operacionais pontuais</b>, não de deterioração de crédito. Normalizando esses eventos, a performance da carteira é <b>estável</b> — e o colchão de subordinação + excesso de spread nunca foi tocado pelos seniores.</div>
  <div class="illus">Dados ilustrativos — substituir pelo loan tape (PIX/boleto)</div>
</section>

<!-- 8 — CORPORATIVO / RUNWAY -->
<section class="slide theme-light vcenter" data-num="08">
  <div class="chapter-mark light-mark"><span class="chapter-num">07</span><span class="chapter-divider"></span><span class="chapter-year">Companhia</span></div>
  <div class="slide-head reveal"><h1>Lastro corporativo da <span class="accent">alavancagem.</span></h1>
  <p class="sub">Como é uma alavancagem da subordinada, a saúde da companhia sustenta a estrutura.</p></div>
  <div class="metrics reveal" data-stagger>
    {metric("Caixa","R$ 32M","posição atual")}
    {metric("Burn mensal","R$ 2,1M","líquido")}
    {metric("Runway","15+ <span style='font-size:.5em'>meses</span>","no burn atual")}
    {metric("Meta originação","R$ 80M <span style='font-size:.5em'>/mês</span>","saída do ano")}
    {metric("Capacidade FIDC","R$ 500M","cota sênior")}
    {metric("Subordinação alvo","≥ 20%","piso de estrutura")}
  </div>
  <div class="callout reveal">Metas corporativas, caixa e runway dimensionados para <b>sustentar a cota subordinada</b> ao longo do ciclo — alinhando o risco do acionista ao dos cotistas seniores.</div>
  <div class="illus">Dados ilustrativos — substituir pelos números reais da companhia</div>
</section>

<!-- 9 — Q&A -->
<section class="slide theme-dark closing2" data-num="09">
  <div class="closing2-bg"><div class="closing2-grid"></div><div class="closing2-glow"></div></div>
  <div class="closing2-inner">
    <div class="closing2-eyebrow reveal"><span>—</span><span>Discussão</span></div>
    <h2 class="closing2-line reveal"><span class="cl-row hi">Q&amp;A</span></h2>
    <div class="closing2-divider reveal"></div>
    <div class="closing2-logo reveal"><img src="robbin-logo-white.svg" alt="Robbin" style="height:46px;width:auto;"></div>
  </div>
</section>
"""

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "slides.html")
open(out, "w", encoding="utf-8").write(SLIDES)
print("wrote", out, len(SLIDES), "bytes")
