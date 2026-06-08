#!/usr/bin/env python3
import re, base64, mimetypes, os

SRC = "/root/.claude/uploads/15b373a3-4975-569f-b77d-8889479b7950/60d451ab-Robbin_Pitchdeck_May26_vFFF.html"

# --- framework CSS: from original pitchdeck upload, else cached local copy ---
if os.path.exists(SRC):
    orig = open(SRC, encoding="utf-8", errors="replace").read()
    css = orig.split("<style>", 1)[1].split("</style>", 1)[0]
    open("framework_css.css", "w", encoding="utf-8").write(css)
else:
    css = open("framework_css.css", encoding="utf-8").read()

CUSTOM_CSS = r"""
/* ============ CUSTOM SLIDES (Robbin intern deck) ============ */
/* Darker grays on light slides for readability (scoped so dark slides keep contrast) */
.slide.theme-light, .slide.theme-cream { --muted:#5A5A5A; --muted-2:#2E2E2E; }
.slide.theme-light .slide-head .sub, .slide.theme-cream .slide-head .sub { color:#2E2E2E; }
/* vertically center content on content slides */
.slide.vcenter { justify-content:center; }
/* PIX card fan */
.pix-body { display:flex; align-items:center; gap:2vw; margin-top:2.5vh; }
.pixfan { position:relative; flex:1.7; height:62vh; min-height:380px; }
.pcard {
  position:absolute; left:50%; top:6%;
  width:clamp(160px,13.5vw,232px);
  margin-left:calc(clamp(160px,13.5vw,232px) / -2);
  transform-origin:50% 150%;
  transform:rotate(var(--rot));
  opacity:0;
  animation:fanIn .85s cubic-bezier(.18,.7,.2,1) var(--d) both;
  filter:drop-shadow(0 16px 32px rgba(0,0,0,.28));
}
.pcard img { width:100%; height:auto; display:block; border-radius:13px;
  animation:floaty 6s ease-in-out infinite; animation-delay:var(--d); }
@keyframes fanIn { from{opacity:0; transform:rotate(0deg) translateY(64px) scale(.9);} to{opacity:1; transform:rotate(var(--rot)) translateY(0) scale(1);} }
@keyframes floaty { 0%,100%{transform:translateY(0);} 50%{transform:translateY(-7px);} }
.pix-points { flex:1; display:flex; flex-direction:column; }
.pix-point { border-top:1px solid rgba(12,12,12,.12); padding:2.1vh 0; }
.pix-point:last-child { border-bottom:1px solid rgba(12,12,12,.12); }
.pp-num { font-family:var(--font-mono); font-size:11px; letter-spacing:.2em; color:var(--muted); margin-bottom:.7vh; }
.pp-title { font-family:var(--font-sans); font-weight:700; letter-spacing:-.02em; font-size:clamp(18px,1.5vw,27px); margin-bottom:.5vh; }
.pp-desc { font-family:var(--font-sans); color:var(--muted-2); font-size:clamp(13px,1vw,16px); line-height:1.5; }

/* Presenters */
.pres-grid { display:grid; grid-template-columns:1fr 1fr; gap:4vw; margin-top:4vh; align-content:start; }
.pres { display:flex; flex-direction:column; gap:2vh; }
.pres-top { display:flex; align-items:center; gap:1.4vw; }
.pres-photo { width:clamp(74px,7vw,108px); height:clamp(74px,7vw,108px); border-radius:50%; object-fit:cover; filter:grayscale(1) contrast(1.05); flex-shrink:0; }
.pres-name { font-family:var(--font-sans); font-weight:700; letter-spacing:-.025em; font-size:clamp(22px,2.1vw,34px); }
.pres-role { font-family:var(--font-mono); font-size:11px; letter-spacing:.2em; text-transform:uppercase; color:var(--muted); margin-top:.6vh; }
.pres-bio { font-family:var(--font-sans); font-size:clamp(13px,1.02vw,17px); line-height:1.6; color:var(--muted-2); }
.pres-bio b { color:var(--ink); font-weight:600; }
.pres-exp { display:flex; align-items:center; gap:.8vw; margin-top:auto; padding-top:1.4vh; }
.pres-exp .lbl { font-family:var(--font-mono); font-size:10px; letter-spacing:.16em; text-transform:uppercase; color:var(--muted); }
.pres-exp img { height:clamp(15px,1.4vw,21px); width:auto; filter:grayscale(1) contrast(1.05); opacity:.78; }
.pres-exp .exp-txt { font-family:var(--font-sans); font-weight:600; font-size:clamp(12px,1vw,15px); color:var(--muted-2); }

/* Architecture layers */
.layers { margin-top:3vh; border:1px solid rgba(12,12,12,.13); border-radius:14px; overflow:hidden; }
.layer { display:grid; grid-template-columns:42px 1fr auto; gap:1.4vw; align-items:start; padding:1.9vh 1.6vw; border-bottom:1px solid rgba(12,12,12,.10); }
.layer:last-child { border-bottom:none; }
.layer.hi { background:rgba(12,12,12,.04); }
.layer-num { font-family:var(--font-mono); font-size:12px; color:var(--muted); padding-top:.3vh; }
.layer h3 { font-family:var(--font-sans); font-weight:700; letter-spacing:-.01em; font-size:clamp(15px,1.25vw,21px); margin-bottom:.4vh; }
.layer p { font-family:var(--font-sans); font-size:clamp(12px,.95vw,15px); color:var(--muted-2); line-height:1.5; }
.chips { display:flex; flex-wrap:wrap; gap:6px; margin-top:1vh; }
.chips span { font-family:var(--font-mono); font-size:10px; padding:3px 9px; border:1px solid rgba(12,12,12,.16); border-radius:100px; color:var(--muted-2); }
.layer-badge { font-family:var(--font-mono); font-size:10px; letter-spacing:.12em; text-transform:uppercase; padding:5px 11px; border-radius:6px; border:1px solid rgba(12,12,12,.22); color:var(--ink); white-space:nowrap; align-self:start; }
.layer-badge.strong { background:var(--ink); color:var(--paper); border-color:var(--ink); }

/* Tool flow (dark) */
.flow { margin-top:2.5vh; display:flex; flex-direction:column; }
.flow-row { display:grid; grid-template-columns:46px 1fr; gap:1vw; }
.flow-spine { display:flex; flex-direction:column; align-items:center; }
.flow-dot { width:30px; height:30px; border-radius:50%; border:1px solid rgba(255,255,255,.32); display:grid; place-items:center; flex-shrink:0; margin-top:2px; }
.flow-line { width:1px; flex:1; background:rgba(255,255,255,.15); margin:4px 0; }
.flow-card { border:1px solid rgba(255,255,255,.12); border-radius:12px; padding:1.5vh 1.4vw; background:rgba(255,255,255,.03); margin-bottom:1.2vh; }
.flow-label { font-family:var(--font-mono); font-size:10px; letter-spacing:.14em; text-transform:uppercase; color:var(--muted); margin-bottom:.4vh; }
.flow-title { font-family:var(--font-sans); font-weight:700; font-size:clamp(14px,1.2vw,20px); }
.flow-bubble { font-family:var(--font-sans); font-style:italic; color:var(--cream); opacity:.7; font-size:clamp(12px,.95vw,15px); margin-top:.6vh; }
.flow-pill-inline { font-family:var(--font-mono); font-style:normal; background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.14); border-radius:8px; padding:5px 10px; display:inline-block; color:var(--cream); }
.flow-steps { display:grid; grid-template-columns:1fr 1fr; gap:.5vh 1.4vw; margin-top:.4vh; }
.flow-steps.one { grid-template-columns:1fr; }
.flow-step { display:flex; align-items:center; gap:9px; font-family:var(--font-sans); font-size:clamp(11px,.9vw,14px); color:var(--cream); opacity:.88; }
.flow-step b { width:17px; height:17px; border-radius:50%; border:1px solid rgba(255,255,255,.32); display:grid; place-items:center; font-size:9px; font-family:var(--font-mono); font-weight:500; flex-shrink:0; }
.flow-claude { display:flex; align-items:center; gap:10px; margin-bottom:1vh; }
.flow-claude .pill { font-family:var(--font-mono); font-size:9.5px; letter-spacing:.08em; text-transform:uppercase; background:#FAFAFA; color:#0C0C0C; padding:3px 9px; border-radius:100px; }
.flow-done { display:flex; align-items:center; gap:14px; border:1px solid rgba(255,255,255,.28); background:rgba(255,255,255,.06); border-radius:12px; padding:1.4vh 1.4vw; }
.flow-done .ic { width:34px; height:34px; border-radius:50%; background:#FAFAFA; display:grid; place-items:center; flex-shrink:0; }

/* TBD */
.tbd-wrap { display:flex; flex-direction:column; }
.tbd-box { border:1px dashed rgba(12,12,12,.25); border-radius:16px; padding:5vh 4vw; max-width:64ch; }
.tbd-tag { font-family:var(--font-mono); font-size:13px; letter-spacing:.22em; text-transform:uppercase; color:var(--muted); }
.tbd-box p { font-family:var(--font-sans); font-size:clamp(15px,1.1vw,20px); color:var(--muted-2); margin-top:1.4vh; line-height:1.6; }
.tbd-owner { position:absolute; top:5vh; right:4vw; z-index:6; font-family:var(--font-mono); font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--muted); border:1px solid rgba(12,12,12,.18); border-radius:100px; padding:6px 14px; }
/* Note line (Marcos data slides) */
.df-note { font-family:var(--font-mono); font-style:italic; font-size:clamp(11px,.85vw,13px); color:var(--muted-2); margin-top:1.8vh; line-height:1.55; max-width:78ch; }
/* Data architecture flow */
.dataflow { margin-top:2.5vh; }
.df-band { display:grid; grid-template-columns:1fr 1fr; gap:1.2vw; margin-bottom:1.4vh; }
.df-band-cell { text-align:center; font-family:var(--font-mono); font-size:clamp(10px,.85vw,13px); letter-spacing:.1em; text-transform:uppercase; color:var(--muted-2); border:1px dashed rgba(12,12,12,.25); border-radius:9px; padding:1vh 0; }
.df-cols { display:grid; grid-template-columns:1fr auto 1.25fr auto 1fr; align-items:stretch; gap:.5vw; }
.df-col { display:flex; flex-direction:column; gap:.7vh; border:1px solid rgba(12,12,12,.13); border-radius:14px; padding:1.6vh 1vw; }
.df-stage { font-family:var(--font-mono); font-size:10px; letter-spacing:.16em; text-transform:uppercase; color:var(--muted); margin-bottom:.4vh; }
.df-item { font-family:var(--font-sans); font-weight:600; font-size:clamp(12px,.98vw,15px); border:1px solid rgba(12,12,12,.12); border-radius:9px; padding:.85vh 1vw; }
.df-layer { display:flex; flex-direction:column; border:1px solid rgba(12,12,12,.16); border-radius:9px; padding:.75vh 1vw; background:rgba(12,12,12,.035); }
.df-layer b { font-family:var(--font-sans); font-weight:700; font-size:clamp(12px,.98vw,15px); }
.df-layer i { font-family:var(--font-mono); font-style:normal; font-size:10px; color:var(--muted); margin-top:1px; letter-spacing:.02em; }
.df-arrow { display:flex; align-items:center; justify-content:center; font-size:18px; color:var(--muted); }

/* Vagas */
.vagas-grid { margin-top:4vh; display:grid; grid-template-columns:1fr 1fr; gap:1.4vw; }
.vaga { border:1px solid rgba(12,12,12,.13); border-radius:14px; padding:2.4vh 1.6vw; display:flex; gap:1.2vw; align-items:flex-start; transition:background .25s; }
.vaga:hover { background:rgba(12,12,12,.04); }
.vaga-num { font-family:var(--font-mono); font-size:12px; color:var(--muted); padding-top:.4vh; }
.vaga h3 { font-family:var(--font-sans); font-weight:700; letter-spacing:-.01em; font-size:clamp(17px,1.5vw,25px); }
.vaga-meta { font-family:var(--font-mono); font-size:11px; color:var(--muted); margin-top:.8vh; line-height:1.7; letter-spacing:.04em; }
.vaga-tags { display:flex; gap:6px; margin-top:1.4vh; }
.vaga-tags span { font-family:var(--font-mono); font-size:10px; padding:3px 9px; border:1px solid rgba(12,12,12,.16); border-radius:100px; color:var(--muted-2); }
.vagas-cta { margin-top:4vh; display:flex; align-items:center; gap:1vw; font-family:var(--font-mono); font-size:clamp(13px,1vw,16px); color:var(--ink); }
.vagas-cta .pill { background:var(--ink); color:var(--paper); padding:9px 16px; border-radius:100px; }
.vagas-cta .dim { color:var(--muted); }
"""

BODY = r"""
<div class="deck-mark-mini"><img src="robbin-bird-black.svg" alt="Robbin"></div>
<div class="slide-counter"><span class="current">01</span><span style="opacity:0.4"> / 09</span></div>
<div class="deck-meta">
  <button class="nav-btn" id="prevBtn">&larr; prev</button>
  <div class="progress"><div class="progress-fill" id="progressFill"></div></div>
  <button class="nav-btn" id="nextBtn">next &rarr;</button>
</div>

<div class="deck" id="deck">

  <!-- 1 — COVER -->
  <section class="slide cover5 active" id="cover" data-num="01">
    <div class="cover5-badge">São Paulo · 2026</div>
    <div class="cover5-center">
      <img class="cover5-logo" src="robbin-logo-black.svg" alt="Robbin">
    </div>
    <div class="cover5-meta">Confidential</div>
  </section>

  <!-- 2 — PRESENTERS -->
  <section class="slide theme-light vcenter" data-num="02">
    <div class="chapter-mark light-mark">
      <span class="chapter-num">01</span><span class="chapter-divider"></span><span class="chapter-year">Presenters</span>
    </div>
    <div class="slide-head reveal">
      <h1>Presenters<span class="accent">.</span></h1>
    </div>
    <div class="pres-grid reveal" data-stagger>
      <div class="pres">
        <div class="pres-top">
          <img class="pres-photo" src="Tomas.jpeg" alt="Tomás Corrêa">
          <div>
            <div class="pres-name">Tomás Corrêa</div>
            <div class="pres-role">CTO &amp; Co-Founder</div>
          </div>
        </div>
        <p class="pres-bio">A biologist by training from the <b>University of São Paulo</b>, he was co-founder and <b>CTO of Open Co</b> (originally Geru), Brazil's first 100% digital lender, founded in 2014. Leading the company's technology for nearly nine years, he helped build one of the country's largest digital credit platforms, with over <b>USD 1 billion</b> in loans originated. In 2023 he co-founded <b>Robbin</b>, a B2B credit fintech for retail, where he remains CTO — a company that raised <b>USD 8M</b> in seed and recently announced a <b>USD 108M</b> round.</p>
        <div class="pres-exp"><span class="lbl">ex—</span><img src="openco.svg" alt="Open Co"><span class="lbl" style="margin-left:.5vw">now—</span><img src="robbin-logo-black.svg" alt="Robbin"></div>
      </div>
      <div class="pres">
        <div class="pres-top">
          <img class="pres-photo" src="Marcos.jpeg" alt="Marcos">
          <div>
            <div class="pres-name">Marcos</div>
            <div class="pres-role">Head of Data</div>
          </div>
        </div>
        <p class="pres-bio">A Computer Scientist from <b>USP (IME-USP)</b>, with over a decade in data and technology across Brazil, Japan and the US. He was a <b>Business Intelligence Engineer at Amazon</b> in Tokyo and Head of Data &amp; Tech at Cedar Brands, where he built a GCP data lakehouse architecture from scratch and led initiatives that lifted the group's brand conversion rates by more than <b>50%</b>. Today he is Head of Data at Robbin.</p>
        <div class="pres-exp"><span class="lbl">ex—</span><img src="Amazon_logo.svg.png" alt="Amazon"><img src="images.png" alt="Rakuten"><span class="lbl" style="margin-left:.5vw">now—</span><img src="robbin-logo-black.svg" alt="Robbin"></div>
      </div>
    </div>
  </section>

  <!-- 3 — PIX CARD -->
  <section class="slide theme-light pix-slide vcenter" data-num="03">
    <div class="chapter-mark light-mark">
      <span class="chapter-num">02</span><span class="chapter-divider"></span><span class="chapter-year">The Card</span>
    </div>
    <div class="slide-head reveal">
      <h1>The credit card <span class="accent">on PIX rails.</span></h1>
      <p class="sub">Card UX. PIX economics. Instant settlement. Already live with co-brand anchors.</p>
    </div>
    <div class="pix-body reveal">
      <div class="pixfan">
        <div class="pcard" style="--rot:-40deg; --d:.15s; z-index:1;"><img src="Chilli.png" alt="Chilli Beans"></div>
        <div class="pcard" style="--rot:-27deg; --d:.25s; z-index:2;"><img src="Brinox.png" alt="Grupo Brinox"></div>
        <div class="pcard" style="--rot:-13deg; --d:.35s; z-index:3;"><img src="Malwee.png" alt="Malwee"></div>
        <div class="pcard" style="--rot:13deg;  --d:.45s; z-index:5;"><img src="Cantu.png" alt="Cantu"></div>
        <div class="pcard" style="--rot:27deg;  --d:.5s;  z-index:4;"><img src="Credmoura.png" alt="CredMoura"></div>
        <div class="pcard" style="--rot:40deg;  --d:.6s;  z-index:2;"><img src="JSM.png" alt="Juntos Somos+"></div>
        <div class="pcard" style="--rot:0deg;   --d:.55s; z-index:10;"><img src="Robbin.png" alt="Robbin"></div>
      </div>
      <div class="pix-points" data-stagger>
        <div class="pix-point">
          <div class="pp-num">— 01</div>
          <div class="pp-title">Real-time on PIX</div>
          <div class="pp-desc">Settlement in seconds, 24/7. No interchange. No acquiring middleware.</div>
        </div>
        <div class="pix-point">
          <div class="pp-num">— 02</div>
          <div class="pp-title">SME behavior, unique insights</div>
          <div class="pp-desc">Sell-out data from anchor brands underwrites every transaction.</div>
        </div>
        <div class="pix-point">
          <div class="pp-num">— 03</div>
          <div class="pp-title">Co-branded with anchors</div>
          <div class="pp-desc">Cantu, Brinox, Malwee, Chilli Beans, Baterias Moura, Juntos Somos Mais (Votorantim, Tigre, Gerdau) — already live.</div>
        </div>
      </div>
    </div>
  </section>

  <!-- 4 — ARQUITETURA -->
  <section class="slide theme-light vcenter" data-num="04">
    <div class="chapter-mark light-mark">
      <span class="chapter-num">03</span><span class="chapter-divider"></span><span class="chapter-year">Architecture</span>
    </div>
    <div class="slide-head reveal">
      <h1>Non-technical team in command — <span class="accent">without giving up security.</span></h1>
      <p class="sub">4 layers that separate what moves fast from what must stay stable: anyone builds, the platform guarantees.</p>
    </div>
    <div class="layers reveal" data-stagger>
      <div class="layer">
        <span class="layer-num">01</span>
        <div>
          <h3>Vibe code + AI tools</h3>
          <p>Anyone on the team builds complete apps with AI. Skills and rules embed Robbin's context — the AI acts like a teammate, not a stranger.</p>
          <div class="chips"><span>max speed</span><span>tools.robbin.com.br</span><span>skills &amp; rules</span><span>Claude · Cursor</span></div>
        </div>
        <span class="layer-badge strong">move fast</span>
      </div>
      <div class="layer">
        <span class="layer-num">02</span>
        <div>
          <h3>BFF — Ops / Client / Partner</h3>
          <p>Three backends by audience. Vibe code consumes stable contracts — never touches internal logic directly.</p>
          <div class="chips"><span>contracts by audience</span><span>single ALB</span></div>
        </div>
        <span class="layer-badge">boundary</span>
      </div>
      <div class="layer hi">
        <span class="layer-num">03</span>
        <div>
          <h3>Platform — transactional + managerial</h3>
          <p>7 micro-monoliths by team boundary. A 4-layer data lake for trustworthy data. The stability that lets vibe code fly.</p>
          <div class="chips"><span>auth · credit · payments · cards</span><span>Kafka · Temporal</span><span>Snowflake · dbt</span></div>
        </div>
        <span class="layer-badge">stability</span>
      </div>
      <div class="layer">
        <span class="layer-num">04</span>
        <div>
          <h3>Knowledge system — rules, skills, Ganesha</h3>
          <p>Robbin's accumulated context available to any AI. Without it, every vibe code would be a gamble.</p>
          <div class="chips"><span>behavioral rules</span><span>reusable skills</span><span>Ganesha — API catalog</span></div>
        </div>
        <span class="layer-badge">guardrail</span>
      </div>
    </div>
  </section>

  <!-- 5 — ROBBIN TOOLS (dark) -->
  <section class="slide theme-dark vcenter" data-num="05">
    <div class="chapter-mark">
      <span class="chapter-num">04</span><span class="chapter-divider"></span><span class="chapter-year">Robbin Tools</span>
    </div>
    <div class="slide-head reveal">
      <h1>Creating a tool <span class="muted">is just asking.</span></h1>
      <p class="sub">Claude handles all the technical setup. You just describe what you need. — tools.robbin.com.br</p>
    </div>
    <div class="flow reveal" data-stagger>
      <div class="flow-row">
        <div class="flow-spine"><div class="flow-dot"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></div><div class="flow-line"></div></div>
        <div class="flow-card">
          <div class="flow-label">You</div>
          <div class="flow-title">Ask Claude to create a tool</div>
          <div class="flow-bubble"><span class="flow-pill-inline">"I want to create a Robbin Tool for the ops team"</span></div>
        </div>
      </div>
      <div class="flow-row">
        <div class="flow-spine"><div class="flow-dot"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg></div><div class="flow-line"></div></div>
        <div class="flow-card">
          <div class="flow-claude"><span class="pill">Claude</span><span class="flow-title" style="font-size:clamp(13px,1.1vw,18px)">Sets up the environment automatically</span></div>
          <div class="flow-steps">
            <div class="flow-step"><b>1</b>Checks and installs Git</div>
            <div class="flow-step"><b>2</b>Generates the SSH key</div>
            <div class="flow-step"><b>3</b>Authenticates with GitHub</div>
            <div class="flow-step"><b>4</b>Clones the ai-powers repo</div>
            <div class="flow-step"><b>5</b>Installs the create-robbin-tool skill</div>
          </div>
        </div>
      </div>
      <div class="flow-row">
        <div class="flow-spine"><div class="flow-dot"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></div><div class="flow-line"></div></div>
        <div class="flow-card">
          <div class="flow-label">You</div>
          <div class="flow-title">Describe the tool you want to build</div>
          <div class="flow-bubble">Claude asks: "What does it do? Who will use it? How should it work?"</div>
        </div>
      </div>
      <div class="flow-row">
        <div class="flow-spine"><div class="flow-dot"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></div></div>
        <div class="flow-done">
          <div class="ic"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0C0C0C" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></div>
          <div>
            <div class="flow-title">Tool is live</div>
            <div class="flow-bubble" style="font-style:normal;margin-top:2px;">Ready for the team to use at tools.robbin.com.br</div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- 6 — MARCOS · DATA ROLES -->
  <section class="slide theme-light vcenter" data-num="06">
    <div class="chapter-mark light-mark">
      <span class="chapter-num">05</span><span class="chapter-divider"></span><span class="chapter-year">Data · roles</span>
    </div>
    <div class="slide-head reveal">
      <h1>Who does what in <span class="accent">Data.</span></h1>
      <p class="sub">Data isn't one person — it's a team. Each role owns a different skill.</p>
    </div>
    <div class="layers reveal" data-stagger>
      <div class="layer">
        <span class="layer-num">01</span>
        <div><h3>Data Engineer</h3><p>Builds the plumbing. Makes sure data arrives complete and reliable.</p></div>
        <span class="layer-badge">pipelines</span>
      </div>
      <div class="layer">
        <span class="layer-num">02</span>
        <div><h3>Analytics Engineer</h3><p>The bridge. Models raw data into clean, ready-to-use tables.</p></div>
        <span class="layer-badge">modeling</span>
      </div>
      <div class="layer">
        <span class="layer-num">03</span>
        <div><h3>Data Analyst</h3><p>Turns data into answers — numbers, charts and business recommendations.</p></div>
        <span class="layer-badge">insight</span>
      </div>
      <div class="layer">
        <span class="layer-num">04</span>
        <div><h3>Data Scientist</h3><p>Finds patterns and predicts. Uses statistics and models to anticipate the future.</p></div>
        <span class="layer-badge">prediction</span>
      </div>
      <div class="layer">
        <span class="layer-num">05</span>
        <div><h3>ML Engineer</h3><p>Puts the model to real work — in production and at scale.</p></div>
        <span class="layer-badge">production</span>
      </div>
    </div>
    <p class="df-note">Behind the scenes: Data Platform Engineer (the infra) and DataOps (the quality culture).</p>
  </section>

  <!-- 7 — MARCOS · DATA ARCHITECTURE -->
  <section class="slide theme-light vcenter" data-num="07">
    <div class="chapter-mark light-mark">
      <span class="chapter-num">06</span><span class="chapter-divider"></span><span class="chapter-year">Data · architecture</span>
    </div>
    <div class="slide-head reveal">
      <h1>From <span class="accent">source to consumption.</span></h1>
      <p class="sub">Sources are ingested, transformed across landing, prepared, trusted and delivery layers, then consumed.</p>
    </div>
    <div class="dataflow reveal">
      <div class="df-band">
        <span class="df-band-cell">Orchestration</span>
        <span class="df-band-cell">Data catalog</span>
      </div>
      <div class="df-cols">
        <div class="df-col">
          <div class="df-stage">Ingestion · sources</div>
          <div class="df-item">Database</div>
          <div class="df-item">Files</div>
          <div class="df-item">APIs</div>
          <div class="df-item">Spreadsheets</div>
        </div>
        <div class="df-arrow">→</div>
        <div class="df-col">
          <div class="df-stage">Transformation</div>
          <div class="df-layer"><b>Landing</b><i>raw, as it came</i></div>
          <div class="df-layer"><b>Prepared</b><i>clean &amp; standardized</i></div>
          <div class="df-layer"><b>Trusted</b><i>reliable, integrated</i></div>
          <div class="df-layer"><b>Delivery</b><i>business-ready</i></div>
        </div>
        <div class="df-arrow">→</div>
        <div class="df-col">
          <div class="df-stage">Consumption</div>
          <div class="df-item">Dashboards</div>
          <div class="df-item">Reports</div>
          <div class="df-item">Analyses</div>
          <div class="df-item">ML models</div>
          <div class="df-item">AI</div>
        </div>
      </div>
      <p class="df-note">Data is born scattered across sources, cleaned and organized into layers, and only then becomes a chart, report, analysis, model or AI answer — each stop a specialty.</p>
    </div>
  </section>

  <!-- 8 — Q&A (closing) -->
  <section class="slide theme-dark closing2" data-num="08">
    <div class="closing2-bg"><div class="closing2-grid"></div><div class="closing2-glow"></div></div>
    <div class="closing2-inner">
      <div class="closing2-eyebrow reveal"><span>—</span><span>Discussion</span></div>
      <h2 class="closing2-line reveal">
        <span class="cl-row hi">Q&amp;A</span>
      </h2>
      <div class="closing2-divider reveal"></div>
      <div class="closing2-logo reveal"><img src="robbin-logo-white.svg" alt="Robbin" style="height:46px;width:auto;"></div>
    </div>
  </section>

  <!-- 9 — VAGAS -->
  <section class="slide theme-light vcenter" data-num="09">
    <div class="chapter-mark light-mark">
      <span class="chapter-num">07</span><span class="chapter-divider"></span><span class="chapter-year">Join the team</span>
    </div>
    <div class="slide-head reveal">
      <h1>Open <span class="accent">positions.</span></h1>
      <p class="sub">We're building the financial platform for the AI era — and we want great people with us.</p>
    </div>
    <div class="vagas-grid reveal" data-stagger>
      <div class="vaga"><span class="vaga-num">01</span><div><h3>Summer in Engineering</h3><div class="vaga-meta">Summer program · Engineering<br>São Paulo · Hybrid</div><div class="vaga-tags"><span>Summer</span><span>AI-first</span></div></div></div>
      <div class="vaga"><span class="vaga-num">02</span><div><h3>Summer in Data &amp; Analytics</h3><div class="vaga-meta">Summer program · Data<br>São Paulo · Hybrid</div><div class="vaga-tags"><span>Summer</span><span>Analytics</span></div></div></div>
      <div class="vaga"><span class="vaga-num">03</span><div><h3>Intern in Strategic Finance</h3><div class="vaga-meta">Internship · Strategic Finance<br>São Paulo · Hybrid</div><div class="vaga-tags"><span>Intern</span><span>Finance</span></div></div></div>
      <div class="vaga"><span class="vaga-num">04</span><div><h3>Intern in Data &amp; Analytics</h3><div class="vaga-meta">Internship · Data<br>São Paulo · Hybrid</div><div class="vaga-tags"><span>Intern</span><span>Analytics</span></div></div></div>
    </div>
    <div class="vagas-cta reveal">
      <span class="pill">careers@robbin.com.br</span>
      <span class="dim">— send your CV or refer someone</span>
    </div>
  </section>

</div>
"""

SCRIPT = r"""
<script>
(() => {
  const slides = Array.from(document.querySelectorAll('.slide'));
  const counter = document.querySelector('.slide-counter .current');
  const counterWrap = document.querySelector('.slide-counter');
  const progress = document.getElementById('progressFill');
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  let cur = 0;

  const isLight = s => s.classList.contains('theme-light') || s.classList.contains('theme-cream') || s.classList.contains('cover5');

  function go(i) {
    if (i < 0 || i >= slides.length) return;
    slides[cur].classList.remove('active');
    cur = i;
    slides[cur].classList.add('active');
    const onCover = cur === 0;
    counterWrap.style.visibility = onCover ? 'hidden' : 'visible';
    document.body.classList.toggle('is-cover', onCover);
    if (!onCover) counter.textContent = String(cur).padStart(2, '0');
    progress.style.width = (cur / (slides.length - 1) * 100) + '%';
    document.body.classList.toggle('is-dark-slide', !isLight(slides[cur]));
  }

  prevBtn.addEventListener('click', () => go(cur - 1));
  nextBtn.addEventListener('click', () => go(cur + 1));
  document.addEventListener('keydown', e => {
    if (['ArrowRight','ArrowDown','PageDown',' '].includes(e.key)) { e.preventDefault(); go(cur + 1); }
    else if (['ArrowLeft','ArrowUp','PageUp'].includes(e.key)) { e.preventDefault(); go(cur - 1); }
    else if (e.key === 'Home') { e.preventDefault(); go(0); }
    else if (e.key === 'End') { e.preventDefault(); go(slides.length - 1); }
  });
  let touchX = null;
  document.addEventListener('touchstart', e => { touchX = e.touches[0].clientX; }, {passive:true});
  document.addEventListener('touchend', e => {
    if (touchX == null) return;
    const dx = e.changedTouches[0].clientX - touchX;
    if (Math.abs(dx) > 50) go(dx < 0 ? cur + 1 : cur - 1);
    touchX = null;
  });

  document.body.classList.add('is-cover');
  progress.style.width = '0%';

  // Cover dark/light flip
  const cover = document.getElementById('cover');
  if (cover) {
    cover.classList.add('is-dark');
    setInterval(() => { if (cover.classList.contains('active')) cover.classList.toggle('is-dark'); }, 2000);
  }
})();
</script>
"""

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Robbin — Apresentação</title>
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700;800;900&family=Geist+Mono:wght@400;500;600;700&display=swap" rel="stylesheet" />
<style>
""" + css + CUSTOM_CSS + """
</style>
</head>
<body>
"""

html = HEAD + BODY + SCRIPT + "\n</body>\n</html>\n"
open("presentation.html", "w", encoding="utf-8").write(html)
print("presentation.html:", len(html), "bytes")

# --- self-contained preview ---
def datauri(path):
    mime = "image/svg+xml" if path.endswith(".svg") else (mimetypes.guess_type(path)[0] or "application/octet-stream")
    return "data:%s;base64,%s" % (mime, base64.b64encode(open(path, "rb").read()).decode())

assets = ["robbin-logo-black.svg","robbin-logo-white.svg","robbin-bird-black.svg",
          "Robbin.png","Chilli.png","Brinox.png","Malwee.png","Credmoura.png","JSM.png","Cantu.png",
          "Tomas.jpeg","Marcos.jpeg","openco.svg","Amazon_logo.svg.png","images.png"]
preview = html
for a in assets:
    preview = preview.replace('src="%s"' % a, 'src="%s"' % datauri(a))
open("presentation-preview.html", "w", encoding="utf-8").write(preview)
left = re.findall(r'src="(?!data:)[^"]+"', preview)
print("preview:", len(preview), "bytes | remaining relative srcs:", left)
