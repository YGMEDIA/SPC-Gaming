
/* Hub-Seiten (iOS/Android/Universal): rendert passende Produkte aus products.json.
   Aktivierung über <div id="hubGrid" data-hub-platform="ios" data-hub-type="controller"></div> */
(function () {
  'use strict';
  // B9: Dieselbe Regel wie in scripts/produktdaten.py (detail_label). Sie steht hier
  // zwangslaeufig ein zweites Mal -- der Browser kann kein Python importieren --, und
  // verify.py prueft diese Fassung GEGEN die Python-Fassung, so wie bei A6_SCHWELLE.
  //
  // INNERHALB der IIFE, nicht davor. Die erste Fassung stand im globalen Scope, und drei
  // lexikalische `const` im globalen Scope machen zwei dieser Renderer gegenseitig
  // ausschliessend: Das zweite Skript stirbt mit "Identifier 'LABEL_TEST' has already
  // been declared" -- und zwar ganz, nicht nur die Deklaration. Heute laedt keine Seite
  // zwei davon, es war also keine Live-Stoerung, aber eine Mine, die es vor B9 nicht gab.
  const LABEL_TEST = 'Zum Test';
  const LABEL_DATENBLATT = 'Zum Kurzcheck';
  function detailLabel(detail) {
    return String(detail || '').startsWith('/produkte/') ? LABEL_DATENBLATT : LABEL_TEST;
  }

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

  // §A5-Verfuegbarkeit. Dieselbe Tabelle wie STOCK_LABEL/STOCK_KLASSE in
  // scripts/produktdaten.py; der Browser kann kein Python importieren, und verify.py
  // prueft diese Fassung GEGEN die Python-Fassung, so wie bei LABEL_TEST.
  // Ein fehlender oder unbekannter Wert ergibt KEIN "Verfügbar" -- genau diese
  // Behauptung ohne Beleg stand hier bis zum 06.10.2026 fest im Markup.
  //
  // INNERHALB der IIFE, aus demselben Grund wie LABEL_TEST: zwei dieser Renderer auf
  // einer Seite wuerden sich im globalen Scope gegenseitig abschalten.
  const STOCK_LABEL = {
    ja: 'Verfügbar', nein: 'Nicht verfügbar',
    gebraucht: 'Nur gebraucht', drittanbieter: 'Nur Drittanbieter'
  };
  const STOCK_KLASSE = {
    ja: 'in-stock', nein: 'out-stock',
    gebraucht: 'used-stock', drittanbieter: 'used-stock'
  };
  function stockHTML(p) {
    const k = STOCK_LABEL[p.stock] ? p.stock : '';
    return `<span class="${STOCK_KLASSE[k] || 'out-stock'}">${esc(STOCK_LABEL[k] || '')}</span>`;
  }

  function cardHTML(p, featured) {
    const specs = (p.specs || []).slice(0, 3).map(s =>
      `<span class="spec-tag"><span class="k">${esc(s[0])}</span> ${esc(s[1])}</span>`).join('');
    const detail = p.detail
      ? `<a href="${esc(p.detail)}" class="btn-detail">${esc(detailLabel(p.detail))}</a>` : '';
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
            <div class="price-row"><span class="price">${esc(p.price || '—')}</span>${stockHTML(p)}</div>
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
