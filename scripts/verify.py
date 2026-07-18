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
if os.path.isdir('ratgeber'): err("ZOMBIE: /ratgeber/ existiert wieder (§B2) — muss gelöscht bleiben")

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

# ---------- Ergebnis ----------
print(f"Geprüft: {len(pages)} Seiten · {schema_count} JSON-LD-Blöcke · {len(items)} Produkte")
for w in WARN: print(f"  WARN  {w}")
if ERRORS:
    for e in ERRORS: print(f"  FEHLER {e}")
    print(f"\n❌ ROT — {len(ERRORS)} Fehler, {len(WARN)} Warnungen")
    sys.exit(1)
print(f"\n✅ GRÜN — 0 Fehler, {len(WARN)} Warnungen")
sys.exit(0)
