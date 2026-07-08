/* Alle-Produkte-Seite: lädt products.json, rendert Karten, filtert & sortiert. */
(function () {
  'use strict';

  const TYPE_LABELS = { controller: 'Controller', zubehoer: 'Zubehör' };
  const PLATFORM_LABELS = {
    ios: 'iPhone', android: 'Android', universal: 'Universal',
    tablet: 'Tablet', mini: 'Mini-Gamepad',
    'finger-sleeves': 'Finger Sleeves', trigger: 'Trigger', kuehler: 'Handy-Kühler'
  };

  const state = { type: null, platform: null, brand: null, q: '', sort: 'featured' };
  let PRODUCTS = [];

  const grid = document.getElementById('productGrid');
  const empty = document.getElementById('emptyState');
  const countEl = document.getElementById('resultCount');
  const resetBtn = document.getElementById('filterReset');

  function priceNum(p) {
    const m = (p.price || '').replace(/\s/g, '').match(/(\d+)/);
    return m ? parseInt(m[1], 10) : Number.MAX_SAFE_INTEGER;
  }

  function esc(s) {
    return (s || '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  }

  function cardHTML(p) {
    const specs = (p.specs || []).slice(0, 3).map(s =>
      `<span class="spec-tag"><span class="k">${esc(s[0])}</span> ${esc(s[1])}</span>`).join('');
    const detail = p.detail || '';
    const detailBtn = detail
      ? `<a href="${esc(detail)}" class="btn-detail">Mehr erfahren</a>`
      : '';
    const img = p.img ? ` data-img="${esc(p.img)}"` : '';
    const icon = p.type === 'zubehoer'
      ? (p.platform === 'kuehler' ? '❄️' : p.platform === 'finger-sleeves' ? '🧤' : '🎯')
      : '🎮';
    return `
      <article class="pcard" data-product="${esc(p.slug)}">
        <div class="pcard-img"><div class="product-icon">${icon}</div></div>
        <div class="pcard-body">
          <div class="pcard-brand">${esc(p.brand || '—')}</div>
          <h2 class="pcard-name">${esc(p.name)}</h2>
          ${p.claim ? `<p class="pcard-claim">${esc(p.claim)}</p>` : ''}
          <div class="pcard-specs">${specs}</div>
          <div class="pcard-foot">
            <div class="price-row"><span class="price">${esc(p.price || '—')}</span><span class="in-stock">Verfügbar</span></div>
            <div class="pcard-actions">${detailBtn}<a class="btn-amazon" data-asin="${esc(p.asin)}" data-product="${esc(p.slug)}" href="#"${img}>Amazon →</a></div>
          </div>
        </div>
      </article>`;
  }

  function apply() {
    let list = PRODUCTS.filter(p => {
      if (state.type && p.type !== state.type) return false;
      if (state.platform && p.platform !== state.platform) return false;
      if (state.brand && (p.brand || '') !== state.brand) return false;
      if (state.q) {
        const hay = (p.name + ' ' + p.brand + ' ' + p.claim).toLowerCase();
        if (!hay.includes(state.q.toLowerCase())) return false;
      }
      return true;
    });

    if (state.sort === 'price-asc') list.sort((a, b) => priceNum(a) - priceNum(b));
    else if (state.sort === 'price-desc') list.sort((a, b) => priceNum(b) - priceNum(a));
    else if (state.sort === 'name') list.sort((a, b) => a.name.localeCompare(b.name, 'de'));
    // 'featured' keeps json order (already curated)

    grid.innerHTML = list.map(cardHTML).join('');
    empty.hidden = list.length > 0;
    grid.hidden = list.length === 0;
    countEl.textContent = list.length === 1 ? '1 Produkt' : `${list.length} Produkte`;

    const active = state.type || state.platform || state.brand || state.q;
    resetBtn.hidden = !active;

    // Re-run main.js enhancers (affiliate links, images, clickable cards) on new nodes.
    if (window.SPCEnhance) window.SPCEnhance(grid);
  }

  function buildChips(containerId, facet, values, labelMap) {
    const c = document.getElementById(containerId);
    c.innerHTML = values.map(v => {
      const label = labelMap ? (labelMap[v] || v) : v;
      return `<button type="button" class="chip" data-facet="${facet}" data-value="${esc(v)}">${esc(label)}</button>`;
    }).join('');
    c.addEventListener('click', e => {
      const btn = e.target.closest('.chip');
      if (!btn) return;
      const val = btn.dataset.value;
      state[facet] = state[facet] === val ? null : val;
      c.querySelectorAll('.chip').forEach(x => x.classList.toggle('active', x.dataset.value === state[facet]));
      apply();
    });
  }

  function resetAll() {
    state.type = state.platform = state.brand = null;
    state.q = '';
    document.getElementById('prodSearch').value = '';
    document.querySelectorAll('.chip.active').forEach(x => x.classList.remove('active'));
    apply();
  }

  fetch('/assets/data/products.json')
    .then(r => r.json())
    .then(data => {
      PRODUCTS = data;

      const types = [...new Set(data.map(p => p.type))];
      const platforms = [...new Set(data.map(p => p.platform))];
      const brands = [...new Set(data.map(p => p.brand).filter(Boolean))].sort((a, b) => a.localeCompare(b, 'de'));

      buildChips('chipsType', 'type', types, TYPE_LABELS);
      buildChips('chipsPlatform', 'platform', platforms, PLATFORM_LABELS);
      buildChips('chipsBrand', 'brand', brands, null);

      // Read initial filter from URL (?typ=controller&platform=ios&marke=GameSir)
      const params = new URLSearchParams(location.search);
      if (params.get('typ')) state.type = params.get('typ');
      if (params.get('platform')) state.platform = params.get('platform');
      if (params.get('marke')) state.brand = params.get('marke');
      if (params.get('q')) { state.q = params.get('q'); document.getElementById('prodSearch').value = state.q; }
      document.querySelectorAll('.chip').forEach(x => {
        const f = x.dataset.facet;
        if (state[f] === x.dataset.value) x.classList.add('active');
      });

      document.getElementById('prodSearch').addEventListener('input', e => { state.q = e.target.value; apply(); });
      document.getElementById('prodSort').addEventListener('change', e => { state.sort = e.target.value; apply(); });
      resetBtn.addEventListener('click', resetAll);
      document.getElementById('emptyReset').addEventListener('click', resetAll);

      apply();
    })
    .catch(() => {
      grid.innerHTML = '<p style="grid-column:1/-1;color:var(--ink-soft)">Produkte konnten nicht geladen werden. Bitte lade die Seite neu.</p>';
    });
})();
