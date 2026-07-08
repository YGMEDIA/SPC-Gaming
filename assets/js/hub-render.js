/* Hub-Seiten (iOS/Android/Universal): rendert passende Produkte aus products.json.
   Aktivierung über <div id="hubGrid" data-hub-platform="ios" data-hub-type="controller"></div> */
(function () {
  'use strict';

  const grid = document.getElementById('hubGrid');
  if (!grid) return;

  const wantPlatform = grid.dataset.hubPlatform || null;   // ios | android | universal | ...
  const wantType = grid.dataset.hubType || 'controller';   // controller | zubehoer
  const sortMode = grid.dataset.hubSort || 'featured';

  function esc(s) {
    return (s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  }
  function priceNum(p) {
    const m = (p.price || '').replace(/\s/g, '').match(/(\d+)/);
    return m ? parseInt(m[1], 10) : Number.MAX_SAFE_INTEGER;
  }

  function cardHTML(p, featured) {
    const specs = (p.specs || []).slice(0, 3).map(s =>
      `<span class="spec-tag"><span class="k">${esc(s[0])}</span> ${esc(s[1])}</span>`).join('');
    const detail = p.detail
      ? `<a href="${esc(p.detail)}" class="btn-detail">Mehr erfahren</a>` : '';
    const img = p.img ? ` data-img="${esc(p.img)}"` : '';
    const icon = p.type === 'zubehoer'
      ? (p.platform === 'kuehler' ? '❄️' : p.platform === 'finger-sleeves' ? '🧤' : '🎯')
      : '🎮';
    return `
      <article class="pcard${featured ? ' featured' : ''}" data-product="${esc(p.slug)}">
        <div class="pcard-img"><div class="product-icon">${icon}</div></div>
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
  }

  fetch('/assets/data/products.json')
    .then(r => r.json())
    .then(data => {
      let list = data.filter(p => {
        if (wantType && p.type !== wantType) return false;
        if (wantPlatform) {
          const compat = p.worksOn && p.worksOn.length ? p.worksOn : [p.platform];
          if (!compat.includes(wantPlatform)) return false;
        }
        return true;
      });

      if (sortMode === 'price-asc') list.sort((a, b) => priceNum(a) - priceNum(b));

      grid.innerHTML = list.map((p, i) => cardHTML(p, i === 0)).join('');

      // Optional count element
      const countEl = document.getElementById('hubCount');
      if (countEl) countEl.textContent = list.length === 1 ? '1 Modell' : `${list.length} Modelle`;

      if (window.SPCEnhance) window.SPCEnhance(grid);
    })
    .catch(() => {
      grid.innerHTML = '<p style="grid-column:1/-1;color:var(--ink-soft)">Produkte konnten nicht geladen werden.</p>';
    });
})();
