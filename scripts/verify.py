#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SPC Verify-Suite (P-7). Pflicht-Gate vor jedem "fertig". Exit 0 = grün, 1 = Befunde.
Prüft: Invarianten, products.json-Integrität, JSON-LD, interne Links, Sitemap, No-JS-Statik."""
import json, os, re, sys, glob
import xml.dom.minidom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
# §A6-Schwelle: Produkte darunter bekommen eine Warnung statt einer Kaufempfehlung.
# Steht hier einmal, weil sie an mehreren Stellen geprueft wird (Detailseiten,
# Footer-Text in main.js).
A6_SCHWELLE = 3.8
ERRORS, WARN = [], []
def err(msg): ERRORS.append(msg)
def warn(msg): WARN.append(msg)

sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from schema_util import typen_von as _typen_von   # eine Definition fuer beide Skripte

# ---------- 1 · Invarianten ----------
for f in ['CNAME', '.nojekyll', 'llms.txt', 'robots.txt', 'sitemap.xml', 'assets/data/products.json']:
    if not os.path.exists(f): err(f"Invariante fehlt: {f}")
if os.path.exists('CNAME') and open('CNAME').read().strip() != 'smartphone-controller.com':
    err("CNAME-Inhalt falsch")
# §B2 präzisiert (07.08.): /ratgeber/ darf NUR noindex-Redirect-Stubs enthalten
# (meta refresh + noindex, kein Content). Voll-Content dort = Zombie-Rückkehr = ROT.
if os.path.isdir('ratgeber'):
    for stub in glob.glob('ratgeber/**/index.html', recursive=True):
        s_html = open(stub, encoding='utf-8').read()
        ok_stub = ('noindex' in s_html and 'http-equiv="refresh"' in s_html
                   and len(s_html) < 1200 and '<main' not in s_html)
        if not ok_stub:
            err(f"ZOMBIE: {stub} ist kein Redirect-Stub (§B2) — Voll-Content unter /ratgeber/ verboten")

# §B2 (26.08.2026): Auch die am 08.07.2026 ausgelisteten Marken-Seiten dürfen NUR Redirect-Stubs
# sein (Produkte nicht mehr verfügbar, die Longtail-Datenblätter sind der Ersatz).
for _z in ('marken/ipega', 'marken/mocute'):
    _f = f'{_z}/index.html'
    if os.path.exists(_f):
        _h = open(_f, encoding='utf-8').read()
        if not ('noindex' in _h and 'http-equiv="refresh"' in _h and len(_h) < 1200 and '<main' not in _h):
            err(f"ZOMBIE: {_f} ist kein Redirect-Stub (§B2) — Marken-Voll-Content bleibt gelöscht")

pages = sorted(glob.glob('**/index.html', recursive=True))
pages = [p for p in pages if not p.startswith(('brain/', 'scripts/', '.github/'))]

# ---------- 2 · products.json ----------
try:
    items = json.load(open('assets/data/products.json', encoding='utf-8'))
    if len(items) < 40: warn(f"products.json: nur {len(items)} Produkte (erwartet ≥40)")
    slugs, asins, details = set(), set(), set()
    for i in items:
        for field in ['slug', 'asin', 'name', 'brand', 'type', 'platform', 'price', 'detail']:
            if not i.get(field): err(f"products.json {i.get('slug', i.get('asin','?'))}: Feld '{field}' leer (§A1)")
        if i['slug'] in slugs: err(f"Slug doppelt: {i['slug']}")
        if i['asin'] in asins: err(f"ASIN doppelt: {i['asin']}")
        # detail muss genauso eindeutig sein wie slug und asin: Es ist die EXTERNE
        # Identitaet, ueber die _externes_produkt() eine Seite ihrem Produkt zuordnet.
        # Ein doppelter detail-Pfad macht die Zuordnung mehrdeutig, und dann faellt
        # stillschweigend die komplette Bildpruefung der Seite aus (og:image,
        # twitter:image, cta-photo) samt der Pflicht, ein Product-Schema zu fuehren.
        # Der Lauf wurde zwar rot, aber ueber Kollateralschaden an Preisen — keine
        # einzige Meldung nannte die Ursache.
        if i['detail'] in details:
            err(f"detail doppelt: {i['detail']} (u.a. {i['slug']}) — die Zuordnung Seite "
                f"zu Produkt wird dadurch mehrdeutig und mehrere Gates fallen stumm aus")
        details.add(i['detail'])
        slugs.add(i['slug']); asins.add(i['asin'])
        if not re.match(r'^B0[A-Z0-9]{8}$', i['asin']): err(f"ASIN-Format ungültig: {i['asin']}")
        d = i['detail']
        if not os.path.exists(d.strip('/') + '/index.html'): err(f"detail-Ziel fehlt: {d} ({i['slug']})")
except Exception as e:
    err(f"products.json unlesbar: {e}"); items = []

# ---------- 3 · Seiten-Checks ----------
existing = {'/'} | {'/' + os.path.dirname(p) + '/' for p in pages}
existing |= {'/sitemap.xml', '/robots.txt', '/llms.txt'}
schema_count = 0
for p in pages:
    s = open(p, encoding='utf-8').read()
    if '\x02' in s: err(f"Steuerzeichen \\x02 in {p}")
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', s, re.S):
        schema_count += 1
        try:
            data = json.loads(m.group(1))
            blob = json.dumps(data)
            if '"aggregateRating"' in blob:
                if '"bestRating": "5"' not in blob and '"bestRating":"5"' not in blob:
                    err(f"Schema ohne bestRating 5 in {p} (§A4)")
                for rc in re.findall(r'"reviewCount":\s*"?(\d+)"?', blob):
                    if int(rc) <= 1: err(f"reviewCount ≤1 in {p} (§A4)")
            # §A4-Invariante (GSC WNC-10030322): jedes Product braucht offers, review
            # oder aggregateRating — sonst kritischer Produkt-Snippets-Fehler.
            def _prod_check(o):
                if isinstance(o, dict):
                    if 'Product' in _typen_von(o) and not any(k in o for k in ('offers', 'review', 'aggregateRating')):
                        err(f"Product-Schema ohne offers/review/aggregateRating in {p} (§A4/GSC)")
                    for v in o.values(): _prod_check(v)
                elif isinstance(o, list):
                    for x in o: _prod_check(x)
            _prod_check(data)
        except Exception as e:
            err(f"JSON-LD kaputt in {p}: {e}")
    for href in re.findall(r'href="(/[^"#?]*)"', s):
        h = href if href.endswith(('/', '.xml', '.txt', '.jpg', '.jpeg', '.png', '.webp', '.svg', '.css', '.js', '.ico')) else href + '/'
        if h.startswith('/assets/'):
            if not os.path.exists(h.lstrip('/')): err(f"Asset fehlt: {href} (in {p})")
        elif h not in existing:
            err(f"Interner Link kaputt: {href} (in {p}) (§B5)")
    # Amazon nie hart verlinkt (außer JS baut sie) — im statischen HTML nur data-asin
    if re.search(r'href="https?://(www\.)?amazon\.de/dp/', s):
        # erlaubt in Schema (offers.url) — prüfe nur echte <a href>
        for a in re.findall(r'<a [^>]*href="https?://(?:www\.)?amazon\.de[^"]*"[^>]*>', s):
            if 'data-asin' not in a: err(f"Harter Amazon-Link ohne data-asin-Automation in {p} (§A3)")

# ---------- 4 · Sitemap ----------
try:
    xml.dom.minidom.parse('sitemap.xml')
    sm = open('sitemap.xml', encoding='utf-8').read()
    locs = re.findall(r'<loc>([^<]+)</loc>', sm)
    if len(locs) != len(set(locs)): err("Sitemap: doppelte URLs")
    for u in locs:
        path = u.replace('https://smartphone-controller.com', '').strip()
        f = (path.strip('/') + '/index.html') if path not in ('', '/') else 'index.html'
        if not os.path.exists(f): err(f"Sitemap-URL ohne Datei: {u}")
        if '/ratgeber/' in u: err(f"Sitemap enthält ratgeber: {u}")
    # Rückrichtung: indexierbare Seiten in Sitemap?
    for p in pages:
        s = open(p, encoding='utf-8').read()
        if 'noindex' in s: continue
        url = 'https://smartphone-controller.com/' + ('' if p == 'index.html' else os.path.dirname(p) + '/')
        if url not in locs: warn(f"Indexierbare Seite fehlt in Sitemap: {url}")
except Exception as e:
    err(f"Sitemap: {e}")

# ---------- 5 · No-JS-Statik (§A2) ----------
for f, minimum in [('controller/ios/index.html', 20), ('controller/android/index.html', 20),
                   ('controller/universal/index.html', 20), ('produkte/index.html', 38)]:
    if os.path.exists(f):
        n = open(f, encoding='utf-8').read().count('class="pcard')
        if n < minimum: err(f"No-JS-Statik: {f} hat nur {n} statische Karten (min {minimum}) (§A2)")
    else:
        err(f"Hub fehlt: {f}")

# ---------- 6 · Marken-Hubs gegen products.json (§A1, 30.09.2026) ----------
# Die Erfahrungs- und Plattform-Sektionen der vier Marken-Hubs werden generiert und
# tragen Preise, Sterne und Bewertungszahlen im Fließtext. Ändert der preis-loop
# products.json, müssen die Hubs nachgezogen werden, sonst divergiert Geld-Content
# von der Produktwahrheit. Diese Invariante fängt genau das.
if os.path.exists('scripts/gen_brand_sections.py'):
    import subprocess
    _r = subprocess.run([sys.executable, 'scripts/gen_brand_sections.py', '--check'],
                        capture_output=True, text=True)
    if _r.returncode != 0:
        err(f"Marken-Hubs: gen_brand_sections.py --check schlägt fehl (§A1)\n"
            f"         {_r.stdout.strip().splitlines()[-1] if _r.stdout.strip() else _r.stderr.strip()[:200]}")
    elif 'wären geändert worden: keine' not in _r.stdout:
        _last = _r.stdout.strip().splitlines()[-1]
        err(f"Marken-Hubs sind nicht mehr deckungsgleich mit products.json (§A1). "
            f"Fix: python3 scripts/gen_brand_sections.py — {_last}")
else:
    err("scripts/gen_brand_sections.py fehlt — Marken-Hub-Invariante kann nicht prüfen")

# ---------- 6b · §A1-Vollaudit: HTML gegen products.json (30.09.2026) ----------
# Abschnitt 6 prüft nur die vier Marken-Hubs. Dieses Audit deckt das ab, was zwischen
# den Generator-Markern NICHT geprüft wird und wo am 30.09. elf Abweichungen lagen:
# jede Produktkarte auf allen Seiten (Preis und alle Spec-Chips), die Schema-Werte
# (offers/price, ratingValue, reviewCount) und die Hub-Zugehörigkeit gegen worksOn.
if os.path.exists('scripts/sync_product_values.py'):
    import subprocess
    _a = subprocess.run([sys.executable, 'scripts/sync_product_values.py', '--audit'],
                        capture_output=True, text=True)
    if _a.returncode != 0:
        for _zeile in _a.stdout.strip().splitlines():
            _z = _zeile.strip()
            if (_z and not _z.startswith('0 Abweichung') and 'Abweichung(en)' not in _z
                    and 'Fließtext-Hinweis' not in _z and not _z.startswith('?')):
                err(f"§A1-Audit: {_z}")
else:
    err("scripts/sync_product_values.py fehlt — §A1-Vollaudit kann nicht prüfen")

# Alle Dateien, die Produktaussagen tragen koennen. Eine Liste fuer alle Abschnitte:
# Die VERBOTEN-Liste, die Hall-Invariante und die Bestandszahlen pruefen dieselbe Menge.
# gen_longtail.py, gen_brand_sections.py und gen_pages.py stehen mit drin, weil auch sie
# Produktwerte als Literal tragen koennen und bisher von keinem Prosa-Gate gelesen wurden.
_zu_pruefen = list(pages) + [p for p in ['llms.txt', 'assets/data/longtail.json'] + \
                             sorted(glob.glob('scripts/gen_*.py'))
                             if os.path.exists(p)] + sorted(glob.glob('assets/js/*.js'))

# ---------- 6a2 · Tag-Bilanz der <div>-Ebene (30.09.2026) ----------
# Zwei Hub-Seiten schlossen ihren container-<div> nie: Der Browser holt das am </section>
# selbst nach, deshalb sah die Seite jahrelang richtig aus und keine Prüfung sprach an.
# Verlassen kann man sich darauf nicht, und ein zusätzlicher Wrapper im Markup verschiebt
# die Reparatur an eine andere Stelle.
for _f in pages:
    _t = open(_f, encoding='utf-8').read()
    _tiefe = 0
    for _m in re.finditer(r'<div\b[^>]*>|</div>', _t):
        _tiefe += -1 if _m.group(0).startswith('</') else 1
    if _tiefe > 0:
        err(f"HTML: {_f} lässt {_tiefe} <div> offen")
    elif _tiefe < 0:
        err(f"HTML: {_f} hat {-_tiefe} überzählige </div>")

# ---------- 6b2 · Fließtext gegen products.json (§A1, 30.09.2026) ----------
# Das Wert-Audit prüft strukturierte Felder. Preise und Bewertungen stehen zusätzlich im
# redaktionellen Text, in FAQ-Antworten und Metas — dort lagen nach dem Amazon-Abgleich über
# 50 veraltete Werte, teils als gekipptes Urteil ("gleich teuer" bei 70 gegen 32 Euro).
if os.path.exists('scripts/audit_prosa.py'):
    import subprocess
    _pr = subprocess.run([sys.executable, 'scripts/audit_prosa.py'], capture_output=True, text=True)
    if _pr.returncode != 0:
        for _z in _pr.stdout.strip().splitlines():
            if _z.strip() and 'Abweichung(en)' not in _z:
                err(f"§A1-Fließtext: {_z.strip()}")
else:
    err("scripts/audit_prosa.py fehlt — Fließtext-Werte werden nicht geprüft")

# Karten tragen neben Preis und Claim eine Kurzwertung in <div class="pro"> / <div class="con">.
# sync_cards fasst die nicht an, das Karten-Audit meldete die Karte trotzdem als korrekt:
# am 30.09. stand so "✗ Teuer (149 €)" neben einer span.price mit korrekten 152 €.
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    for _am in re.finditer(r'<article class="pcard[^"]*"', _h):
        _ende = _h.find('</article>', _am.end())
        if _ende < 0:
            continue
        _blk = _h[_am.start():_ende]
        _dm = re.search(r'data-product="([^"]+)"', _blk)
        if not _dm:
            continue
        _p = next((x for x in items if x.get('slug') == _dm.group(1)), None)
        if not _p:
            continue
        _soll = re.search(r'(\d+)', (_p.get('price') or '').replace('.', ''))
        for _cm in re.finditer(r'<div class="(?:pro|con)">(.*?)</div>', _blk, re.S):
            _txt = re.sub(r'<[^>]*>', '', _cm.group(1))
            for _em in re.finditer(r'(\d+(?:[.,]\d+)?)\s*(?:€|Euro)', _txt):
                if _soll and int(float(_em.group(1).replace(',', '.'))) != int(_soll.group(1)):
                    err(f"§A1: {_f} Karte {_p['slug']} — Kurzwertung nennt "
                        f"{_em.group(1)} €, products.json {_p['price']}")

# Die Marken-Tabelle "Die vier Marken im Bewertungsvergleich" führt einen GEWICHTETEN
# Schnitt (so steht es auch in der Fußnote). Sie wird hier nachgerechnet, damit niemand
# sie mit dem einfachen Mittelwert gegenprüft: Am 30.09. hat ein Prüflauf genau das getan
# und alle 16 Zellen als falsch gemeldet, obwohl alle 16 stimmten.
_MARKEN_TABELLE = {'8BitDo': 2, 'Backbone': 3, 'Razer': 3, 'GameSir': 5}
for _marke, _n_soll in _MARKEN_TABELLE.items():
    _ps = []
    for _p in items:
        if _p.get('brand') != _marke or _p.get('type') != 'controller':
            continue
        _bw = next((v for k, v in _p.get('specs', []) if k.startswith('Bew')), '')
        _m2 = re.match(r'([\d,]+)\s*\(([\d.]+)\)', _bw)
        if _m2:
            _ps.append((float(_m2.group(1).replace(',', '.')), int(_m2.group(2).replace('.', ''))))
    if not _ps:
        continue
    _summe = sum(c for _, c in _ps)
    _gew = f"{sum(s * c for s, c in _ps) / _summe:.2f}".replace('.', ',')
    if len(_ps) != _n_soll:
        err(f"§A1: {_marke} hat jetzt {len(_ps)} Controller, die Marken-Tabelle ist auf "
            f"{_n_soll} gebaut — Zeile und Bewertungssumme prüfen")
    for _bf in glob.glob('marken/*/index.html'):
        _h = open(_bf, encoding='utf-8').read()
        if 'Die vier Marken im Bewertungsvergleich' not in _h:
            continue
        _zeile = re.search(r'<td>(?:<strong>)?' + re.escape(_marke) + r'(?:</strong>)?</td>'
                           r'<td>(\d+)</td><td>([\d,]+)</td><td>([\d.]+)</td>', _h)
        if not _zeile:
            err(f"§A1: {_bf} — Marken-Tabellenzeile für {_marke} nicht lesbar")
            continue
        if _zeile.group(2) != _gew:
            err(f"§A1: {_bf} — Ø {_marke} steht mit {_zeile.group(2)}, gewichtet aus "
                f"products.json sind es {_gew}")
        if _zeile.group(3).replace('.', '') != str(_summe):
            err(f"§A1: {_bf} — Bewertungssumme {_marke} steht mit {_zeile.group(3)}, "
                f"products.json ergibt {_summe}")

# ---------- 6b3 · Maschinenlesbare Werte und Generator-Literale (§A1, 30.09.2026) ----------
# data-price steuert die Sortierung "Preis aufsteigend" auf dem Controller-Hub. Vier der
# acht Werte waren nach dem Amazon-Abgleich veraltet, während die SICHTBAREN Preise
# daneben stimmten: ein funktionaler Fehler, den keine Textprüfung sehen kann.
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    for _m in re.finditer(r'<[^>]*data-price="(\d+)"[^>]*>', _h):
        _dm = re.search(r'data-product="([^"]+)"', _m.group(0))
        if not _dm:
            continue
        _p = next((x for x in items if x.get('slug') == _dm.group(1)), None)
        if not _p:
            continue
        _soll = re.search(r'(\d+)', (_p.get('price') or '').replace('.', ''))
        if _soll and _m.group(1) != _soll.group(1):
            err(f"§A1: {_f} data-price=\"{_m.group(1)}\" für {_p['slug']}, "
                f"products.json sagt {_p['price']} — die Preissortierung rechnet falsch")

# data-platform ist der Zwilling von data-price: Es steuert den Live-Filter
# (iPhone/Android/Universal) auf dem Controller-Hub. Fünf von acht Werten wichen von
# worksOn ab, unter anderem erschien der kabelgebundene Ultimate 2C im iPhone-Filter —
# genau die Aussage, die eine Runde zuvor aus dem TEXT entfernt worden war. Im Attribut
# hat sie überlebt und dort funktional gewirkt.
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    for _m in re.finditer(r'<[^>]*data-platform="([^"]*)"[^>]*>', _h):
        _dm = re.search(r'data-product="([^"]+)"', _m.group(0))
        if not _dm:
            continue
        _p = next((x for x in items if x.get('slug') == _dm.group(1)), None)
        if not _p:
            continue
        _ist, _soll = set(_m.group(1).split()), set(_p.get('worksOn') or [])
        if _ist != _soll:
            err(f"§A1: {_f} data-platform=\"{_m.group(1)}\" für {_p['slug']}, worksOn sagt "
                f"{' '.join(sorted(_soll))} — der Hub-Filter zeigt das Produkt falsch an")

# data-asin erzeugt den Affiliate-Link. Ein falscher Wert verkauft ein fremdes Produkt.
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    for _m in re.finditer(r'<[^>]*data-asin="([^"]*)"[^>]*>', _h):
        _dm = re.search(r'data-product="([^"]+)"', _m.group(0))
        if not _dm:
            continue
        _p = next((x for x in items if x.get('slug') == _dm.group(1)), None)
        if _p and _m.group(1) != _p.get('asin'):
            err(f"§A1: {_f} data-asin=\"{_m.group(1)}\" für {_p['slug']}, products.json sagt "
                f"{_p['asin']} — der Kauflink führt zum falschen Produkt")

# worksOn ist handgepflegt und wurde bisher gegen NICHTS geprueft. Runde 4 hat
# data-platform aus worksOn gesetzt und damit einen falschen Wert nur sauber ins
# Attribut propagiert: viture-8bitdo trug "ios", waehrend der claim DESSELBEN Eintrags
# "Kein iOS, kein Bluetooth" sagt und specs "USB-C" fuehrt. Das Produkt stand als Karte
# im iPhone-Hub, mit genau diesem Satz sichtbar darauf.
for _p in items:
    _claim = (_p.get('claim') or '')
    _verb = dict(_p.get('specs') or {}).get('Verb.', '')
    _w = set(_p.get('worksOn') or [])
    if re.search(r'\bKein iOS\b|\bohne iOS\b|\bnicht .{0,12}iPhone\b', _claim, re.I) and 'ios' in _w:
        err(f"§A1: {_p['slug']} hat 'ios' in worksOn, der eigene claim sagt aber "
            f"\"{_claim[:70]}\"")
    if re.search(r'\bKein Bluetooth\b|\bohne Bluetooth\b', _claim, re.I) and 'Bluetooth' in _verb:
        err(f"§A1: {_p['slug']} fuehrt Bluetooth in den Specs, der eigene claim "
            f"widerspricht: \"{_claim[:70]}\"")
    if 'kabelgebunden' in _verb.lower() and re.search(r'\bkabellos\b|\bper Bluetooth\b', _claim, re.I):
        err(f"§A1: {_p['slug']} ist laut specs kabelgebunden, der claim sagt kabellos")

# ItemList-Zähler gegen die tatsächliche Länge und gegen die Kartenzahl. Genau diese
# Klasse hat die unvollständige Entfernung des VITURE aus dem iPhone-Hub überlebt:
# Karte, Listeneintrag und sichtbarer Zähler waren korrigiert, "numberOfItems" blieb
# auf 25. Ein Zähler, den niemand nachrechnet, ist ein stiller Widerspruch im Schema.
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    for _sm in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', _h, re.S):
        try:
            _obj = json.loads(_sm.group(1))
        except Exception:
            continue
        for _node in (_obj.get('@graph') if isinstance(_obj.get('@graph'), list) else [_obj]):
            if not isinstance(_node, dict) or 'ItemList' not in _typen_von(_node):
                continue
            _liste = _node.get('itemListElement') or []
            if _node.get('numberOfItems') is not None and int(_node['numberOfItems']) != len(_liste):
                err(f"§A4: {_f} ItemList numberOfItems={_node['numberOfItems']}, "
                    f"die Liste hat {len(_liste)} Einträge")
            # Bewusst NICHT gegen die Kartenzahl: Mehrere Seiten führen absichtlich eine
            # Top-Auswahl im Schema und zeigen mehr Karten. numberOfItems gegen die
            # Listenlänge gilt dagegen immer.

# Der Affiliate-Tag ist die Geldleitung und stand nur in main.js, von keinem Gate gelesen.
if os.path.exists('assets/js/main.js'):
    _mj = open('assets/js/main.js', encoding='utf-8').read()
    if "AFFILIATE_TAG = 'ygmedia-21'" not in _mj:
        err("§A3: assets/js/main.js führt nicht mehr den PartnerNet-Tag ygmedia-21 — "
            "jeder Kauflink liefe auf ein fremdes Konto")
# Repoweit: KEIN anderer PartnerNet-Tag darf irgendwo stehen. Die Pruefung auf
# Anwesenheit des richtigen Tags in einer Datei deckte nur eine von drei Stellen ab
# (main.js, gen_pages.py, ein Product-Schema). Abwesenheit des falschen schlaegt
# Anwesenheit des richtigen - dieselbe Lehre wie bei der Hall-Invariante.
# ALLE Textdateien, nicht nur HTML/Python/JS: Ein fremder Tag in products.json,
# sitemap.xml oder style.css blieb sonst unentdeckt - genau die drei Orte, die der
# Pruefer getestet hat.
_TAG_DATEIEN = [x for x in glob.glob('**/*', recursive=True)
                if os.path.isfile(x) and x.split('.')[-1] in
                ('html', 'py', 'js', 'json', 'txt', 'css', 'xml', 'md')
                and not x.startswith(('brain/', 'SPC-Gaming-Visuals/', '.git/'))]
for _f in _TAG_DATEIEN:
    if not os.path.exists(_f):
        continue
    for _tm in re.finditer(r'tag=([A-Za-z0-9_-]+)', open(_f, encoding='utf-8').read()):
        if _tm.group(1) != 'ygmedia-21':
            err(f"§A3: {_f} enthält den fremden PartnerNet-Tag \"{_tm.group(1)}\" — "
                f"die Provision liefe auf ein anderes Konto")


# Der Footer nennt die Empfehlungsschwelle und wird in 109 Seiten injiziert. Er stand
# auf "4★+", während §A6 bei 3,8 liegt und 11 Produkte darunter empfohlen werden.
# Eine Schwelle, die an zwei Stellen steht, muss an beiden dieselbe sein.
# (Stand ausgerueckt: Der Block lag versehentlich IN der Tag-Schleife und meldete
# denselben Fehler 141 Mal, einmal pro gepruefter Datei. Fehlte main.js, starb verify
# mit NameError statt zu melden, dass die Schwelle fehlt.)
_mj_pfad = 'assets/js/main.js'
if not os.path.exists(_mj_pfad):
    err("§A6: assets/js/main.js fehlt — Footer, Affiliate-Tag und Empfehlungsschwelle "
        "sind damit ungeprueft")
else:
    _sm2 = re.search(r'Empfehlungsschwelle liegt bei <strong>([\d,]+) Sternen',
                     open(_mj_pfad, encoding='utf-8').read())
    if not _sm2:
        err("§A6: assets/js/main.js nennt die Empfehlungsschwelle nicht mehr — "
            "der Footer trug schon einmal eine andere Zahl als verify.py")
    elif _sm2.group(1).replace(',', '.') != str(A6_SCHWELLE):
        err(f"§A6: assets/js/main.js nennt {_sm2.group(1)} Sterne als Schwelle, "
            f"verify.py prüft gegen {A6_SCHWELLE}")

# Bestands- und Testzahlen auf der Startseite und im Header. Sie standen auf
# "100+ Controller getestet" neben "40+ Modelle im Sortiment" auf derselben Seite:
# unbelegt, in sich widersprüchlich, und auf der meistbesuchten Seite. Zahlen, die
# den eigenen Bestand beziffern, werden gerechnet.
_n_produkte = len(items)
_n_reviews = len([p for p in items if (p.get('detail') or '').startswith('/controller/')])
# REPOWEIT und ueber ALLE Vorkommen. Vorher: zwei fest benannte Dateien und `re.search`,
# also genau EIN Treffer je Datei. index.html traegt "Modelle im Sortiment" viermal, und
# seit die Navigation statisch ausgeliefert wird, steht die Zahl auf 112 Stellen statt auf
# einer Laufzeitstelle. Ein gefaelschtes zweites Vorkommen blieb damit unsichtbar.
_ZAHL_PAARE = [(str(_n_produkte), 'Modelle im Sortiment'),
               (str(_n_reviews), 'ausführliche Tests')]
_gefunden = {lbl: 0 for _, lbl in _ZAHL_PAARE}
for _f in _zu_pruefen:
    _h = open(_f, encoding='utf-8').read()
    for _zahl, _label in _ZAHL_PAARE:
        # Zwischen Zahl und Label duerfen beliebig viele Tags stehen, aber kein Text:
        # im Markup ist das <div class="num">13</div><div class="cap">ausfuehrliche Tests</div>.
        for _m in re.finditer(r'([\d.]+\+?)\s*(?:<[^>]*>\s*)*' + re.escape(_label), _h):
            _gefunden[_label] += 1
            if _m.group(1) != _zahl:
                err(f"§A5: {_f} nennt {_m.group(1)} {_label}, products.json ergibt {_zahl}")
for _zahl, _label in _ZAHL_PAARE:
    if not _gefunden[_label]:
        err(f"§A5: die Zahl zu \"{_label}\" steht nirgends mehr im Repo — sie stand "
            f"schon einmal unbelegt bei 100+")
# Kategorie-Kacheln der Startseite gegen den Hub-Bestand
for _flag, _label in [('ios', 'iPhone Controller'), ('android', 'Android Controller'),
                      ('universal', 'Universal / Multi')]:
    _soll = len([p for p in items if _flag in (p.get('worksOn') or []) and p.get('type') == 'controller'])
    _hi = open('index.html', encoding='utf-8').read()
    _m = re.search(re.escape(_label) + r'</div>\s*<div class="cat-count">(\d+)', _hi)
    if _m and int(_m.group(1)) != _soll:
        err(f"§A5: index.html Kachel \"{_label}\" nennt {_m.group(1)} Modelle, "
            f"worksOn ergibt {_soll}")

# REPOWEIT: Jede Stelle, die "N Controller für <Plattform>" behauptet, muss den
# gerechneten Bestand nennen. llms.txt stand als EINZIGE Stelle auf 28 iPhone-Controllern,
# waehrend products.json, der Hub, sein ItemList-Zaehler, sein hubCount und die
# Startseiten-Kachel uebereinstimmend 24 sagen. Die Invariante war auf index.html
# festgenagelt - dieselbe Bindung an eine Datei, die schon zweimal Befunde durchgelassen hat.
_PLATTFORM_WORT = {'ios': r'(?:iPhone|iOS)', 'android': r'Android', 'universal': r'Universal'}
for _flag, _wort in _PLATTFORM_WORT.items():
    _soll = len([p for p in items if _flag in (p.get('worksOn') or []) and p.get('type') == 'controller'])
    for _f in _zu_pruefen:
        for _m in re.finditer(r'(\d{1,3})\s+Controller\s+(?:für|fuer)\s+' + _wort, 
                              open(_f, encoding='utf-8').read()):
            if int(_m.group(1)) != _soll:
                err(f"§A5: {_f} nennt {_m.group(1)} Controller für {_flag}, "
                    f"worksOn ergibt {_soll}")

# Datenstand: EINE Zahl fuer das ganze Repo. Vor dieser Invariante standen fuenf
# verschiedene Angaben gleichzeitig live (Juni, Juli, August, September, 30.09.), und
# neunzehn Seiten mit "Stand Juli 2026" trugen Preise, die erst am 30.09. entstanden.
# Bei jedem Preis-Sync wird hier EINE Zeile geaendert, das Gate haelt den Rest nach.
DATENSTAND_MONAT = 'September 2026'
DATENSTAND_TAG = '30.09.2026'
for _f in _zu_pruefen:
    _h = open(_f, encoding='utf-8').read()
    for _dm in re.finditer(r'(?:Stand|Datenstand|Aktuell)[:\s]*'
                           r'((?:Januar|Februar|März|April|Mai|Juni|Juli|August|September'
                           r'|Oktober|November|Dezember)\s*\d{4}|\d{2}\.\d{2}\.\d{4})', _h):
        if _dm.group(1) not in (DATENSTAND_MONAT, DATENSTAND_TAG):
            err(f"§A5: {_f} nennt den Datenstand \"{_dm.group(1)}\", aktuell ist "
                f"{DATENSTAND_MONAT} ({DATENSTAND_TAG})")

# Die MASCHINENLESBARE Fassung des Datums muss zur sichtbaren passen. Eine Seite, die
# "Stand September 2026" zeigt und im Schema dateModified 2026-07-18 fuehrt, sagt
# Menschen und Google Verschiedenes - und Google liest das Schema. Geprueft wird nur,
# dass dateModified nicht AELTER ist als der ausgewiesene Datenstand.
_DS_ISO = '-'.join(reversed(DATENSTAND_TAG.split('.')))
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    if not re.search(r'(?:Stand|Datenstand|Aktuell)[:\s]*' + re.escape(DATENSTAND_MONAT), _h):
        continue
    for _dm in re.finditer(r'"dateModified":\s*"(\d{4}-\d{2}-\d{2})', _h):
        if _dm.group(1) < _DS_ISO:
            err(f"§A5: {_f} zeigt \"{DATENSTAND_MONAT}\", fuehrt im Schema aber "
                f"dateModified {_dm.group(1)} — Google liest das Schema")

# Sitemap: lastmod darf nicht aelter sein als die letzte Aenderung der Datei selbst.
# 88 von 108 Eintraegen standen auf Juli, waehrend die Seiten am 30.09. geaendert wurden.
# Header und Footer werden vorher entfernt: seit die Navigation statisch ausgeliefert wird
# (§A2), traegt der Trust-Strip den Datenstand auf JEDER Seite. Das ist eine Aussage ueber
# den Produktdatenbestand, nicht ueber die einzelne Seite — wuerde sie mitzaehlen, feuerte
# dieses Gate entweder fuer alle 109 Seiten oder fuer keine und pruefte damit nichts mehr.
_CHROME = re.compile(r'<header[^>]*id="site-header".*?</header>'
                     r'|<footer[^>]*id="site-footer".*?</footer>', re.S)
if os.path.exists('sitemap.xml'):
    _sm = open('sitemap.xml', encoding='utf-8').read()
    for _um in re.finditer(r'<url>\s*<loc>https://smartphone-controller\.com/([^<]*)</loc>\s*'
                           r'<lastmod>([^<]+)</lastmod>', _sm):
        _datei = (_um.group(1) or '') + 'index.html'
        if not os.path.exists(_datei):
            continue
        _hs = _CHROME.sub(' ', open(_datei, encoding='utf-8').read())
        if re.search(r'(?:Stand|Datenstand|Aktuell)[:\s]*' + re.escape(DATENSTAND_MONAT), _hs) \
                and _um.group(2) < _DS_ISO:
            err(f"§B: sitemap.xml fuehrt fuer /{_um.group(1)} lastmod {_um.group(2)}, "
                f"die Seite weist aber {DATENSTAND_MONAT} aus")

# "Preise woechentlich geprueft" ist eine Prozessbehauptung, die der eigene Verlauf
# widerlegt: letzte Preispflege 21.07., naechste 30.09., also zehn Wochen. Solche
# Frequenz-Zusagen gehoeren nicht auf die Seite, solange sie niemand einhaelt.
# Offen gefasst statt aufgezaehlt: "laufend gepflegt" ist dieselbe Zusage wie
# "laufend geprueft" und stand nach Runde 9 weiter live. Adverb und Partizip werden
# jeweils als Gruppe geprueft, nicht als Paarliste.
_FREQUENZ = re.compile(
    r'\b(?:wöchentlich|täglich|monatlich|laufend|fortlaufend|regelmäßig|ständig|stets)\s*'
    r'(?:aktualisiert|gepflegt|geprüft|kontrolliert|nachgezogen)'
    r'|\b(?:immer|stets)\s+aktuell\b', re.I)
for _f in _zu_pruefen:
    for _fm in _FREQUENZ.finditer(open(_f, encoding='utf-8').read()):
        err(f"§A5: {_f} verspricht \"{_fm.group(0)}\" — eine Frequenz-Zusage, die der "
            f"Verlauf nicht hergibt (Preispflege 21.07. -> 30.09.)")

# §A2 + §C2: Pflichtangaben muessen OHNE JavaScript dastehen. Der Footer wurde bis zur
# zehnten Pruefrunde ausschliesslich per main.js injiziert - ohne JS gab es auf 109
# Seiten keinen Affiliate-Hinweis, kein Impressum und keinen Datenschutz-Link. Der
# No-JS-Check prueft bisher nur Produktkartenzahlen auf vier Hubs.
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    if 'http-equiv="refresh"' in _h:
        continue
    _fehlt = [_n for _n, _p in (('Impressum-Link', r'href="/impressum/"'),
                                ('Datenschutz-Link', r'href="/datenschutz/"'),
                                ('Affiliate-Hinweis', r'Transparenz-Hinweis'))
              if not re.search(_p, _h)]
    if _fehlt:
        err(f"§A2/§C2: {_f} zeigt ohne JavaScript nicht: {', '.join(_fehlt)}")

# Preis direkt hinter einem Produktlink (§A1). Die zwoelfte Datenquelle: Beide Audits
# binden Preise ueber NAMEN und Aliase an Produkte. Ein Preis, der ueber
# href="/produkte/<slug>/" an ein Produkt gebunden ist, war fuer beide unsichtbar --
# obwohl der Slug maschinenlesbar danebensteht. So standen in
# blog/mobile-gaming-setup/ ein Kuehler mit 18 statt 16 Euro und ein Trigger-Link auf
# ein 20-Euro-Produkt neben der Aussage "ab 9 Euro", waehrend alle drei Gates gruen waren.
# Der Schwanz endet am naechsten Link ODER am naechsten Produktnamen: ein festes
# Zeichenfenster nahm sonst den Preis des naechsten Produkts mit (belegt an
# blog/guenstige-handy-controller/, wo 50 Euro zum EasySMX M15 gehoeren, nicht zum davor
# verlinkten MGPXPRO).
# Abgeschnitten wird an MARKEN, nicht an Produktnamen: im Fliesstext steht "EasySMX M15",
# in products.json heisst das Produkt "M15 Controller (Mecha)" -- der Name trifft den Text
# also nie, die Marke schon.
_MARKEN = sorted({(p['brand'], p['slug']) for p in items if p.get('brand')})
_NAMEN = sorted({(p.get('name') or '', p['slug']) for p in items if p.get('name')})
# Der Link darf Attribute VOR href tragen: zwei Links im Bestand schreiben class= zuerst
# und waren fuer die erste Fassung dieses Gates unsichtbar.
# WAS DIESES GATE NICHT KANN: Es sieht nur HINTER den Link. Ein Preis DAVOR, dessen
# Produktbezug allein im Linktext steht ("24 Euro teure <a …>Peltier-Kuehler</a>"), faellt
# durch. Eine Pruefung davor haette Fehlalarme auf legitime Differenzsaetze erzeugt
# ("Der Kishi V3 Pro kostet 64 Euro mehr"); alle 232 Stellen wurden am 30.09. von Hand
# auf diese Klasse abgesucht, ohne echten Fund.
# Der Schwanz steht in einem LOOKAHEAD, wird also nicht mitkonsumiert. Als er Teil des
# Treffers war, verschluckte jeder Match bis zu 200 Zeichen und finditer setzte dahinter
# auf: ein Produktlink, der dicht hinter einem anderen stand, wurde stumm uebersprungen.
# Auf blog/mobile-gaming-setup/ fehlte dadurch genau der Link, dessen falscher Preis
# diesen Gate ueberhaupt ausgeloest hat.
_PLINK = re.compile(r'<a\b[^>]*?href="/produkte/([^"/]+)/"[^>]*>(.*?)</a>(?=(.{0,200}))', re.S)
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    for _m in _PLINK.finditer(_h):
        _slug = _m.group(1)
        # Der Schwanz darf Tags ENTHALTEN, sie werden entfernt. Ein Muster, das am
        # naechsten "<" endet, liess sich mit einem <strong> um den Preis aushebeln --
        # genau der Original-Defekt blieb so gruen.
        _schwanz = _m.group(3).split('<a ')[0]
        # Am Blockende abschneiden. Ohne das reichte das Fenster ueber den Absatz hinaus:
        # auf produkte/razer-phone-cooler/ steht hinter dem Link auf den Black Shark der
        # naechste Abschnitt mit der EIGENEN Preistabelle (70 €) — als Abweichung gemeldet,
        # obwohl beide Angaben stimmen. "Direkt hinter dem Link" endet am Block.
        _schwanz = re.split(r'</(?:p|div|li|td|h[1-6]|section)\b|<(?:h[1-6]|table|tr|section)\b',
                            _schwanz)[0]
        _schwanz = re.sub(r'<[^>]*>', ' ', _schwanz)
        _eigen = next((x for x in items if x['slug'] == _slug), None)
        _eigene_marke = (_eigen or {}).get('brand')
        for _n, _s in list(_MARKEN) + list(_NAMEN):
            if _s == _slug or len(_n) < 4 or _n == _eigene_marke:
                continue
            _i = _schwanz.find(_n)
            if _i >= 0:
                _schwanz = _schwanz[:_i]
        _pm = re.search(r'(\d+)\s*(?:€|Euro)', _schwanz)
        if not _pm:
            continue
        if not _eigen:
            err(f"§A1: {_f} verlinkt /produkte/{_slug}/, das products.json nicht kennt")
            continue
        _soll = re.search(r'(\d+)', _eigen.get('price', '') or '')
        if _soll and _soll.group(1) != _pm.group(1):
            err(f"§A1: {_f} nennt {_pm.group(1)} € direkt hinter dem Link auf "
                f"/produkte/{_slug}/, products.json sagt {_eigen['price']}")

# "ab N €" ist eine Untergrenzen-BEHAUPTUNG, keine blosse Zahl (§A5). Das Fliesstext-Audit
# nimmt solche Stellen bewusst von der Preisprüfung aus, weil sie zu keinem einzelnen
# Produkt gehoeren — damit waren sie bis 30.09.2026 voellig ungeprueft. Laut Protokoll ist
# genau daran schon einmal "Hall-Effect ab 20 €" live gegangen, obwohl der guenstigste
# Hall-Controller 30 € kostet.
# WAS DIESES GATE NICHT KANN: Es kennt die gemeinte Menge nicht ("ab 30 €" kann sich auf
# das Sortiment, eine Kategorie oder eine Marke beziehen) und prueft deshalb NICHT, ob N
# wirklich das Minimum dieser Menge ist. Es prueft nur, dass N ueberhaupt ein Preis ist,
# den wir fuehren. Ob die Untergrenze stimmt, bleibt Handarbeit.
_PREISE_ROH = {re.search(r'(\d+)', p['price']).group(1)
               for p in items if p.get('price') and re.search(r'(\d+)', p['price'])}
# Preisband-Ueberschriften sind keine Untergrenzen-Behauptung: "Ab 100 Euro: Premium" auf
# /geschenke/ benennt ein Budget-Segment. Ausgenommen wird nur, was eine Ueberschrift
# EROEFFNET — "Hall-Effect ab 20 €" als h2 bleibt damit geprueft, und genau diese Form ist
# laut Protokoll schon einmal falsch live gegangen.
# Nur den KOPF der Ueberschrift maskieren, nicht ihren Rest: die erste Fassung entfernte
# die ganze Ueberschrift, damit waere "Controller ab 5 Euro" im selben h2 unsichtbar
# geworden.
_BANDTITEL = re.compile(r'(<h[1-4][^>]*>\s*)(?:Ab|ab)\s+\d+\s*(?:€|Euro)')
for _f in pages:
    _h = re.sub(r'<[^>]*>', ' ', _BANDTITEL.sub(r'\1', open(_f, encoding='utf-8').read()))
    for _m in re.finditer(r'\bab\s+(?:ca\.\s*)?(?:€\s*)?(\d+)\s*(?:€|Euro)\b', _h, re.I):
        if _m.group(1) not in _PREISE_ROH:
            err(f"§A5: {_f} behauptet \"{_m.group(0).strip()}\", aber kein Produkt in "
                f"products.json kostet {_m.group(1)} € — eine Untergrenze muss ein Preis "
                f"sein, den wir tatsaechlich fuehren")

# platformLabel gegen worksOn (§A1). platformLabel steuert ueber ALT_PLATFORM in
# gen_pages.py den Alt-Text jedes Produktbildes: "Universal" wird zu "fuer Android &
# iPhone". Als der VITURE-Eintrag in Runde 6 sein falsches worksOn-ios verlor, blieb
# platformLabel auf "Universal" stehen — die Seite sagte im Lead "Kein iOS, kein
# Bluetooth" und im Alt-Text derselben Seite "fuer Android & iPhone". platformLabel kam
# in keinem der drei Pruefskripte vor.
_LABEL_VERLANGT = {'Universal': ('android', 'ios'), 'iPhone': ('ios',), 'Android': ('android',)}
for _p in items:
    _lbl = _p.get('platformLabel')
    if _lbl not in _LABEL_VERLANGT:
        continue
    _fehlt = [f for f in _LABEL_VERLANGT[_lbl] if f not in (_p.get('worksOn') or [])]
    if _fehlt:
        err(f"§A1: {_p['slug']} traegt platformLabel \"{_lbl}\", worksOn fuehrt aber "
            f"{', '.join(_fehlt)} nicht — das Label steuert den Alt-Text jedes "
            f"Produktbildes dieser Seite")

# Product-Schema "image" darf nur das Hauptbild fuehren (§A5/§C3). Google liest dieses
# Feld als DAS Produktbild. In den Amazon-Galerien liegen nachweislich A+-Werbebanner mit
# eingebrannter Herstellerwerbung: beim Kishi V3 alle drei, beim ROG Tessen alle drei,
# dazu mindestens je eins bei GameSir und Backbone. Ueber die URL sind sie nicht von
# echten Produktfotos zu unterscheiden, nur durch Ansehen. Das Hauptbild ist die einzige
# Klasse, die garantiert werbefrei ist, weil Amazon dafuer weissen Hintergrund ohne Text
# vorschreibt.
# WAS DIESES GATE NICHT KANN: Es sagt nichts ueber die SICHTBAREN Galerien. Die bleiben
# stehen und sind als Katalogbilder ausgewiesen; ob dort Werbung stehen darf, ist eine
# Lizenz- und Kennzeichnungsfrage fuer Yasin (siehe STATUS).
# Gebunden an DAS Produkt dieser Seite, nicht an eine repoweite Freigabeliste. Die erste
# Fassung pruefte nur "ist irgendein Hauptbild aus dem Sortiment" — damit lief das
# ASUS-ROG-Bild als GameSir-Testsieger wieder durch, also genau der Fehler, der die ganze
# Bildarbeit ausgeloest hat. Derselbe Freibrief-Bauplan wie das geloeschte ALLE_PREISE.
# Aufgeloest wird ueber die SEITE (Pfad, sonst die data-asin darauf), NICHT ueber den
# Namen im Schema. Die zweite Fassung tat das Umgekehrte und kehrte bei eindeutigem
# Namenstreffer sofort zurueck — der ASIN-Zweig war toter Code. Wer Schema-name UND
# -image gemeinsam auf ein fremdes Produkt stellte, kam durch: die Seite lieferte ein
# Product-Schema mit fremdem Namen und fremdem Foto, aber eigenem Preis und eigener
# Bewertung. Ein Gate, das an die Behauptung bindet statt an die Identitaet, prueft die
# Behauptung gegen sich selbst.
def _hat_produktschema(_html):
    """Geparst, nicht gegreppt. Die String-Variante ('\"@type\": \"Product\"') liess sich
    mit einem Leerzeichen mehr lautlos abschalten, und damit stand der Ursprungsbefund
    wieder offen: fremdes Werbebild als Testsieger, alle Gates gruen."""
    for _sm in re.finditer(r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
                           _html, re.S):
        try:
            _d = json.loads(_sm.group(1))
        except Exception:
            continue
        for _o in (_d.get('@graph', [_d]) if isinstance(_d, dict) else _d):
            if isinstance(_o, dict) and 'Product' in _typen_von(_o):
                return True
    return False


def _externes_produkt(_f):
    """Das Produkt dieser Seite, bestimmt NUR aus Pfad und products.json[].detail.
    Beides sind externe Identitaeten: Sie stehen im Dateisystem bzw. im Datenkern und
    lassen sich durch eine Aenderung AN der Seite nicht verschieben. Genau deshalb darf
    die Pflicht, ein Product-Schema zu fuehren, nur hieran haengen — nicht am Vorhandensein
    des Schemas selbst."""
    _rel = _f.replace(os.sep, '/')
    _m = re.match(r'produkte/([^/]+)/index\.html$', _rel)
    if _m:
        _p = next((x for x in items if x['slug'] == _m.group(1)), None)
        if _p:
            return _p
    _d = [x for x in items
          if (x.get('detail') or '').strip('/') and
             (x['detail']).strip('/') == os.path.dirname(_rel)]
    return _d[0] if len(_d) == 1 else None


def _seiten_produkt(_f, _html):
    """Das Produkt, zu dem DIESE Seite gehoert.
    Reihenfolge: Pfad, dann das detail-Feld aus products.json, erst dann die data-asin
    der Seite. Die ersten beiden sind EXTERNE Identitaeten — sie stehen im Datenkern bzw.
    im Dateisystem und lassen sich durch eine Aenderung an der Seite nicht verschieben.
    Die data-asin ist eine Behauptung der Seite und bleibt nur die letzte Rueckfallebene.
    Vorher hingen die 13 handgepflegten Review-Seiten ausschliesslich an ihr: ein zweiter,
    voellig legitimer Kauf-Button ("Alternative ansehen") machte verify rot UND liess
    zugleich das og:image-Gate still durchlaufen."""
    _rel = _f.replace(os.sep, '/')
    _m = re.match(r'produkte/([^/]+)/index\.html$', _rel)
    if _m:
        _p = next((x for x in items if x['slug'] == _m.group(1)), None)
        if _p:
            return _p
    # Leeres detail darf nicht auf die Wurzel-index.html matchen
    # (os.path.dirname('index.html') ist '').
    _ueber_detail = [x for x in items
                     if (x.get('detail') or '').strip('/')
                     and x['detail'].strip('/') == os.path.dirname(_rel)]
    if len(_ueber_detail) == 1:
        return _ueber_detail[0]
    _asins = set(re.findall(r'data-asin="([^"]+)"', _html))
    _auf_seite = [x for x in items if x.get('asin') and x['asin'] in _asins]
    return _auf_seite[0] if len(_auf_seite) == 1 else None


def _name_passt(_name, _p):
    if not _name:
        return False
    _voll = f"{_p.get('brand','')} {_p.get('name','')}".strip()
    return _name in (_p.get('name'), _voll) or _name.replace(f"{_p.get('brand','')} ", '') == _p.get('name')

for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    for _sm in re.finditer(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', _h, re.S):
        try:
            _d = json.loads(_sm.group(1))
        except Exception:
            continue
        for _obj in (_d.get('@graph', [_d]) if isinstance(_d, dict) else _d):
            if not isinstance(_obj, dict) or 'Product' not in _typen_von(_obj):
                continue
            _pr = _seiten_produkt(_f, _h)
            if not _pr:
                err(f"§A5: {_f} traegt ein Product-Schema, aber die Seite laesst sich "
                    f"keinem Produkt zuordnen (weder ueber den Pfad noch ueber genau "
                    f"eine data-asin) — ohne Zuordnung ist sie nicht pruefbar")
                continue
            # Identitaetspruefungen ZUERST und unabhaengig vom Bild. Vorher standen sie
            # hinter einem `if not _bilder: continue`: ein Product-Schema ohne image-Feld
            # konnte beliebig behaupten, ein anderes Produkt zu sein. Betraf genau eine
            # von 42 Seiten (backbone-one-2-review) — die Pruefung deckte 41 ab, und
            # genau deshalb fiel die Luecke niemandem auf.
            if not _name_passt(_obj.get('name'), _pr):
                err(f"§A5: {_f} gehoert zu {_pr['slug']}, ihr Product-Schema nennt aber "
                    f"\"{_obj.get('name')}\" — ein Schema, das ein anderes Produkt "
                    f"behauptet, als die Seite verkauft")
            # offers.url traegt eine ASIN. Der Affiliate-Tag darin ist repoweit gegated,
            # die ASIN daneben war es nicht — waehrend fuer data-asin genau das seit
            # Langem geprueft wird. Ein Kauflink im Schema, der auf ein fremdes Produkt
            # zeigt, ist derselbe Fehler an einer anderen Stelle.
            _offers = _obj.get('offers') or {}
            if isinstance(_offers, dict) and _offers.get('url') and _pr.get('asin'):
                _am = re.search(r'/dp/([A-Z0-9]{10})', str(_offers['url']))
                if _am and _am.group(1) != _pr['asin']:
                    err(f"§A5: {_f} gehoert zu {_pr['slug']} (ASIN {_pr['asin']}), "
                        f"offers.url im Schema zeigt aber auf {_am.group(1)}")
            _bilder = _obj.get('image')
            _bilder = _bilder if isinstance(_bilder, list) else ([_bilder] if _bilder else [])
            if not _bilder:
                continue
            if len(_bilder) > 1:
                err(f"§A5: {_f} fuehrt {len(_bilder)} Bilder im Product-Schema — dort "
                    f"gehoert nur das Amazon-Hauptbild hin, Galeriebilder koennen "
                    f"Werbebanner sein")
            for _b in _bilder:
                if _b != _pr.get('img'):
                    err(f"§A5: {_f} fuehrt im Product-Schema von {_pr['slug']} das Bild "
                        f"{_b}, das Hauptbild dieses Produkts ist aber {_pr.get('img')}")

# og:image, twitter:image und das sichtbare Produktfoto gegen das Produkt der Seite
# (§A1/§A5). Der urspruengliche Befund ("ASUS-ROG-Werbebild als GameSir-Testsieger")
# betraf ausdruecklich auch og:image und twitter:image — ein Gate bekam aber nur der
# Schema-Zweig. Jede dieser Stellen liess sich auf ein fremdes Produkt umstellen, ohne
# dass eins der vier Gates etwas sagte.
# Geprueft wird nur auf Seiten MIT Product-Schema, also echten Produktseiten. Die
# Vergleichsseiten tragen bewusst das Standard-OG-Bild der Domain und haben kein
# Product-Schema; sie wuerden sonst drei Fehlalarme erzeugen.
# NICHT geprueft wird der <title>: "Backbone One – PlayStation Edition" steht dort als
# "Backbone One PlayStation Edition" (Gedankenstrich), eine Normalisierung brauchte mehr
# Regeln als der Fall wert ist.
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    # Die Vorbedingung haengt an der EXTERNEN Identitaet der Seite, nicht am Schema.
    # Vorher stand hier "hat die Seite ein Product-Schema?" — wer das Schema entfernte
    # oder sein @type auf "Thing" aenderte, schaltete damit die komplette Bildpruefung ab
    # (nachgewiesen: alle vier Bilder auf ein fremdes Produkt, verify gruen). Eine
    # Vorbedingung, die der Prueffling selbst stellt, ist keine.
    _pr = _externes_produkt(_f)
    if not _pr or not _pr.get('img'):
        continue
    # Und die Pflicht andersherum: Eine Produktseite OHNE Product-Schema ist selbst ein
    # Befund. Die 13 handgepflegten Review-Seiten haben keinen Generator-Zeichenvergleich,
    # der das sonst auffangen wuerde.
    if not _hat_produktschema(_h):
        err(f"§A4: {_f} gehoert zu {_pr['slug']}, traegt aber kein Product-Schema — "
            f"ohne das greift keine der schemagebundenen Pruefungen")
    _stellen = []
    for _feld in ('og:image', 'twitter:image'):
        _m = (re.search(r'(?:property|name)="' + re.escape(_feld) + r'"\s+content="([^"]*)"', _h)
              or re.search(r'content="([^"]*)"\s+(?:property|name)="' + re.escape(_feld) + r'"', _h))
        if _m:
            _stellen.append((_feld, _m.group(1)))
    _c = (re.search(r'<img[^>]*class="cta-photo"[^>]*src="([^"]*)"', _h)
          or re.search(r'<img[^>]*src="([^"]*)"[^>]*class="cta-photo"', _h))
    if _c:
        _stellen.append(('cta-photo', _c.group(1)))
    for _feld, _wert in _stellen:
        if _wert != _pr['img']:
            err(f"§A1: {_f} gehoert zu {_pr['slug']}, {_feld} zeigt aber {_wert} statt "
                f"des Hauptbildes {_pr['img']}")

# canonical muss auf die eigene URL zeigen (§B). Ein falscher Wert deindexiert die Seite
# still: Google folgt ihm und wirft die Seite aus dem Index, ohne dass sich sichtbar etwas
# aendert. 109 von 109 sind korrekt, geprueft hat es bisher nichts.
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    if 'http-equiv="refresh"' in _h:
        continue
    _soll = 'https://smartphone-controller.com/' + ('' if _f == 'index.html' else os.path.dirname(_f) + '/')
    _m = re.search(r'<link[^>]*rel="canonical"[^>]*href="([^"]*)"', _h) or \
         re.search(r'<link[^>]*href="([^"]*)"[^>]*rel="canonical"', _h)
    if not _m:
        err(f"§B: {_f} hat kein rel=\"canonical\"")
    elif _m.group(1).rstrip('/') + '/' != _soll:
        err(f"§B: {_f} zeigt canonical auf {_m.group(1)}, die eigene URL ist {_soll} — "
            f"ein falscher canonical nimmt die Seite still aus dem Index")

# Video-Herkunft (§A5). 21 Seiten binden ein Amazon-Produktvideo samt Poster ein. Die
# Poster-URLs stehen weder in img noch in gallery und fielen damit nicht unter die
# Herkunftsregel fuer Produktbilder, obwohl sie dieselbe Rolle spielen.
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    for _m in re.finditer(r'<video[^>]*>', _h):
        for _attr in ('src', 'poster'):
            _a = re.search(_attr + r'="([^"]*)"', _m.group(0))
            if _a and not _a.group(1).startswith(('https://m.media-amazon.com/',
                                                  'https://m.media-amazon.com/images/S/')):
                err(f"§A5: {_f} bindet ein Video mit {_attr} \"{_a.group(1)}\" ein — "
                    f"Produktvideos und ihre Poster muessen aus dem Amazon-Katalog kommen")

# Ungueltige "<" im Markup (§A2). Zwei Klassen, mit unterschiedlicher Schwere:
#   1. Ein "<", das ein Tag EROEFFNET, aber nie mit ">" schliesst — der Parser
#      verschluckt alles bis zum naechsten ">", typischerweise den ganzen Absatz samt
#      schliessendem Tag. Das ist der gefaehrliche Fall.
#   2. Ein rohes "<" im Text ("<10mm") — ungueltiges Markup, aber der Parser behaelt den
#      Text. Wird gemeldet, mit eigener, zutreffender Begruendung.
#
# Zwei Fehlversuche davor, beide lehrreich:
# 1. `<(?![a-zA-Z!/?])` war gegenueber seiner eigenen Begruendung INVERTIERT: Es meldete
#    "<10mm" (harmlos, "1" kann kein Tag-Name sein, der Text bleibt stehen) und liess
#    "<ab 20 Millimeter" durch (schaedlich).
# 2. Eine Liste gueltiger Elementnamen war eine FREIGABELISTE und damit genau die Bauart,
#    die der Pattern-Katalog verbietet: "<b 200 Gramm" kam durch, weil "b" auf der Liste
#    steht, und gleichzeitig meldete sie 21 gueltige Elemente (<abbr>, <mark>, <clipPath>)
#    als Fehler -- mit der Anweisung, sie als &lt; zu schreiben, was das Markup zerstoert
#    haette.
#
# Die Regel ist jetzt STRUKTURELL, nicht namensbasiert: Zwischen einem tag-eroeffnenden
# "<" und dem naechsten "<" muss ein ">" stehen. Das braucht keine Liste und kennt damit
# auch Elemente, die wir noch nie benutzt haben. Geprueft: 0 Befunde auf den 125
# Bestandsseiten, 10/10 in der Gegenprobe.
# Maskiert wird alles, worin ein "<" legitim steht: script, style, Kommentare UND
# Attributwerte. Ohne die Attributmaske meldete das Gate alt="Gewicht < 200 g" und
# onclick="if(a<b)go()" als Fehler — mit html.parser nachgemessen bleiben beide intakt,
# die Meldung "der Parser frisst alles bis zum naechsten >" war dort schlicht falsch.
_MASKE = re.compile(r'<(script|style)\b[^>]*>.*?</\1>|<!--.*?-->|="[^"]*"|=\'[^\']*\'', re.S)
for _f in pages:
    _roh = _MASKE.sub(lambda m: ' ' * len(m.group(0)), open(_f, encoding='utf-8').read())
    for _m in re.finditer(r'<', _roh):
        _i = _m.start()
        _rest = _roh[_i + 1:]
        _stelle = _roh[max(0, _i - 35):_i + 40].replace('\n', ' ')
        if not re.match(r'[a-zA-Z!/?]', _rest):
            # Diese Klasse ist nicht gefaehrlich: "<10mm" ueberlebt den Parser, der Text
            # bleibt vollstaendig stehen (mit html.parser nachgemessen). Sie ist trotzdem
            # ungueltiges Markup und ein Zeichen dafuer, dass jemand ein "<" getippt hat,
            # wo &lt; hingehoert. Deshalb gemeldet, aber mit zutreffender Begruendung --
            # die alte Meldung behauptete hier faelschlich dasselbe wie beim gefaehrlichen
            # Fall.
            err(f"§A2: {_f} enthaelt ein rohes \"<\" im Text (…{_stelle}…) — ungueltiges "
                f"Markup, als &lt; schreiben (der Text selbst bleibt sichtbar)")
            continue
        _nz, _ng = _rest.find('<'), _rest.find('>')
        if _ng < 0 or (0 <= _nz < _ng):
            err(f"§A2: {_f} oeffnet ein Tag, das nie mit \">\" schliesst "
                f"(…{_stelle}…) — der Parser frisst alles bis zum naechsten \">\"")

# longtail.json verweist mit "alternatives" auf Slugs aus products.json. Ein haengender
# Verweis liess den Generator mit KeyError sterben und riss damit den gesamten
# Generator-Abgleich mit -- 40 Pruefungen weg, ersetzt durch eine Zeile, die keine davon
# nannte. Der Generator laesst die unbekannte Alternative jetzt weg; gemeldet wird sie
# hier. 13 der 42 Produkte sind als Alternative verdrahtet, das trifft also jedes dritte.
_LT = "assets/data/longtail.json"
if os.path.exists(_LT):
    try:
        _ltd = json.load(open(_LT, encoding="utf-8"))
    except Exception as _e:
        err(f"§A1: {_LT} ist kein gueltiges JSON ({_e})")
        _ltd = []
    _slugs = {x["slug"] for x in items}
    for _e in (_ltd if isinstance(_ltd, list) else []):
        _alt = _e.get("alternatives") or []
        _bekannt_alt = [_a for _a in _alt if _a in _slugs]
        for _a in _alt:
            if _a == _e.get("slug"):
                err(f"§A1: {_LT}: {_e.get('slug')} fuehrt sich selbst als Alternative")
            elif _a not in _slugs:
                err(f"§A1: {_LT}: {_e.get('slug')} verweist als Alternative auf "
                    f"\"{_a}\", das products.json nicht kennt — der Verweis laeuft ins "
                    f"Leere und die Karte fehlt still auf der Seite")
        # Der leere Fall war bis zur 19. Runde ungemeldet, waehrend der Generator daran
        # mit IndexError starb: Die Reparatur der Vorrunde hatte den Fehler nur zwei
        # Zeilen weiter geschoben. Diese Seiten leben davon, auf etwas Aktuelles zu
        # verweisen — ohne Alternative sind sie eine Sackgasse.
        if not _bekannt_alt:
            err(f"§A1: {_LT}: {_e.get('slug')} hat keine einzige bekannte Alternative — "
                f"die Seite verweist auf kein aktuelles Produkt mehr")

# Doppelte Schema-Bloecke (§A4). Ein nicht-idempotenter Generator haengt bei jedem Lauf
# an: am 30.09. standen nach einem zweiten `gen_hubs.py`-Lauf ItemList, BreadcrumbList UND
# FAQPage doppelt auf allen drei Haupt-Hubs. verify hat die Bloecke bis dahin nur GEZAEHLT
# und blieb gruen — eine doppelte FAQPage auf einer URL ist ein Rich-Results-Risiko.
# Geprueft wird der @type, nicht der Bytevergleich: zwei ItemLists mit verschiedenen
# Eintraegen waeren genauso falsch wie zwei identische.
_EINMALIG = {'ItemList', 'BreadcrumbList', 'FAQPage', 'Product', 'WebSite', 'Organization'}
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    _typen = []
    for _sm in re.finditer(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', _h, re.S):
        try:
            _d = json.loads(_sm.group(1))
        except Exception:
            continue
        for _obj in (_d.get('@graph', [_d]) if isinstance(_d, dict) else _d):
            for _t in _typen_von(_obj):
                if _t in _EINMALIG:
                    _typen.append(_t)
    # Product darf mehrfach vorkommen (Vergleichsseiten fuehren zwei Produkte).
    for _t in set(_typen) - {'Product'}:
        if _typen.count(_t) > 1:
            err(f"§A4: {_f} traegt {_typen.count(_t)}x {_t} — doppelte Schema-Bloecke auf "
                f"einer URL sind ein Rich-Results-Risiko (nicht-idempotenter Generator?)")

# Statische Hauptnavigation (§A2). Bis 30.09.2026 stand auf allen 109 Seiten nur
# <header id="site-header"></header>: ohne JavaScript hatte KEINE Seite eine Navigation,
# die zehn wichtigsten internen Links der Domain existierten fuer jeden nicht-JS-Crawler
# nicht. Gleiche Bauart wie die Footer-Luecke, eine Ebene hoeher und mit mehr SEO-Gewicht.
# Quelle der Linkliste bleibt das nav-Array in main.js; scripts/sync_header.py leitet das
# statische Markup daraus ab.
# Geprueft wird ZEICHENGLEICH gegen den Generator, nicht nur an den hrefs. Die erste
# Fassung verglich nur href="...": ein Nav-Label liess sich durch beliebigen Text
# ersetzen und der Trust-Strip ("Unabhaengig & herstellerneutral", "42 Modelle im
# Sortiment", "Datenstand September 2026") stand auf 109 Seiten voellig ungeprueft.
# Ein FEHLENDES header-Element fiel ebenfalls nicht auf, nur ein leeres -- Stubs werden
# wie beim Footer-Gate ueber http-equiv="refresh" abgegrenzt.
try:
    sys.path.insert(0, 'scripts')
    import sync_header as _sh
    _SOLL_HEADER = _sh.header_html(_sh.nav_aus_mainjs(), _sh.trust_aus_mainjs())
except Exception as _e:
    _SOLL_HEADER = None
    err(f"§A2: statischer Header nicht ableitbar ({type(_e).__name__}: {_e}) — ohne die "
        f"Quelle in main.js laesst sich die Navigation nicht pruefen")
if _SOLL_HEADER:
    for _f in pages:
        _h = open(_f, encoding='utf-8').read()
        if 'http-equiv="refresh"' in _h:
            continue
        _m = re.search(r'<header[^>]*id="site-header"[^>]*>(.*?)</header>', _h, re.S)
        if not _m:
            err(f"§A2: {_f} hat gar kein site-header-Element — ohne JavaScript keine "
                f"Navigation (python3 scripts/sync_header.py)")
            continue
        if not _m.group(1).strip():
            err(f"§A2: {_f} hat einen leeren site-header — ohne JavaScript keine "
                f"Navigation (python3 scripts/sync_header.py)")
        elif _m.group(1) != _SOLL_HEADER:
            err(f"§A2: {_f} weicht im site-header von scripts/sync_header.py ab — "
                f"'python3 scripts/sync_header.py' laufen lassen; steht die Abweichung "
                f"absichtlich dort, gehoert sie ins nav-Array in main.js")

# Cache-Busting fuer JEDES nachgeladene Asset. main.js traegt Impressum-, Datenschutz- und
# Affiliate-Hinweis; ohne Versionsparameter behalten wiederkehrende Besucher eine alte
# Fassung, bis ihr Browser-Cache ablaeuft. Der Parameter ist der Inhalts-Hash und muss zum
# aktuellen Dateiinhalt passen.
# Bis zum 30.09.2026 galt das NUR fuer main.js — eine Luecke derselben Bauart wie so viele
# in dieser Session: die Regel war richtig, ihr Geltungsbereich zu eng. style.css
# entscheidet, ob die Pflichtangaben lesbar sind, und finder.js / hub-render.js /
# produkte.js rendern Preise und Produktkarten. Eine veraltete Fassung davon zeigt alte
# Preise, also genau den Fehler, gegen den products.json als einzige Wahrheit gebaut ist.
import hashlib
_ASSETS = ['assets/css/style.css', 'assets/js/main.js', 'assets/js/finder.js',
           'assets/js/hub-render.js', 'assets/js/produkte.js']
_ASSET_HASH = {a: hashlib.sha256(open(a, 'rb').read()).hexdigest()[:8]
               for a in _ASSETS if os.path.exists(a)}
for _a in _ASSETS:
    if _a not in _ASSET_HASH:
        err(f"§D: {_a} ist eingeplant, existiert aber nicht — Liste in verify.py und "
            f"scripts/bump_asset_version.py nachziehen")
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    if 'http-equiv="refresh"' in _h:
        continue
    for _a, _hash in _ASSET_HASH.items():
        # ALLE Referenzen, nicht nur die erste: re.search haette eine zweite, veraltete
        # Einbindung hinter einer korrekten stumm durchgelassen.
        for _vm in re.finditer(re.escape('/' + _a) + r'(?:\?v=([0-9a-f]+))?(?=["\'])', _h):
            if _vm.group(1) != _hash:
                err(f"§D: {_f} laedt {_a} mit v={_vm.group(1) or 'ohne Version'}, "
                    f"der Inhalts-Hash ist {_hash} — "
                    f"'python3 scripts/bump_asset_version.py' oder die Version von Hand "
                    f"nachziehen")

# ---------- 6b4 · Bildebene (§A1/§A5/§C3, 30.09.2026) ----------
# Die Bildebene hatte bis zur elften Pruefrunde KEIN Gate. Zweimal hintereinander lief
# deshalb ein fremdes Produkt als unseres: ein ASUS-ROG-Werbebild als GameSir-Testsieger
# und ein weisser Backbone One als EasySMX M15 (inklusive og:image, twitter:image und
# Product-Schema). Ein Skript kann kein Bild lesen - aber es kann pruefen, WOHER ein Bild
# kommt und ob die Zuordnung zu products.json stimmt. Alles andere bleibt Augenarbeit.
_PRESSEBILDER = 'assets/img/products-real/'
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    if _PRESSEBILDER in _h:
        err(f"§C3: {_f} bindet ein Bild aus {_PRESSEBILDER} ein — dort liegen "
            f"Hersteller-Pressebilder ohne dokumentierte Lizenz")

# Produktbilder muessen aus products.json stammen. Ein lokales Bild unter
# assets/img/products/ ist nicht verifizierbar und war genau einmal vergeben - an das
# falsche Produkt.
for _p in items:
    for _feld, _wert in [('img', _p.get('img'))] + \
                        [('gallery', g) for g in (_p.get('gallery') or [])]:
        if _wert and not _wert.startswith('https://m.media-amazon.com/'):
            err(f"§A5: {_p['slug']} fuehrt {_feld} \"{_wert}\" — Produktbilder muessen "
                f"aus dem Amazon-Katalog der eigenen ASIN stammen, lokale Dateien sind "
                f"nicht belegbar")

# data-img und cta-photo muessen zum Produkt derselben Karte passen.
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    for _m in re.finditer(r'<[^>]*data-product="([^"]+)"[^>]*data-img="([^"]*)"[^>]*>'
                          r'|<[^>]*data-img="([^"]*)"[^>]*data-product="([^"]+)"[^>]*>', _h):
        _slug = _m.group(1) or _m.group(4)
        _bild = _m.group(2) or _m.group(3)
        _p = next((x for x in items if x.get('slug') == _slug), None)
        if _p and _bild and _bild not in [_p.get('img')] + (_p.get('gallery') or []):
            err(f"§A1: {_f} data-img fuer {_slug} zeigt auf ein Bild, das nicht zu diesem "
                f"Produkt gehoert")

# width/height muessen das echte Seitenverhaeltnis treffen. Getippte Masse veralten still,
# wenn die Bildquelle wechselt: am 30.09.2026 standen an vier Amazon-Bildern noch die Masse
# der frueher dort liegenden lokalen Pressebilder, darunter 1920x700 an einem 1500x1500
# grossen Banner -- ein sichtbarer Layout-Sprung beim Nachladen. Belegt sind die Masse in
# assets/data/bildmasse.json, gefuellt von scripts/mess_bilder.py; so bleibt dieses Gate
# offline lauffaehig.
# WAS DIESES GATE NICHT KANN: Es beweist "HTML passt zum Belegstand", nicht "Belegstand
# passt zu den echten Bildern" -- dafuer misst 'python3 scripts/mess_bilder.py --check'
# jedes Bild live nach. Ohne diesen Hinweis liest der naechste Durchgang Gruen als
# "Masse sind geprueft".
# Geprueft wird das VERHAELTNIS, nicht die absolute Groesse: /assets/img/autor-yg.svg liegt
# in 112x112 vor und steht bewusst mit 56x56 im Markup (Retina-Asset, halb ausgespielt).
# Das ist korrekt; falsch waere erst eine andere Bildform.
_MASSE_DATEI = 'assets/data/bildmasse.json'
if not os.path.exists(_MASSE_DATEI):
    err(f"§A1: {_MASSE_DATEI} fehlt — ohne belegte Pixelmasse laesst sich kein "
        f"width/height pruefen (python3 scripts/mess_bilder.py)")
else:
    _masse = json.load(open(_MASSE_DATEI, encoding='utf-8'))
    for _f in pages:
        _h = open(_f, encoding='utf-8').read()
        for _tag in re.findall(r'<img[^>]*>', _h):
            _w = re.search(r'\bwidth="(\d+)"', _tag)
            _hh = re.search(r'\bheight="(\d+)"', _tag)
            _src = re.search(r'src="([^"]+)"', _tag)
            if not (_w and _hh and _src):
                continue
            _echt = _masse.get(_src.group(1))
            if _echt is None:
                err(f"§A1: {_f} deklariert Masse fuer \"{_src.group(1)}\", das Bild steht "
                    f"aber nicht in {_MASSE_DATEI} (python3 scripts/mess_bilder.py)")
            else:
                _dw, _dh = int(_w.group(1)), int(_hh.group(1))
                _soll, _ist = _echt[0] / _echt[1], _dw / _dh
                if abs(_soll - _ist) / _soll > 0.01:
                    err(f"§A1: {_f} deklariert {_dw}x{_dh} fuer \"{_src.group(1)}\" "
                        f"(Verhaeltnis {_ist:.2f}), das Bild ist aber {_echt[0]}x{_echt[1]} "
                        f"(Verhaeltnis {_soll:.2f}) — das springt beim Nachladen")

# ---------- 6c · Detailseiten gegen ihren Generator (§A1, 30.09.2026) ----------
# Der Prosa-Text der /produkte/-Seiten (verdict, desc, pros, cons, faqs) stammt aus
# scripts/gen_content.py und wird an FÜNF Stellen ausgespielt: meta/og/twitter
# description, Product-Schema "description", sichtbare Einordnungs-Box, Fließtext und
# Stärken/Schwächen-Liste. Am 30.09. lagen dort 62 veraltete Werte, obwohl das
# Wert-Audit grün meldete: Es prüft die strukturierten Felder, nicht den Text.
# Regex-Prüfungen auf diesen Text wären ein Fass ohne Boden. Stattdessen der harte
# Vergleich: Die Datei muss zeichengleich sein mit dem, was der Generator baut.
# Das fängt beides ab — veralteten Text in gen_content.py (er erscheint nach einem
# Regen an allen fünf Stellen und fällt im Audit auf) und Handkorrekturen an der
# Datei, die der nächste Regen stumm überschreiben würde.
try:
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    from gen_pages import generierte_seiten
    from gen_longtail import generierte_seiten as longtail_seiten
    _n_gen = 0
    # Beide Generatoren: gen_pages fuer die 29 Produktseiten, gen_longtail fuer die
    # 10 Datenblaetter. Letzterer hatte keinen __main__-Guard, ein Import schrieb also
    # Dateien - deshalb gab es fuer diese zehn Seiten bisher keinen Zeichenvergleich.
    # Welcher Generator die Seite baut, entscheidet die Reparaturanweisung. Bis 01.10.
    # nannte die Meldung fuer ALLE 39 Seiten 'gen_pages.py --regen <slug>' und
    # 'gen_content.py' — fuer die 10 Longtail-Seiten gibt dieser Befehl "0 Seiten
    # regeneriert" aus und der Fehler bleibt stehen. Eine Reparaturanweisung, die ins
    # Leere zeigt, ist schlimmer als keine: man fuehrt sie aus und glaubt, es sei erledigt.
    _quelle = {}
    for _t in generierte_seiten():
        _quelle[_t[0]] = ('python3 scripts/gen_pages.py --regen ' + _t[0],
                          'scripts/gen_content.py')
    for _t in longtail_seiten():
        _quelle[_t[0]] = ('python3 scripts/gen_longtail.py',
                          'assets/data/longtail.json')
    for _slug, _pfad, _soll in list(generierte_seiten()) + list(longtail_seiten()):
        _n_gen += 1
        if not os.path.exists(_pfad):
            err(f"§A1: {_pfad} fehlt, der Generator kennt das Produkt aber")
            continue
        if open(_pfad, encoding='utf-8').read() != _soll:
            _befehl, _ursprung = _quelle.get(
                _slug, ('python3 scripts/gen_pages.py --regen ' + _slug, 'scripts/gen_content.py'))
            err(f"§A1: produkte/{_slug}/ weicht vom Generator ab — '{_befehl}' und die "
                f"Ursache in {_ursprung} beheben, nicht in der HTML-Datei")
    if _n_gen == 0:
        err("§A1: der Generator liefert keine Detailseiten — Import oder CONTENT-Dict kaputt")
    # Offenlegen, was dieses Gate NICHT abdeckt. Ohne diese Zeilen liest sich Gruen als
    # Vollstaendigkeit, und genau in der ungedeckten Flaeche sass der X2s-Fehler, der
    # vier Pruefrunden ueberlebt hat.
    #   - 13 Review-Seiten unter /controller/<plattform>/<slug>-review/: handgepflegt,
    #     kein Zeichenvergleich. Werte pruefen sync_product_values und audit_prosa.
    #   - Die 10 Longtail-Datenblaetter sind seit der achten Runde MIT abgedeckt:
    #     gen_longtail.py hat jetzt einen __main__-Guard und generierte_seiten().
    _handgepflegt = [p['slug'] for p in items
                     if (p.get('detail') or '') and not (p['detail']).startswith('/produkte/')]
    # Verwaiste Detailseiten: Seite liegt unter /produkte/, kein Generator baut sie und
    # products.json kennt den Slug nicht. Entsteht, wenn ein Produkt aus dem Datenkern
    # entfernt wird und die Seite live stehen bleibt — dann zeigt sie dauerhaft Werte,
    # die keine Quelle mehr hat. Die Liste wurde bisher berechnet und nie benutzt.
    # Gebaut wird aus ZWEI Quellen: products.json ueber gen_pages und longtail.json ueber
    # gen_longtail. Die erste Fassung dieses Gates kannte nur die erste und meldete prompt
    # alle 10 Longtail-Seiten als verwaist — ein Gate, das beim ersten Lauf zehn
    # Fehlalarme erzeugt, hat die Quellenlage nicht verstanden, nicht das Repo.
    # Aus dem, was die Generatoren tatsaechlich LIEFERN, nicht aus dem detail-Feld.
    # detail ist eine Behauptung von products.json; gen_pages verlangt zusaetzlich einen
    # CONTENT-Eintrag. Fehlt der, baut KEIN Generator die Seite, sie faellt stumm aus dem
    # Zeichenvergleich — und das Gate schwieg, waehrend seine eigene Meldung woertlich
    # behauptete, genau das zu pruefen. Wieder ein Proxy statt der Messung.
    _gebaut = {os.path.relpath(_t[1], ROOT).replace(os.sep, '/')
               for _t in list(generierte_seiten()) + list(longtail_seiten())}
    _verwaist = [x for x in glob.glob('produkte/*/index.html') if x not in _gebaut]
    for _v in _verwaist:
        err(f"§A1: {_v} ist verwaist — weder gen_pages (products.json) noch gen_longtail "
            f"(longtail.json) baut diese Seite; ihre Werte haben keine Quelle mehr")
    if len(_handgepflegt) != 13:
        warn(f"§A1: Generator-Abgleich deckt {_n_gen} Seiten; ohne Zeichenvergleich sind "
             f"{len(_handgepflegt)} handgepflegte Review-Seiten (zuletzt 13) — "
             f"Stand in STATUS nachziehen")
except Exception as _e:
    # Dieses except umschliesst den gesamten Abschnitt 6c: Zeichenvergleich aller 39
    # Generator-Seiten, Verwaisten-Gate und die _handgepflegt-Warnung. Faellt hier etwas
    # aus, fallen ALLE diese Pruefungen aus — und die alte Meldung nannte keine einzige
    # davon. Am 01.10. hat ein KeyError im Longtail-Generator genau so 40 Pruefungen
    # unsichtbar gemacht. Die Meldung sagt jetzt, was verloren ging.
    err(f"§A1: Generator-Abgleich abgebrochen ({type(_e).__name__}: {_e}) — damit sind "
        f"der Zeichenvergleich ALLER generierten Seiten, das Verwaisten-Gate und die "
        f"Zaehlung der handgepflegten Seiten in diesem Lauf NICHT gelaufen. Erst diesen "
        f"Abbruch beheben, dann dem Rest des Laufs trauen.")

# §A6: Jedes Produkt unter 3,8 Sternen braucht eine sichtbare Warnung statt Kaufempfehlung,
# und keins ab 3,8 darf noch eine Nicht-Empfehlung tragen. Am 30.09. fehlte die Warnung bei
# vier von sechs schwachen Produkten, während der MGPXPRO mit 4,3 Sternen noch "keine
# Kaufempfehlung" trug — eine handgepflegte Warnung altert in beide Richtungen.
# Eine Warnung, die zählt: der generierte Kasten oder eine ausdrückliche Nicht-Empfehlung.
_WARNUNG = re.compile(r'unter unserer Empfehlungsschwelle|keine (?:uneingeschränkte )?Kaufempfehlung'
                      r'|sprechen keine Kaufempfehlung aus|raten wir ab|zur Notlösung')
# Eine Nicht-Empfehlung, die auf einer starken Seite nichts zu suchen hat. Bewusst enger
# als _WARNUNG: "liegt genau auf unserer Empfehlungsschwelle" ist bei 3,8 korrekt und
# darf nicht als Nicht-Empfehlung gelesen werden.
_ABRATEN = re.compile(r'keine (?:uneingeschränkte )?Kaufempfehlung|sprechen keine Kaufempfehlung aus'
                      r'|raten wir ab|zur Notlösung|unter unserer Empfehlungsschwelle')
for _p in items:
    _bw = next((v for k, v in _p.get('specs', []) if k.startswith('Bew')), None)
    _m = re.match(r'([\d,]+)\s*\(([\d.]+)\)', _bw or '')
    _d = _p.get('detail') or ''
    if not _m or not _d:
        continue
    _f = _d.lstrip('/') + 'index.html'
    if not os.path.exists(_f):
        continue
    _html = open(_f, encoding='utf-8').read()
    _stern = float(_m.group(1).replace(',', '.'))
    if _stern < A6_SCHWELLE and not _WARNUNG.search(_html):
        err(f"§A6: {_f} zeigt {_m.group(1)} Sterne, aber keine Warnung "
            f"(Schwelle {A6_SCHWELLE})")
    if _stern >= A6_SCHWELLE and _ABRATEN.search(_html):
        err(f"§A6: {_f} rät vom Produkt ab, liegt mit {_m.group(1)} Sternen aber auf oder "
            f"über der Schwelle — Bewertung ist gestiegen, Text nicht nachgezogen")

# ---------- 7 · Widerlegte Aussagen dürfen nicht zurückkehren (§A5/§A6, 30.09.2026) ----------
# Diese Formulierungen standen im Bestandstext, wurden gegen products.json bzw. gegen
# unsere eigenen Review-Seiten widerlegt und korrigiert. Sie stehen teils in Bestand-FAQs,
# die gen_brand_sections.py ins FAQPage-Schema rendert, ohne sie selbst zu erzeugen:
# eine Handkorrektur dort ist verlierbar. Am 30.09. ist genau das passiert (der Fix
# "doppelt so teure" ging durch ein git checkout verloren und fiel erst im dritten
# Prüflauf auf). Diese Invariante fängt jede Rückkehr maschinell ab.
# Die Strings sind bewusst eng gefasst: Sie müssen die widerlegte Aussage treffen und
# dürfen legitime Formulierungen nicht blockieren. "Bluetooth-Gamepads" allein wäre zu
# breit (die Tablet-Seiten empfehlen Bluetooth-Gamepads völlig zu Recht), "Nur der Kishi
# Ultra" ebenso (er ist tatsächlich der einzige mit Klinke und Passthrough).
VERBOTEN = [
    ("doppelt so teure V3 Pro", "marken/razer/index.html",
     "der Preisabstand ist kein Faktor zwei; die konkrete Prozentzahl steht im Text und folgt products.json"),
    ("genauso gut bewertet wie der", "marken/razer/index.html",
     "Amazon-Abgleich 30.09.: der V3 (4,4) steht besser da als der V3 Pro (4,2), nicht gleichauf"),
    ("V3 und V3 Pro sind für Smartphones ausgelegt", "marken/razer/index.html",
     "Amazon-Abgleich 30.09.: der V3 Pro führt Tablets bis 8 Zoll ausdrücklich, nur der V3 nicht"),
    ("läuft an Android, PC und Switch", "marken/8bitdo/index.html",
     "die Ultimate-2C-Review sagt ausdrücklich 'Windows-PC + Android (nicht Switch)'"),
    ("MFi-fähige Gamepads", "marken/8bitdo/index.html",
     "iOS-Eignung der 8BitDo-Modelle ist strittig (products.json gegen Review-Seite), siehe Befund in STATUS"),
    ("Modelle sind Bluetooth-Gamepads", "marken/8bitdo/index.html",
     "Verbindungsart des Ultimate 2C ist strittig (products.json 'Bluetooth' gegen Review 'Wired')"),
    ("Modelle sind klassische Bluetooth-Gamepads", "marken/8bitdo/index.html",
     "dieselbe strittige Verbindungsart, Variante im Bestandstext"),
    ("weder Bluetooth noch iPhone", "marken/gamesir/index.html",
     "der iPhone-Ausschluss des X3 Pro ist nicht belegt (products.json führt worksOn ios)"),
    ("weder Bluetooth noch iOS", "marken/gamesir/index.html",
     "dieselbe Aussage, andere Schreibweise — genau diese Variante ist am 30.09. einmal durchgerutscht"),
    # Der Ultimate 2C: products.json sagt "USB (kabelgebunden)" und worksOn [android,
    # universal], die eigene Review sagt "Kabelgebunden (nicht kabellos)", "(nicht Switch)"
    # und "Kein iOS-Support". Trotzdem stand er am 30.09. auf sechs Seiten als
    # Bluetooth-Gamepad fuer iPhone, zwei davon in FAQPage-Schemas.
    ("Bluetooth-Gamepad wie den 8BitDo Ultimate 2C", "mehrere Seiten",
     "der Ultimate 2C ist kabelgebunden (products.json: USB), kein Bluetooth-Gamepad"),
    ("Bluetooth-Gamepad: Modelle wie der 8BitDo Ultimate 2C", "mehrere Seiten",
     "der Ultimate 2C ist kabelgebunden und laeuft laut worksOn nicht an iOS"),
    ("Bluetooth-Standalone-Controller wie der 8BitDo Ultimate 2C", "mehrere Seiten",
     "der Ultimate 2C ist kabelgebunden"),
    # Footer- und Header-Claims aus main.js, am 30.09. als unbelegt entfernt. Sie standen
    # auf JEDER Seite und haben sich als Selbstbeschreibung angefuehlt, nicht als Aussage,
    # die jemand pruefen muesste. Genau deshalb gehoeren sie hierher.
    ("Bestpreis-Links", "assets/js/main.js",
     "wir verlinken ausschliesslich Amazon, vergleichen keine Haendlerpreise"),
    ("Direkt zum günstigsten Händler", "assets/js/main.js",
     "es gibt nur einen Haendler im Link (Amazon), also auch keinen guenstigsten"),
    ("Offizieller Amazon-Partner", "assets/js/main.js",
     "die Teilnahme am PartnerNet ist kein offizieller Partnerstatus; korrekt ist "
     "'Teilnehmer am Amazon-PartnerNet'"),
    ("Preise & Specs laufend geprüft", "assets/js/main.js",
     "geprueft wird beim Amazon-Abgleich, nicht laufend — der Datenstand steht im Footer"),
    ("100+ Controller getestet", "assets/js/main.js",
     "das Sortiment umfasst 42 Modelle; die Zahl wird aus products.json abgeleitet"),
    # Alt-Texte, die ein Bild beschrieben, das so nicht existiert (elfte Pruefrunde).
    ("TMR-Thumbsticks im Detail", "index.html",
     "das Bild dahinter war ein Razer-Werbebanner mit Person auf dem Sofa, keine "
     "Stick-Nahaufnahme"),
    # Die drei Razer-Bild-IDs standen hier kurzzeitig auf der Sperrliste. Yasin hat am
    # 30.09. entschieden: Galerien bleiben wie sie sind, Banner werden nicht einzeln
    # geprueft. Die Sperre ist deshalb raus. Was bleibt: falsche Alt-Texte (oben) und die
    # Regel, dass Product.image nur das Amazon-Hauptbild fuehrt -- dort liest Google DAS
    # Produktbild, und das ist eine andere Frage als die sichtbare Galerie.
    ("Tessen Controller in den Händen beim Spielen", "asus-rog-tessen-review",
     "das Bild zeigt den Controller freigestellt auf Weiss, ohne Haende und ohne Handy"),
    # Sticks-Vergleich G8 Galileo gegen Kishi V3: widerspricht der eigenen Tabelle
    # (beide driftfrei) und dem eigenen Artikel hall-effect-vs-tmr ("Auf dem Datenblatt
    # gewinnt TMR").
    ("bessere Sticks (Hall-Effect)", "mehrere Seiten",
     "beide Modelle haben driftfreie Sticks; laut eigenem Artikel liegt TMR auf dem "
     "Datenblatt sogar vorn"),
    ("günstiger und hat die besseren Sticks", "razer-kishi-v3-review",
     "dieselbe widerlegte Aussage im Kurz-Urteil"),
    ("den direkten Duell", "vergleich/backbone-one-vs-gamesir-g8",
     "Duell ist saechlich: 'das direkte Duell'"),
]
# REPOWEIT statt pro Datei. Die Bindung an EINE Datei hat am 30.09. vier Befunde
# überleben lassen: Dieselbe widerlegte Aussage über den Ultimate 2C stand unverändert
# auf sechs weiteren Seiten, zwei davon in FAQPage-Schemas. Eine widerlegte Aussage ist
# überall widerlegt, nicht nur dort, wo sie zuerst auffiel.
for _s, _hinweis, _grund in VERBOTEN:
    for _f in _zu_pruefen:
        if _s in open(_f, encoding='utf-8').read():
            err(f"WIDERLEGT: \"{_s}\" steht in {_f} — {_grund}")

# (Die frühere Einzelfall-Prüfung für 8bitdo-ultimate-mobile steht nicht mehr hier:
# Sie prüfte die ANWESENHEIT des richtigen Werts in EINER Datei, direkt unter dem
# Kommentar, der genau das verbietet. Abgedeckt ist der Fall längst durch den
# Generator-Abgleich (6c) und das Fließtext-Audit, beide repoweit.)

# ---------- 8 · Datenabgeleitete Superlative nachrechnen (§A6, 30.09.2026) ----------
# Mehrere Claims und Texte behaupten Spitzen- oder Alleinstellungen, die sich aus
# products.json berechnen lassen. Der Amazon-Abgleich vom 30.09. hat fuenf davon
# stumm gekippt, obwohl jede einzelne Zahl im Text belegt war. Diese Invariante
# rechnet sie bei jedem Lauf neu.
def _bew(p):
    for k, v in p.get('specs', []):
        if k.startswith('Bew'):
            m = re.match(r'([\d,]+)\s*\(([\d.]+)\)', v)
            if m:
                return float(m.group(1).replace(',', '.')), int(m.group(2).replace('.', ''))
    return None, None

def _preis(p):
    m = re.search(r'(\d+)', p.get('price', ''))
    return int(m.group(1)) if m else None

_ctrl = [p for p in items if p.get('type') == 'controller' and _bew(p)[0]]
_zub = [p for p in items if p.get('type') != 'controller' and _bew(p)[1]]
_kuehler = [p for p in items if 'ühler' in p.get('name', '') or 'Cooler' in p.get('name', '')]
_gs = [p for p in items if p.get('brand') == 'GameSir']
_razer = [p for p in items if p.get('brand') == 'Razer' and _bew(p)[0]]

def _behauptung(bedingung, text):
    if not bedingung:
        err(f"SUPERLATIV gekippt (§A6): {text}")

# Die Aussagen stehen so in den Claims und auf den Marken-Seiten.
_behauptung(max(_razer, key=lambda p: _bew(p)[0])['slug'] == 'razer-kishi-v3',
            '"der bestbewertete Razer" gilt nicht mehr fuer den Kishi V3')
_behauptung(max(_zub, key=lambda p: _bew(p)[1])['slug'] == 'risoka-finger-sleeves',
            '"unser meistbewertetes Zubehoer" gilt nicht mehr fuer die RISOKA Sleeves')
_behauptung(min(_ctrl, key=lambda p: _bew(p)[0])['slug'] == 'turtle-beach-atom',
            '"am schwaechsten bewerteter Controller" gilt nicht mehr fuer den Turtle Beach Atom')
_behauptung(min(_kuehler, key=lambda p: _bew(p)[0])['slug'] == 'razer-phone-cooler',
            '"schwaechste Bewertung im Kuehler-Segment" gilt nicht mehr fuer den Razer Phone Cooler')
_dual = [p for p in _gs if 'BT' in dict(p['specs']).get('Verb.', '') and 'USB' in dict(p['specs']).get('Verb.', '')]
_behauptung(len(_dual) == 1 and _dual[0]['slug'] == 'gamesir-g8-plus',
            '"der einzige GameSir mit BT und USB-C" gilt nicht mehr fuer den G8 Plus')
_tab = {p['slug'] for p in items if 'tablet' in (p.get('worksOn') or [])}
_behauptung('gamesir-g8-plus' in _tab and 'razer-kishi-v3' not in _tab,
            'die Tablet-Zuordnung im Razer- oder GameSir-Text passt nicht mehr zu worksOn')
# Titel und Description von blog/guenstige-handy-controller nennen den Einstiegspreis
# fuer Hall-Effect-Sticks. Er stand dort bei 20 EUR, als der Ultimate 2C noch so viel
# kostete, und wurde beim Abgleich stumm falsch.
_hall = [p for p in items
         if 'Hall' in dict(p.get('specs') or {}).get('Sticks', '')
         and re.search(r'(\d+)', (p.get('price') or ''))]
if _hall:
    _guenstigster = min(_hall, key=lambda p: int(re.search(r'(\d+)', p['price'].replace('.', '')).group(1)))
    _preis_hall = re.search(r'(\d+)', _guenstigster['price'].replace('.', '')).group(1)
    # REPOWEIT auf ABWESENHEIT des falschen Werts pruefen, nicht auf Anwesenheit des
    # richtigen an EINER Stelle. Am 30.09. stand "Hall-Effect ab 20 Euro" auf vier
    # weiteren Seiten, eine davon im FAQPage-Schema, waehrend die gebundene Seite
    # laengst korrigiert war. Schwellenaussagen wie "ab 20 Euro" faengt keine
    # Preisregel, weil sie zu keinem Produkt gehoeren - nur diese Invariante.
    # Schreibweisen per grep aus dem Bestand gesammelt, nicht erfunden: Hall-Effect (435x),
    # Hall-Effekt (19x), Hall-Sensorik (17x), Hall-Sensor/-en (14x), driftfrei* (111x),
    # Drift-Schutz (5x). "Hall-Effekt" mit k und das grossgeschriebene "Driftfreie"
    # fehlten und schalteten die Invariante fuer diese Stellen still ab.
    _falsch = [str(x) for x in range(5, int(_preis_hall))]
    # Vollstaendig gegrept, nicht ergaenzt: Hall-Effect 443x, Hall-Sticks 98x,
    # Driftfreie 54x, driftfrei* 64x, Hall-Effekt 21x, Hall-Sensorik 18x,
    # Hall-Trigger 10x, Hall-Sensor/-en 15x, Drift-Schutz 5x, Hall-Technik 4x.
    # "Hall-Sticks" mit 98 Vorkommen hat in der letzten Runde gefehlt.
    _HALLWORT = (r'Hall[- ]?Effe[ck]t\w*|Halleffekt\w*|Hall[- ](?:Sensor|Stick|Trigger|Technik)\w*'
                 r'|drift[- ]?frei\w*|Drift[- ]Schutz')
    _muster = re.compile(r'(?:' + _HALLWORT + r')[^.!?]{0,90}?'
                         r'\b(?:ab|für|schon für|bereits ab)\s*(?:etwa |rund |ca\. )?('
                         + '|'.join(_falsch) + r')(?:,-)?\s*[ -]?(?:€|Euro|EUR)(?!\s*(?:mehr|weniger|Aufpreis|Aufschlag))'
                         r'|\b(?:ab|für|schon für|bereits ab)\s*(?:etwa |rund |ca\. )?('
                         + '|'.join(_falsch) + r')(?:,-)?\s*[ -]?(?:€|Euro|EUR)(?!\s*(?:mehr|weniger|Aufpreis|Aufschlag))'
                         r'[^.!?]{0,90}?(?:' + _HALLWORT + r')', re.I)
    # Eingerueckt: Die Schleife stand ausserhalb ihres Guards und lief in einen
    # NameError, sobald kein Hall-Produkt gefunden wurde - alles danach lief nie.
    for _f in _zu_pruefen:
        for _mm in _muster.finditer(open(_f, encoding='utf-8').read()):
            err(f"SUPERLATIV gekippt (§A6): {_f} verspricht Hall-Effect ab "
                f"{_mm.group(1) or _mm.group(2)} EUR, guenstigster Hall-Controller ist "
                f"{_guenstigster['slug']} mit {_preis_hall} EUR")

# marken/razer nennt den Preisabstand V3 -> V3 Pro als Prozentzahl. Prozentaussagen
# entgehen jeder Wertpruefung, weil die Zahl in keinem Produkt steht: Sie ist erst aus
# zwei Preisen berechenbar. Nach dem Abgleich kippen sie stumm.
_p_v3 = next((p for p in items if p['slug'] == 'razer-kishi-v3'), None)
_p_v3p = next((p for p in items if p['slug'] == 'razer-kishi-v3-pro'), None)
if _p_v3 and _p_v3p:
    _a = int(re.search(r'(\d+)', _p_v3['price'].replace('.', '')).group(1))
    _b = int(re.search(r'(\d+)', _p_v3p['price'].replace('.', '')).group(1))
    _prozent = round((_b - _a) / _a * 100)
    _rf = 'marken/razer/index.html'
    if os.path.exists(_rf):
        _rh = open(_rf, encoding='utf-8').read()
        for _pm in re.finditer(r'rund (\d+) Prozent teurere', _rh):
            if int(_pm.group(1)) != _prozent:
                err(f"SUPERLATIV gekippt (§A6): {_rf} nennt {_pm.group(1)} Prozent Aufpreis "
                    f"V3 -> V3 Pro, aus products.json sind es {_prozent} Prozent")

_v3, _v3p = next(p for p in items if p['slug'] == 'razer-kishi-v3'), next(p for p in items if p['slug'] == 'razer-kishi-v3-pro')
_behauptung(_bew(_v3)[0] >= _bew(_v3p)[0],
            '"der Mehrpreis kostet Zufriedenheit" gilt nicht mehr: der V3 Pro liegt jetzt vorn')

# ---------- Ergebnis ----------
print(f"Geprüft: {len(pages)} Seiten · {schema_count} JSON-LD-Blöcke · {len(items)} Produkte")
for w in WARN: print(f"  WARN  {w}")
if ERRORS:
    for e in ERRORS: print(f"  FEHLER {e}")
    print(f"\n❌ ROT — {len(ERRORS)} Fehler, {len(WARN)} Warnungen")
    sys.exit(1)
print(f"\n✅ GRÜN — 0 Fehler, {len(WARN)} Warnungen")
sys.exit(0)
