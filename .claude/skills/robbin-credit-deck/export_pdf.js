// Render each slide of a built Robbin deck to one landscape PDF page and merge.
// Usage: node export_pdf.js [presentation.html] [out.pdf]
// Deps: playwright + pdf-lib. If not resolvable locally, this tries a couple of
// known locations; otherwise run `npm install playwright pdf-lib` in the cwd.
function req(name, extra) {
  for (const p of [name, ...(extra||[])]) { try { return require(p); } catch (e) {} }
  throw new Error(`Cannot resolve '${name}'. Run: npm install ${name}`);
}
const { chromium } = req('playwright', ['/opt/node22/lib/node_modules/playwright']);
const { PDFDocument } = req('pdf-lib', ['/tmp/pdfmerge/node_modules/pdf-lib']);
const fs = require('fs'); const path = require('path');

const htmlArg = process.argv[2] || 'presentation.html';
const out = process.argv[3] || 'presentation.pdf';
const fileUrl = 'file://' + path.resolve(htmlArg);

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720, deviceScaleFactor: 2 } });
  await p.goto(fileUrl, { waitUntil: 'networkidle' });
  // freeze animations, hide the on-screen nav/counter (they are not part of the print)
  await p.addStyleTag({ content: `.reveal,[data-stagger]>*{opacity:1!important;transform:none!important;animation:none!important}
    .deck-meta,.nav,.slide-counter,.deck-mark,.deck-mark-mini,.deck-nav{display:none!important}` });
  const n = await p.evaluate(() => document.querySelectorAll('section.slide').length);
  const merged = await PDFDocument.create();
  for (let i = 0; i < n; i++) {
    await p.evaluate((idx) => {
      const slides = [...document.querySelectorAll('section.slide')];
      slides.forEach((s, j) => { s.style.display = j === idx ? 'flex' : 'none'; s.classList.toggle('active', j === idx); });
    }, i);
    await new Promise(r => setTimeout(r, 120));
    const buf = await p.pdf({ width: '1280px', height: '720px', printBackground: true, pageRanges: '1' });
    const doc = await PDFDocument.load(buf);
    const [pg] = await merged.copyPages(doc, [0]);
    merged.addPage(pg);
  }
  await b.close();
  fs.writeFileSync(out, await merged.save());
  console.log('wrote', out, 'pages:', merged.getPageCount());
})();
