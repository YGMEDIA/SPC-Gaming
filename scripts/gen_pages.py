# -*- coding: utf-8 -*-
"""Erzeugt /produkte/<slug>/index.html für alle Produkte ohne Review-Seite."""
import json, os, re, html, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_content import CONTENT

import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = 'https://smartphone-controller.com'

items = json.load(open(f'{ROOT}/assets/data/products.json'))
by_slug = {i['slug']: i for i in items}

TYPE_CRUMB = {'controller': ('Controller', '/controller/'), 'zubehoer': ('Zubehör', '/zubehoer/')}
PLATFORM_HUB = {
    'ios': ('/controller/ios/', 'iPhone Controller'),
    'android': ('/controller/android/', 'Android Controller'),
    'universal': ('/controller/universal/', 'Universal Controller'),
    'tablet': ('/controller/tablet/', 'Tablet Controller'),
    'mini': ('/controller/mini-gamepad/', 'Mini-Gamepads'),
    'finger-sleeves': ('/zubehoer/finger-sleeves/', 'Finger Sleeves'),
    'trigger': ('/zubehoer/trigger/', 'Trigger & Auslöser'),
    'kuehler': ('/zubehoer/handy-kuehler/', 'Handy-Kühler'),
}

def esc(s): return html.escape(str(s), quote=True)

def parse_rating(specs):
    for k, v in specs or []:
        if k == 'Bew.':
            m = re.match(r'([\d,]+)\s*\(([\d.+]+)\)', v)
            if m:
                val = m.group(1).replace(',', '.')
                cnt = m.group(2).replace('.', '').replace('+', '')
                return val, cnt, v
    return None, None, None

def price_num(p):
    m = re.search(r'(\d+)', (p or '').replace('.', ''))
    return m.group(1) if m else None

def related(prod):
    """3 verwandte Produkte: gleiche Plattform bevorzugt, dann gleicher Typ."""
    pool = [x for x in items if x['slug'] != prod['slug'] and x['platform'] == prod['platform']]
    pool += [x for x in items if x['slug'] != prod['slug'] and x['type'] == prod['type'] and x not in pool]
    return pool[:3]

def detail_url(p):
    return p['detail'] if p['detail'] else f"/produkte/{p['slug']}/"

ALT_PLATFORM = {'Universal': 'für Android & iPhone', 'Android': 'für Android', 'iPhone': 'fürs iPhone',
                'Tablet': 'für Tablet & Smartphone', 'Mini-Gamepad': 'für unterwegs'}

def alt_text(prod, full_name):
    """Beschreibender, keyword-relevanter Alt-Text: Produktname + Merkmal + Kontext (§ Block A4)."""
    if prod['type'] == 'controller':
        suffix = ALT_PLATFORM.get(prod.get('platformLabel', ''), 'für Smartphones')
        if 'controller' in full_name.lower():
            return f"{full_name} {suffix}"
        return f"{full_name}, Smartphone-Controller {suffix}"
    pl = prod.get('platformLabel', '')
    if pl and pl.lower() not in full_name.lower():
        return f"{full_name}, {pl} für Mobile Gaming"
    return f"{full_name}, Gaming-Zubehör für Smartphones"

def build(prod, c):
    slug = prod['slug']
    url = f"{DOMAIN}/produkte/{slug}/"
    full_name = prod['name'] if prod['brand'].lower() in prod['name'].lower() else f"{prod['brand']} {prod['name']}"
    rating_val, rating_cnt, rating_raw = parse_rating(prod.get('specs'))
    p_num = price_num(prod.get('price'))
    typ_label, typ_url = TYPE_CRUMB[prod['type']]
    hub_url, hub_label = PLATFORM_HUB.get(prod['platform'], (typ_url, typ_label))
    img = prod.get('img') or f"{DOMAIN}/assets/img/og-default.jpg"
    if img.startswith('/'): img = DOMAIN + img
    gallery = [u for u in (prod.get('gallery') or []) if u and u != img]
    video = prod.get('video') or None

    title = f"{full_name} — Kurzcheck & Preis | smartphone-controller.com"
    if len(title) > 68:
        title = f"{full_name} — Kurzcheck & Preis"
    desc = c['verdict'][:158].rsplit(' ', 1)[0] + ' …' if len(c['verdict']) > 158 else c['verdict']

    # --- Product Schema (Rating nur wenn sichtbar auf der Seite) ---
    schema_prod = {
        "@context": "https://schema.org", "@type": "Product",
        "name": full_name,
        "image": [img] + gallery if gallery else img,
        "description": c['verdict'],
        "brand": {"@type": "Brand", "name": prod['brand']},
        "url": url,
    }
    if p_num:
        schema_prod["offers"] = {"@type": "Offer", "price": p_num, "priceCurrency": "EUR",
                                 "availability": "https://schema.org/InStock",
                                 "url": f"https://www.amazon.de/dp/{prod['asin']}?tag=ygmedia-21"}
    if rating_val and rating_cnt and int(rating_cnt) > 1:
        schema_prod["aggregateRating"] = {"@type": "AggregateRating", "ratingValue": rating_val,
                                          "bestRating": "5", "reviewCount": rating_cnt}
    schema_bc = {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": 1, "name": "Home", "item": DOMAIN + "/"},
        {"@type": "ListItem", "position": 2, "name": typ_label, "item": DOMAIN + typ_url},
        {"@type": "ListItem", "position": 3, "name": full_name, "item": url},
    ]}
    schema_faq = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for q, a in c['faqs']]} if c.get('faqs') else None

    schemas = '\n'.join(
        f'<script type="application/ld+json">\n{json.dumps(s, ensure_ascii=False, indent=1)}\n</script>'
        for s in [schema_prod, schema_bc] + ([schema_faq] if schema_faq else []))

    specs_rows = f'<tr><td>Preis</td><td>{esc(prod["price"] or "siehe Amazon")}</td></tr>\n'
    for k, v in prod.get('specs') or []:
        label = {'Verb.': 'Verbindung', 'Bew.': 'Amazon-Bewertung'}.get(k, k)
        val = f'{v.split("(")[0].strip()} / 5 ({v.split("(")[1].rstrip(")")} Bewertungen)' if k == 'Bew.' and '(' in v else v
        specs_rows += f'<tr><td>{esc(label)}</td><td>{val}</td></tr>\n'
    specs_rows += f'<tr><td>Kategorie</td><td><a href="{hub_url}">{esc(hub_label)}</a></td></tr>'

    pros = '\n'.join(f'<li class="pro-item">✓ {esc(x)}</li>' for x in c['pros'])
    cons = '\n'.join(f'<li class="con-item">✗ {esc(x)}</li>' for x in c['cons'])
    paras = '\n'.join(f'<p>{esc(x)}</p>' for x in c['desc'])
    faq_html = '\n'.join(
        f'<div class="faq-item"><h3 class="faq-q">{esc(q)}</h3><p class="faq-a">{esc(a)}</p></div>'
        for q, a in c.get('faqs', []))
    faq_section = f'<hr class="divider">\n<h2>Häufige Fragen</h2>\n<div class="faq-list">{faq_html}</div>' if faq_html else ''

    gallery_section = ''
    if gallery:
        figs = '\n'.join(
            f'<figure class="gallery-item"><img src="{esc(u)}" alt="{esc(full_name)}, Produktansicht {i + 2}" '
            f'loading="lazy" onerror="this.closest(\'figure\').remove()"></figure>'
            for i, u in enumerate(gallery))
        gallery_section = f'<h2>Produktbilder</h2>\n<div class="gallery-grid">\n{figs}\n</div>'

    # Produktvideo nur bei belegtem video-Feld (Amazon-ImageBlock-Extraktion, §A5);
    # preload="none": ohne Klick lädt nur das Poster, Seite bleibt voll statisch (§A2).
    video_section = ''
    if video:
        video_section = (
            f'<h2>Produktvideo</h2>\n'
            f'<figure class="video-wrap"><video controls preload="none" poster="{esc(video["poster"])}" '
            f'src="{esc(video["url"])}" title="Produktvideo: {esc(full_name)}"></video>'
            f'<figcaption class="video-note">Video von der Amazon-Produktseite · Länge {esc(video["duration"])} Min.</figcaption></figure>'
        )

    rel_cards = ''
    for r in related(prod):
        rel_cards += (f'<a href="{detail_url(r)}" class="related-card"><span class="rc-icon">🎮</span>'
                      f'<div><div class="rc-name">{esc(r["brand"])} {esc(r["name"])}</div>'
                      f'<div class="rc-price">{esc(r["price"] or "Preis auf Amazon")}</div></div>'
                      f'<span class="rc-arrow">›</span></a>')

    rating_badge = ''
    if rating_val:
        stars = '★' * round(float(rating_val)) + '☆' * (5 - round(float(rating_val)))
        rating_badge = (f'<div class="rating-badge"><div><div class="rb-num">{rating_val.replace(".", ",")}</div>'
                        f'<div class="rb-label">/ 5</div></div><div><div class="stars" aria-label="{rating_val} von 5 Sternen">{stars}</div>'
                        f'<div style="font-size:11px;color:var(--ink-dim)">Amazon ({rating_cnt} Bew.)</div></div></div>')

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
  <meta property="og:title" content="{esc(full_name)} — Kurzcheck & Preis">
  <meta property="og:description" content="{esc(desc)}">
  <meta property="og:url" content="{url}">
  <meta property="og:site_name" content="smartphone-controller.com">
  <meta property="og:locale" content="de_DE">
  <meta property="og:image" content="{esc(img)}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(full_name)} — Kurzcheck & Preis">
  <meta name="twitter:description" content="{esc(desc)}">
  <meta name="twitter:image" content="{esc(img)}">
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
.pros-cons-grid{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:16px 0}}
.pros-box,.cons-box{{border-radius:var(--radius-lg);padding:18px 20px;border:1px solid var(--line)}}
.pros-box{{background:#f2faf4}}.cons-box{{background:#fbf4f2}}
.pros-box h3,.cons-box h3{{font-size:14px;font-weight:800;margin-bottom:10px}}
.pro-item,.con-item{{font-size:14px;line-height:1.55;padding:4px 0;list-style:none}}
.pro-item{{color:#1d7a3a}}.con-item{{color:#a04434}}
.sticky-cta{{position:sticky;top:184px}}
.cta-box{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius-lg);padding:20px;box-shadow:var(--shadow-md)}}
.cta-box .cta-name{{font-weight:800;font-size:17px;text-align:center;margin-bottom:4px}}
.cta-box .cta-brand{{text-align:center;font-size:12px;color:var(--ink-dim);margin-bottom:14px}}
.cta-box .cta-price{{font-size:26px;font-weight:800;text-align:center;color:var(--ink);margin-bottom:4px}}
.cta-box .cta-available{{text-align:center;font-size:12px;color:#1d7a3a;font-weight:600;margin-bottom:14px}}
.cta-box .btn{{width:100%;justify-content:center;margin-bottom:10px}}
.cta-box .cta-note{{font-size:11px;color:var(--ink-dim);text-align:center;line-height:1.5}}
.cta-photo{{display:block;width:100%;max-height:260px;object-fit:contain;border-radius:var(--radius);margin-bottom:14px;background:#fff}}
.rating-badge{{display:flex;align-items:center;gap:12px;border-top:1px solid var(--line);margin-top:14px;padding-top:14px}}
.rb-num{{font-size:26px;font-weight:800;line-height:1}}
.rb-label{{font-size:11px;color:var(--ink-dim)}}
.stars{{color:#f5a623;font-size:15px;letter-spacing:2px}}
.faq-list{{margin:8px 0}}
.faq-item{{border-bottom:1px solid var(--line);padding:16px 0}}
.faq-item:last-child{{border-bottom:none}}
.faq-q{{font-size:16px;font-weight:700;margin-bottom:8px}}
.faq-a{{font-size:14px;color:var(--ink-soft);line-height:1.6}}
.gallery-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px;margin:16px 0}}
.gallery-item{{margin:0;border:1px solid var(--line);border-radius:var(--radius-lg);background:#fff;padding:12px}}
.gallery-item img{{width:100%;height:230px;object-fit:contain;display:block}}
.video-wrap{{margin:16px 0;border:1px solid var(--line);border-radius:var(--radius-lg);background:#fff;padding:12px}}
.video-wrap video{{width:100%;max-height:480px;display:block;border-radius:var(--radius);background:#000}}
.video-note{{font-size:12px;color:var(--ink-dim);margin-top:8px;text-align:center}}
.divider{{border:none;border-top:1px solid var(--line);margin:32px 0}}
.related-card{{display:flex;align-items:center;gap:12px;border:1px solid var(--line);border-radius:var(--radius-lg);padding:14px 16px;background:var(--surface);transition:box-shadow .15s,border-color .15s}}
.related-card:hover{{box-shadow:var(--shadow-md);border-color:var(--blue-dim)}}
.rc-icon{{font-size:24px}}.rc-name{{font-weight:700;font-size:14px}}.rc-price{{font-size:12px;color:var(--ink-dim)}}
.rc-arrow{{margin-left:auto;color:var(--ink-dim);font-size:20px}}
@media(max-width:920px){{.review-grid{{grid-template-columns:1fr}}.sticky-cta{{position:static}}.pros-cons-grid{{grid-template-columns:1fr}}}}
  </style>
{schemas}
</head>
<body>
<header class="site-header" id="site-header" data-active="/produkte/"></header>
<main>
  <section class="page-hero">
    <div class="container">
      <nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span class="sep" aria-hidden="true">›</span><a href="{typ_url}">{typ_label}</a><span class="sep" aria-hidden="true">›</span><span class="cur">{esc(prod['name'])}</span></nav>
      <span class="eyebrow">📋 Produkt-Check · {esc(prod['brand'])}</span>
      <h1>{esc(full_name)}</h1>
      <p class="lead">{esc(prod['claim']).replace('&amp;nbsp;', ' ').replace('&amp;amp;', '&amp;')}</p>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="review-grid">
        <div class="review-body">

          <h2>Kurz-Einschätzung</h2>
          <div class="verdict-box">
            <div class="vb-label">⭐ Unsere Einordnung</div>
            <div class="vb-text">{esc(c['verdict'])}</div>
          </div>

          {paras}

          <h2>Technische Daten</h2>
          <table class="specs-table" aria-label="Technische Daten {esc(full_name)}">
            {specs_rows}
          </table>

          {gallery_section}

          {video_section}

          <h2>Stärken & Schwächen</h2>
          <div class="pros-cons-grid">
            <div class="pros-box"><h3>Stärken</h3><ul>{pros}</ul></div>
            <div class="cons-box"><h3>Schwächen</h3><ul>{cons}</ul></div>
          </div>

          {faq_section}

          <hr class="divider">
          <h2>Das könnte dich auch interessieren</h2>
          <div class="grid-auto" style="grid-template-columns:repeat(auto-fill,minmax(220px,1fr))">
            {rel_cards}
          </div>
        </div>

        <aside class="sticky-cta" aria-label="Preis und Kauf">
          <div class="cta-box" data-product="{esc(slug)}">
            <img class="cta-photo" src="{esc(img)}" alt="{esc(alt_text(prod, full_name))}" loading="lazy" onerror="this.remove()">
            <div class="cta-name">{esc(full_name)}</div>
            <div class="cta-brand">{esc(prod['brand'])}</div>
            <div class="cta-price">{esc(prod['price'] or 'Preis auf Amazon')}</div>
            <div class="cta-available">✓ Auf Amazon verfügbar</div>
            <a class="btn btn-primary" data-asin="{esc(prod['asin'])}" data-product="{esc(slug)}" href="#">Kaufen →</a>
            <a class="btn btn-secondary" href="/produkte/">← Alle Produkte</a>
            <p class="cta-note">Affiliate-Link · Preis auf Amazon.de prüfen · keine Zusatzkosten für dich</p>
            {rating_badge}
          </div>
        </aside>
      </div>
    </div>
  </section>
</main>
<footer class="site-footer" id="site-footer"></footer>
<script src="/assets/js/main.js"></script>
</body></html>'''

# ---- Erzeugen ----
# Normalmodus: nur Produkte OHNE detail (Erstanlage).
# --regen [slug ...]: bestehende /produkte/-Seiten neu bauen (alle oder nur die genannten);
# Review-Seiten (detail außerhalb /produkte/) werden NIE angefasst.
import sys
regen = '--regen' in sys.argv
regen_slugs = {a for a in sys.argv[1:] if not a.startswith('-')}
created = []
for prod in items:
    if regen:
        if not (prod.get('detail') or '').startswith('/produkte/'):
            continue
        if regen_slugs and prod['slug'] not in regen_slugs:
            continue
    elif prod['detail']:
        continue
    c = CONTENT.get(prod['slug'])
    if not c:
        print('FEHLT IM CONTENT-DICT:', prod['slug']); continue
    d = f"{ROOT}/produkte/{prod['slug']}"
    os.makedirs(d, exist_ok=True)
    open(f'{d}/index.html', 'w', encoding='utf-8').write(build(prod, c))
    prod['detail'] = f"/produkte/{prod['slug']}/"
    created.append(prod['slug'])

json.dump(items, open(f'{ROOT}/assets/data/products.json', 'w'), ensure_ascii=False, indent=2)
mode = 'regeneriert' if regen else 'erzeugt'
print(f"✓ {len(created)} Detailseiten {mode}:")
for s in created: print('  /produkte/' + s + '/')
