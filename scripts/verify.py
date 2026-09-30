#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SPC Verify-Suite (P-7). Pflicht-Gate vor jedem "fertig". Exit 0 = grün, 1 = Befunde.
Prüft: Invarianten, products.json-Integrität, JSON-LD, interne Links, Sitemap, No-JS-Statik."""
import json, os, re, sys, glob
import xml.dom.minidom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
ERRORS, WARN = [], []
def err(msg): ERRORS.append(msg)
def warn(msg): WARN.append(msg)

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
    slugs, asins = set(), set()
    for i in items:
        for field in ['slug', 'asin', 'name', 'brand', 'type', 'platform', 'price', 'detail']:
            if not i.get(field): err(f"products.json {i.get('slug', i.get('asin','?'))}: Feld '{field}' leer (§A1)")
        if i['slug'] in slugs: err(f"Slug doppelt: {i['slug']}")
        if i['asin'] in asins: err(f"ASIN doppelt: {i['asin']}")
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
                    if o.get('@type') == 'Product' and not any(k in o for k in ('offers', 'review', 'aggregateRating')):
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
     "Kishi V3 Pro kostet 149 statt 93 Euro, also rund 60 Prozent mehr, nicht das Doppelte"),
    ("V3 und V3 Pro sind für Smartphones ausgelegt", "marken/razer/index.html",
     "beide führen das iPad mini laut eigener Review in der Kompatibilitätsliste"),
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
]
for _s, _f, _grund in VERBOTEN:
    if os.path.exists(_f) and _s in open(_f, encoding='utf-8').read():
        err(f"WIDERLEGT: \"{_s}\" steht wieder in {_f} — {_grund}")

# Ratings im HTML folgen products.json, statt gegen einen festen Wert zu prüfen: Ein
# fixer String würde rot, sobald Amazon sich ändert und der preis-loop korrekt nachzieht.
for _slug, _f in [('8bitdo-ultimate-mobile', 'produkte/8bitdo-ultimate-mobile/index.html')]:
    _p = next((x for x in items if x.get('slug') == _slug), None)
    if _p and os.path.exists(_f):
        _bew = next((v for k, v in _p.get('specs', []) if k.startswith('Bew')), None)
        if _bew:
            _m = re.match(r'([\d,]+)\s*\(([\d.]+)\)', _bew)
            if _m:
                _html = open(_f, encoding='utf-8').read()
                _stern, _anz = _m.group(1), _m.group(2)
                if f'{_stern} Sterne' not in _html:
                    err(f"§A1: {_f} zeigt nicht die {_stern} Sterne aus products.json")
                if _anz.replace('.', '') not in _html and _anz not in _html:
                    err(f"§A1: {_f} zeigt nicht die {_anz} Bewertungen aus products.json")

# ---------- Ergebnis ----------
print(f"Geprüft: {len(pages)} Seiten · {schema_count} JSON-LD-Blöcke · {len(items)} Produkte")
for w in WARN: print(f"  WARN  {w}")
if ERRORS:
    for e in ERRORS: print(f"  FEHLER {e}")
    print(f"\n❌ ROT — {len(ERRORS)} Fehler, {len(WARN)} Warnungen")
    sys.exit(1)
print(f"\n✅ GRÜN — 0 Fehler, {len(WARN)} Warnungen")
sys.exit(0)
