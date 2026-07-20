# -*- coding: utf-8 -*-
"""Erzeugt /produkte/<slug>/ für Longtail-Altmodelle aus longtail.json (Pattern P-6).

Abgrenzung zu gen_pages.py: KEINE Preise, KEINE Ratings, KEIN Kauflink für das
Altmodell selbst (§A5 — keine erfundenen Daten). Stattdessen ehrlicher
Verfügbarkeits-Hinweis + 2-3 kaufbare Alternativen aus products.json als
Konversionspfad. Idempotent: kompletter Overwrite pro Lauf.
"""
import json, os, html, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = 'https://smartphone-controller.com'

longtail = json.load(open(f'{ROOT}/assets/data/longtail.json'))
products = json.load(open(f'{ROOT}/assets/data/products.json'))
by_slug = {p['slug']: p for p in products}

def esc(s): return html.escape(str(s), quote=True)

def detail_url(p):
    return p['detail'] if p['detail'] else f"/produkte/{p['slug']}/"

def build(item):
    slug = item['slug']
    url = f"{DOMAIN}/produkte/{slug}/"
    full_name = item['name'] if item['brand'].lower() in item['name'].lower() else f"{item['brand']} {item['name']}"
    title = f"{full_name}: Datenblatt, Einordnung & Alternativen"
    if len(title) > 62:
        title = f"{full_name}: Datenblatt & Alternativen"
    assert len(title) <= 62, f"Title zu lang ({len(title)}): {title}"
    title += " | smartphone-controller.com"
    desc = item['verdict'][:158].rsplit(' ', 1)[0] + ' …' if len(item['verdict']) > 158 else item['verdict']
    og_img = f"{DOMAIN}/assets/img/og-default.jpg"

    # --- Schemas: KEIN Product-Schema. Google verlangt bei Product zwingend offers,
    # review oder aggregateRating (GSC-Kritikmeldung WNC-10030322 vom 20.07.2026);
    # ohne belegbaren Preis/Rating (§A5) bleibt nur der Verzicht. Breadcrumb + FAQ reichen.
    schema_bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
        {"@type": "ListItem", "position": 2, "name": "Controller", "item": DOMAIN + "/controller/"},
        {"@type": "ListItem", "position": 3, "name": full_name, "item": url},
    ]}
    schema_faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in item['faqs']]}
    schemas = '\n'.join(
        f'<script type="application/ld+json">\n{json.dumps(s, ensure_ascii=False, indent=1)}\n</script>'
        for s in [schema_bc, schema_faq])

    specs_rows = '<tr><td>Status</td><td>Altmodell, nicht mehr regulär erhältlich</td></tr>\n'
    for k, v in item['specs']:
        specs_rows += f'<tr><td>{esc(k)}</td><td>{esc(v)}</td></tr>\n'
    specs_rows += '<tr><td>Kategorie</td><td><a href="/controller/">Alle Controller im Überblick</a></td></tr>'

    paras = '\n'.join(f'<p>{esc(x)}</p>' for x in item['desc'])
    faq_html = '\n'.join(
        f'<div class="faq-item"><h3 class="faq-q">{esc(q)}</h3><p class="faq-a">{esc(a)}</p></div>'
        for q, a in item['faqs'])

    alts = [by_slug[s] for s in item['alternatives']]
    alt_cards = ''.join(
        f'<a href="{detail_url(a)}" class="related-card"><span class="rc-icon">🎮</span>'
        f'<div><div class="rc-name">{esc(a["brand"])} {esc(a["name"])}</div>'
        f'<div class="rc-price">{esc(a["price"] or "Preis auf Amazon")}</div></div>'
        f'<span class="rc-arrow">›</span></a>' for a in alts)
    top_alt = alts[0]

    return f'''<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(desc)}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="product">
  <meta property="og:title" content="{esc(full_name)} — Datenblatt & Alternativen">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="smartphone-controller.com">
  <meta property="og:locale" content="de_DE">
  <meta property="og:image" content="{og_img}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(full_name)} — Datenblatt & Alternativen">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{og_img}">
  <link rel="stylesheet" href="/assets/css/style.css">
  <style>
.review-grid{{display:grid;grid-template-columns:1fr 300px;gap:32px;align-items:start}}
.specs-table{{width:100%;border-collapse:collapse;margin:16px 0}}
.specs-table tr{{border-bottom:1px solid var(--line)}}
.specs-table td{{padding:10px 12px;font-size:14px}}
.specs-table td:first-child{{color:var(--ink-dim);font-weight:600;width:40%}}
.review-body h2{{font-size:22px;font-weight:800;margin:28px 0 12px;letter-spacing:-.01em}}
.review-body p{{font-size:15px;line-height:1.7;color:var(--ink-soft);margin-bottom:14px}}
.verdict-box{{background:var(--blue-bg);border:1px solid var(--blue-dim);border-radius:var(--radius-lg);padding:20px 24px;margin:24px 0}}
.verdict-box .vb-label{{font-size:11px;font-weight:800;color:var(--blue);text-transform:uppercase;letter-spacing:.06em;margin-bottom:6px}}
.verdict-box .vb-text{{font-size:15px;font-weight:700;color:var(--ink);line-height:1.5}}
.avail-box{{background:#fbf4f2;border:1px solid #e8cfc8;border-radius:var(--radius-lg);padding:16px 20px;margin:20px 0;font-size:14px;line-height:1.6;color:#7a3a2c}}
.avail-box strong{{display:block;margin-bottom:4px;font-size:12px;text-transform:uppercase;letter-spacing:.05em}}
.sticky-cta{{position:sticky;top:184px}}
.cta-box{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius-lg);padding:20px;box-shadow:var(--shadow-md)}}
.cta-box .cta-name{{font-weight:800;font-size:17px;text-align:center;margin-bottom:4px}}
.cta-box .cta-brand{{text-align:center;font-size:12px;color:var(--ink-dim);margin-bottom:14px}}
.cta-box .cta-avail{{text-align:center;font-size:12.5px;color:#a04434;font-weight:600;margin-bottom:14px;line-height:1.5}}
.cta-box .btn{{width:100%;justify-content:center;margin-bottom:10px}}
.cta-box .cta-note{{font-size:11px;color:var(--ink-dim);text-align:center;line-height:1.5}}
.faq-list{{margin:8px 0}}
.faq-item{{border-bottom:1px solid var(--line);padding:16px 0}}
.faq-item:last-child{{border-bottom:none}}
.faq-q{{font-size:16px;font-weight:700;margin-bottom:8px}}
.faq-a{{font-size:14px;color:var(--ink-soft);line-height:1.6}}
.divider{{border:none;border-top:1px solid var(--line);margin:32px 0}}
.related-card{{display:flex;align-items:center;gap:12px;border:1px solid var(--line);border-radius:var(--radius-lg);padding:14px 16px;background:var(--surface);transition:box-shadow .15s,border-color .15s}}
.related-card:hover{{box-shadow:var(--shadow-md);border-color:var(--blue-dim)}}
.rc-icon{{font-size:24px}}.rc-name{{font-weight:700;font-size:14px}}.rc-price{{font-size:12px;color:var(--ink-dim)}}
.rc-arrow{{margin-left:auto;color:var(--ink-dim);font-size:20px}}
@media(max-width:920px){{.review-grid{{grid-template-columns:1fr}}.sticky-cta{{position:static}}}}
  </style>
{schemas}
</head>
<body>
<header class="site-header" id="site-header" data-active="/produkte/"></header>
<main>
  <section class="page-hero">
    <div class="container">
      <nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span class="sep" aria-hidden="true">›</span><a href="/controller/">Controller</a><span class="sep" aria-hidden="true">›</span><span class="cur">{esc(full_name)}</span></nav>
      <span class="eyebrow">📋 Datenblatt · {esc(item['brand'])} · Altmodell</span>
      <h1>{esc(full_name)}</h1>
      <p class="lead">{esc(item['claim'])}</p>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="review-grid">
        <div class="review-body">

          <h2>Kurz-Einschätzung</h2>
          <div class="verdict-box">
            <div class="vb-label">⭐ Unsere Einordnung</div>
            <div class="vb-text">{esc(item['verdict'])}</div>
          </div>

          <div class="avail-box"><strong>Verfügbarkeit</strong>{esc(item['availability'])}</div>

          {paras}

          <h2>Technische Eckdaten</h2>
          <table class="specs-table" aria-label="Technische Eckdaten {esc(full_name)}">
            {specs_rows}
          </table>
          <p style="font-size:12.5px;color:var(--ink-dim)">Angaben laut Hersteller bzw. Archiv-Datenblatt; wir haben dieses Altmodell nicht selbst im aktuellen Test.</p>

          <h2>Alternativen im Sortiment</h2>
          <p>Diese aktuell kaufbaren Modelle decken denselben Einsatzzweck ab, mit laufendem Hersteller-Support:</p>
          <div class="grid-auto" style="grid-template-columns:repeat(auto-fill,minmax(220px,1fr))">
            {alt_cards}
          </div>

          <hr class="divider">
          <h2>Häufige Fragen</h2>
          <div class="faq-list">{faq_html}</div>
        </div>

        <aside class="sticky-cta" aria-label="Verfügbarkeit und Alternativen">
          <div class="cta-box">
            <div class="cta-name">{esc(full_name)}</div>
            <div class="cta-brand">{esc(item['brand'])} · Altmodell</div>
            <div class="cta-avail">Nicht mehr regulär erhältlich — wir verlinken deshalb keinen Kauf-Button.</div>
            <a class="btn btn-primary" href="{detail_url(top_alt)}">Beste Alternative: {esc(top_alt['name'])} →</a>
            <a class="btn btn-secondary" href="/controller-finder/">Controller finden →</a>
            <p class="cta-note">Alternative führt zu unserem Test bzw. Kurzcheck mit aktuellem Preis.</p>
          </div>
        </aside>
      </div>
    </div>
  </section>
</main>
<footer class="site-footer" id="site-footer"></footer>
<script src="/assets/js/main.js"></script>
</body></html>'''

created = []
for item in longtail:
    d = f"{ROOT}/produkte/{item['slug']}"
    os.makedirs(d, exist_ok=True)
    page = build(item)
    open(f'{d}/index.html', 'w', encoding='utf-8').write(page)
    # Gate: Schema-FAQ == sichtbarer Text, >=2 interne Links auf kaufbare Produkte
    import re as _re
    text = _re.sub(r'<[^>]+>', '', page)
    for q, a in item['faqs']:
        assert q in text and a in text, f"{item['slug']}: FAQ nicht sichtbar"
    buyable = set(_re.findall(r'href="(/(?:produkte|controller)/[a-z0-9-]+[^"]*?)"', page))
    buyable = {b for b in buyable if any(detail_url(p) == b for p in products)}
    assert len(buyable) >= 2, f"{item['slug']}: nur {len(buyable)} kaufbare Links"
    created.append(item['slug'])

print(f"✓ {len(created)} Longtail-Seiten erzeugt:")
for s in created: print('  /produkte/' + s + '/')
