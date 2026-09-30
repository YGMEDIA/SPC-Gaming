#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_product_values.py — zieht Produktwerte aus products.json ins HTML nach.

Ergaenzt sync_new_products.py: Jenes rendert Karten auf den drei Plattform-Hubs
und /produkte/ neu, dieses findet die restlichen Stellen im gesamten Repo:
Karten auf Marken-, Geschenk- und Themenseiten, Bewertungs-Strings in Prosa und
Schemas, Produktnamen und Claims.

Arbeitsweise:
  · Karten werden ueber `data-product="<slug>"` gefunden; innerhalb der Karte
    werden Preis-Zeile und Bewertungs-Spec gegen products.json gesetzt.
  · Bewertungs-Strings der Form "4,5 (854)" sind produktweit eindeutig genug,
    um sie global zu ersetzen, wenn der alte Wert bekannt ist.
  · Namen und Claims werden nur ersetzt, wenn der alte Wert explizit uebergeben
    wird (--rename), damit nichts versehentlich getroffen wird.

Aufruf:
  python3 scripts/sync_product_values.py --check     nur berichten
  python3 scripts/sync_product_values.py             schreiben
  python3 scripts/sync_product_values.py --rename alt.json   zusaetzlich Namen/Claims

Die --rename-Datei ist {slug: {"name": [alt, neu], "claim": [alt, neu],
"rating": [alt, neu]}} und wird pro Preis-Welle einmal geschrieben.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECK = '--check' in sys.argv

SKIP_DIRS = {'.git', 'brain', 'assets', 'node_modules', 'scripts', '.github'}

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_hubs import esc   # gleiche Escaping-Regel wie der Karten-Generator


def load_products():
    with open(os.path.join(ROOT, 'assets', 'data', 'products.json'), encoding='utf-8') as f:
        d = json.load(f)
    return d['products'] if isinstance(d, dict) and 'products' in d else d


def pages():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith('.')]
        for fn in filenames:
            if fn.endswith('.html'):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def spec(p, key):
    for k, v in p.get('specs', []):
        if k.startswith(key):
            return v
    return None



def karten_bloecke(html):
    """Alle Produktkarten als (slug, start, ende) ab dem oeffnenden <article>.

    Wichtig: NICHT ab data-product scannen. In 29 Karten steht das Attribut erst
    im Kauf-Button, also hinter Claim und Preis; ein Scan ab dort laesst genau die
    Felder aus, die gesynct werden sollen.
    """
    out = []
    for m in re.finditer(r'<article class="pcard[^"]*"', html):
        ende = html.find('</article>', m.end())
        if ende == -1:
            continue
        dm = re.search(r'data-product="([^"]+)"', html[m.start():ende])
        if dm:
            out.append((dm.group(1), m.start(), ende))
    return out

def sync_cards(html, products):
    """Preis und ALLE Spec-Chips jeder Produktkarte gegen products.json setzen.

    Frueher wurde nur der Bewertungs-Chip gezogen. Am 30.09. blieben dadurch
    `Verb. Bluetooth`-Chips beim 8BitDo 2C stehen, obwohl der Claim daneben schon
    "kabelgebunden" sagte: die Karte widersprach sich selbst.
    """
    hits = 0
    by = {p['slug']: p for p in products}
    for slug, start, end in reversed(karten_bloecke(html)):
        p = by.get(slug)
        if p:
            block = html[start:end]
            neu = block
            # Preis in der price-row
            neu = re.sub(r'(<span class="price">)[^<]*',
                         lambda mm: mm.group(1) + p['price'], neu)
            # Claim (B2, 30.09.): Die Karten-Beschreibung folgt products.json. Sieben
            # Produkte hatten gar keinen Claim, ihre Karten zeigten keine Beschreibung.
            if p.get('claim'):
                if '<p class="pcard-claim">' in neu:
                    neu = re.sub(r'(<p class="pcard-claim">)[^<]*(</p>)',
                                 lambda mm: mm.group(1) + esc(p['claim']) + mm.group(2), neu)
                else:
                    # Element fehlt ganz: hinter dem Produktnamen einsetzen. Betraf am
                    # 30.09. sieben Karten, die dadurch voellig ohne Beschreibung dastanden.
                    neu = re.sub(r'(</h[23]>)',
                                 lambda mm: mm.group(1) + f'\n          <p class="pcard-claim">{esc(p["claim"])}</p>',
                                 neu, count=1)
            # Alle Spec-Chips. Das \s* gehoert NICHT in die Gruppe, sonst steht am
            # Ende ein doppeltes Leerzeichen und der Lauf "aendert" korrekte Karten.
            for k, v in p.get('specs', []):
                neu = re.sub(r'(<span class="k">' + re.escape(k) + r'</span>)\s*[^<]*',
                             lambda mm, v=v: mm.group(1) + ' ' + v, neu)
            if neu != block:
                html = html[:start] + neu + html[end:]
                hits += 1
    return html, hits



def sync_leads(html, products, path_rel):
    """Hero-Untertitel der Detailseiten gegen products.json setzen.

    gen_pages.py rendert den Claim dort ein zweites Mal. Diese Stelle liegt
    ausserhalb jeder Produktkarte und wird von sync_cards nicht erreicht.
    """
    hits = 0
    for p in products:
        if not p.get('detail') or p['detail'].strip('/') != path_rel.rsplit('/', 1)[0]:
            continue
        m = re.search(r'(<p class="lead">)(.*?)(</p>)', html, re.S)
        if m and re.sub(r'<[^>]+>', '', m.group(2)).strip() != p['claim']:
            html = html[:m.start()] + m.group(1) + esc(p['claim']) + m.group(3) + html[m.end():]
            hits += 1
    return html, hits


def audit_leads(products, fehler):
    """Lead-Drift melden. Gleiche Fehlerklasse wie die Karten, andere Renderstelle."""
    for p in products:
        if not p.get('detail'):
            continue
        f = os.path.join(ROOT, p['detail'].strip('/'), 'index.html')
        if not os.path.exists(f):
            continue
        m = re.search(r'<p class="lead">(.*?)</p>', open(f, encoding='utf-8').read(), re.S)
        if m and re.sub(r'<[^>]+>', '', m.group(1)).strip() != p['claim']:
            rel = os.path.relpath(f, ROOT)
            fehler.append(f'{rel}: Hero-Lead weicht vom Claim in products.json ab')

def audit(products, mit_text=True):
    """§A1-Audit ueber das ganze Repo: Karten, Schema-Werte und Hub-Zugehoerigkeit
    gegen products.json. Findet, was zwischen den Generator-Markern NICHT geprueft
    wird. Gibt eine Liste von Meldungen zurueck, leer heisst deckungsgleich."""
    by = {p['slug']: p for p in products}
    fehler = []
    hinweise = []

    def preis_zahl(s):
        m = re.search(r'(\d+)', s or '')
        return m.group(1) if m else None

    for path in pages():
        rel = os.path.relpath(path, ROOT)
        html = open(path, encoding='utf-8').read()

        # 1. Karten: Preis und Spec-Chips
        for slug, start, end in karten_bloecke(html):
            p = by.get(slug)
            if p is None:
                # Verwaiste Karte: Der Slug existiert in products.json nicht. Solche
                # Karten wurden am 30.09. von Sync UND Audit uebersprungen und trugen
                # noch Claims und Preise von vor Monaten.
                fehler.append(f'{rel}: Karte "{slug}" hat keinen Eintrag in products.json')
            if p:
                block = html[start:end]
                pm = re.search(r'<span class="price">([^<]*)', block)
                if pm and pm.group(1).strip() != p['price']:
                    fehler.append(f'{rel}: Karte {slug} zeigt Preis "{pm.group(1).strip()}", products.json sagt "{p["price"]}"')
                cl = re.search(r'<p class="pcard-claim">([^<]*)</p>', block)
                if cl and p.get('claim') and cl.group(1).strip() != esc(p['claim']):
                    fehler.append(f'{rel}: Karte {slug} zeigt einen anderen Claim als products.json')
                for k, v in p.get('specs', []):
                    cm = re.search(r'<span class="k">' + re.escape(k) + r'</span>\s*([^<]*)', block)
                    if cm and cm.group(1).strip() != v:
                        fehler.append(f'{rel}: Karte {slug} zeigt {k} "{cm.group(1).strip()}", products.json sagt "{v}"')

        # 2. Schema-Werte auf Produkt-/Review-Seiten
        for sm in re.finditer(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', html, re.S):
            try:
                obj = json.loads(sm.group(1))
            except json.JSONDecodeError:
                continue
            if obj.get('@type') != 'Product':
                continue
            # Produkt ueber die ASIN im Kaufbutton derselben Seite bestimmen
            asins = set(re.findall(r'data-asin="([^"]+)"', html))
            treffer = [p for p in products if p['asin'] in asins and p['name'] in html]
            if len(treffer) != 1:
                continue
            p = treffer[0]
            offers = obj.get('offers') or {}
            if isinstance(offers, dict) and offers.get('price'):
                if str(offers['price']).replace('.00', '') != preis_zahl(p['price']):
                    fehler.append(f'{rel}: Schema-Preis "{offers["price"]}", products.json sagt "{preis_zahl(p["price"])}"')
            agg = obj.get('aggregateRating') or {}
            bew = spec(p, 'Bew')
            if agg and bew:
                mm = re.match(r'([\d,]+)\s*\(([\d.]+)\)', bew)
                if mm:
                    soll_r = mm.group(1).replace(',', '.')
                    soll_c = mm.group(2).replace('.', '')
                    if agg.get('ratingValue') and str(agg['ratingValue']) != soll_r:
                        fehler.append(f'{rel}: Schema ratingValue "{agg["ratingValue"]}", products.json sagt "{soll_r}"')
                    if agg.get('reviewCount') and str(agg['reviewCount']).replace('.', '') != soll_c:
                        fehler.append(f'{rel}: Schema reviewCount "{agg["reviewCount"]}", products.json sagt "{soll_c}"')
                    if '.' in str(agg.get('reviewCount', '')):
                        fehler.append(f'{rel}: Schema reviewCount "{agg["reviewCount"]}" enthält einen Tausenderpunkt und wird als Kommazahl gelesen')

    if mit_text:
        # 2b. Fliesstext, Vergleichstabellen, Cross-Sell-Kacheln und llms.txt.
        # Der dritte grosse Traeger von Produktwerten neben Karte und Schema: Jeder
        # Euro-Betrag und jeder Sternwert im Umkreis eines Produktnamens wird gegen
        # products.json gehalten. Hier lagen am 30.09. 59 veraltete Stellen.
        namen = sorted(((p['name'], p) for p in products), key=lambda t: -len(t[0]))
        for path in pages() + [os.path.join(ROOT, 'llms.txt')]:
            if not os.path.exists(path):
                continue
            rel = os.path.relpath(path, ROOT)
            roh = open(path, encoding='utf-8').read()
            # Karten und JSON-LD ausblenden, die pruefen die Abschnitte 1 und 2
            text = re.sub(r'<article class="pcard.*?</article>', ' ', roh, flags=re.S)
            text = re.sub(r'<script type="application/ld\+json">.*?</script>', ' ', text, flags=re.S)
            for name, p in namen:
                soll_preis = preis_zahl(p['price'])
                bew = spec(p, 'Bew')
                mm = re.match(r'([\d,]+)\s*\(([\d.]+)\)', bew or '')
                soll_stern, soll_anz = (mm.group(1), mm.group(2)) if mm else (None, None)
                for treffer in re.finditer(re.escape(name), text):
                    umfeld = text[treffer.end():treffer.end() + 60]
                    # Ein weiterer Produktname im Umfeld macht die Zuordnung unsicher
                    if any(n2 in umfeld for n2, _ in namen if n2 != name and name not in n2):
                        continue
                    for pm in re.finditer(r'(\d{1,4})\s*(?:€|Euro)', umfeld):
                        if pm.group(1) != soll_preis:
                            hinweise.append(f'{rel}: "{name}" gefolgt von "{pm.group(1)} €", '
                                          f'products.json sagt "{soll_preis} €"')
                    if soll_stern:
                        for sm2 in re.finditer(r'(\d,\d)\s*(?:von 5|/ ?5|Sterne)', umfeld):
                            if sm2.group(1) != soll_stern:
                                hinweise.append(f'{rel}: "{name}" gefolgt von "{sm2.group(1)} Sterne", '
                                              f'products.json sagt "{soll_stern}"')
                    if soll_anz:
                        for am in re.finditer(r'([\d.]{3,6})\s*(?:Amazon-)?Bewertungen', umfeld):
                            if am.group(1).replace('.', '') != soll_anz.replace('.', ''):
                                hinweise.append(f'{rel}: "{name}" gefolgt von "{am.group(1)} Bewertungen", '
                                              f'products.json sagt "{soll_anz}"')

    audit_leads(products, fehler)

    # 3. Hub-Zugehoerigkeit gegen worksOn
    HUBS = {'controller/ios/index.html': 'ios', 'controller/android/index.html': 'android',
            'controller/tablet/index.html': 'tablet', 'controller/mini-gamepad/index.html': 'mini'}
    for rel, flag in HUBS.items():
        path = os.path.join(ROOT, rel)
        if not os.path.exists(path):
            continue
        html = open(path, encoding='utf-8').read()
        # data-product steht je nach Seite am <article> ODER erst im Kaufbutton
        # darin (Tablet-Hub). Deshalb ueber die Kartenbloecke gehen.
        ist = set()
        for km in re.finditer(r'<article class="pcard[^"]*"', html):
            ende = html.find('</article>', km.end())
            dm = re.search(r'data-product="([^"]+)"', html[km.start():ende])
            if dm:
                ist.add(dm.group(1))
        soll = {p['slug'] for p in products if flag in p.get('worksOn', [])}
        for s in sorted(ist - soll):
            fehler.append(f'{rel}: {s} steht im Hub, hat aber kein "{flag}" in worksOn')
        for s in sorted(soll - ist):
            fehler.append(f'{rel}: {s} hat "{flag}" in worksOn, fehlt aber im Hub')
    return fehler, hinweise


def sync_ratings(html, mapping):
    """Bekannte alte Bewertungs-Strings global ersetzen (auch in Schemas und Prosa)."""
    hits = 0
    for alt, neu in mapping.items():
        if alt in html:
            hits += html.count(alt)
            html = html.replace(alt, neu)
    return html, hits


def main():
    products = load_products()
    if '--audit' in sys.argv:
        fehler, hinweise = audit(products)
        for f in fehler:
            print(f'  {f}')
        print(f'\n{len(fehler)} harte Abweichung(en) zwischen HTML und products.json')
        if hinweise and '--text' in sys.argv:
            print(f'\nDazu {len(hinweise)} Fließtext-Hinweis(e) — enthalten Nachbarzahlen,')
            print('also einzeln prüfen, nicht blind ersetzen:')
            for h in hinweise:
                print(f'  ? {h}')
        elif hinweise:
            print(f'{len(hinweise)} Fließtext-Hinweis(e) unterdrückt (mit --text anzeigen)')
        return 1 if fehler else 0
    rename = {}
    if '--rename' in sys.argv:
        with open(sys.argv[sys.argv.index('--rename') + 1], encoding='utf-8') as f:
            rename = json.load(f)

    rating_map = {}
    text_map = {}
    for slug, felder in rename.items():
        for feld, (alt, neu) in felder.items():
            (rating_map if feld == 'rating' else text_map)[alt] = neu

    gesamt = {'karten': 0, 'ratings': 0, 'texte': 0, 'dateien': 0}
    for path in pages():
        with open(path, encoding='utf-8') as f:
            original = f.read()
        html, k = sync_cards(original, products)
        html, kl = sync_leads(html, products, os.path.relpath(path, ROOT))
        k += kl
        html, r = sync_ratings(html, rating_map)
        html, t = sync_ratings(html, text_map)
        if html != original:
            gesamt['karten'] += k
            gesamt['ratings'] += r
            gesamt['texte'] += t
            gesamt['dateien'] += 1
            rel = os.path.relpath(path, ROOT)
            print(f'  {rel:<52} Karten {k:>2} · Bewertungen {r:>2} · Texte {t:>2}')
            if not CHECK:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(html)

    verb = 'wären geändert' if CHECK else 'geändert'
    print(f"\n{gesamt['dateien']} Datei(en) {verb}: "
          f"{gesamt['karten']} Karten, {gesamt['ratings']} Bewertungen, {gesamt['texte']} Textstellen")
    return 0


if __name__ == '__main__':
    sys.exit(main())
