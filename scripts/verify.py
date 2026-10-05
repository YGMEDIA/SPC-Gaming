#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SPC Verify-Suite (P-7). Pflicht-Gate vor jedem "fertig". Exit 0 = grün, 1 = Befunde.
Prüft: Invarianten, products.json-Integrität, JSON-LD, interne Links, Sitemap, No-JS-Statik."""
import html
import json, os, re, sys, glob
# subprocess stand bisher nur als lokaler Import INNERHALB des audit_prosa-Guards. Fehlt
# diese Datei, war der Name danach undefiniert und jede weitere Nutzung ein NameError.
import subprocess
import xml.dom.minidom

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
# §A6-Schwelle: Produkte darunter bekommen eine Warnung statt einer Kaufempfehlung.
# Stand hier als Literal und war damit die dritte Kopie (dazu assets/js/finder.js und,
# beim Bau der Bestenlisten, fast eine vierte). Jetzt eine Quelle; die JS-Fassung wird
# weiter unten GEGEN diese geprueft, weil sie im Browser laeuft und nicht importieren kann.
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from produktdaten import A6_SCHWELLE
ERRORS, WARN = [], []
def err(msg): ERRORS.append(msg)
def warn(msg): WARN.append(msg)


def _klartext(_roh):
    """Sichtbarer Text einer Datei: ohne Kommentare, ohne Tags, Entities aufgeloest.

    EINE Funktion fuer alle Gates, die Aussagen im Text pruefen. Die Lehre dahinter hat
    sechzehn Pruefrunden gekostet: Jedes Gate, das rohes Markup liest, scheitert in beide
    Richtungen. `<strong>27</strong> der 28` macht richtigen Text rot, und derselbe Satz
    mit falscher Zahl plus Markup bleibt gruen. Ich habe das fuer die Mengensaetze geloest
    und danach fuenf weitere Gates gebaut, die es nicht uebernommen haben -- Pool-Satz,
    Fragenzahl, Abschnittszahlen, und zweimal in derselben Datei zwei Bildschirmseiten
    entfernt.

    Block-Grenzen werden zu einem Pilcrow, damit Satzanfaenge erkennbar bleiben: Nach einer
    Ueberschrift steht im Text kein Satzzeichen, und ein Muster, das einen Satzanfang
    verlangt, findet den Satz sonst nicht.

    `<script>`- und `<style>`-Inhalt faellt heraus. Die erste Fassung liess ihn stehen,
    und das ist in BEIDE Richtungen falsch: Ein Fehlalarm, weil eine JS-Zeichenkette in
    suche/index.html (`„' + q + '"`) wie schiefe Typografie aussah -- und, schwerer, ein
    Loch, weil jeder Anwesenheits-Anker dieses Pakets sich von einer Zeichenkette in einem
    Skript erfuellen laesst, waehrend die Seite den Satz nicht zeigt. Genau die Klasse,
    die in Runde 16 eine Kopie in llms.txt gedeckt hat.
    """
    _t = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', ' \u00b6 ', _roh, flags=re.S | re.I)
    _t = re.sub(r'<!--.*?-->', ' ', _t, flags=re.S)
    _t = re.sub(r'</?(?:p|li|td|th|h[1-6]|div|section|main|article|blockquote|dd|dt)\b'
                r'[^>]*>|<br\s*/?>', ' \u00b6 ', _t, flags=re.I)
    _t = html.unescape(re.sub(r'<[^>]*>', ' ', _t))
    # U+00A0 mitnormalisieren: `&nbsp;` wird von html.unescape zu einem geschuetzten
    # Leerzeichen, und `[ \t]+` hat es stehen gelassen. Zwei richtige Saetze wurden
    # dadurch rot (`3,8&nbsp;Sternen`, `Frage 1&nbsp;von&nbsp;3`), waehrend Muster mit
    # `\s+` an derselben Stelle gruen blieben -- dasselbe Gate, zwei Verhalten.
    return re.sub(r'[ \t\u00a0\u202f\u2009]+', ' ', _t.replace('\n', ' \u00b6 '))


def _jsonld_texte(_roh):
    """Die Zeichenketten-Werte aller JSON-LD-Bloecke, als Text.

    Warum eigens: `_klartext` entfernt `<script>`-Inhalt, und das ist richtig -- eine
    Zeichenkette in einem JS-Programm ist kein Seitentext, und solange sie mitgelesen
    wurde, liess sich jeder Anwesenheits-Anker von ihr erfuellen. Dieselbe Entfernung hat
    aber ein Gate stillgelegt: Die Abschnittszahlen stehen auch in `headline` und
    `description` des Article-Schemas, also in einem script-Block, und waren danach
    ungeprueft -- Runde 19 hat 9 Ursachen und 7 Stoerungsbilder ins Schema geschrieben,
    sichtbar blieben 5 und 4, und der Lauf blieb gruen.

    Der Unterschied, auf den es ankommt: JSON-LD ist AUSGELIEFERTER INHALT (Google liest
    es, und §A4 verlangt fuer jeden Schema-Wert eine sichtbare Entsprechung), ein
    beliebiger JS-String ist Programmtext. Deshalb kommen hier nur die Werte aus
    `application/ld+json` dazu, nicht der uebrige Skriptinhalt.
    """
    _aus = []
    # Beide Anfuehrungszeichen-Formen, wie `_ist_datenskript` (Hinweis R29).
    for _sm in re.finditer(r'<script[^>]+type\s*=\s*[\'"]application/ld\+json[\'"]'
                           r'[^>]*>(.*?)</script>', _roh, re.S | re.I):
        try:
            _obj = json.loads(_sm.group(1))
        except Exception:
            # Kaputtes JSON-LD meldet das Schema-Gate; hier faellt es nur aus.
            continue

        def _sammle(_o):
            if isinstance(_o, str):
                _aus.append(_o)
            elif isinstance(_o, dict):
                for _v in _o.values():
                    _sammle(_v)
            elif isinstance(_o, list):
                for _v in _o:
                    _sammle(_v)
        _sammle(_obj)
    return ' \u00b6 '.join(_aus)


def _ohne_kommentare(_quelle, _ist_js):
    """Quelltext ohne Kommentare. Auch ANHAENGENDE `//`-Kommentare.

    Die erste Fassung entfernte nur `//` am Zeilenanfang. Ein anhaengender Kommentar, der
    die Regel dokumentiert ("... // NICHT gtag('event', ...) benutzen"), wurde damit als
    Verstoss gemeldet -- genau die Klasse, fuer die diese Funktion gebaut wurde, einen
    Schritt daneben (R25). Das `(?<!:)` haelt `https://` heraus; eine vollstaendige
    JS-Tokenisierung waere hier der Regress, und ein `//` in einem String-Literal ist
    der benannte Rest.
    """
    if _ist_js:
        _q = re.sub(r'/\*.*?\*/', ' ', _quelle, flags=re.S)
        return re.sub(r'(?m)(?<!:)//.*$', ' ', _q)
    return re.sub(r'<!--.*?-->', ' ', _quelle, flags=re.S)


_JSON_TYPEN = ('application/ld+json', 'application/json', 'importmap',
               'speculationrules', 'application/schema+json')


def _ist_datenskript(_attrtext):
    """Traegt dieses <script> einen Daten-Typ? Dann ist sein Inhalt kein Code.

    Entscheidend ist der geparste `type`, nicht ein Substring: `data-json="1"`,
    `id="jsonld-helper"` und `class="json"` sind ausfuehrbare Skripte und liefen durch
    (R28). `type="text/JSONP"` ist ebenfalls Code.
    """
    _tm = re.search(r'\btype\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))', _attrtext,
                    re.I)
    if not _tm:
        return False      # ohne type ist es JavaScript
    _typ = (_tm.group(1) or _tm.group(2) or _tm.group(3) or '').strip().lower()
    return _typ in _JSON_TYPEN


def _metatexte(_roh):
    """Nur die DESCRIPTION-Metas: das ist der Ort, der Leser ueber Suchergebnisse erreicht.

    Gebraucht fuer Zusagen, die dort LEBEN (die Meta-Description der Finder-Seite). Fuer
    die gilt "sichtbar auf der Seite" nicht, aber auch nicht "irgendwo in der Datei": Sonst
    deckt ein JSON-LD-Wert sie, und genau das war Befund 6 aus Runde 20.

    Die erste Fassung nahm JEDEN content/alt/title/aria-label-Wert. R21 hat die Zusage aus
    description, og:description und twitter:description entfernt und in ein `title=` am
    Finder-Element gelegt: Der Anker blieb erfuellt, und die Zusage erreichte ueber
    Suchergebnisse niemanden mehr. Dasselbe Loch eine Ebene tiefer. Geprueft wird deshalb
    genau das Feld, um das es geht.
    """
    _aus = []
    for _m in re.finditer(r'<meta\b[^>]*>', _roh, re.I):
        _tag = _m.group(0)
        if not re.search(r'(?:name|property)\s*=\s*[\'"](?:description|og:description|'
                         r'twitter:description)[\'"]', _tag, re.I):
            continue
        # Einfache Anfuehrungszeichen mitlesen: im Repo sind 104 Attribute einfach gequotet, davon 101 class-Attribute,
        # und ein `content='...'` waere hier unsichtbar gewesen (R22, latent).
        _cm = re.search(r'content\s*=\s*(?:"([^"]*)"|\'([^\']*)\')', _tag)
        if _cm:
            _aus.append(html.unescape(_cm.group(1) or _cm.group(2) or ''))
    return ' \u00b6 '.join(_aus)


def _text_und_metas(_roh):
    """Sichtbarer Text PLUS Attributwerte PLUS JSON-LD-Werte.

    Eine Zusage kann in der Meta-Description stehen (die Finder-Seite macht genau das).
    `_klartext` entfernt Tags samt Attributen, also waere sie dort unsichtbar: Beim
    Umstellen des Fragenzahl-Gates auf Klartext ist genau diese Stelle rot geworden.
    Die JSON-LD-Werte kommen dazu, weil `_klartext` script-Bloecke entfernt und damit das
    Abschnittszahlen-Gate stillgelegt hatte (Begruendung in `_jsonld_texte`).
    """
    _attr = ' \u00b6 '.join(
        html.unescape(m.group(1))
        for m in re.finditer(r'(?:content|alt|title|aria-label)="([^"]*)"', _roh))
    return (_klartext(_roh) + ' \u00b6 ' + _attr + ' \u00b6 ' + _jsonld_texte(_roh))


sys.path.insert(0, os.path.join(ROOT, 'scripts'))
from schema_util import typen_von as _typen_von   # eine Definition fuer beide Skripte
from lesezeit import minuten as _lesezeit_minuten  # dito: Generator, Sync und Gate
from lesezeit import BYLINE as _lz_BYLINE, KARTE as _lz_KARTE
from lesezeit import karten as _lz_karten
from produktdaten import spec as _spec            # eine Leseregel fuer products.json
from produktdaten import spec_wie as _spec_wie    # (Docstring dort: warum nicht hier)
from produktdaten import spec_paare as _spec_paare
from produktdaten import preis_zahl as _preis_zahl
from produktdaten import bewertung as _bewertung, sterne_text as _sterne_text
from produktdaten import formfehler as _formfehler
# Namen bewusst eindeutig: `_txt`/`_liste` kollidieren mit lokalen Variablen
# in diesem Lauf (Zeile 344, 471, 1906) und wurden dadurch ueberschrieben --
# derselbe Fehler, den `_klartext` eine Runde vorher gemacht hat.
from produktdaten import text as _pfeld, liste as _pliste
from css_kaskade import wert as _css_wert, sichtbar as _css_sichtbar

def _gate(_skript, *_args, _grenze=180):
    """Ein Unter-Gate starten und NIE am Timeout sterben.

    Die Aufrufe standen mit `timeout=180` ohne `try` da: Ein `TimeoutExpired` haette
    verify.py mit Traceback beendet statt mit einem Befund -- und ein Gate, das abbricht,
    prueft alles dahinter nicht mehr. Genau diese Klasse hat die Robustheitsprobe fuer
    products.json schon zweimal gefunden.
    """
    try:
        return subprocess.run([sys.executable, 'scripts/' + _skript, *_args],
                              capture_output=True, text=True, timeout=_grenze)
    except subprocess.TimeoutExpired:
        err(f"{_skript} hat nach {_grenze} s nicht geantwortet — das Gate ist damit "
            f"ungeprueft, nicht gruen")
        class _R:
            returncode, stdout, stderr = 0, '', ''
        return _R()


# ---------- 1 · Invarianten ----------
for f in ['CNAME', '.nojekyll', 'llms.txt', 'robots.txt', 'sitemap.xml', 'assets/data/products.json']:
    if not os.path.exists(f): err(f"Invariante fehlt: {f}")
if os.path.exists('CNAME') and open('CNAME').read().strip() != 'smartphone-controller.com':
    err("CNAME-Inhalt falsch")
# `CLAUDE.md` liegt zweimal im Repo (Wurzel als Einstieg, `brain/` als Vault-Seite) und war
# bis zum 02.10.2026 bit-identisch. Dann habe ich die Pattern-Spanne nur in der Wurzel auf
# P-1…P-13 gezogen, und die Vault-Kopie behauptete weiter P-1…P-8 -- derselbe Fall, den
# `sync_footer.py` fuer den Pflicht-Footer loest ("bevor die fuenfte Kopie entsteht").
# Zwei Kopien ohne Gate divergieren; wer die eine pflegt, pflegt die andere mit.
if os.path.exists('brain/CLAUDE.md') and os.path.exists('CLAUDE.md'):
    _a = open('CLAUDE.md', encoding='utf-8').read()
    _b = open('brain/CLAUDE.md', encoding='utf-8').read()
    if _a != _b:
        import difflib as _dl
        _d = [x for x in _dl.unified_diff(_b.splitlines(), _a.splitlines(),
                                          'brain/CLAUDE.md', 'CLAUDE.md', lineterm='', n=0)
              if x[:1] in '+-' and x[:3] not in ('+++', '---')]
        err("CLAUDE.md und brain/CLAUDE.md sind auseinandergelaufen: "
            + ' | '.join(x[:110] for x in _d[:4]))
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
# 404.html gehoert dazu: GitHub Pages liefert sie unter jeder nicht existierenden URL, sie
# traegt also Kopf, Fuss, Pflichtangaben und Assets wie jede andere Seite. Ohne sie hier
# waere sie die einzige ausgelieferte HTML-Datei ohne Gate — und damit haette das
# Schliessen einer ungegateten Flaeche eine neue geoeffnet.
if os.path.exists('404.html'):
    pages.append('404.html')

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

# ---------- 2b · Formfehler in products.json ----------
# Die Leseregeln selbst stehen in produktdaten.py, geteilt mit kompat.py. Warum dort und
# nicht hier, steht im Docstring des Moduls: Beim Schliessen dieses Befundes habe ich hier
# erst eine eigene Fassung gebaut, obwohl kompat.py schon eine hatte -- die elfte Kopie,
# beim Aufraeumen der zehn. Der Pruefer hat genau diese Kopie gefunden.
for _m in _formfehler(items):
    err(_m)

# Eine Amazon-Produkt-URL, in allen Formen, die wirklich vorkommen. Gebraucht an zwei
# Stellen (statisches HTML und JS-Dateien), deshalb hier und nicht zweimal.
#   amazon.de/dp/B0...            die kurze Form
#   amazon.de/Produktname/dp/B0   die Form aus Adresszeile und SiteStripe "Full link"
#   amazon.de/-/en/dp/B0          die Sprachvariante
#   amazon.de/gp/product/B0       die alte Produktseite
#   amazon.de/gp/aw/d/B0          die mobile Form
#   amazon.de/exec/obidos/ASIN/   die sehr alte Form
#   amzn.to / amzn.eu             Kurzlinks, tragen ihr Tag unsichtbar
# NUR Produktpfade: Ein blosses `gp/` traf auch `gp/help/customer/display.html`, also den
# legitimen Link auf Amazons Datenschutzerklaerung in datenschutz/index.html -- der erste
# Lauf dieses Musters war genau dort rot. Das Gate soll Kauflinks finden, nicht jeden
# Amazon-Link.
_AMAZON_LINK = (r'amazon\.[a-z.]{2,6}/(?:[^"\'\s?]*/)*?'
                r'(?:dp|gp/product|gp/aw/d|exec/obidos)/'
                r'|amzn\.(?:to|eu)/')

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
    # Amazon nie hart verlinkt (außer JS baut sie) — im statischen HTML nur data-asin.
    # Das Muster hiess `amazon\.de/dp/` und verlangte `dp` DIREKT hinter der Domain. Die
    # Form, die Adresszeile und SiteStripe liefern, ist aber
    # `amazon.de/<Produktname>/dp/<ASIN>` -- die ging durch, mit richtigem Tag und ohne
    # data-asin (R26 gemessen, an dieser Stelle und am JS-Gate). _AMAZON_LINK deckt beide
    # Stellen, damit sie nicht wieder auseinanderlaufen.
    # DIESELBE Konstante auch in der Schleife. Vorher stand hier ein eigenes,
    # handgeschriebenes Hostmuster -- der Auslöser benutzte _AMAZON_LINK, die Pruefung
    # dahinter die alte Form. Vier Dinge liefen damit durch (R27, je gemessen):
    # `amzn.to` und `amzn.eu` (genau die Formen, deren Tag unsichtbar ist und die der
    # eigene Fehlertext als die gefaehrlichsten benennt), ein Zeilenumbruch nach `<a`,
    # und `AMAZON.DE` in Grossschreibung. re.S und re.I decken die letzten zwei.
    if re.search(_AMAZON_LINK, s, re.I):
        # erlaubt in Schema (offers.url) — prüfe nur echte <a href>
        # Beide Anfuehrungszeichen-Formen: `href='...'` fiel offen, weil der Ausloeser
        # ueber die ganze Seite feuerte und die Schleife danach kein Tag fand (R28).
        for _am2 in re.finditer(r'<a\s[^>]*href\s*=\s*(?:"[^"]*"|\'[^\']*\')[^>]*>',
                                s, re.S | re.I):
            _tag = _am2.group(0)
            if re.search(_AMAZON_LINK, _tag, re.I) and 'data-asin' not in _tag:
                err(f"Harter Amazon-Link ohne data-asin-Automation in {p} (§A3): "
                    f"{_tag[:100]}")
    # §A3 gilt auch fuer inline <script> einer Seite: Das JS-Gate liest nur
    # assets/js/*.js, das Statik-Gate nur <a href>. Eine Amazon-URL in einem
    # Seiten-Skript war von keinem der beiden erfasst (R27).
    # NUR ausfuehrbare Skripte. Ein `application/ld+json`-Block ist Daten, und dort ist
    # die Amazon-URL ausdruecklich erlaubt (`offers.url`) -- die erste Fassung dieses
    # Gates hat deshalb 30 Produktseiten gemeldet, alle zu Recht gruen.
    # Der TYPE wird geparst, nicht als Substring ueber alle Attribute gesucht. Die erste
    # Fassung schloss jedes <script> aus, dessen Attributtext irgendwo "json" enthielt --
    # vier ausfuehrbare Formen liefen damit durch (`data-json="1"`, `id="jsonld-helper"`,
    # `class="json"`, `type="text/JSONP"`), gemessen in R28.
    _inline = ' '.join(_m3.group(2) for _m3 in
                       re.finditer(r'<script\b(?![^>]*\bsrc=)([^>]*)>(.*?)</script>',
                                   s, re.S | re.I)
                       if not _ist_datenskript(_m3.group(1) or ''))
    _im = re.search(_AMAZON_LINK, _ohne_kommentare(_inline, True), re.I)
    if _im:
        err(f"§A3: {p} schreibt in einem inline <script> eine Amazon-URL "
            f"(\"{_im.group(0)}\") — Kauflinks entstehen ausschliesslich in "
            f"assets/js/main.js aus data-asin")

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
        # err statt warn: Eine indexierbare Seite, die nicht in der Sitemap steht,
        # wird schlechter gefunden — das ist ein Fehler, keine Randnotiz. Gemessen
        # vor der Umstellung: 0 Seiten betroffen, die Verschaerfung bricht nichts.
        if url not in locs:
            err(f"§B: Indexierbare Seite fehlt in der Sitemap: {url}")
except Exception as e:
    err(f"Sitemap: {e}")

# robots.txt inhaltlich (§B). Bis 01.10. wurde nur geprueft, DASS die Datei existiert.
# Ein versehentliches "Disallow: /" haette die komplette Domain aus dem Index genommen,
# und alle vier Gates waeren gruen geblieben — der teuerste denkbare Fehler mit der
# billigsten denkbaren Ursache.
if os.path.exists('robots.txt'):
    _rb = open('robots.txt', encoding='utf-8').read()
    # Nur der Block fuer "User-agent: *" zaehlt; die KI-Crawler-Bloecke duerfen eigene
    # Regeln haben.
    _bloecke = re.split(r'(?mi)^User-agent:', _rb)
    _stern = next((b for b in _bloecke if b.strip().startswith('*')), '')
    if not _stern:
        err("§B: robots.txt hat keinen Block fuer \"User-agent: *\"")
    _dis = re.findall(r'(?mi)^\s*Disallow:\s*(\S*)', _stern)
    if '/' in _dis:
        err("§B: robots.txt sperrt mit \"Disallow: /\" die komplette Domain")
    # Die Sitemap-Zeile muss auf unsere Sitemap zeigen.
    _smz = re.search(r'(?mi)^\s*Sitemap:\s*(\S+)', _rb)
    if not _smz:
        err("§B: robots.txt nennt keine Sitemap")
    elif _smz.group(1) != 'https://smartphone-controller.com/sitemap.xml':
        err(f"§B: robots.txt verweist auf die Sitemap {_smz.group(1)}, erwartet ist "
            f"https://smartphone-controller.com/sitemap.xml")
    # Keine URL der Sitemap darf von robots.txt gesperrt sein. Eine Seite anzubieten und
    # gleichzeitig das Crawlen zu verbieten ist ein Widerspruch, den Google meldet.
    if os.path.exists('sitemap.xml'):
        _locs2 = re.findall(r'<loc>([^<]+)</loc>', open('sitemap.xml', encoding='utf-8').read())
        for _u in _locs2:
            _pfad = _u.replace('https://smartphone-controller.com', '') or '/'
            for _d in _dis:
                if not _d:
                    continue
                if re.match('^' + re.escape(_d).replace(r'\*', '.*'), _pfad):
                    err(f"§B: sitemap.xml fuehrt {_pfad}, robots.txt sperrt es mit "
                        f"\"Disallow: {_d}\"")

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
    # Lief bis hierher ganz ohne `timeout`: ein Haenger haette verify.py unbegrenzt
    # blockiert, und ein Gate, das nicht endet, meldet auch nichts.
    _r = _gate('gen_brand_sections.py', '--check')
    if _r.returncode != 0:
        err(f"Marken-Hubs: gen_brand_sections.py --check schlägt fehl (§A1)\n"
            f"         {_r.stdout.strip().splitlines()[-1] if _r.stdout.strip() else _r.stderr.strip()[:200]}")
    elif 'wären geändert worden: keine' not in _r.stdout:
        _last = _r.stdout.strip().splitlines()[-1]
        err(f"Marken-Hubs sind nicht mehr deckungsgleich mit products.json (§A1). "
            f"Fix: python3 scripts/gen_brand_sections.py — {_last}")

else:
    err("scripts/gen_brand_sections.py fehlt — Marken-Hub-Invariante kann nicht prüfen")

# Die Preisfrage-Seite ist VOLLSTAENDIG gerechnet (Spanne, Median, Baender, Lesezeit) --
# und ihr `--check`-Modus existierte, wurde aber von keinem Gate aufgerufen. Drei
# Mutationen ("mittlere Preis 50 -> 70 €", "30 bis 190 -> 240 €", "28 -> 31 Controller")
# blieben damit gruen (R27). Die Absicherung lag nur in der Idempotenzprobe, und die ist
# ausdruecklich nicht in CI.
if os.path.exists('scripts/gen_preisfrage.py'):
    _rp = _gate('gen_preisfrage.py', '--check')
    if _rp.returncode != 0:
        _zeilen = (_rp.stdout + _rp.stderr).strip().splitlines()
        err(f"§A1: scripts/gen_preisfrage.py --check schlaegt fehl — die Preisfrage-Seite "
            f"weicht von dem ab, was aus products.json folgt. Fix: "
            f"'python3 scripts/gen_preisfrage.py'. {_zeilen[-1][:160] if _zeilen else ''}")
else:
    err('scripts/gen_preisfrage.py fehlt — die Preisfrage-Seite ist dann ungegatet')

# B6: Die vier Bestenlisten waren die SIEBTE Renderstelle fuer Produktdaten und die
# einzige ungegatete -- sechs andere sind am 30.09. geschlossen worden. Gemessen am
# 04.10.: 14 Spec-Chips mit Werten, die products.json nicht fuehrt, null sichtbare
# Bewertungen auf vier Seiten, deren Zweck eine Rangfolge ist, und eine Sortier-Regel,
# die "Ergonomie" nennt -- ein Kriterium, das es im Datenkern nicht gibt.
if os.path.exists('scripts/gen_bestenliste.py'):
    _rb = _gate('gen_bestenliste.py', '--check')
    if _rb.returncode != 0:
        _zb = (_rb.stdout + _rb.stderr).strip().splitlines()
        err(f"§A1: scripts/gen_bestenliste.py --check schlaegt fehl — eine Bestenliste "
            f"weicht von dem ab, was aus products.json folgt. Fix: "
            f"'python3 scripts/gen_bestenliste.py'. {_zb[-1][:160] if _zb else ''}")
else:
    err('scripts/gen_bestenliste.py fehlt — die vier Bestenlisten sind dann ungegatet')

# Ein "Mehr erfahren" einer Produktkarte darf nicht auf die eigene Seite zeigen. Gefunden
# beim Umbau auf die Karten-Regel: Auf /zubehoer/handy-kuehler/ zeigten ZWEI von drei
# Karten dorthin statt auf die Produktseite. Die beiden Kuehler hingen damit an keinem
# Kategorie-Hub, und die erste B7-Messung hat das verdeckt statt es zu finden -- sie zaehlte
# jeden Link, auch den aus einem Vergleichssatz, und fand deshalb "jedes Produkt haengt an
# mindestens einer Uebersicht".
# Nur Karten MIT data-product: Eine Karte ohne (etwa das ROG Phone 9 Pro auf
# /gaming-phones/) hat kein bekanntes Ziel; das ist ein eigener, redaktioneller Befund.
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    _u = '/' if _f == 'index.html' else '/' + os.path.dirname(_f).replace(os.sep, '/') + '/'
    _m = re.search(r'<main\b.*?</main>', _h, re.S)
    if not _m:
        continue
    for _k in re.finditer(r'<article[^>]*class="[^"]*\bpcard\b[^"]*"[^>]*>.*?</article>',
                          _m.group(0), re.S):
        if 'data-product=' not in _k.group(0):
            continue
        for _a in re.finditer(r'<a[^>]*class="[^"]*btn-detail[^"]*"[^>]*href="([^"]*)"'
                              r'|<a[^>]*href="([^"]*)"[^>]*class="[^"]*btn-detail[^"]*"',
                              _k.group(0)):
            _z = (_a.group(1) or _a.group(2) or '').split('?')[0].split('#')[0]
            if _z.rstrip('/') == _u.rstrip('/'):
                _sl = re.search(r'data-product="([^"]+)"', _k.group(0))
                err(f"§B7: {_f} — die Karte fuer "
                    f"{_sl.group(1) if _sl else '?'} verlinkt \"Mehr erfahren\" auf die "
                    f"Seite selbst statt auf die Produktseite")

# B10 (Heath, das Unerwartete): Wo ein guenstigeres Geschwister DERSELBEN MARKE und
# Kategorie BESSER bewertet ist, steht das auf der Seite des teureren Modells -- an der
# Stelle, an der die Annahme "teurer ist besser" am staerksten wirkt.
# Gemessen am 05.10.2026: Sechs Produkte trifft die Regel, und KEINE ihrer Seiten sagte
# es; vier nannten das guenstigere Modell irgendwo, keine nannte es besser bewertet.
# Geprueft wird die EIGENSCHAFT am ausgelieferten Stand, nicht der Lauf eines Generators:
# Den Block setzen zwei Wege (gen_pages.py und sync_guenstiger.py).
if os.path.exists('scripts/sync_guenstiger.py'):
    _rg = _gate('sync_guenstiger.py', '--check')
    if _rg.returncode != 0:
        _zg = (_rg.stdout + _rg.stderr).strip().splitlines()
        err(f"§B10: scripts/sync_guenstiger.py --check schlaegt fehl. Fix: "
            f"'python3 scripts/sync_guenstiger.py'. {_zg[-1][:160] if _zg else ''}")
else:
    err('scripts/sync_guenstiger.py fehlt — der B10-Hinweis ist dann ungegatet')

try:
    from guenstiger import finden as _b10_finden, MARKER as _B10_M
except Exception as _e:                                       # pragma: no cover
    _b10_finden = None
    err(f'§B10: guenstiger.py nicht importierbar ({_e}) — der Hinweis ist ungegatet')
if _b10_finden is not None:
    for _p10 in items:
        _d10 = (_pfeld(_p10, 'detail') or '').strip('/')
        _f10 = _d10 + '/index.html'
        if not _d10 or not os.path.exists(_f10):
            continue
        _h10 = open(_f10, encoding='utf-8').read()
        _hat = f'<!-- {_B10_M}:START -->' in _h10
        _soll = _b10_finden(_p10, items)
        if _soll is not None and not _hat:
            err(f"§B10: {_f10} — {_pfeld(_soll, 'name')} ist guenstiger UND besser "
                f"bewertet, die Seite sagt es aber nicht. Das ist die Zahl, die gegen "
                f"den eigenen Preis spricht, und sie gehoert auf die Seite")
        elif _soll is None and _hat:
            err(f"§B10: {_f10} fuehrt einen B10-Hinweis, obwohl es kein guenstigeres, "
                f"besser bewertetes Geschwister (mehr) gibt — ein Hinweis auf ein "
                f"Angebot, das es nicht gibt")
        elif _soll is not None:
            # Der genannte Name und beide Zahlen muessen im Block stehen. Drei Loecher,
            # alle im Pruefbericht zu B10 belegt:
            # (1) `.index(END)` brach mit ValueError ab, wenn nur der START-Marker stand.
            #     Ein Gate, das abbricht, prueft nicht nur diesen Fall nicht -- es nimmt
            #     die 250 err()-Stellen mit, die dahinter liegen. Also `find()` + Meldung.
            # (2) `wert not in block` ist ein Teilstring-Test: "88 €" steckt in "188 €",
            #     "4,4" in "14,4". Beide Zahlen werden daher mit Ziffergrenzen geprueft.
            # (3) Ein leerer Name machte die Zusicherung wirkungslos (`'' in x` ist immer
            #     wahr) und lieferte den Linktext "Der Razer </a>". Der Name wird deshalb
            #     im Linktext auf die Zielseite geprueft -- das ist die Aussage, die der
            #     Satz macht -- und ein leerer Name ist selbst der Befund.
            _a10 = _h10.index(f'<!-- {_B10_M}:START -->')
            _e10 = _h10.find(f'<!-- {_B10_M}:END -->')
            if _e10 < _a10:
                err(f"§B10: {_f10} — der B10-Marker hat keinen Partner (START ohne END "
                    f"oder END vor START). Fix: 'python3 scripts/sync_guenstiger.py' "
                    f"bzw. 'python3 scripts/gen_pages.py --regen'")
                continue
            _roh10 = _h10[_a10:_e10]
            _blk = _klartext(_roh10)
            # Der Link wird im auskommentar-befreiten Markup gesucht, nicht im rohen: Ein
            # Block, der komplett in einem HTML-Kommentar steht, traegt sein `<a>` sonst
            # weiter und die Zusicherung haelt an einem unsichtbaren Satz fest.
            _sicht10 = re.sub(r'<!--.*?-->', '', _roh10, flags=re.S)
            _sn, _sc = _bewertung(_soll)
            _nm10 = _pfeld(_soll, 'name').strip()
            _zl10 = (_pfeld(_soll, 'detail') or '').rstrip('/') + '/'
            _lk10 = re.search(rf'<a[^>]*href="{re.escape(_zl10)}"[^>]*>(.*?)</a>',
                              _sicht10, re.S)
            if not _nm10:
                err(f"§B10: {_f10} — das guenstigere Modell traegt in products.json "
                    f"keinen Namen; der Hinweis kann es nicht benennen")
            elif not (_lk10 and _nm10 in _klartext(_lk10.group(1))):
                err(f"§B10: {_f10} — der Hinweis nennt \"{_nm10}\" nicht im Linktext auf "
                    f"{_zl10} (Fix: 'python3 scripts/sync_guenstiger.py' bzw. "
                    f"'python3 scripts/gen_pages.py --regen')")
            for _was, _wert in (('Sterne', _sterne_text(_sn)),
                                ('Preis', f"{_preis_zahl(_soll)} €")):
                if not re.search(rf'(?<![\d,.]){re.escape(str(_wert))}(?!\d)', _blk):
                    err(f"§B10: {_f10} — der Hinweis nennt {_was} \"{_wert}\" nicht "
                        f"(Fix: 'python3 scripts/sync_guenstiger.py' bzw. "
                        f"'python3 scripts/gen_pages.py --regen')")

    # Der Gegentest ueber ALLE Seiten. Die Schleife oben laeuft ueber products.json und
    # sieht deshalb nur Produktseiten: Ein Block auf einer Blog- oder Hub-Seite war fuer
    # §B10 unsichtbar (gemessen am 05.10.2026, je ein eingeschmuggelter Block auf
    # blog/hall-effect-erklaert/ und controller/universal/ blieb gruen). "Wo nicht, steht
    # keiner" gilt fuer die ganze Site, nicht fuer die 42 Seiten der Datei.
    _b10_ok = {(_pfeld(_p10, 'detail') or '').strip('/') + '/index.html' for _p10 in items}
    for _f10 in pages:
        if (f'<!-- {_B10_M}:START -->' in open(_f10, encoding='utf-8').read()
                and _f10 not in _b10_ok):
            err(f"§B10: {_f10} fuehrt einen B10-Hinweis, ist aber keine Produktseite — "
                f"der Hinweis gehoert auf die Seite des teureren Modells, sonst nirgends")

# B11 (Dunford, Obviously Awesome): Die echte Alternative des Lesers ist Amazon selbst und
# ein Video, nicht ein anderer Blog. Gemessen am 05.10.2026 ueber alle 127 Seiten: "YouTube"
# stand auf 0 Seiten, "Amazon" auf der Startseite dreimal im Seiteninhalt und jedes Mal
# als Datenquelle (mit Footer vier, die vierte ist der Provisionshinweis).
# Positioniert wurde gegen "klassische Affiliate-Seiten" -- gegen einen Gegner, den der
# Leser gar nicht erwaegt. Drei Eigenschaften, alle am ausgelieferten Stand:
if os.path.exists('scripts/sync_positionierung.py'):
    _rp11 = _gate('sync_positionierung.py', '--check')
    if _rp11.returncode != 0:
        _z11 = (_rp11.stdout + _rp11.stderr).strip().splitlines()
        err(f"§B11: scripts/sync_positionierung.py --check schlaegt fehl. Fix: "
            f"'python3 scripts/sync_positionierung.py'. {_z11[-1][:160] if _z11 else ''}")
else:
    err('scripts/sync_positionierung.py fehlt — die Positionierung ist dann ungegatet')

try:
    from positionierung import (MARKER as _B11_M, SEITEN as _B11_S, ZAHLWORT as _B11_W,
                                fakten as _b11_fakten, _spanne as _b11_spanne,
                                schwaechen as _b11_schwaechen)
except Exception as _e:                                       # pragma: no cover
    _B11_M = None
    err(f'§B11: positionierung.py nicht importierbar ({_e}) — die Positionierung ist '
        f'ungegatet')
if _B11_M:
    _f11 = _b11_fakten(items)
    _b11_soll = {d for d, _ in _B11_S}
    # 1 · Die Zahlen im Block muessen die gemessenen sein. Teilstring-Tests waeren hier
    # besonders wertlos: "42" steckt in "142" und "13" in "130". Darum Ziffergrenzen,
    # dieselbe Lehre wie bei §B10.
    _b11_zahlen = {
        'start': (('Produktseiten mit Kompatibilitaets-Aussage', _f11['kompat']),
                  ('davon mit Negativzeile', _f11['kompat_nein']),
                  ('Produkte', _f11['produkte']),
                  ('Controller', _f11['controller']),
                  ('Controller unter der Schwelle', _f11['unter_schwelle']),
                  ('Seiten mit B10-Hinweis', _f11['guenstiger'])),
        'methode': (('Produkte', _f11['produkte']),
                    ('eigene Tests', _f11['tests']),
                    ('Kurzchecks', _f11['kurzchecks'])),
    }
    for _d11, _art11 in _B11_S:
        if not os.path.exists(_d11):
            err(f"§B11: {_d11} fehlt — die Seite traegt die Positionierung")
            continue
        _h11 = open(_d11, encoding='utf-8').read()
        _a11 = _h11.find(f'<!-- {_B11_M}:START -->')
        _e11 = _h11.find(f'<!-- {_B11_M}:END -->')
        if _a11 < 0:
            err(f"§B11: {_d11} traegt keinen Positionierungs-Block (Fix: "
                f"'python3 scripts/sync_positionierung.py')")
            continue
        if _e11 < _a11:
            err(f"§B11: {_d11} — der Marker hat keinen Partner (START ohne END oder END "
                f"vor START). Fix: 'python3 scripts/sync_positionierung.py'")
            continue
        # BEIDE Marker zaehlen. Die erste Fassung zaehlte nur START und nahm von END das
        # erste Vorkommen: Ein verwaistes zweites END blieb damit stumm gruen, obwohl
        # "Marker gepaart" als gepruefte Eigenschaft ausgewiesen war. Folgenlos fuer den
        # Leser, aber es verschiebt beim naechsten Umzug die Reichweite von `entferne()`.
        for _mk11, _nz11 in ((f'<!-- {_B11_M}:START -->', _h11.count(f'<!-- {_B11_M}:START -->')),
                             (f'<!-- {_B11_M}:END -->', _h11.count(f'<!-- {_B11_M}:END -->'))):
            if _nz11 != 1:
                err(f"§B11: {_d11} traegt den Marker {_mk11} {_nz11}x, erwartet genau 1")
        if (_h11.count(f'<!-- {_B11_M}:START -->') != 1
                or _h11.count(f'<!-- {_B11_M}:END -->') != 1):
            continue
        _t11 = _klartext(_h11[_a11:_e11])
        for _was11, _wert11 in _b11_zahlen[_art11]:
            if not re.search(rf'(?<![\d,.]){_wert11}(?!\d)', _t11):
                err(f"§B11: {_d11} — der Block nennt die gemessene Zahl {_wert11} "
                    f"({_was11}) nicht (Fix: 'python3 scripts/sync_positionierung.py')")
        # Und die Gegenrichtung (P-11, Mechanismus 2): KEINE Zahl im Block darf
        # ungedeckt sein. Die Anwesenheitspruefung allein genuegt nicht, weil "42"
        # zweimal im Abschnitt steht: Wird eine der beiden zu "142", bleibt die andere
        # stehen und die Eigenschaft gilt weiter. Gemessen am 05.10.2026 -- diese Form
        # wurde nur ueber den Zeichenvergleich des Sync-Skripts rot, nicht ueber §B11.
        _txt11 = _t11
        for _nm11 in sorted({_pfeld(_p, 'name') for _p in items}, key=len, reverse=True):
            if _nm11:
                _txt11 = _txt11.replace(_nm11, ' ')
        _txt11 = re.sub(r'\b(iPhone|iPad|iOS|Android|Galaxy|Generation|Gen\.?)\s*\d+',
                        ' ', _txt11)
        _erl11 = {str(_v) for _v in _f11.values() if _v is not None}
        _erl11.add(_sterne_text(A6_SCHWELLE))
        for _z11 in re.findall(r'\d+(?:,\d+)?', _txt11):
            if _z11 not in _erl11:
                err(f"§B11: {_d11} — die Zahl {_z11} im Positionierungs-Block ist aus "
                    f"keiner Regel abgeleitet (gedeckt waeren {sorted(_erl11)}). Fix: "
                    f"'python3 scripts/sync_positionierung.py'")
        if _art11 == 'start':
            # 2 · Die Alternative muss BENANNT sein. Das ist die Massnahme selbst: Ein
            # Positionierungs-Abschnitt, der Amazon und das Video nicht nennt, positioniert
            # wieder gegen niemanden.
            for _alt11 in ('Amazon', 'Video'):
                if _alt11 not in _t11:
                    err(f"§B11: {_d11} — der Positionierungs-Abschnitt nennt \"{_alt11}\" "
                        f"nicht; er soll die echte Alternative benennen")
            if _b11_spanne(_f11) not in _t11:
                err(f"§B11: {_d11} — die Lesezeit-Spanne \"{_b11_spanne(_f11)}\" steht "
                    f"nicht im Block (Fix: 'python3 scripts/sync_positionierung.py')")
            # Die Zahl der Schwaechen steht als WORT im Satz ("mindestens zwei"), also
            # faellt sie durch die Ziffernpruefung oben. Geprueft wird deshalb das Wort,
            # das die Regel fuer den gemessenen Mindestwert rendert.
            _w11 = str(_B11_W.get(_f11['min_cons'], _f11['min_cons']))
            if _w11 not in _t11:
                err(f"§B11: {_d11} — der Block nennt die gemessene Mindestzahl der "
                    f"Schwaechen (\"{_w11}\") nicht (Fix: "
                    f"'python3 scripts/sync_positionierung.py')")
    for _f11n in pages:
        if (f'<!-- {_B11_M}:START -->' in open(_f11n, encoding='utf-8').read()
                and _f11n not in _b11_soll):
            err(f"§B11: {_f11n} fuehrt einen Positionierungs-Block, gehoert aber nicht zu "
                f"den drei Seiten, die ihn tragen")


    # 3 · Solange nicht JEDES Produkt einen eigenen Test hat, soll keine Methodenseite eine
    # All-Aussage ueber eigene Tests machen. Genau die stand bis zum 05.10. auf beiden:
    # "Jeder Controller wird ueber mehrere Wochen im echten Gaming-Alltag getestet",
    # waehrend die Startseite daneben "13 von 42" sagte und 13 Seiten einen Test tragen.
    #
    # WAS DIESE PRUEFUNG IST, UND WAS SIE NICHT IST. Sie sucht ein SPRACHMUSTER, kein
    # Datum. Die erste Fassung hat sich im Kommentar "Eigenschaft statt Satz" genannt und
    # das nicht eingeloest: Von zehn echten All-Aussagen fing sie eine (Verb zuerst,
    # Fuellwort zwischen Quantor und Nomen, "Test" als Substantiv, "Geraet" statt
    # "Modell", "kein X ohne Test" rutschten durch), und neun legitime Saetze wurden rot,
    # darunter die Korrektur "NICHT jeder Controller ist von uns getestet" -- die Meldung
    # schnitt das "Nicht" ab und legte der Seite das Gegenteil in den Mund.
    # Jetzt: zwei Satzstellungen, Fuellwoerter, mehr Nomen und Verben, die Sonderform
    # "kein X ohne Test", und drei Ausnahmen (Verneinung, Frage, Satz nennt die gemessene
    # Zahl). Eine Verneinung IN einer Aussage, die daneben einen All-Anspruch erhebt,
    # findet sie weiterhin nicht, und ein deutscher Satz laesst sich immer so bauen, dass
    # ein Muster ihn verfehlt. Das ist eine Stichprobe auf die bekannten Formen, kein
    # Beweis -- so steht es auch in P-16 und im Protokoll.
    _B11_NOMEN = r'(?:Controller|Modelle?n?|Produkte?n?|Ger(?:ä|ae)te?n?|Gamepads?)'
    _B11_QUANT = r'(?:jede[rsmn]?|alle[nrs]?|s(?:ä|ae)mtliche[nrs]?)'
    _B11_TEST = (r'(?:getestet|testen|teste|gepr(?:ü|ue)ft|durchlaufen|'
                 r'Test\b|Tests\b|Testprozess)')
    # Die zweite Satzstellung nimmt NUR die Test-Verben. Mit "geprueft" und den
    # Substantiven darin genuegte irgendein Testwort, gefolgt von irgendeinem Quantor
    # binnen 120 Zeichen -- und auf einer Methodenseite ist genau dieses Vokabular der
    # Normalfall: "Im Test zeigte sich, dass alle Controller mit Android laufen" wurde
    # rot, eine Aussage, die mit eigenen Tests gar nichts zu tun hat. Gemessen fielen so
    # 7 von 14 legitimen Saetzen; mit dieser Zeile ist es einer, und der steht als
    # genannte Grenze unten.
    _B11_TEST2 = r'(?:getestet|testen|teste|durchlaufen)'
    _B11_ALL = re.compile(
        rf'{_B11_QUANT}\s+(?:\w+\s+){{0,2}}{_B11_NOMEN}\b[^.!?]{{0,120}}?\b{_B11_TEST}'
        rf'|\b{_B11_TEST2}\b[^.!?]{{0,120}}?{_B11_QUANT}\s+(?:\w+\s+){{0,2}}{_B11_NOMEN}\b'
        rf'|\bkein(?:e[nrs]?)?\s+(?:\w+\s+){{0,2}}{_B11_NOMEN}\b[^.!?]{{0,70}}\bohne\b'
        rf'[^.!?]{{0,50}}\bTest', re.I)
    _B11_VERNEINT = re.compile(r'\b(nicht|nie|niemals|selten|nur wenige|nein)\b', re.I)
    # Die Schwelle haengt an der Klasse, die der Satz nennt: "Jeder CONTROLLER wird
    # getestet" ist wahr, sobald alle 28 Controller einen Test tragen, auch wenn die 14
    # Zubehoerteile keinen haben. Die erste Fassung verglich immer gegen alle 42 und
    # haette diesen richtigen Satz blockiert.
    for _d11, _art11 in _B11_S:
        if _art11 != 'methode' or not os.path.exists(_d11):
            continue
        for _satz in re.split(r'(?<=[.!?])\s+', _klartext(open(_d11, encoding='utf-8').read())):
            _m11 = _B11_ALL.search(_satz)
            if not _m11:
                continue
            _kein = _m11.group(0).lower().startswith('kein')
            if (not _kein and _B11_VERNEINT.search(_satz)) or _satz.rstrip().endswith('?'):
                continue            # Verneinung oder Frage ist keine All-Behauptung
            _ctrl11 = re.search(r'Controller', _m11.group(0), re.I)
            _ist, _soll11 = ((_f11['tests_controller'], _f11['controller']) if _ctrl11
                             else (_f11['tests'], _f11['produkte']))
            # Die Ausnahme gilt der FORM, nicht jeder Ziffer im Satz: entweder steht die
            # gemessene Zahl in einer einschraenkenden Wendung ("13 davon", "13 von 42"),
            # oder Zahl UND Grundgesamtheit stehen beide da ("Von allen 42 Produkten
            # tragen 13 einen eigenen Test"). Vorher genuegte eine nackte 13 irgendwo, und
            # "ein 13-Punkte-Test im Alltag" war damit freigestellt.
            # BEKANNTE GRENZE: "Alle Modelle werden getestet, 13 davon besonders
            # gruendlich" bleibt gruen. Der Satz nennt die Zahl in der richtigen Form und
            # erhebt daneben trotzdem einen All-Anspruch; der Unterschied zur wahren
            # Startseiten-Fassung liegt allein im Verb (gepruefT gegen getesteT). Das
            # trennt kein Muster, und es wird hier auch nicht behauptet.
            if (re.search(rf'(?<![\d,.]){_ist}(?!\d)\s*(?:von|der|davon|/)\b', _satz)
                    or (re.search(rf'(?<![\d,.]){_ist}(?!\d)', _satz)
                        and re.search(rf'(?<![\d,.]){_soll11}(?!\d)', _satz))):
                continue            # der Satz nennt die gemessene Zahl in ihrer Rolle
            if _ist < _soll11:
                _zit = re.sub(r'[¶\s]+', ' ', _satz).strip()
                err(f"§B11: {_d11} behauptet im Satz \"{_zit[:140]}\", aber nur "
                    f"{_ist} von {_soll11} tragen einen eigenen Test — eine All-Aussage "
                    f"auf der Methodenseite ist genau da falsch, wo der Leser sie prueft")

# ---------- §A6 · mindestens zwei echte Schwaechen je Produktseite ----------
# Der ungegatete Teil der Verfassung: "Jedes Review nennt mindestens zwei echte
# Schwaechen." Das stand seit dem ersten Tag als Gesetz da und wurde von NICHTS geprueft,
# aufgefallen erst, als B11 den Satz auf die Startseite geschrieben hat. Auf den 29
# generierten Seiten faengt der §A1-Zeichenvergleich eine geloeschte Schwaeche zufaellig
# mit; die 13 handgepflegten Reviews hatten gar keinen Rueckhalt (gemessen: eine
# Review-Seite von 4 auf 1 Schwaeche gekuerzt, Lauf blieb gruen).
# Gemessen am 05.10.2026: 42 Seiten, Minimum 2, Verteilung 16x2 / 16x3 / 9x4 / 1x5.
# EIGENER try: Ein Verfassungs-Gate darf nicht daran haengen, ob die Positionierung
# importierbar ist -- sonst schaltet das Entfernen einer Massnahme ein Gesetz mit ab.
try:
    from positionierung import schwaechen as _schwaechen
except Exception as _e:                                       # pragma: no cover
    _schwaechen = None
    err(f"§A6: die Schwaechen-Zaehlung ist nicht importierbar ({_e}) — damit ist das "
        f"Gesetz 'jedes Review nennt mindestens zwei echte Schwaechen' ungegatet")
if _schwaechen is not None:
    for _p6 in items:
        _d6 = (_pfeld(_p6, 'detail') or '').strip('/') + '/index.html'
        if not _pfeld(_p6, 'detail') or not os.path.exists(_d6):
            continue
        _n6 = _schwaechen(open(_d6, encoding='utf-8').read())
        if _n6 < 2:
            err(f"§A6: {_d6} nennt {_n6} Schwaeche(n), gefordert sind mindestens zwei. "
                f"Ein Review ohne echte Schwaechen ist eine Werbeseite, und die "
                f"Startseite behauptet das Gegenteil fuer alle {len(items)} "
                f"Produktseiten")

# B9 (Cialdini, Autoritaet am Entscheidungspunkt): Die Beschriftung des Detail-Knopfs
# sagt, WAS den Leser erwartet -- ein eigener Test oder ein Datenblatt. Gemessen am
# 05.10.2026 ueber alle 200 Produktkarten der Site, VOR der Massnahme:
#   66 zeigten auf einen eigenen Test und sagten "Mehr erfahren"  (Signal verschenkt)
#   95 zeigten auf ein Datenblatt und sagten dasselbe             (nichtssagend)
#    2 zeigten auf ein Datenblatt und sagten "Zum Test"           (schlicht falsch)
# Dazu benannte main.js jeden Knopf um, dessen Text auf /zum test|details/i passte, und
# loeschte damit 35 der 37 richtigen Beschriftungen. Die zwei "Zum Kurzcheck" ueberlebten
# die Regel -- auf zwei von 200 Karten war die Unterscheidung also auch mit JavaScript da,
# auf 198 nicht. Drei Eigenschaften:
from produktdaten import (detail_label as _b9_label, LABEL_TEST as _B9_T,
                          LABEL_DATENBLATT as _B9_D, BTN_DETAIL as _B9_MUSTER,
                          btn_ziel_text as _b9_ziel, PRODUKT_PRAEFIXE as _B9_P)

_B9_A = re.compile(_B9_MUSTER)
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    # Weiterleitungs-Stubs ueberspringen, aber NICHT jede Seite mit `noindex`: 404.html
    # traegt `noindex, follow` im Head und steht trotzdem ausdruecklich in `pages`
    # ("sonst waere sie die einzige ausgelieferte HTML-Datei ohne Gate"). Die erste
    # Fassung sprang ueber sie hinweg und liess damit genau die Datei ungeprueft, die der
    # Kommentar oben aufnimmt.
    if 'http-equiv="refresh"' in _h[:_h.find('</head>') + 7]:
        continue
    _h2 = re.sub(r'<!--.*?-->', ' ', _h, flags=re.S)
    for _m in _B9_A.finditer(_h2):
        _z, _x = _b9_ziel(_m)
        if not _z.startswith(_B9_P):
            continue
        _soll = _b9_label(_z)
        if _x.strip() != _soll:
            err(f"§B9: {_f} beschriftet den Knopf zu {_z} mit \"{_x.strip()}\", "
                f"abgeleitet waere \"{_soll}\" — "
                f"'python3 scripts/sync_product_values.py' bzw. den Generator laufen lassen")

# Die drei JS-Renderer fuehren die Regel zwangslaeufig ein zweites Mal (der Browser kann
# kein Python importieren). Sie wird GEGEN die Python-Fassung geprueft, so wie A6_SCHWELLE.
for _jf in ('assets/js/hub-render.js', 'assets/js/produkte.js', 'assets/js/finder.js'):
    if not os.path.exists(_jf):
        continue
    _js = _ohne_kommentare(open(_jf, encoding='utf-8').read(), True)
    if 'detailLabel' not in _js:
        err(f"§B9: {_jf} rendert Produktkarten, kennt aber `detailLabel` nicht — die "
            f"Beschriftung waere dort wieder fest verdrahtet")
        continue
    for _name, _wert in (('LABEL_TEST', _B9_T), ('LABEL_DATENBLATT', _B9_D)):
        _mm = re.search(rf'{_name}\s*=\s*[\'"]([^\'"]*)[\'"]', _js)
        if not _mm:
            err(f"§B9: {_jf} nennt {_name} nicht")
        elif _mm.group(1) != _wert:
            err(f"§B9: {_jf} setzt {_name} auf \"{_mm.group(1)}\", produktdaten.py sagt "
                f"\"{_wert}\" — zwei Fassungen derselben Regel")
    if "startsWith('/produkte/')" not in _js and 'startsWith("/produkte/")' not in _js:
        err(f"§B9: {_jf} leitet die Beschriftung nicht aus dem Ziel ab "
            f"(kein startsWith('/produkte/'))")
    # Die Funktion zu HABEN genuegt nicht, sie muss im Karten-Markup auch BENUTZT werden.
    # Die erste Fassung dieses Gates prueft nur die Erwaehnung -- `detailLabel` stehen
    # lassen und daneben "Mehr erfahren" fest verdrahten blieb still gruen, also genau
    # der Zustand, den B9 beseitigt hat.
    for _am in re.finditer(r'<a[^>]*class=\\?"btn-detail\\?"[^>]*>(.{0,80}?)</a>', _js, re.S):
        if 'detailLabel' not in _am.group(1):
            err(f"§B9: {_jf} schreibt die Beschriftung des Detail-Knopfs fest "
                f"(\"{_am.group(1).strip()[:40]}\") statt sie mit detailLabel() aus dem "
                f"Ziel abzuleiten")

# main.js darf die Beschriftung NICHT zur Laufzeit ueberschreiben. Genau das hat sie
# geloescht, und §A2 verlangt ohnehin, dass JS identisches Markup hydratisiert.
if os.path.exists('assets/js/main.js'):
    _mj9 = _ohne_kommentare(open('assets/js/main.js', encoding='utf-8').read(), True)
    # Geprueft wird die EIGENSCHAFTS-KLASSE, nicht eine Schreibweise. Die erste Fassung
    # suchte woertlich `detailLink.textContent =` -- `innerHTML`, `innerText` und ein
    # anderer Variablenname blieben still gruen, obwohl sie dasselbe tun. Das ist die
    # Lehre dieses Pakets ("ein Gate, das die Erwaehnung prueft, prueft nicht die
    # Verwendung") eine Ebene tiefer, und `innerHTML` ist genau die Variante, die jemand
    # beim naechsten "for consistency" tippt.
    # Der Variablenname wird aus dem `.btn-detail`-Query ABGELEITET, nicht geraten.
    _b9_vars = set(re.findall(r'(?:const|let|var)\s+(\w+)\s*=\s*[^;\n]*'
                              r'querySelector(?:All)?\([^)]*btn-detail', _mj9))
    _b9_schreib = r'(?:textContent|innerText|innerHTML|outerHTML|replaceChildren|' \
                  r'insertAdjacentHTML|append|textContent)'
    for _v in _b9_vars or {'detailLink'}:
        if re.search(rf'\b{re.escape(_v)}\s*\.\s*{_b9_schreib}\s*(?:=[^=]|\()', _mj9):
            err(f"§B9/§A2: assets/js/main.js schreibt die Beschriftung des Detail-Knopfs "
                f"zur Laufzeit um (ueber `{_v}`) — damit sieht der Leser mit JavaScript "
                f"etwas anderes als der ohne, und das Autoritaetssignal der Karte ist weg")

# B8 (Cialdini): Sternzahl und Bewertungszahl sind ZWEI Signale. "4,8 aus 12 Bewertungen"
# und "4,4 aus 3.147" sind sehr verschiedene Aussagen, und wer nur den Wert zeigt, zeigt
# die halbe. Gemessen am 04.10. stand der Wert in 26px/800 und die Anzahl in 11px im
# schwaechsten Farbton des Systems -- Faktor 2,4 in der Groesse, blassester Ton.
#
# ZWEITE FASSUNG. Die erste hatte in beide Richtungen Loecher, und beide Male an der
# Stelle, an der sie die eigentliche Arbeit tun sollte:
#   · `<div class="rb-count">([^<]*)</div>` verlangte reinen Text. Die Anzahl mit
#     <strong> hervorzuheben -- also genau das, was B8 will -- machte den Lauf ROT.
#     Umgekehrt genuegte IRGENDEINE Ziffer: "Platz 3" kam durch.
#   · `if _st and _lab:` ohne `else` hat sich still abgeschaltet. Sechs Formen mit FUENF
#     vollen Sternen neben "8,7 von 10" blieben gruen -- `.stars` als <span>, mit zweiter
#     Klasse, mit einfachen Anfuehrungszeichen, ohne rb-label, "von 10 Punkten", "von
#     zehn". Und die Glyphen-GESAMTzahl wurde nie geprueft: ★★★★☆☆☆ ging durch.
# Das wiegt besonders, weil die vier Seiten mit Zehner-Skala die HANDGEPFLEGTEN sind --
# dort gibt es keinen Generator-Abgleich, der einspringt.
_B8_ZAHL = re.compile(r'\d')
_B8_WORT = re.compile(r'Bewertung', re.I)


def _b8_text(_s):
    """Tag-freier Text eines Fragments, Entities aufgeloest."""
    return html.unescape(re.sub(r'<[^>]+>', ' ', _s))


def _b8_element(_bd, _klasse):
    """Inhalt des ERSTEN Elements mit dieser Klasse, per Tag-Zaehlung statt Regex.

    Tag-unabhaengig (div, span, p) und klassen-token-genau, damit "stars rb-stars"
    genauso trifft wie "stars".
    """
    _m = re.search(r'<([a-z]+)[^>]*class\s*=\s*["\'][^"\']*\b'
                   + _klasse + r'\b[^"\']*["\'][^>]*>', _bd, re.I)
    if not _m:
        return None
    _tag = _m.group(1).lower()
    _tiefe, _i = 1, _m.end()
    for _t in re.finditer(rf'<{_tag}\b|</{_tag}\s*>', _bd[_i:], re.I):
        _tiefe += 1 if not _t.group(0).startswith('</') else -1
        if _tiefe == 0:
            return _bd[_i:_i + _t.start()]
    return _bd[_i:]


for _f in pages:
    _roh = open(_f, encoding='utf-8').read()
    # Kommentare und nicht ausgelieferte Container raus: ein Badge in <template> oder in
    # einem Kommentar steht nicht auf der Seite und darf nicht geprueft werden.
    _h = re.sub(r'<!--.*?-->', ' ', _roh, flags=re.S)
    _h = re.sub(r'<(template|noscript|script|style)\b.*?</\1>', ' ', _h, flags=re.S)
    if 'rating-badge' not in _h:
        continue
    _badges = []
    for _bm in re.finditer(r'<div[^>]*class\s*=\s*["\'][^"\']*\brating-badge\b', _h):
        _tiefe, _ende = 0, None
        for _m in re.finditer(r'<div\b|</div\s*>', _h[_bm.start():]):
            _tiefe += 1 if not _m.group(0).startswith('</') else -1
            if _tiefe == 0:
                _ende = _bm.start() + _m.end()
                break
        if _ende is None:
            err(f"§B8: {_f} hat ein rating-badge, dessen <div> nicht geschlossen wird")
            continue
        _badges.append(_h[_bm.start():_ende])
    for _bd in _badges:
        _num_r = _b8_element(_bd, 'rb-num')
        if _num_r is None:
            err(f"§B8: {_f} hat ein rating-badge ohne Wert (rb-num)")
            continue
        _num = _b8_text(_num_r).strip()
        # 1 · Die Anzahl steht da, als ANZAHL -- Ziffer UND das Wort "Bewertung".
        _cnt_r = _b8_element(_bd, 'rb-count')
        if _cnt_r is None:
            err(f"§B8: {_f} zeigt die Bewertung {_num}, aber kein `.rb-count` — Wert und "
                f"Anzahl sind zwei Signale, und eines davon fehlt")
            continue
        _cnt = _b8_text(_cnt_r)
        if not (_B8_ZAHL.search(_cnt) and _B8_WORT.search(_cnt)):
            err(f"§B8: {_f} — `.rb-count` nennt keine Bewertungszahl "
                f"(\"{' '.join(_cnt.split())[:60]}\"). Eine Ziffer allein genuegt nicht")
        # 2 · Nicht als Fussnote gesetzt.
        if re.search(r'<[a-z]+[^>]*\brb-count\b[^>]*style="[^"]*font-size', _bd) or \
                re.search(r'<[a-z]+[^>]*style="[^"]*font-size:\s*(?:[0-9]|1[01])px[^"]*"'
                          r'[^>]*>[^<]*\d[^<]*Bewertung', _bd, re.I):
            err(f"§B8: {_f} setzt die Bewertungszahl als Inline-Fussnote statt in "
                f"`.rb-count` mit eigener Regel")
        # 3 · Glyphen gegen die GENANNTE Skala. Fehlt eine der beiden Angaben, ist das
        #     ein Befund und kein Grund, die Pruefung zu ueberspringen.
        _st_r = _b8_element(_bd, 'stars')
        _lab_r = _b8_element(_bd, 'rb-label')
        if _st_r is None:
            err(f"§B8: {_f} zeigt {_num} ohne Sterne-Darstellung (`.stars`) — dann ist "
                f"die Skalentreue nicht pruefbar")
            continue
        if _lab_r is None:
            err(f"§B8: {_f} zeigt Sterne ohne Skalen-Angabe (`.rb-label`) — dann ist "
                f"nicht pruefbar, worauf sich {_num} bezieht")
            continue
        _lz = re.search(r'(\d+)', _b8_text(_lab_r))
        _nz = re.search(r'(\d+(?:[.,]\d+)?)', _num)
        if not _lz or not _nz:
            err(f"§B8: {_f} — Skala oder Wert nicht als Zahl lesbar "
                f"(Wert \"{_num[:20]}\", Skala \"{_b8_text(_lab_r).strip()[:20]}\")")
            continue
        _glyph = _b8_text(_st_r)
        _voll, _leer = _glyph.count('★'), _glyph.count('☆')
        if _voll + _leer != 5:
            err(f"§B8: {_f} zeigt {_voll + _leer} Sterne-Glyphen statt 5 "
                f"({_voll}x voll, {_leer}x leer) — eine Fuenfer-Darstellung hat fuenf")
            continue
        _skala = int(_lz.group(1))
        _wert = float(_nz.group(1).replace(',', '.'))
        _soll = max(0, min(5, round(_wert / _skala * 5))) if _skala else 0
        if _voll != _soll:
            err(f"§B8: {_f} zeigt {_voll} volle Sterne fuer \"{_num} von {_skala}\" — "
                f"auf einer Fuenfer-Darstellung sind das {_soll}")

# B7: Der Rueckweg. Jede Produktseite verlinkt zurueck auf jede Uebersicht, die sie
# fuehrt. Gemessen am 04.10., VOR dieser Massnahme: Alle vier Marken-Hubs verlinkten
# lueckenlos ihre Produkte, und alle 14 Produkte dieser Marken verlinkten NICHT zurueck;
# 29 von 42 Produktseiten nannten keinen einzigen Plattform-Hub. Die Verlinkung war nicht
# duenn, sie war EINSEITIG -- genau das meint B7 mit "systematisch statt punktuell".
#
# Geprueft wird die EIGENSCHAFT am ausgelieferten Stand, nicht der Lauf eines Generators:
# Den Block setzen zwei verschiedene Wege (gen_pages.py fuer /produkte/, sync_hublinks.py
# fuer die handgepflegten Reviews), und ein Gate, das nur einen davon kennt, deckt die
# Haelfte nicht ab.
if os.path.exists('scripts/sync_hublinks.py'):
    _rh = _gate('sync_hublinks.py', '--check')
    if _rh.returncode != 0:
        _zh = (_rh.stdout + _rh.stderr).strip().splitlines()
        err(f"§B7: scripts/sync_hublinks.py --check schlaegt fehl. Fix: "
            f"'python3 scripts/sync_hublinks.py'. {_zh[-1][:160] if _zh else ''}")
else:
    err('scripts/sync_hublinks.py fehlt — der Rueckweg ist dann ungegatet')

try:
    from hublinks import (taxonomie_karte as _b7_karte, _rumpf as _b7_rumpf,
                          _kartenziele as _b7_ziele)
    _B7_KARTE, _B7_OHNE_H1 = _b7_karte()
except Exception as _e:                                       # pragma: no cover
    _B7_KARTE, _B7_OHNE_H1 = None, []
    err(f'§B7: hublinks nicht importierbar ({_e}) — der Rueckweg-Gate faellt aus')
for _u7 in _B7_OHNE_H1:
    err(f"§B7: {_u7} ist eine Uebersicht ohne <h1>. Ohne sie gibt es keine Beschriftung, "
        f"und der Rueckweg zeigt die nackte URL als Satzbaustein")
if _B7_KARTE is not None:
    for _p in items:
        _det = (_pfeld(_p, 'detail') or '').rstrip('/')
        _f7 = _det.lstrip('/') + '/index.html'
        if not _det or not os.path.exists(_f7):
            continue
        _soll = {_u.rstrip('/') for _u, _ in _B7_KARTE.get(_det, [])}
        if not _soll:
            err(f"§B7: {_f7} steht in keiner Uebersicht — die Produktseite ist dann nur "
                f"ueber die Suche erreichbar")
            continue
        _ist = {_m.group(1).rstrip('/') for _m in
                re.finditer(r'href="(/[^"#?]*)"',
                            _b7_rumpf(open(_f7, encoding='utf-8').read()))}
        _fehlt = sorted(_soll - _ist)
        if _fehlt:
            err(f"§B7: {_f7} wird von {', '.join(sorted(_soll))} gefuehrt, verlinkt aber "
                f"nicht zurueck auf {', '.join(_fehlt)} — "
                f"'python3 scripts/sync_hublinks.py' bzw. 'gen_pages.py --regen'")

# Zwei Eigenschaften, die der Generator herstellt und die deshalb am AUSGELIEFERTEN Stand
# nachgewiesen werden, nicht an seinem Quelltext:
#   1. Die Sortier-Begruendung steht INNERHALB des Blocks. Ein stehengebliebener
#      Hand-Satz daneben hiesse: zwei Regeln auf einer Seite, die sich widersprechen.
#      Genau so war es, bevor der Generator kam (die "Ergonomie"-Fassung).
#   2. Die ItemList fuehrt dieselben Produkte in derselben Reihenfolge wie die Karten.
#      Eine Rangfolge, deren Schema eine andere Ordnung behauptet als die Seite, ist
#      §A4-Verstoss am Kern: Das Schema IST die sichtbare Wahrheit.
try:
    from gen_bestenliste import LISTEN as _B6_LISTEN, vollname as _b6_vollname
except Exception as _e:                                       # pragma: no cover
    _B6_LISTEN = []
    err(f'§A1: gen_bestenliste nicht importierbar ({_e}) — die Bestenlisten-Gates '
        f'fallen damit aus')
for _ld in _B6_LISTEN:
    _bf = _ld['datei']
    if not os.path.exists(_bf):
        err(f"§A1: {_bf} aus gen_bestenliste.LISTEN fehlt")
        continue
    _bt = open(_bf, encoding='utf-8').read()
    _a, _e2 = _bt.find('<!-- BESTEN:START -->'), _bt.find('<!-- BESTEN:END -->')
    if _a < 0 or _e2 < 0:
        err(f"§A1: {_bf} hat keinen BESTEN-Block mehr — die Bestenliste ist dann wieder "
            f"Handtext (Fix: 'python3 scripts/gen_bestenliste.py')")
        continue
    _innen, _ausserhalb = _bt[_a:_e2], _bt[:_a] + _bt[_e2:]
    # Ankern am KRITERIEN-Vokabular. Zwei Fassungen, zwei Befunde, beide aus derselben
    # Zeile -- das Muster aus P-13 Mechanismus 16:
    #   1. Die nackte Zeichenkette "Sortiert nach" machte einen legitimen Satz rot
    #      ("Sortiert nach Veroeffentlichung findest du unsere Tests im Blog").
    #   2. Der Zusatz "mindestens ein 'und'" hatte Loch UND Fehlalarm: Der alte
    #      Handsatz mit Komma-Aufzaehlung ("Preis, Sticks, Ergonomie, Kompatibilitaet.")
    #      kam durch -- also genau der Befund, der B6 erzwungen hat -- und ein einziges
    #      "und" im Blog-Satz holte den Fehlalarm zurueck.
    # Eine Sortier-Regel nennt KRITERIEN. Danach wird gesucht, nicht nach Bindewoertern.
    _regelform = re.compile(
        r'(?i)(sortiert|geordnet|gerankt|gereiht|Reihenfolge)\s+nach\s+[^.!?]{0,160}'
        r'(Preis|Stick|Ergonomie|Kompatibilit|Bewertung|Stern|Plattform|Verbindung|'
        r'Akku|Gewicht|Urteil|Ausstattung)')
    if _regelform.search(_klartext(_ausserhalb)):
        err(f"§A6: {_bf} nennt eine Sortier-Regel AUSSERHALB des BESTEN-Blocks. Die "
            f"Seite behauptet damit zwei Reihenfolgen-Begruendungen, und nur eine davon "
            f"wird gegen products.json gerechnet")
    # Reihenfolge: sichtbare Karten gegen ItemList
    _karten = re.findall(r'data-product="([^"]+)"', _innen)
    # "Top N" im Titel, in den Social-Metas und in den Ueberschriften ist eine Zusage
    # ueber die Seite. Wer eine Position aus `LISTEN` nimmt, bricht sie -- und nichts hat
    # das gemerkt: Nach dem Entfernen standen viermal "Top 10" ueber neun Karten, alle
    # Gates gruen, und die eigene Batterie fuehrte den Vorgang als LEGITIM. Dieselbe
    # Gate-Klasse gibt es fuer den Finder laengst.
    # NUR die Stellen, an denen "Top N" eine Zusage ueber DIESE Seite ist: Titel, die
    # beiden Social-Titel und der Ueberschriftentext. Die erste Fassung las jedes
    # "Top N" der ganzen Datei -- und haette damit einen Querverweis auf die
    # Schwesterseite rot gemacht ("Beste Android Controller Top 5" als Linktext auf der
    # Top-10-Seite), also ausgerechnet den naechsten geplanten Schritt im content-loop
    # (B7, interne Verlinkung). Ein Gate, das die naechste Korrektur blockiert, hat die
    # falsche Regel (P-13 Mechanismus 6).
    # Linktexte werden aus den Ueberschriften gestrichen, weil eine Ueberschrift sehr
    # wohl auf eine andere Seite verlinken darf.
    _zusagen = re.findall(r'<title>([^<]*)</title>', _bt)
    _zusagen += re.findall(r'<meta[^>]+property="og:title"[^>]+content="([^"]*)"', _bt)
    _zusagen += re.findall(r'<meta[^>]+name="twitter:title"[^>]+content="([^"]*)"', _bt)
    for _hm in re.finditer(r'<h[12][^>]*>(.*?)</h[12]>', _bt, re.S):
        _zusagen.append(re.sub(r'<a\b[^>]*>.*?</a>', ' ', _hm.group(1), flags=re.S))
    # GRENZE, gemessen: /vergleich/beste-budget-controller/ nennt an keiner dieser
    # Stellen eine Zahl. Dort traegt allein der `topn`-Befund im Generator.
    for _tm in {m for _z in _zusagen
                for m in re.findall(r'\bTop[\s-](\d+)\b', re.sub(r'<[^>]+>', ' ', _z))}:
        if int(_tm) != len(_karten):
            err(f"§A6: {_bf} verspricht \"Top {_tm}\", der BESTEN-Block fuehrt aber "
                f"{len(_karten)} Positionen")
    _il = None
    for _sm in re.finditer(r'<script type="application/ld\+json">(.*?)</script>',
                           _innen, re.S):
        try:
            _o = json.loads(_sm.group(1))
        except Exception:
            continue
        if 'ItemList' in _typen_von(_o):
            _il = _o
    if _il is None:
        err(f"§A4: {_bf} fuehrt {len(_karten)} Positionen, aber kein ItemList-Schema — "
            f"eine Rangfolge ohne Listen-Auszeichnung")
        continue
    _ile = _il.get('itemListElement') or []
    if [e.get('position') for e in _ile] != list(range(1, len(_ile) + 1)):
        err(f"§A4: {_bf} ItemList-Positionen sind nicht 1..{len(_ile)} in Reihenfolge")
    # `vollname` aus dem Generator, NICHT hier nachgebaut. Die erste Fassung dieses
    # Gates hat die Regel "Marke plus Name, ohne die Marke zu doppeln" ein zweites Mal
    # geschrieben -- auf einer Seite, die genau diese Klasse zehnmal geschlossen hat.
    # Ein Gate, das seine eigene Fassung der Regel fuehrt, prueft sich selbst.
    _slug_von_name = {_b6_vollname(_p): _pfeld(_p, 'slug') for _p in items}
    _schema_slugs = [_slug_von_name.get(e.get('name')) for e in _ile]
    if _schema_slugs != _karten:
        err(f"§A4: {_bf} — die ItemList fuehrt eine andere Reihenfolge als die Karten.\n"
            f"        Karten : {_karten}\n"
            f"        Schema : {_schema_slugs}")


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
    # timeout: Ohne ihn konnte dieser Aufruf den ganzen Lauf anhalten, statt ihn rot zu
    # machen -- ein leeres `name`-Feld genuegte (Ursache jetzt in audit_prosa.py selbst
    # behoben). Ein Gate, das nicht endet, meldet auch nichts, was es schon gefunden hat.
    try:
        _pr = subprocess.run([sys.executable, 'scripts/audit_prosa.py'],
                             capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        err('§A1-Fließtext: scripts/audit_prosa.py ist nach 180 s nicht fertig geworden '
            'und wurde abgebrochen — das Fließtext-Audit ist in diesem Lauf NICHT '
            'gelaufen. Haeufigste Ursache: ein leeres oder sehr kurzes Produktfeld, das '
            'als Suchname an jeder Position trifft')
        _pr = None
    if _pr is not None and _pr.returncode != 0:
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
        _soll = re.search(r'(\d+)', str(_p.get('price') or '').replace('.', ''))
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
        # str(): Ein Nicht-String-Wert in Bew. liess re.match mit TypeError statt einer
        # Meldung abbrechen -- dieselbe Klasse wie bei Verb., eine Stelle uebersehen.
        _bw = _spec_wie(_p, 'Bew')
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
        _soll = re.search(r'(\d+)', str(_p.get('price') or '').replace('.', ''))
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
        _ist, _soll = set(_m.group(1).split()), set(_pliste(_p, 'worksOn'))
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
    # str(): claim als Zahl liess re.search hier mit TypeError abbrechen (Runde 18).
    _claim = str(_p.get('claim') or '')
    _verb = _spec(_p, 'Verb.')
    _w = set(_pliste(_p, 'worksOn'))
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

# Die position-Werte JEDER Liste muessen 1..n in Reihenfolge sein. Gilt fuer ItemList und
# BreadcrumbList gleichermassen: Eine Liste mit den Positionen 1, 7, 3 ist kaputte
# strukturierte Daten, ob sie eine Rangfolge oder einen Pfad beschreibt.
# Gefunden hat das die eigene B6-Batterie: Ein Fall, der eine ItemList-Position verbiegen
# sollte, traf die BreadcrumbList derselben Seite -- und blieb gruen. Die Luecke war
# nicht der Fall, sondern das fehlende Gate. Vorher war die Pruefung nur INNERHALB des
# BESTEN-Blocks verankert, also auf vier von 127 Seiten.
# Gemessen beim Einbau: 124 Listen-Schemas, 0 mit kaputter Folge.
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    for _sm in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', _h, re.S):
        try:
            _obj = json.loads(_sm.group(1))
        except Exception:
            continue
        for _node in (_obj.get('@graph') if isinstance(_obj.get('@graph'), list)
                      else [_obj]):
            if not isinstance(_node, dict):
                continue
            if not ({'ItemList', 'BreadcrumbList'} & set(_typen_von(_node))):
                continue
            _el = [e for e in (_node.get('itemListElement') or []) if isinstance(e, dict)]
            _pos = [e.get('position') for e in _el]
            # Eine ungeordnete Liste (ItemListUnordered) darf laut schema.org ganz ohne
            # `position` auskommen. Die erste Fassung machte so eine Liste rot -- ein
            # Fehlalarm auf voellig konformem Markup. Geprueft wird die FOLGE, und zwar
            # nur, wenn ueberhaupt eine behauptet wird.
            if all(e.get('position') is None for e in _el):
                continue
            if _pos != list(range(1, len(_el) + 1)):
                err(f"§A4: {_f} {'/'.join(sorted(_typen_von(_node)))} hat die "
                    f"position-Werte {_pos}, erwartet 1..{len(_el)} in Reihenfolge")

# Ueberschriften-Hierarchie: keine Ebene darf uebersprungen werden (h1 -> h3). Das ist
# eine Struktur-Zusage an Crawler und Screenreader, und sie war ungegatet -- aufgefallen,
# weil der erste Bestenlisten-Generator `h3` fest verdrahtete und damit auf drei Seiten,
# die vorher `h2` trugen, einen Sprung h1 -> h3 erzeugt hat. Gefunden hat das der
# Pruefbericht, nicht ein Gate.
# Gemessen beim Einbau: 127 Seiten, 0 Spruenge.
for _f in pages:
    # HTML-Kommentare raus, sonst zaehlt eine auskommentierte Ueberschrift mit.
    _h = re.sub(r'<!--.*?-->', ' ', open(_f, encoding='utf-8').read(), flags=re.S)
    _h = re.sub(r'<(script|style|template|noscript)[^>]*>.*?</\1>', ' ', _h, flags=re.S)
    _vorher = None
    for _m in re.finditer(r'<h([1-6])\b', _h):
        _e = int(_m.group(1))
        if _vorher is not None and _e > _vorher + 1:
            err(f"§B: {_f} ueberspringt eine Ueberschriften-Ebene (h{_vorher} -> h{_e})")
            break
        _vorher = _e

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
    # Nur die Formen, die WIRKLICH Geld bewegen: der URL-Parameter (`?tag=` / `&tag=`)
    # und die Konstante, aus der main.js den Link baut. Das Muster hiess vorher bloss
    # `tag=([A-Za-z0-9_-]+)` ueber alle Textdateien -- und traf damit ein ganz normales
    # Python-Schluesselwortargument (`_tag=None`) in verify.py selbst, mit der Meldung
    # "enthält den fremden PartnerNet-Tag \"None\"". Gemessen, und zwar als Eigenschaft statt als Anzahl:
    # KEIN Vorkommen von `tag=` mit einem echten Affiliate-Wert steht ausserhalb von
    # `?`/`&`. Eine Anzahl stand hier als "19" und war nicht reproduzierbar (drei
    # Zaehlregeln: 30, 32, 39) -- sie ist entfernt, die Eigenschaft bleibt.
    _inhalt = open(_f, encoding='utf-8').read()
    for _tm in re.finditer(r'[?&]tag=([A-Za-z0-9_-]+)', _inhalt):
        if _tm.group(1) != 'ygmedia-21':
            err(f"§A3: {_f} enthält den fremden PartnerNet-Tag \"{_tm.group(1)}\" in "
                f"einem Kauflink — die Provision liefe auf ein anderes Konto")
    for _tm in re.finditer(r'AFFILIATE_TAG\s*[=:]\s*[\'"]([A-Za-z0-9_-]+)[\'"]', _inhalt):
        if _tm.group(1) != 'ygmedia-21':
            err(f"§A3: {_f} setzt AFFILIATE_TAG auf \"{_tm.group(1)}\" — jeder daraus "
                f"gebaute Kauflink liefe auf ein fremdes Konto")


# §A8: Custom Events NUR als dataLayer.push, NIE als gtag('event', ...). Das ist eine
# harte Regel in CLAUDE.md und war repoweit UNBEWACHT (Hinweis aus dem 24. Pruefbericht;
# gemessen: `gtag('event', ...)` in finder.js blieb gruen). Der heutige Stand ist korrekt,
# die Regel hatte nur kein Gate -- genau die Klasse, die dieses Paket schliesst.
#
# Zwei Praezisierungen, beide aus dem ersten Lauf dieses Gates:
#   · Nur die AUSGELIEFERTE Flaeche (Seiten und assets/js). Die erste Fassung lief ueber
#     alle Textdateien und meldete verify.py SELBST, weil das Muster in dieser Zeile
#     steht.
#   · KOMMENTARE heraus. `main.js` traegt in Zeile 352 den Hinweis "NICHT gtag('event',
#     ...)" -- eine Dokumentation der Regel, die das Gate als Verstoss gemeldet hat.
#     `gtag('consent', ...)` ist ausserdem Consent Mode und kein Custom Event; das Muster
#     verlangt deshalb ausdruecklich 'event'.

def _js_flaeche(_f):
    """Der JS-Code einer Datei: bei .js die Datei, bei HTML nur die <script>-Bloecke.

    Beides ohne Kommentare. Die erste Fassung entTagte HTML nur von `<!-- -->` -- und
    `gtag(` kann auf einer Seite NUR in einem <script> stehen, also genau dort, wo die
    Kommentar-Entfernung nicht griff. Zwei Fehlalarme (R26): eine Doku-Zeile in einem
    <script>-Kommentar und ein Satz in der Prosa, der die verbotene Form nennt. Prosa ist
    kein Code; sie wird jetzt gar nicht mehr gelesen.
    """
    _roh = open(_f, encoding='utf-8').read()
    if _f.endswith('.js'):
        return _ohne_kommentare(_roh, True)
    # Inline-Handler sind auch JS. Der Docstring behauptete "`gtag(` kann auf einer Seite
    # NUR in einem <script> stehen" -- das Repo widerlegt es selbst: controller/index.html
    # traegt fuenf `onclick=`/`onchange=`-Handler (R27). Ein gtag('event', ...) darin
    # laeuft und war vom Gate nicht gelesen.
    _aus = [_ohne_kommentare(_m.group(1), True) for _m in
             re.finditer(r'<script\b[^>]*>(.*?)</script>', _roh, re.S | re.I)]
    # Auch unquotierte Werte, und OHNE Kommentare: Der Docstring sagte "beides ohne
    # Kommentare", die on*-Attribute gingen aber roh durch -- ein Kommentar darin, der die
    # Regel dokumentiert, wurde als Verstoss gemeldet (R28, Fehlalarm). Und nur quotierte
    # Werte zu lesen war ein Loch.
    # HTML-Kommentare zuerst heraus: Ein auskommentierter Inline-Handler, der die Regel
    # dokumentiert, waere sonst ein Fehlalarm (Hinweis R29).
    _ohne_html_komm = re.sub(r'<!--.*?-->', ' ', _roh, flags=re.S)
    for _m in re.finditer(r'\son[a-z]+\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))',
                          _ohne_html_komm, re.I):
        _wert = html.unescape(_m.group(1) or _m.group(2) or _m.group(3) or '')
        _aus.append(_ohne_kommentare(_wert, True))
    return ' '.join(_x for _x in _aus if _x)


for _f in list(pages) + sorted(glob.glob('assets/js/*.js')):
    if not os.path.exists(_f):
        continue
    _ih = _js_flaeche(_f)
    # Backticks sind gueltiges JS und waren nicht erfasst (Hinweis R25).
    for _gm in re.finditer(r"gtag\s*\(\s*['\"`]event['\"`]", _ih):
        err(f"§A8: {_f} feuert ein Custom Event per gtag('event', ...) — erlaubt ist nur "
            f"dataLayer.push({{event: '...'}}), sonst greifen die GTM-Trigger und die "
            f"DLV-Namen (product_name, destination, platform, budget, prio) nicht")

# §A3 fuer die JS-Seite: Die Kauflinks entstehen aus data-asin in main.js. Eine hart
# geschriebene Amazon-URL in einer ANDEREN JS-Datei umgeht diese eine Stelle -- mit
# richtigem Tag blieb sie gruen (Hinweis aus dem 24. Pruefbericht). Das statische HTML
# prueft das Gate weiter oben; hier fehlte die JS-Seite.
for _f in sorted(glob.glob('assets/js/*.js')):
    if os.path.basename(_f) == 'main.js':
        continue   # DIE eine Stelle, die Kauflinks baut
    # Kommentare heraus: Das Gate las das Rohfile und haette einen Kommentar, der §A3
    # dokumentiert, als Verstoss gemeldet (R25). Dazu zwei weitere Formen aus demselben
    # Bericht: der SiteStripe-Kurzlink `amzn.to/...` traegt sein Tag unsichtbar, und
    # Die Formen stehen in _AMAZON_LINK, geteilt mit der Statik-Pruefung.
    _jh = _ohne_kommentare(open(_f, encoding='utf-8').read(), True)
    _mm = re.search(_AMAZON_LINK, _jh)
    if _mm:
        err(f"§A3: {_f} schreibt eine Amazon-URL direkt (\"{_mm.group(0)}\") — Kauflinks "
            f"entstehen ausschliesslich in assets/js/main.js aus data-asin, sonst gibt es "
            f"zwei Stellen, an denen der Affiliate-Tag richtig sein muss. Ein Kurzlink "
            f"(amzn.to) traegt sein Tag ausserdem unsichtbar, also greift auch die "
            f"Tag-Pruefung nicht")

# Der Footer nennt die Empfehlungsschwelle und wird in 111 Seiten injiziert. Er stand
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
# seit die Navigation statisch ausgeliefert wird, steht die Zahl auf fast jeder Seite statt auf
# einer Laufzeitstelle. Ein gefaelschtes zweites Vorkommen blieb damit unsichtbar.
# "Modelle verglichen" stand im SELBEN fb-stat-Block wie die geprueften Zahlen und nannte
# 40, waehrend der Finder damals 28 verglich. Die 40 stammte aus der Zeit von "40
# Produkte"; der Kommentar oben zitiert genau dieses Markup als Vorbild und hat die
# Nachbarzahl nicht mitgenommen.
# ZWEITER FEHLER, diesmal von mir selbst erzeugt: Am 02.10. habe ich den §A6-Filter in
# finder.js eingebaut, womit der Finder nur noch Modelle ab 3,8 vergleicht. Die Zahl sank
# damit von 28 auf 27, waehrend dieses Gate weiter aus dem Typ allein ableitete -- es
# verteidigte also die falsche Zahl gegen Korrektur, wortlich Mechanismus 6 des Patterns,
# das in diesem Paket neu geschrieben wurde. Abgeleitet wird jetzt so, wie der Finder
# filtert: Typ UND Bewertung ueber der Schwelle.
def _bew_wert(_p):
    _v = _spec_wie(_p, 'Bew')
    _m = re.match(r'([\d,.]+)', str(_v or ''))
    return float(_m.group(1).replace(',', '.')) if _m else None
_n_alle_ctrl = len([p for p in items if p.get('type') == 'controller'])
_n_controller = len([p for p in items if p.get('type') == 'controller'
                     and (_bew_wert(p) or 0) >= A6_SCHWELLE])
# Die Zahl der Finder-Fragen wird an mehreren Stellen als Versprechen genannt. Am 01.10.
# hat der B3-Lauf eine falsche Stelle korrigiert ("vier Fragen" in 404.html) und dabei
# behauptet, eine bestimmte Zahl von Stellen sage korrekt "3 Fragen" (die Zahl ist nicht reproduzierbar, siehe unten) -- eine sagte "5 Fragen", und keine
# Pruefung las sie.
#
# DREI VORFASSUNGEN, DREI FEHLER, und der dritte ist der Grund fuer die jetzige Form:
#  1. `.finder-step`-Elemente in index.html gezaehlt -- davon gibt es dort null, weil der
#     Finder per JS rendert. Stiller Leerlauf.
#  2. Jedes "N Fragen" im Repo als Finder-Aussage behandelt. Ein Satz ueber einen FREMDEN
#     Fragebogen wurde rot, und vier ausgelieferte Stellen blieben ungeprueft, weil sie
#     anders formuliert sind.
#  3. Nur noch gezaehlt, wo in +-400 Zeichen ein Finder-Bezug steht. Das ist zu grob: Auf
#     controller-finder/ liegen 75 % des Textes in dieser Reichweite, auf 404.html 56 %.
#     Der Pruefer hat die seiteneigene Leser-Checkliste in blog/huellen-kompatibilitaet von
#     drei auf vier Punkte erweitert -- eine gewoehnliche, danach WAHRE Redaktion -- und
#     das Gate wurde rot. Sieben von zwanzig wahren Saetzen waren betroffen. Gleichzeitig
#     blieben neun falsche Varianten gruen, darunter "in 4 kurzen Fragen" (die flektierte
#     Form, waehrend das Repo selbst "3 kurze Fragen" schreibt) und der ausgelieferte Satz
#     "Finder in drei Schritten", also dieselbe Zusage mit anderem Substantiv.
#
# Konsequenz, dieselbe wie bei den Mengensaetzen: Nicht jede moegliche Formulierung
# erkennen, sondern genau die Formen, die das Repo tatsaechlich benutzt. Gemessen gibt es genau
# diese; die beiden Checklisten-Saetze in huellen-kompatibilitaet unterscheiden sich im
# Wortlaut klar davon und werden deshalb nicht mehr beruehrt.
# GRENZE: Eine neu formulierte Zusage wird nicht geprueft. Der Anker darunter meldet, wenn
# eine der 9 Formen nirgends mehr steht; dann gehoert die neue Fassung hierher.
FINDER_JS = 'assets/js/finder.js'
# sieben/acht/neun fehlten, waehrend acht der zehn Muster sie zulassen: Der Wert kam
# als None zurueck, und die Richtigkeitspruefung sprang still ab.
_ZAHLWORT = {'zwei': 2, 'drei': 3, 'vier': 4, 'fünf': 5, 'fuenf': 5, 'sechs': 6,
             'sieben': 7, 'acht': 8, 'neun': 9, 'zehn': 10}
_FRAGEN_FORMEN = [
    (re.compile(r'in (\d+|[Zz]wei|[Dd]rei|[Vv]ier|[Ff]ünf|[Ss]echs|[Ss]ieben) Fragen die passenden Modelle'),
     'in N Fragen die passenden Modelle'),
    # `\d+ Sekunden` statt der harten 60: Die Dauer gehoert seit B12 zeitversprechen.py,
    # und eine zweite Kopie derselben Zahl liess verify auch dann rot bleiben, wenn die
    # Quelle geaendert UND der Sync gelaufen war -- mit einer Meldung, die auf die falsche
    # Datei zeigte. Dieses Muster prueft die FRAGENzahl, die Dauer prueft §A5/B12.
    (re.compile(r'\d+ Sekunden: (\d+|[Zz]wei|[Dd]rei|[Vv]ier|[Ff]ünf|[Ss]echs|[Ss]ieben) Fragen zu Handy'),
     'Meta-Description der Finder-Seite'),
    (re.compile(r'(\d+|[Zz]wei|[Dd]rei|[Vv]ier|[Ff]ünf|[Ss]echs|[Ss]ieben) kurze Fragen zu deinem Handy'),
     'Startseiten-Hero'),
    (re.compile(r'Beantworte (\d+|[Zz]wei|[Dd]rei|[Vv]ier|[Ff]ünf|[Ss]echs|[Ss]ieben) kurze Fragen'),
     'Finder-Seite, Aufforderung'),
    # Die faule Luecke dieser Form war die letzte Heuristik im Block und hat drei
    # wahre Saetze rot gemacht ("Unser Finder und diese Liste in vier Schritten
    # ergaenzen sich"). Ersetzt durch die eine konkrete Zusage, die sie gedeckt hat.
    (re.compile(r'Finder in (\d+|[Zz]wei|[Dd]rei|[Vv]ier|[Ff]ünf|[Ss]echs) '
                r'Schritten ab'),
     'Finder in N Schritten (was-ist-ein-smartphone-controller)'),
    # Hier steht Markup zwischen Name und Zahl: `Controller-Finder →</a> — 3 Fragen`.
    (re.compile(r'Controller-Finder\s*(?:→|&rarr;)?\s*(?:</a>)?\s*[—–-]?\s*'
                r'(\d+|[Zz]wei|[Dd]rei|[Vv]ier|[Ff]ünf|[Ss]echs|[Ss]ieben) Fragen'),
     'Finder-Link mit Zahl'),
    (re.compile(r'[Mm]atch in (\d+|[Zz]wei|[Dd]rei|[Vv]ier|[Ff]ünf|[Ss]echs|[Ss]ieben) Fragen'), 'Match-in-N-Fragen'),
    (re.compile(r'[Ii]n (\d+|[Zz]wei|[Dd]rei|[Vv]ier|[Ff]ünf|[Ss]echs|[Ss]ieben) Fragen zur Empfehlung'), '404-Kachel'),
    (re.compile(r'Controller-Finder: (\d+|[Zz]wei|[Dd]rei|[Vv]ier|[Ff]ünf|[Ss]echs|[Ss]ieben) Fragen'),
     'Kopfkommentar in finder.js'),
    # "Genau diese drei Punkte fragt unser Finder ab" -- steht sichtbar UND im
    # FAQPage-Schema. Der Nachbarsatz "Unsere Reviews bewerten alle drei Punkte" ist
    # KEINE Finder-Zusage, deshalb verlangt das Muster "fragt unser Finder ab".
    (re.compile(r'(\d+|[Zz]wei|[Dd]rei|[Vv]ier|[Ff]ünf|[Ss]echs|[Ss]ieben) Punkte '
                r'fragt unser Finder ab'),
     'FAQ der Finder-Seite, sichtbar und im Schema'),
]
# WO jede Form lebt. Runde 20 hat gezeigt, dass "irgendwo in der Datei" als Abdeckung
# nicht reicht: Die Zusage von der Startseite genommen und als JSON-LD-"slogan" hinterlegt
# liess den Anker erfuellt und die Seite stumm. Seitdem deckt eine Zusage nur dort, wo sie
# den Leser erreicht -- 'sichtbar' im Seitentext, 'meta' in der Description, 'quelle' fuer
# die Kopie im Quelltext, die ausdruecklich keine Leser-Zusage ist.
# Reihenfolge wie _FRAGEN_FORMEN. Die erste Fassung hatte acht Eintraege fuer zehn Formen
# -- das Gate direkt darunter hat das im ersten Lauf gemeldet.
_FORM_ORT = [
    'sichtbar',   # 0 "in N Fragen die passenden Modelle"
    'meta',       # 1 Meta-Description der Finder-Seite
    'sichtbar',   # 2 Startseiten-Hero
    'sichtbar',   # 3 Finder-Seite, Aufforderung
    'sichtbar',   # 4 "Finder in N Schritten" (was-ist-ein-smartphone-controller)
    'sichtbar',   # 5 Finder-Link mit Zahl
    'sichtbar',   # 6 "Match in N Fragen"
    'sichtbar',   # 7 404-Kachel
    'quelle',     # 8 Kopfkommentar in finder.js -- keine Leser-Zusage
    'sichtbar',   # 9 FAQ der Finder-Seite (steht sichtbar UND im Schema)
]
if len(_FORM_ORT) != len(_FRAGEN_FORMEN):
    err(f'§A5: _FORM_ORT hat {len(_FORM_ORT)} Eintraege, _FRAGEN_FORMEN hat '
        f'{len(_FRAGEN_FORMEN)} — jede Form muss sagen, wo sie lebt')
_fm = (re.search(r'const answers\s*=\s*\{([^}]*)\}', open(FINDER_JS, encoding='utf-8').read())
       if os.path.exists(FINDER_JS) else None)
if not _fm:
    err(f'§A5: das answers-Objekt in {FINDER_JS} ist nicht gefunden worden — die Zahl der '
        f'Finder-Fragen laesst sich nicht ableiten')
else:
    # In REIHENFOLGE, nicht nur die Anzahl: Die Schritte auf der Seite muessen den
    # Schluesseln in dieser Reihenfolge entsprechen, sonst steht eine Frage ueber fremden
    # Antworten (R21).
    _answers_keys = re.findall(r'(\w+)\s*:', _fm.group(1))
    _n_fragen = len(_answers_keys)
    if _n_fragen < 2:
        err(f'§A5: {FINDER_JS} ergibt {_n_fragen} Finder-Frage(n) — keine plausible '
            f'Ableitung, Struktur von answers geaendert?')
    _ft = [0] * len(_FRAGEN_FORMEN)
    for _f in _zu_pruefen:
        # Klartext plus Metas: `in <strong>9 Fragen</strong>` blieb vorher
        # ungeprueft, und die Zusage der Finder-Seite steht in der
        # Meta-Description, also in einem Attribut.
        _roh_f = open(_f, encoding='utf-8').read()
        _fh = _text_und_metas(_roh_f)
        _sicht = _klartext(_roh_f)
        _meta_f = _metatexte(_roh_f)
        for _i, (_mu, _was) in enumerate(_FRAGEN_FORMEN):
            _ort = _FORM_ORT[_i] if _i < len(_FORM_ORT) else 'quelle'
            _deckt = (_mu.search(_sicht) if _ort == 'sichtbar'
                      else _mu.search(_meta_f) if _ort == 'meta'
                      else _mu.search(_roh_f))
            for _m in _mu.finditer(_fh):
                # Gezaehlt wird nur, wo die Zusage den Leser erreicht (siehe _FORM_ORT).
                # Der WERT wird weiter ueberall geprueft, denn eine falsche Zahl ist auch
                # in einer Description und in einem Kommentar falsch.
                if _deckt and (_ort != 'sichtbar' or _f in pages):
                    _ft[_i] += 1
                _roh = _m.group(1)
                _ist = int(_roh) if _roh.isdigit() else _ZAHLWORT.get(_roh.lower())
                if _ist is not None and _ist != _n_fragen:
                    err(f'§A5: {_f} verspricht "{_m.group(0)[:60]}" ({_was}), der Finder '
                        f'stellt {_n_fragen} (answers-Objekt in {FINDER_JS})')
    for _i, (_mu, _was) in enumerate(_FRAGEN_FORMEN):
        if not _ft[_i]:
            err(f'§A5: die Finder-Zusage "{_was}" steht nirgends mehr im Repo — sie wurde '
                f'entfernt oder umformuliert. Dann gehoert die neue Fassung in '
                f'_FRAGEN_FORMEN in scripts/verify.py, sonst altert die Zahl ungeprueft')
    # Die Finder-SEITE zaehlt ihre Fragen selbst mit ("Frage 1 von 3") und baut sie als
    # statische Schritte. Beides war ungegatet: Ein kompletter vierter Schritt samt
    # "Frage 4 von 4" blieb gruen, und umgekehrt blieb die Seite bei "von 3" stehen,
    # nachdem eine vierte Frage in answers ergaenzt und alle 48 Textstellen nachgezogen
    # waren -- also genau am Ende des regulaeren, vom Gate abgesegneten Aenderungswegs.
    _FINDER_SEITE = 'controller-finder/index.html'
    if os.path.exists(_FINDER_SEITE):
        # Markup normalisieren, bevor gesucht wird: einfache Anfuehrungszeichen zu
        # doppelten, Leerraum um das Gleichheitszeichen weg, Inline-Tags aus dem
        # Zaehlertext entfernt. Ohne das meldete das Gate Fehler, die es nicht gibt --
        # Im Repo stehen 101 einfach gequotete `class`-Attribute (alles generierte
        # Seiten), und `Frage <b>1</b> von 3` ist gueltiges Markup. Die erste Fassung
        # dieses Kommentars bezog die 101 auf `class='finder-step'` -- diese Schreibweise
        # steht nirgends, die Zahl gehoert zu den Attributen insgesamt. Das Lesezeit-Gate
        # in derselben Datei hat dieses Problem laengst geloest; dieses hatte es nicht
        # uebernommen.
        _fs_roh = open(_FINDER_SEITE, encoding='utf-8').read()
        _fs = re.sub(r"(\w)\s*=\s*'([^']*)'", r'\1="\2"', _fs_roh)
        _fs = re.sub(r'(\w)\s*=\s*"', r'\1="', _fs)
        _fs = re.sub(r'Frage\s*(?:<[^>]*>\s*)*(\d+)\s*(?:<[^>]*>\s*)*\s*von\s*'
                     r'(?:<[^>]*>\s*)*(\d+)', r'Frage \1 von \2', _fs)
        # a) "Frage N von M": M muss die Fragenzahl sein, N darf sie nicht ueberschreiten
        _vonm = re.findall(r'Frage\s+(\d+)\s+von\s+(\d+)', _fs)
        if not _vonm:
            err(f'§A5: {_FINDER_SEITE} nennt keine "Frage N von M" mehr — die Zaehlung der '
                f'Seite war bisher gegen das answers-Objekt gebunden')
        for _nr, _ges in _vonm:
            if int(_ges) != _n_fragen:
                err(f'§A5: {_FINDER_SEITE} sagt "Frage {_nr} von {_ges}", der Finder stellt '
                    f'{_n_fragen} (answers-Objekt in {FINDER_JS})')
            elif int(_nr) > _n_fragen or int(_nr) < 1:
                err(f'§A5: {_FINDER_SEITE} sagt "Frage {_nr} von {_ges}" — die Nummer liegt '
                    f'ausserhalb von 1 bis {_n_fragen}')
        if len(_vonm) != _n_fragen:
            err(f'§A5: {_FINDER_SEITE} traegt {len(_vonm)} Fragen-Zaehler, der Finder '
                f'stellt {_n_fragen} Fragen')
        # b) die statischen Schritte und die Fortschrittspunkte
        for _kl, _was2 in (('finder-step', 'Frage-Abschnitte'),
                           ('fp-step', 'Fortschrittspunkte')):
            # Als TOKEN zaehlen, nicht per \b: `class="finder-step-alt"` wurde
            # mitgezaehlt, weil der Bindestrich eine Wortgrenze ist. Die Nachbesserung
            # aus Runde 19 war nur in der Anwesenheitspruefung 130 Zeilen weiter unten
            # gelandet, nicht hier -- eine von drei umbenannten Klassen hielt damit
            # beide Pruefungen gruen, waehrend zwei Fragen gleichzeitig sichtbar waren.
            _n_kl = sum(1 for _cm in re.finditer(r'class\s*=\s*(?:"([^"]*)"|\'([^\']*)\')', _fs)
                        if _kl in (_cm.group(1) or _cm.group(2) or '').split())
            if _n_kl != _n_fragen:
                err(f'§A5: {_FINDER_SEITE} hat {_n_kl} {_was2} ({_kl}), der Finder stellt '
                    f'{_n_fragen} Fragen')
        # c) jede Frage braucht ihre Antwortgruppe in answers
        _gruppen = set(re.findall(r'data-key="(\w+)"', _fs))
        _keys = set(re.findall(r'(\w+)\s*:', _fm.group(1)))
        if _gruppen != _keys:
            err(f'§A5: die Antwortgruppen auf {_FINDER_SEITE} ({sorted(_gruppen)}) '
                f'stimmen nicht mit answers in {FINDER_JS} ({sorted(_keys)}) ueberein')

# ---------------------------------------------------------------------------------------
# §A1/B12 · ANWESENHEITSPFLICHT LESEZEIT. Eigener Abschnitt mit Trennmarken, und zwar aus
# gegebenem Anlass: Dieser Block stand zuerst zwischen dem B12-Kommentar und dem
# Zeitversprechen-Gate, und beim Ersetzen des Nachbarblocks habe ich ihn mitgeloescht --
# verify blieb gruen, weil eine geloeschte Pruefung nichts meldet. Dasselbe ist dem
# Finder-§A6-Gate zwei Abschnitte weiter unten zweimal passiert, und die Lehre dazu stand
# schon da. Trennmarken sind billiger als die dritte Wiederholung.
#
# Das Lesezeit-Gate weiter unten prueft nur Seiten, die eine Lesezeit NENNEN. Eine Seite,
# die ihre wieder verliert, blieb damit stumm gruen (eigene Probe am 05.10.). Deshalb hier
# die Pflicht, abgeleitet statt aufgezaehlt: jede Produktseite aus products.json, alles
# unter /produkte/ (29 Datenblaetter plus 10 Longtail-Seiten) und jeder Blog-Artikel.
_b12_pflicht = {(_pfeld(_p, 'detail') or '').strip('/') + '/index.html' for _p in items
                if _pfeld(_p, 'detail')}
_b12_pflicht |= set(glob.glob('produkte/*/index.html'))
# glob('blog/*/index.html') trifft die Listenseite blog/index.html nicht, die liegt eine
# Ebene hoeher. Die erste Fassung filterte sie trotzdem heraus, und der Kommentar daneben
# erklaerte einen Filter, der nie etwas getan hat.
_b12_pflicht |= set(glob.glob('blog/*/index.html'))
for _f12 in sorted(_b12_pflicht):
    if not os.path.exists(_f12):
        continue            # fehlende Ziele meldet §A1 an seiner Stelle
    if not _lz_BYLINE.search(open(_f12, encoding='utf-8').read()):
        err(f'§A1/B12: {_f12} nennt keine Lesezeit. Jede PRODUKTSEITE und jeder '
            f'BLOG-ARTIKEL sagt vorher, wie lange er dauert (Fix: "python3 '
            f'scripts/sync_lesezeit.py" bzw. "gen_pages.py --regen" / "gen_longtail.py"). '
            f'Die Bestenlisten unter /vergleich/ und die Marken-Hubs tragen bewusst keine: '
            f'Sie werden ueberflogen, nicht gelesen')
# ---------------------------------------------------------------------------------------

# B12 (Hormozi, der Nenner der Wert-Gleichung): Das Zeitversprechen zum Finder steht an
# sieben Stellen und hat seit dem 05.10. EINE Quelle (scripts/zeitversprechen.py). Die
# erste Fassung suchte es repoweit per Muster und entschied am Umfeld, ob eine Zahl eine
# Finder-Zusage ist. Der Pruefer hat beide Richtungen zerlegt: fuenf Umformulierungen
# ("in zwei Minuten", "in 90 s", "in neunzig Sekunden", Zusage entfernt, Kachel ersetzt)
# blieben gruen, weil die uebrigen Stellen weiter 60 sagten -- und ein Fehlersuche-Artikel
# wurde faelschlich rot, weil "Wahl" und "Ergebnis" Alltagswoerter sind.
# Jetzt: zeichengleicher Vergleich gegen die gepflegte Zahl, Anwesenheitspflicht je
# Stelle, plus ein enger Sweep auf genau den zwei Seiten, auf denen jede Sekundenangabe
# eine Finder-Zusage ist. Ob 60 Sekunden stimmen, prueft das Gate ausdruecklich nicht.
if os.path.exists('scripts/sync_zeitversprechen.py'):
    _rz = _gate('sync_zeitversprechen.py', '--check')
    if _rz.returncode != 0:
        _zz = (_rz.stdout + _rz.stderr).strip().splitlines()
        err(f"§A5/B12: scripts/sync_zeitversprechen.py --check schlaegt fehl. Fix: "
            f"'python3 scripts/sync_zeitversprechen.py'. {_zz[-1][:160] if _zz else ''}")
else:
    err('scripts/sync_zeitversprechen.py fehlt — das Finder-Zeitversprechen ist ungegatet')

try:
    from zeitversprechen import STELLEN as _B12_STELLEN, pruefe as _b12_pruefe
except Exception as _e:                                       # pragma: no cover
    _B12_STELLEN = None
    err(f'§A5/B12: zeitversprechen.py nicht importierbar ({_e}) — das Zeitversprechen '
        f'ist ungegatet')
if _B12_STELLEN:
    for _dz in sorted({_d for _d, _, _ in _B12_STELLEN}):
        if not os.path.exists(_dz):
            err(f'§A5/B12: {_dz} fehlt, traegt aber eine Finder-Zusage')
            continue
        for _bz in _b12_pruefe(_dz, open(_dz, encoding='utf-8').read())[0]:
            err(f'§A5/B12: {_bz}')

# ---------------------------------------------------------------------------------------
# §A6 IM CONTROLLER-FINDER. Eigener Abschnitt mit Trennmarken, weil dieses Gate schon
# ZWEIMAL durch eine Block-Ersetzung im Nachbarbereich geloescht wurde, ohne dass etwas
# rot wurde (02.10., beide Male beim Umbau des Fragenzahl-Gates darueber). Beim zweiten
# Mal hatte ich die Lehre dazu eine Runde vorher selbst aufgeschrieben.
# Inhalt: Der Finder gibt Kaufempfehlungen aus, also darf kein Produkt unter der Schwelle
# in die Ergebnisse. Bis zum 02.10.2026 stand die 3.8 dort nur als Ranking-Gewicht, und
# STATUS behauptete trotzdem "Schwelle als benannte Konstante mit Filter vor der Ausgabe".
# Dass kein Modell unter 3,8 in die Top 3 kam, war ein Ergebnis der Gewichtung, keine
# Garantie (ueber alle 36 Antwortkombinationen, platform 3 x budget 4 x prio 3: 0 Faelle).
if os.path.exists(FINDER_JS):
    _fj_roh = open(FINDER_JS, encoding='utf-8').read()
    # Kommentare entfernen, BEVOR gesucht wird: Sonst genuegt es, die Filterzeile
    # auszukommentieren und eine kaputte daneben zu stellen.
    _fj = re.sub(r'/\*.*?\*/', ' ', _fj_roh, flags=re.S)
    _fj = re.sub(r'(?m)^\s*//.*$', ' ', _fj)
    _fk = re.findall(r'const A6_SCHWELLE\s*=\s*([\d.]+)', _fj)
    if not _fk:
        err(f'§A6: {FINDER_JS} hat keine aktive Konstante A6_SCHWELLE — die '
            f'Empfehlungsschwelle liegt dann wieder nur als Ranking-Gewicht im Code')
    elif len(_fk) > 1:
        err(f'§A6: {FINDER_JS} setzt A6_SCHWELLE {len(_fk)}x ({", ".join(_fk)}) — welche '
            f'gilt, ist nicht entscheidbar')
    elif float(_fk[0]) != A6_SCHWELLE:
        err(f'§A6: {FINDER_JS} nennt {_fk[0]} als Schwelle, verify.py prueft gegen '
            f'{A6_SCHWELLE}')
    # Der Filter muss IN renderResults stehen und ALLEIN in seinem Ausdruck: in eine nicht
    # aufgerufene Funktion verschoben wirkt er nicht, und `true || ...` entwertet ihn.
    _rr = re.search(r'function renderResults\s*\([^)]*\)\s*\{(.*?)\n  \}', _fj, re.S)
    if not _rr:
        err(f'§A6: renderResults() in {FINDER_JS} ist nicht gefunden worden — der Filter '
            f'gegen A6_SCHWELLE laesst sich nicht verorten')
    else:
        _rr_t = re.sub(r'\s+', ' ', _rr.group(1))
        # Der Parametername ist frei: `.filter(prod => ratingOf(prod) >= A6_SCHWELLE)`
        # wurde vorher als "filtert nicht" gemeldet, also mit falscher Ursache.
        if not re.search(r'\.filter\(\s*\(?\s*(\w+)\s*\)?\s*=>\s*ratingOf\(\s*\1\s*\)'
                         r'\s*>=\s*A6_SCHWELLE\s*\)', _rr_t):
            err(f'§A6: renderResults() in {FINDER_JS} filtert nicht allein gegen '
                f'A6_SCHWELLE — ein Produkt unter der Schwelle kann als Empfehlung '
                f'ausgespielt werden. Eine andere Schreibweise ist erlaubt, muss aber in '
                f'scripts/verify.py mitgezogen werden, sonst laeuft die Pruefung ins Leere')
    # Die Schrittgrenze in finder.js ist hart verdrahtet (`if (step < 2) show(step + 1)`).
    # Am Ende des vom Gate abgesegneten Aenderungswegs -- vierter Key in answers, vierter
    # Zaehler, vierter Abschnitt, alle Textstellen nachgezogen -- rendert der Finder nach
    # Frage 3 trotzdem das Ergebnis. Die Grenze muss zur Fragenzahl passen.
    _sg = re.search(r'if\s*\(\s*step\s*<\s*(\d+)\s*\)', _fj)
    if not _sg:
        err(f'§A5: die Schrittgrenze (`if (step < N)`) in {FINDER_JS} ist nicht gefunden '
            f'worden — ob der Finder alle Fragen zeigt, laesst sich nicht pruefen')
    elif int(_sg.group(1)) != _n_fragen - 1:
        err(f'§A5: {FINDER_JS} schaltet nur bis `step < {_sg.group(1)}` weiter, bei '
            f'{_n_fragen} Fragen muss die Grenze {_n_fragen - 1} sein — sonst wird die '
            f'letzte Frage nie gezeigt')

    # ratingOf muss die Bewertung noch lesen, sonst laeuft der Filter ins Leere. Die
    # erste Fassung sprang still ab, wenn das Funktionsmuster nicht traf: Als
    # `const ratingOf = (p) => 5;` geschrieben fiel die Pruefung wortlos aus.
    # Verlangt wird die Hausform `function ratingOf(...)`. Die Pfeilfunktion zuzulassen
    # war ein Loch: `const ratingOf = (p) => 5;` liess das Muster in den Rumpf der
    # NAECHSTEN Funktion laufen, dort stand "bew", und die Pruefung blieb gruen, waehrend
    # jeder Controller die Bewertung 5 bekam. Eine Umstellung auf Pfeilfunktion ist
    # erlaubt, muss aber hier mit angepasst werden -- derselbe Vertrag wie bei _SAETZE.
    if not re.search(r'function\s+ratingOf\s*\(', _fj):
        err(f'§A6: ratingOf() in {FINDER_JS} ist nicht mehr als `function ratingOf(...)` '
            f'deklariert. Erlaubt, aber dann muss die Pruefung in scripts/verify.py mit '
            f'angepasst werden, sonst laeuft sie ins Leere')
        _ro = None
    else:
        _ro = re.search(r'function\s+ratingOf\s*\([^)]*\)\s*\{(.*?)\n  \}', _fj, re.S)
    if _ro and not (re.search(r'bew', _ro.group(1), re.I)
                    and re.search(r'\bspecs\b', _ro.group(1))):
        # Die erste Fassung verlangte nur das Token "bew" im Rumpf. `function ratingOf(p)
        # { const bew = 5; return bew; }` blieb damit gruen, waehrend jeder Controller 5
        # bekam, der Filter nichts mehr ausschloss und die 27 auf der Seite falsch wurde.
        err(f'§A6: ratingOf() in {FINDER_JS} liest das Bew.-Feld nicht mehr aus den specs '
            f'— der Filter gegen A6_SCHWELLE laeuft dann ins Leere')

    _fp = 'scripts/finder_probe.js'
    _fseite = 'controller-finder/index.html'

    # DER VERTRAG ZWISCHEN SEITE UND SKRIPT WIRD AUSGEFUEHRT, NICHT GESUCHT.
    #
    # Drei Pruefrunden lang war das hier eine Sammlung von Mustern ueber Markup, und jede
    # Runde hat eine Nachbarform gefunden, die durchlief, waehrend der Finder auf der Seite
    # tot war:
    #   R18  Script-Tag entfernt · fuenf Element-Namen umbenannt
    #   R19  Script-Tag auskommentiert · in <noscript> · `data-step` umbenannt · Klasse mit
    #        Suffix umbenannt (\b trifft `finder-step-alt`) · `data-back` nur im CSS-Kommentar
    #   R20  `data-step` am FALSCHEN Element · `data-step` gedoppelt · Script-Tag im <head>
    #        ohne `defer` · Startzustand `is-active` entfernt
    # Jede dieser Formen war "Anwesenheit irgendwo" statt "wirkt". Deshalb wird die Seite
    # jetzt GEPARST (scripts/dom_baum.py), finder.js laeuft dagegen (scripts/finder_probe.js),
    # und geprueft werden die ZUSTAENDE: wie viele Schritte, welcher ist aktiv, welche
    # Schrittnummern tragen die Abschnitte, wie viele Karten erscheinen, was empfiehlt er.
    # Drei Dinge bleiben Quelltext-Pruefung, weil sie keinen Zustand erzeugen: die
    # Ladeordnung des Script-Tags, die CSS-Bindung der umgeschalteten Klasse und das
    # fetch-Ziel.
    #
    # WAS DIESE PRUEFUNG NICHT KANN -- benannt, nicht geschlossen, weil ein vollstaendiger
    # Browser-Nachbau der Regress waere, vor dem Lehre 174 warnt (alle vom Pruefer in
    # Runde 21 gemessen und als gruen belegt):
    #   · CSS: Die Auswertung steht in scripts/css_kaskade.py und rechnet Spezifitaet,
    #     `!important`, Attribut-Selektoren, `:not()` und At-Regeln mit. WAS SIE NICHT
    #     KANN, steht im Docstring DIESES Moduls und nur dort -- hier stand lange eine
    #     zweite, veraltete Liste, die vier inzwischen geschlossene Punkte als offen
    #     fuehrte (R26). Zwei widersprechende GRENZEN-Bloecke in einer Funktion sind
    #     schlimmer als keiner: Wer den ersten liest, hoert auf zu lesen.
    # Geprueft wird dagegen alles, was im geparsten Baum steht: `disabled` (auch am
    # <fieldset>), `hidden`, inline `display`/`visibility`, `aria-hidden`, die Zuordnung
    # Frage zu Antwortgruppe, der Karteninhalt und das fetch-Ziel.
    _fp = 'scripts/finder_probe.js'
    _fseite = 'controller-finder/index.html'
    _CSS = 'assets/css/style.css'

    if not os.path.exists(_fp) or not os.path.exists('scripts/dom_baum.py'):
        err(f'§A6: {_fp} oder scripts/dom_baum.py fehlt — der Finder wird dann nur noch '
            f'im Quelltext gelesen, nicht ausgefuehrt')
    elif os.path.exists(_fseite):
        _fsh_roh = open(_fseite, encoding='utf-8').read()

        # 1 · LADEORDNUNG. Erzeugt keinen Zustand, den der Harness sehen koennte: Im
        # <head> ohne `defer` ist #finder beim Lauf noch nicht geparst, finder.js kehrt in
        # Zeile 6 wortlos zurueck, kein Klick wirkt, keine Fehlermeldung. (R20 gemessen.)
        from dom_baum import baum as _dom_baum, ladeordnung as _ladeordnung
        _lo, _ = _ladeordnung(_fsh_roh, FINDER_JS)
        if _lo == 'fehlt':
            err(f'§A5: {_fseite} laedt {FINDER_JS} nicht per <script src> (ausserhalb von '
                f'Kommentar, <template> und <noscript>) — der Finder laeuft dann gar '
                f'nicht, waehrend die Seite seine Leistung zusagt')
        elif _lo == 'vor':
            err(f'§A5: {_fseite} laedt {FINDER_JS} VOR dem Element id="finder" und ohne '
                f'`defer` — das Skript findet den Finder dann nicht und kehrt wortlos '
                f'zurueck. Script-Tag ans Ende des <body> oder `defer` setzen')
        elif _lo == 'async':
            err(f'§A5: {_fseite} laedt {FINDER_JS} mit `async` — ob #finder dann schon '
                f'geparst ist, ist ein Wettlauf. `defer` setzen oder das Tag ans Ende '
                f'des <body>')

        # 2 · CSS-BINDUNG, als KASKADE und fuer JEDES Element auf dem Weg.
        # Zwei Fassungen vorher, zwei Befunde: Die erste suchte IRGENDEINE Regel (R21: eine
        # spaetere Regel gewinnt, Finder leer, Lauf gruen). Die zweite nahm die letzte
        # passende Regel, fragte aber nur `.finder-step` und `.finder-result` ab und
        # verlangte, dass der ganze Selektor eine einfache Klassenkette ist. R22 hat damit
        # BEIDE Richtungen gezeigt: `.finder-options{display:none}` am Ende von style.css
        # blieb gruen (Nachbarelement, gleiche Schadensform), und ein voellig korrektes
        # `#finder .finder-step{display:none}` wurde rot mit falscher Begruendung.
        # Jetzt steht die Auswertung in scripts/css_kaskade.py: Spezifitaet ueber alle
        # Verbundgruppen, Attribut-Selektoren, `:not()`, At-Regeln, `!important`. Abgefragt
        # wird jede Klasse, ID und jeder Tag-Name auf dem Weg von #finder bis zu den
        # Schritten, dem Ergebnis und den Antwort-Knoepfen; diese Ketten kommen aus dem
        # geparsten Baum, nicht aus einer Liste hier.
        #
        # WAS DIE AUSWERTUNG NICHT KANN, steht im Docstring von scripts/css_kaskade.py und
        # NUR DORT. Hier stand bis Runde 27 eine zweite Liste, die vier inzwischen
        # geschlossene Punkte als offen fuehrte -- und zwar 45 Zeilen unter dem Satz, der
        # genau das verbietet. Ich habe beide Bloecke in derselben Arbeit geschrieben: den
        # richtigen Verweis und die veraltete Liste darunter. Wer die Liste liest, haelt
        # @media, Spezifitaet, !important und visibility/opacity fuer unbewacht und baut
        # sie zum vierten Mal.
        # Die Budget-Schwellen AUS score() lesen, nicht tippen: Die Beschriftungen
        # ("Bis 50 €", "50-100 €", "Über 100 €") nennen genau diese Zahlen, und wenn die
        # Logik sich verschiebt, muessen sie mit. Abgeleitet aus den Bedingungen
        # `answers.budget === 'x' && price <= N`.
        _BUDGET_GRENZEN = {}
        for _bm in re.finditer(r"answers\.budget\s*===\s*'(\w+)'([^;]*);", _fj):
            _BUDGET_GRENZEN[_bm.group(1)] = set(re.findall(r'price\s*[<>]=?\s*(\d+)',
                                                           _bm.group(2)))

        # Die CSS-Quellen: das Stylesheet UND der <style>-Block der Seite. Die
        # Auswertung selbst (Spezifitaet, Attribut-Selektoren, :not(), At-Regeln,
        # !important) steht in scripts/css_kaskade.py, mit Falltabelle. Was sie nicht
        # kann, steht im Docstring DIESES Moduls -- und nur dort.
        # Dieser Aufbau stand hier einmal doppelt (toter Code, Hinweis R26).
        _css_quellen = []
        if os.path.exists(_CSS):
            _css_quellen.append((_CSS, open(_CSS, encoding='utf-8').read()))
        for _sm in re.finditer(r'<style\b[^>]*>(.*?)</style>', _fsh_roh, re.S | re.I):
            _css_quellen.append((f'{_fseite} (<style>)', _sm.group(1)))
        _umschaltet = sorted(set(re.findall(r"classList\.toggle\(\s*'([\w-]+)'", _fj)
                                 + re.findall(r'classList\.toggle\(\s*"([\w-]+)"', _fj)))

        def _sichtbar(_eintrag, _zusatz=()):
            return _css_sichtbar(_css_quellen, _eintrag, _zusatz)

        # 3 · FETCH-ZIEL. Nicht nur "die Datei existiert": R21 hat den Pfad auf
        # longtail.json gezeigt -- Datei vorhanden, Lauf gruen, und der Finder zeigte fuer
        # JEDE Kombination "Keine perfekte Uebereinstimmung", also genau das Schadensbild,
        # das die Meldung dieser Pruefung wortwoertlich ankuendigt. Der Harness laedt
        # inzwischen GENAU diesen Pfad, die Ausfuehrungsprobe unten faellt also mit auf;
        # hier wird zusaetzlich geprueft, dass die Datei die Felder fuehrt, die der Finder
        # liest. Beides zusammen, weil die Meldung sonst nur "keine Empfehlung" sagt und
        # nicht, woran es liegt.
        _ff = [_x for _x in re.findall(r'fetch\(\s*[\'"](/[^\'"]+)[\'"]', _fj)]
        for _fu in _ff:
            _lokal = _fu.lstrip('/')
            if not os.path.exists(_lokal):
                err(f'§A5: {FINDER_JS} laedt {_fu}, diese Datei gibt es nicht — der '
                    f'Finder bleibt dann ohne Produkte und zeigt dauerhaft '
                    f'"Keine perfekte Übereinstimmung"')
                continue
            try:
                _dd = json.load(open(_lokal, encoding='utf-8'))
            except Exception as _e:
                err(f'§A5: {FINDER_JS} laedt {_fu}, das kein lesbares JSON ist ({_e})')
                continue
            _FELDER_FINDER = ('slug', 'type', 'specs', 'price')
            _ok = (isinstance(_dd, list) and _dd
                   and all(isinstance(_x, dict) for _x in _dd)
                   and any(all(_k in _x for _k in _FELDER_FINDER) for _x in _dd)
                   and any(_x.get('type') == 'controller' for _x in _dd))
            if not _ok:
                err(f'§A5: {FINDER_JS} laedt {_fu}, aber dort steht nicht der '
                    f'Produktbestand: der Finder braucht Einträge mit '
                    f'{", ".join(_FELDER_FINDER)} und mindestens einen vom Typ '
                    f'"controller". Mit dieser Datei zeigt er fuer jede Antwort '
                    f'"Keine perfekte Übereinstimmung"')

        import shutil as _shutil
        if not _shutil.which('node'):
            # Sichtbar statt stumm: ohne node laeuft diese Pruefung nicht, und das muss
            # im Lauf stehen. err() waere falsch, weil node keine Zusage dieses Repos ist.
            warn(f'§A6: node fehlt — der Finder wurde NICHT ausgefuehrt. Der Vertrag '
                 f'zwischen {_fseite} und {FINDER_JS} und die Wirkung des '
                 f'§A6-Filters sind in diesem Lauf ungeprueft')
        else:
            def _finder_lauf(_nutzlast):
                try:
                    _pr = subprocess.run([_shutil.which('node'), _fp], input=json.dumps(
                        _nutzlast), capture_output=True, text=True, timeout=180)
                except subprocess.TimeoutExpired:
                    return {'fehler': 'node hat nach 180 s nicht geantwortet'}
                try:
                    return json.loads(_pr.stdout or '{}')
                except Exception as _e:
                    return {'fehler': f'Ausgabe unlesbar ({_e}): {_pr.stdout[:200]} '
                                      f'{_pr.stderr[:300]}'}

            _dom = _dom_baum(_fsh_roh)
            _b = _finder_lauf({'dom': _dom})
            if _b.get('fehler'):
                err(f'§A6: die Ausfuehrungsprobe des Finders ist fehlgeschlagen: '
                    f'{str(_b["fehler"])[:300]}')
            elif _b.get('startfehler'):
                err(f'§A6: {FINDER_JS} stuerzt beim Start gegen {_fseite} ab '
                    f'({_b["startfehler"][:120]}) — der Finder reagiert dann auf keinen '
                    f'Klick')
            elif _b.get('kein_finder'):
                err(f'§A5: {_fseite} fuehrt kein Element id="finder" — {FINDER_JS} kehrt '
                    f'wortlos zurueck, der Finder ist tot, die Seite sagt seine Leistung '
                    f'aber weiter zu')
            else:
                # a) Die Elemente, die finder.js braucht, in der WIRKUNG geprueft.
                for _feld, _was in (('hat_ergebnis', '.finder-result in #finder'),
                                    ('hat_grid', 'id="finderMatches"'),
                                    ('hat_titel', 'id="finderResultTitle"'),
                                    ('hat_neustart', 'id="finderRestart"')):
                    if not _b.get(_feld):
                        err(f'§A5: {_fseite} fuehrt {_was} nicht — {FINDER_JS} greift '
                            f'darauf zu und bricht dort ab')
                if _b.get('schritte') != _n_fragen:
                    err(f'§A5: im geparsten {_fseite} findet {FINDER_JS} '
                        f'{_b.get("schritte")} .finder-step-Abschnitte, es stellt aber '
                        f'{_n_fragen} Fragen')
                if _b.get('fragen') != _n_fragen:
                    err(f'§A5: die Antwort-Schaltflaechen auf {_fseite} ergeben '
                        f'{_b.get("fragen")} Fragengruppen, {FINDER_JS} kennt '
                        f'{_n_fragen}')
                # JEDER Schritt traegt genau eine Antwortgruppe, und zwar die, die an
                # dieser Stelle in `answers` steht. R21 hat die Antwortgruppen von
                # Schritt 2 und 3 vertauscht: Die Budget-Ueberschrift stand ueber den
                # Prioritaets-Antworten, und alle Zustaende blieben korrekt, weil die
                # Gruppen nur nach Schluessel gebildet wurden.
                _kjs = _b.get('keys_je_schritt') or []
                _soll_keys = [[_k] for _k in _answers_keys]
                if _kjs != _soll_keys:
                    err(f'§A5: die Antwortgruppen liegen je Schritt bei {_kjs}, erwartet '
                        f'ist {_soll_keys} — die Reihenfolge der Schritte auf {_fseite} '
                        f'muss der Reihenfolge in `answers` ({", ".join(_answers_keys)}) '
                        f'folgen, sonst steht eine Frage ueber fremden Antworten')
                if _b.get('knoepfe_in_schritten') != _b.get('knoepfe'):
                    err(f'§A5: {_b.get("knoepfe")} .finder-opt-Schaltflaechen auf '
                        f'{_fseite}, aber nur {_b.get("knoepfe_in_schritten")} liegen in '
                        f'einem .finder-step — die uebrigen gehoeren zu keiner Frage')
                # Deaktiviert = fuer den Leser nicht benutzbar. Der Harness ruft den
                # Handler deshalb nicht auf; ohne diese Meldung waere das Ergebnis nur
                # "keine Empfehlung" und nicht die Ursache. (R21, im Browser belegt.)
                if _b.get('knoepfe_deaktiviert'):
                    err(f'§A5: {_b["knoepfe_deaktiviert"]} Antwort-Schaltflaeche(n) auf '
                        f'{_fseite} sind `disabled` (am Knopf oder an einem <fieldset>) — '
                        f'der Leser kann den Finder dann nicht bedienen, waehrend die '
                        f'Seite seine Leistung zusagt')
                # Unsichtbar ohne Stylesheet: hidden, inline display/visibility,
                # aria-hidden. Diese drei stehen im Baum und brauchen keinen
                # CSS-Interpreter, deshalb werden sie geprueft (R21).
                if _b.get('finder_versteckt'):
                    err(f'§A2/§A5: der Finder-Bereich auf {_fseite} ist versteckt '
                        f'({_b["finder_versteckt"]}) — weder mit noch ohne JavaScript '
                        f'sichtbar')
                if _b.get('schritte_versteckt'):
                    err(f'§A2/§A5: Frage-Abschnitte auf {_fseite} sind versteckt '
                        f'({", ".join(_b["schritte_versteckt"])}) — der Leser sieht die '
                        f'Frage nicht')
                # Zurueck-Knoepfe: einer je Schritt ausser dem ersten, abgeleitet aus
                # der Fragenzahl. Und sie muessen WIRKEN -- R19 hat `data-back` von den
                # Knoepfen entfernt und das Wort in einem CSS-Kommentar gelassen, womit
                # die Mustersuche erfuellt und die Knoepfe tot waren.
                if _b.get('zurueck') != _n_fragen - 1:
                    err(f'§A5: {_fseite} fuehrt {_b.get("zurueck")} Zurueck-Schaltflaechen '
                        f'([data-back]), erwartet ist eine je Schritt ausser dem ersten, '
                        f'also {_n_fragen - 1}')
                elif _b.get('zurueck_mit_handler') != _b.get('zurueck'):
                    err(f'§A5: nur {_b.get("zurueck_mit_handler")} von '
                        f'{_b.get("zurueck")} Zurueck-Schaltflaechen bekommen von '
                        f'{FINDER_JS} einen Klick-Handler')
                elif _b.get('zurueck_wirkt') is not True:
                    err(f'§A5: die Zurueck-Schaltflaeche fuehrt nicht zum vorhergehenden '
                        f'Schritt (gemessen durch Ausfuehrung gegen {_fseite}) — der '
                        f'Leser kommt dann nicht zurueck')
                if _b.get('knoepfe_ohne_key'):
                    err(f'§A5: {_b["knoepfe_ohne_key"]} .finder-opt-Schaltflaeche(n) auf '
                        f'{_fseite} haben kein data-key oder kein data-value — ihr Klick '
                        f'beantwortet keine Frage')
                # a2) CSS-KASKADE ueber die Ketten aus dem geparsten Baum.
                _kt = _b.get('ketten') or {}
                _AK = _b.get('aktiv_klasse') or 'is-active'
                # Der Finder selbst und alle Vorfahren auf dem Weg muessen sichtbar sein.
                for _rolle, _ketten in (('der Finder-Bereich', [_kt.get('finder')]),
                                        ('ein Frage-Abschnitt', _kt.get('schritte') or []),
                                        ('das Ergebnis', [_kt.get('ergebnis')]),
                                        ('eine Antwort-Schaltflaeche', _kt.get('knoepfe') or [])):
                    for _kette in _ketten:
                        if not _kette:
                            continue
                        for _i2, _e in enumerate(_kette):
                            _eigen = (_i2 == 0)
                            # Ob ein Element umgeschaltet wird, sagt der Harness (er hat
                            # die echten Knoten), nicht eine Klassenliste hier. Und es
                            # gilt auch fuer VORFAHREN: Die Antwort-Knoepfe von Schritt 2
                            # und 3 liegen unter einem `.finder-step` ohne die aktive
                            # Klasse, also korrekt versteckt -- die erste Fassung hat sie
                            # als Defekt gemeldet.
                            if _e.get('u'):
                                # Ohne die aktive Klasse MUSS er versteckt sein, mit ihr
                                # MUSS er sichtbar sein. Das Element wird dafuer mit
                                # SEINEN Attributen uebergeben, nicht nur mit Klassen:
                                # `.finder-step[data-step]{display:none}` war sonst
                                # unsichtbar fuer diese Pruefung (R24).
                                _ohne = set(_e['c']) - {_AK}
                                _e_ohne = dict(_e); _e_ohne['c'] = sorted(_ohne)
                                _d, _offen = _css_wert(_css_quellen, _e_ohne, 'display')
                                # Nur melden, was das Ergebnis aendern koennte: Eine
                                # unentscheidbare Regel mit demselben Wert wie die
                                # geltende kippt nichts (R29).
                                _ist_none = bool(_d) and _d[0].strip().lower() == 'none'
                                _offen = [x for x in _offen
                                          if (x[0].strip().lower() == 'none') != _ist_none]
                                if _offen:
                                    err(f'§A2/§A5: eine CSS-Regel fuer '
                                        f'`.{".".join(sorted(_ohne))}` ist nicht '
                                        f'entscheidbar (`{_offen[0][2]}` in '
                                        f'{_offen[0][1]}) — das Gate kann fuer dieses '
                                        f'Element nichts zusichern. `:has()` haengt am '
                                        f'Teilbaum darunter, den die Probe nicht liefert')
                                if not _d or _d[0].lower() != 'none':
                                    err(f'§A2/§A5: `.{".".join(sorted(_ohne))}` wird nicht '
                                        f'per `display: none` versteckt (letzte passende '
                                        f'Regel: {_d[0] if _d else "keine"}'
                                        f'{" in " + _d[1] + " via " + _d[2] if _d else ""})'
                                        f' — dann stehen alle Schritte gleichzeitig auf '
                                        f'der Seite, egal was {FINDER_JS} umschaltet')
                                _ok, _d2 = _sichtbar(_e, {_AK})
                                if not _ok:
                                    err(f'§A2/§A5: `.{".".join(sorted(set(_e["c"]) | {_AK}))}` '
                                        f'wird von der geltenden Regel versteckt (Spezifitaet, dann Reihenfolge) '
                                        f'({_d2[0]} in {_d2[1]} via {_d2[2]}), '
                                        f'{FINDER_JS} schaltet aber `{_AK}` um — der '
                                        f'umgeschaltete Zustand hat dann keine Wirkung, '
                                        f'auch ohne JavaScript')
                                continue
                            _ok, _d2 = _sichtbar(_e)
                            if not _ok:
                                _wer = ('das Element selbst' if _eigen
                                        else 'ein Vorfahr davon')
                                # Die URSACHE aus _sichtbar nennen, nicht `display: none`
                                # behaupten: Bei `visibility:hidden` und `opacity:0` stand
                                # vorher die falsche Eigenschaft in der Meldung (R25).
                                err(f'§A2/§A5: {_rolle} ist per CSS versteckt — {_wer} '
                                    f'(`{_d2[2]}` in {_d2[1]}) setzt `{_d2[0]}`, und das '
                                    f'ist nach Spezifitaet und Reihenfolge die geltende '
                                    f'Regel. Der Finder ist dann unbenutzbar, mit und '
                                    f'ohne JavaScript')

                # a3) Beschriftung gegen data-value. R22: ios/android vertauscht, die
                # Beschriftungen unveraendert -- ein Leser mit iPhone drueckte "iPhone"
                # und bekam die Android-Auswahl, Lauf gruen.
                # Beschriftung gegen Wert, fuer ALLE drei Fragen. Die erste Fassung
                # deckte nur die Plattform; R23 hat die Werte der dritten Frage rotiert --
                # der Leser drueckte "Beste Qualitaet" und bekam die Rangfolge fuer
                # "Kompakt fuer unterwegs", Lauf gruen. Dieselbe Defektform wie der
                # Blocker, der diese Pruefung erzwungen hat, drei Zeilen daneben.
                # VERTRAG wie bei _SAETZE: Diese Zuordnung ist redaktionell, nicht
                # ableitbar. Wer eine Beschriftung umformuliert, zieht das Muster hier mit
                # -- sonst laeuft die Pruefung ins Leere, und DAS meldet der Anker darunter.
                _WORT = {'ios': r'iPhone|iOS', 'android': r'Android',
                         'quality': r'Qualit|Präzision|Praezision',
                         'value': r'Preis-Leistung|Preis/Leistung|Preis-Leistungs',
                         'portable': r'[Kk]ompakt|unterwegs|[Pp]ortabel'}
                _wort_treffer = 0
                for _o in _b.get('optionen') or []:
                    _mu2 = _WORT.get((_o.get('value') or '').lower())
                    if _mu2:
                        _wort_treffer += 1
                    if _mu2 and not re.search(_mu2, _o.get('text') or '', re.I):
                        err(f'§A5: die Antwort-Schaltflaeche "{(_o.get("text") or "")[:30]}" '
                            f'auf {_fseite} traegt data-value="{_o.get("value")}" — '
                            f'Beschriftung und Wert gehoeren nicht zusammen, der Leser '
                            f'waehlt etwas anderes als er liest')
                    # Die Budget-Beschriftungen nennen Zahlen; sie muessen zu den
                    # Schwellen in score() passen.
                    # (Anker fuer die Wort-Zuordnung steht nach der Schleife.)
                    if (_o.get('key') == 'budget' and _o.get('value') in _BUDGET_GRENZEN):
                        _soll_z = _BUDGET_GRENZEN[_o['value']]
                        _zahlen = set(re.findall(r'(\d+)', _o.get('text') or ''))
                        if _soll_z and not (_soll_z & _zahlen):
                            err(f'§A5: die Budget-Schaltflaeche '
                                f'"{(_o.get("text") or "")[:30]}" nennt {sorted(_zahlen)}, '
                                f'die Schwelle fuer "{_o["value"]}" in {FINDER_JS} ist '
                                f'{sorted(_soll_z)} — Beschriftung und Logik gehen '
                                f'auseinander')

                # Anker: Jeder Wert, zu dem ein Wortmuster existiert, muss auch
                # vorkommen. Sonst deckt eine Umbenennung der Werte die Pruefung still ab.
                _werte = {(_o.get('value') or '').lower() for _o in _b.get('optionen') or []}
                _fehlt_wort = sorted(set(_WORT) - _werte)
                if _fehlt_wort:
                    err(f'§A5: zu den Antwortwerten {_fehlt_wort} fuehrt verify.py ein '
                        f'Beschriftungsmuster, aber {_fseite} kennt diese Werte nicht '
                        f'mehr — entweder wurden sie umbenannt (dann _WORT in '
                        f'scripts/verify.py mitziehen) oder die Antwort ist weg')

                # b) Die Schrittnummern muessen 0..n-1 GENAU EINMAL vorkommen. R20:
                # `data-step` an den Frage-Abschnitten entfernt (das Attribut stand
                # weiter an den Fortschrittspunkten, also war "irgendwo vorhanden"
                # erfuellt) und `data-step="2"` auf "1" gedoppelt -- beide Male blieb der
                # Lauf gruen, und nach der ersten Antwort war der Finder-Bereich LEER.
                _sw = _b.get('step_werte') or []
                if sorted(_sw, key=lambda x: (x is None, x)) != [str(_i) for _i in range(_n_fragen)]:
                    err(f'§A5: die data-step-Werte der Frage-Abschnitte in {_fseite} sind '
                        f'{_sw}, erwartet ist jede Zahl von 0 bis {_n_fragen - 1} genau '
                        f'einmal — sonst ist `+s.dataset.step` undefined oder doppelt, '
                        f'und es wird kein oder mehr als ein Schritt angezeigt')
                # c) Startzustand: genau ein Schritt aktiv, auch ohne JavaScript (§A2).
                # finder.js ruft beim Laden kein show(0); fehlt `is-active` im Markup,
                # ist keine Frage sichtbar, mit und ohne JS.
                if _b.get('aktiv_start') != [0]:
                    err(f'§A2/§A5: beim Ausliefern von {_fseite} sind die Schritte '
                        f'{_b.get("aktiv_start")} aktiv, erwartet ist genau der erste '
                        f'([0]). {FINDER_JS} schaltet beim Laden nichts ein, also zeigt '
                        f'die Seite sonst keine Frage — auch ohne JavaScript nicht')
                # d) Nach jedem Klick genau ein Schritt aktiv, nach dem letzten das
                # Ergebnis. Ueber alle Kombinationen, schlechtester Zustand gewinnt.
                # ALLE beobachteten Werte je Position, nicht nur den ersten Weg: Die
                # erste Fassung uebernahm einen spaeteren Wert nur, wenn er != 1 war --
                # an der LETZTEN Position ist der Defektwert aber 1 (die Frage bleibt
                # neben dem Ergebnis stehen), also war dort jede Kombination ausser der
                # ersten blind (R22, 12 der 36 Faelle).
                _ajp = _b.get('aktiv_je_position') or []
                _soll_ank = [1] * (_n_fragen - 1) + [0]
                if len(_ajp) != len(_soll_ank) or any(
                        set(_ajp[_i]) != {_soll_ank[_i]} for _i in range(len(_ajp))):
                    err(f'§A5: nach den Klicks sind je Position {_ajp} Schritte aktiv '
                        f'(alle beobachteten Werte ueber {_b.get("kombis")} '
                        f'Kombinationen), erwartet ist genau {_soll_ank} — nach jeder '
                        f'Antwort eine Frage, nach der letzten keine und dafuer das '
                        f'Ergebnis')
                if _b.get('ergebnis_aktiv_am_ende') != [True]:
                    err(f'§A5: das Ergebnis von {FINDER_JS} wird nicht in jeder '
                        f'Antwortkombination angezeigt (is-active am Ende: '
                        f'{_b.get("ergebnis_aktiv_am_ende")})')
                # e) Die Trefferzahl wird GEMESSEN, nicht aus dem Quelltext gelesen. Das
                # Muster `.slice(0, N)` war zweimal ein Stellvertreter: erst traf es die
                # Spec-Chip-Zeile, dann ein dekoratives slice innerhalb der ranked-Kette.
                # Beide Male las das Gate 3, waehrend der Finder 27 Karten ausgab.
                # Eine Karte ohne Kauflink ist keine Empfehlung, sondern ein leeres
                # <article>. R21 hat die Kartenvorlage ausgehoehlt und nur
                # `data-product` stehen gelassen: Die Probe meldete weiter 3 Karten, im
                # Browser standen drei leere Kaesten ohne ein einziges data-asin -- die
                # Geldleitung aus dem Finder war weg (§A3).
                if _b.get('karten_ohne_asin'):
                    err(f'§A3: {_b["karten_ohne_asin"]} der vom Finder erzeugten Karten '
                        f'tragen kein data-asin — aus ihnen entsteht kein Affiliate-Link')
                if _b.get('karten_ohne_text'):
                    err(f'§A5: {_b["karten_ohne_text"]} der vom Finder erzeugten Karten '
                        f'haben praktisch keinen sichtbaren Inhalt — der Leser sieht eine '
                        f'leere Empfehlung')
                # Leeres Ergebnis nur mit dem Ausweichtitel. R22: ein Antwortzweig
                # lieferte 0 Karten, waehrend der Titel "Deine Top 3 Empfehlungen"
                # versprach -- 9 der 36 Kombinationen, und jedes berichtete Feld stand auf
                # seinem guten Wert, weil nur das MAXIMUM der Kartenzahl gemessen wurde.
                _fbm = re.search(r"title\.textContent\s*=\s*'([^']+)'", _fj)
                _ausweich = _fbm.group(1) if _fbm else None
                if not _ausweich:
                    err(f'§A5: der Ausweichtitel fuer "keine Treffer" ist in {FINDER_JS} '
                        f'nicht gefunden worden — ob ein leeres Ergebnis als solches '
                        f'benannt wird, laesst sich nicht pruefen')
                for _paar in _b.get('paare') or []:
                    _nz, _titel = _paar.split('|', 1)
                    if int(_nz) == 0 and _ausweich and _titel.strip() != _ausweich:
                        err(f'§A5: eine Antwortkombination zeigt KEINE Karte, der Titel '
                            f'sagt aber "{_titel[:50]}" statt "{_ausweich}" — der Leser '
                            f'liest eine Empfehlung und sieht nichts')
                    elif int(_nz) and _ausweich and _titel.strip() == _ausweich:
                        err(f'§A5: eine Antwortkombination zeigt {_nz} Karte(n), der Titel '
                            f'sagt aber "{_ausweich}"')
                # Die PLATTFORM-Zusage je Kombination gegen worksOn. R23: Faellt der
                # Filter `else return -1` aus score(), empfiehlt der Finder einem
                # iPhone-Nutzer den 8BitDo Ultimate 2C (worksOn android/universal, und das
                # Repo sagt an mehreren Stellen "Kein iOS-Support") -- Lauf gruen. Lauf 22
                # hatte das als Grenze eingeordnet, aber die Maschinerie liegt bereits
                # vollstaendig vor: Antworten und Empfehlungen je Kombination plus worksOn.
                # Eine Grenze, die nichts Schweres verdeckt, ist keine (Lehre 189).
                for _kk in _b.get('je_kombi') or []:
                    _plat = (_kk.get('antworten') or {}).get('platform')
                    if not _plat or _plat == 'any':
                        continue
                    for _slug in _kk.get('slugs') or []:
                        _sp = next((x for x in items if x.get('slug') == _slug), None)
                        if _sp is None:
                            continue   # eigene Meldung weiter unten
                        _wo = set(_pliste(_sp, 'worksOn'))
                        # KEIN Freifahrtschein fuer 'universal'. Die erste Fassung hat
                        # 'universal' als "passt an alles" gelesen und die Pruefung damit
                        # stumm abgeschaltet -- gemessen: vier Controller fuehren
                        # ('android', 'universal') UND `platformLabel: "Android"`, darunter
                        # genau das Modell, das der Pruefer gefunden hat
                        # (8bitdo-ultimate-2c, "Kein iOS-Support" im Repo). 'universal' ist
                        # eine Bauform-Kategorie, keine Plattform-Zusage; kein einziger
                        # Controller fuehrt es allein. Die Plattform muss ausdruecklich
                        # dastehen.
                        if _plat not in _wo:
                            err(f'§A1/§A5: der Finder empfiehlt auf die Antwort '
                                f'"{_plat}" das Modell {_slug}, dessen worksOn '
                                f'{sorted(_wo)} diese Plattform nicht nennt — der Leser '
                                f'bekommt ein Modell empfohlen, das an seinem Geraet '
                                f'nicht laeuft (nachgewiesen durch Ausfuehrung)')
                if _b.get('doppelte_karten'):
                    err(f'§A5: in {_b["doppelte_karten"]} Antwortkombination(en) erscheint '
                        f'dasselbe Modell mehrfach unter den Empfehlungen — dreimal '
                        f'dasselbe Modell als "Top 3" ist eine sichtbar falsche Seite')
                _max = _b.get('max_karten') or 0
                _top_treffer = 0
                for _f2 in _zu_pruefen:
                    _roh2 = open(_f2, encoding='utf-8').read()
                    _t2 = _text_und_metas(_roh2)
                    _TOPM = r'Top[- ]?(\d+)[- ]?(?:Match|Empfehlung|Treffer)'
                    for _tm in re.finditer(_TOPM, _t2):
                        # Sichtbar, nicht bloss ausgeliefert: R20 hat die Zusage von der
                        # Startseite genommen und als "slogan" ins Organization-Schema
                        # gelegt -- Anker erfuellt, Seite stumm.
                        if _f2 in pages and re.search(_TOPM, _klartext(_roh2)):
                            _top_treffer += 1
                        if int(_tm.group(1)) != _max:
                            err(f'§A5: {_f2} verspricht "Top-{_tm.group(1)}", der Finder '
                                f'zeigt hoechstens {_max} Karten (gemessen ueber alle '
                                f'{_b.get("kombis")} Antwortkombinationen). Entweder die '
                                f'Begrenzung in {FINDER_JS} oder die Zusage stimmt nicht')
                if not _top_treffer:
                    err(f'§A5: keine SEITE nennt mehr eine Top-N-Zusage zum Finder — die '
                        f'gemessene Trefferzahl ({_max}) prueft damit nichts mehr. Die '
                        f'Zusage stand auf der Startseite ("Top-3-Matches"); wurde sie '
                        f'umformuliert, gehoert das Muster hier mitgezogen')

                # f) §A6: GEGENPROBE. Die Probe mit den echten Daten allein beweist den
                # Filter nicht -- ein `if (p) return 5;` in ratingOf macht ihn wirkungslos,
                # und die Ausgabe bleibt identisch, weil die Rangfolge das schwache Modell
                # ohnehin aus den Top 3 haelt. Deshalb ein Satz, der NUR aus Produkten
                # unter der Schwelle besteht: empfiehlt er dann etwas, filtert er nicht.
                _schwach = [p for p in items if p.get('type') == 'controller'
                            and (_bew_wert(p) or 0) < A6_SCHWELLE]
                if not _schwach:
                    # Heute genau einer (turtle-beach-atom, 3,5). Faellt er aus dem
                    # Sortiment, hat die Gegenprobe keinen Eingabewert und wuerde stumm
                    # bestehen. Dann wird einer gebaut: abgeleitet von einem echten
                    # Eintrag. Pruefmittel in verify.py, products.json bleibt unberuehrt.
                    _vorlage = next((p for p in items if p.get('type') == 'controller'), None)
                    if _vorlage:
                        _probe_p = json.loads(json.dumps(_vorlage))
                        _probe_p['slug'] = 'pruefmittel-unter-schwelle'
                        _probe_p['specs'] = [[_k, '1,0 (99)' if _k.startswith('Bew') else _v]
                                             for _k, _v in _spec_paare(_vorlage)]
                        if not any(_k.startswith('Bew') for _k, _v in _spec_paare(_vorlage)):
                            _probe_p['specs'].append(['Bew.', '1,0 (99)'])
                        _schwach = [_probe_p]
                if _schwach:
                    _gp = _finder_lauf({'dom': _dom, 'produkte': _schwach})
                    if _gp.get('fehler'):
                        err(f'§A6: die Gegenprobe des Finders ist fehlgeschlagen: '
                            f'{str(_gp["fehler"])[:300]}')
                    elif _gp.get('slugs'):
                        err(f'§A6 VERLETZT: mit einem Produktsatz, der NUR aus Modellen '
                            f'unter {A6_SCHWELLE} Sternen besteht, empfiehlt der Finder '
                            f'trotzdem {", ".join(_gp["slugs"])} — der Filter in '
                            f'renderResults() wirkt nicht. Steht er im Quelltext, wird er '
                            f'von ratingOf unterlaufen (nachgewiesen durch Ausfuehrung)')

                # g) Was er mit den echten Daten empfiehlt, muss ueber der Schwelle liegen.
                if not _b.get('slugs'):
                    err(f'§A6: die Ausfuehrungsprobe hat ueber alle {_b.get("kombis")} '
                        f'Kombinationen KEINE einzige Empfehlung erhalten — damit beweist '
                        f'sie nichts. Laedt der Finder products.json noch?')
                for _slug in _b.get('slugs') or []:
                    _sp = next((x for x in items if x.get('slug') == _slug), None)
                    if _sp is None:
                        err(f'§A6: der Finder empfiehlt "{_slug}", das products.json '
                            f'nicht kennt')
                    elif _bew_wert(_sp) is None:
                        err(f'§A6: der Finder empfiehlt {_slug}, dessen Bewertung sich '
                            f'aus products.json nicht lesen laesst')
                    elif _bew_wert(_sp) < A6_SCHWELLE:
                        err(f'§A6 VERLETZT: der Finder spielt {_slug} mit '
                            f'{_bew_wert(_sp)} Sternen als Kaufempfehlung aus, die '
                            f'Schwelle ist {A6_SCHWELLE} — nachgewiesen durch '
                            f'Ausfuehrung, nicht durch Quelltextlesen')

# ENDE §A6 IM CONTROLLER-FINDER
# ---------------------------------------------------------------------------------------

# Die Zahl der eigenen Tests steht auf der Startseite auch in PROSA ("13 davon ausfuehrlich
# getestet"). Die Stat-Bloecke waren gegatet, die zwei Prosa-Stellen nicht -- dieselbe Zahl,
# halb geprueft. Das ist die Klasse, die P-13 beschreibt.
for _f in pages:
    _kt = _klartext(open(_f, encoding='utf-8').read())
    for _m in re.finditer(r'(\d+)\s+davon\s+ausf(?:ü|ue)hrlich\s+getestet', _kt):
        if int(_m.group(1)) != _n_reviews:
            err(f"§A5: {_f} sagt \"{_m.group(1)} davon ausfuehrlich getestet\", "
                f"products.json ergibt {_n_reviews} Produkte mit eigener Testseite")

_ZAHL_PAARE = [(str(_n_produkte), 'Modelle im Sortiment'),
               (str(_n_reviews), 'ausführliche Tests'),
               (str(_n_controller), 'Modelle verglichen'),
               ]
# Die Finder-Seite nennt den Vergleichs-Pool im Verhaeltnis zum Sortiment. Zwei Fassungen
# davor waren falsch, und die zweite hat mein eigenes Gate erzwungen:
#   "allen 28 Controllern aus dem Sortiment" -- stimmte vor dem §A6-Filter, danach nicht.
#   "allen 27 Controllern aus dem Sortiment" -- meine Korrektur. Sie hat die Zahl
#   verschoben und den Rahmen stehen gelassen: "im Sortiment" sind 28, und "allen"
#   behauptet Vollstaendigkeit ueber genau die Eigenschaft, die der Filter aufgegeben hat.
#   Das Gate war an das Label gebunden und machte die ehrliche Fassung rot -- Mechanismus 6
#   des eigenen Patterns, zum zweiten Mal an derselben Zahl.
# Geprueft wird deshalb die Verhaeltnis-Aussage: N der M Controller, N = Pool ab Schwelle,
# M = alle Controller. Damit ist die ehrliche Fassung die gruene.
_POOL_SATZ = re.compile(r'(\d+)\s+der\s+(\d+)\s+Controller im Sortiment')
# Der Begruendungssatz nennt, wie viele Modelle die Schwelle verfehlen. Die erste Fassung
# sagte "Der eine, der fehlt" und war damit ungegatet: Sinkt ein zweites Modell unter 3,8,
# zieht der regulaere Aenderungsweg die Verhaeltniszahl nach (das Gate verlangt es), und
# der Begruendungssatz bleibt bei "der eine". Der Pruefer hat das Ende zu Ende gezeigt.
# Beide Wortstellungen: "1 Modell liegt unter ..." und "Davon liegt 1 Modell unter ...".
# Die zweite entstand, weil die erste mit einer Ziffer am Satzanfang begann (Hinweis aus
# dem 24. Pruefbericht) -- und das Gate hat die Umformulierung korrekt gemeldet, genau wie
# der Vertrag es ankuendigt. Hier steht sie jetzt mit drin.
_UNTER_SATZ = re.compile(r'(?:(\d+)\s+Modelle?\s+(?:liegt|liegen)'
                         r'|(?:liegt|liegen)\s+(\d+)\s+Modelle?)'
                         r'\s+unter unserer Empfehlungsschwelle von ([\d,]+) Sternen')
# Beide Wortstellungen deckt das Muster; die Satzeinleitung ("Von den 28", "Davon") ist
# ihm gleichgueltig, und das ist richtig: Sie traegt keine Zahl, die altern kann. Der
# sechsundzwanzigste Bericht hat angemerkt, dass "Davon" zuerst auf die 27 liest -- jetzt
# steht "Von den 28", und beides erfuellt dasselbe Muster.
_n_unter = _n_alle_ctrl - _n_controller
_unter_treffer = 0
for _f in _zu_pruefen:
    for _m in _UNTER_SATZ.finditer(_klartext(open(_f, encoding='utf-8').read())):
        if _f in pages:
            _unter_treffer += 1
        # Gruppe 1 ODER 2, je nach Wortstellung; Gruppe 3 ist die Schwelle.
        _zahl = _m.group(1) or _m.group(2)
        if int(_zahl) != _n_unter:
            err(f'§A5: {_f} sagt "{_zahl} Modell(e) liegt unter der '
                f'Empfehlungsschwelle", products.json ergibt {_n_unter}')
        if _m.group(3).replace(',', '.') != str(A6_SCHWELLE):
            err(f'§A5: {_f} nennt {_m.group(3)} Sterne als Empfehlungsschwelle, '
                f'verify.py prueft gegen {A6_SCHWELLE}')
if not _unter_treffer:
    err('§A5: der Satz zur Zahl der Modelle unter der Empfehlungsschwelle steht auf keiner '
        'Seite mehr — er begruendet die Luecke zwischen Pool und Sortiment und war in '
        'seiner ersten Fassung ("der eine, der fehlt") ungegatet')
_pool_treffer = 0
for _f in _zu_pruefen:
    # Klartext, nicht rohes Markup: `<strong>27</strong> der 28` hat den richtigen Satz rot
    # gemacht, und eine Kopie mit falscher Zahl plus Markup blieb gruen.
    for _m in _POOL_SATZ.finditer(_klartext(open(_f, encoding='utf-8').read())):
        # Fuer den Anker zaehlen nur SEITEN. Repoweit gezaehlt deckte eine Kopie in
        # llms.txt den Rueckfall auf die als falsch belegte Fassung auf der Seite.
        if _f in pages:
            _pool_treffer += 1
        if (int(_m.group(1)), int(_m.group(2))) != (_n_controller, _n_alle_ctrl):
            err(f'§A5: {_f} sagt "{_m.group(1)} der {_m.group(2)} Controller im '
                f'Sortiment", der Finder vergleicht {_n_controller} von {_n_alle_ctrl} '
                f'(Typ controller, Bewertung ab {A6_SCHWELLE})')
if not _pool_treffer:
    err('§A5: die Verhaeltnis-Aussage zum Finder-Pool ("N der M Controller im Sortiment") '
        'steht nirgends mehr im Repo — sie war zweimal falsch und gehoert deshalb gegatet')
_gefunden = {lbl: 0 for _, lbl in _ZAHL_PAARE}
for _f in _zu_pruefen:
    # Klartext, nicht rohes Markup. Dieses Gate war das letzte des Pakets, das die Datei
    # direkt gelesen hat, und es scheiterte in beide Richtungen: `<strong>99 Modelle</strong>
    # im Sortiment` und `Modelle&nbsp;im Sortiment` blieben gruen, Ziffern als Entity
    # ebenfalls; umgekehrt machte eine auskommentierte Altfassung ("Stand 08/2026: 40
    # Modelle im Sortiment") die richtige Kachel rot. Die frueher noetige Tag-Toleranz
    # zwischen Zahl und Label (`<div class="num">13</div><div class="cap">...`) erledigt
    # _klartext mit, weil Block-Grenzen zu einem Pilcrow werden -- der Zwischenraum darf
    # deshalb Pilcrows enthalten.
    _h = _klartext(open(_f, encoding='utf-8').read())
    for _zahl, _label in _ZAHL_PAARE:
        for _m in re.finditer(r'([\d.]+\+?)[\s\u00b6]*' + re.escape(_label), _h):
            # Fuer den Anker zaehlen nur SEITEN: Repoweit gezaehlt deckte eine Kopie in
            # llms.txt oder einem Generator das Umbenennen des Labels auf der Seite.
            if _f in pages:
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
    _soll = len([p for p in items if _flag in _pliste(p, 'worksOn') and p.get('type') == 'controller'])
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
    _soll = len([p for p in items if _flag in _pliste(p, 'worksOn') and p.get('type') == 'controller'])
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
# str(): brand oder name als Zahl liess sorted() mit TypeError abbrechen, als Liste mit
# "cannot use 'tuple' as a set element" -- vier Abbruchstellen aus Runde 18, alle in
# derselben Klasse wie die Spec-Werte aus Runde 17. Die FORM selbst meldet formfehler().
_MARKEN = sorted({(str(p['brand']), str(p['slug'])) for p in items if p.get('brand')})
_NAMEN = sorted({(str(p.get('name') or ''), str(p['slug'])) for p in items if p.get('name')})
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
        _soll = _preis_zahl(_eigen)
        if _soll is not None and _soll != int(_pm.group(1)):
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
_PREISE_ROH = {str(_preis_zahl(p)) for p in items if _preis_zahl(p) is not None}
# Tausenderpunkt: zwei Leser desselben Feldes rechnen verschieden. `preis_zahl()` in
# produktdaten.py wirft den Punkt weg ("1.299 €" -> 1299), das eigene `preis()` in
# gen_preisfrage.py nimmt die erste Ziffernfolge ("1.299 €" -> 1). Heute traegt kein Preis
# einen Tausenderpunkt, also ist der Unterschied latent -- und ein latenter Unterschied,
# der in einem Kommentar als "heute kein Problem" steht, ist genau die Form, die hier
# schon mehrfach still live gegangen ist. Statt der Beschreibung steht jetzt die
# Eigenschaft im Gate: Der erste vierstellige Preis macht den Lauf rot, nicht die Seite
# falsch. Fix ist dann beide Stellen auf `preis_zahl()` zu ziehen (§A1, eine Wahrheit).
for _p in items:
    if re.search(r'\d\.\d{3}', str((_p or {}).get('price') or '')):
        err(f"§A1: {_p.get('slug')} hat den Preis \"{_p.get('price')}\" mit "
            f"Tausenderpunkt. produktdaten.preis_zahl() liest daraus "
            f"{_preis_zahl(_p)}, gen_preisfrage.preis() dagegen die erste Ziffernfolge "
            f"— beide Stellen auf preis_zahl() ziehen, bevor dieser Preis live geht.")
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
    _lbl = _pfeld(_p, 'platformLabel')   # als Liste/Objekt war es ein dict-Schluessel
    if _lbl not in _LABEL_VERLANGT:
        continue
    _fehlt = [f for f in _LABEL_VERLANGT[_lbl] if f not in _pliste(_p, 'worksOn')]
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
    # Das Gate schuetzt INDEXIERBARE Seiten: Nur dort entscheidet ein falscher canonical
    # darueber, ob die Seite im Index landet. Redirect-Stubs zeigen bewusst auf ihr Ziel,
    # und 404.html hat gar keine eigene URL — sie antwortet unter jeder. Ein
    # Selbst-canonical waere dort sogar falsch.
    if 'http-equiv="refresh"' in _h or 'noindex' in _h:
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
    # Und gegen products.json: url, poster und duration sind dort gepflegt, auf der Seite
    # standen sie bisher ungeprueft. duration kam in keinem der vier Gates vor, wird aber
    # sichtbar als "Laenge N Min." ausgespielt.
    _pv = _externes_produkt(_f)
    # video als Zahl/bool/Liste liess .get() hier mit AttributeError abbrechen.
    _vd = (_pv or {}).get('video')
    _vd = _vd if isinstance(_vd, dict) else {}
    if _vd:
        for _feld, _muster in (('url', r'<video[^>]*src="([^"]*)"'),
                               ('poster', r'<video[^>]*poster="([^"]*)"')):
            _vm = re.search(_muster, _h)
            if _vm and _vd.get(_feld) and _vm.group(1) != _vd[_feld]:
                err(f"§A1: {_f} zeigt video.{_feld} \"{_vm.group(1)}\", products.json "
                    f"fuehrt fuer {_pv['slug']} \"{_vd[_feld]}\"")
        if _vd.get('duration') and '<video' in _h and str(_vd['duration']) not in _h:
            err(f"§A1: {_f} nennt die Videolaenge {_vd['duration']} aus products.json "
                f"nirgends, bindet das Video aber ein")

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
    # Struktur statt nur Rohtext. longtail.json wurde von zwei Gates gelesen, aber nur als
    # Zeichenkette (Datenstand, verbotene Formulierungen, Preise im Fliesstext). Dass ein
    # Pflichtfeld leer ist oder zwei Eintraege denselben Slug tragen, haette keins gemerkt
    # — products.json hat beide Pruefungen seit Langem.
    _lt_slugs, _lt_kw = set(), set()
    for _e in (_ltd if isinstance(_ltd, list) else []):
        for _feld in ('slug', 'brand', 'name', 'keyword', 'claim', 'verdict', 'desc',
                      'specs', 'availability', 'faqs', 'alternatives'):
            if not _e.get(_feld):
                err(f"§A1: {_LT}: {_e.get('slug', '?')} hat kein \"{_feld}\"")
        if _e.get('slug') in _lt_slugs:
            err(f"§A1: {_LT}: Slug doppelt: {_e.get('slug')}")
        if _e.get('keyword') in _lt_kw:
            err(f"§A1: {_LT}: Keyword doppelt: {_e.get('keyword')} — zwei Seiten auf "
                f"dasselbe Suchwort machen sich gegenseitig Konkurrenz")
        _lt_slugs.add(_e.get('slug'))
        _lt_kw.add(_e.get('keyword'))
        if _e.get('slug') in _slugs:
            err(f"§A1: {_LT}: {_e.get('slug')} steht auch in products.json — ein Slug "
                f"gehoert in genau eine der beiden Quellen")
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

# products.json gegen das Vokabular in assets/js/produkte.js (§A1). Die Felder `platform`
# und `type` waren bis 01.10. nur auf Nicht-Leer geprueft, obwohl sie im Browser die
# Filterleiste und die Label steuern: Ein Wert, den PLAT_ORDER nicht kennt, erzeugt gar
# keinen Filter-Chip, ein unbekannter `type` zeigt den Rohwert statt eines Labels.
# `platformLabel` ist nicht frei waehlbar, sondern genau das Label zu `platform`. Diese
# Regel hat sofort eine Abweichung gefunden, die ich selbst eingebaut hatte: viture-8bitdo
# trug platform "universal" und label "Android", waehrend seine zwei Geschwister mit
# identischem worksOn beides auf "android" haben.
_PJS = 'assets/js/produkte.js'
if os.path.exists(_PJS):
    _pjs = open(_PJS, encoding='utf-8').read()

    def _js_karte(_name):
        _m = re.search(_name + r"\s*=\s*\{(.*?)\}", _pjs, re.S)
        return dict(re.findall(r"'?([\w-]+)'?\s*:\s*'([^']*)'", _m.group(1))) if _m else {}

    def _js_liste(_name):
        _m = re.search(_name + r"\s*=\s*\[(.*?)\]", _pjs, re.S)
        return re.findall(r"'([^']+)'", _m.group(1)) if _m else []

    _PLAT_LABELS = _js_karte('PLATFORM_LABELS')
    _TYPE_LABELS = _js_karte('TYPE_LABELS')
    _PLAT_ORDER = _js_liste('PLAT_ORDER')
    if not (_PLAT_LABELS and _TYPE_LABELS and _PLAT_ORDER):
        err(f"§A1: Vokabular in {_PJS} nicht lesbar (PLATFORM_LABELS / TYPE_LABELS / "
            f"PLAT_ORDER) — ohne es laesst sich products.json nicht dagegen pruefen")
    else:
        for _p in items:
            # str(): platform/type als Liste oder Objekt liessen den dict-Zugriff mit
            # "unhashable type" abbrechen (Runde 18, breite Typprobe).
            _pl, _ty = _pfeld(_p, 'platform'), _pfeld(_p, 'type')
            if _pl not in _PLAT_ORDER:
                err(f"§A1: {_p['slug']} hat platform \"{_pl}\", das PLAT_ORDER in {_PJS} "
                    f"nicht kennt — fuer diesen Wert entsteht kein Filter-Chip")
            if _pl not in _PLAT_LABELS:
                err(f"§A1: {_p['slug']} hat platform \"{_pl}\" ohne Label in {_PJS}")
            elif _pfeld(_p, 'platformLabel') != _PLAT_LABELS[_pl]:
                err(f"§A1: {_p['slug']} traegt platformLabel \"{_pfeld(_p, 'platformLabel')}\", "
                    f"zu platform \"{_pl}\" gehoert aber \"{_PLAT_LABELS[_pl]}\"")
            if _ty not in _TYPE_LABELS:
                err(f"§A1: {_p['slug']} hat type \"{_ty}\", das TYPE_LABELS in {_PJS} nicht "
                    f"kennt — die Seite zeigt dann den Rohwert statt eines Labels")

# Die Stub-Regel kommt aus hublinks.py und steht NICHT ein zweites Mal hier. Die erste
# Fassung hat sie nachgebaut (`'noindex' in _h`) -- genau die "zweite Wahrheit", die P-15
# Mechanismus 1 verbietet, und mit demselben Fehler: Ein Blog-Artikel, der das Wort
# "noindex" im Text nennt, fiel still als Linkquelle aus dem Waisen-Gate.
from hublinks import ist_stub as _ist_stub_quelle


# Verwaiste Seiten im SEO-Sinn (§B): indexierbar, in der Sitemap, aber von keiner
# einzigen Seite verlinkt. Die Rueckrichtung war bis 01.10. nur fuer /produkte/ gegen die
# Generatoren geprueft, nicht gegen die Verlinkung — und die ist es, die zaehlt: Eine Seite
# ohne einen einzigen internen Link wird selten gecrawlt und rankt entsprechend.
# Gefunden hat die erste Messung genau eine: produkte/gamesir-g4s/, waehrend die neun
# anderen Longtail-Datenblaetter alle von einem Marken-Hub verlinkt sind.
# Links aus den JS-Dateien zaehlen mit (Navigation und Footer entstehen dort), noindex-
# Seiten und Redirect-Stubs sind ausgenommen — die sollen bewusst unverlinkt sein.
_url_zu_datei = {('/' if _f == 'index.html' else '/' + os.path.dirname(_f).replace(os.sep, '/') + '/'): _f
                 for _f in pages}
_verlinkt = set()
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    # B7: Ein Link von einer noindex-Weiterleitung ist KEIN Link. Die Seite sagt dem
    # Crawler "indexiere mich nicht, geh woanders hin" -- was sie verlinkt, bekommt davon
    # kein Signal. Bis zum 04.10. zaehlten solche Quellen mit, und genau daran haben
    # DREI Seiten vorbeigelebt: produkte/ipega-pg-9023/, produkte/ipega-pg-9083s/ und
    # produkte/mocute-050/ hatten je genau EINE eingehende Quelle, und die war in beiden
    # Faellen eine Weiterleitung (/marken/ipega/, /marken/mocute/). Entstanden ist das
    # beim Zurueckbauen der zwei Marken-Hubs zu Stubs: Die Seiten verloren ihren einzigen
    # echten Link, und das Gate hat nichts gemerkt, weil es die Quelle nicht angesehen hat.
    if _ist_stub_quelle(_h):
        continue
    for _m in re.finditer(r'href="(/[^"#?]*)"', _h):
        _u = _m.group(1)
        if not _u.endswith('/'):
            _u += '/'
        if _u in _url_zu_datei and _url_zu_datei[_u] != _f:
            _verlinkt.add(_u)
for _js in sorted(glob.glob('assets/js/*.js')):
    _s = open(_js, encoding='utf-8').read()
    for _m in re.finditer(r"""href=["'](/[^"'#?]*)|href:\s*['"](/[^'"]+)""", _s):
        _u = _m.group(1) or _m.group(2)
        if not _u.endswith('/'):
            _u += '/'
        _verlinkt.add(_u)
for _u, _f in sorted(_url_zu_datei.items()):
    if _u == '/' or _u in _verlinkt:
        continue
    _h = open(_f, encoding='utf-8').read()
    if 'noindex' in _h or 'http-equiv="refresh"' in _h:
        continue
    err(f"§B: {_f} ist indexierbar, wird aber von keiner einzigen Seite verlinkt — "
        f"eine Seite ohne internen Link wird selten gecrawlt")

# Kompatibilitaets-Antwort (Massnahme B1, §A1). Auf den 29 generierten /produkte/-Seiten
# deckt das der Zeichenvergleich in 6c ab. Die 13 handgepflegten Review-Seiten haben
# keinen Generator: Dort setzt scripts/sync_kompat.py den Block, und ohne dieses Gate
# koennte eine Handaenderung ihn still von products.json wegdriften lassen — genau das
# Muster, das diese Session reihenweise veraltet vorgefunden hat.
try:
    from kompat import kompat_html as _kompat_html
    from gen_hubs import esc as _kesc
except Exception as _e:
    _kompat_html = None
    err(f"§A1: Kompatibilitaets-Block nicht pruefbar ({type(_e).__name__}: {_e})")
if _kompat_html:
    for _p in items:
        _d = (_p.get('detail') or '').strip('/')
        if not _d or _d.startswith('produkte/'):
            continue
        _f = _d + '/index.html'
        if not os.path.exists(_f):
            continue
        _h = open(_f, encoding='utf-8').read()
        _soll = _kompat_html(_p, _kesc)
        _hat = '<div class="kompat-box"' in _h
        if _soll and not _hat:
            err(f"§A1: {_f} fuehrt keinen Kompatibilitaets-Block — "
                f"'python3 scripts/sync_kompat.py' laufen lassen")
        elif _soll and _soll not in _h:
            err(f"§A1: {_f} hat einen Kompatibilitaets-Block, der von products.json "
                f"abweicht — 'python3 scripts/sync_kompat.py' laufen lassen; die Ursache "
                f"gehoert in products.json (worksOn, Verb.), nicht in die HTML-Datei")
        elif not _soll and _hat:
            err(f"§A1: {_f} fuehrt einen Kompatibilitaets-Block, obwohl products.json "
                f"fuer {_p['slug']} nichts belegbares hergibt")

# Ein Handlungsaufruf pro Seite (Massnahme B3, Grundlage Miller/StoryBrand). Eine Seite
# darf denselben Aufruf mehrfach zeigen -- Wiederholung ist richtig --, aber nicht zwei
# verschiedene primaere Ziele anbieten. Gemessen am 01.10.: Drei Zubehoer-Artikel trugen
# je zwei primaere Aufrufe, einen themennahen und einen generischen Finder-Block, waehrend
# 16 von 19 Artikeln genau einen hatten. Dazu ein Button auf der Startseite, dessen
# BESCHRIFTUNG den Finder versprach und dessen LINK zur Produktliste fuehrte -- schlimmer
# als Redundanz, weil er etwas anderes tut als er sagt.
# Kartenbuttons zaehlen nicht mit: "Kaufen" und "Zum Test" gehoeren zum Eintrag, nicht zur
# Seite. Gezaehlt werden nur btn-primary ausserhalb von Karten, und zwar VERSCHIEDENE
# Ziele, nicht Vorkommen.
_OHNE_KARTEN = [
    (re.compile(r'<(script|style)\b[^>]*>.*?</\1>', re.S), ' '),
    (re.compile(r'<(header|footer)[^>]*id="site-(?:header|footer)".*?</\1>', re.S), ' '),
    (re.compile(r'<article class="pcard.*?</article>', re.S), ' '),
]
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    if 'http-equiv="refresh"' in _h:
        continue
    for _re, _ersatz in _OHNE_KARTEN:
        _h = _re.sub(_ersatz, _h)
    _ziele = set()
    for _m in re.finditer(r'<a[^>]*href="([^"]*)"[^>]*class="[^"]*btn-primary[^"]*"'
                          r'|<a[^>]*class="[^"]*btn-primary[^"]*"[^>]*href="([^"]*)"', _h):
        _ziele.add(_m.group(1) or _m.group(2))
    if len(_ziele) > 1:
        err(f"§B3: {_f} bietet {len(_ziele)} verschiedene primaere Handlungsaufrufe an "
            f"({', '.join(sorted(_ziele))}) — eine Seite fuehrt an genau ein Ziel, "
            f"Wiederholung desselben Aufrufs ist erlaubt")

# Abgeleitete Mengenaussagen im Problem-Artikel (§A1). Der Artikel nennt zwei Zahlen, die
# nicht in products.json stehen, sondern aus ihr folgen, und die mit jedem Sortimentswechsel
# falsch werden. Beide werden hier nachgerechnet.
#
# ACHT PRUEFRUNDEN HABEN GEZEIGT, WARUM DIESES GATE SO SCHMAL IST. Die Vorfassungen haben
# versucht, JEDE Formulierung eines solchen Anspruchs zu erkennen: ein Muster mit sieben
# Anspruchswoertern und einer fausen Luecke dazwischen, dazu eine Satzgrenzen-Heuristik mit
# Abkuerzungsliste. Dieser Ansatz hat in jeder Runde entweder ein Loch gelassen oder, viel
# schlimmer, auf WAHREM Text die falsche Zahl erzwungen:
#   - Die faule Luecke band die Zahl an das positionsmaessig erste Anspruchswort, nicht an
#     den Anspruch des Satzes. "6 der 28 Controller funktionieren kabellos und am Kabel"
#     ist wahr, enthaelt "kabellos", und das Gate verlangte 17. Die Meldung schickte den
#     Autor also zu einer Zahl, die products.json widerspricht. 13 von 78 wahren Saetzen
#     waren rot.
#   - Die Satzgrenze scheiterte an "USB-C." (das Wort vor dem Punkt war "C", also ein
#     Abkuerzungspunkt), an "usw." und "etc." (als Ausnahme gefuehrt, stehen aber am
#     Satzende), an fehlenden Tags im Fenster, an Punkt+Gross+Klein und an Punkt+Gross.
# Keine Verfeinerung hat gehalten, weil die Aufgabe "welchen Anspruch erhebt dieser deutsche
# Satz" mit Schluesselwoertern nicht loesbar ist.
#
# Deshalb prueft dieses Gate jetzt GENAU DIE ZWEI SAETZE, die im Artikel stehen, auf dem
# tagfreien Text. Das ist sound: keine Heuristik, kein Fehlalarm, und der Alterungsfall
# (products.json aendert sich, der Satz nicht) wird sicher erkannt. Dazu ein Anker je Satz,
# damit keiner still verschwindet oder umformuliert wird.
# GRENZE, ehrlich und vollstaendig:
#   NICHT geprueft wird ein NEU geschriebener, frei formulierter Mengensatz an einer
#   anderen Stelle ("Zur Einordnung: 19 der 28 Controller sind kabelgebunden" in einem
#   neuen Absatz bleibt gruen). Das ist der bewusste Tausch gegen die Fehlalarme, an denen
#   acht Vorfassungen gescheitert sind.
#   GEPRUEFT wird: die Zahl in den zwei bestehenden Saetzen, gegen products.json, auf
#   tagfreiem Text (Markup zwischen den Woertern hilft nicht), und ihre Anwesenheit. Jede
#   Aenderung am Satz -- Kuerzung, Erweiterung, Umformulierung, Entfernung -- meldet der
#   Anker, weil das Muster den vollen Satz traegt.
#   Wer die Aussage umformulieren will, aendert das Muster hier mit. Genauso fuehren die
#   VERBOTEN-Liste und die Hall-Invariante in diesem Repo ihre Schreibweisen namentlich.
def _verb(_p):
    # .strip(): Ein Feld mit nur Leerzeichen war wahr und rutschte am Pflichtfeld-Gate
    # vorbei, waehrend die Quote es als kabelgebunden zaehlte.
    return _spec(_p, 'Verb.').strip()
_ctrl = [p for p in items if p.get('type') == 'controller']
# Ein Controller ohne Verb.-Feld wuerde als kabellos durchgehen und die Quote still
# verschieben, waehrend das Gate gruen bleibt. Heute fuehren alle 28 das Feld; damit das
# so bleibt, ist das Fehlen selbst ein Fehler.
for _p in _ctrl:
    if not _verb(_p):
        err(f"§A1: Controller {_p.get('slug')} hat kein Spec-Feld \"Verb.\" — die "
            f"Mengenaussagen im Problem-Artikel werden damit still falsch")
# POSITIV abgeleitet, nicht negativ. Die erste Fassung zaehlte "alles ohne BT/Bluetooth"
# als kabelgebunden und fiel damit bei jeder unbekannten Schreibweise OFFEN aus: Der
# Pruefer hat `Verb.` von einem Controller auf "BLE 5.3" gesetzt, alle Gates blieben gruen,
# und die Seite behauptete weiter 11 statt 10. Dasselbe fuer "kabellos", "2,4 GHz Funk",
# "Wireless", "Funk-Dongle", "n/a" und "-" -- neun von neun Proben stumm. products.json
# fuehrt heute neun verschiedene Schreibweisen von `Verb.`; eine zehnte ist keine
# Konstruktion. Kabelgebunden heisst deshalb jetzt: nennt eine Steckverbindung UND keine
# Funkverbindung. Unbekanntes zaehlt zu keiner Gruppe, die Summe sinkt, und der Satz wird
# rot -- die Pruefung faellt geschlossen aus. `scripts/kompat.py` benutzt im selben Repo
# seit B1 schon die positive Form; das Gate hatte die lose.
# VOKABULAR statt zwei Suchbegriffe. Die positive Ableitung war nur halb geschlossen:
# `_funk()` kannte nur BT und Bluetooth, also landete "BLE 5.3 / USB-C" in der Gruppe
# "kabelgebunden" -- Steckbegriff vorhanden, Funkbegriff nicht erkannt, Summe unveraendert,
# Satz gruen, Zahl falsch. Das ist realistisch, weil alle sechs heutigen Doppelmodelle
# genau in dieser Kombinationsschreibweise notiert sind ("BT 5.0 / USB-C" 3x, "BT/USB-C"
# 2x, "BT+USB-C" 1x) -- eine unbekannte Funk-Schreibweise trifft also sofort sechs
# Produkte.
# Hier stand bis R28 zusaetzlich "und der 8BitDo Ultimate 2C real 2,4 GHz plus USB-C ist".
# Das war eine unbelegte Produktaussage (§A5) und vom eigenen Repo widerlegt:
# products.json fuehrt ihn als "Ultimate 2C Wired" mit `Verb.: USB (kabelgebunden)`, die
# VERBOTEN-Liste weiter unten in DIESER Datei nennt "Ultimate 2C als Bluetooth-Gamepad"
# ausdruecklich als widerlegt, und STATUS haelt fest, dass die Frage am 30.09. per
# Amazon-Abgleich geklaert wurde (es ist die Wired-Variante). Waere der Satz wahr, waeren
# es 7 Doppelmodelle statt 6 und 10 kabelgebundene statt 11.
# Jetzt muss JEDES Token des Feldes bekannt sein. Was nicht im Vokabular steht, ist selbst
# ein Befund, und zwar bevor irgendeine Zahl gerechnet wird. Dasselbe Verfahren benutzt
# das Repo schon fuer `platform` und `type` gegen das JS-Vokabular.
_VERB_STECK = {'usb', 'usb-a', 'usb-c', 'lightning'}
_VERB_FUNK = {'bt', 'bluetooth', 'ble'}
_VERB_FUELL = {'kabelgebunden', 'kabellos', 'und', 'oder', 'bzw', 'per', 'via'}


def _verb_tokens(_p):
    return [t for t in re.split(r'[\s/+,()&]+', _verb(_p)) if t]


def _steck(_p):
    return any(t.lower() in _VERB_STECK for t in _verb_tokens(_p))


def _funk(_p):
    return any(t.lower() in _VERB_FUNK for t in _verb_tokens(_p))


for _p in [x for x in items if x.get('type') == 'controller']:
    for _t in _verb_tokens(_p):
        _tl = _t.lower()
        if (_tl in _VERB_STECK or _tl in _VERB_FUNK or _tl in _VERB_FUELL
                or re.fullmatch(r'\d+([.,]\d+)*', _t)):
            continue
        err(f"§A1: Controller {_p.get('slug')} hat Verb.=\"{_verb(_p)}\", und \"{_t}\" "
            f"steht in keinem Vokabular (Steckverbindung, Funkverbindung, Version). "
            f"Solange unklar ist, zu welcher Gruppe das gehoert, sind die Mengenaussagen "
            f"im Problem-Artikel nicht ableitbar — Token in scripts/verify.py ergaenzen")
_kabel_soll = len([p for p in _ctrl if _steck(p) and not _funk(p)])
# Ein Feld, dessen Tokens alle bekannt sind, das aber keiner Gruppe zugeordnet werden
# kann (etwa nur "kabelgebunden" ohne Anschluss), ist ebenfalls ein Befund.
for _p in _ctrl:
    if _verb(_p) and not _steck(_p) and not _funk(_p):
        err(f"§A1: Controller {_p.get('slug')} hat Verb.=\"{_verb(_p)}\" — das nennt weder "
            f"eine Steckverbindung noch eine Funkverbindung, damit laesst sich die "
            f"Mengenaussage im Problem-Artikel nicht ableiten")
# Modelle, die per Funk UND am Kabel laufen. Sie sind der Grund, warum der Artikel dem
# Leser keinen Selbsttest mehr anbietet: Bei ihnen sieht ein leerer Akku genauso aus wie
# gar keiner, und drei Anleitungsversuche sind daran gescheitert.
_beides_soll = len([p for p in _ctrl if _funk(p) and _steck(p)])
# Annahme hinter "kabelgebunden = kein Akku", hier offengelegt: products.json fuehrt nur
# bei einem einzigen Produkt ein Akkufeld (trust-gxt-rgb, also 1 der 42 Produkte und 1 der
# 28 Controller), die Gleichsetzung ist also abgeleitet und nicht gemessen. Heute traegt
# sie, weil jedes kabelgebundene Modell im Sortiment seinen Strom aus dem Handy zieht.
# Kommt ein kabelgebundenes Modell MIT Akku dazu, wuerde der Artikel still falsch; deshalb
# faellt dieser Fall auf (Gegenprobe weiter unten).
# Die Muster treffen den VOLLEN Satz, nicht nur seinen Anfang. Mit dem kuerzeren Praefix
# war beides falsch: Eine Erweiterung blieb unsichtbar (der Praefix traf weiter, also
# schwieg der Anker bei "... sind kabelgebunden oder kabellos" und bei "Keineswegs 11 der
# 28 ... sind kabelgebunden"), und eine Uebernahme der Phrase mit anderer, WAHRER Zahl
# wurde rot ("9 der 28 Controller in unserem Sortiment sind kabelgebunden und tragen
# USB-C" -- neun tun das wirklich). Mit dem vollen Satz ist jede Abweichung eine
# Abweichung, und der Anker meldet sie.
_SAETZE = [
    (re.compile(r'(?:^|(?<=[.!?:;\u00b6]\s))\s*(\d+)\s+der\s+(\d+)\s+Controller in unserem '
                r'Sortiment sind kabelgebunden und ziehen ihren Strom aus dem Handy'),
     lambda: (_kabel_soll, len(_ctrl)), 'kabelgebunden'),
    (re.compile(r'(?:^|(?<=[.!?:;\u00b6]\s))\s*(\d+)\s+der\s+(\d+)\s+Controller in unserem '
                r'Sortiment laufen sowohl per Funk als auch am Kabel, und ein leerer Akku '
                r'sieht genau so aus wie keiner'),
     lambda: (_beides_soll, len(_ctrl)), 'mit Funk UND Kabel'),
]
_satz_treffer = [0] * len(_SAETZE)
# REPOWEIT, nicht nur ueber die Seiten: Eine falsche Kopie des Satzes in llms.txt oder als
# Literal in einem Generator blieb gruen, weil die Schleife nur `pages` las. Das ist Lehre
# 11 aus dem eigenen Protokoll ("repoweit statt an einer Datei festgenagelt"), hier zum
# wiederholten Mal nicht angewandt.
for _f in _zu_pruefen:
    _kh = open(_f, encoding='utf-8').read()
    # Block-Grenzen werden zu einem Satzzeichen, Kommentare verschwinden. Ohne das
    # erste war der Satzanfang-Lookbehind ein Fehlalarm: Nach einer Ueberschrift, in
    # einer Tabellenzelle oder als erster Satz eines Absatzes steht im tagfreien Text
    # kein Satzzeichen davor, und der Anker meldete den wortgleich vorhandenen Satz als
    # verschwunden (6 von 12 Platzierungen). Ohne das zweite erfuellte eine Kopie des
    # Satzes in einem HTML-Kommentar den Anker, waehrend der sichtbare Satz fehlen durfte.
    _kt = re.sub(r'<!--.*?-->', ' ', _kh, flags=re.S)
    _kt = re.sub(r'</?(?:p|li|td|th|h[1-6]|div|section|main|article|blockquote|dd|dt)\b'
                 r'[^>]*>|<br\s*/?>', ' \u00b6 ', _kt, flags=re.I)
    # Auch der Zeilenumbruch ist eine Grenze. Ohne ihn blieb eine falsche Kopie des Satzes
    # in llms.txt gruen: Dort gibt es keine Block-Tags, und das Zusammenziehen des
    # Leerraums machte aus dem Umbruch ein Leerzeichen. Der Preis ist klein und benannt:
    # Steht ein Praefix wie "Keineswegs" vor dem Umbruch, erkennt das Muster den Satz
    # trotzdem -- eine uebersehene Erweiterung, kein Fehlalarm.
    _kt = _kt.replace('\n', ' \u00b6 ')
    # script/style heraus, wie _klartext es tut: Dieser Block baute seinen Text selbst und
    # liess Programmtext stehen. Heute nicht ausnutzbar (der Satzanfang-Lookbehind traf in
    # der Probe des Pruefers nicht), aber es ist dieselbe Abweichung von der
    # "eine Funktion"-Lehre, die sechs Gates einzeln kaputt gemacht hat.
    _kt = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', ' \u00b6 ', _kt, flags=re.S | re.I)
    _kt = html.unescape(re.sub(r'<[^>]*>', ' ', _kt))
    _kt = re.sub(r'\s+', ' ', _kt)
    for _i, (_muster, _sollfn, _was) in enumerate(_SAETZE):
        for _m in _muster.finditer(_kt):
            # Fuer den Anker zaehlen nur SEITEN. Vorher zaehlte er repoweit, womit eine
            # Kopie in llms.txt oder in einem Generator-Literal ihn erfuellte, waehrend
            # der Satz von der Seite verschwinden durfte. Geprueft wird der WERT weiter
            # repoweit, denn eine falsche Kopie ist auch dort falsch.
            if _f in pages:
                _satz_treffer[_i] += 1
            _soll = _sollfn()
            if (int(_m.group(1)), int(_m.group(2))) != _soll:
                err(f'§A1: {_f} sagt "{_m.group(1)} der {_m.group(2)} Controller '
                    f'{_was}", products.json ergibt {_soll[0]} von {_soll[1]}')
for _i, (_muster, _sollfn, _was) in enumerate(_SAETZE):
    if not _satz_treffer[_i]:
        err(f'§A1: der Satz zu "{_was}" steht auf keiner Seite mehr — er wurde entfernt '
            f'oder umformuliert (eine Kopie in llms.txt oder einem Generator zaehlt hier '
            f'nicht). Beides ist erlaubt, aber dann gehoert die neue Fassung in _SAETZE '
            f'in scripts/verify.py, sonst altert die Zahl ungeprueft')
# ---------------------------------------------------------------------------------------
# BLOG-LISTE GEGEN DEN BESTAND. Zwei Befunde am 02.10., beide aus dem B4-Paket vom Vortag:
# Das ItemList-Schema auf /blog/ fuehrte 18 von 19 Artikeln (die Preisfrage-Seite fehlte,
# seit sie als Generator dazukam), und die Karte zu dieser Seite nannte einen anderen Titel
# als die Seite selbst ("... Preise 2026 im Ueberblick" gegen "... Preise 2026", nachdem
# der Generator-Titel wegen §B1 gekuerzt wurde). Beides blieb gruen, weil kein Gate die
# Liste gegen den Bestand und die Kartentitel gegen die Zielseiten hielt.
if os.path.exists('blog/index.html'):
    _bl = open('blog/index.html', encoding='utf-8').read()
    _artikel_dirs = sorted(os.path.dirname(f).replace(os.sep, '/')
                           for f in glob.glob('blog/*/index.html')
                           if 'http-equiv="refresh"' not in open(f, encoding='utf-8').read())
    _il = re.search(r'<script type="application/ld\+json">(\{"@context[^<]*"ItemList".*?)'
                    r'</script>', _bl, re.S)
    if not _il:
        err('§A4: blog/index.html hat kein ItemList-Schema mehr — die Liste der Artikel '
            'war bisher dort maschinenlesbar')
    else:
        try:
            _ild = json.loads(_il.group(1))
        except Exception as _e:
            err(f'§A4: das ItemList-Schema in blog/index.html ist kein gueltiges JSON ({_e})')
            _ild = None
        if _ild:
            _liste = [e.get('url', '').rstrip('/').split('/')[-1]
                      for e in _ild.get('itemListElement', [])]
            _gelistet = set(_liste)
            # Als Menge gelesen blieb ein doppelter Eintrag unsichtbar, und die position
            # wurde nie geprueft (alle auf 1 waere gruen gewesen).
            for _u in sorted(_gelistet):
                if _liste.count(_u) > 1:
                    err(f'§A4: das ItemList-Schema von blog/index.html fuehrt /blog/{_u}/ '
                        f'{_liste.count(_u)}x')
            _pos = [e.get('position') for e in _ild.get('itemListElement', [])]
            if _pos != list(range(1, len(_pos) + 1)):
                err(f'§A4: die position-Werte im ItemList-Schema von blog/index.html '
                    f'lauten {_pos[:6]}..., erwartet ist 1 bis {len(_pos)}')
            for _d in _artikel_dirs:
                _slug = _d.split('/')[-1]
                if _slug not in _gelistet:
                    err(f'§A4: /blog/{_slug}/ fehlt im ItemList-Schema von blog/index.html '
                        f'({len(_gelistet)} Eintraege, {len(_artikel_dirs)} Artikel)')
            for _u in _gelistet:
                if f'blog/{_u}' not in _artikel_dirs:
                    err(f'§A4: das ItemList-Schema von blog/index.html fuehrt /blog/{_u}/, '
                        f'diese Seite gibt es nicht')
            # §A4: der Schema-Name muss dem H1 der Zielseite entsprechen, sonst behauptet
            # die maschinenlesbare Fassung einen anderen Titel als die Seite.
            for _e in _ild.get('itemListElement', []):
                _eu = (_e.get('url') or '').rstrip('/').split('/')[-1]
                _ez = f'blog/{_eu}/index.html'
                if not os.path.exists(_ez):
                    continue
                _eh1 = re.search(r'<h1[^>]*>(.*?)</h1>', open(_ez, encoding='utf-8').read(), re.S)
                if not _eh1:
                    continue
                _eh1t = html.unescape(re.sub(r'<[^>]*>', '', _eh1.group(1))).strip()
                if _eh1t and _eh1t != (_e.get('name') or '').strip():
                    err(f'§A4: das ItemList-Schema von blog/index.html nennt fuer '
                        f'/blog/{_eu}/ "{(_e.get("name") or "")[:50]}", die Seite hat den '
                        f'H1 "{_eh1t[:50]}"')
    # Kartentitel gegen den H1 der Zielseite
    for _href, _ktext in _lz_karten(_bl):
        if not _href or not _href.startswith('/blog/'):
            continue
        _ziel = _href.strip('/') + '/index.html'
        if not os.path.exists(_ziel):
            continue
        _h1 = re.search(r'<h1[^>]*>(.*?)</h1>', open(_ziel, encoding='utf-8').read(), re.S)
        if not _h1:
            # Still uebersprungen hiess: H1 durch <p> ersetzt, und weder dieses noch ein
            # anderes Gate hat es gemerkt.
            err(f'§A4: {_ziel} hat kein <h1> — Kartentitel und Schema-Name lassen sich '
                f'dann gegen nichts pruefen')
            continue
        _h1t = html.unescape(re.sub(r'<[^>]*>', '', _h1.group(1))).strip()
        if _h1t and _h1t not in re.sub(r'\s+', ' ', _ktext):
            err(f'§A1: die Karte zu {_href} auf blog/index.html nennt nicht den Titel der '
                f'Zielseite ("{_h1t[:60]}") — Karte und Seite sind auseinandergelaufen')
# ENDE BLOG-LISTE
# ---------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------
# ABSCHNITTSZAHLEN DES PROBLEM-ARTIKELS. P-13 nennt "Anzahl Abschnitte" ausdruecklich im
# Geltungsbereich, und genau diese Zahl stand nach B5 getippt da: drei Descriptions,
# Article-headline und -description, Breadcrumb-Schema, sichtbarer Breadcrumb, H1,
# Lead und "Kurz gesagt" im Artikel, dazu ItemList-Schema und Karte auf /blog/, der
# Querverweis in huellen-kompatibilitaet und llms.txt. Hier stand "Gemessen: 16 Stellen
# mit der Ursachen-Zahl und 11 mit der Stoerungsbild-Zahl" -- die Zahlen sind entfernt,
# nicht korrigiert: Sie haengen an der Dateimenge UND an der Textbildung, und nach dem
# Umbau von `_text_und_metas` (JSON-LD-Werte dazu) ergaben drei Messungen drei Ergebnisse.
# Wie viele Stellen es sind, zaehlt das Gate selbst; eine getippte Zahl daneben ist genau
# das, was dieses Gate verhindern soll. Der Title traegt KEINE
# Abschnittszahl (er sagt "Meist in 2 Min. geloest"), die erste Fassung dieses
# Kommentars hat ihn falsch mitgezaehlt. Fuenf Proben des Pruefers blieben gruen,
# darunter der Regelfall redaktioneller Arbeit: ein h2 zu h3 heruntergestuft, der Abschnitt
# also weg, die Zahlen unveraendert.
# Abgeleitet wird aus der Struktur: Die Ursachen sind als "<h2>1." bis "<h2>N." numeriert,
# die weiteren Stoerungsbilder sind die uebrigen Problem-h2 ohne die drei Abschluss-
# Abschnitte. Beides zusammen deckt jede Formulierung, in der das Repo die Zahlen nennt.
_ART = 'blog/controller-verbindet-nicht/index.html'
_ZW_ART = {'fünf': 5, 'vier': 4, 'drei': 3, 'sechs': 6, 'sieben': 7, 'acht': 8, 'neun': 9,
           'zwei': 2}
if os.path.exists(_ART):
    # Kommentare entfernen und die Attributnotation normalisieren, BEVOR gezaehlt wird.
    # Ohne das erste blieb ein auskommentierter Stoerungsbild-Abschnitt gruen, waehrend elf
    # Stellen weiter vier nannten; ohne das zweite war `data-rolle='stoerung'` ein
    # Fehlalarm, und einfach gequotete Attribute sind die Notation von 101 Stellen im Repo.
    # Dieser Fix stand schon in Runde 15 im Skript und ist nie gelandet, weil das
    # Batch-Skript vorher an einer Assertion abgebrochen ist -- gemeldet hatte ich ihn
    # trotzdem.
    _ah_roh = open(_ART, encoding='utf-8').read()
    _ah = re.sub(r'<!--.*?-->', ' ', _ah_roh, flags=re.S)
    _ah = re.sub(r"(\w)\s*=\s*'([^']*)'", r'\1="\2"', _ah)
    _ah = re.sub(r'(\w)\s*=\s*"', r'\1="', _ah)
    _h2 = [re.sub(r'<[^>]*>', '', m).strip()
           for m in re.findall(r'<h2[^>]*>.*?</h2>', _ah, re.S)]
    # Die Stoerungsbild-Abschnitte tragen `data-rolle="stoerung"` im Markup. Die erste
    # Fassung zaehlte per AUSSCHLUSS (alle nicht numerierten h2 minus drei Literale) und
    # war damit ein Fehlalarm auf richtigem Inhalt: "Fazit" in "Fazit: Was wirklich hilft"
    # umbenannt oder ein neuer Einleitungsabschnitt erhoehte die Zahl, und das Gate
    # verlangte eine 5, die der Artikel nicht hergibt -- Mechanismus 6 des eigenen
    # Patterns, im eigenen neuen Gate.
    _n_ursachen = len([x for x in _h2 if re.match(r'^\d+\.', x)])
    _n_weitere = len(re.findall(r'<h2[^>]*\bdata-rolle="stoerung"', _ah))
    if _n_ursachen < 2 or _n_weitere < 1:
        err(f'§A1: aus {_ART} lassen sich keine plausiblen Abschnittszahlen ableiten '
            f'({_n_ursachen} numerierte Ursachen, {_n_weitere} weitere) — Struktur der '
            f'h2-Ueberschriften geaendert?')
    else:
        # Die numerierten Ueberschriften muessen 1..N lauten, sonst zaehlt die Ableitung
        # eine Luecke mit.
        _nrn = [int(re.match(r'^(\d+)\.', x).group(1)) for x in _h2 if re.match(r'^\d+\.', x)]
        if _nrn != list(range(1, _n_ursachen + 1)):
            err(f'§A1: die numerierten Abschnitte in {_ART} lauten {_nrn}, erwartet ist '
                f'1 bis {_n_ursachen}')
        _URS = re.compile(r'(\d+|fünf|vier|sechs|sieben|acht|neun|drei|zwei)\s+'
                          r'(?:häufigsten\s+)?Ursachen')
        _WEI = re.compile(r'(\d+|fünf|vier|sechs|sieben|acht|neun|drei|zwei)\s+'
                          r'weitere[nr]?\s+Störungsbilder')
        _u_treffer = _w_treffer = 0
        for _f in _zu_pruefen:
            # Klartext plus Metas: Die Abschnittszahlen stehen auch in den
            # Descriptions und im Article-Schema, also in Attributen.
            _roh_f = open(_f, encoding='utf-8').read()
            _fh = _text_und_metas(_roh_f)
            _sicht = _klartext(_roh_f)
            for _mu, _soll, _was, _zz in ((_URS, _n_ursachen, 'Ursachen', 'u'),
                                          (_WEI, _n_weitere, 'weitere Störungsbilder', 'w')):
                for _m in _mu.finditer(_fh):
                    # Fuer den Anker zaehlen nur SEITEN: Repoweit gezaehlt deckte eine
                    # Kopie in llms.txt oder einem Generator das Verschwinden von der
                    # Seite. Dieselbe Lehre wie beim Mengensatz- und Pool-Anker.
                    # SICHTBAR muss es sein, nicht bloss ausgeliefert. Runde 20 hat die
                    # Zusage von der Seite genommen und als JSON-LD-Wert hinterlegt: Der
                    # Anker war erfuellt, die Seite zeigte nichts, und §A4 faengt das
                    # nicht (es gibt keine maschinelle Pruefung "Schema-Zeichenkette steht
                    # sichtbar"). Der WERT wird weiter in Metas und JSON-LD geprueft, denn
                    # eine falsche Zahl ist auch dort falsch.
                    if _f in pages and _mu.search(_sicht):
                        if _zz == 'u':
                            _u_treffer += 1
                        else:
                            _w_treffer += 1
                    _r = _m.group(1)
                    _ist = int(_r) if _r.isdigit() else _ZW_ART.get(_r.lower())
                    if _ist is not None and _ist != _soll:
                        err(f'§A1: {_f} nennt "{_m.group(0)}", {_ART} hat {_soll} '
                            f'{_was} (aus den h2-Ueberschriften abgeleitet)')
        if not _u_treffer:
            err(f'§A1: die Zahl der Ursachen steht nirgends mehr sichtbar auf einer '
                f'Seite — sie ist aus {_ART} ableitbar und gehoert dorthin zurueck')
        if not _w_treffer:
            err(f'§A1: die Zahl der weiteren Stoerungsbilder steht nirgends mehr '
                f'sichtbar auf einer Seite — sie ist aus {_ART} ableitbar')
        # Namensverweise auf Abschnitte muessen auf vorhandene h2 zeigen. Vorher standen
        # hier vier NUMMERN-Verweise ("Punkt 4 oben", "derselbe Punkt wie in Ursache 5"):
        # Der Pruefer hat Ursache 4 und 5 getauscht und korrekt neu numeriert -- das Gate
        # erlaubt Umsortierung ausdruecklich -- und alle vier Verweise zeigten auf den
        # falschen Abschnitt, bei gruenem verify. Ein falscher NAME faellt dem Leser auf,
        # eine falsche Nummer nicht; deshalb stehen jetzt Namen da, und sie werden geprueft.
        # Alle Ueberschriften, nicht nur h2: Der Artikel fuehrt auch h3, und ein Verweis
        # darauf darf nicht rot werden.
        _ueber = {re.sub(r'\s+', ' ', re.sub(r'<[^>]*>', '', m)).strip()
                  for m in re.findall(r'<h[23][^>]*>.*?</h[23]>', _ah, re.S)}
        _ueber = {re.sub(r'^\d+\.\s*', '', t) for t in _ueber} | _ueber
        # "Abschnitten" (Dativ Plural) traf das Muster nicht: Von fuenf Namensverweisen im
        # Artikel waren nur zwei erfasst, und die drei im Fazit blieben ungeprueft -- eine
        # umbenannte Ueberschrift liess sie still auf nichts zeigen.
        # Anfuehrungszeichen: deutsche, englische, gerade und die franzoesischen Guillemets.
        _AUF = r'„|&bdquo;|"|“|»|&raquo;'
        _ZU = r'"|&ldquo;|“|”|«|&laquo;'
        # Aufzaehlungen mitlesen: Das Fazit nennt "Abschnitten" einmal und dann DREI
        # Namen in Folge. Die erste Fassung verlangte das Wort direkt vor jedem
        # Anfuehrungszeichen und erfasste deshalb nur den ersten -- drei von fuenf
        # Verweisen blieben ungeprueft. Gelesen wird deshalb der Satz nach dem Wort und
        # jeder zitierte Name darin.
        _KLAMMER = re.compile(r'(?:' + _AUF + r')([^"„“”»«]{6,70})(?:' + _ZU + r')')
        _refs = []
        _kt_art = _klartext(_ah)
        for _am in re.finditer(r'Abschnitt(?:e|en|es|s)?\s', _kt_art):
            _satz = _kt_art[_am.end():]
            _ende = min((x for x in (_satz.find('. '), _satz.find('\u00b6')) if x >= 0),
                        default=len(_satz))
            _refs += [m.group(1) for m in _KLAMMER.finditer(_satz[:_ende + 1])]
        for _ref in _refs:
            _ref = re.sub(r'\s+', ' ', _ref).strip().rstrip('.,;:')
            # Der Verweis muss eine Ueberschrift GANZ nennen. Die erste Fassung hat
            # beidseitig auf Teilstrings geprueft, womit `Abschnitt "Controller"` und
            # `Abschnitt "Fazit zur Spieleunterstuetzung unter Android"` gruen blieben.
            if _ref not in _ueber:
                err(f'§A1: {_ART} verweist auf einen Abschnitt "{_ref[:50]}", den es so '
                    f'nicht gibt — Ueberschrift umbenannt oder Verweis veraltet (der '
                    f'Verweis muss die Ueberschrift wortgleich nennen)')
# ENDE ABSCHNITTSZAHLEN
# ---------------------------------------------------------------------------------------

# Gegenprobe zur Annahme "kabelgebunden = kein Akku": Eine als kabelgebunden gefuehrte
# Seite, die eine Akkulaufzeit nennt, wird gemeldet. Gesucht wird auf dem Text, in beiden
# Reihenfolgen -- im Bestand stehen sechs Schreibweisen ("40 h Akku", "40h-Akku",
# "12 Stunden Akkulaufzeit"), und drei Vorfassungen sind an der Markup-Form gescheitert.
_EINH = r'(?:h|Std|Stdn|Stunde|Stunden|Min|Minute|Minuten)\.?\b'
_AKKU = (r'(?:Akku|Batterie|Laufzeit)\w*[^<]{0,30}?\d+\s*[-–]?\s*' + _EINH
         + r'|\d+\s*[-–]?\s*' + _EINH + r'[^<]{0,30}?(?:Akku|Batterie|Laufzeit)')
for _p in _ctrl:
    if not (_steck(_p) and not _funk(_p)):
        continue
    _d = (_p.get('detail') or '').strip('/')
    # Beide Kandidatenpfade pruefen, nicht nur den ersten: Eine spaeter ergaenzte
    # produkte/<slug>/-Seite waere sonst von der Gegenprobe ausgenommen.
    _gefunden_eine = False
    for _kand in (f'{_d}/index.html', f"produkte/{_p.get('slug')}/index.html"):
        if not (_kand and os.path.exists(_kand)):
            continue
        _gefunden_eine = True
        _ph = open(_kand, encoding='utf-8').read()
        _pt = re.sub(r'</(?:p|li|td|th|h[1-6]|div)>|<br\s*/?>', ' ¶ ', _ph, flags=re.I)
        _pt = html.unescape(re.sub(r'<[^>]*>', ' ', _pt))
        # Nennt der SATZ ein fremdes Produkt, gehoert die Laufzeit dorthin. Ein Name, der
        # im eigenen Namen steckt ("Kishi V3" in "Kishi V3 Pro"), ist kein Fremdname --
        # sonst sind zwei der elf Seiten komplett blind.
        _eigen = _pfeld(_p, 'name')
        _fremd = [_pfeld(x, 'name') for x in items
                  if x.get('slug') != _p.get('slug') and len(_pfeld(x, 'name')) > 3
                  and _pfeld(x, 'name') not in _eigen]
        for _m in re.finditer(_AKKU, _pt):
            _l = max(_pt.rfind(c, 0, _m.start()) for c in '.!?¶') + 1
            _r = min((x for x in (_pt.find(c, _m.end()) for c in '.!?¶') if x >= 0),
                     default=len(_pt))
            if any(fn in _pt[_l:_r] for fn in _fremd):
                continue
            err(f"§A1: {_p.get('slug')} gilt als kabelgebunden (kein BT/Bluetooth in "
                f"Verb.), aber {_kand} nennt eine Akkulaufzeit. Entweder stimmt die "
                f"Gleichsetzung \"kabelgebunden = ohne Akku\" nicht mehr (dann Zahl und "
                f"Satz im Problem-Artikel pruefen), oder die Laufzeit gehoert zu einem "
                f"Fremdprodukt (dann den Satz umformulieren)")
            break
        # kein break: der zweite Kandidatenpfad wird mitgeprueft
    if not _gefunden_eine:
        err(f"§A1: zu {_p.get('slug')} (kabelgebunden) ist keine Produktseite gefunden "
            f"worden — die Akku-Gegenprobe laeuft fuer dieses Produkt nicht")

# Genannte Lesezeit gegen den tatsaechlichen Textumfang. Die Zahl stand an drei Orten
# getippt (Byline des Artikels, Karte auf /blog/, Karte auf der Startseite) und war am
# 01.10.2026 auf 17 von 19 Seiten zu hoch -- einmal 8 Minuten fuer einen 5-Minuten-Text.
# Ein Artikel hatte drei verschiedene Werte: 3 auf der Startseite, 5 in der eigenen
# Byline, 4 in Wahrheit. Jede Textaenderung macht eine getippte Lesezeit falscher, und
# B5 hat diesen Artikel gerade von 803 auf 1232 Woerter verlaengert (Regel aus
# lesezeit.py). Die erste Fassung dieses Kommentars nannte "272 Woerter" aus einer
# ad-hoc-Zaehlung mit anderem Wortmuster -- dieselbe Sorte unbelegte Zahl, gegen die
# das Gate darunter gebaut ist.
# Die Rechenregel kommt aus lesezeit.py, geteilt mit gen_preisfrage.py und
# sync_lesezeit.py: zwei eigene Formulierungen derselben Regel waeren der Fehler, der
# hier schon dreimal aufgetreten ist.
#
# Abdeckungs-Anker (Pruefer-Befund 01.10.): Die erste Fassung band beide Pruefungen an
# genau ein Markup. Der Pruefer hat sechs Umschreibungen gezeigt, die gruen blieben,
# obwohl die Zahl nachweisbar falsch war: `class="article-byline compact"`,
# `&middot;` statt `·`, "Lesezeit: 9 Min.", "ca. 9 Min. Lesezeit", gedrehte
# Attributreihenfolge in der Karte und eine umbenannte Byline-Klasse. Die letzte ist die
# schwerste, weil sie Byline-Pruefung, Karten-Pruefung UND das Nachziehen in
# sync_lesezeit.py gleichzeitig abschaltet; beide Dateien benutzen dieselben Muster, die
# deshalb seit dem 01.10. in lesezeit.py stehen. In der Nachpruefung kamen zwei weitere
# Loecher dazu: eine Lesezeit in einem title/alt/aria-Attribut, und 20 Zeichen Markup
# zwischen Zahl und Wort. Beide hatten dieselbe Ursache -- das Fenster wurde aus dem
# rohen HTML geschnitten und erst DANACH entTagt.
# Geprueft wird auf dem Text ohne Tags, mit Rueckabbildung auf die Originalposition, und
# verglichen wird die STELLE, nicht die Anzahl: Jedes "Lesezeit" neben einer Zahl oder
# Zeiteinheit muss genau dort stehen, wo eines der beiden Muster seine Zahl liest. Heute
# 41 von 41 (19 Bylines, 19 Karten auf /blog/, 3 auf der Startseite). Attribute,
# Kommentare, CDATA und Skript-Bloecke werden getrennt geprueft, weil sie im Text ohne
# Tags nicht vorkommen.
# Bewusste Einschraenkung: Eine Lesezeit im Fliesstext wird rot, auch wenn sie stimmt.
# Sie gehoert in Byline oder Karte, weil nur dort jemand nachrechnet.
# Beide Muster kommen aus lesezeit.py, geteilt mit sync_lesezeit.py.
_BYLINE, _KARTE_LZ = _lz_BYLINE, _lz_KARTE
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    if 'Lesezeit' not in _h:
        continue
    # Eine Lesezeit gehoert in den sichtbaren Text. Steht sie woanders, sieht sie kein
    # Leser, behauptet aber trotzdem etwas.
    # Erste Fassung: vier Attributnamen aufgezaehlt (title/alt/aria-label/content) --
    # data-hinweis, placeholder und summary blieben gruen. Zweite Fassung: alle Namen,
    # aber nur doppelte Anfuehrungszeichen -- `title='9 Min. Lesezeit'` blieb gruen. Das
    # war zweimal dieselbe Form: eine Liste. Jetzt gilt es fuer jede Notation, und die
    # Nicht-Text-Orte sind nach Art getrennt, weil die Meldung sonst die falsche Ursache
    # nennt (ein JS-String wurde als Attribut gemeldet).
    for _bl in re.finditer(r'<(script|style)\b[^>]*>((?:(?!</\1>).)*?Lesezeit(?:(?!</\1>).)*?)</\1>',
                           _h, re.S):
        err(f'§A1: {_f} nennt eine Lesezeit in einem <{_bl.group(1)}>-Block — dort '
            f'rechnet sie kein Gate nach')
    _ohne_bl = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', ' ', _h, flags=re.S)
    for _am in re.finditer(r'[\w-]+\s*=\s*(?:"([^"]*Lesezeit[^"]*)"'
                           r"|'([^']*Lesezeit[^']*)'"
                           r'|([^\s"\'>]*Lesezeit[^\s>]*))', _ohne_bl):
        _wert = next(g for g in _am.groups() if g is not None)
        err(f'§A1: {_f} nennt eine Lesezeit in einem Attribut ("{_wert[:60]}") — '
            f'dort sieht sie kein Leser und kein Gate rechnet sie nach')
    for _cm in re.finditer(r'<!(?:--((?:(?!-->).)*?Lesezeit(?:(?!-->).)*?)--'
                           r'|\[CDATA\[((?:(?!\]\]>).)*?Lesezeit(?:(?!\]\]>).)*?)\]\])>',
                           _h, re.S):
        _wert = next(g for g in _cm.groups() if g is not None)
        err(f'§A1: {_f} nennt eine Lesezeit in einem Kommentar- oder CDATA-Abschnitt '
            f'("{_wert.strip()[:60]}") — sie altert dort ungeprueft')
    # Abdeckung POSITIONSGENAU. Die zweite Fassung verglich nur die ANZAHL der Anspruechte
    # mit der Anzahl der Treffer, und der Pruefer hat gezeigt, dass sich ein Fehlen und
    # ein Zuviel aufheben: Eine Karte auf "neunundneunzig Min. Lesezeit" geaendert senkt
    # beide Zahlen um eins, die Differenz bleibt null, und eine frei erfundene Lesezeit
    # stand gruen auf der Seite. Jetzt wird jeder einzelne Anspruch danach gefragt, ob er
    # in einem Treffer LIEGT.
    # Der Text wird dafuer einmal ohne Tags gebildet, mit Rueckabbildung auf die
    # Originalposition: Damit ist der Abstand zwischen Zahl und Wort der Abstand im Text
    # (200 Zeichen Markup dazwischen schieben die Zahl nicht mehr weg), und die Position
    # bleibt trotzdem pruefbar.
    # Nebenbei wird mitgezaehlt, ob ein Zeichen INNERHALB eines Kastens liegt, in den die
    # Lesezeit gehoert (article-meta in der Karte, article-byline im Artikel). Das steuert
    # nur die URSACHE in der Meldung, nicht ihr Auftreten: Der Fehler wird so oder so
    # gemeldet. Noetig, weil die Meldung bei Inline-Markup in einer Karte vorher
    # "gehoert in eine Artikel-Karte" sagte, waehrend die Zahl genau dort stand -- eine
    # richtige Meldung mit falscher Ursache schickt den Leser in die falsche Richtung,
    # und das ist an diesem Projekt schon mehrfach passiert (sync_footer als Ursache der
    # abgeschnittenen STATUS, "filtert nicht" bei nur anderem Parameternamen).
    _VOID_LZ = {'img', 'br', 'hr', 'input', 'meta', 'link', 'source', 'area', 'col',
                'embed', 'param', 'track', 'wbr', 'base'}
    _klar, _pos, _inbox = [], [], []
    _tiefe, _box_tiefe = 0, None
    for _tm in re.finditer(r'<[^>]*>|[^<]+', _h):
        _roh_t = _tm.group(0)
        if _roh_t.startswith('<'):
            _tn = re.match(r'</?\s*([a-zA-Z][\w-]*)', _roh_t)
            if not _tn or _roh_t.startswith('<!'):
                continue
            _name = _tn.group(1).lower()
            if _roh_t.startswith('</'):
                if _box_tiefe is not None and _tiefe <= _box_tiefe:
                    _box_tiefe = None
                _tiefe = max(0, _tiefe - 1)
            elif _name not in _VOID_LZ and not _roh_t.rstrip().endswith('/>'):
                _tiefe += 1
                if _box_tiefe is None and re.search(
                        r'class="[^"]*\b(?:article-meta|article-byline)\b', _roh_t):
                    _box_tiefe = _tiefe
            continue
        for _k, _ch in enumerate(_roh_t):
            _klar.append(_ch)
            _pos.append(_tm.start() + _k)
            _inbox.append(_box_tiefe is not None)
    _lz_text = ''.join(_klar)
    # S-3 (vierte Pruefung): Die erste positionsgenaue Fassung nahm den ganzen
    # Match-SPAN als abgedeckt. Weil `.*?` in BYLINE bis zum ersten "· Zahl Min.
    # Lesezeit" laeuft, lag eine davor eingefuegte zweite, falsche Lesezeit INNERHALB
    # des Spans und galt damit als geprueft -- "99 Min. Lesezeit, gerundet · 6 Min.
    # Lesezeit" stand gruen und sichtbar auf der Seite. Dasselbe im Karten-Excerpt.
    # Abgedeckt ist deshalb genau die Stelle, die das Muster als Zahl liest: Gruppe 3
    # ist bei beiden Mustern "\s*Min. Lesezeit".
    _erlaubt = {m.start(3) + m.group(3).index('Lesezeit')
                for m in list(_BYLINE.finditer(_h)) + list(_KARTE_LZ.finditer(_h))}
    for _m in re.finditer(r'Lesezeit', _lz_text):
        # Anspruch liegt vor, wenn eine Zahl ODER eine Zeiteinheit in Reichweite steht.
        # Nur auf Ziffern zu pruefen war ein Loch: "neunundneunzig Min. Lesezeit" in einer
        # Karte blieb gruen, weil weder das Karten-Muster (\d+) noch der Anspruch-Test
        # zugriffen. Eine ausgeschriebene Zahl behauptet dasselbe.
        _fenster = _lz_text[max(0, _m.start() - 35):_m.end() + 35]
        if not re.search(r'\d|\bMin\b|\bMinute', _fenster):
            continue  # ohne Zahl und ohne Zeiteinheit ist es das Wort, keine Angabe
        if _pos[_m.start()] not in _erlaubt:
            _umfeld = re.sub(r'\s+', ' ', _lz_text[max(0, _m.start() - 40):_m.end() + 14])
            if _inbox[_m.start()]:
                # Die Zahl steht am richtigen Ort, nur liest das Muster sie nicht mehr.
                _grund = ('Sie steht in einem article-meta- oder article-byline-Kasten, '
                          'also am richtigen Ort — aber das Muster in scripts/lesezeit.py '
                          'liest sie dort nicht mehr. Typische Ursache ist Markup zwischen '
                          'Kasten und Zahl (<strong>6</strong>, ein Kommentar, ein span). '
                          'Entweder das Markup entfernen oder BYLINE/KARTE in '
                          'scripts/lesezeit.py mitziehen')
            else:
                _grund = ('Sie gehoert in die Byline oder in eine Artikel-Karte, denn nur '
                          'dort rechnet sie jemand nach. Hier steht sie ausserhalb beider '
                          'Kaesten, also im Fliesstext: dann verschieben')
            err(f'§A1: {_f} nennt eine Lesezeit, die kein Gate-Muster erfasst '
                f'("...{_umfeld.strip()}..."). {_grund} — eine getippte Lesezeit altert '
                f'ungeprueft, genau das war der Zustand vor dem 01.10.')
# Typografie der Anfuehrungszeichen im sichtbaren Text. Der achtzehnte Pruefbericht hat
# zwei Stellen gefunden, die mit „ oeffnen und mit geradem " schliessen -- beide in Text,
# den dieses Paket neu geschrieben hat, beide sichtbar auf der Seite. Grün blieben sie,
# weil das Namensverweis-Gate das gerade Zeichen absichtlich zulaesst (es soll den Verweis
# FINDEN, auch bei schiefer Typografie). Die Typografie braucht also ihre eigene Pruefung.
# Repoweit gemessen: 2 Treffer, beide aus diesem Paket. Der Bestand ist sauber, das Gate
# kann deshalb scharf stehen.
# Metas und JSON-LD gehoeren dazu: Runde 19 hat gezeigt, dass `„Klick&quot;` in einer
# Meta-Description gruen blieb, waehrend dieselbe Form im sichtbaren Text rot wird. Die
# Description ist ausgelieferter Text wie jeder andere. Bestand vorher gemessen: 0 Treffer,
# das Gate kann also sofort beidseitig scharf stehen.
for _f in pages:
    for _qm in re.finditer(r'„[^„“"»«]{1,90}"',
                           _text_und_metas(open(_f, encoding='utf-8').read())):
        err(f'§: {_f} schliesst ein mit „ geoeffnetes Zitat mit geradem " statt mit “ '
            f'("{_qm.group(0)[:60]}")')

_lz_soll = {}
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    _soll = _lesezeit_minuten(_h)
    _pfad = '/' + os.path.dirname(_f.replace(os.sep, '/')) + '/'
    # finditer, nicht search: Die zweite Fassung prueefte nur die ERSTE Byline je Seite,
    # eine zweite mit "99 Min. Lesezeit" blieb gruen.
    for _bm in _BYLINE.finditer(_h):
        _lz_soll[_pfad] = _soll
        if _soll is None:
            # Ohne <main> liefert lesezeit.minuten() None. Die erste Fassung uebersprang
            # das still (`if _soll is not None`), womit eine Seite ohne <main> in Byline
            # UND Karte frei erfundene Zahlen tragen durfte, beide gruen.
            err(f'§A1: {_f} nennt eine Lesezeit, hat aber kein <main>-Element — damit '
                f'laesst sich kein Artikeltext bestimmen und die Zahl ist ungeprueft')
            continue
        if int(_bm.group(2)) != _soll:
            err(f'§A1: {_f} nennt {_bm.group(2)} Min. Lesezeit, der Artikeltext ergibt '
                f'{_soll} (scripts/sync_lesezeit.py zieht nach)')
# Jede Karte muss dasselbe sagen wie die Seite, auf die sie zeigt. Ein unbekanntes Ziel
# ist dabei selbst ein Fehler: Die zweite Fassung uebersprang es stumm (`_soll is None`),
# womit eine Karte auf einen Artikel ohne Byline frei erfinden durfte, was sie wollte --
# und `sync_lesezeit.py` meldete dazu "0 unerfasst", weil mit der Zahl auch das Wort
# verschwand.
for _f in pages:
    for _m in _KARTE_LZ.finditer(open(_f, encoding='utf-8').read()):
        if _m.group(1) not in _lz_soll:
            err(f'§A1: {_f} nennt fuer {_m.group(1)} eine Lesezeit, aber dort findet '
                f'das Byline-Muster keine — entweder fehlt sie, oder ihr Markup bzw. '
                f'ihre Formulierung wurde geaendert (dann steht sie da, ist aber '
                f'ungeprueft). Wiederherstellen oder die Angabe aus der Karte nehmen')
            continue
        _soll = _lz_soll[_m.group(1)]
        if _soll is None:
            continue  # bereits bei der Byline gemeldet
        if int(_m.group(2)) != _soll:
            err(f'§A1: {_f} nennt fuer {_m.group(1)} {_m.group(2)} Min. Lesezeit, '
                f'die Seite selbst ergibt {_soll}')

# Anwesenheits-Anker (M-2/G-2 der vierten Pruefung). Der ganze Block haengt am Wort
# "Lesezeit": Wurde es in Byline UND Karte konsistent zu "Lesedauer" umbenannt oder die
# Angabe ganz entfernt, blieb alles gruen, und sync_lesezeit.py meldete "18 Artikel,
# 0 unerfasst", also wieder seinen Blindfleck als Erfolg. Ein Gate, das nur prueft was da
# ist, merkt nicht, dass etwas fehlt. Jeder Blog-Artikel traegt deshalb genau eine
# gegatete Lesezeit in seiner Byline.
# Redirect-Stubs sind keine Artikel: Sie tragen noindex plus meta-refresh, haben kein
# <main> und keine Byline. Die erste Fassung hielt jede Seite unter blog/ fuer einen
# Artikel, womit ein Stub dort zwei Fehlalarme ausgeloest haette (keine Byline, keine
# Karte). Im Repo liegen 16 solche Stubs, bisher keiner unter blog/.
def _ist_stub(_pfad):
    _t = open(_pfad, encoding='utf-8').read()
    return 'http-equiv="refresh"' in _t
_blog_artikel = sorted(f for f in pages
                       if re.match(r'blog/[^/]+/index\.html$', f.replace(os.sep, '/'))
                       and not _ist_stub(f))
for _f in _blog_artikel:
    _n = len(_BYLINE.findall(open(_f, encoding='utf-8').read()))
    if _n != 1:
        err(f'§A1: {_f} hat {_n} gegatete Lesezeit-Angaben in der Byline, erwartet ist '
            f'genau eine — entfernt, umformuliert oder doppelt gesetzt')
# Dasselbe fuer die 22 Artikel-Karten. Zwei Fassungen vorher: Die erste deckte nur die
# 19 Bylines, also die Haelfte der Stellen. Die zweite haengte an einem Regex ueber
# `<a href=... class="...article-card...">` und war damit an eine Schreibweise gebunden --
# `class` vor `href`, einfache Anfuehrungszeichen, ein Zeilenumbruch nach `<a` oder die
# Karte als `<div>` mit innerem `<a>` schalteten sie ab, waehrend eine falsche Lesezeit
# sichtbar auf der Seite stand. Genau die Lehre, die dieser Anker durchsetzen soll, an ihm
# selbst vorbeigegangen.
# Jetzt wird GEPARST (lesezeit.karten, html.parser): Attribute als Attribute, Tiefe
# gezaehlt. Geprueft wird zweierlei -- jede geparste Karte traegt eine Lesezeit, UND das
# Muster, mit dem sync_lesezeit.py sie pflegt, findet sie auch. Letzteres ist der Punkt,
# an dem eine Umformatierung auffaellt, bevor sie die Pflege still beendet.
for _f in pages:
    _h = open(_f, encoding='utf-8').read()
    _geparst = _lz_karten(_h)
    for _href, _text in _geparst:
        if not _href or not _href.startswith('/blog/'):
            continue
        if not re.search(r'\d+\s*Min\. Lesezeit', _text):
            err(f'§A1: die Artikel-Karte fuer {_href} in {_f} traegt keine Lesezeit — '
                f'Label entfernt oder umformuliert, damit zeigt die Liste eine Zahl, '
                f'die niemand nachrechnet, oder gar keine')
    _blog_karten = [k for k in _geparst if (k[0] or '').startswith('/blog/')]
    _gepflegt = len(_KARTE_LZ.findall(_h))
    if len(_blog_karten) != _gepflegt:
        err(f'§A1: {_f} hat {len(_blog_karten)} Artikel-Karten, aber '
            f'scripts/sync_lesezeit.py findet nur {_gepflegt} davon — das Markup wurde '
            f'so umformatiert, dass der Sync die Lesezeit dort nicht mehr nachzieht')

# Soll-Anzahl der Karten (G-4): Eine ganze Karte konnte aus /blog/ verschwinden, ohne dass
# etwas rot wurde. Jeder Blog-Artikel gehoert genau einmal in die Blog-Liste.
if 'blog/index.html' in pages:
    _bh = open('blog/index.html', encoding='utf-8').read()
    _gelistet = [k[0] for k in _lz_karten(_bh) if (k[0] or '').startswith('/blog/')]
    for _f in _blog_artikel:
        _pf = '/' + os.path.dirname(_f.replace(os.sep, '/')) + '/'
        if _gelistet.count(_pf) != 1:
            err(f'§A1: {_pf} steht {_gelistet.count(_pf)}x als Karte auf /blog/, '
                f'erwartet ist genau einmal')

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

# Statischer Pflicht-Footer (§A2/§C2), zeichengleich gegen scripts/sync_footer.py.
# Bis 01.10.2026 pruefte das Gate darunter nur die ANWESENHEIT von Impressum-Link,
# Datenschutz-Link und Transparenz-Hinweis. Der Text selbst lag als Literal an vier Orten
# (drei Generatoren und 111 HTML-Dateien) und haette dort beliebig auseinanderlaufen
# koennen -- genau die Lage, die der Header vor sync_header.py hatte, und genau das
# Muster, nach dem an einem einzigen Tag dreimal zwei Kopien derselben Regel gedriftet
# sind. Quelle ist jetzt buildFooter() in main.js; damit sagen die Fassung ohne JS und
# die mit JS zwangslaeufig dasselbe.
try:
    import sync_footer as _sf
    _SOLL_FOOTER = _sf.footer_html(*_sf.aus_mainjs())
except Exception as _e:
    _SOLL_FOOTER = None
    err(f"§C2: Pflicht-Footer nicht ableitbar ({type(_e).__name__}: {_e}) — ohne die "
        f"Quelle in main.js laesst er sich nicht pruefen")
if _SOLL_FOOTER:
    for _f in pages:
        _h = open(_f, encoding='utf-8').read()
        if 'http-equiv="refresh"' in _h:
            continue
        _m = re.search(r'<footer[^>]*id="site-footer"[^>]*>(.*?)</footer>', _h, re.S)
        if not _m:
            err(f"§C2: {_f} hat kein site-footer-Element — ohne JavaScript keine "
                f"Pflichtangaben (python3 scripts/sync_footer.py)")
        elif _m.group(1) != _SOLL_FOOTER:
            err(f"§C2: {_f} weicht im site-footer von scripts/sync_footer.py ab — "
                f"'python3 scripts/sync_footer.py' laufen lassen; steht die Abweichung "
                f"absichtlich dort, gehoert sie in buildFooter() in main.js")

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
                        [('gallery', g) for g in _pliste(_p, 'gallery')]:
        _wert = str(_wert or '')   # img als Zahl: .startswith mit AttributeError
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
        if _p and _bild and _bild not in [_pfeld(_p, 'img')] + _pliste(_p, 'gallery'):
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
    _bw = _spec_wie(_p, 'Bew', None)
    # str(): ein Nicht-String-Wert liess re.match hier mit TypeError abbrechen
    _m = re.match(r'([\d,]+)\s*\(([\d.]+)\)', str(_bw or ''))
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
    # Haertung: Ein Nicht-String-Wert oder ein fehlendes Bew.-Feld liess die Aufrufer mit
    # TypeError bzw. TypeError beim Vergleich abbrechen, statt zu melden. Rueckgabe ist
    # jetzt immer ein Paar; (0.0, 0) heisst "keine lesbare Bewertung", und die
    # Behauptungen darueber werden dann vom Gate als gekippt gemeldet.
    if p is None:
        return (0.0, 0)
    m = re.match(r'([\d,]+)\s*\(([\d.]+)\)', _spec_wie(p, 'Bew'))
    if m:
        return float(m.group(1).replace(',', '.')), int(m.group(2).replace('.', ''))
    return 0.0, 0

def _preis(p):
    # Delegiert, damit es nicht zwei Preisregeln gibt. Der Unterschied bleibt bewusst:
    # hier ist 0 der Ersatzwert, weil die Aufrufer sortieren und vergleichen.
    return _preis_zahl(p) or 0

_ctrl = [p for p in items if p.get('type') == 'controller' and _bew(p)[0]]
_zub = [p for p in items if p.get('type') != 'controller' and _bew(p)[1]]
_kuehler = [p for p in items if 'ühler' in _pfeld(p, 'name') or 'Cooler' in _pfeld(p, 'name')]
_gs = [p for p in items if p.get('brand') == 'GameSir']
_razer = [p for p in items if p.get('brand') == 'Razer' and _bew(p)[0]]

def _produkt(_slug):
    """products.json-Eintrag zu einem Slug, oder None mit Meldung.

    `next(p for p in items if p['slug'] == ...)` ohne Default warf StopIteration, sobald
    ein Produkt umbenannt oder entfernt wurde: alles danach lief nicht mehr, und keine
    Meldung nannte die Ursache.
    """
    _t = next((p for p in items if p.get('slug') == _slug), None)
    if _t is None:
        err(f'§A1: products.json kennt den Slug "{_slug}" nicht mehr — eine Aussage '
            f'darueber laesst sich nicht pruefen (umbenannt oder entfernt?)')
    return _t


def _nicht_leer(_menge, _was):
    """Meldet statt mit ValueError abzubrechen, wenn eine Menge leer ist.

    Ein neuer Controller ohne `detail`-Feld liess `max()` mit "iterable argument is empty"
    sterben, womit alles danach nicht mehr lief und keine Meldung die Ursache nannte --
    dieselbe Klasse wie die Nicht-String-Werte, nur eine Zeile weiter.
    """
    if not _menge:
        err(f'§A1: die Menge "{_was}" ist leer, eine Aussage darueber laesst sich nicht '
            f'pruefen — products.json geaendert (fehlendes Feld, anderer type)?')
        return False
    return True


def _behauptung(bedingung, text):
    if not bedingung:
        err(f"SUPERLATIV gekippt (§A6): {text}")

# Die Aussagen stehen so in den Claims und auf den Marken-Seiten.
_behauptung(_nicht_leer(_razer, "_razer") and max(_razer, key=lambda p: _bew(p)[0])['slug'] == 'razer-kishi-v3',
            '"der bestbewertete Razer" gilt nicht mehr fuer den Kishi V3')
_behauptung(_nicht_leer(_zub, "_zub") and max(_zub, key=lambda p: _bew(p)[1])['slug'] == 'risoka-finger-sleeves',
            '"unser meistbewertetes Zubehoer" gilt nicht mehr fuer die RISOKA Sleeves')
_behauptung(_nicht_leer(_ctrl, "_ctrl") and min(_ctrl, key=lambda p: _bew(p)[0])['slug'] == 'turtle-beach-atom',
            '"am schwaechsten bewerteter Controller" gilt nicht mehr fuer den Turtle Beach Atom')
_behauptung(_nicht_leer(_kuehler, "_kuehler") and min(_kuehler, key=lambda p: _bew(p)[0])['slug'] == 'razer-phone-cooler',
            '"schwaechste Bewertung im Kuehler-Segment" gilt nicht mehr fuer den Razer Phone Cooler')
_dual = [p for p in _gs if 'BT' in _spec(p, 'Verb.') and 'USB' in _spec(p, 'Verb.')]
_behauptung(len(_dual) == 1 and _dual[0]['slug'] == 'gamesir-g8-plus',
            '"der einzige GameSir mit BT und USB-C" gilt nicht mehr fuer den G8 Plus')
_tab = {p['slug'] for p in items if 'tablet' in _pliste(p, 'worksOn')}
_behauptung('gamesir-g8-plus' in _tab and 'razer-kishi-v3' not in _tab,
            'die Tablet-Zuordnung im Razer- oder GameSir-Text passt nicht mehr zu worksOn')
# Titel und Description von blog/guenstige-handy-controller nennen den Einstiegspreis
# fuer Hall-Effect-Sticks. Er stand dort bei 20 EUR, als der Ultimate 2C noch so viel
# kostete, und wurde beim Abgleich stumm falsch.
_hall = [p for p in items if 'Hall' in _spec(p, 'Sticks') and _preis_zahl(p) is not None]
if _hall:
    _guenstigster = min(_hall, key=_preis_zahl)
    _preis_hall = str(_preis_zahl(_guenstigster))
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
    _ma, _mb = _preis_zahl(_p_v3), _preis_zahl(_p_v3p)
    if _ma is None or _mb is None:
        # Ohne lesbaren Preis liess .group(1) hier mit AttributeError abbrechen statt
        # zu melden -- die letzte der Stellen aus dem Robustheits-Befund.
        err('§A1: Preis von razer-kishi-v3 oder -v3-pro ist nicht lesbar, die '
            'Aufpreis-Aussage laesst sich nicht pruefen')
    _a, _b = _ma or 0, _mb or 0
    _prozent = round((_b - _a) / _a * 100) if _a else 0
    _rf = 'marken/razer/index.html'
    if os.path.exists(_rf):
        _rh = open(_rf, encoding='utf-8').read()
        for _pm in re.finditer(r'rund (\d+) Prozent teurere', _rh):
            if int(_pm.group(1)) != _prozent:
                err(f"SUPERLATIV gekippt (§A6): {_rf} nennt {_pm.group(1)} Prozent Aufpreis "
                    f"V3 -> V3 Pro, aus products.json sind es {_prozent} Prozent")

_v3, _v3p = _produkt('razer-kishi-v3'), _produkt('razer-kishi-v3-pro')
_behauptung(_v3 is not None and _v3p is not None and _bew(_v3)[0] >= _bew(_v3p)[0],
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
