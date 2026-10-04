#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Welcher CSS-Wert fuer ein Element gilt: Selektor-Auswertung plus Kaskade.

Gebraucht wird genau eine Frage: Ist der Controller-Finder im Ruhezustand sichtbar? Das
haengt an `display`, `visibility` und `opacity`, und damit an der Frage, welche Regel
gewinnt. Vier Pruefrunden haben an dieser Stelle Befunde gebracht, jede in BEIDE
Richtungen -- ein Loch und ein Fehlalarm aus derselben Zeile:

  R21  Die Pruefung suchte IRGENDEINE Regel. Eine spaetere gewinnt, Finder leer, Lauf gruen.
  R22  Nur zwei Klassennamen abgefragt: `.finder-options{display:none}` blieb gruen, und
       korrektes `#finder .finder-step{display:none}` wurde rot.
  R24  Nach Quellreihenfolge statt Spezifitaet geordnet: `.finder-step[data-step]` am Ende
       blieb gruen, und eine bloesse UMSORTIERUNG der zwei Regeln ergab 14 Fehler.
  R25  Spezifitaet nur aus der letzten Verbundgruppe: `.finder .finder-step{display:none}`
       blieb gruen (real (0,2,0), gerechnet (0,1,0)). `~` wurde als Kombinator zerlegt und
       zerschnitt `[class~="x"]`. Und `:not()` galt als immer treffend, womit die voellig
       korrekte Fassung `.finder-step:not(.is-active){display:none}` 14 Fehler ergab.

Die Lehre daraus steht in P-13 Mechanismus 16: Ein Gate mit Loch UND Fehlalarm hat die
falsche Regel, nicht die zu enge. Deshalb liegt die Auswertung jetzt hier, mit einer
Falltabelle in `selbsttest()`, die alle oben genannten Formen enthaelt.

WAS DIESES MODUL NICHT KANN, ausdruecklich und nicht geschlossen:
  · Natives CSS-Nesting (`.finder { & .finder-step { ... } }` oder ohne `&`) faellt
    stumm weg: Der Block-Regex kann nicht verschachteln, der Rumpf landet als
    Deklarationstext und die Deklarations-Suche findet nichts. Dieselbe Ursache, die bei
    `@media` geschlossen wurde -- dort geht es, weil der Rumpf vollstaendige Regeln
    enthaelt, beim Nesting muessen die Selektoren zusammengesetzt werden, und das ist ein
    Parser. Gemessen: 0 Vorkommen in den ausgelieferten CSS-Quellen (R27).
  · `_argument()` zaehlt Klammern, ueberspringt aber keine Anfuehrungszeichen und keine
    `[…]`: In `:not([data-x=")"])` oder `:is(a[title="x)y"])` schliesst das `)` im String
    das Argument zu frueh, und der Rest der Gruppe wird als eigene Token gelesen. Das
    waere ein Parser fuer String- und Klammer-Zustaende; es bleibt offen und steht hier,
    statt still auf die naechste Runde zu warten. Gemessen in den ausgelieferten CSS-
    Quellen (72 Quellen, 2989 Selektoren): 9 Selektoren mit Funktions-Pseudoklasse, alle
    `:nth-child(even)`, davon 0 mit Anfuehrungszeichen oder `[` im Argument (R30).
  · `opacity: calc(0)` und andere berechnete Werte gelten als sichtbar.
  · Vererbung und `!important` aus einem Autoren-Stylesheet gegen Nutzer-Stylesheets.
    (`@media`, `@supports`, `@layer`, `@container` und `@scope` werden dagegen
    AUFGESCHNITTEN und ihr Inhalt mitgelesen -- hier stand bis R27 das Gegenteil.)
  · Die Vorfahren-TEILE eines Selektors werden beim Treffen ignoriert, nur beim
    Gewichten gezaehlt. `#woanders .finder-step{display:none}` gilt hier also als
    zutreffend -- das macht das Gate strenger, nicht blinder.
  · Pseudoklassen: `:not()`, `:is()`, `:where()`, `:matches()` und `:any()` werden
    AUSGEWERTET (siehe `_LISTEN_PS`, mit der Spezifitaetsregel je Form -- `:where()`
    zaehlt null). `:has()` ist nicht entscheidbar, weil der Harness nur die Kette nach
    OBEN liefert; solche Regeln werden als "nicht entscheidbar" GEMELDET, nicht
    verworfen. Alle uebrigen Pseudoklassen (`:hover`, `:focus`, `:nth-child`, …) gelten
    als nicht treffend -- fuer die Frage "sichtbar im Ruhezustand" ist das bei den
    Interaktions-Formen richtig und bei den strukturellen eine Grenze.
    Hier stand bis R28 "Pseudoklassen ausser `:not()` gelten als NICHT treffend", mit
    `:hover` als Begruendung. Gemessen galt der Satz fuer genau eine von sechs Formen,
    und `_LISTEN_PS` direkt darunter implementierte das Gegenteil.
  · (Mehrere Deklarationen derselben Eigenschaft in einem Block sind KEINE Grenze mehr:
    es gilt die letzte, und ein `!important` darin schlaegt jede spaetere ohne. Hier stand
    bis R28 "es gilt die erste" -- die Aussage von vor dem Semikolon-Fix, in derselben
    Runde widerlegt, in der der Fix entstand.)

Aufruf:  python3 scripts/css_kaskade.py     (Falltabelle, Exit 1 bei Abweichung)
"""
import re
import sys

_TOKEN = re.compile(r'(#[\w-]+)|(\.[\w-]+)|(\[[^\]]*\])'
                    r'|(::?[\w-]+(?=\())'           # Funktions-Pseudoklasse, Argument folgt
                    r'|(::?[\w-]+)|([a-zA-Z][\w-]*)|(\*)')


def _argument(text, i):
    r"""Das Argument einer Funktions-Pseudoklasse ab der offenen Klammer bei i.

    Rueckgabe (Inhalt, Index hinter der schliessenden Klammer). Mit Klammerzaehlung, weil
    ein Regex `\((.*?)\)` am ERSTEN `)` abschneidet: `:not(:is(.is-active))` wurde als
    `:not(":is(.is-active")` gelesen, das innere `:is` fiel in den Zweig fuer unbekannte
    Pseudoklassen und galt als "trifft nicht". Beide Richtungen kippten damit (R29):
    `.finder-step:not(:is(.is-active))` -- ein browseridentisches Refactoring -- ergab 14
    Fehler, und `.finder-step:is(:not(.gibtsnicht))` toetete den Finder bei gruenem Lauf.
    Auch die Spezifitaet war falsch, weil der unbekannte Rest zusaetzlich zaehlte.
    """
    tiefe, j = 0, i
    while j < len(text):
        if text[j] == '(':
            tiefe += 1
        elif text[j] == ')':
            tiefe -= 1
            if tiefe == 0:
                return text[i + 1:j], j + 1
        j += 1
    return text[i + 1:], len(text)      # unbalanciert: Rest als Argument


# Welche Pseudoklassen eine LISTE von Selektoren enthalten und wie sie zaehlen.
#   :not   trifft, wenn KEINE Alternative trifft; Spezifitaet die staerkste
#   :is    trifft, wenn EINE trifft; Spezifitaet die staerkste
#   :where wie :is, aber Spezifitaet NULL (so steht es in der CSS-Spezifikation)
# `:is()`, `:where()` und `:has()` galten vorher als "nicht treffend", begruendet mit
# `:hover` ("stellt der Leser erst her") -- fuer die drei gilt das nicht, sie sind im
# Ruhezustand unbedingt. `.finder-step:is(.is-active){display:none}` toetete den Finder
# und blieb gruen (R27).
_LISTEN_PS = {'not': ('negativ', True), 'is': ('positiv', True),
              'matches': ('positiv', True), 'any': ('positiv', True),
              'where': ('positiv', False)}

# Welcher Wert heisst "weg". `visibility` und `opacity` kamen auf Hinweis aus R24 dazu:
# Der DOM-Harness prueft sie inline schon, aus dem Stylesheet fehlten sie.
def _opak_null(v):
    """opacity als ZAHL lesen. Die Literal-Liste ('0','0.0','0%','.0') hat `0.00`,
    `0e0` und negative Werte durchgelassen (R26)."""
    v = v.strip().rstrip('%')
    try:
        return float(v) <= 0
    except ValueError:
        return False


WEG = {'display': lambda v: v == 'none',
       'visibility': lambda v: v in ('hidden', 'collapse'),
       'opacity': _opak_null}


def _trenne(text, zeichen):
    """Zerlegt an diesen Zeichen, aber nur AUSSERHALB von [] und ().

    Geteilt zwischen `teile()` (Kombinatoren) und der Selektorliste in `regeln()`. Die
    Liste wurde vorher mit `split(',')` zerlegt und damit auch INNERHALB von `:not(a, b)`
    -- der Auswertungszweig fuer Komma-Listen in `gruppe()` war ueber `wert()` nie
    erreichbar. Ergebnis war beides: `:not(.gibtsnicht, .auchnicht){display:none}` toetete
    den Finder bei gruenem Lauf, und das korrekte Refactoring mit zwei Argumenten ergab
    14 Fehler (R26).
    """
    aus, buf, tiefe = [], '', 0
    for ch in text:
        if ch in '[(':
            tiefe += 1
        elif ch in '])':
            tiefe = max(0, tiefe - 1)
        if tiefe == 0 and ch in zeichen:
            aus.append(buf)
            buf = ''
            continue
        buf += ch
    aus.append(buf)
    return [x for x in (y.strip() for y in aus) if x]


def teile(sel):
    """Zerlegt an Kombinatoren AUSSERHALB von [] und ().

    Die erste Fassung war `re.split(r'[\\s>+~]+', sel)` und hat damit `[class~="x"]`
    zerschnitten: `~` ist Kombinator UND Attribut-Operator. Das ergab ein Loch (die
    Regel fiel stumm weg) und einen Fehlalarm (eine Gruppe ohne lesbare Token galt als
    auf jedem Element treffend).
    """
    return _trenne(sel.strip(), ' \t\n>+~')


def _attr_trifft(at, attrs):
    """True/False, oder None wenn die Form nicht lesbar ist.

    Das `i`-Flag (`[data-step="0" i]`) kam auf Befund aus R26 dazu: Vorher lieferte die
    Form None, die Gruppe wurde unentscheidbar, die Regel uebersprungen -- das Gate fiel
    dort OFFEN aus, obwohl die Regel den Finder toetet.
    """
    m = re.match(r'\[\s*([\w-]+)\s*(?:([~^$*|]?=)\s*["\']?([^"\']*?)["\']?\s*)?'
                 r'(?:\s+([iIsS]))?\s*\]', at)
    if not m:
        return None
    n, op, v, flag = m.group(1), m.group(2), m.group(3), m.group(4)
    if n not in attrs:
        return False
    w = attrs[n]
    if op is None:
        return True
    if flag and flag.lower() == 'i':
        w, v = w.lower(), (v or '').lower()
    return {'=': w == v, '*=': v in w, '^=': w.startswith(v), '$=': w.endswith(v),
            '~=': v in w.split(), '|=': w == v or w.startswith(v + '-')}.get(op)


def gruppe(g, e):
    """(trifft?, (a, b, c)). trifft ist None, wenn die Gruppe nicht entscheidbar ist."""
    a = b = c = 0
    trifft, unklar, gesehen = True, False, False
    attrs = e.get('a') or {}
    klassen = set(e.get('c') or [])
    i = 0
    while i < len(g):
        m = _TOKEN.match(g, i)
        if not m:
            i += 1
            continue
        gesehen = True
        _id, _kl, _at, _fn, _ps, _tg, _st = m.groups()
        i = m.end()
        if _fn:
            # Funktions-Pseudoklasse: Argument mit Klammerzaehlung lesen.
            if i < len(g) and g[i] == '(':
                inner, i = _argument(g, i)
            else:
                inner = ''
            name = _fn.lstrip(':').lower()
            if name in _LISTEN_PS:
                art, zaehlt = _LISTEN_PS[name]
                stark, einer, alle_unklar = (0, 0, 0), False, False
                for teil in _trenne(inner, ','):
                    # selektor(), nicht gruppe(): Ein komplexes Argument wie
                    # `:not(.finder .is-active)` wurde sonst als VERBUND gelesen, also
                    # verlangte es beide Klassen am Element selbst (R27, Fehlalarm).
                    t2, s2 = selektor(teil, e)
                    if t2 is None:
                        alle_unklar = True
                    elif t2:
                        einer = True
                    stark = max(stark, s2)
                if zaehlt:
                    a, b, c = a + stark[0], b + stark[1], c + stark[2]
                if alle_unklar:
                    unklar = True
                elif (art == 'negativ') == einer:
                    trifft = False
            elif name == 'has':
                # :has() haengt am Teilbaum UNTER dem Element; die Kette liefert nur nach
                # oben. Unentscheidbar, und das wird gemeldet (siehe wert()).
                b += 1
                unklar = True
            else:
                b += 1
                trifft = False      # :nth-child() und Verwandte: siehe GRENZE
            continue
        if _id:
            a += 1
            if e.get('id') != _id[1:]:
                trifft = False
        elif _kl:
            b += 1
            if _kl[1:] not in klassen:
                trifft = False
        elif _at:
            b += 1
            r = _attr_trifft(_at, attrs)
            if r is None:
                unklar = True
            elif not r:
                trifft = False
        elif _ps:
            b += 1
            trifft = False      # siehe GRENZE im Modul-Docstring
        elif _tg:
            c += 1
            if (e.get('tag') or '').lower() != _tg.lower():
                trifft = False
        # * aendert nichts
    if not gesehen:
        return None, (0, 0, 0)
    # Ein BEWIESENER Nicht-Treffer schlaegt Unklarheit: `.irgendwas:has(.x)` trifft dieses
    # Element nachweislich nicht, weil die Klasse fehlt -- was im `:has()` steht, ist dann
    # gleichgueltig. Die erste Fassung gab `None` zurueck, sobald irgendein Teil unklar
    # war, und meldete damit jede `:has()`-Regel im Stylesheet als unentscheidbar, auch
    # die an fremden Elementen (R28, mein eigener Fehlalarm beim Schliessen von B28-1).
    if not trifft:
        return False, (a, b, c)
    if unklar:
        return None, (a, b, c)
    return True, (a, b, c)


def selektor(sel, e):
    """(trifft die LETZTE Gruppe?, Spezifitaet ueber ALLE Gruppen).

    Die Summe ueber alle Gruppen ist der Unterschied zu R25: Jedes Scoping-Praefix
    erhoeht im Browser das Gewicht, und die alte Fassung hat es ignoriert.
    """
    gr = teile(sel)
    if not gr:
        return None, (0, 0, 0)
    sa = sb = sc = 0
    for g in gr:
        _, (a, b, c) = gruppe(g, e)
        sa, sb, sc = sa + a, sb + b, sc + c
    t, _ = gruppe(gr[-1], e)
    return t, (sa, sb, sc)


def regeln(text, quelle, bedingung=''):
    r"""Alle Regeln als (Selektor-Text, Deklarationen, Quelle, Bedingung), At-Regeln mit.

    Der Block-Regex `([^{}]+)\{([^}]*)\}` kann nicht verschachteln: Der Rumpf eines
    `@media`-Blocks landete als Deklarationstext und fiel durch. Der Docstring behauptete
    deshalb lange, Regeln in `@media` wuerden "wie unbedingte gelesen" -- gemessen wurden
    sie GAR NICHT gelesen, das Gate fiel dort offen aus (R26: eine Regel in einem
    `@media (max-width:768px)` toetet den Finder auf jedem Handy, Lauf gruen; dasselbe mit
    `@supports`).

    Jetzt werden At-Regeln aufgeschnitten und ihr Inhalt mitgelesen, mit der Bedingung im
    Quellennamen. Das ist bewusst STRENG: Eine Regel, die den Finder in irgendeinem
    Viewport versteckt, wird gemeldet. Gemessen, bevor das scharf gestellt wurde:
    `style.css` fuehrt 12 At-Regel-Bloecke und darin 4 Finder-Regeln, keine davon mit
    `display`/`visibility`/`opacity` -- es entsteht also kein Fehlalarm im Bestand.
    """
    aus = []
    i = 0
    while True:
        m = re.search(r'@([\w-]+)([^{;]*)\{', text[i:])
        if not m:
            break
        kopf_bis = i + m.start()
        # Alles vor der At-Regel sind gewoehnliche Regeln.
        aus += [(s, d, quelle, bedingung)
                for s, d in re.findall(r'([^{}]+)\{([^}]*)\}', text[i:kopf_bis])]
        start = i + m.end()
        tiefe, j = 1, start
        while j < len(text) and tiefe:
            if text[j] == '{':
                tiefe += 1
            elif text[j] == '}':
                tiefe -= 1
            j += 1
        rumpf = text[start:j - 1]
        _at = '@' + m.group(1) + ' ' + m.group(2).strip()
        if m.group(1).lower() in ('media', 'supports', 'layer', 'container', 'scope'):
            aus += regeln(rumpf, quelle, (bedingung + ' ' + _at).strip())
        # @keyframes, @font-face usw. tragen keine Selektoren fuer Elemente.
        i = j
    aus += [(s, d, quelle, bedingung)
            for s, d in re.findall(r'([^{}]+)\{([^}]*)\}', text[i:])]
    return aus


def wert(quellen, element, eigenschaft):
    """(geltender Wert, unentscheidbare Regeln). Der Wert ist None, wenn keine greift.

    Reihenfolge: `!important` schlaegt alles ohne; dann hoehere Spezifitaet; bei
    gleicher die spaetere Regel.

    Der ZWEITE Rueckgabewert ist neu und der Grund dafuer steht in R28: `:has()` wurde
    intern als unentscheidbar markiert, und `wert()` hat die Regel danach mit
    `if not t: continue` weggeworfen -- also genau so behandelt wie "trifft nicht". Der
    Kommentar daneben behauptete "wird gemeldet". Eine Regel, die den Finder toetet,
    verschwand lautlos. Unentscheidbares muss beim Aufrufer ankommen, sonst ist die
    Markierung eine Behauptung.

    Eigenschaftsname und `!important` werden ohne Ruecksicht auf Gross- und
    Kleinschreibung gelesen.
    """
    best = None
    lauf = 0
    unklar = []
    for name, text in quellen:
        text = re.sub(r'/\*.*?\*/', ' ', text, flags=re.S)
        for sel_text, dekl, quelle, bedingung in regeln(text, name):
            # Die LETZTE Deklaration im Block gewinnt, wie im Browser -- und ein
            # `!important` darin schlaegt jede spaetere ohne. Die erste Fassung nahm
            # `re.search`, also die erste Deklaration: `{display:block;display:none}` war
            # ein Loch und `{display:none;display:block}` ein Fehlalarm (R27). Die zweite
            # Fassung nahm `finditer` ueber dasselbe Muster -- Treffer koennen sich nicht
            # ueberlappen, und das `;` gehoerte schon zum ersten, also fand sie wieder nur
            # einen. Deshalb wird am Semikolon ZERLEGT.
            _treffer = []
            for _stueck in dekl.split(';'):
                _em = re.match(r'\s*' + eigenschaft + r'\s*:\s*([^!]+?)\s*'
                               r'(!\s*important)?\s*$', _stueck, re.I)
                if _em:
                    _treffer.append(_em)
            if not _treffer:
                continue
            dm = next((x for x in reversed(_treffer) if x.group(2)), _treffer[-1])
            for sel in _trenne(sel_text, ','):
                lauf += 1
                t, spez = selektor(sel, element)
                _wo = quelle + (f' in {bedingung}' if bedingung else '')
                if t is None:
                    # Nicht entscheidbar -- MIT Sortierschluessel, damit der Aufrufer
                    # erkennt, ob die Regel ueberhaupt gewinnen koennte.
                    unklar.append(((1 if dm.group(2) else 0, spez, lauf),
                                   dm.group(1).strip(), _wo, sel.strip()))
                    continue
                if not t:
                    continue
                schl = (1 if dm.group(2) else 0, spez, lauf)
                if best is None or schl > best[0]:
                    best = (schl, dm.group(1).strip(), _wo, sel.strip())
    # Unentscheidbares, das gegen den Sieger ohnehin verliert, ist bedeutungslos: Eine
    # `:has()`-Regel ohne `!important` kann ein `display:block!important` nicht kippen.
    # Die erste Fassung meldete sie trotzdem und erklaerte ein sichtbares Element fuer
    # nicht zusicherbar (R29) -- dieselbe Regel wie in `gruppe()`, eine Ebene hoeher
    # vergessen.
    _schl_best = best[0] if best else (-1, (-1, -1, -1), -1)
    _offen = [(w, q, s) for (k, w, q, s) in unklar if k > _schl_best]
    return (None if best is None else (best[1], best[2], best[3])), _offen


def sichtbar(quellen, element, zusatz_klassen=()):
    """(sichtbar?, Grund) -- prueft alle drei Eigenschaften.

    Grund ist (Ursache, Quelle, Selektor) bei "versteckt", oder
    ('unentscheidbar', Quelle, Selektor) wenn eine Regel nicht beurteilbar ist. Letzteres
    ist AUCH ein "nicht sichtbar": Das Gate kann dann nichts zusichern, und das gehoert
    gemeldet statt verschwiegen (R28).
    """
    e = dict(element)
    e['c'] = sorted(set(element.get('c') or []) | set(zusatz_klassen))
    for eig, ist_weg in WEG.items():
        d, offen = wert(quellen, e, eig)
        _weg_sonst = bool(d) and ist_weg(d[0].strip().lower())
        # Eine unentscheidbare Regel wird nur gemeldet, wenn sie das ERGEBNIS aendern
        # koennte. Sagt sie dasselbe wie die geltende Regel, ist sie bedeutungslos: Eine
        # `:has()`-Regel mit `display:none` neben einem schon geltenden `display:none`
        # kippt nichts. Die erste Fassung meldete sie trotzdem und machte damit einen
        # legitimen Fall rot (R29, eigene Probe).
        for _w, _q, _s in offen:
            if ist_weg(_w.strip().lower()) != _weg_sonst:
                return False, (f'{eig}: nicht entscheidbar ({_w})', _q, _s)
        if _weg_sonst:
            return False, (f'{eig}: {d[0].strip()}', d[1], d[2])
    return True, None


# ---------------------------------------------------------------------------------------
# FALLTABELLE. Jede Form, die eine Pruefrunde gefunden hat, steht hier -- auch die, die
# TREFFEN MUSS und die, die NICHT treffen darf. Ein Gate mit Loch und Fehlalarm hat die
# falsche Regel; beide Richtungen gehoeren deshalb in denselben Test.
# ---------------------------------------------------------------------------------------
_AKTIV = {'c': ['finder-step', 'is-active'], 'id': None, 'tag': 'div',
          'a': {'class': 'finder-step is-active', 'data-step': '0'}}
_INAKTIV = {'c': ['finder-step'], 'id': None, 'tag': 'div',
            'a': {'class': 'finder-step', 'data-step': '1'}}
_FINDER = {'c': ['finder'], 'id': 'finder', 'tag': 'div',
           'a': {'class': 'finder', 'id': 'finder'}}
_ERGEBNIS = {'c': ['finder-result'], 'id': None, 'tag': 'div',
             'a': {'class': 'finder-result', 'data-step': 'result'}}

FAELLE = [
    ('.finder-step', _AKTIV, True, (0, 1, 0)),
    ('.finder-step.is-active', _AKTIV, True, (0, 2, 0)),
    ('.finder-step.is-active', _INAKTIV, False, (0, 2, 0)),
    ('.finder .finder-step', _AKTIV, True, (0, 2, 0)),              # R25 B25-1a
    ('#finder .finder-step', _AKTIV, True, (1, 1, 0)),              # R25 B25-1b
    ('#finder .finder-step.is-active', _AKTIV, True, (1, 2, 0)),
    ('.finder > .finder-step', _AKTIV, True, (0, 2, 0)),
    ('div.finder-step', _AKTIV, True, (0, 1, 1)),
    ('.finder-step[data-step]', _AKTIV, True, (0, 2, 0)),           # R24
    ('.finder-step[data-step="0"]', _AKTIV, True, (0, 2, 0)),
    ('.finder-step[data-step="9"]', _AKTIV, False, (0, 2, 0)),
    ('[class~="finder-step"][data-step]', _AKTIV, True, (0, 2, 0)),  # R25 B25-2 Loch
    ('[class~="finder-step"]', _AKTIV, True, (0, 1, 0)),
    ('.finder-step[data-step~="0"]', _AKTIV, True, (0, 2, 0)),      # R25 B25-2 Fehlalarm
    ('.finder-step:not(.is-active)', _AKTIV, False, (0, 2, 0)),     # R25 B25-3
    ('.finder-step:not(.is-active)', _INAKTIV, True, (0, 2, 0)),
    ('.finder-step:not(.x)', _AKTIV, True, (0, 2, 0)),
    ('.finder-step.is-active:not(.x)', _AKTIV, True, (0, 3, 0)),
    ('.finder-result[id]', _ERGEBNIS, False, (0, 2, 0)),            # trifft nichts
    ('.finder-step:hover', _AKTIV, False, (0, 2, 0)),
    # R27: :is()/:where()/:matches() positiv, :where() ohne Spezifitaet, und :not() mit
    # komplexem Argument (vorher ein Fehlalarm, weil es als Verbund gelesen wurde).
    ('.finder-step:is(.is-active)', _AKTIV, True, (0, 2, 0)),
    ('.finder-step:is(.is-active)', _INAKTIV, False, (0, 2, 0)),
    ('.finder-step:is(.a, .is-active)', _AKTIV, True, (0, 2, 0)),
    ('.finder-step:is(.a, .b)', _AKTIV, False, (0, 2, 0)),
    ('.finder-step:where(.is-active)', _AKTIV, True, (0, 1, 0)),
    ('.finder-step:not(.finder .is-active)', _AKTIV, False, (0, 3, 0)),
    ('.finder-step:not(.finder .gibtsnicht)', _AKTIV, True, (0, 3, 0)),
    # R29: verschachtelte Funktions-Pseudoklassen. Der Regex schnitt am ersten `)` ab,
    # beide Richtungen kippten, und die Spezifitaet war zu hoch.
    ('.finder-step:not(:is(.is-active))', _AKTIV, False, (0, 2, 0)),
    ('.finder-step:not(:is(.is-active))', _INAKTIV, True, (0, 2, 0)),
    ('.finder-step:is(:not(.gibtsnicht))', _AKTIV, True, (0, 2, 0)),
    ('.finder-step:is(:not(.is-active))', _AKTIV, False, (0, 2, 0)),
    ('.finder-step:where(:is(.is-active))', _AKTIV, True, (0, 1, 0)),
    ('.finder-step:not(:is(.a, .b))', _AKTIV, True, (0, 2, 0)),
    ('.finder-step:has(:is(.x))', _AKTIV, None, (0, 2, 0)),
    ('div', _FINDER, True, (0, 0, 1)),
    ('#finder div', _FINDER, True, (1, 0, 1)),
    ('.finder', _FINDER, True, (0, 1, 0)),
    ('button', _AKTIV, False, (0, 0, 1)),
    ('*', _AKTIV, True, (0, 0, 0)),
]

# Kaskaden-Faelle: (Name, CSS, Element, Zusatzklassen, soll_sichtbar)
_BASIS = ('.finder-step, .finder-result { display: none; }\n'
          '.finder-step.is-active, .finder-result.is-active { display: block; }\n')
KASKADE = [
    ('Basis, aktiv', _BASIS, _AKTIV, (), True),
    ('Basis, inaktiv', _BASIS, _INAKTIV, (), False),
    ('Regeln vertauscht (Spezifitaet entscheidet)',
     '.finder-step.is-active, .finder-result.is-active { display: block; }\n'
     '.finder-step, .finder-result { display: none; }\n', _AKTIV, (), True),
    ('Klassen-Nachfahre angehaengt', _BASIS + '.finder .finder-step{display:none}\n',
     _AKTIV, (), False),
    ('ID-Nachfahre angehaengt', _BASIS + '#finder .finder-step{display:none}\n',
     _AKTIV, (), False),
    ('Attribut-Verbund angehaengt', _BASIS + '.finder-step[data-step]{display:none}\n',
     _AKTIV, (), False),
    ('class~-Verbund angehaengt',
     _BASIS + '[class~="finder-step"][data-step]{display:none}\n', _AKTIV, (), False),
    ('nur class~ (verliert)', _BASIS + '[class~="finder-step"]{display:none}\n',
     _AKTIV, (), True),
    (':not()-Fassung statt der Basis',
     '.finder-step:not(.is-active), .finder-result:not(.is-active){display:none}\n',
     _AKTIV, (), True),
    (':not()-Fassung, inaktiv',
     '.finder-step:not(.is-active), .finder-result:not(.is-active){display:none}\n',
     _INAKTIV, (), False),
    ('!important davor', '.finder-step{display:none!important}\n' + _BASIS, _AKTIV, (), False),
    (':is() versteckt', _BASIS + '.finder-step:is(.is-active){display:none}\n',
     _AKTIV, (), False),
    (':where() versteckt (verliert an Spezifitaet)',
     _BASIS + '.finder-step:where(.is-active){display:none}\n', _AKTIV, (), True),
    (':not() mit Nachfahre innen, trifft nicht',
     _BASIS + '.finder-step:not(.finder .is-active){display:none}\n', _AKTIV, (), True),
    # R26: sieben Formen, die alle den Finder toeten und alle gruen blieben.
    (':not() mit Komma-Liste, trifft',
     _BASIS + '.finder-step:not(.gibtsnicht, .auchnicht){display:none}\n', _AKTIV, (), False),
    (':not() mit Komma-Liste, trifft nicht',
     '.finder-step:not(.is-active, .is-done), .finder-result:not(.is-active, .is-done)'
     '{display:none}\n', _AKTIV, (), True),
    ('Regel in @media', _BASIS + '@media (max-width:768px){.finder-step.is-active'
     '{display:none}}\n', _AKTIV, (), False),
    ('Regel in @supports', _BASIS + '@supports (display:grid){.finder-step.is-active'
     '{display:none}}\n', _AKTIV, (), False),
    ('Regel in @media, trifft nicht', _BASIS + '@media print{.irgendwas{display:none}}\n',
     _AKTIV, (), True),
    ('!IMPORTANT gross', '.finder-step{display:none !IMPORTANT}\n' + _BASIS, _AKTIV, (), False),
    ('Eigenschaftsname gross', _BASIS + '#finder .finder-step{Display:none}\n',
     _AKTIV, (), False),
    ('opacity 0.00', _BASIS + '.finder{opacity:0.00}\n', _FINDER, (), False),
    ('opacity 0e0', _BASIS + '.finder{opacity:0e0}\n', _FINDER, (), False),
    ('opacity 1 (sichtbar)', _BASIS + '.finder{opacity:1}\n', _FINDER, (), True),
    ('Attribut mit i-Flag', _BASIS + '.finder-step[data-step="0" i]{display:none}\n',
     _AKTIV, (), False),
    ('Attribut mit i-Flag, trifft nicht',
     _BASIS + '.finder-step[data-step="9" i]{display:none}\n', _AKTIV, (), True),
    ('visibility aus dem Stylesheet', _BASIS + '.finder{visibility:hidden}\n', _FINDER, (), False),
    ('opacity 0 aus dem Stylesheet', _BASIS + '.finder{opacity:0}\n', _FINDER, (), False),
    ('Tag-Selektor', _BASIS + 'div{display:none}\n', _FINDER, (), False),
    ('unbeteiligte Regel', _BASIS + '.irgendwas{display:none}\n', _AKTIV, (), True),
    # R28: :has() ist nicht entscheidbar und MUSS gemeldet werden -- vorher wurde die
    # Regel stillschweigend verworfen, also wie "trifft nicht" behandelt.
    (':has() am aktiven Schritt', _BASIS + '.finder-step.is-active:has(.x){display:none}\n',
     _AKTIV, (), False),
    (':has() am Container', _BASIS + '#finder:has(.x){display:none}\n', _FINDER, (), False),
    ('verschachteltes :not(:is()) versteckt',
     _BASIS + '.finder-step:is(:not(.gibtsnicht)){display:none}\n', _AKTIV, (), False),
    ('verschachteltes :not(:is()) als Refactoring (kein Alarm)',
     '.finder-step:not(:is(.is-active)), .finder-result:not(:is(.is-active))'
     '{display:none}\n.finder-step.is-active, .finder-result.is-active{display:block}\n',
     _AKTIV, (), True),
    (':has() verliert gegen !important (kein Alarm)',
     '.finder-step, .finder-result{display:none}\n'
     '.finder-step:has(.x){display:none}\n'
     '.finder-step.is-active{display:block!important}\n', _AKTIV, (), True),
    (':has() mit !important gewinnt (Alarm)',
     '.finder-step, .finder-result{display:none}\n'
     '.finder-step.is-active{display:block}\n'
     '.finder-step:has(.x){display:none!important}\n', _AKTIV, (), False),
    (':has() sagt dasselbe wie die geltende Regel (kein Alarm)',
     '.finder-step, .finder-result{display:none}\n'
     '.finder-step:has(.x){display:none}\n'
     '.finder-step.is-active{display:block!important}\n', _INAKTIV, (), False),
    (':has() an einem fremden Element (kein Alarm)',
     _BASIS + '.irgendwas:has(.x){display:none}\n', _AKTIV, (), True),
    ('zwei Deklarationen, none zuletzt',
     _BASIS + '.finder-step.is-active{display:block;display:none}\n', _AKTIV, (), False),
    ('zwei Deklarationen, block zuletzt',
     '.finder-step{display:none}\n'
     '.finder-step.is-active{display:none;display:block}\n', _AKTIV, (), True),
    ('!important vor spaeterer Deklaration',
     _BASIS + '.finder-step.is-active{display:none!important;display:block}\n',
     _AKTIV, (), False),
    ('flex statt block',
     '.finder-step, .finder-result { display: none; }\n'
     '.finder-step.is-active{display:flex}\n', _AKTIV, (), True),
]


def selbsttest():
    falsch = 0
    for sel, el, st, ss in FAELLE:
        t, s = selektor(sel, el)
        if (t, s) != (st, ss):
            falsch += 1
            print(f'>>> {sel:38s} trifft={t} spez={s} (soll {st}, {ss})')
    for name, css, el, zus, soll in KASKADE:
        ok, grund = sichtbar([('probe', css)], el, zus)
        if ok != soll:
            falsch += 1
            print(f'>>> {name:44s} sichtbar={ok} (soll {soll}) {grund}')
    print(f'{len(FAELLE)} Selektor-Faelle + {len(KASKADE)} Kaskaden-Faelle, {falsch} falsch')
    return 1 if falsch else 0


if __name__ == '__main__':
    sys.exit(selbsttest())
