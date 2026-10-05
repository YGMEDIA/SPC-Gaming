#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setzt die B11-Positionierung auf Startseite, /ueber-uns/ und /redaktion/.

Drei handgepflegte Seiten, keine davon generiert: Deshalb gibt es hier nur den Sync und
keinen Generator-Zwilling wie bei B1, B7 und B10. Die Regel steht in positionierung.py,
die Zahlen kommen aus den Regeln, die sie besitzen.

Aufruf:  python3 scripts/sync_positionierung.py
         python3 scripts/sync_positionierung.py --check   (nur melden, nichts schreiben)
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
os.chdir(ROOT)

from gen_hubs import esc
from positionierung import (MARKER, SEITEN, block, fakten, html_methode, html_start,
                            laden)

# Je Seite: der Anker und ob der Block DAVOR oder DAHINTER gehoert.
# Startseite: vor den Emotions-Abschnitt, also direkt hinter das Versprechen-Band. Die
# Positionierung beantwortet "warum hier und nicht dort" und gehoert damit vor das erste
# inhaltliche Argument, nicht hinter die Produktliste.
# Methodenseiten: hinter die Ueberschrift, an die Stelle des Absatzes, der dort die
# All-Aussage trug.
ANKER = {
    'index.html': ('<!-- Emotions- & Problem→Lösung-Abschnitt -->', 'davor'),
    'ueber-uns/index.html': ('<h2 style="margin-top:32px">Wie wir testen</h2>', 'dahinter'),
    'redaktion/index.html': ('<h2 style="margin-top:24px">Unser Testprozess</h2>', 'dahinter'),
}

ANF, END = f'<!-- {MARKER}:START -->', f'<!-- {MARKER}:END -->'

# Entfernen und Einsetzen sind EIN Paar, und das Paar haengt an der Richtung. Steht der
# Block vor dem Anker, traegt er die Einrueckung des Ankers vor sich her; das Entfernen
# muss sie mitnehmen, sonst waechst die Datei bei jedem Lauf um eine eingerueckte
# Leerzeile. Steht er dahinter, ist es genau umgekehrt: Dann gehoert der Zeilenumbruch
# DAVOR zum Block. Zwei Richtungen, zwei Paare, beide hier nebeneinander -- die
# Idempotenzprobe faehrt jedes Sync-Skript drei Mal und haelt das fest.
MUSTER = {
    'davor': (rf'{re.escape(ANF)}.*?{re.escape(END)}\n?\s*', '\n\n    '),
    'dahinter': (rf'\n?{re.escape(ANF)}.*?{re.escape(END)}', '\n'),
}


def entferne(s, wohin):
    return re.sub(MUSTER[wohin][0], '', s, flags=re.S)


def main():
    nur_pruefen = '--check' in sys.argv
    items = laden()
    f = fakten(items)
    geaendert, befunde = 0, []

    for datei, art in SEITEN:
        if not os.path.exists(datei):
            befunde.append(f'{datei}: Seite fehlt')
            continue
        s = open(datei, encoding='utf-8').read()
        inhalt = (html_start if art == 'start' else html_methode)(f, esc)
        if not inhalt:
            befunde.append(f'{datei}: die Regel liefert keinen Inhalt — dann stimmt eine '
                           f'der Zahlen nicht (Fakten: {f})')
            continue
        anker, wohin = ANKER[datei]
        ohne = entferne(s, wohin)
        if ohne.count(anker) != 1:
            befunde.append(f'{datei}: Anker kommt {ohne.count(anker)}x vor, erwartet '
                           f'genau 1 — {anker[:60]}')
            continue
        fuge = MUSTER[wohin][1]
        neu = (ohne.replace(anker, block(inhalt) + fuge + anker, 1) if wohin == 'davor'
               else ohne.replace(anker, anker + fuge + block(inhalt), 1))
        if neu != s:
            geaendert += 1
            if not nur_pruefen:
                open(datei, 'w', encoding='utf-8').write(neu)
            print(f'  {"wuerde geaendert" if nur_pruefen else "gesetzt"}: {datei}')

    for b in befunde:
        print(f'  FEHLER: {b}')
    print(f'\n{len(SEITEN)} Positionierungs-Seiten, '
          f'{geaendert} {"abweichend" if nur_pruefen else "geschrieben"}, '
          f'{len(befunde)} Befund(e)')
    if befunde:
        return 1
    if nur_pruefen and geaendert:
        print('  Fix: python3 scripts/sync_positionierung.py')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
