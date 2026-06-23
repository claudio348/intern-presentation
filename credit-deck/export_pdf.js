const {chromium} = require('/opt/node22/lib/node_modules/playwright');
const {PDFDocument} = require('/tmp/pdfmerge/node_modules/pdf-lib');
const fs = require('fs');
(async () => {
  const out = process.argv[2] || '/home/user/intern-presentation/credit-deck/presentation.pdf';
  const b = await chromium.launch();
  const p = await b.newPage({viewport:{width:1280,height:720,deviceScaleFactor:2}});
  await p.goto('file:///home/user/intern-presentation/credit-deck/presentation.html', {waitUntil:'networkidle'});
  await p.addStyleTag({content:`.reveal,[data-stagger]>*{opacity:1!important;transform:none!important;animation:none!important}
    .deck-meta,.nav,.slide-counter,.deck-mark,.deck-mark-mini,.deck-nav{display:none!important}`});
  const n = await p.evaluate(()=>document.querySelectorAll('section.slide').length);
  const merged = await PDFDocument.create();
  for (let i=0;i<n;i++){
    await p.evaluate((idx)=>{
      const slides=[...document.querySelectorAll('section.slide')];
      slides.forEach((s,j)=>{ s.style.display = j===idx?'flex':'none'; s.classList.toggle('active', j===idx); });
    }, i);
    await new Promise(r=>setTimeout(r,120));
    const buf = await p.pdf({width:'1280px', height:'720px', printBackground:true, pageRanges:'1'});
    const doc = await PDFDocument.load(buf);
    const [pg] = await merged.copyPages(doc, [0]);
    merged.addPage(pg);
  }
  await b.close();
  fs.writeFileSync(out, await merged.save());
  console.log('wrote', out, 'pages:', merged.getPageCount());
})();
