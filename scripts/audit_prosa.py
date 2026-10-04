#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prüft Produktwerte im Fließtext gegen products.json (§A1).

Warum ein eigenes Werkzeug: sync_product_values.py deckt die strukturierten Renderstellen
ab (Karten, Tabellen, Schema, Kacheln, Vergleichstabellen). Preise und Bewertungen stehen
aber zusätzlich im redaktionellen Text, in FAQ-Antworten und in Meta-Descriptions. Nach dem
Amazon-Vollabgleich am 30.09.2026 waren dort über 50 Werte veraltet, während beide Gates
grün meldeten. Mehrfach war das keine Zahlendifferenz, sondern ein gekipptes Urteil:
"gleich teuer" bei 70 gegen 32 Euro, "der günstigere Kishi V3" bei 88 gegen 63 Euro.

Der Ansatz: nur Werte prüfen, die dem Produktnamen GRAMMATISCH ANHÄNGEN
("G8 Plus (90 €)", "Kishi Ultra für 119 Euro", "steht bei 3,2 von 5 Sternen").
Ein reines Zeichenfenster um den Namen produziert Fehlalarme, sobald im selben Satz ein
zweites Produkt mit eigenem Preis steht. Genau daran ist die erste Fassung gescheitert:
Sie meldete "Kishi Ultra (63 €) gegen G8 Plus (76 €)" als Fehler, obwohl beide Werte
stimmten, und unterzählte gleichzeitig die echten Treffer.

Die /produkte/-Seiten prüft dieses Skript nicht: Ihr Text stammt aus gen_content.py und
wird von verify.py Abschnitt 6c über den Generator-Abgleich erfasst.
"""
import json, os, re, sys, glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

items = json.load(open('assets/data/products.json', encoding='utf-8'))
bySlug = {p['slug']: p for p in items}


def preis(p):
    m = re.search(r'(\d+)', (p.get('price') or '').replace('.', ''))
    return int(m.group(1)) if m else None


def bewertung(p):
    for k, v in p.get('specs') or []:
        if k.startswith('Bew'):
            m = re.match(r'([\d,]+)\s*\(([\d.]+)\)', v)
            if m:
                return m.group(1), int(m.group(2).replace('.', ''))
    return None, None


# Kurznamen, unter denen Produkte im Text auftauchen. Der volle Name ("GameSir G8 Plus")
# kommt automatisch dazu. Längste Namen werden zuerst gematcht und ihr Bereich als belegt
# markiert, damit "Kishi V3" nicht in "Kishi V3 Pro" hineingreift.
KURZ = {
    'G8 Plus': 'gamesir-g8-plus', 'G8 Galileo': 'gamesir-g8-galileo',
    'X5 Lite': 'gamesir-x5-lite', 'X2s': 'gamesir-x2s', 'X3 Pro': 'gamesir-x3-pro',
    'Kishi V3 Pro': 'razer-kishi-v3-pro', 'Kishi V3': 'razer-kishi-v3',
    'Kishi Ultra': 'razer-kishi-ultra', 'Ultimate 2C': '8bitdo-ultimate-2c',
    'Ultimate Mobile': '8bitdo-ultimate-mobile', 'Backbone Pro': 'backbone-pro',
    'FunCooler 6': 'black-shark-funcooler', 'Black Shark FunCooler': 'black-shark-funcooler',
    'FunCooler': 'black-shark-funcooler', 'Phone Cooler Chroma': 'razer-phone-cooler',
    'Scuf Nomad': 'scuf-nomad', 'M4 Snap-On': 'abxylute-m4-snapon',
    'ROG Tessen': 'asus-rog-tessen', 'MGPXPRO': 'marsgaming-mgpxpro',
    'MGPX': 'marsgaming-mgpx', 'MGP-BT2': 'marsgaming-mgp-bt2', 'M15': 'easysmx-m15',
    'AK77': 'ozkak-trigger-set', 'abxylute S8': 'abxylute-s8',
    # products.json schreibt "Backbone One – PlayStation Edition" mit Halbgeviertstrich,
    # die Seiten schreiben es ohne. Ohne diesen Alias greift das Audit dort nicht.
    'Backbone One PlayStation Edition': 'backbone-one-ps',
    'PlayStation Edition': 'backbone-one-ps',
    'Backbone One (2. Gen)': 'backbone-one-2', 'Backbone One 2. Gen': 'backbone-one-2',
    'One der 2. Generation': 'backbone-one-2',
    # Kurzformen aus dem Fliesstext, sonst loest ein Quervergleich nicht auf
    'Ozkak 4-Trigger': 'ozkak-trigger-l1r1', 'Ozkak Mobile Controller 4-Trigger': 'ozkak-trigger-l1r1',
    'Ozkak L1R1-Aufsatz': 'ozkak-mini-portable',
    'Ouligay-30er-Pack': 'ouligay-sleeves', 'Ouligay': 'ouligay-sleeves',
    'RISOKA-Set': 'risoka-finger-sleeves', 'RXKFIGX-Pack': 'rxkfigx-sleeves',
}
ALIAS = dict(KURZ)
for p in items:
    # Leere oder zu kurze Namen bleiben draussen. Ein einziges Produkt mit `"name": ""`
    # hat diesen Lauf nicht abbrechen, sondern HAENGEN lassen: re.escape('') trifft an
    # jeder Zeichenposition jeder Seite, und der Belegt-Scan darunter wird dadurch
    # quadratisch. verify.py rief dieses Script ohne timeout auf, erkannte das leere Feld
    # korrekt als Fehler -- und gab die Meldung nie aus, weil der Lauf nicht endete.
    # Das ist eine Stufe schlimmer als ein Abbruch: kein Exit-Code, kein Befund, nichts.
    for _n in (str(p.get('name') or ''), f"{p.get('brand') or ''} {p.get('name') or ''}"):
        if len(_n.strip()) > 2:
            ALIAS.setdefault(_n.strip(), p['slug'])
# "Backbone One" ist mehrdeutig (2. Gen und PlayStation Edition) und bleibt deshalb draußen:
# beide Varianten tragen unterschiedliche Preise, eine Zuordnung über den Kurznamen wäre geraten.
for mehrdeutig in ('Backbone One', 'Bluetooth Controller (weiß)'):
    ALIAS.pop(mehrdeutig, None)
NAMEN = sorted(ALIAS, key=len, reverse=True)
# ALLE_PREISE stand hier als Freigabeliste aller im Sortiment vorkommenden Preise und
# hat vier Pruefrunden lang einen falschen Preis gedeckt (46 statt 53 EUR auf der
# X2s-Seite). Sie ist in Runde 5 aus der Logik entfernt worden, die Definition blieb
# stehen — und verify.py beschreibt die Loeschung seitdem als erfolgt. Jetzt ist sie weg.

# Anhängende Konstruktionen. Alles davor ist der Produktname, die Gruppe der Wert.
# \s*(?:</a>)? faengt "…G8 Plus</a> für 76 Euro" mit ab.
# Der Lookahead am Ende schliesst Differenzen aus: "kostet 64 Euro mehr" nennt nicht den
# Preis, sondern den Abstand zu einem anderen Produkt. Ohne ihn meldet das Audit korrekte
# Vergleichssaetze als Fehler und wird als "kennt nur Fehlalarme" abgeschaltet.
_DIFF = r'(?!\s*(?:mehr|weniger|günstiger|teurer|Unterschied|Aufpreis|Ersparnis|billiger))'

# Zwischen Name und Wert dürfen ein paar Füllwörter stehen ("G8 Plus bietet für 76 Euro",
# "Phone Cooler kühlt kräftig, steht bei 3,3 von 5 Sternen"). Die Lücke darf aber weder eine
# Ziffer noch ein Euro-Zeichen enthalten und nicht über einen Satz hinausreichen, sonst
# springt das Muster auf den Preis des NÄCHSTEN Produkts. Dass ein zweiter Produktname in
# der Lücke steht, prüft lueckt_ok() zusätzlich.
_LUECKE = r'(?P<l>(?:[^!?€\d.]|\.(?!\s*[A-ZÄÖÜ])){0,45}?)'

def muster_preis():
    return re.compile(
        _LUECKE + r'(?:'
        r'\((?:ca\.\s*|ab\s*|rund\s*|nur\s*)?(?P<a>\d+(?:[.,]\d+)?)\s*(?:€|Euro)'
        r'|(?:für|kostet|kosten|liegt bei|liegen bei|mit|ab|zu)\s+'
        r'(?:ca\.\s*|rund\s*|nur\s*|etwa\s*)?(?P<b>\d+(?:[.,]\d+)?)\s*(?:€|Euro)'
        r')' + _DIFF)


def muster_sterne():
    # Für Sterne ist die Lücke bewusst weiter: Zwischen Name und Bewertung steht oft der
    # (korrekte) Preis, "Phone Cooler Chroma (70 Euro) … steht bei 3,3 von 5 Sternen".
    # Eine ziffernfreie Lücke wie beim Preis würde diese Stellen gar nicht erreichen.
    return re.compile(
        r'(?P<l>(?:[^!?.]|\.(?!\s*[A-ZÄÖÜ])){0,130}?)(?:'
        r'\((?P<a>\d[.,]\d)\s*(?:von 5\s*)?Stern'
        r'|(?:mit|bei|auf|steht bei|kommt auf|von)\s+(?P<b>\d[.,]\d)\s*(?:von 5\s*)?Stern'
        r')')


# "… bis 88 Euro (Razer Kishi V3)" und "… für rund 30 Euro liegt mit dem Ultimate 2C":
# der Wert steht VOR dem Namen. Rückwärts geprüft, weil die Vorwärts-Muster diese Bauform
# strukturell nicht sehen können. Die zweite Variante (ohne Klammer) verlangt ein
# Bindewort, sonst greift sie in beliebige Aufzählungen.
P_DAVOR = re.compile(
    r'(?P<v>\d+(?:[.,]\d+)?)\s*(?:€|Euro)\s*(?:'
    r'\((?:der |die |das )?'
    r'|(?:liegt|liegen|bekommst du|bekommt man|gibt es|startet)\s+(?:\w+\s+){0,3}?'
    r'(?:mit\s+)?(?:dem|den|der|das)\s+(?:[A-ZÄÖÜ0-9][\w\d.-]*\s+){0,2}'
    r')$')

# "4,4 Sterne aus 3.147 Bewertungen": die Anzahl ist ein eigenes Signal und war bis
# 30.09. berechnet, aber nie verglichen. Näherungen sind zulässig, wenn die Richtung
# stimmt: "über 2.100" bei 2.188 ist wahr, "über 2.400" wäre es nicht.
P_ANZAHL = re.compile(
    r'(?P<l>(?:[^!?.]|\.(?!\s*[A-ZÄÖÜ])){0,130}?)'
    r'(?P<ca>über|mehr als|fast|knapp|rund|etwa|circa|ca\.)?\s*'
    r'(?P<v>\d[\d.]{1,7})\s*(?:Amazon-)?(?:Bewertungen|Rezensionen|Kundenbewertungen|Stimmen|Käufer)')


def anzahl_ok(ist, ca, soll):
    """Zulässig: exakt, oder eine Näherung, deren Richtung gegen den Istwert trägt."""
    if ist == soll:
        return True
    if ca in ('über', 'mehr als'):
        return ist < soll
    if ca in ('fast', 'knapp'):
        return ist > soll
    if ca in ('rund', 'etwa', 'circa', 'ca.'):
        return abs(ist - soll) <= max(5, soll * 0.05)
    return False

P_PREIS, P_STERNE = muster_preis(), muster_sterne()


def luecke_ok(m):
    """False, sobald in der Lücke ein anderer Produktname steht: dann gehört der Wert dorthin."""
    l = m.group('l') or ''
    return not any(n in l for n in NAMEN)


# Auch die GENERIERTEN Seiten laufen hier durch. verify.py 6c beweist nur
# "Datei == Generator", niemals "Generator == products.json" — ein veralteter Wert in
# gen_content.py erzeugt nach einem Regen eine Seite, die zu ihrem Generator passt und
# trotzdem falsch ist. Genau diese Ebene blieb in der Runde davor offen. Über den
# gerenderten Text geprüft, schließt sich die Kette: products.json → Generator → Datei.
#
# Zusätzlich zu den HTML-Seiten werden Textquellen gelesen, die Produktwerte tragen:
# llms.txt (die GEO-Datei für KI-Crawler) und longtail.json (Quelle der zehn verwaisten
# Datenblätter, ein zweiter Generator mit demselben Veraltungsrisiko).
# scripts/gen_hubs.py traegt Produktwerte als Literal im HUBS-Dict: Ein veralteter Wert
# dort faellt nie durch einen Regen auf, deshalb steht die Datei hier.
# (Der frueher an dieser Stelle genannte Grund "nicht idempotent" gilt seit dem
# Marker-Umbau vom 30.09. nicht mehr — zwei Laeufe liefern denselben Hash. Eine behobene
# Schwaeche weiter zu behaupten schickt den naechsten Durchgang auf die falsche Faehrte.)
# Dritte Generator-Quelle nach gen_content.py und longtail.json.
# assets/js/*.js war die siebte ungeprüfte Quelle: Kein Gate las sie, obwohl main.js
# den Footer in 109 Seiten injiziert und dort eine Empfehlungsschwelle behauptet hat,
# die der eigenen (3,8) widersprach.
import glob as _glob
# ALLE Generatoren, nicht nur zwei: gen_longtail.py, gen_brand_sections.py und
# gen_pages.py koennen ebenso Produktwerte als Literal tragen und wurden von keinem
# Prosa-Gate gelesen.
TEXTQUELLEN = (['llms.txt', 'assets/data/longtail.json']
               + sorted(_glob.glob('scripts/gen_*.py'))
               + sorted(_glob.glob('assets/js/*.js')))


def seiten():
    for f in sorted(glob.glob('**/index.html', recursive=True)):
        if f.startswith('ratgeber/') or f.startswith('marken/razer-kishi/'):
            continue          # Redirect-Stubs ohne Inhalt
        yield f
    for f in TEXTQUELLEN:
        if os.path.exists(f):
            yield f


def attribut_text(text):
    """Zieht die Werte aus content/alt/title/aria-label in den Prüftext.

    maskiere_tags() ersetzt Tags samt Attributinhalt durch Leerzeichen — damit war der
    Text in `meta description`, `og:description`, `alt` und `title` für jede Prüfung
    unsichtbar, obwohl der Docstring dieses Skripts Meta-Descriptions ausdrücklich als
    Ziel nennt. Die Attributwerte werden deshalb ZUSÄTZLICH als eigener Textblock
    angehängt, positionsunabhängig: Für die Zeilennummer genügt die Fundstelle des Tags.
    """
    stuecke = []
    for m in re.finditer(r'''(?:content|alt|title|aria-label|data-note)\s*=\s*("([^"]{3,})"|'([^']{3,})')''', text):
        stuecke.append(m.group(2) or m.group(3))
    return '\n'.join(stuecke)


def maskiere_tags(text):
    """Ersetzt HTML-Tags durch gleich viele Leerzeichen.

    Die Lückenregeln verboten '<' und '>', weil ein Tag den Bezug zum Produktnamen
    brechen sollte. Das tut es aber nicht: "Der G8 Galileo kostet <strong>92 €</strong>"
    ist ein einziger Satz, und die Fettung ist die naheliegendste Redaktionsform für
    einen Preis. Die Folge war eine Prüfung, die jeder ausgezeichnete Preis aushebelt.
    Zeilenumbrüche innerhalb eines Tags bleiben erhalten, damit Zeilennummern stimmen.
    """
    return re.sub(r'<[^>]*>', lambda m: ''.join(c if c == '\n' else ' ' for c in m.group(0)), text)


def maskiere_urls(text):
    """Ersetzt URLs zeichenweise durch '_', damit Offsets und Zeilennummern stimmen.

    Die Luecken-Regeln verbieten '.', '<' und '>', weil ein Satzende oder ein Tag den
    Bezug zum Produktnamen bricht. In einer URL stehen diese Zeichen aber ohne
    inhaltliche Bedeutung. Ohne Maskierung war jede Zeile in llms.txt (Markdown mit
    vollen Links) unpruefbar - dort standen drei der acht Blocker.
    """
    return re.sub(r'https?://[^\s)"\'<>]+', '_', text)


def pruefe():
    befunde = []
    for f in seiten():
        _roh = open(f, encoding='utf-8').read()
        # Attributwerte hinten anhaengen, damit Metas und alt-Texte mitgeprueft werden.
        _rumpf = maskiere_tags(maskiere_urls(_roh))
        _grenze = len(_rumpf) + 1
        h = _rumpf + '\n' + maskiere_urls(attribut_text(_roh))
        belegt = []
        for n in NAMEN:
            for m in re.finditer(re.escape(n), h):
                if any(a <= m.start() < b for a, b in belegt):
                    continue
                belegt.append((m.start(), m.end()))
                p = bySlug[ALIAS[n]]
                rest = h[m.end():]
                zeile = (h[:m.start()].count('\n') + 1 if m.start() < _grenze
                         else 'Attributwert (content/alt/title)')
                ctx = lambda: re.sub(r'\s+', ' ', h[max(0, m.start() - 70):m.end() + 130])
                pm = P_PREIS.match(rest)
                if pm and luecke_ok(pm):
                    ist = int(float((pm.group('a') or pm.group('b')).replace(',', '.')))
                    soll = preis(p)
                    if soll and ist != soll:
                        befunde.append((f, zeile, n, f'{ist} € statt {soll} €', ctx()))
                dm = P_DAVOR.search(h[max(0, m.start() - 60):m.start()])
                if dm:
                    ist = int(float(dm.group('v').replace(',', '.')))
                    soll = preis(p)
                    if soll and ist != soll:
                        befunde.append((f, zeile, n, f'{ist} € statt {soll} € (Wert vor dem Namen)', ctx()))
                sm = P_STERNE.match(rest)
                if sm and luecke_ok(sm):
                    ist = sm.group('a') or sm.group('b')
                    soll = bewertung(p)[0]
                    if soll and ist != soll and ist.replace('.', ',') not in AGG_STERNE:
                        befunde.append((f, zeile, n, f'{ist} statt {soll} Sterne', ctx()))
                am = P_ANZAHL.match(rest)
                if am and luecke_ok(am):
                    soll = bewertung(p)[1]
                    ist = int(am.group('v').replace('.', ''))
                    if soll and ist not in AGG_ANZAHLEN and not anzahl_ok(ist, am.group('ca'), soll):
                        befunde.append((f, zeile, n,
                                        f"{am.group('ca') or ''} {am.group('v')} statt "
                                        f"{soll} Bewertungen".strip(), ctx()))
    return befunde


def produkte_im_kontext(f, h):
    """Alle Produkte, auf die sich eine Seite beziehen kann."""
    slugs = {s for s in re.findall(r'data-product="([^"]+)"', h) if s in bySlug}
    for p in items:
        d = (p.get('detail') or '').strip()
        if d and (f'href="{d}"' in h or f.startswith(d.lstrip('/'))):
            slugs.add(p['slug'])
    for n in NAMEN:
        if n and n in h:
            slugs.add(ALIAS[n])
    return [bySlug[s] for s in slugs]


MARKEN = {p['brand'] for p in items}

# Marken-Summen und gewichtete Marken-Schnitte gehoeren zu keinem einzelnen Produkt,
# stehen aber voellig zu Recht im Text ("GameSir kommt auf 3.625 Bewertungen"). Sie
# muessen in JEDER Pruefrunde erlaubt sein, nicht nur in der seitenbezogenen: Seit die
# Luecke zwischen Name und Wert 130 Zeichen umfasst, bindet die namensverankerte Runde
# sonst eine Markensumme an den zufaellig davorstehenden Produktnamen.
AGG_STERNE, AGG_ANZAHLEN = {'5,0'}, set()
for _marke in MARKEN:
    _mp = [p for p in items if p.get('brand') == _marke and bewertung(p)[0]]
    for _teil in (_mp, [p for p in _mp if p.get('type') == 'controller']):
        if not _teil:
            continue
        _su = sum(bewertung(p)[1] for p in _teil)
        AGG_ANZAHLEN.add(_su)
        AGG_STERNE.add(f"{sum(float(bewertung(p)[0].replace(',', '.')) * bewertung(p)[1] for p in _teil) / _su:.2f}"
                       .replace('.', ','))


def naechstes_produkt(text, start):
    """Das Produkt, dessen Name am dichtesten VOR der Fundstelle steht (max. 140 Zeichen).

    Auf Seiten ohne eigenes Produkt ist das der einzige belastbare Bezug. Ohne diese
    Einschraenkung meldet die Pruefung allgemeine Saetze ("ein No-Name-Controller mit
    3,5 Sternen") als Fehler, obwohl sie ueber gar kein Produkt im Sortiment sprechen.
    """
    fenster = text[max(0, start - 140):start]
    bester, pos = None, -1
    for n in NAMEN:
        i = fenster.rfind(n)
        if i > pos:
            bester, pos = ALIAS[n], i
    return bySlug.get(bester) if bester else None


def fremdbezug(text, start, ende, eigen):
    """True, wenn in der Umgebung ein anderes Produkt oder eine andere Marke steht.

    Quervergleiche sind auf jeder Seite legitim ("Der Ozkak hat mit 687 Bewertungen die
    groessere Erfahrungsbasis"). Ohne diese Ausnahme meldet die enge Seitenpruefung sie
    als Fehler und wird damit unbrauchbar.

    Bewusst NUR Produktnamen, keine Marken: "Razer", "GameSir", "Backbone" und "8BitDo"
    stehen auf fast jeder Seite, damit war die Ausnahme praktisch immer erfuellt und die
    Pruefung faktisch abgeschaltet.
    """
    umfeld = text[max(0, start - 170):ende + 60]
    wert = text[start:ende]
    for n in NAMEN:
        if n not in umfeld or (eigen is not None and ALIAS[n] == eigen['slug']):
            continue
        fremd = bySlug[ALIAS[n]]
        # Nur überspringen, wenn der Wert dem genannten Fremdprodukt WIRKLICH gehört.
        # Die alte Fassung sprang schon, sobald irgendein fremder Name im Fenster stand,
        # und übersprang damit 42 von 286 Wertstellen (14 %) — genau die Bauform, die
        # pros/cons in gen_content.py benutzen ("3,4 Sterne, der Backbone Pro bei 4,4").
        s_soll, a_soll = bewertung(fremd)
        if s_soll and re.search(r'(?<![\d,.])' + re.escape(s_soll.replace(',', '[.,]')), wert):
            return True
        if s_soll and wert.replace('.', ',').startswith(s_soll):
            return True
        if a_soll and wert.replace('.', '').strip().startswith(str(a_soll)):
            return True
    return False


def pruefe_seitenwerte():
    """Sterne und Bewertungszahlen seitenweit gegen die Produkte im Kontext.

    Auf der eigenen Produktseite steht der Wert ohne Produktnamen ("4,4 Sterne bei 3.147
    Bewertungen: Bestseller") - der Bezug ergibt sich aus der Seite. Jede namensverankerte
    Pruefung ist dort blind, und genau dort sass die Fehlerklasse dieser Runde: Ein
    veralteter Wert in gen_content.py erzeugt nach dem Regen eine Seite, die zu ihrem
    Generator passt und trotzdem falsch ist.

    Bewusst nur Sterne und Anzahlen: Preise stehen haeufig in Spannen und Schwellen
    ("unter 50 EUR", "zwischen 75 und 90 EUR"), die zu keinem Produkt gehoeren muessen.
    Bewertungswerte sind dagegen immer produktgebunden.
    """
    # Absichtlich REPOWEIT statt seitenbezogen: Eine seitenbezogene Menge meldete 17
    # Fehlalarme (Marken-Summen wie "3.625 Bewertungen über fünf Geräte" und
    # Quervergleiche in FAQs). Die Fehlerklasse, um die es geht, ist ein Wert, der zu
    # GAR KEINEM Produkt gehört - 125 Bewertungen, 2.835 Bewertungen. Den fängt die
    # weite Menge genauso, ohne einen einzigen Fehlalarm. Werte, die faelschlich zu
    # einem ANDEREN Produkt passen, deckt die namensverankerte Prüfung ab, und auf den
    # Vergleichsseiten prüft pruefe_vergleiche zusätzlich seitengenau.
    global_sterne, global_anzahlen = AGG_STERNE, AGG_ANZAHLEN
    befunde = []
    for f in seiten():
        # Die Sammelquellen (gen_content.py, gen_hubs.py, longtail.json, llms.txt) halten
        # den Text ALLER Produkte in einer Datei. "Seitenbezogen" ergibt dort keinen Sinn:
        # Jeder Wert gehoert zu irgendeinem Produkt der Datei. Ihre Werte prueft die
        # namensverankerte Runde, und ihr gerendertes Ergebnis wird hier seitenbezogen
        # geprueft - genau dort faellt ein veralteter Sternwert auf.
        if f in TEXTQUELLEN:
            continue
        roh = open(f, encoding='utf-8').read()
        eigen = next((p for p in items
                      if (p.get('detail') or '').strip()
                      and f.startswith((p['detail']).lstrip('/'))), None)
        # SEITENBEZOGEN statt repoweit. Die weite Menge liess jeden Wert durch, der zu
        # IRGENDEINEM Produkt gehoert - und weil im Sortiment fast jeder Sternwert
        # zwischen 3,3 und 4,6 vorkommt, war ein falscher Sternwert praktisch unsichtbar.
        # Genau daran ist der Rot-Test "veraltete Sterne in gen_content.py" gescheitert.
        ps = produkte_im_kontext(f, roh)
        if not ps:
            continue
        if eigen:
            # Auf der eigenen Produktseite ist der Bezug eindeutig: eng pruefen.
            sterne = {bewertung(eigen)[0]} | global_sterne
            anzahlen = {bewertung(eigen)[1]} | global_anzahlen
        else:
            sterne = {bewertung(p)[0] for p in ps if bewertung(p)[0]} | global_sterne
            anzahlen = {bewertung(p)[1] for p in ps if bewertung(p)[1]} | global_anzahlen
        text = re.sub(r'<[^>]+>', ' ', roh) + '\n' + attribut_text(roh)
        # Auch die nackte Klammerform "Bewertung (3,8)" zaehlt: Sie stand vier Prüfrunden
        # lang falsch auf der X2s-Seite, weil jedes Muster das Wort "Stern" verlangte.
        for m in re.finditer(r'(?:Bewertung|Rating)\s*\((\d[.,]\d)\)'
                             r'|(\d[.,]\d)\s*(?:von\s*5(?!\d)|/\s*5(?!\d)|\s*Stern)', text):
            _vs = text[max(0, m.start() - 20):m.start()]
            if re.search(r'\b(?:unter|über|ab|mindestens|weniger als|mehr als)\s*$', _vs, re.I):
                continue
            _wert = (m.group(1) or m.group(2)).replace('.', ',')
            if eigen is None:
                _np = naechstes_produkt(text, m.start())
                if _np is None or _wert == bewertung(_np)[0] or _wert in global_sterne:
                    continue
            elif fremdbezug(text, m.start(), m.end(), eigen):
                continue
            if _wert not in sterne:
                befunde.append((f, roh[:roh.find(m.group(0))].count('\n') + 1, 'Seitenwert',
                                f'{_wert} Sterne gehört zu keinem Produkt im Sortiment',
                                re.sub(r'\s+', ' ', text[max(0, m.start() - 95):m.end() + 55])))
        for m in re.finditer(r'(?<![\d.,])(\d[\d.]{1,7})\s*(?:Amazon-)?(?:Bewertungen|Rezensionen|Kundenbewertungen|Stimmen|Käufer)', text):
            w = int(m.group(1).replace('.', ''))
            if w in anzahlen:
                continue
            if eigen is None:
                _np = naechstes_produkt(text, m.start())
                if _np is None or w == bewertung(_np)[1] or w in global_anzahlen:
                    continue
            elif fremdbezug(text, m.start(), m.end(), eigen):
                continue
            vor = text[max(0, m.start() - 26):m.start()]
            # "weniger als 100 Bewertungen meiden wir" ist eine Schwelle, kein Produktwert.
            if re.search(r'\b(?:weniger als|unter|mindestens|ab|höchstens|maximal)\s*$', vor, re.I):
                continue
            if re.search(r'(?:über|mehr als|fast|knapp|rund|etwa|circa|ca\.)\s*$', vor) \
                    and any(anzahl_ok(w, k, a) for a in anzahlen
                            for k in ('über', 'fast', 'rund')):
                continue
            befunde.append((f, roh[:roh.find(m.group(0))].count('\n') + 1, 'Seitenwert',
                            f'{m.group(1)} Bewertungen gehört zu keinem Produkt im Sortiment',
                            re.sub(r'\s+', ' ', text[max(0, m.start() - 95):m.end() + 55])))
    return befunde


# Schwellen ("unter 50 €", "ab 80 €") und Spannen ("1–3 €", "zwischen 75 und 90 €")
# beziffern keinen Produktpreis. Sie stehen überall in Kaufberatung und Seitentiteln und
# waren die einzige Quelle von Fehlalarmen der Preisprüfung.
# Wortgrenze zwingend: Ohne \b traf "und" das Ende von "r-und", und damit galt JEDER
# Preis der Form "rund 40 €" als Schwelle. 101 Stellen im Repo waren so stumm
# ausgenommen, darunter 19 in gen_content.py. Ein fehlendes \b hat die Preisprüfung
# auf genau den Seiten abgeschaltet, für die sie gebaut wurde.
# re.I, weil dieselben Woerter am Satzanfang grossgeschrieben stehen: "Über 100 €" ist in
# controller/beste/ eine Preisband-Ueberschrift und kein Produktpreis. Ohne re.I haette das
# Audit dort einen Produktpreis erwartet. Geprueft: im ganzen Repo trifft das genau diese
# eine Stelle, und die ist tatsaechlich eine Schwelle.
# "und" nur noch als zweite Haelfte einer Spanne ("zwischen 30 und 100 Euro"). Allein
# stehend war es die breiteste Ausnahme der Liste: jeder Preis, dem irgendein "und"
# vorangeht, waere prueffrei gewesen. Im Repo steht es 6x, jedes Mal hinter "zwischen".
_SCHWELLE = re.compile(r'(?:\bzwischen\b[^.!?]{0,40}\bund'
                       r'|\b(?:ab|unter|über|ueber|bis|zwischen|maximal|höchstens'
                       r'|mindestens|budget|klasse))\s*(?:€\s*)?$', re.I)
_SPANNE = re.compile(r'[–—-]\s*$')


# Abo-, Versand- und Fremdpreise sind keine Produktpreise:
# "Backbone+ (ca. 3 €/Monat)", "Dazu kommen 5 € Versand", "Ein DualSense Edge kostet 200 €".
# Ohne diese Ausnahmen meldet das Audit korrekten Text rot, und ein Gate, das bei
# richtigem Text anschlaegt, wird abgeschaltet.
_ABO = re.compile(r'^\s*(?:€|Euro)?\s*(?:/|pro |im )\s*(?:Monat|Jahr|Woche)|^\s*(?:€|Euro)?\s*Versand')
_FREMD = re.compile(r'DualSense|DualShock|Xbox|Switch Pro|Steam Deck|PlayStation Portal'
                    r'|Joy-Con|Stadia|Backbone\+|Versandkosten', re.I)


_DIFFWORT = re.compile(r'^\s*(?:€|Euro)?\s*(?:mehr|weniger|günstiger|teurer|billiger'
                       r'|Aufschlag|Aufpreis|Ersparnis|Unterschied|Differenz'
                       r'|unter dem|über dem|unter den|über den)')


def kein_produktpreis(text, start, ende=None):
    vor = text[max(0, start - 18):start]
    if ende is not None and _DIFFWORT.match(text[ende:ende + 18]):
        return True
    if _SCHWELLE.search(vor) or _SPANNE.search(vor):
        return True
    if _FREMD.search(text[max(0, start - 75):start]):
        return True
    return bool(ende is not None and _ABO.match(text[ende:ende + 16]))


def verwaiste_detailseiten():
    """Seiten unter /produkte/, zu denen es keinen products.json-Eintrag gibt.

    Zehn Longtail-Datenblaetter zu ausgelaufenen Modellen. Sie haben keinen eigenen
    Preis, verweisen aber auf kaufbare Alternativen - und fielen aus jeder
    Preispruefung heraus, weil diese ueber products.json iteriert.
    """
    bekannt = {(p.get('detail') or '').lstrip('/') + 'index.html' for p in items}
    return [f for f in sorted(glob.glob('produkte/*/index.html')) if f not in bekannt]


def pruefe_detailpreise():
    """Preise auf der eigenen Produktseite gegen das Produkt dieser Seite.

    Im Urteilstext steht der Preis ohne Produktnamen ("Starker Allrounder für 46 €"),
    und er ist weit genug vom Namen entfernt, dass keine Anbindungsregel ihn erreicht.
    Auf einer Produktseite ist der Bezug aber eindeutig. Erlaubt sind der eigene Preis,
    die Preise der auf der Seite genannten oder verlinkten Produkte sowie Differenzen
    und Summen daraus. Spannen und Schwellen ("ab 80 €", "unter 50 €") werden
    übersprungen, weil sie zu keinem einzelnen Produkt gehören müssen.
    """
    befunde = []
    ziele = [((p.get('detail') or '').lstrip('/') + 'index.html', p)
             for p in items if (p.get('detail') or '').strip()]
    ziele += [(f, None) for f in verwaiste_detailseiten()]
    for f, p in ziele:
        if not os.path.exists(f):
            continue
        roh = open(f, encoding='utf-8').read()
        kontext = produkte_im_kontext(f, roh)
        # Geschwister derselben Marke gehoeren zum Kontext: Eine Produktseite verweist
        # regelmaessig auf ihre Farb- und Ausstattungsvarianten, ohne deren vollen Namen
        # zu nennen ("die schwarze und weiße Variante desselben Modells, je ca. 40 €").
        # Geschwisterpreise sind NICHT pauschal erlaubt. "gleiche Marke + gleicher Typ"
        # gab 62 zusaetzliche Werte frei und machte Saetze wie "Mit 80 Euro ist er der
        # teuerste GameSir" auf der 53-Euro-Seite unsichtbar - vier GameSir-Produktlinien
        # galten wechselseitig als Varianten. Erlaubt sind sie nur dort, wo der Satz
        # ausdruecklich von einer Variante spricht; genau dafuer existiert die Regel
        # ("die schwarze und weiße Variante desselben Modells, je ca. 40 €").
        geschwister = ([x for x in items
                        if x.get('brand') == p.get('brand') and x.get('type') == p.get('type')
                        and x not in kontext] if p else [])
        preise = {preis(x) for x in kontext if preis(x)} | ({preis(p)} if p else set())
        preise.discard(None)
        varianten_preise = {preis(x) for x in geschwister if preis(x)}
        erlaubt = set(preise)
        for a in preise:
            for b in preise:
                erlaubt |= {abs(a - b), a + b}
        # Empfehlungskacheln ausblenden: Ihre Preise prueft sync_product_values
        # strukturell ueber den href-Slug, im Fliesstext stehen sie ohne Satzbezug.
        ohne_kacheln = re.sub(r'<div class="(?:rc-price|cat-count)">[^<]*</div>', ' ', roh)
        text = re.sub(r'<[^>]+>', ' ', ohne_kacheln) + '\n' + attribut_text(roh)
        for m in re.finditer(r'(?<![\d,.])(\d{1,4})\s*(?:€|Euro\b)', text):
            w = int(m.group(1))
            if kein_produktpreis(text, m.start(), m.end()):
                continue
            # Variantenhinweis im Satz? Dann zaehlen auch die Geschwisterpreise.
            # Muss VOR der Bezugspruefung stehen: "die schwarze und weiße Variante
            # desselben Modells (je ca. 40 €)" nennt bewusst keinen Produktnamen.
            if w in varianten_preise and re.search(
                    r'Variante|Farbe|Ausführung|Version|Schwestermodell|Farbvariante',
                    text[max(0, m.start() - 130):m.end() + 70], re.I):
                continue
            # Steht kein Produktname davor, gehoert der Preis dem Produkt DIESER Seite.
            # Die Menge aller auf der Seite genannten Produkte reicht als Freigabe nicht:
            # "Mit 80 Euro ist er der teuerste GameSir" blieb gruen, weil der G8 Galileo
            # weiter oben korrekt mit 80 € steht. Der Bezug ist aber dieser Satz.
            _folgend = None
            _fen = text[m.end():m.end() + 60]
            for _n in NAMEN:
                if _n and _n in _fen:
                    _folgend = bySlug[ALIAS[_n]]
                    break
            if _folgend is not None and w == preis(_folgend):
                continue
            if p and naechstes_produkt(text, m.start()) is None and _folgend is None:
                if w != preis(p):
                    befunde.append((f, roh[:roh.find(m.group(0))].count('\n') + 1, p['slug'],
                                    f'{w} € ohne Produktbezug auf der Seite von {p["slug"]} '
                                    f'({p["price"]})',
                                    re.sub(r'\s+', ' ', text[max(0, m.start() - 95):m.end() + 55])))
                continue
            if w in erlaubt:
                continue
            befunde.append((f, roh[:roh.find(m.group(0))].count('\n') + 1,
                            p['slug'] if p else 'verwaist',
                            f'{w} € gehört zu keinem Produkt im Kontext dieser Seite',
                            re.sub(r'\s+', ' ', text[max(0, m.start() - 95):m.end() + 55])))
    return befunde


def pruefe_vergleiche():
    """Vergleichsseiten: jeder Wert muss zu einem der verglichenen Produkte gehören.

    Auf diesen Seiten steht der Produktname im <h2> und der Wert im <p> darunter. Keine
    namensverankerte Prüfung kann das sehen — genau so überlebte auf
    vergleich/g8-plus-vs-kishi-v3-pro ein kompletter Vor-Abgleich-Absatz (4,4 Sterne,
    125 Bewertungen, 149 €, 59 € Aufpreis), während dieselbe Seite an vier anderen
    Stellen die richtigen Werte trug.

    Deshalb hier seitenweit: Erlaubt sind die Werte der Produkte auf der Seite sowie
    Differenzen und Summen ihrer Preise. Alles andere wird gemeldet.
    """
    befunde = []
    for f in sorted(glob.glob('vergleich/*/index.html')):
        h = open(f, encoding='utf-8').read()
        # Produkte der Seite aus DREI Quellen: data-product (steht auf Duell-Seiten nur
        # beim Sieger), verlinkte detail-URLs, und die Namen in der Vergleichstabelle.
        # Nur data-product zu nehmen hiess: genau die Duell-Seiten, für die diese Prüfung
        # gebaut ist, wurden stumm übersprungen.
        slugs = {s for s in re.findall(r'data-product="([^"]+)"', h) if s in bySlug}
        for p in items:
            d = (p.get('detail') or '').strip()
            if d and f'href="{d}"' in h:
                slugs.add(p['slug'])
        kopf = re.search(r'<tr>\s*<t[hd][^>]*>Merkmal</t[hd]>(.*?)</tr>', h, re.S)
        if kopf:
            for zelle in re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', kopf.group(1), re.S):
                klar = re.sub(r'<[^>]+>', '', zelle).strip()
                for n in NAMEN:
                    if n and n in klar:
                        slugs.add(ALIAS[n]); break
        ps = [bySlug[s] for s in slugs]
        if len(ps) < 2:
            befunde.append((f, 1, 'Vergleichsseite',
                            f'nur {len(ps)} Produkt(e) auflösbar — die Wertprüfung dieser '
                            f'Seite läuft ins Leere', 'data-product, detail-Links und '
                            'Tabellenkopf ergaben kein Paar'))
            continue
        preise = {preis(p) for p in ps if preis(p)}
        erlaubt_preis = set(preise)
        for a in preise:
            for b in preise:
                erlaubt_preis |= {abs(a - b), a + b}
        sterne = {bewertung(p)[0] for p in ps if bewertung(p)[0]} | {'5,0'}
        anzahlen = {bewertung(p)[1] for p in ps if bewertung(p)[1]}
        # Marken-Aggregate und Skalenwerte gehoeren zu keinem einzelnen Produkt, stehen
        # aber voellig zu Recht auf Vergleichsseiten ("GameSir kommt auf 3.625 Bewertungen").
        for _marke in {x.get('brand') for x in items}:
            _mp = [x for x in items if x.get('brand') == _marke and bewertung(x)[0]]
            for _teil in (_mp, [x for x in _mp if x.get('type') == 'controller']):
                if _teil:
                    anzahlen.add(sum(bewertung(x)[1] for x in _teil))
        text = re.sub(r'<script type="application/ld\+json">.*?</script>', ' ', h, flags=re.S)
        text = re.sub(r'<[^>]+>', ' ', text) + '\n' + attribut_text(h)
        for m in re.finditer(r'(\d+(?:[.,]\d+)?)\s*(?:€|Euro\b)', text):
            w = int(float(m.group(1).replace(',', '.')))
            if w not in erlaubt_preis and not kein_produktpreis(text, m.start(), m.end()):
                befunde.append((f, text[:m.start()].count('\n') + 1, 'Vergleichsseite',
                                f'{w} € gehört zu keinem Produkt der Seite '
                                f'(erlaubt: {sorted(erlaubt_preis)})',
                                re.sub(r'\s+', ' ', text[max(0, m.start() - 90):m.end() + 60])))
        for m in re.finditer(r'(\d[.,]\d)\s*(?:von 5\s*)?Stern', text):
            if m.group(1) not in sterne:
                befunde.append((f, text[:m.start()].count('\n') + 1, 'Vergleichsseite',
                                f'{m.group(1)} Sterne gehört zu keinem Produkt der Seite '
                                f'(erlaubt: {sorted(sterne)})',
                                re.sub(r'\s+', ' ', text[max(0, m.start() - 90):m.end() + 60])))
        for m in re.finditer(r'(\d[\d.]{1,7})\s*(?:Amazon-)?(?:Bewertungen|Rezensionen|Kundenbewertungen|Stimmen|Käufer)', text):
            w = int(m.group(1).replace('.', ''))
            _vor = text[max(0, m.start() - 26):m.start()]
            if re.search(r'\b(?:weniger als|unter|mindestens|ab|höchstens|maximal)\s*$', _vor, re.I):
                continue
            if re.search(r'(?:über|mehr als|fast|knapp|rund|etwa|circa|ca\.)\s*$', _vor) \
                    and any(anzahl_ok(w, k, a) for a in anzahlen for k in ('über', 'fast', 'rund')):
                continue
            if w not in anzahlen:
                befunde.append((f, text[:m.start()].count('\n') + 1, 'Vergleichsseite',
                                f'{m.group(1)} Bewertungen gehört zu keinem Produkt der Seite '
                                f'(erlaubt: {sorted(anzahlen)})',
                                re.sub(r'\s+', ' ', text[max(0, m.start() - 90):m.end() + 60])))
    return befunde


if __name__ == '__main__':
    befunde = (pruefe() + pruefe_seitenwerte() + pruefe_detailpreise()
               + pruefe_vergleiche())
    for f, z, n, was, ctx in befunde:
        print(f'{f}:{z}  [{n}] {was}')
        if '--text' in sys.argv:
            print(f'      …{ctx}…')
    print(f'\n{len(befunde)} Fließtext-Abweichung(en) gegen products.json')
    sys.exit(1 if befunde else 0)
