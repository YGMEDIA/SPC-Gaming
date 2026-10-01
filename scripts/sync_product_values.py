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
from schema_util import typen_von   # eine Definition fuer beide Skripte

# Reichweite EINES Spec-Chips, gemeinsam von Schreiber und Audit benutzt. Getrennte
# Muster sind am 30.09. zweimal auseinandergelaufen (erst beim Escaping, dann bei der
# Reichweite) -- beide Male war das Ergebnis: Audit gruen, Schreiber loescht still.
# Der Chip wird an seinem EIGENEN schliessenden </span> begrenzt, nicht ueber ein Muster,
# das Tags ueberspringt. Die Tag-Ueberspringen-Variante hat bei einem rohen "<" das
# schliessende </span> als Tag gelesen und geloescht -- derselbe Fehler, den der
# HTML-Parser macht, nur im Reparaturwerkzeug. Mit dieser Begrenzung ist der erfasste
# Bereich exakt der Chipinhalt, egal was darin steht, und der Schreiber stellt ihn
# vollstaendig wieder her statt halb.
# Struktur: <span class="spec-tag"><span class="k">LABEL</span> WERT</span>
# Geprueft: 466 Chips im Repo, keiner mit verschachteltem <span>.
# (?s), damit auch ein Chip erfasst wird, dessen Inhalt auf einer eigenen Zeile steht:
# ohne DOTALL fand das Muster ihn nicht, das Audit schwieg und der Schreiber reparierte
# ihn auch nicht. Zusaetzlich bricht der Inhalt an einem oeffnenden <span ab, damit ein
# fehlendes </span> nicht den NAECHSTEN Chip mitfrisst -- dann gibt es gar keinen Treffer,
# und genau das meldet der else-Zweig im Audit.
CHIP_REST = r'</span>\s*((?:(?!</span>|<span)[\s\S])*)</span>' 


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
                # ESCAPT schreiben, genau wie das Audit weiter unten gegen esc(v) prueft.
                # Roh geschrieben stand "Tablet/iPad <10mm" im Markup, das Audit erwartete
                # "&lt;10mm" und wurde nach einem Schreiblauf rot. Schlimmer: das Muster
                # [^<]* endete am eingeschleusten "<", der Rest blieb stehen und der Wert
                # wurde beim naechsten Lauf erneut davorgesetzt ("&lt;10mm&lt;10mm...").
                neu = re.sub(r'(<span class="k">' + re.escape(k) + r')' + CHIP_REST,
                             lambda mm, v=v: mm.group(1) + '</span> ' + esc(v) + '</span>', neu)
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


def sync_detail_felder(html, p):
    """Technik-Tabelle und CTA-Leiste der eigenen Detailseite gegen products.json."""
    hits = 0
    bew = spec(p, 'Bew')
    paare = [(r'(<tr>\s*<td[^>]*>Preis</td>\s*<td[^>]*>)[^<]*(</td>)', p['price'])]
    if bew:
        # products.json fuehrt "3,5 (649)", die Tabelle "3,5 / 5 (649 Bewertungen)"
        bm = re.match(r'([\d,]+)\s*\(([\d.]+)\)', bew)
        if bm:
            paare.append((r'(<tr>\s*<td[^>]*>(?:Amazon-)?Bewertung</td>\s*<td[^>]*>)[^<]*(</td>)',
                          f'{bm.group(1)} / 5 ({bm.group(2)} Bewertungen)'))
    # esc(), weil gen_pages.py dieselbe Zelle escapt schreibt. Zwei Schreiber derselben
    # Stelle mit verschiedenen Regeln sind am 30.09. schon zweimal auseinandergelaufen.
    for muster, wert in paare:
        neu, n = re.subn(muster, lambda m, w=wert: m.group(1) + esc(w) + m.group(2), html)
        html, hits = neu, hits + n
    neu, n = re.subn(r'(class="cta-price"[^>]*>)[^<]*',
                     lambda m: m.group(1) + esc(p['price']), html)
    html, hits = neu, hits + n
    return html, hits


def sync_kacheln(html, products):
    """Empfehlungskacheln (rc-price / cat-count) gegen products.json.

    Das Produkt wird ueber den href-Slug des umschliessenden <a> aufgeloest, NICHT
    ueber den Produktnamen. Der Namensabgleich hat am 30.09. vier redaktionelle
    Vergleichs-Untertitel vernichtet, weil ein Label wie "G8 Galileo vs. Kishi V3"
    auf einen Produktnamen ENDET. Praefixe waren nie das Risiko, Suffixe sind es.

    Ersetzt wird ausserdem nur der Preis-Teil der Zelle. Zellen wie
    "80 € · Testsieger" behalten ihren Zusatz, Zellen ohne Euro-Betrag
    ("Meistgeklickter Vergleich") werden gar nicht angefasst.
    """
    nach_detail = {}
    for p in products:
        if p.get('detail'):
            nach_detail[p['detail'].rstrip('/')] = p

    # <a href="/pfad/" ...> ... <div class="rc-price|cat-count">ZELLE
    muster = (r'<a href="([^"]+)"([^>]*)>(?=(?:(?!</a>).)*?'
              r'<div class="(?:rc-price|cat-count)">)')
    hits = 0
    out = []
    pos = 0
    for m in re.finditer(muster, html, re.S):
        ende = html.find('</a>', m.end())
        if ende == -1:
            continue
        p = nach_detail.get(m.group(1).rstrip('/'))
        if not p:
            continue
        block = html[m.start():ende]
        def zelle(mm, p=p):
            inhalt = mm.group(2)
            neu, n = re.subn(r'^(?:ca\.\s*|ab\s*)?[\d.,]+\s*€', p['price'], inhalt, count=1)
            return mm.group(1) + (neu if n else inhalt)
        neu_block = re.sub(r'(<div class="(?:rc-price|cat-count)">)([^<]*)', zelle, block)
        if neu_block != block:
            out.append(html[pos:m.start()]); out.append(neu_block)
            pos = ende
            hits += 1
    out.append(html[pos:])
    return ''.join(out), hits


def audit_detail_felder(products, fehler):
    """Technik-Tabelle, CTA-Leiste und Kacheln als HARTE Pruefung, nicht als Hinweis."""
    for p in products:
        if not p.get('detail'):
            continue
        f = os.path.join(ROOT, p['detail'].strip('/'), 'index.html')
        if not os.path.exists(f):
            continue
        html = open(f, encoding='utf-8').read()
        rel = os.path.relpath(f, ROOT)
        m = re.search(r'<tr>\s*<td[^>]*>Preis</td>\s*<td[^>]*>([^<]*)</td>', html)
        if m and m.group(1).strip() != p['price']:
            fehler.append(f'{rel}: Technik-Tabelle zeigt Preis "{m.group(1).strip()}", '
                          f'products.json sagt "{p["price"]}"')
        m = re.search(r'class="cta-price"[^>]*>([^<]*)', html)
        if m and m.group(1).strip() != p['price']:
            fehler.append(f'{rel}: CTA-Leiste zeigt "{m.group(1).strip()}", '
                          f'products.json sagt "{p["price"]}"')
        bew = spec(p, 'Bew')
        bm = re.match(r'([\d,]+)\s*\(([\d.]+)\)', bew or '')
        if bm:
            soll = f'{bm.group(1)} / 5 ({bm.group(2)} Bewertungen)'
            m = re.search(r'<tr>\s*<td[^>]*>(?:Amazon-)?Bewertung</td>\s*<td[^>]*>([^<]*)</td>', html)
            if m and m.group(1).strip() != soll:
                fehler.append(f'{rel}: Tabellen-Bewertung zeigt "{m.group(1).strip()}", '
                              f'products.json sagt "{soll}"')
    # Kacheln repoweit. Zuordnung ueber den href-Slug, nicht ueber den Produktnamen:
    # ein Label wie "G8 Galileo vs. Kishi V3" endet auf einen Produktnamen und
    # erzeugte namensbasiert sechs Fehlalarme. Geprueft wird nur der Preis-Teil der
    # Zelle, Zusaetze wie "80 € · Testsieger" sind redaktionell und zulaessig.
    nach_detail = {x['detail'].rstrip('/'): x for x in products if x.get('detail')}
    for path in pages():
        html = open(path, encoding='utf-8').read()
        rel = os.path.relpath(path, ROOT)
        for m in re.finditer(r'<a href="([^"]+)"[^>]*>', html):
            ende = html.find('</a>', m.end())
            if ende == -1:
                continue
            p = nach_detail.get(m.group(1).rstrip('/'))
            if not p:
                continue
            for zm in re.finditer(r'<div class="(?:rc-price|cat-count)">([^<]*)',
                                  html[m.start():ende]):
                inhalt = zm.group(1).strip()
                pm = re.match(r'(?:ca\.\s*|ab\s*)?[\d.,]+\s*€', inhalt)
                if pm and pm.group(0).strip() != p['price']:
                    fehler.append(f'{rel}: Kachel zu {p["slug"]} zeigt "{pm.group(0).strip()}", '
                                  f'products.json sagt "{p["price"]}"')


def vergleich_produkte(html, products):
    """Die beiden Produkte einer vs-table ueber die Tabellenkoepfe aufloesen.

    Kopfzeilen mit <td> zaehlen mit: Zwei Vergleichsseiten schreiben ihren Kopf so, und
    die starre <th>-Bedingung hat sie stumm uebersprungen. Ein vertauschtes Preispaar
    blieb dort unentdeckt.
    """
    kopf = re.search(r'<tr>\s*<t[hd][^>]*>\s*Merkmal\s*</t[hd]>.*?</tr>', html, re.S)
    if not kopf:
        return None
    spalten = [re.sub(r'<[^>]+>', '', x).strip()
               for x in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', kopf.group(0), re.S)][1:]
    treffer = []
    for sp in spalten:
        kandidaten = [x for x in products if x['name'] and x['name'] in sp]
        treffer.append(max(kandidaten, key=lambda x: len(x['name'])) if kandidaten else None)
    return treffer if len(treffer) == 2 and all(treffer) else None


def sync_vergleich(html, products):
    """Preis- und Bewertungszeile der vs-table gegen products.json.

    Nur die WERTE, nicht die winner/loser-Markierung: welche Seite gewinnt, ist
    eine redaktionelle Aussage und wird separat geprueft. Am 30.09. hatte sich
    genau diese Markierung durch gefallene Preise umgekehrt.
    """
    paar = vergleich_produkte(html, products)
    if not paar:
        return html, 0
    hits = 0
    for zeile, holen in [('Preis', lambda p: p['price']),
                         ('(?:Amazon-)?Bewertung', None)]:
        m = re.search(r'(<tr>\s*<td[^>]*>' + zeile + r'</td>)(.*?)(</tr>)', html, re.S)
        if not m:
            continue
        zellen = re.findall(r'<td[^>]*>.*?</td>', m.group(2), re.S)
        if len(zellen) != 2:
            continue
        neu_zellen = []
        for zelle, prod in zip(zellen, paar):
            if holen:
                wert = holen(prod)
            else:
                bew = spec(prod, 'Bew')
                bm = re.match(r'([\d,]+)\s*\(([\d.]+)\)', bew or '')
                if not bm:
                    neu_zellen.append(zelle); continue
                wert = f'{bm.group(1)} / 5 ({bm.group(2)} Bewertungen)'
            # Markierungen (Haken, Zusatztext) erhalten, nur den Wert tauschen
            inhalt = re.search(r'<td[^>]*>(.*?)</td>', zelle, re.S).group(1)
            if holen:
                neu_inhalt = re.sub(r'(?:ca\.\s*)?[\d.,]+\s*€', wert, inhalt, count=1)
            else:
                neu_inhalt = re.sub(r'[\d,]+\s*/\s*5\s*\([\d.]+ Bewertungen\)', wert, inhalt, count=1)
            neu_zellen.append(zelle.replace(inhalt, neu_inhalt))
        neu = m.group(1) + ''.join(neu_zellen) + m.group(3)
        if neu != m.group(0):
            html = html[:m.start()] + neu + html[m.end():]
            hits += 1
    return html, hits


def audit_vergleich(fehler):
    """Zeigt die vs-table die Werte aus products.json, und stimmt die Markierung?"""
    products = load_products()
    for path in pages():
        rel = os.path.relpath(path, ROOT)
        if not rel.startswith('vergleich/'):
            continue
        html = open(path, encoding='utf-8').read()
        paar = vergleich_produkte(html, products)
        if not paar:
            continue
        m = re.search(r'<tr>\s*<td[^>]*>Preis</td>(.*?)</tr>', html, re.S)
        if not m:
            continue
        zellen = re.findall(r'<td[^>]*>.*?</td>', m.group(1), re.S)
        if len(zellen) != 2:
            continue
        for zelle, prod in zip(zellen, paar):
            pm = re.search(r'(?:ca\.\s*)?([\d.,]+)\s*€', zelle)
            if pm and pm.group(0).strip() != prod['price']:
                fehler.append(f'{rel}: Vergleichstabelle zeigt "{pm.group(0).strip()}" fuer '
                              f'{prod["slug"]}, products.json sagt "{prod["price"]}"')
        # Markierung gegen die echten Preise
        preise = [int(re.search(r'(\d+)', x['price']).group(1)) for x in paar]
        markiert = 0 if 'winner' in zellen[0] else (1 if 'winner' in zellen[1] else None)
        if markiert is not None and preise[0] != preise[1]:
            guenstiger = 0 if preise[0] < preise[1] else 1
            if markiert != guenstiger:
                fehler.append(f'{rel}: Preis-Sieger ist als {paar[markiert]["slug"]} markiert, '
                              f'guenstiger ist aber {paar[guenstiger]["slug"]} '
                              f'({preise[guenstiger]} statt {preise[markiert]} Euro)')

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
                    # DIESELBE Reichweite wie der Schreiber oben. Vorher endete das Audit am
                    # ersten "<", waehrend der Schreiber ueber Fremdtags hinweggreift:
                    # sichtbarer Zusatztext in einem Chip war damit fuer alle drei Gates
                    # unsichtbar UND wurde vom naechsten Sync-Lauf stumm geloescht.
                    # Gegen die ESCAPTE Fassung vergleichen, wie eine Zeile hoeher beim Claim:
                    # products.json haelt Klartext ("Tablet/iPad <10mm"), im HTML steht
                    # zwangslaeufig "&lt;10mm".
                    cm = re.search(r'<span class="k">' + re.escape(k) + CHIP_REST, block)
                    if cm:
                        # ROH vergleichen, nicht tag-normalisiert. Das Audit strich Tags
                        # vorher weg und verglich nur den Text — ein <strong> im Chip war
                        # damit unsichtbar, waehrend der Schreiber den ganzen Bereich
                        # ersetzt und es ersatzlos loescht. Also wieder "Audit gruen,
                        # Schreiber loescht still", die Fehlerklasse, die der Kommentar
                        # oben als behoben beschreibt. Schreiber und Audit teilen sich
                        # jetzt nicht nur das Muster, sondern auch die Vergleichsregel.
                        ist = cm.group(1).strip()
                        if ist != esc(v):
                            fehler.append(f'{rel}: Karte {slug} zeigt {k} "{ist}", '
                                          f'products.json sagt "{esc(v)}"')
                    elif re.search(r'<span class="k">' + re.escape(k) + r'</span>', block):
                        # Label steht da, der Chip laesst sich aber nicht abgrenzen --
                        # typischerweise fehlt das schliessende </span>. Vorher lief dieser
                        # Fall stumm durch, waehrend der Schreiber den naechsten Chip
                        # mitfrass. Heute 0x im Repo.
                        fehler.append(f'{rel}: Karte {slug} hat das Label {k}, der Chip '
                                      f'laesst sich aber nicht abgrenzen — entweder fehlt '
                                      f'das schliessende </span> oder im Chip steht ein '
                                      f'verschachteltes <span>. Beides muss von Hand '
                                      f'aufgeloest werden, der Sync kann es nicht '
                                      f'reparieren; der Wert bleibt ungeprueft')

        # 2. Schema-Werte auf Produkt-/Review-Seiten
        for sm in re.finditer(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', html, re.S):
            try:
                obj = json.loads(sm.group(1))
            except json.JSONDecodeError:
                continue
            # Rekursiv ueber @graph: Ein Block ohne eigenen @type haelt die Product-Knoten
            # in einer Liste. Die flache Pruefung liess genau die vier @graph-Seiten
            # ungeprueft (G8 Galileo, X5 Lite, Kishi V3, Backbone One 2. Gen) - dort
            # liefen ratingValue, reviewCount und offers/price frei durch alle Gates.
            for obj in (obj.get('@graph') if isinstance(obj.get('@graph'), list) else [obj]):
              # @type kann eine Liste sein. Der Stringvergleich liess sich mit
              # "@type": ["Product"] abschalten: Schema-Preis und -Bewertung liefen
              # dann ungeprueft durch.
              if not isinstance(obj, dict) or 'Product' not in typen_von(obj):
                continue
              # Reihenfolge: das detail-Feld aus products.json, erst dann die
              # data-asin der Seite. (Einen Pfad-Zweig wie in verify.py braucht es hier
              # nicht: die /produkte/-Seiten deckt dort der Generator-Zeichenvergleich ab.
              # Der Kommentar behauptete ihn trotzdem — nachgemessen ueber alle 125
              # Seiten: 0 Abweichungen zwischen beiden Aufloesungen.) Die ersten beiden sind
              # externe Identitaeten und lassen sich durch eine Aenderung an der Seite
              # nicht verschieben. Hing die Zuordnung allein an der ASIN, machte ein
              # zweiter, voellig legitimer Kauf-Button ("Alternative ansehen") diese
              # Pruefung zum Fehlalarm.
              # (Das uebrig gebliebene "if True:" ist raus; es hatte keine Wirkung und
              # tarnte, dass der Zweig darunter unbedingt laeuft.)
              rel_dir = os.path.dirname(rel.replace(os.sep, '/'))
              treffer = [x for x in products
                         if (x.get('detail') or '').strip('/')
                         and (x['detail']).strip('/') == rel_dir]
              if len(treffer) != 1:
                  asins = set(re.findall(r'data-asin="([^"]+)"', html))
                  treffer = [x for x in products
                             if x['asin'] in asins and x['name'] in html]
              if len(treffer) != 1:
                  # Stilles Ueberspringen war hier eine Luecke auf Zeit: sobald eine
                  # Vergleichsseite ein Product-Schema bekommt, liefen Preis und
                  # Bewertung darin ungeprueft durch. Jetzt wird es gemeldet.
                  fehler.append(f'{rel}: Product-Schema "{obj.get("name")}" laesst sich '
                                f'keinem Produkt eindeutig zuordnen (weder ueber detail '
                                f'noch ueber die data-asin) — Preis und Bewertung darin '
                                f'bleiben ungeprueft')
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
                        # {2,7}: Neun Produkte haben zweistellige Bewertungszahlen (16, 39, 40, 57, 64, 74,
                        # 85, 86, 87) und fielen durch die alte Untergrenze von drei Stellen.
                        for am in re.finditer(r'([\d.]{2,7})\s*(?:Amazon-)?Bewertungen', umfeld):
                            if am.group(1).replace('.', '') != soll_anz.replace('.', ''):
                                hinweise.append(f'{rel}: "{name}" gefolgt von "{am.group(1)} Bewertungen", '
                                              f'products.json sagt "{soll_anz}"')

    audit_leads(products, fehler)
    audit_detail_felder(products, fehler)
    audit_vergleich(fehler)

    # 3. Hub-Zugehoerigkeit gegen worksOn
    # Der Universal-Hub fehlte hier und wurde damit gegen nichts geprueft, obwohl er
    # dieselbe Zuordnung trifft wie die anderen vier.
    HUBS = {'controller/ios/index.html': 'ios', 'controller/android/index.html': 'android',
            'controller/universal/index.html': 'universal',
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
        # Nur Controller: Die /controller/-Hubs fuehren kein Zubehoer, obwohl Sleeves,
        # Trigger und Kuehler ebenfalls "universal" in worksOn tragen.
        soll = {p['slug'] for p in products
                if flag in p.get('worksOn', []) and p.get('type') == 'controller'}
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
        rel_dir = os.path.dirname(os.path.relpath(path, ROOT))
        eigen = next((x for x in products
                      if x.get('detail') and x['detail'].strip('/') == rel_dir), None)
        if eigen:
            html, kd = sync_detail_felder(html, eigen)
            k += kd
        html, kk = sync_kacheln(html, products)
        k += kk
        if os.path.relpath(path, ROOT).startswith('vergleich/'):
            html, kv = sync_vergleich(html, products)
            k += kv
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
