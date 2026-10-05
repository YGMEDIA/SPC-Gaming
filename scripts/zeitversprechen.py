#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B12: Das Zeitversprechen zum Finder hat EINE Quelle und sieben Schreibstellen.

WARUM NICHT ALS HEURISTIK
Die erste Fassung suchte repoweit nach "N Sekunden" und entschied am Umfeld (45 Zeichen
um die Zahl, Stichwoerter Finder/Fragen/Ergebnis/Empfehlung/Wahl), ob die Stelle eine
Finder-Zusage ist. Der Pruefer hat beide Richtungen zerlegt:

  LOCH       "in zwei Minuten", "in 90 s", "in neunzig Sekunden", Zusage ganz entfernt,
             Kachel durch "kostenlos" ersetzt -- fuenf Ein-Zeilen-Mutationen, alle exit 0,
             weil die uebrigen Stellen weiter 60 sagten. Und eine ZUSAETZLICHE Zusage
             ("Plane dafuer rund 90 Sekunden ein") auf der Finder-Seite selbst, deren
             Umfeld zufaellig kein Stichwort enthielt.
  FEHLALARM  "Nach 20 Sekunden blinkt die LED, dann ist die Wahl des Modus wieder frei"
             in einem Fehlersuche-Artikel wurde als Finder-Zusage gemeldet. "Wahl",
             "Fragen", "Ergebnis" sind Alltagswoerter, und das Fenster laeuft ueber
             Blockgrenzen (es muss, sonst findet es die Kachel "60 Sek. | bis zum
             Ergebnis" nicht).

Beides faellt weg, sobald die Zahl nicht mehr erraten, sondern gepflegt wird: Hier steht
sie einmal, `sync_zeitversprechen.py` schreibt sie an die sieben bekannten Stellen, und
verify.py vergleicht zeichengleich. Das ist P-13 Mechanismus 1 (eine Regel, von allen
benutzt) statt einer Mustersuche -- und P-13 Mechanismus 25 (die Pflicht gilt der MENGE):
Fehlt eine der sieben Stellen, wird der Lauf rot, statt dass die uebrigen sechs sie decken.

WAS NICHT GEPRUEFT WIRD
Ob 60 Sekunden stimmen. Das kann kein Gate, und der Leser misst es in 60 Sekunden selbst
nach. Geprueft wird, dass die Site EIN Versprechen macht und nicht zwei.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

SEKUNDEN = 60

START = 'index.html'
FINDER = 'controller-finder/index.html'
ERKLAERER = 'blog/was-ist-ein-smartphone-controller/index.html'

# Je Stelle: Datei · Muster mit der Zahl in Gruppe 1 · Beschreibung fuer die Meldung.
# Jedes Muster MUSS in seiner Datei genau einmal passen; passt es nicht, ist die Zusage
# entfernt oder umformuliert worden, und dann gehoert die neue Fassung hierher.
STELLEN = (
    (START, re.compile(r'(?<=damit du in )(\d+)(?= Sekunden die richtige Wahl)'),
     'Startseiten-Hero'),
    (START, re.compile(r'(?<=<div class="num">)(\d+)(?= Sek\.</div>)'),
     'Kachel im Finder-Teaser der Startseite'),
    (FINDER, re.compile(r'(?<=du hast die Antwort in )(\d+)(?= Sekunden)'),
     'Finder-Seite, Aufforderung'),
    (FINDER, re.compile(r'(?<=name="description" content="Controller finden in )(\d+)'
                        r'(?= Sekunden)'), 'Meta-Description der Finder-Seite'),
    (FINDER, re.compile(r'(?<=property="og:description" content="Controller finden in )'
                        r'(\d+)(?= Sekunden)'), 'og:description der Finder-Seite'),
    (FINDER, re.compile(r'(?<=name="twitter:description" content="Controller finden in )'
                        r'(\d+)(?= Sekunden)'), 'twitter:description der Finder-Seite'),
    (ERKLAERER, re.compile(r'(?<=Fragen, )(\d+)(?= Sekunden, personalisierte Empfehlung)'),
     'Finder-Hinweis im Erklaerer-Artikel'),
)

# Auf diesen zwei Seiten ist JEDE Sekundenangabe eine Finder-Zusage. Das ist die enge
# Fassung der alten Heuristik: Sie gilt nur dort, wo es heute keine andere Sekundenangabe
# gibt und auch keine hingehoert, und sie faengt damit die eine Form, die eine Liste
# bekannter Stellen nicht faengt -- eine ZUSAETZLICHE Zusage daneben.
SWEEP = (START, FINDER)
DAUER = re.compile(r'(\d+)\s*(?:Sekunden\b|Sek\.)')
# Benannte Ausnahmen fuer den Sweep: eine sichtbare Sekundenangabe auf einer der zwei
# Seiten, die KEINE Finder-Zusage ist. Heute leer, und das ist die Aussage -- auf diesen
# zwei Seiten steht heute keine andere Zeitangabe. Wer eine braucht (ein Kuehler, der in
# 30 Sekunden kuehlt), traegt sie hier ein, statt sie in STELLEN zu setzen: Dort wuerde
# der Sync sie mit der Finder-Zahl ueberschreiben.
AUSNAHMEN = ()


def stellen_je_datei():
    aus = {}
    for datei, muster, was in STELLEN:
        aus.setdefault(datei, []).append((muster, was))
    return aus


def pruefe(datei, text):
    """(Befunde, gefundene Spannen) fuer eine Datei. Befund = Text einer Meldung."""
    befunde, spannen = [], []
    for muster, was in stellen_je_datei().get(datei, ()):
        treffer = list(muster.finditer(text))
        if len(treffer) != 1:
            befunde.append(f'{datei}: die Zusage "{was}" passt {len(treffer)}x, erwartet '
                           f'genau 1 — entfernt oder umformuliert. Dann gehoert die neue '
                           f'Fassung in STELLEN in scripts/zeitversprechen.py')
            continue
        spannen.append(treffer[0].span())
        if int(treffer[0].group(1)) != SEKUNDEN:
            befunde.append(f'{datei}: "{was}" verspricht {treffer[0].group(1)} Sekunden, '
                           f'die Quelle sagt {SEKUNDEN}')
    if datei in SWEEP:
        # Die gepflegten Zahlen werden ausgeblendet, dann faellt Unsichtbares weg:
        # Ein Kommentar `<!-- Teaser-Rotation: 30 Sekunden -->` und ein `const T=8; /* 8
        # Sekunden */` im Script wurden sonst als Zusage gemeldet. Beides sieht kein
        # Leser, und die Meldung haette zum Eintragen geraten -- fuer einen Kommentar
        # falsch. Jedes andere Text-Gate dieses Repos raeumt vorher auf, dieses nicht.
        _blind = list(text)
        for a, b in spannen:
            _blind[a:b] = ' ' * (b - a)
        _rein = re.sub(r'<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->', ' ',
                       ''.join(_blind), flags=re.S)
        for m in DAUER.finditer(_rein):
            if any(a in _rein[max(0, m.start() - 60):m.end() + 60] for a in AUSNAHMEN):
                continue
            befunde.append(f'{datei}: zusaetzliche Zeitangabe "{m.group(0)}" ausserhalb '
                           f'der gepflegten Zusagen. Auf dieser Seite ist jede sichtbare '
                           f'Sekundenangabe ein Finder-Versprechen. Drei Wege: als Stelle '
                           f'in STELLEN eintragen (dann schreibt der Sync die gepflegte '
                           f'Zahl hinein, was fuer eine FREMDE Zeitangabe falsch waere), '
                           f'die Angabe weglassen, oder sie in AUSNAHMEN aufnehmen')
    return befunde, spannen


def setze(datei, text):
    """Die gepflegte Zahl an allen Stellen dieser Datei einsetzen."""
    for muster, _ in stellen_je_datei().get(datei, ()):
        text = muster.sub(str(SEKUNDEN), text, count=1)
    return text
