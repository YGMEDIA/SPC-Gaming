#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B11: Die echte Alternative heisst Amazon und YouTube, nicht "andere Blogs".

DIE UNBEQUEME FRAGE (Dunford, Obviously Awesome)
Positionierung faengt bei der Frage an, was der Kunde STATTDESSEN tun wuerde. Fuer uns ist
das nicht ein anderer Controller-Blog. Es ist Amazon selbst und ein Video. Wer einen
Controller sucht, geht zuerst dorthin.

GEMESSEN AM 05.10.2026 ueber alle 127 ausgelieferten Seiten:
  "YouTube" steht auf 0 Seiten. Die Alternative wird nirgends benannt.
  "Amazon" steht auf der Startseite DREIMAL im Seiteninhalt (ohne Navigation und Footer),
  alle drei Male als DATENQUELLE: "Belegte Amazon-Daten", "Preise und Bewertungen von
  Amazon.de", "Produktbilder aus dem Amazon-Katalog". Mit dem repoweiten Footer sind es
  vier, die vierte ist der Provisionshinweis. Auf /ueber-uns/ zwei im Inhalt, beide der
  Provisionshinweis. Kein einziges Mal als das, womit der Leser uns vergleicht.
  (Hier stand zuerst "zweimal". Gezaehlt waren SAETZE, nicht Stellen, und der Messbereich
  war nicht genannt -- derselbe Fehler, den diese Massnahme auf den Seiten abstellt.)
  Positioniert wurde gegen "klassische Affiliate-Seiten" und "Marketing-Blabla" -- gegen
  einen Gegner also, den der Leser gar nicht in Betracht zieht.

WAS DIESER BLOCK SAGT, UND WARUM ER NACHRECHENBAR IST
Jede Zahl im Text kommt aus einer Regel, die schon im Repo steht, und keine aus dieser
Datei: die Kompatibilitaets-Aussage aus `kompat.py` (B1), der Hinweis auf das guenstigere
Geschwister aus `guenstiger.py` (B10), die Schwelle aus `produktdaten.A6_SCHWELLE` (§A6),
die Lesezeit aus `lesezeit.py` (B5), Test gegen Kurzcheck aus dem `detail`-Praefix (B9).
Eine Positionierung, die Eigenschaften behauptet, muss sie belegen koennen; wer sie
haendisch eintippt, hat beim naechsten Produktwechsel eine Behauptung ohne Deckung.

DIE ZWEITE HAELFTE: EINE AUSSAGE, DIE NICHT STIMMTE
/ueber-uns/ und /redaktion/ sagten beide "Jeder Controller wird ueber mehrere Wochen im
echten Gaming-Alltag getestet". Die Startseite sagt im selben Atemzug "42 Modelle im
Sortiment, 13 davon ausfuehrlich getestet", und gemessen tragen genau 13 der 42 Seiten
einen eigenen Test. Beides kann nicht stimmen. Die All-Aussage stand auf den zwei Seiten,
auf denen ein Leser die Methode PRUEFT -- der teuerste Ort fuer eine Uebertreibung. Der
Methodik-Block sagt jetzt beide Zahlen und benennt, was die uebrigen Seiten sind.

Verwendet von sync_positionierung.py. Die Zahlen prueft verify.py (§B11) am
ausgelieferten Stand nach, nicht am Lauf des Generators.
"""
import json
import os
import re
import sys
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from produktdaten import (A6_SCHWELLE, LABEL_TEST, LABEL_DATENBLATT, bewertung,
                          sterne_text, text as pfeld)
from kompat import kompat, kompat_html
from guenstiger import finden
from lesezeit import minuten

MARKER = 'POSITION'

# Die Seiten, die eine Positionierung tragen, und welcher Block dorthin gehoert.
# /redaktion/ steht hier mit, obwohl die Aufgabe nur Startseite und /ueber-uns/ nannte:
# Die All-Aussage ueber die Tests stand dort in ihrer staerksten Form ("mindestens 2-3
# Wochen"), und eine Methodenseite mit einer Aussage, die auf der Nachbarseite korrigiert
# wird, ist schlimmer als gar keine.
SEITEN = (('index.html', 'start'),
          ('ueber-uns/index.html', 'methode'),
          ('redaktion/index.html', 'methode'))


def _testseite(p):
    """Traegt dieses Produkt einen eigenen Test? Dieselbe Regel wie die B9-Beschriftung."""
    return pfeld(p, 'detail').startswith('/controller/')


class _Schwaechen(HTMLParser):
    """Zaehlt die Punkte in der Schwaechen-Liste einer Produktseite.

    Geparst, nicht per Regex: Die Pro/Contra-Kaesten stehen auf 42 Seiten in zwei
    Schreibweisen (Generator und Handfassung), und ein Muster, das die eine trifft,
    uebersieht die andere stillschweigend. Angesprungen wird die Klasse, nicht die
    Ueberschrift -- eine umbenannte Ueberschrift darf die Zaehlung nicht abschalten.

    GENAU `cons-box`, nicht "irgendeine Klasse mit con": Meine erste Fassung traf
    `pros-cons-grid`, also die Klammer um BEIDE Kaesten, und zaehlte die Staerken mit.
    Das Minimum sprang damit von 2 auf 5 -- die Zahl haette den Satz auf der Startseite
    verstaerkt, und zwar mit den Punkten, die das Gegenteil von einer Schwaeche sind.
    """

    MUSTER = re.compile(r'\bcons-box\b|\bcontra-box\b|\bschwaechen-box\b', re.I)
    # Dieselbe Liste wie in `lesezeit._KartenLeser`, und aus demselben Grund: Ein `<img>`
    # oder `<br>` ohne Schraegstrich kommt nie wieder vom Stapel, der Kasten schliesst
    # nie, und JEDES spaetere <li> der Seite zaehlt als Schwaeche. Die Richtung ist
    # Aufblaehen, also stumm gruen -- genau das, was dieses Gate verhindern soll. Der
    # Fehler stand im selben scripts/-Verzeichnis schon dokumentiert; ich habe ihn
    # trotzdem noch einmal gebaut.
    VOID = {'img', 'br', 'hr', 'input', 'meta', 'link', 'source', 'area', 'col',
            'embed', 'param', 'track', 'wbr', 'base'}

    def __init__(self):
        super().__init__()
        self.tiefe, self.stapel, self.n, self._template = None, [], 0, 0

    def handle_starttag(self, tag, attrs):
        if tag == 'template':
            # Was in <template> steht, rendert der Browser nicht. Eine Schwaeche dort
            # ist fuer den Leser keine.
            self._template += 1
            return
        if self._template or tag in self.VOID:
            return
        self.stapel.append(tag)
        if self.tiefe is None and self.MUSTER.search(dict(attrs).get('class', '') or ''):
            self.tiefe = len(self.stapel)
        elif self.tiefe is not None and tag == 'li':
            self.n += 1

    def handle_endtag(self, tag):
        if tag == 'template':
            self._template = max(0, self._template - 1)
            return
        if self._template or tag in self.VOID:
            return
        if self.tiefe is not None and len(self.stapel) == self.tiefe:
            self.tiefe = None
        if self.stapel:
            self.stapel.pop()


def schwaechen(html):
    """Anzahl der genannten Schwaechen im <main> einer Produktseite."""
    m = re.search(r'<main\b.*?</main>', html, re.S)
    if not m:
        return 0
    p = _Schwaechen()
    p.feed(m.group(0))
    return p.n


ZAHLWORT = {2: 'zwei', 3: 'drei', 4: 'vier', 5: 'fünf', 6: 'sechs'}


def fakten(items, wurzel='.'):
    """Alle Zahlen des Blocks, jede aus der Regel, die sie besitzt.

    `wurzel` nur fuer die Lesezeit: Sie steht nicht in products.json, sondern ergibt sich
    aus dem Text der Testseiten. Fehlt eine Seite, faellt sie aus der Spanne heraus,
    statt den Lauf abzubrechen -- ein fehlendes Ziel meldet §A1 an seiner Stelle.
    """
    ctrl = [p for p in items if pfeld(p, 'type') == 'controller']
    tests = [p for p in items if _testseite(p)]
    lese, cons = [], []
    for p in items:
        f = os.path.join(wurzel, pfeld(p, 'detail').strip('/'), 'index.html')
        if not os.path.exists(f):
            continue
        h = open(f, encoding='utf-8').read()
        cons.append(schwaechen(h))
        if _testseite(p):
            m = minuten(h)
            if m:
                lese.append(m)
    return {
        # Die SCHWAECHSTE Seite bestimmt den Satz, nicht der Durchschnitt: "mindestens
        # zwei" ist eine Aussage ueber das Minimum, und eine Aussage ueber das Minimum
        # darf nur so stark sein wie ihr schwaechstes Glied (gemessen: 42 Seiten,
        # Minimum 2, 16 davon genau auf 2).
        'min_cons': min(cons) if cons else 0,
        'produkte': len(items),
        'controller': len(ctrl),
        'tests': len(tests),
        # Getrennt, weil die All-Aussagen-Pruefung an der genannten Klasse haengt:
        # "Jeder Controller wird getestet" waere wahr, sobald alle 28 Controller
        # einen Test tragen, auch wenn die 14 Zubehoerteile keinen haben.
        'tests_controller': sum(1 for p in ctrl if _testseite(p)),
        'kurzchecks': len(items) - len(tests),
        'kompat': sum(1 for p in items if kompat_html(p, lambda x: x)),
        # Die Negativzeile steht NICHT in jedem Kasten: `kompat()` liefert sie nur, wenn
        # die Verbindungsart eine Ausgrenzung hergibt. Erste Fassung des Textes sagte "an
        # welche Geraete es passt und an welche nicht" ueber alle 33 -- gemessen tragen 13
        # davon eine Negativzeile. Der staerkere Teil der Aussage galt fuer ein Drittel.
        'kompat_nein': sum(1 for p in items if (kompat(p) or (None, None, None))[1]),
        'guenstiger': sum(1 for p in items if finden(p, items)),
        'unter_schwelle': sum(1 for p in ctrl if (bewertung(p)[0] is not None
                                           and bewertung(p)[0] < A6_SCHWELLE)),
        # Ein Controller OHNE Bewertung ist weder ueber noch unter der Schwelle.
        # `or 99` hat ihn stillschweigend als unauffaellig gezaehlt und haette aus
        # einer fehlenden Zahl eine Aussage gemacht; §B11 meldet ihn stattdessen.
        'ohne_bewertung': sum(1 for p in ctrl if bewertung(p)[0] is None),
        'lese_min': min(lese) if lese else None,
        'lese_max': max(lese) if lese else None,
    }


def _spanne(f):
    """"1 bis 2 Minuten" oder "2 Minuten", wenn alle Testseiten gleich lang sind."""
    a, b = f['lese_min'], f['lese_max']
    if a is None:
        return ''
    return f'{a} Minuten' if a == b else f'{a} bis {b} Minuten'


def html_start(f, esc):
    """Der Abschnitt der Startseite: die drei Fragen, die der Leser sonst offen laesst.

    Die Behauptungen stehen bewusst ueber UNS und nicht ueber Amazon. Was in einer
    Artikelbeschreibung steht oder fehlt, koennten wir nicht belegen, und eine
    Positionierung, die mit einer unbelegbaren Aussage ueber den Wettbewerber anfaengt,
    gibt genau das Argument aus der Hand, mit dem sie wirbt.
    """
    spanne = _spanne(f)
    if not spanne or not f['produkte']:
        return ''
    return (
        '<section class="section-sm" aria-labelledby="pos-title">\n'
        '  <div class="container">\n'
        '    <h2 class="sec-title" id="pos-title"><span class="bar" aria-hidden="true">'
        '</span> Warum nicht einfach bei Amazon schauen?</h2>\n'
        '    <p style="color:var(--ink-soft);line-height:1.7;margin:10px 0 4px;'
        'max-width:760px">Die meisten tun genau das, oder sie suchen ein Video dazu. '
        'Drei Fragen bleiben dabei offen. Genau die beantworten wir.</p>\n'
        '    <div class="feature-grid">\n'
        '      <div class="feature-card">\n'
        '        <h3>Passt das an mein Gerät?</h3>\n'
        f'        <p>Auf {f["kompat"]} unserer {f["produkte"]} Produktseiten steht in '
        'einem eigenen Kasten, an welche Geräte ein Modell passt, auf '
        f'{f["kompat_nein"]} davon auch ausdrücklich, an welche nicht. Abgeleitet aus '
        'der Verbindungsart, nicht getextet: Ein Lightning-Controller passt nicht an ein '
        'iPhone 15, und das gehört vor den Kauf, nicht in die Rücksendung.</p>\n'
        '      </div>\n'
        '      <div class="feature-card">\n'
        '        <h3>Wo ist der Haken?</h3>\n'
        f'        <p>Jede unserer {f["produkte"]} Produktseiten nennt mindestens '
        f'{ZAHLWORT.get(f["min_cons"], f["min_cons"])} '
        f'Schwächen. Liegt ein Modell unter {sterne_text(A6_SCHWELLE)} Sternen, bekommt '
        f'es eine Warnung statt einer Empfehlung. Von den {f["controller"]} Controllern '
        f'trifft das aktuell {f["unter_schwelle"]}.</p>\n'
        '      </div>\n'
        '      <div class="feature-card">\n'
        '        <h3>Ist teurer wirklich besser?</h3>\n'
        f'        <p>Auf {f["guenstiger"]} Produktseiten steht, dass ein günstigeres '
        'Modell derselben Marke besser bewertet ist, mit Namen, Preis und beiden '
        'Bewertungen. Das ist die Zahl, die gegen unsere eigene Provision spricht.</p>\n'
        '      </div>\n'
        '    </div>\n'
        f'    <p style="color:var(--ink-soft);line-height:1.7;margin-top:18px;'
        f'max-width:760px">Und statt eines Videos: Unsere Tests liest du in {spanne}. '
        'Oben steht das Urteil, darunter die Daten, dann die Schwächen. Was du nicht '
        'brauchst, überspringst du.</p>\n'
        '  </div>\n'
        '</section>')


def html_methode(f, esc):
    """Der Methodik-Absatz fuer /ueber-uns/ und /redaktion/.

    Er ersetzt die All-Aussage. Was bleibt, ist der Testprozess selbst; was dazukommt,
    sind die zwei Zahlen und die Auskunft, was die anderen Seiten sind. Der Satz ueber die
    Beschriftung ist kein Schmuck: Er macht die Unterscheidung fuer den Leser pruefbar,
    weil sie auf jeder Karte steht (B9).
    """
    if not f['tests'] or not f['kurzchecks']:
        return ''
    return (
        '<p style="margin-top:12px;color:var(--ink-soft);line-height:1.7">Von den '
        f'{f["produkte"]} Modellen im Sortiment haben {f["tests"]} einen eigenen Test. '
        'Diese Controller spielen wir über mehrere Wochen im Alltag, in PUBG Mobile, '
        'CoD Mobile, Cloud-Gaming-Sessions und Emulation, und prüfen Stick-Präzision, '
        'Verbindungsstabilität und Hüllen-Kompatibilität an echten Geräten. Die übrigen '
        f'{f["kurzchecks"]} Seiten sind Kurzchecks: eingeordnete Daten aus '
        'Herstellerangaben und von Amazon, ohne eigenen Test. Welche Art Seite dich '
        f'erwartet, steht auf jedem Knopf. „{esc(LABEL_TEST)}“ führt zu einem eigenen '
        f'Test, „{esc(LABEL_DATENBLATT)}“ zum Datenblatt.</p>')


def block(inhalt):
    """Leerer Inhalt ergibt KEINEN Block (Lehre aus B10)."""
    if not inhalt:
        return ''
    return f'<!-- {MARKER}:START -->\n{inhalt}\n<!-- {MARKER}:END -->'


def laden(wurzel='.'):
    return json.load(open(os.path.join(wurzel, 'assets/data/products.json'),
                          encoding='utf-8'))
