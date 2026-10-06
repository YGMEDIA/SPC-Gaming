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


def voller_name(p):
    """Marke + Name, ohne die Marke zu verdoppeln.

    Drei Backbone-Produkte tragen "Backbone" bereits im name-Feld; die bedingungslose
    Verkettung ergab "Backbone Backbone Pro" im sichtbaren Text von acht Seiten.
    """
    return p['name'] if p['brand'].lower() in p['name'].lower() else f"{p['brand']} {p['name']}"

def _sterne(wert, skala=5):
    """Sterne-Glyphen, die zur genannten Skala passen.

    Die alte Zeile war `'★' * round(wert) + '☆' * (5 - round(wert))` und galt still als
    Fuenfer-Skala. Auf den vier handgepflegten Review-Seiten steht daneben ein
    Redaktions-Score auf ZEHNER-Skala, und dort stand fuenfmal ★ -- fuer 8,5 von 10. Fuer
    den Leser heisst fuenf von fuenf "perfekt". Die Glyphen werden deshalb aus dem
    Verhaeltnis gerechnet, nie aus dem Rohwert.
    """
    voll = max(0, min(5, round(wert / skala * 5)))
    return '★' * voll + '☆' * (5 - voll)


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

def rating_of(p):
    """Bewertung als float, oder None. Nur für Vergleiche innerhalb dieses Generators."""
    v, c, _ = parse_rating(p.get('specs'))
    return (float(v), int(c)) if v and c else (None, None)

A6_SCHWELLE = 3.8

from kompat import kompat_html   # Massnahme B1, eine Quelle fuer Generator und Sync
# Massnahme B7: derselbe Aufbau. Die Zuordnung Produkt -> Uebersicht wird aus dem
# Linkgraph GELESEN, nicht gepflegt; `taxonomie_karte()` laeuft einmal pro Lauf.
from hublinks import taxonomie_karte, hublinks_html, block as hub_block
# Massnahme B10: dieselbe Aufteilung wie bei B1 -- eine Regel, zwei Wege. Der Block steht
# VOR dem Kurz-Urteil, an derselben Stelle wie der Kompatibilitaets-Block, weil wer erst
# danach erfaehrt, dass es ein besseres Angebot gibt, die Entscheidung schon getroffen hat.
# Die erste Fassung setzte ihn hinter Urteil und Absaetze: Auf vier von sechs Seiten stand
# er damit richtig (die pflegt sync_guenstiger.py), auf zwei falsch -- und die Begruendung
# stand drei Mal in der Doku, ohne dass sie fuer ein Drittel der Faelle galt.
from guenstiger import html as guenstiger_html, block as guenstiger_block
# Massnahme B12: Die Lesezeit kommt aus derselben Regel, die sync_lesezeit.py
# nachzieht und verify.py prueft. Zweistufig gebaut (siehe `build_fertig`), weil
# der Text erst steht, wenn die Seite gebaut ist.
from lesezeit import minuten as lesezeit_minuten
from produktdaten import STOCK_SCHEMA, STOCK_CTA, stock   # §A5, eine Quelle fuer Karte, Schema und Kaufleiste
from datenstand import MONAT as DATENSTAND_MONAT   # §A5, eine Quelle fuers ganze Repo


def a6_warnbox(prod):
    """§A6: Produkte unter 3,8 Sternen bekommen eine sichtbare Warnung statt Kaufempfehlung.

    Der Kasten wird aus products.json gerechnet, nicht getextet: Wenn eine Bewertung die
    Schwelle überschreitet, verschwindet er von selbst, und wenn eine kippt, erscheint er.
    Handgepflegte Warnkästen sind genau daran gescheitert (MGPXPRO trug 'keine
    Kaufempfehlung' weiter, als er längst bei 4,3 stand).

    Die Alternative kommt aus derselben Unterkategorie (platform), bestbewertet zuerst,
    und muss selbst mindestens 4,0 tragen. Findet sich keine, nennt der Kasten keine.
    """
    r, c = rating_of(prod)
    if r is None or r >= A6_SCHWELLE:
        return ''
    pool = [(rating_of(x), x) for x in items
            if x['slug'] != prod['slug'] and x['platform'] == prod['platform']]
    besser = sorted(((rc[0], rc[1], x) for rc, x in pool if rc[0] and rc[0] >= 4.0),
                    key=lambda t: (-t[0], -t[1]))
    alt = ''
    if besser:
        br, _, bx = besser[0]
        bname = bx['name'] if bx['brand'].lower() in bx['name'].lower() else f"{bx['brand']} {bx['name']}"
        # Ohne Artikel formuliert: Produktnamen sind teils Plural ("Finger Sleeves") und
        # tragen selbst Klammern, "Der X (4,2 Sterne)" wird damit falsch und doppelt geklammert.
        alt = (f' Besser bewertet in derselben Kategorie: <a href="{detail_url(bx)}">{esc(bname)}</a> '
               f'mit {str(br).replace(".", ",")} Sternen.')
    return (f'<div class="note note-warn"><strong>Eingeschränkte Empfehlung:</strong> Mit '
            f'<strong>{str(r).replace(".", ",")} von 5 Sternen aus {c} Bewertungen</strong> liegt '
            f'dieses Produkt unter unserer Empfehlungsschwelle von '
            f'{str(A6_SCHWELLE).replace(".", ",")}.{alt}</div>')

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

_TAXONOMIE_KARTE = None


def _karte():
    """Die Zuordnung Produkt -> Uebersichten, einmal je Lauf.

    `taxonomie_karte()` liest alle Seiten; bei 29 Produktseiten waere das 29 Mal
    derselbe Durchgang. Gecacht, weil sich der Linkgraph waehrend eines Laufs nicht
    aendert: Dieser Generator schreibt nur Produktseiten, und die sind keine
    Taxonomie-Seiten.
    """
    global _TAXONOMIE_KARTE
    if _TAXONOMIE_KARTE is None:
        _TAXONOMIE_KARTE = taxonomie_karte()[0]   # [1] sind die Hubs ohne h1, die meldet
    return _TAXONOMIE_KARTE                       # sync_hublinks.py


def build(prod, c, lesezeit):
    # Kein Default: Ein Aufrufer, der die Lesezeit vergisst, soll einen TypeError
    # bekommen und keine Seite mit "None Min. Lesezeit" schreiben.
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
        # NUR das Hauptbild. Google liest Product.image als DAS Produktbild; in den
        # Amazon-Galerien liegen nachweislich A+-Werbebanner mit eingebrannter
        # Herstellerwerbung (Razer 3/3, ASUS 3/3, dazu GameSir und Backbone). Welche der
        # 116 Galeriebilder Banner sind, klaert nur Ansehen. Das Hauptbild ist die einzige
        # Klasse, die garantiert werbefrei ist: Amazon schreibt dafuer weissen Hintergrund
        # ohne Text vor. Sichtbar bleiben die Galerien, sie sind als Katalogbilder
        # ausgewiesen -- in den strukturierten Daten haben Werbebanner nichts zu suchen.
        "image": img,
        "description": c['verdict'],
        "brand": {"@type": "Brand", "name": prod['brand']},
        "url": url,
    }
    if p_num:
        schema_prod["offers"] = {"@type": "Offer", "price": p_num, "priceCurrency": "EUR",
                                 "availability": STOCK_SCHEMA[stock(prod)],
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
        # Wert escapen wie das Label daneben: ohne esc() stand "Tablet/iPad <10mm" roh
        # im Markup, waehrend dieselbe Angabe auf den Karten korrekt "&lt;10mm" trug.
        specs_rows += f'<tr><td>{esc(label)}</td><td>{esc(val)}</td></tr>\n'
    specs_rows += f'<tr><td>Kategorie</td><td><a href="{hub_url}">{esc(hub_label)}</a></td></tr>'

    pros = '\n'.join(f'<li class="pro-item">✓ {esc(x)}</li>' for x in c['pros'])
    cons = '\n'.join(f'<li class="con-item">✗ {esc(x)}</li>' for x in c['cons'])
    paras = '\n'.join(f'<p>{esc(x)}</p>' for x in c['desc'])
    faq_html = '\n'.join(
        f'<div class="faq-item"><h3 class="faq-q">{esc(q)}</h3><p class="faq-a">{esc(a)}</p></div>'
        for q, a in c.get('faqs', []))
    hub_links = hub_block(hublinks_html(prod.get('detail'), _karte(), esc))
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
                      f'<div><div class="rc-name">{esc(voller_name(r))}</div>'
                      f'<div class="rc-price">{esc(r["price"] or "Preis auf Amazon")}</div></div>'
                      f'<span class="rc-arrow">›</span></a>')

    # cta_link=(url, label) im CONTENT-Dict: zusätzlicher Button in der Kaufleiste,
    # z. B. zur passenden Vergleichsseite. Ohne das Feld bleibt die Leiste unverändert.
    cta_extra = ''
    if c.get('cta_link'):
        _u, _l = c['cta_link']
        cta_extra = f'<a class="btn btn-secondary" href="{esc(_u)}">{esc(_l)}</a>'

    # Massnahme B8 (Cialdini): Sternzahl UND Bewertungszahl sind zwei Signale, nicht eins.
    # Gemessen am 04.10.2026 stand der Wert in 26px/800 und die Anzahl in 11px im
    # SCHWAECHSTEN Farbton des Systems (--ink-dim) -- Faktor 2,4 in der Groesse und der
    # blasseste Ton, den es gibt. "4,8 Sterne" aus 12 Bewertungen und "4,4 Sterne" aus
    # 3.147 sind sehr verschiedene Aussagen; wer die Anzahl zur Fussnote macht, zeigt nur
    # Anzahl bekommt deshalb eine eigene Klasse `.rb-count` mit 13px statt 11px und
    # --ink-soft statt --ink-dim, und sie wird ausgeschrieben ("566 Bewertungen",
    # nicht "(566 Bew.)").
    rating_badge = ''
    if rating_val:
        stars = _sterne(float(rating_val))
        _cnt_de = f'{int(rating_cnt):,}'.replace(',', '.') if rating_cnt else ''
        # Singular: "1 Bewertungen" waere ein neuer Grammatikfehler. Heute ist die
        # kleinste Anzahl 16, aber eine Regel, die bei 1 falsch wird, ist falsch.
        _bew_wort = 'Bewertung' if str(rating_cnt) == '1' else 'Bewertungen'
        rating_badge = (
            f'<div class="rating-badge">'
            f'<div><div class="rb-num">{rating_val.replace(".", ",")}</div>'
            f'<div class="rb-label">von 5</div></div>'
            f'<div><div class="stars" aria-label="{rating_val.replace(chr(46), chr(44))} von 5 Sternen">{stars}</div>'
            f'<div class="rb-count">{_cnt_de} {_bew_wort} bei Amazon</div></div></div>')

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
  <link rel="stylesheet" href="/assets/css/style.css?v=43e618fc">
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
.note-warn{{background:var(--red-bg);border-left:4px solid var(--red);padding:16px 18px;border-radius:var(--radius);margin:22px 0;font-size:14px;line-height:1.6}}
.note-info{{background:var(--blue-bg);border-left:4px solid var(--blue);padding:16px 18px;border-radius:var(--radius);margin:22px 0;font-size:14px;line-height:1.6}}
.note-info a{{color:var(--blue);font-weight:600}}
.sticky-cta{{position:sticky;top:184px}}
.cta-box{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius-lg);padding:20px;box-shadow:var(--shadow-md)}}
.cta-box .cta-name{{font-weight:800;font-size:17px;text-align:center;margin-bottom:4px}}
.cta-box .cta-brand{{text-align:center;font-size:12px;color:var(--ink-dim);margin-bottom:14px}}
.cta-box .cta-price{{font-size:26px;font-weight:800;text-align:center;color:var(--ink);margin-bottom:4px}}
.cta-box .cta-available{{text-align:center;font-size:12px;color:#1d7a3a;font-weight:600;margin-bottom:14px}}
.cta-box .cta-available.nein,.cta-box .cta-available.gebraucht,.cta-box .cta-available.drittanbieter{{color:var(--ink-dim)}}
.cta-box .btn{{width:100%;justify-content:center;margin-bottom:10px}}
.cta-box .cta-note{{font-size:11px;color:var(--ink-dim);text-align:center;line-height:1.5}}
.cta-photo{{display:block;width:100%;max-height:260px;object-fit:contain;border-radius:var(--radius);margin-bottom:14px;background:#fff}}
.rating-badge{{display:flex;align-items:center;gap:12px;border-top:1px solid var(--line);margin-top:14px;padding-top:14px}}
.rb-num{{font-size:26px;font-weight:800;line-height:1}}
.rb-label{{font-size:11px;color:var(--ink-dim)}}
.rb-count{{font-size:13px;color:var(--ink-soft);line-height:1.4;margin-top:2px}}
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
<header class="site-header" id="site-header" data-active="/produkte/">
<div class="trust-strip"><div class="container">
<span class="ts">Unabhängig &amp; herstellerneutral</span>
<span class="ts">42 Modelle im Sortiment</span>
<span class="ts">Datenstand Oktober 2026</span>
</div></div>
<div class="header-main">
<a href="/" class="logo" aria-label="smartphone-controller.com – Startseite"><span class="logo-text">smartphone-controller<span class="logo-tld">.com</span></span></a>
</div>
<nav class="main-nav" aria-label="Hauptnavigation"><div class="container">
<a href="/produkte/" class="nav-link">🛒 Alle Produkte</a>
<a href="/controller-finder/" class="nav-link">🎮 Controller-Finder</a>
<a href="/controller/ios/" class="nav-link">iPhone</a>
<a href="/controller/android/" class="nav-link">Android</a>
<a href="/controller/universal/" class="nav-link">Universal</a>
<a href="/zubehoer/finger-sleeves/" class="nav-link">Finger Sleeves</a>
<a href="/zubehoer/trigger/" class="nav-link">Trigger</a>
<a href="/vergleich/" class="nav-link">Vergleiche</a>
<a href="/blog/" class="nav-link">Blog</a>
<a href="/marken/gamesir/" class="nav-link">GameSir ★<span class="nav-badge">Top-Marke</span></a>
</div></nav>
</header>
<main>
  <section class="page-hero">
    <div class="container">
      <nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span class="sep" aria-hidden="true">›</span><a href="{typ_url}">{typ_label}</a><span class="sep" aria-hidden="true">›</span><span class="cur">{esc(prod['name'])}</span></nav>
      <span class="eyebrow">📋 Produkt-Check · {esc(prod['brand'])}</span>
      <h1>{esc(full_name)}</h1>
      <p class="lead">{esc(prod['claim']).replace('&amp;nbsp;', ' ').replace('&amp;amp;', '&amp;')}</p>
      <div class="article-byline">Kurzcheck ohne eigenen Test · {lesezeit} Min. Lesezeit</div>
    </div>
  </section>

  <section class="section">
    <div class="container">
      <div class="review-grid">
        <div class="review-body">

          {kompat_html(prod, esc)}

          {guenstiger_block(guenstiger_html(prod, items, esc))}

          <h2>Kurz-Einschätzung</h2>
          <div class="verdict-box">
            <div class="vb-label">⭐ Unsere Einordnung</div>
            <div class="vb-text">{esc(c['verdict'])}</div>
          </div>

          {paras}

          {a6_warnbox(prod)}

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

          {hub_links}

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
            <div class="cta-available {stock(prod) or 'nein'}">{STOCK_CTA[stock(prod)]}</div>
            <a class="btn btn-primary" data-asin="{esc(prod['asin'])}" data-product="{esc(slug)}" href="#">Kaufen →</a>
            {cta_extra}
            <a class="btn btn-secondary" href="/produkte/">← Alle Produkte</a>
            <p class="cta-note">Affiliate-Link · Preis auf Amazon.de prüfen · keine Zusatzkosten für dich</p>
            {rating_badge}
          </div>
        </aside>
      </div>
    </div>
  </section>
</main>
<footer class="site-footer" id="site-footer">
  <div class="container">
    <p class="foot-affiliate">Transparenz-Hinweis: Einige Links auf dieser Seite sind Affiliate-Links (Amazon PartnerNet). Kaufst du über einen solchen Link, erhalten wir eine kleine Provision — für dich ändert sich der Preis nicht. Das beeinflusst unsere Tests und Bewertungen nicht.</p>
    <p class="foot-legal"><a href="/impressum/">Impressum</a> · <a href="/datenschutz/">Datenschutz</a> · <a href="/affiliate-hinweis/">Affiliate</a> · <a href="/sitemap.xml">Sitemap</a> · © 2026 YG MEDIA</p>
  </div>
</footer>
<script src="/assets/js/main.js?v=74cdf24b"></script>
</body></html>'''

def build_fertig(prod, c):
    """Zweistufig: einmal bauen, um den Text zu zaehlen, dann mit der echten Lesezeit.

    Dieselbe Loesung wie in gen_preisfrage.py und aus demselben Grund: Eine getippte
    Lesezeit auf einer Seite, die sonst jede Zahl ableitet, waere die erste, die nicht
    mehr stimmt. Gezaehlt wird mit `lesezeit.minuten`, also mit genau der Regel, die
    sync_lesezeit.py nachzieht und verify.py prueft -- mit einer eigenen Formulierung
    wuerden Generator und Sync sich bei jedem Lauf gegenseitig ueberschreiben.
    """
    m = lesezeit_minuten(build(prod, c, lesezeit=1))
    if m is None:
        raise SystemExit(f"FEHLER: die gebaute Seite fuer {prod.get('slug')} hat kein "
                         f"<main>-Element, die Lesezeit laesst sich nicht bestimmen")
    return build(prod, c, lesezeit=m)


def generierte_seiten():
    """(slug, pfad, Soll-HTML) für jede Seite, die dieser Generator besitzt.

    verify.py nutzt das, um Datei gegen Generator zu vergleichen. Solange beide
    deckungsgleich sind, sind alle fünf Renderstellen des CONTENT-Texts abgedeckt
    (meta/og/twitter description, Schema-description, Einordnungs-Box, Fließtext,
    Stärken/Schwächen) und Handkorrekturen an der Datei können nicht mehr stumm
    verloren gehen.
    """
    for prod in items:
        if not (prod.get('detail') or '').startswith('/produkte/'):
            continue
        c = CONTENT.get(prod['slug'])
        if not c:
            continue
        yield prod['slug'], f"{ROOT}/produkte/{prod['slug']}/index.html", build_fertig(prod, c)


# ---- Erzeugen ----
# Normalmodus: nur Produkte OHNE detail (Erstanlage).
# --regen [slug ...]: bestehende /produkte/-Seiten neu bauen (alle oder nur die genannten);
# Review-Seiten (detail außerhalb /produkte/) werden NIE angefasst.
# Der Lauf steht unter __main__, damit verify.py build() importieren kann, ohne
# dabei Seiten zu schreiben und products.json neu zu serialisieren.
if __name__ == '__main__':
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
        open(f'{d}/index.html', 'w', encoding='utf-8').write(build_fertig(prod, c))
        prod['detail'] = f"/produkte/{prod['slug']}/"
        created.append(prod['slug'])

    with open(f'{ROOT}/assets/data/products.json', 'w', encoding='utf-8') as fh:
        json.dump(items, fh, ensure_ascii=False, indent=2)
        fh.write('\n')
    mode = 'regeneriert' if regen else 'erzeugt'
    print(f"✓ {len(created)} Detailseiten {mode}:")
    for s in created: print('  /produkte/' + s + '/')
