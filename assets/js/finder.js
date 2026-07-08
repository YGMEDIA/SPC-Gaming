/* Controller-Finder: 3 Fragen → Match-Score gegen products.json → Top-Empfehlungen. */
(function () {
  'use strict';

  const finder = document.getElementById('finder');
  if (!finder) return;

  const answers = { platform: null, budget: null, prio: null };
  let step = 0;
  let PRODUCTS = [];

  const steps = finder.querySelectorAll('.finder-step');
  const result = finder.querySelector('.finder-result');
  const progress = finder.querySelectorAll('.fp-step');

  function esc(s) {
    return (s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  }
  function priceNum(p) {
    const m = (p.price || '').replace(/\s/g, '').match(/(\d+)/);
    return m ? parseInt(m[1], 10) : 999;
  }

  function show(n) {
    steps.forEach(s => s.classList.toggle('is-active', +s.dataset.step === n));
    result.classList.toggle('is-active', n === 'result');
    progress.forEach(p => {
      const idx = +p.dataset.step;
      p.classList.toggle('is-active', typeof n === 'number' && idx <= n);
    });
    step = n;
    finder.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // Rating aus specs ziehen (z.B. "4,2 (450)")
  function ratingOf(p) {
    for (const [k, v] of (p.specs || [])) {
      if (/bew/i.test(k)) {
        const m = v.replace(',', '.').match(/([\d.]+)/);
        if (m) return parseFloat(m[1]);
      }
    }
    return 0;
  }

  function score(p) {
    let s = 0;
    // Plattform
    const compat = p.worksOn && p.worksOn.length ? p.worksOn : [p.platform];
    if (answers.platform === 'any') s += 2;
    else if (compat.includes(answers.platform)) s += 5;
    else return -1; // passt gar nicht

    // Budget
    const price = priceNum(p);
    if (answers.budget === 'low' && price <= 50) s += 4;
    else if (answers.budget === 'mid' && price > 50 && price <= 100) s += 4;
    else if (answers.budget === 'high' && price > 100) s += 4;
    else if (answers.budget === 'any') s += 2;
    else s += Math.max(0, 3 - Math.abs(price - ({ low: 40, mid: 75, high: 130 }[answers.budget] || 75)) / 40);

    // Priorität
    const rating = ratingOf(p);
    const specsText = (p.specs || []).map(x => x.join(' ')).join(' ').toLowerCase();
    if (answers.prio === 'quality') {
      s += rating >= 4.3 ? 4 : rating >= 4 ? 2 : 0;
      if (/hall|tmr/.test(specsText)) s += 2;
    } else if (answers.prio === 'value') {
      if (rating >= 4 && price <= 80) s += 4;
      else if (rating >= 3.8) s += 2;
      s += Math.max(0, 2 - price / 60);
    } else if (answers.prio === 'portable') {
      if (/mini|snap|138|leicht|kompakt/.test((p.name + specsText).toLowerCase())) s += 3;
      if (p.platform === 'mini') s += 2;
      s += rating >= 4 ? 1 : 0;
    }
    return s;
  }

  function renderResults() {
    let ranked = PRODUCTS
      .filter(p => p.type === 'controller')
      .map(p => ({ p, s: score(p) }))
      .filter(x => x.s > 0)
      .sort((a, b) => b.s - a.s)
      .slice(0, 3);

    const grid = document.getElementById('finderMatches');
    const title = document.getElementById('finderResultTitle');

    if (!ranked.length) {
      title.textContent = 'Keine perfekte Übereinstimmung';
      grid.innerHTML = '<p style="grid-column:1/-1;color:var(--ink-soft)">Für diese Kombination haben wir keinen idealen Treffer. Schau dir am besten <a href="/produkte/">alle Produkte</a> an.</p>';
      show('result');
      return;
    }
    title.textContent = ranked.length === 1 ? 'Deine Empfehlung' : `Deine Top ${ranked.length} Empfehlungen`;

    grid.innerHTML = ranked.map(({ p }, i) => {
      const specs = (p.specs || []).slice(0, 3).map(x =>
        `<span class="spec-tag"><span class="k">${esc(x[0])}</span> ${esc(x[1])}</span>`).join('');
      const detail = p.detail ? `<a href="${esc(p.detail)}" class="btn-detail">Mehr erfahren</a>` : '';
      const img = p.img ? ` data-img="${esc(p.img)}"` : '';
      const badge = i === 0 ? '<span class="pcard-badge badge-top">Bester Match</span>' : '';
      return `
        <article class="pcard${i === 0 ? ' featured' : ''}" data-product="${esc(p.slug)}">
          <div class="pcard-img">${badge}<div class="product-icon">🎮</div></div>
          <div class="pcard-body">
            <div class="pcard-brand">${esc(p.brand || '—')}</div>
            <h2 class="pcard-name">${esc(p.name)}</h2>
            ${p.claim ? `<p class="pcard-claim">${esc(p.claim)}</p>` : ''}
            <div class="pcard-specs">${specs}</div>
            <div class="pcard-foot">
              <div class="price-row"><span class="price">${esc(p.price || '—')}</span><span class="in-stock">Verfügbar</span></div>
              <div class="pcard-actions">${detail}<a class="btn-amazon" data-asin="${esc(p.asin)}" data-product="${esc(p.slug)}" href="#"${img}>Kaufen →</a></div>
            </div>
          </div>
        </article>`;
    }).join('');

    show('result');
    if (window.SPCEnhance) window.SPCEnhance(grid);
    if (typeof window.gtag === 'function') {
      window.gtag('event', 'finder_complete', { platform: answers.platform, budget: answers.budget, prio: answers.prio });
    }
  }

  // Antwort-Buttons
  finder.querySelectorAll('.finder-opt').forEach(btn => {
    btn.addEventListener('click', () => {
      answers[btn.dataset.key] = btn.dataset.value;
      if (step < 2) show(step + 1);
      else renderResults();
    });
  });
  // Zurück
  finder.querySelectorAll('[data-back]').forEach(btn => {
    btn.addEventListener('click', () => { if (step > 0) show(step - 1); });
  });
  // Neu starten
  document.getElementById('finderRestart').addEventListener('click', () => {
    answers.platform = answers.budget = answers.prio = null;
    show(0);
  });

  fetch('/assets/data/products.json')
    .then(r => r.json())
    .then(data => { PRODUCTS = data; })
    .catch(() => {});
})();
