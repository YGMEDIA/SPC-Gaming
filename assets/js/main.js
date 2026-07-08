/* ============================================================
   smartphone-controller.com — Global JavaScript
   ============================================================ */

(function () {
  'use strict';

  /* ---------- Config ---------- */
  const AFFILIATE_TAG = 'ygmedia-21';
  const DOMAIN = 'https://smartphone-controller.com';

  /* ---------- Header HTML ---------- */
  function buildHeader(activePage) {
    const nav = [
      { href: '/produkte/', label: 'Alle Produkte', icon: '🛒' },
      { href: '/controller-finder/', label: 'Controller-Finder', icon: '🎮' },
      { href: '/controller/ios/', label: 'iPhone' },
      { href: '/controller/android/', label: 'Android' },
      { href: '/controller/universal/', label: 'Universal' },
      { href: '/zubehoer/finger-sleeves/', label: 'Finger Sleeves' },
      { href: '/zubehoer/trigger/', label: 'Trigger' },
      { href: '/vergleich/', label: 'Vergleiche' },
      { href: '/ratgeber/', label: 'Ratgeber' },
      { href: '/marken/gamesir/', label: 'GameSir ★', badge: 'Top-Marke' },
    ];

    return `
<div class="trust-strip">
  <div class="container">
    <span class="ts">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.6"/></svg>
      Unabhängig & herstellerneutral
    </span>
    <span class="ts">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12l5 5L20 7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      100+ Controller getestet
    </span>
    <span class="ts">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M5 12l5 5L20 7" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
      Datenstand Juni 2026
    </span>
  </div>
</div>
<div class="header-main">
  <a href="/" class="logo" aria-label="smartphone-controller.com – Startseite">
    <span class="logo-mark" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none"><path d="M6 9h12a3 3 0 013 3v0a3 3 0 01-3 3h-1l-1.5-2h-7L7 15H6a3 3 0 01-3-3v0a3 3 0 013-3z" stroke="#fff" stroke-width="1.8"/><circle cx="8" cy="12" r="1.1" fill="#fff"/><circle cx="16.5" cy="11" r=".9" fill="#fff"/><circle cx="16.5" cy="13" r=".9" fill="#fff"/></svg>
    </span>
    <span class="logo-text">smartphone-controller<span class="logo-tld">.com</span></span>
  </a>
  <div class="searchbar" role="search">
    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="11" cy="11" r="7" stroke="currentColor" stroke-width="2"/><path d="M21 21l-4-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
    <input type="text" placeholder="Controller, Marke, Modell …" aria-label="Suche" id="siteSearch">
  </div>
  <div class="header-actions">
    <a href="/ratgeber/" class="header-action-btn">
      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>
      <span class="lbl">Ratgeber</span>
    </a>
  </div>
</div>
<nav class="main-nav" aria-label="Hauptnavigation">
  <div class="container">
    ${nav.map(n => `
    <a href="${n.href}" class="nav-link${activePage === n.href ? ' active' : ''}"
       ${activePage === n.href ? 'aria-current="page"' : ''}>
      ${n.icon ? n.icon + ' ' : ''}${n.label}
      ${n.badge ? `<span class="nav-badge">${n.badge}</span>` : ''}
    </a>`).join('')}
  </div>
</nav>`;
  }

  /* ---------- Footer HTML ---------- */
  function buildFooter() {
    return `
<div class="foot-promo-bar">
  <div class="container">
    <div class="foot-promo">
      <span class="foot-promo-ico"><svg viewBox="0 0 24 24" fill="none"><path d="M9 12l2 2 4-4" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.6"/></svg></span>
      <div><div class="foot-promo-t">Unabhängig getestet</div><div class="foot-promo-s">Keine bezahlten Platzierungen</div></div>
    </div>
    <div class="foot-promo">
      <span class="foot-promo-ico"><svg viewBox="0 0 24 24" fill="none"><path d="M4 7l8-4 8 4v6c0 5-3.5 7.5-8 9-4.5-1.5-8-4-8-9V7z" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/></svg></span>
      <div><div class="foot-promo-t">Aktuelle Daten</div><div class="foot-promo-s">Preise & Specs laufend geprüft</div></div>
    </div>
    <div class="foot-promo">
      <span class="foot-promo-ico"><svg viewBox="0 0 24 24" fill="none"><path d="M3 12h4l2-7 4 14 2-7h6" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
      <div><div class="foot-promo-t">Echte Testkriterien</div><div class="foot-promo-s">Latenz, Hall-Effect, Ergonomie</div></div>
    </div>
    <div class="foot-promo">
      <span class="foot-promo-ico"><svg viewBox="0 0 24 24" fill="none"><path d="M12 3v18M5 8l7-5 7 5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg></span>
      <div><div class="foot-promo-t">Bestpreis-Links</div><div class="foot-promo-s">Direkt zum günstigsten Händler</div></div>
    </div>
  </div>
</div>
<div class="container">
  <div class="foot-cols">
    <div class="foot-brand">
      <div class="foot-brand-logo">
        <a href="/" class="logo" aria-label="smartphone-controller.com">
          <span class="logo-mark" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none"><path d="M6 9h12a3 3 0 013 3v0a3 3 0 01-3 3h-1l-1.5-2h-7L7 15H6a3 3 0 01-3-3v0a3 3 0 013-3z" stroke="#fff" stroke-width="1.8"/><circle cx="8" cy="12" r="1.1" fill="#fff"/><circle cx="16.5" cy="11" r=".9" fill="#fff"/><circle cx="16.5" cy="13" r=".9" fill="#fff"/></svg>
          </span>
          <span class="logo-text">smartphone-controller<span class="logo-tld">.com</span></span>
        </a>
      </div>
      <p>Das unabhängige Fachportal für Smartphone-Gaming-Controller. Wir testen, vergleichen und erklären – damit du den passenden Controller findest, nicht nur den teuersten.</p>
      <div class="foot-rating">
        <div class="foot-stars" aria-hidden="true">
          <svg viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
          <svg viewBox="0 0 24 24" class="star-half"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
        </div>
        <div class="foot-rating-text">Wir empfehlen nur Controller mit <strong>4★+ auf Amazon</strong> — top-bewertete Modelle, ehrlich getestet.</div>
      </div>
    </div>
    <div class="foot-col">
      <h4>Controller</h4>
      <a href="/produkte/">Alle Produkte</a>
      <a href="/controller/">Alle Controller</a>
      <a href="/controller/ios/">iPhone Controller</a>
      <a href="/controller/android/">Android Controller</a>
      <a href="/controller/universal/">Universal</a>
      <a href="/controller/mini-gamepad/">Mini-Gamepads</a>
    </div>
    <div class="foot-col">
      <h4>Zubehör</h4>
      <a href="/zubehoer/finger-sleeves/">Finger Sleeves</a>
      <a href="/zubehoer/trigger/">Trigger & Auslöser</a>
      <a href="/zubehoer/handy-kuehler/">Handy-Kühler</a>
    </div>
    <div class="foot-col">
      <h4>Marken</h4>
      <a href="/marken/gamesir/">GameSir</a>
      <a href="/marken/razer/">Razer</a>
      <a href="/marken/backbone/">Backbone</a>
      <a href="/marken/8bitdo/">8BitDo</a>
    </div>
    <div class="foot-col">
      <h4>Über uns</h4>
      <a href="/ueber-uns/">Über uns</a>
      <a href="/redaktion/">Testmethodik</a>
      <a href="/affiliate-hinweis/">Affiliate-Info</a>
      <a href="/kontakt/">Kontakt</a>
      <a href="/ratgeber/">Alle Ratgeber</a>
    </div>
  </div>
  <p class="foot-affiliate">
    Transparenz-Hinweis: Einige Links auf dieser Seite sind Affiliate-Links (Amazon PartnerNet). Kaufst du über einen solchen Link, erhalten wir eine kleine Provision — für dich ändert sich der Preis nicht. Das beeinflusst unsere Tests und Bewertungen nicht.
  </p>
</div>
<div class="foot-bottom">
  <div class="container">
    <div class="foot-legal">
      <a href="/impressum/">Impressum</a>
      <a href="/datenschutz/">Datenschutz</a>
      <a href="/affiliate-hinweis/">Affiliate</a>
      <a href="/sitemap.xml">Sitemap</a>
      <span>© 2026 YG MEDIA</span>
    </div>
    <div class="foot-pay">
      <span class="foot-amazon-badge">
        <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true"><path d="M4 8h16M4 8l1.5 9.5a2 2 0 002 1.5h5a2 2 0 002-1.5L16 8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/></svg>
        Offizieller <strong>Amazon</strong>-Partner
      </span>
    </div>
  </div>
</div>`;
  }

  /* ---------- Inject Header & Footer ---------- */
  function enhance(root) {
      // Affiliate link handling — append tag automatically
      root.querySelectorAll('a[data-asin]').forEach(link => {
        const asin = link.dataset.asin;
        if (asin) {
          link.href = `https://www.amazon.de/dp/${asin}?tag=${AFFILIATE_TAG}`;
          link.rel = 'nofollow sponsored noopener';
          link.target = '_blank';
        }
      });
  
      // Product images — render data-img as <img>, keep icon as fallback.
      // Source priority: card's own data-img > any child element's data-img.
      root.querySelectorAll('.pcard-img').forEach(imgBox => {
        const card = imgBox.closest('.pcard') || imgBox.parentElement;
        const src = imgBox.dataset.img ||
                    card?.dataset.img ||
                    card?.querySelector('[data-img]')?.dataset.img;
        if (!src) return; // no image → leave the emoji icon in place
        const iconEl = imgBox.querySelector('.product-icon');
        const name = card?.querySelector('.pcard-name')?.textContent?.trim() || 'Produkt';
        const img = document.createElement('img');
        img.className = 'pcard-photo';
        img.src = src;
        img.alt = name;
        img.loading = 'lazy';
        // If the image fails to load, fall back to the icon.
        img.addEventListener('error', () => {
          img.remove();
          if (iconEl) iconEl.style.display = '';
        });
        if (iconEl) iconEl.style.display = 'none';
        imgBox.appendChild(img);
      });
  
      // Make whole product cards clickable.
      // Priority: internal review page (.btn-detail) > Amazon link as fallback.
      // The Amazon button keeps its own behaviour and is excluded from the card click.
      root.querySelectorAll('.pcard').forEach(card => {
        const detailLink = card.querySelector('.btn-detail[href]:not([href="#"])');
        const amazonLink = card.querySelector('.btn-amazon');
        const target = detailLink || amazonLink;
        if (!target) return;
  
        // Rename the detail button label to "Mehr erfahren" for consistency.
        if (detailLink && /zum test|details/i.test(detailLink.textContent)) {
          detailLink.textContent = 'Mehr erfahren';
        }
  
        card.classList.add('pcard-clickable');
        card.addEventListener('click', function (e) {
          // Ignore clicks on real links/buttons inside the card.
          if (e.target.closest('a, button')) return;
          if (detailLink) {
            window.location.href = detailLink.getAttribute('href');
          } else if (amazonLink) {
            amazonLink.click();
          }
        });
        // Keyboard accessibility: Enter/Space activates the card.
        card.setAttribute('tabindex', '0');
        card.setAttribute('role', 'link');
        const label = card.querySelector('.pcard-name')?.textContent?.trim();
        if (label) card.setAttribute('aria-label', label + ' – Details ansehen');
        card.addEventListener('keydown', function (e) {
          if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            (detailLink || amazonLink).click ? (detailLink ? window.location.href = detailLink.getAttribute('href') : amazonLink.click()) : null;
          }
        });
      });
  
  }

  // Expose so dynamically-rendered pages (e.g. /produkte/) can enhance new cards.
  window.SPCEnhance = enhance;

  function init() {
    const headerEl = document.getElementById('site-header');
    const footerEl = document.getElementById('site-footer');

    // Determine active page from data attribute or current path
    const activePage = document.documentElement.dataset.activePage ||
      window.location.pathname;

    if (headerEl) headerEl.innerHTML = buildHeader(activePage);
    if (footerEl) footerEl.innerHTML = buildFooter();

    // Enhance static + future dynamic product cards
    enhance(document);

    // Track affiliate clicks (for GA4 via GTM later)
    document.querySelectorAll('a[data-asin], .btn-amazon').forEach(link => {
      link.addEventListener('click', function () {
        const productName = this.dataset.product || this.closest('[data-product]')?.dataset.product || 'unknown';
        if (typeof gtag === 'function') {
          gtag('event', 'affiliate_click', {
            product_name: productName,
            destination: this.href
          });
        }
      });
    });

    // Simple search (redirects to /suche/ with query param)
    const searchInput = document.getElementById('siteSearch');
    if (searchInput) {
      searchInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && this.value.trim()) {
          window.location.href = `/suche/?q=${encodeURIComponent(this.value.trim())}`;
        }
      });
    }

    // Set current year in footer copyright if needed
    document.querySelectorAll('.current-year').forEach(el => {
      el.textContent = new Date().getFullYear();
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
