#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Die Messvorschrift hinter "der Rueckweg haelt" (B7).

In beide Richtungen, weil ein Gate, das nur rot wird, die falsche Regel haben kann:

    jeder Defekt MUSS rot werden        (sonst geht er live)
    jedes legitime Refactoring MUSS gruen bleiben
                                        (sonst verteidigt das Gate den Fehler gegen
                                         Korrektur -- P-13 Mechanismus 6, und beim
                                         Top-N-Gate aus B6 ist genau das passiert)

Geprueft werden die drei Gates, die mit B7 entstanden sind:
  · sync_hublinks.py --check   (Rueckweg auf den handgepflegten Seiten)
  · §B7 im verify.py           (Rueckweg am AUSGELIEFERTEN Stand, beide Seitenarten)
  · Waisen-Gate                (Links von noindex-Weiterleitungen zaehlen nicht mehr)

Jeder Fall bekommt eine FRISCHE Kopie des Repos.

NICHT in dieser Batterie, und das ist ein Befund fuer sich: "Ein Produkt wechselt die
Plattform-Zugehoerigkeit" laesst sich NICHT als legitimes Refactoring pruefen. Eine
Aenderung an `worksOn` zieht handgepflegte Prosa nach -- die Kachelzahlen der Startseite
("iPhone Controller: 24 Modelle", von §A5 gegen worksOn nachgerechnet) und die
Marken-Hub-Texte, die gen_brand_sections.py prueft. Nach dem Lauf ALLER zwoelf
Generatoren bleibt der Stand rot, und zwar zu Recht. In diesem Repo ist ein
worksOn-Wechsel also nie eine reine Umsortierung, sondern immer auch eine Textaufgabe.
Der Rueckweg selbst folgt dabei korrekt (per Hand nachgemessen), nur beweist das ein
Batterie-Fall nicht, der an einem unbeteiligten Nachbarn rot wird.

Aufruf:  python3 scripts/links_batterie.py
         python3 scripts/links_batterie.py --kurz
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REVIEW = 'controller/universal/gamesir-g8-galileo-review/index.html'
DATENBLATT = 'produkte/8bitdo-ultimate-mobile/index.html'
HUB = 'marken/gamesir/index.html'
PRODUKTE = 'produkte/index.html'
HUBLINKS = 'scripts/hublinks.py'
TABLETSEITE = 'controller/universal/gamesir-g8-plus-review/index.html'
REDAKTION = 'controller/universal/gamesir-x5-lite-review/index.html'
KISHIPRO = 'controller/universal/razer-kishi-v3-pro-review/index.html'
WAISE = 'produkte/ipega-pg-9023/index.html'
BLOGSEITE = 'blog/hall-effect-erklaert/index.html'
START = 'index.html'
UEBERUNS = 'ueber-uns/index.html'
METHODE = 'redaktion/index.html'
# §A5-Verfuegbarkeit (06.10.2026) und die Black-Friday-Schwellen-Matrix.
BF = 'black-friday/index.html'
HUBRENDER = 'assets/js/hub-render.js'
PRODUKTJSON = 'assets/data/products.json'
# Ein Produkt, dessen Verfuegbarkeit NICHT 'ja' ist -- die Karte muss das sagen.
GEN_KARTE = 'produkte/index.html'
POSBLOCK = ('<!-- POSITION:START -->\n<p>Irgendwas 42 13 29 Amazon Video 1 bis 2 '
            'Minuten</p>\n<!-- POSITION:END -->\n')


def _block_weg(h):
    return re.sub(r'<!-- HUBLINKS:START -->.*?<!-- HUBLINKS:END -->\n?', '', h, flags=re.S)


def _hall_satz(h):
    """Der Satz "<Zahlwort> der <N> Controller" aus der Hall-Direktantwort.

    Stand dreimal als Literal "Fünf der 28 Controller" hier. Nachdem am 06.10.2026 sechs
    weitere Hall-Specs belegt wurden, waren es elf, die Mutationen griffen nicht mehr,
    und die Batterie meldete "Mutation hat nicht gegriffen" -- drei Faelle ohne
    Beweiswert bei unveraenderter Schlusszeile. Vierter Fall derselben Klasse an einem
    Tag.
    """
    m = re.search(r'([A-ZÄÖÜ][a-zäöüß]+) der (\d+) Controller', h)
    if not m:
        raise SystemExit('links_batterie: Hall-Direktantwort nicht gefunden -- der Satz '
                         'hat seine Form geaendert')
    return m.group(0), m.group(1), m.group(2)


def _b10_preis(h):
    """Der Preis, den der §B10-Hinweis auf dieser Seite nennt.

    Vorgeschichte: Zwei Faelle standen mit dem Literal "kostet 88 € und kommt" da.
    Beim Vollabgleich am 06.10.2026 fiel der Kishi V3 auf 78 €, die Mutation griff nicht
    mehr, und die Batterie meldete "Mutation hat nicht gegriffen" -- zwei Faelle ohne
    Beweiswert, waehrend die Schlusszeile weiter "111 Faelle" sagte. Ein Wert, der
    woanders gepflegt wird, gehoert nicht als Literal in eine Probe.
    """
    m = re.search(r'kostet (\d+) € und kommt', h)
    if not m:
        raise SystemExit('links_batterie: §B10-Hinweis auf der KISHIPRO-Seite nicht '
                         'gefunden -- der Satz hat seine Form geaendert')
    return m.group(1)


_KRITERIEN = '<h2 style="margin-top:24px">Unsere Bewertungskriterien</h2>'


def _satz(h, text):
    """Setzt einen Satz in den Fliesstext der Methodenseite, vor die Kriterien-Liste.

    Eigene Funktion, weil die All-Aussagen-Faelle sich nur im SATZ unterscheiden duerfen:
    Wer daneben auch noch die Einfuegestelle variiert, misst zwei Dinge auf einmal.
    """
    return h.replace(_KRITERIEN, f'<p>{text}</p>\n{_KRITERIEN}', 1)


FAELLE = [
    # ---- Defekte: MUESSEN rot werden -------------------------------------------------
    ('Rueckweg-Block von einer Review-Seite entfernt', REVIEW, _block_weg, 'ROT'),
    ('Rueckweg-Block von einem Datenblatt entfernt', DATENBLATT, _block_weg, 'ROT'),
    ('ein Hub-Link im Block von Hand geloescht', REVIEW,
     lambda h: h.replace('<a href="/marken/gamesir/">', '<span>', 1), 'ROT'),
    ('Hub-Link auf ein falsches Ziel umgebogen', REVIEW,
     lambda h: h.replace('href="/marken/gamesir/"', 'href="/marken/razer/"', 1), 'ROT'),
    ('Block aus <main> heraus in den Footer verschoben', REVIEW,
     lambda h: h.replace('<!-- HUBLINKS:START -->', '</main><!-- HUBLINKS:START -->', 1),
     'ROT'),
    # Der Kern des Waisen-Befunds: Ein Link von einer noindex-Weiterleitung ist kein Link.
    ('Longtail-Block von /produkte/ entfernt (Waisen entstehen)', PRODUKTE,
     lambda h: re.sub(r'<!-- LONGTAIL:START -->.*?<!-- LONGTAIL:END -->\n?', '', h,
                      flags=re.S), 'ROT'),
    ('einzige Quelle einer Seite wird zur noindex-Weiterleitung', HUB,
     lambda h: h.replace('<head>', '<head><meta name="robots" content="noindex">', 1),
     'ROT'),
    # Wenn ein Hub ein Produkt neu aufnimmt, MUSS der Rueckweg nachgezogen werden.
    ('Hub nimmt ein Produkt auf, Rueckweg fehlt', HUB,
     lambda h: h.replace('</main>',
                         '<p><a href="/controller/android/turtle-beach-atom-review/">'
                         'Turtle Beach Atom</a></p></main>', 1), 'ROT'),
    ('Taxonomie-Erkennung auf Bestenlisten ausgeweitet (Block veraltet)', HUBLINKS,
     lambda q: q.replace("'/controller/tablet/', '/controller/mini-gamepad/',",
                         "'/controller/tablet/', '/controller/mini-gamepad/',\n"
                         "    '/controller/beste/',"), 'ROT'),

    # Aus dem Pruefbericht: sechs Formen, die alle still gruen blieben.
    # NICHT auf einem Marken-Hub: den besitzt gen_brand_sections.py, und ein zusaetzlicher
    # Absatz macht dort dessen eigenes --check rot. Der Fall waere aus dem falschen Grund
    # rot geworden und haette ueber die Zuordnungsregel nichts bewiesen.
    ('Fliesstext-Erwaehnung erzeugt keine Zuordnung', 'zubehoer/trigger/index.html',
     lambda h: h.replace('</main>',
                         '<p>Wer kuehlen will, nimmt den '
                         '<a href="/produkte/magnet-peltier-cooler/">Peltier-Kuehler</a>.'
                         '</p></main>', 1), 'GRUEN'),
    ('Karte verlinkt "Mehr erfahren" auf die eigene Seite', HUB,
     lambda h: h.replace('<a href="/controller/universal/gamesir-g8-galileo-review/" '
                         'class="btn-detail">',
                         '<a href="/marken/gamesir/" class="btn-detail">', 1), 'ROT'),
    ('Hub ohne <h1>', HUB,
     lambda h: re.sub(r'<h1[^>]*>.*?</h1>', '<p class="ersatz">GameSir</p>', h, count=1,
                      flags=re.S), 'ROT'),
    # `&` und `&amp;` im h1 bedeuten dasselbe und MUESSEN dasselbe Label ergeben. Ohne
    # `html.unescape()` vor dem Escapen stand auf fuenf Seiten sichtbar "Tablet &amp;amp;
    # iPad" -- bei gruenem Lauf. Geprueft wird deshalb der TEXT, nicht nur der Exit-Code.
    ('&amp; statt & im h1 ergibt dasselbe Label', 'controller/tablet/index.html',
     lambda h: re.sub(r'(<h1[^>]*>.*?)&(?!amp;|#)(.*?</h1>)', r'\1&amp;\2', h, count=1,
                      flags=re.S), 'LABEL_GLEICH'),
    ('HTML-Kommentar nennt "<aside"', REVIEW,
     lambda h: h.replace('<!-- HUBLINKS:START -->',
                         '<!-- Reihenfolge: Inhalt, dann <aside -->\n'
                         '<!-- HUBLINKS:START -->', 1), 'GRUEN'),
    ('Hub-Prosa nennt das Wort "noindex"', 'zubehoer/trigger/index.html',
     lambda h: h.replace('</main>',
                         '<p>Altmodelle stehen bei uns auf noindex.</p></main>', 1),
     'GRUEN'),

    # --- B8: Sternzahl und Bewertungszahl sind zwei Signale -----------------------------
    ('Bewertungszahl aus dem Badge entfernt', DATENBLATT,
     lambda h: re.sub(r'<div class="rb-count">.*?</div>', '', h, count=1, flags=re.S),
     'ROT'),
    # `.rb-count` BLEIBT, bekommt aber einen Inline-Fussnoten-Stil. Die erste Fassung
    # ersetzte die Klasse und wurde deshalb ueber den Zweig "Anzahl fehlt" rot -- aus dem
    # richtigen Grund, aber nicht an dem, was das Etikett behauptet.
    ('Bewertungszahl als Inline-Fussnote gesetzt', DATENBLATT,
     lambda h: h.replace('<div class="rb-count">',
                         '<div class="rb-count" style="font-size:11px">', 1), 'ROT'),
    ('fuenf volle Sterne neben "von 10"', REDAKTION,
     lambda h: re.sub(r'(<div class="stars"[^>]*>)[^<]*(</div>)', r'\1★★★★★\2', h,
                      count=1, flags=re.S), 'ROT'),
    ('Sterne passen nicht zum Wert (Fuenfer-Skala)', DATENBLATT,
     lambda h: re.sub(r'(<div class="stars"[^>]*>)[^<]*(</div>)', r'\1★★☆☆☆\2', h,
                      count=1, flags=re.S), 'ROT'),
    ('rb-label "von 10 Punkten" plus fuenf volle Sterne', REDAKTION,
     lambda h: re.sub(r'(<div class="stars"[^>]*>)[^<]*(</div>)', r'\1★★★★★\2',
                      h.replace('<div class="rb-label">von 10</div>',
                                '<div class="rb-label">von 10 Punkten</div>', 1),
                      count=1, flags=re.S), 'ROT'),
    ('sieben Glyphen statt fuenf', REDAKTION,
     lambda h: re.sub(r'(<div class="stars"[^>]*>)[^<]*(</div>)', r'\1★★★★☆☆☆\2', h,
                      count=1, flags=re.S), 'ROT'),
    ('.stars als <span> mit zweiter Klasse, fuenf voll', REDAKTION,
     lambda h: re.sub(r'<div class="stars"([^>]*)>[^<]*</div>',
                      r'<span class="stars rb-stars"\1>★★★★★</span>', h, count=1), 'ROT'),
    ('rb-label geloescht', REDAKTION,
     lambda h: re.sub(r'<div class="rb-label">[^<]*</div>', '', h, count=1), 'ROT'),
    ('Sterne-Darstellung ganz entfernt', REDAKTION,
     lambda h: re.sub(r'<div class="stars"[^>]*>[^<]*</div>', '', h, count=1), 'ROT'),
    ('rb-count: Ziffer ohne Bezug zu Bewertungen', REDAKTION,
     lambda h: re.sub(r'<div class="rb-count">.*?</div>',
                      '<div class="rb-count">Platz 3</div>', h, count=1, flags=re.S),
     'ROT'),
    ('LEGITIM Anzahl mit <strong> hervorgehoben', REDAKTION,
     lambda h: re.sub(r'(<div class="rb-count">)(.*?)(</div>)',
                      lambda m: m.group(1) + m.group(2).replace(
                          '1.953', '<strong>1.953</strong>') + m.group(3),
                      h, count=1, flags=re.S), 'GRUEN'),
    ('LEGITIM Badge in einem HTML-Kommentar', REDAKTION,
     lambda h: h.replace('</main>', '<!-- <div class="rating-badge">'
                         '<div class="rb-num">9,9</div></div> --></main>', 1), 'GRUEN'),
    ('LEGITIM rb-label "von 10 Punkten", Sterne stimmen', REDAKTION,
     lambda h: h.replace('<div class="rb-label">von 10</div>',
                         '<div class="rb-label">von 10 Punkten</div>', 1), 'GRUEN'),
    ('rb-count ohne Zahl', DATENBLATT,
     lambda h: re.sub(r'<div class="rb-count">[^<]*</div>',
                      '<div class="rb-count">Bewertungen bei Amazon</div>', h, count=1),
     'ROT'),
    # Am GENERATOR, nicht an der Seite: Eine generierte Seite von Hand zu aendern ist
    # korrekterweise eine Divergenz (§A1). Die erste Fassung dieses Falls editierte die
    # Seite und wurde deshalb am Generator-Abgleich rot -- aus dem richtigen Grund, aber
    # nicht an dem, was das Etikett behauptet.
    ('LEGITIM Formulierung der Anzahl im Generator geaendert', 'scripts/gen_pages.py',
     lambda q: q.replace('{_bew_wort} bei Amazon', '{_bew_wort} auf Amazon.de', 1),
     'GRUEN_NACH_SYNC'),

    # --- B9: Autoritaetssignal am Entscheidungspunkt ------------------------------------
    ('Label von Hand auf "Mehr erfahren" zurueckgedreht', 'controller/ios/index.html',
     lambda h: h.replace('>Zum Kurzcheck</a>', '>Mehr erfahren</a>', 1), 'ROT'),
    ('Datenblatt-Karte behauptet "Zum Test"', 'controller/ios/index.html',
     lambda h: h.replace('>Zum Kurzcheck</a>', '>Zum Test</a>', 1), 'ROT'),
    ('JS-Fassung der Regel weicht ab', 'assets/js/finder.js',
     lambda j: j.replace("const LABEL_TEST = 'Zum Test';",
                         "const LABEL_TEST = 'Mehr erfahren';", 1), 'ROT_NACH_BUMP'),
    ('JS verdrahtet die Beschriftung wieder fest', 'assets/js/hub-render.js',
     lambda j: j.replace('${esc(detailLabel(p.detail))}', 'Mehr erfahren', 1),
     'ROT_NACH_BUMP'),
    ('main.js benennt den Knopf wieder um', 'assets/js/main.js',
     lambda j: j.replace('        card.classList.add',
                         '        if (detailLink) detailLink.textContent = "Mehr erfahren";'
                         '\n        card.classList.add', 1), 'ROT_NACH_BUMP'),
    ('Prosa-Zahl der eigenen Tests gefaelscht', 'index.html',
     lambda h: h.replace('haben 13 davon ausführlich getestet',
                         'haben 12 davon ausführlich getestet', 1), 'ROT'),
    ('LEGITIM btn-detail ausserhalb einer Karte, anderes Ziel', 'index.html',
     lambda h: h.replace('</main>', '<p><a class="btn-detail" href="/controller-finder/">'
                         'Zum Finder</a></p></main>', 1), 'GRUEN'),
    ('LEGITIM btn-detail in einem HTML-Kommentar', 'index.html',
     lambda h: h.replace('</main>', '<!-- <a class="btn-detail" '
                         'href="/produkte/gamesir-x2/">Mehr erfahren</a> --></main>', 1),
     'GRUEN'),
    ('LEGITIM main.js setzt eine ANDERE textContent', 'assets/js/main.js',
     lambda j: j.replace('        card.classList.add',
                         '        if (amazonLink) amazonLink.textContent = "Kaufen";'
                         '\n        card.classList.add', 1), 'GRUEN_NACH_BUMP'),

    # Aus dem B9-Pruefbericht: zwei Blocker und zwei blinde Flecken.
    ('main.js benennt per innerHTML um', 'assets/js/main.js',
     lambda j: j.replace('        card.classList.add',
                         '        if (detailLink) detailLink.innerHTML = "Mehr erfahren";'
                         '\n        card.classList.add', 1), 'ROT_NACH_BUMP'),
    ('main.js benennt ueber einen anderen Variablennamen um', 'assets/js/main.js',
     lambda j: j.replace('const detailLink = card.querySelector',
                         'const dl = card.querySelector', 1).replace('detailLink', 'dl')
     .replace('        card.classList.add',
              '        if (dl) dl.textContent = "Mehr erfahren";'
              '\n        card.classList.add', 1), 'ROT_NACH_BUMP'),
    ('falsches Label auf 404.html', '404.html',
     lambda h: h.replace('</main>', '<a class="btn-detail" '
                         'href="/produkte/gamesir-x2/">Zum Test</a></main>', 1), 'ROT'),
    ('LEGITIM richtiges Label auf 404.html', '404.html',
     lambda h: h.replace('</main>', '<a class="btn-detail" '
                         'href="/produkte/gamesir-x2/">Zum Kurzcheck</a></main>', 1),
     'GRUEN'),
    ('LEGITIM falsches Label auf einem Redirect-Stub', 'ratgeber/index.html',
     lambda h: h.replace('</body>', '<a class="btn-detail" '
                         'href="/produkte/gamesir-x2/">Zum Test</a></body>', 1), 'GRUEN'),

    # --- B10: die Zahl, die gegen den eigenen Preis spricht -----------------------------
    ('B10-Hinweis von Hand entfernt', KISHIPRO,
     lambda h: re.sub(r'<!-- GUENSTIGER:START -->.*?<!-- GUENSTIGER:END -->\n?', '', h,
                      flags=re.S), 'ROT'),
    ('Preis im B10-Hinweis verfaelscht', KISHIPRO,
     lambda h: h.replace(f'kostet {_b10_preis(h)} € und kommt', 'kostet 99 € und kommt', 1),
     'ROT'),
    ('Sternzahl im B10-Hinweis verfaelscht', KISHIPRO,
     lambda h: h.replace('auf 4,4 Sterne aus', 'auf 4,9 Sterne aus', 1), 'ROT'),
    ('genanntes Modell im B10-Hinweis ausgetauscht', KISHIPRO,
     lambda h: h.replace('>Razer Kishi V3</a>', '>Razer Kishi Ultra</a>', 1), 'ROT'),
    # Teilstring-Falle: "88 €" steckt in "188 €". Die erste Fassung des Gates testete
    # `wert not in block` und liess diese Form durch -- rot wurde sie nur, weil der
    # Zeichenvergleich des Sync-Skripts daneben steht.
    ('Preis im B10-Hinweis um eine Ziffer verlaengert', KISHIPRO,
     lambda h: h.replace(f'kostet {_b10_preis(h)} € und kommt',
                         f'kostet 1{_b10_preis(h)} € und kommt', 1), 'ROT'),
    # Der Abbruch-Fall: Ein START ohne END liess verify.py mit ValueError sterben, also
    # exit 1 ohne Urteil -- und nahm die 250 Pruefstellen hinter §B10 mit. Die Batterie
    # unterscheidet ABBRUCH von ROT, deshalb greift dieser Fall die Klasse wirklich.
    ('B10-END-Marker entfernt', KISHIPRO,
     lambda h: h.replace('<!-- GUENSTIGER:END -->', '', 1), 'ROT'),
    ('B10-Hinweis in einen HTML-Kommentar gehuellt', KISHIPRO,
     lambda h: h.replace('<!-- GUENSTIGER:START -->', '<!-- GUENSTIGER:START --><!--', 1)
                .replace('<!-- GUENSTIGER:END -->', '--><!-- GUENSTIGER:END -->', 1),
     'ROT'),
    ('B10-Hinweis auf einer Seite, die keinen haben darf', REVIEW,
     lambda h: h.replace('<div class="verdict-box">',
                         '<!-- GUENSTIGER:START -->\n<div class="note note-info">'
                         'Guenstiger: irgendwas 1 € 5,0 Sterne</div>\n'
                         '<!-- GUENSTIGER:END -->\n<div class="verdict-box">', 1), 'ROT'),
    # Die Schleife des Gates laeuft ueber products.json und sieht nur Produktseiten. Ein
    # Block auf einer Blog- oder Hub-Seite blieb damit stumm gruen.
    ('B10-Hinweis auf einer Blog-Seite', BLOGSEITE,
     lambda h: h.replace('</main>',
                         '<!-- GUENSTIGER:START -->\n<div class="note note-info">'
                         'Guenstiger: irgendwas 1 € 5,0 Sterne</div>\n'
                         '<!-- GUENSTIGER:END -->\n</main>', 1), 'ROT'),
    ('LEGITIM zusaetzlicher Absatz auf einer B10-Seite', KISHIPRO,
     lambda h: h.replace('</main>', '<p>Nachtrag: Preis geprueft.</p></main>', 1), 'GRUEN'),

    # --- B11: die echte Alternative heisst Amazon und Video ----------------------------
    ('B11-Block auf der Startseite entfernt', START,
     lambda h: re.sub(r'<!-- POSITION:START -->.*?<!-- POSITION:END -->\n?', '', h,
                      flags=re.S), 'ROT'),
    ('B11-Block auf /ueber-uns/ entfernt', UEBERUNS,
     lambda h: re.sub(r'<!-- POSITION:START -->.*?<!-- POSITION:END -->\n?', '', h,
                      flags=re.S), 'ROT'),
    ('abgeleitete Zahl im B11-Block verfaelscht', START,
     lambda h: h.replace('Auf 33 unserer 42', 'Auf 44 unserer 42', 1), 'ROT'),
    # Teilstring-Falle mit eigener Pointe: "42" steht zweimal im Abschnitt. Die
    # Anwesenheitspruefung allein bleibt gruen, weil das zweite stehen bleibt -- erst das
    # Drift-Gate (keine ungedeckte Zahl) macht die Form rot.
    ('Zahl im B11-Block um eine Ziffer verlaengert', START,
     lambda h: h.replace('unserer 42 Produktseiten', 'unserer 142 Produktseiten', 1), 'ROT'),
    ('Alternative "Amazon" aus dem B11-Block entfernt', START,
     lambda h: h.replace('Warum nicht einfach bei Amazon schauen?',
                         'Warum nicht einfach woanders schauen?', 1), 'ROT'),
    ('Alternative "Video" aus dem B11-Block entfernt', START,
     lambda h: h.replace('oder sie suchen ein Video dazu', 'oder sie suchen etwas dazu', 1)
                .replace('Und statt eines Videos:', 'Und ausserdem:', 1), 'ROT'),
    ('Lesezeit-Spanne im B11-Block verfaelscht', START,
     lambda h: h.replace('liest du in 1 bis 2 Minuten', 'liest du in 1 bis 5 Minuten', 1),
     'ROT'),
    ('B11-END-Marker entfernt', UEBERUNS,
     lambda h: h.replace('<!-- POSITION:END -->', '', 1), 'ROT'),
    ('B11-Block zweimal auf derselben Seite', UEBERUNS,
     lambda h: h.replace('<!-- POSITION:END -->',
                         '<!-- POSITION:END -->\n<!-- POSITION:START -->\n<p>Doppelt</p>\n'
                         '<!-- POSITION:END -->', 1), 'ROT'),
    ('B11-Block auf einer Seite, die keinen traegt', BLOGSEITE,
     lambda h: h.replace('</main>', POSBLOCK + '</main>', 1), 'ROT'),
    # Die zwei Formen, die NUR die Eigenschaftspruefung findet: Der Zeichenvergleich sieht
    # sie nicht, weil der Block selbst unberuehrt bleibt.
    ('All-Aussage ueber eigene Tests wieder eingesetzt', METHODE,
     lambda h: h.replace('<h2 style="margin-top:24px">Unser Testprozess</h2>',
                         '<h2 style="margin-top:24px">Unser Testprozess</h2>\n'
                         '<p>Jeder Controller wird ueber mindestens 2-3 Wochen im echten '
                         'Gaming-Alltag getestet.</p>', 1), 'ROT'),
    ('All-Aussage anders formuliert', UEBERUNS,
     lambda h: h.replace('<h2 style="margin-top:32px">Wie wir Geld verdienen</h2>',
                         '<p>Alle Modelle im Sortiment testen wir selbst, bevor wir sie '
                         'empfehlen, und zwar wochenlang getestet im Alltag.</p>\n'
                         '    <h2 style="margin-top:32px">Wie wir Geld verdienen</h2>', 1),
     'ROT'),
    # Vier Satzstellungen, an denen die erste Fassung des Musters vorbeigelesen hat: Verb
    # zuerst, Fuellwort zwischen Quantor und Nomen, "Test" als Substantiv statt Verb, und
    # die Verneinungsform, die trotzdem eine All-Aussage ist.
    ('All-Aussage mit Verb zuerst', METHODE, lambda h: _satz(
        h, 'Wir testen jeden Controller ueber mehrere Wochen im Gaming-Alltag.'), 'ROT'),
    ('All-Aussage mit Fuellwort', METHODE, lambda h: _satz(
        h, 'Jeder einzelne Controller wird ueber mehrere Wochen getestet.'), 'ROT'),
    ('All-Aussage mit Test als Substantiv', METHODE, lambda h: _satz(
        h, 'Jeder Controller geht bei uns durch einen mehrwoechigen Test.'), 'ROT'),
    ('All-Aussage als "kein X ohne Test"', METHODE, lambda h: _satz(
        h, 'Kein Controller kommt ohne eigenen Test auf diese Seite.'), 'ROT'),
    # Und die Gegenrichtung: vier wahre Saetze, die das Muster NICHT faelschlich faengt.
    # Der erste ist die ehrliche Korrektur der alten Behauptung, der letzte steht in
    # dieser Form schon auf der Startseite.
    ('LEGITIM verneinte All-Aussage', METHODE, lambda h: _satz(
        h, 'Nicht jeder Controller im Sortiment ist von uns getestet.'), 'GRUEN'),
    ('LEGITIM Verneinung im Nebensatz', METHODE, lambda h: _satz(
        h, 'Jeder Controller, den wir nicht selbst getestet haben, bekommt einen '
           'Kurzcheck.'), 'GRUEN'),
    ('LEGITIM Frage statt Behauptung', METHODE, lambda h: _satz(
        h, 'Werden alle Controller getestet? Nein, 13 von 42.'), 'GRUEN'),
    ('LEGITIM All-Satz nennt die gemessene Zahl', METHODE, lambda h: _satz(
        h, 'Jedes Modell im Sortiment haben wir geprueft, 13 davon ausfuehrlich '
           'getestet.'), 'GRUEN'),
    # Methoden-Vokabular ohne All-Anspruch ueber eigene Tests. Die zweite Satzstellung
    # hat solche Saetze zuerst rot gemacht, und genau dieses Vokabular ist auf einer
    # Methodenseite der Normalfall.
    ('LEGITIM Testwort ohne All-Anspruch', METHODE, lambda h: _satz(
        h, 'Im Test zeigte sich, dass alle Controller mit Android laufen.'), 'GRUEN'),
    ('LEGITIM geprueft plus Quantor ohne Testbezug', METHODE, lambda h: _satz(
        h, 'Wir haben die Preise geprueft und alle Produkte neu sortiert.'), 'GRUEN'),
    ('All-Aussage mit Zahl in falscher Rolle', METHODE, lambda h: _satz(
        h, 'Jeder Controller bekommt einen 13-Punkte-Test im Alltag.'), 'ROT'),
    # §A6, der zweite Blocker des Pruefauflaufs: eine handgepflegte Review-Seite verliert
    # Schwaechen. Vorher blieb das stumm gruen.
    ('Schwaechen auf einer handgepflegten Review-Seite geloescht', KISHIPRO,
     lambda h: re.sub(r"(<div class=\"cons-box\"><h3>[^<]*</h3><ul>)(.*?)</ul>",
                      lambda m: m.group(1) + re.findall(r'<li.*?</li>', m.group(2), re.S)[0]
                      + '</ul>', h, count=1, flags=re.S), 'ROT'),
    ('LEGITIM Absatz neben dem B11-Block', START,
     lambda h: h.replace('<!-- POSITION:START -->',
                         '<p>Nachtrag: Stand geprueft.</p>\n    <!-- POSITION:START -->', 1),
     'GRUEN'),
    ('LEGITIM Testsatz auf der Methodenseite ohne All-Quantor', METHODE,
     lambda h: h.replace('<h2 style="margin-top:24px">Unsere Bewertungskriterien</h2>',
                         '<p>Die getesteten Modelle spielen wir ueber mehrere Wochen.</p>\n'
                         '<h2 style="margin-top:24px">Unsere Bewertungskriterien</h2>', 1),
     'GRUEN'),

    # --- B12: das Zeitversprechen, und zwar in beide Richtungen ------------------------
    ('Finder-Dauer auf der Startseite verfaelscht', START,
     lambda h: h.replace('in 60 Sekunden die richtige Wahl',
                         'in 90 Sekunden die richtige Wahl', 1), 'ROT'),
    ('Finder-Dauer in der Kachel verfaelscht', START,
     lambda h: h.replace('>60 Sek.<', '>45 Sek.<', 1), 'ROT'),
    ('Lesezeit auf einer Review-Seite verfaelscht', KISHIPRO,
     lambda h: re.sub(r'· \d+ Min\. Lesezeit ·', '· 9 Min. Lesezeit ·', h, count=1), 'ROT'),
    # Die Gegenrichtung, die beim Bauen gefehlt hat: Das Lesezeit-Gate prueft nur Seiten,
    # die eine NENNEN. Eine Seite, die ihre verliert, blieb stumm gruen.
    ('Lesezeit auf einer Review-Seite entfernt', KISHIPRO,
     lambda h: re.sub(r' · \d+ Min\. Lesezeit', '', h, count=1), 'ROT'),
    ('Lesezeit auf einer generierten Seite entfernt', 'produkte/marsgaming-mgpx/index.html',
     lambda h: re.sub(r'<div class="article-byline">[^<]*Lesezeit</div>', '', h, count=1),
     'ROT'),
    ('LEGITIM Sekundenangabe ohne Finder-Bezug', 'blog/controller-verbindet-nicht/index.html',
     lambda h: h.replace('etwa 5 Sekunden', 'etwa 7 Sekunden', 1), 'GRUEN'),
    # Die Formen, an denen die erste Fassung des Gates gescheitert ist: Umformulierung
    # statt Zahlendreher, und eine ZUSAETZLICHE Zusage neben der gepflegten.
    ('Finder-Zusage umformuliert statt verfaelscht', START,
     lambda h: h.replace('in 60 Sekunden die richtige Wahl',
                         'in zwei Minuten die richtige Wahl', 1), 'ROT'),
    ('zusaetzliche Finder-Zusage auf der Finder-Seite', 'controller-finder/index.html',
     lambda h: h.replace('</main>', '<p>Plane dafuer rund 90 Sekunden ein.</p></main>', 1),
     'ROT'),
    ('Finder-Dauer in der Meta-Description verfaelscht', 'controller-finder/index.html',
     lambda h: h.replace('content="Controller finden in 60 Sekunden',
                         'content="Controller finden in 30 Sekunden', 1), 'ROT'),
    ('Lesezeit auf einer generierten Seite verfaelscht', 'produkte/marsgaming-mgpx/index.html',
     lambda h: re.sub(r'· \d+ Min\. Lesezeit', '· 7 Min. Lesezeit', h, count=1), 'ROT'),
    ('Lesezeit auf einem Blog-Artikel entfernt', 'blog/hall-effect-erklaert/index.html',
     lambda h: re.sub(r' · \d+ Min\. Lesezeit', '', h, count=1), 'ROT'),
    # Alterungsprobe (P-13 Mechanismus 3): Text verlaengern, ohne eine Zahl anzufassen.
    ('Text verlaengert, Lesezeit bleibt stehen', KISHIPRO,
     lambda h: h.replace('</main>', '<p>' + ('Nachtrag zum Test mit vielen Woertern. ' * 120)
                         + '</p></main>', 1), 'ROT'),
    ('LEGITIM Absatz neben der Byline', KISHIPRO,
     lambda h: h.replace('</main>', '<p>Nachtrag.</p></main>', 1), 'GRUEN'),

    # --- §A1: eine Bewertung hinter einem Produktlink gehoert diesem Produkt ----------
    # Gefunden beim Nachmessen des X2s-Retro-Winkels: "X2s (3,8)" auf marken/gamesir,
    # waehrend products.json 3,9 fuehrt. Repoweit gab es genau eine Stelle dieser Form,
    # und sie war falsch.
    ('Bewertung hinter einem Produktlink verfaelscht', 'marken/gamesir/index.html',
     lambda h: h.replace('>X2s</a> (3,9)', '>X2s</a> (3,8)', 1), 'ROT'),
    ('falsche Bewertung hinter einem Produktlink im Fliesstext', KISHIPRO,
     lambda h: h.replace('</main>', '<p>Der <a href="/controller/universal/'
                         'gamesir-x5-lite-review/">X5 Lite</a> (4,7) ist die '
                         'Alternative.</p></main>', 1), 'ROT'),
    ('LEGITIM richtige Bewertung hinter einem Produktlink', KISHIPRO,
     lambda h: h.replace('</main>', '<p>Der <a href="/controller/universal/'
                         'gamesir-x5-lite-review/">X5 Lite</a> (4,2) ist die '
                         'Alternative.</p></main>', 1), 'GRUEN'),
    ('LEGITIM Zahl in Klammern ohne Produktlink davor', KISHIPRO,
     lambda h: h.replace('</main>', '<p>Der Markt liegt im Schnitt bei (4,1).</p></main>',
                         1), 'GRUEN'),

    # --- S1-Zitier-Pass: die Direktantwort auf der staerksten Inhaltsseite -------------
    ('Hall-Zahl in der Direktantwort verfaelscht', 'blog/hall-effect-erklaert/index.html',
     lambda h: h.replace(_hall_satz(h)[0],
                         f'Sechs der {_hall_satz(h)[2]} Controller', 1), 'ROT'),
    ('Sortimentszahl in der Direktantwort verfaelscht',
     'blog/hall-effect-erklaert/index.html',
     lambda h: h.replace(_hall_satz(h)[0],
                         f'{_hall_satz(h)[1]} der 30 Controller', 1), 'ROT'),
    # Ein Zahlwort, das das Gate nicht kennt, waere sonst eine stumme Luecke: Die Pruefung
    # haengt am Wort, also muss ein unbekanntes Wort selbst der Befund sein.
    ('unbekanntes Zahlwort in der Direktantwort', 'blog/hall-effect-erklaert/index.html',
     lambda h: h.replace(_hall_satz(h)[0],
                         f'Etliche der {_hall_satz(h)[2]} Controller', 1), 'ROT'),
    ('LEGITIM Satz daneben ergaenzt', 'blog/hall-effect-erklaert/index.html',
     lambda h: h.replace('Drei davon stehen hier mit Preis und Einordnung.',
                         'Drei davon stehen hier mit Preis und Einordnung. Nachtrag: '
                         'Stand geprueft.', 1), 'GRUEN'),
    ('Zahl im Mini-Gamepad-Einstieg verfaelscht', 'controller/mini-gamepad/index.html',
     lambda h: h.replace('Zwei Mini-Gamepads führen wir', 'Drei Mini-Gamepads führen wir',
                         1), 'ROT'),
    ('unbekanntes Zahlwort im Mini-Gamepad-Einstieg',
     'controller/mini-gamepad/index.html',
     lambda h: h.replace('Zwei Mini-Gamepads führen wir',
                         'Etliche Mini-Gamepads führen wir', 1), 'ROT'),
    ('Preis im Mini-Gamepad-Einstieg verfaelscht', 'controller/mini-gamepad/index.html',
     lambda h: h.replace('Ultimate Mobile für 45 Euro', 'Ultimate Mobile für 48 Euro', 1),
     'ROT'),

    # --- §A5: der Plattform-Chip einer Karte gegen worksOn ----------------------------
    # Aus der Aufarbeitung der 14 ungedeckten Spec-Chips: Zwei davon waren wahr, standen
    # aber in keinem specs-Eintrag und wurden deshalb von nichts geprueft.
    ('Plattform-Chip laesst eine Plattform aus', 'controller/index.html',
     lambda h: h.replace('<span class="k">Plattform</span> iOS+Android',
                         '<span class="k">Plattform</span> nur iOS', 1), 'ROT'),
    ('LEGITIM Plattform-Chip anders formuliert', 'controller/index.html',
     lambda h: h.replace('<span class="k">Plattform</span> iOS+Android',
                         '<span class="k">Plattform</span> iPhone und Android', 1),
     'GRUEN'),

    # ---- Legitim: MUSS gruen bleiben --------------------------------------------------
    ('LEGITIM unveraendert', REVIEW, lambda h: h, 'GRUEN'),
    # Die Beschriftung kommt aus der <h1> der Zielseite. Sie steht dort NICHT als
    # zusammenhaengender Text ("<span class=\"hl\">GameSir</span> Controller 2026"),
    # deshalb wird im h1-Bereich ersetzt und nicht per Literal -- meine erste Fassung traf
    # vier andere Stellen der Datei und meldete faelschlich, nichts bemerke die Aenderung.
    ('LEGITIM Hub bekommt eine neue Ueberschrift, Bloecke neu gesetzt', HUB,
     lambda h: re.sub(r'(<h1[^>]*>.*?)Controller 2026(.*?</h1>)',
                      r'\1Gamepads 2026\2', h, count=1, flags=re.S),
     'GRUEN_NACH_SYNC'),
    # Die Hub-Zugehoerigkeit haengt an `worksOn` (daraus baut gen_hubs die Karten), nicht
    # an `platform`. Meine erste Fassung aenderte `platform` und griff gar nicht.
    ('LEGITIM ein Absatz zusaetzlich auf der Review-Seite', REVIEW,
     lambda h: h.replace('<!-- HUBLINKS:START -->',
                         '<p>Nachtrag: Preis am 04.10. geprueft.</p>\n'
                         '<!-- HUBLINKS:START -->', 1), 'GRUEN'),
    ('LEGITIM ein weiterer interner Link im Fliesstext', REVIEW,
     lambda h: h.replace('<!-- HUBLINKS:START -->',
                         '<p>Mehr dazu im <a href="/blog/hall-effect-erklaert/">'
                         'Hall-Effect-Erklaerer</a>.</p>\n<!-- HUBLINKS:START -->', 1),
     'GRUEN'),
    # ---- §A5 Verfuegbarkeit (06.10.2026) ---------------------------------------------
    # "Verfügbar" stand 197 Mal als Literal im Markup und kam aus nichts; beim
    # Vollabgleich war es fuer 6 von 42 Produkten falsch. Diese Faelle halten das Gate
    # in BEIDE Richtungen fest: der Defekt muss rot werden, und das Nachziehen aus dem
    # Datenkern muss gruen bleiben.
    ('Badge-Text eines nicht kaufbaren Produkts auf "Verfügbar"', GEN_KARTE,
     lambda h: h.replace('<span class="out-stock">Nicht verfügbar</span>',
                         '<span class="out-stock">Verfügbar</span>', 1), 'ROT'),
    ('Badge-Klasse gruen an "Nicht verfügbar"', GEN_KARTE,
     lambda h: h.replace('<span class="out-stock">Nicht verfügbar</span>',
                         '<span class="in-stock">Nicht verfügbar</span>', 1), 'ROT'),
    ('Verfuegbarkeitstext ohne Badge-Klasse', GEN_KARTE,
     lambda h: h.replace('<span class="out-stock">Nicht verfügbar</span>',
                         '<em>Nicht verfügbar</em>', 1), 'ROT'),
    ('Schema-availability auf InStock bei stock=nein',
     'produkte/hellcool-controller/index.html',
     lambda h: h.replace('"availability": "https://schema.org/OutOfStock"',
                         '"availability": "https://schema.org/InStock"'), 'ROT'),
    ('JS-Label weicht von produktdaten.py ab', HUBRENDER,
     lambda j: j.replace("nein: 'Nicht verfügbar'", "nein: 'Nicht lieferbar'"),
     'ROT_NACH_BUMP'),
    ('JS-Klasse weicht von produktdaten.py ab', HUBRENDER,
     lambda j: j.replace("nein: 'out-stock'", "nein: 'in-stock'"), 'ROT_NACH_BUMP'),
    ('JS-Renderer fuehrt die Verfuegbarkeits-Tabelle gar nicht', HUBRENDER,
     lambda j: '\n'.join(z for z in j.split('\n')
                         if 'STOCK_LABEL' not in z and 'STOCK_KLASSE' not in z)
               .replace('${stockHTML(p)}', '<span class="in-stock">Verfügbar</span>'),
     'ROT_NACH_BUMP'),
    # Die Einrueckung ist die von json.dump(indent=2) in einer Liste von Objekten:
    # vier Leerzeichen. Mit zwei griff die Mutation nicht, und der Fall haette
    # "Mutation hat nichts geaendert" gemeldet statt etwas zu beweisen.
    ('stock-Feld bei einem Produkt entfernt', PRODUKTJSON,
     lambda j: j.replace('    "price": "190 €",\n    "stock": "nein",',
                         '    "price": "190 €",', 1), 'ROT'),
    ('stock-Wert ausserhalb der vier erlaubten', PRODUKTJSON,
     lambda j: j.replace('"stock": "nein"', '"stock": "vielleicht"', 1), 'ROT'),

    # ---- §A5 Black-Friday-Schwellen-Matrix (06.10.2026) ------------------------------
    # Die Seite nennt ihre eigene Rechenregel ("rund 20 Prozent unter dem Regulaerpreis")
    # und hat sie um das Fuenffache verfehlt, weil Spalte 2 vom Preis-Sync nachgezogen
    # wurde und die daraus berechnete Spalte 3 nicht.
    ('BF-Schwelle 2 € neben der Regel', BF,
     lambda h: h.replace('<strong>unter 54 €</strong>', '<strong>unter 56 €</strong>'),
     'ROT'),
    ('BF-Schwelle auf den alten Wert zurueck (4 statt 20 Prozent)', BF,
     lambda h: h.replace('<strong>unter 54 €</strong>', '<strong>unter 65 €</strong>'),
     'ROT'),
    ('BF-Regulaerpreis vom Datenkern geloest', BF,
     lambda h: h.replace('<td>68 €</td><td><strong>unter 54 €',
                         '<td>80 €</td><td><strong>unter 54 €'), 'ROT'),
    ('BF-Deal-Regel aus dem Text entfernt', BF,
     lambda h: h.replace('rund 20 Prozent unter dem Regulärpreis',
                         'deutlich unter dem Regulärpreis'), 'ROT'),
    ('BF-Regel auf 25 Prozent, Schwellen bleiben', BF,
     lambda h: h.replace('rund 20 Prozent unter dem Regulärpreis',
                         'rund 25 Prozent unter dem Regulärpreis'), 'ROT'),
    ('EINE BF-Zeile unlesbar gemacht (Teil-Ausfall)', BF,
     lambda h: h.replace('<strong>unter 62 €</strong>', 'unter 62 EUR'), 'ROT'),
    ('BF-Tabelle ganz entfernt', BF,
     lambda h: re.sub(r'<table[^>]*class="bf-table".*?</table>', '', h, flags=re.S),
     'ROT'),
    ('LEGITIM BF-Schwelle 1 € gerundet', BF,
     lambda h: h.replace('<strong>unter 54 €</strong>', '<strong>unter 55 €</strong>'),
     'GRUEN'),
    ('LEGITIM eine BF-Zeile ganz geloescht', BF,
     lambda h: re.sub(r'<tr><td><a href="/controller/universal/razer-kishi-v3-review/".*?</tr>\n',
                      '', h, flags=re.S), 'GRUEN'),
    # Die QUELLE aendern, nicht die generierte Seite: Ein Edit am Output wird vom
    # Zeichenvergleich (verify 6c) rot, und der Fall haette das Generator-Gate bewiesen
    # statt die Verneinungs-Ausnahme. Genau so war meine erste Fassung falsch.
    ('LEGITIM Verneinung im Hall-Satz, Quelle geaendert (kein Fehlalarm)',
     'scripts/gen_content.py',
     lambda h: h.replace('(kein Hall-Effect)', '(ohne Hall-Effect)'), 'GRUEN_NACH_SYNC'),
    ('LEGITIM Redirect-Stub verlinkt zusaetzlich auf eine Seite', 'ratgeber/index.html',
     lambda h: h.replace('</body>',
                         '<p><a href="/produkte/mocute-050/">Mocute 050</a></p></body>', 1),
     'GRUEN'),
]


def lauf(arbeit):
    r = subprocess.run([sys.executable, 'scripts/verify.py'], cwd=arbeit,
                       capture_output=True, text=True, timeout=300)
    aus = r.stderr + r.stdout
    if not re.search(r'(GRÜN|ROT) —', aus):
        letzte = [x for x in aus.strip().splitlines() if x.strip()]
        return 'ABBRUCH', (letzte[-1][:90] if letzte else '')
    if r.returncode == 0:
        return 'GRUEN', ''
    zeilen = [x for x in aus.splitlines() if 'FEHLER' in x]
    return 'ROT', (zeilen[0].strip()[:95] if zeilen else '')


def main():
    kurz = '--kurz' in sys.argv
    rumpf = tempfile.mkdtemp(prefix='spc-links-')
    falsch, ungegriffen = 0, 0
    try:
        for etikett, datei, mutation, soll in FAELLE:
            arbeit = os.path.join(rumpf, re.sub(r'\W+', '_', etikett)[:40])
            shutil.copytree(ROOT, arbeit,
                            ignore=shutil.ignore_patterns('.git', 'node_modules', 'brain',
                                                      'SPC-Gaming-Visuals',
                                                          '__pycache__'))
            pfad = os.path.join(arbeit, datei)
            vorher = open(pfad, encoding='utf-8').read()
            try:
                nachher = mutation(vorher)
            except Exception as e:
                print(f'>>> {etikett}: Mutation selbst kaputt ({e})')
                falsch += 1
                shutil.rmtree(arbeit, ignore_errors=True)
                continue
            # Eine Mutation, die nicht greift, prueft NICHTS -- und sah bisher aus wie ein
            # bestandener Fall. Dieselbe Falle wie bei den Finder-Proben (R17) und, eine
            # Runde spaeter, bei der Bestenlisten-Batterie.
            if nachher == vorher and soll != 'GRUEN':
                print(f'>>> {etikett}: Mutation hat nicht gegriffen (Datei unveraendert)')
                ungegriffen += 1
                shutil.rmtree(arbeit, ignore_errors=True)
                continue
            open(pfad, 'w', encoding='utf-8').write(nachher)

            erwartet = soll
            if soll in ('ROT_NACH_BUMP', 'GRUEN_NACH_BUMP'):
                # Eine JS-Aenderung aendert den Inhalts-Hash, und §D verlangt die
                # nachgezogene Asset-Version. Ohne diesen Schritt entscheidet §D ueber
                # rot/gruen, und der Fall sagt nichts ueber das gemeinte Gate.
                subprocess.run([sys.executable, 'scripts/bump_asset_version.py'],
                               cwd=arbeit, capture_output=True, text=True, timeout=300)
                erwartet = 'ROT' if soll == 'ROT_NACH_BUMP' else 'GRUEN'

            if soll == 'LABEL_GLEICH':
                for s in ('sync_hublinks.py', 'sync_guenstiger.py', 'gen_pages.py', 'bump_asset_version.py'):
                    subprocess.run([sys.executable, 'scripts/' + s]
                                   + (['--regen'] if s == 'gen_pages.py' else []),
                                   cwd=arbeit, capture_output=True, text=True, timeout=300)
                # Eine Seite, die den TABLET-Hub wirklich fuehrt. Die erste Fassung las
                # die G8-Galileo-Seite, und die verlinkt gar nicht dorthin -- der Fall
                # prueft dann eine Beschriftung, die auf der Seite nicht vorkommt.
                _p = os.path.join(arbeit, TABLETSEITE)
                _b = re.search(r'<p class="hublinks">(.*?)</p>',
                               open(_p, encoding='utf-8').read(), re.S)
                _txt = re.sub(r'<[^>]+>', '', _b.group(1)) if _b else ''
                if '&amp;amp;' in _txt or '&amp;' not in _txt:
                    print(f'>>> {etikett}: Beschriftung falsch escaped: {_txt[:120]}')
                    falsch += 1
                    shutil.rmtree(arbeit, ignore_errors=True)
                    continue
                erwartet = 'GRUEN'

            if soll == 'GRUEN_NACH_SYNC':
                # Legitime Aenderung: Erst MUSS ein Gate sie bemerken, dann MUSS nach dem
                # Nachziehen alles gruen sein. Ohne den ersten Schritt wuerde der Fall
                # auch dann bestehen, wenn gar nichts geprueft wird.
                r1 = subprocess.run([sys.executable, 'scripts/sync_hublinks.py', '--check'],
                                    cwd=arbeit, capture_output=True, text=True, timeout=180)
                r2 = subprocess.run([sys.executable, 'scripts/verify.py'], cwd=arbeit,
                                    capture_output=True, text=True, timeout=300)
                if r1.returncode == 0 and r2.returncode == 0:
                    print(f'>>> {etikett}: weder --check noch verify bemerken die '
                          f'Aenderung — dann prueft der Fall nichts')
                    falsch += 1
                    shutil.rmtree(arbeit, ignore_errors=True)
                    continue
                # VOLLE Nachzieh-Kette. Eine geaenderte `worksOn` wirkt bis in die
                # Kachelzahlen der Startseite ("iPhone Controller: 24 Modelle"), und ein
                # Fall, der an einem NICHT nachgezogenen Nachbarn rot wird, prueft nicht
                # das, wofuer er geschrieben ist.
                for s in ('sync_new_products.py', 'sync_product_values.py', 'gen_hubs.py',
                          'gen_pages.py', 'gen_brand_sections.py', 'gen_bestenliste.py',
                          'gen_preisfrage.py', 'gen_longtail.py', 'sync_kompat.py',
                          'sync_lesezeit.py', 'sync_hublinks.py', 'sync_guenstiger.py', 'bump_asset_version.py'):
                    subprocess.run([sys.executable, 'scripts/' + s]
                                   + (['--regen'] if s == 'gen_pages.py' else []),
                                   cwd=arbeit, capture_output=True, text=True, timeout=300)
                erwartet = 'GRUEN'

            art, wie = lauf(arbeit)
            ok = (art == erwartet)
            if not ok:
                falsch += 1
            if not kurz or not ok:
                print(f'{"ok " if ok else ">>>"} {art:8s} | {etikett:56s} | soll '
                      f'{erwartet:6s} | {wie}')
            shutil.rmtree(arbeit, ignore_errors=True)

        n_rot = sum(1 for f in FAELLE if f[3].startswith('ROT'))
        print(f'\n{len(FAELLE)} Faelle ({n_rot} muessen rot werden, '
              f'{len(FAELLE) - n_rot} muessen gruen bleiben), {falsch} falsch, '
              f'{ungegriffen} nicht gegriffen')
        return 1 if (falsch or ungegriffen) else 0
    finally:
        shutil.rmtree(rumpf, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
