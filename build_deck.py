#!/usr/bin/env python3
import re, base64, mimetypes, os

SRC = "/root/.claude/uploads/15b373a3-4975-569f-b77d-8889479b7950/60d451ab-Robbin_Pitchdeck_May26_vFFF.html"

# --- extract original framework CSS ---
orig = open(SRC, encoding="utf-8", errors="replace").read()
css = orig.split("<style>", 1)[1].split("</style>", 1)[0]

CUSTOM_CSS = r"""
/* ============ CUSTOM SLIDES (Robbin intern deck) ============ */
/* PIX card fan */
.pix-body { display:flex; align-items:center; gap:3vw; flex:1; min-height:0; margin-top:1vh; }
.pixfan { position:relative; flex:1.25; height:48vh; min-height:300px; }
.pcard {
  position:absolute; left:50%; top:7%;
  width:clamp(110px,9.2vw,156px);
  margin-left:calc(clamp(110px,9.2vw,156px) / -2);
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
.pres-grid { display:grid; grid-template-columns:1fr 1fr; gap:4vw; flex:1; min-height:0; margin-top:4vh; align-content:start; }
.pres { display:flex; flex-direction:column; gap:2.2vh; }
.pres-top { display:flex; align-items:center; gap:1.4vw; }
.pres-photo { width:clamp(74px,7vw,108px); height:clamp(74px,7vw,108px); border-radius:50%; object-fit:cover; filter:grayscale(1) contrast(1.05); flex-shrink:0; }
.pres-name { font-family:var(--font-sans); font-weight:700; letter-spacing:-.025em; font-size:clamp(22px,2.1vw,34px); }
.pres-role { font-family:var(--font-mono); font-size:11px; letter-spacing:.2em; text-transform:uppercase; color:var(--muted); margin-top:.6vh; }
.pres-bio { font-family:var(--font-sans); font-size:clamp(14px,1.05vw,18px); line-height:1.62; color:var(--muted-2); }
.pres-bio b { color:var(--ink); font-weight:600; }
.pres-tbd { font-family:var(--font-mono); font-size:12px; color:var(--muted); border:1px dashed rgba(12,12,12,.22); border-radius:10px; padding:1.6vh 1.2vw; letter-spacing:.04em; margin-top:auto; }

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
.tbd-wrap { flex:1; display:flex; flex-direction:column; justify-content:center; }
.tbd-box { border:1px dashed rgba(12,12,12,.25); border-radius:16px; padding:5vh 4vw; max-width:64ch; }
.tbd-tag { font-family:var(--font-mono); font-size:13px; letter-spacing:.22em; text-transform:uppercase; color:var(--muted); }
.tbd-box p { font-family:var(--font-sans); font-size:clamp(15px,1.1vw,20px); color:var(--muted-2); margin-top:1.4vh; line-height:1.6; }
.tbd-owner { position:absolute; top:5vh; right:4vw; z-index:6; font-family:var(--font-mono); font-size:11px; letter-spacing:.16em; text-transform:uppercase; color:var(--muted); border:1px solid rgba(12,12,12,.18); border-radius:100px; padding:6px 14px; }

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
      <div class="cover5-tag">A plataforma financeira da era da IA.</div>
    </div>
    <div class="cover5-meta">Confidencial</div>
  </section>

  <!-- 2 — CARTÃO PIX -->
  <section class="slide theme-light pix-slide" data-num="02">
    <div class="chapter-mark light-mark">
      <span class="chapter-num">01</span><span class="chapter-divider"></span><span class="chapter-year">O Cartão</span>
    </div>
    <div class="slide-head reveal">
      <h1>O cartão de crédito <span class="accent">sobre o trilho do PIX.</span></h1>
      <p class="sub">UX de cartão. Economia do PIX. Liquidação instantânea. Já no ar com âncoras co-brand.</p>
    </div>
    <div class="pix-body reveal">
      <div class="pixfan">
        <div class="pcard" style="--rot:-44deg; --d:.15s; z-index:1;"><img src="Chilli.png" alt="Chilli Beans"></div>
        <div class="pcard" style="--rot:-29deg; --d:.25s; z-index:2;"><img src="Brinox.png" alt="Grupo Brinox"></div>
        <div class="pcard" style="--rot:-14deg; --d:.35s; z-index:3;"><img src="Malwee.png" alt="Malwee"></div>
        <div class="pcard" style="--rot:14deg;  --d:.45s; z-index:5;"><img src="Cantu.png" alt="Cantu"></div>
        <div class="pcard" style="--rot:29deg;  --d:.5s;  z-index:4;"><img src="Credmoura.png" alt="CredMoura"></div>
        <div class="pcard" style="--rot:44deg;  --d:.6s;  z-index:2;"><img src="JSM.png" alt="Juntos Somos+"></div>
        <div class="pcard" style="--rot:0deg;   --d:.55s; z-index:10;"><img src="Robbin.png" alt="Robbin"></div>
      </div>
      <div class="pix-points" data-stagger>
        <div class="pix-point">
          <div class="pp-num">— 01</div>
          <div class="pp-title">Tempo real no PIX</div>
          <div class="pp-desc">Liquidação em segundos, 24/7. Sem interchange. Sem middleware de adquirência.</div>
        </div>
        <div class="pix-point">
          <div class="pp-num">— 02</div>
          <div class="pp-title">Insights exclusivos de PMEs</div>
          <div class="pp-desc">Dados de sell-out das marcas âncora embasam cada transação.</div>
        </div>
        <div class="pix-point">
          <div class="pp-num">— 03</div>
          <div class="pp-title">Co-branded com âncoras</div>
          <div class="pp-desc">Cantu, Brinox, Malwee, Chilli Beans, Baterias Moura, Juntos Somos Mais (Votorantim, Tigre, Gerdau) — já no ar.</div>
        </div>
      </div>
    </div>
  </section>

  <!-- 3 — APRESENTADORES -->
  <section class="slide theme-light" data-num="03">
    <div class="chapter-mark light-mark">
      <span class="chapter-num">02</span><span class="chapter-divider"></span><span class="chapter-year">Apresentadores</span>
    </div>
    <div class="slide-head reveal">
      <h1>Quem <span class="accent">apresenta.</span></h1>
    </div>
    <div class="pres-grid reveal" data-stagger>
      <div class="pres">
        <div class="pres-top">
          <img class="pres-photo" src="Tomas.jpeg" alt="Tomás Corrêa">
          <div>
            <div class="pres-name">Tomás Corrêa</div>
            <div class="pres-role">CTO &amp; Cofundador</div>
          </div>
        </div>
        <p class="pres-bio">Biólogo de formação, foi cofundador e <b>CTO da Open Co</b> (originalmente Geru), primeira credora 100% digital do Brasil, fundada em 2014. À frente da tecnologia da empresa entre 2014 e 2023, ajudou a construir a maior plataforma digital de crédito do país, com mais de <b>USD 1 bilhão</b> em empréstimos concedidos.</p>
      </div>
      <div class="pres">
        <div class="pres-top">
          <img class="pres-photo" src="Marcos.jpeg" alt="Marcos">
          <div>
            <div class="pres-name">Marcos</div>
            <div class="pres-role">Robbin</div>
          </div>
        </div>
        <p class="pres-bio">Apresenta a segunda parte do conteúdo de hoje.</p>
        <div class="pres-tbd">// Bio do Marcos — TBD</div>
      </div>
    </div>
  </section>

  <!-- 4 — ARQUITETURA -->
  <section class="slide theme-light" data-num="04">
    <div class="chapter-mark light-mark">
      <span class="chapter-num">03</span><span class="chapter-divider"></span><span class="chapter-year">Arquitetura</span>
    </div>
    <div class="slide-head reveal">
      <h1>Time não técnico no comando — <span class="accent">sem abrir mão de segurança.</span></h1>
      <p class="sub">4 camadas que separam o que muda rápido do que precisa ser estável: qualquer pessoa cria, a plataforma garante.</p>
    </div>
    <div class="layers reveal" data-stagger>
      <div class="layer">
        <span class="layer-num">01</span>
        <div>
          <h3>Vibe code + AI tools</h3>
          <p>Qualquer pessoa do time cria apps completos com IA. Skills e rules embutem o contexto da Robbin — a IA age como alguém do time, não como estranho.</p>
          <div class="chips"><span>velocidade máxima</span><span>tools.robbin.com.br</span><span>skills &amp; rules</span><span>Claude · Cursor</span></div>
        </div>
        <span class="layer-badge strong">move fast</span>
      </div>
      <div class="layer">
        <span class="layer-num">02</span>
        <div>
          <h3>BFF — Ops / Client / Partner</h3>
          <p>Três backends por audiência. Vibe code consome contratos estáveis — nunca acessa lógica interna diretamente.</p>
          <div class="chips"><span>contratos por audiência</span><span>single ALB</span></div>
        </div>
        <span class="layer-badge">fronteira</span>
      </div>
      <div class="layer hi">
        <span class="layer-num">03</span>
        <div>
          <h3>Platform — transacional + gerencial</h3>
          <p>7 micro-monólitos por fronteira de time. Data lake em 4 camadas para dados confiáveis. A estabilidade que deixa o vibe code voar.</p>
          <div class="chips"><span>auth · crédito · pagamentos · cartões</span><span>Kafka · Temporal</span><span>Snowflake · dbt</span></div>
        </div>
        <span class="layer-badge">estabilidade</span>
      </div>
      <div class="layer">
        <span class="layer-num">04</span>
        <div>
          <h3>Knowledge system — rules, skills, Ganesha</h3>
          <p>Contexto acumulado da Robbin disponível para qualquer IA. Sem isso, cada vibe code seria uma aposta.</p>
          <div class="chips"><span>behavioral rules</span><span>reusable skills</span><span>Ganesha — API catalog</span></div>
        </div>
        <span class="layer-badge">guardrail</span>
      </div>
    </div>
  </section>

  <!-- 5 — ROBBIN TOOLS (dark) -->
  <section class="slide theme-dark" data-num="05">
    <div class="chapter-mark">
      <span class="chapter-num">04</span><span class="chapter-divider"></span><span class="chapter-year">Robbin Tools</span>
    </div>
    <div class="slide-head reveal">
      <h1>Criar uma ferramenta <span class="muted">é só pedir.</span></h1>
      <p class="sub">O Claude cuida de todo o setup técnico. Você só descreve o que precisa. — tools.robbin.com.br</p>
    </div>
    <div class="flow reveal" data-stagger>
      <div class="flow-row">
        <div class="flow-spine"><div class="flow-dot"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></div><div class="flow-line"></div></div>
        <div class="flow-card">
          <div class="flow-label">Você</div>
          <div class="flow-title">Pede ao Claude para criar uma ferramenta</div>
          <div class="flow-bubble"><span class="flow-pill-inline">"Quero criar uma Robbin Tool para o time de ops"</span></div>
        </div>
      </div>
      <div class="flow-row">
        <div class="flow-spine"><div class="flow-dot"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg></div><div class="flow-line"></div></div>
        <div class="flow-card">
          <div class="flow-claude"><span class="pill">Claude</span><span class="flow-title" style="font-size:clamp(13px,1.1vw,18px)">Configura o ambiente automaticamente</span></div>
          <div class="flow-steps">
            <div class="flow-step"><b>1</b>Verifica e instala o Git</div>
            <div class="flow-step"><b>2</b>Gera a chave SSH</div>
            <div class="flow-step"><b>3</b>Autentica no GitHub</div>
            <div class="flow-step"><b>4</b>Clona o repositório ai-powers</div>
            <div class="flow-step"><b>5</b>Instala a skill create-robbin-tool</div>
          </div>
        </div>
      </div>
      <div class="flow-row">
        <div class="flow-spine"><div class="flow-dot"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg></div><div class="flow-line"></div></div>
        <div class="flow-card">
          <div class="flow-label">Você</div>
          <div class="flow-title">Descreve a ferramenta que quer criar</div>
          <div class="flow-bubble">O Claude pergunta: "O que ela faz? Quem vai usar? Como deve funcionar?"</div>
        </div>
      </div>
      <div class="flow-row">
        <div class="flow-spine"><div class="flow-dot"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></div></div>
        <div class="flow-done">
          <div class="ic"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#0C0C0C" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg></div>
          <div>
            <div class="flow-title">Ferramenta no ar</div>
            <div class="flow-bubble" style="font-style:normal;margin-top:2px;">Pronta para o time usar em tools.robbin.com.br</div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <!-- 6 — TBD MARCOS 1 -->
  <section class="slide theme-light" data-num="06">
    <div class="tbd-owner">Marcos · 01</div>
    <div class="chapter-mark light-mark">
      <span class="chapter-num">05</span><span class="chapter-divider"></span><span class="chapter-year">A definir</span>
    </div>
    <div class="tbd-wrap reveal">
      <div class="slide-head"><h1>Conteúdo do <span class="muted">Marcos.</span></h1></div>
      <div class="tbd-box" style="margin-top:4vh;">
        <div class="tbd-tag">// TBD</div>
        <p>Espaço reservado para o conteúdo que o Marcos vai apresentar. Estrutura e visual prontos — é só preencher.</p>
      </div>
    </div>
  </section>

  <!-- 7 — TBD MARCOS 2 -->
  <section class="slide theme-light" data-num="07">
    <div class="tbd-owner">Marcos · 02</div>
    <div class="chapter-mark light-mark">
      <span class="chapter-num">06</span><span class="chapter-divider"></span><span class="chapter-year">A definir</span>
    </div>
    <div class="tbd-wrap reveal">
      <div class="slide-head"><h1>Conteúdo do <span class="muted">Marcos.</span></h1></div>
      <div class="tbd-box" style="margin-top:4vh;">
        <div class="tbd-tag">// TBD</div>
        <p>Segundo slide reservado para o Marcos. Mesmo template — pronto para receber o conteúdo final.</p>
      </div>
    </div>
  </section>

  <!-- 8 — Q&A (closing) -->
  <section class="slide theme-dark closing2" data-num="08">
    <div class="closing2-bg"><div class="closing2-grid"></div><div class="closing2-glow"></div></div>
    <div class="closing2-inner">
      <div class="closing2-eyebrow reveal"><span>—</span><span>Discussão</span></div>
      <h2 class="closing2-line reveal">
        <span class="cl-row light">Perguntas</span>
        <span class="cl-row hi">&amp; Respostas</span>
      </h2>
      <div class="closing2-divider reveal"></div>
      <div class="closing2-logo reveal"><img src="robbin-logo-white.svg" alt="Robbin" style="height:46px;width:auto;"></div>
    </div>
  </section>

  <!-- 9 — VAGAS -->
  <section class="slide theme-light" data-num="09">
    <div class="chapter-mark light-mark">
      <span class="chapter-num">07</span><span class="chapter-divider"></span><span class="chapter-year">Junte-se ao time</span>
    </div>
    <div class="slide-head reveal">
      <h1>Vagas em <span class="accent">aberto.</span></h1>
      <p class="sub">Estamos construindo a plataforma financeira da era da IA — e queremos gente boa junto.</p>
    </div>
    <div class="vagas-grid reveal" data-stagger>
      <div class="vaga"><span class="vaga-num">01</span><div><h3>Summer em Engineering</h3><div class="vaga-meta">Programa de verão · Engenharia<br>São Paulo · Híbrido</div><div class="vaga-tags"><span>Summer</span><span>AI-first</span></div></div></div>
      <div class="vaga"><span class="vaga-num">02</span><div><h3>Summer em Data &amp; Analytics</h3><div class="vaga-meta">Programa de verão · Dados<br>São Paulo · Híbrido</div><div class="vaga-tags"><span>Summer</span><span>Analytics</span></div></div></div>
      <div class="vaga"><span class="vaga-num">03</span><div><h3>Intern em Strategic Finance</h3><div class="vaga-meta">Estágio · Finanças estratégicas<br>São Paulo · Híbrido</div><div class="vaga-tags"><span>Intern</span><span>Finance</span></div></div></div>
      <div class="vaga"><span class="vaga-num">04</span><div><h3>Intern em Data &amp; Analytics</h3><div class="vaga-meta">Estágio · Dados<br>São Paulo · Híbrido</div><div class="vaga-tags"><span>Intern</span><span>Analytics</span></div></div></div>
    </div>
    <div class="vagas-cta reveal">
      <span class="pill">careers@robbin.com.br</span>
      <span class="dim">— manda seu CV ou indica alguém</span>
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
<html lang="pt-BR">
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
          "Tomas.jpeg","Marcos.jpeg"]
preview = html
for a in assets:
    preview = preview.replace('src="%s"' % a, 'src="%s"' % datauri(a))
open("presentation-preview.html", "w", encoding="utf-8").write(preview)
left = re.findall(r'src="(?!data:)[^"]+"', preview)
print("preview:", len(preview), "bytes | remaining relative srcs:", left)
