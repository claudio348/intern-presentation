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
