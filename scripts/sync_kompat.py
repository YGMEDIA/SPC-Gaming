#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Setzt die Kompatibilitaets-Antwort (B1) in die handgepflegten Review-Seiten.

Die 29 generierten /produkte/-Seiten bekommen den Block von gen_pages.py. Die 13
handgepflegten Review-Seiten unter /controller/ haben keinen Generator — ohne dieses
Script muesste man den Block dort von Hand pflegen, und damit waere er genau die Sorte
Handtext, die diese Session reihenweise veraltet vorgefunden hat.

Beide Wege ziehen den Inhalt aus derselben Funktion (scripts/kompat.py) und escapen mit
derselben Regel. Marker-Idempotenz wie bei gen_hubs: erst den Block frueherer Laeufe
entfernen, dann neu setzen.

Aufruf:  python3 scripts/sync_kompat.py
         python3 scripts/sync_kompat.py --check   (nur melden, nichts schreiben)
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
os.chdir(ROOT)

from gen_hubs import esc          # dieselbe Escaping-Regel wie der Karten-Generator
from kompat import kompat_html    # dieselbe Quelle wie gen_pages.py

MARKER = 'KOMPAT'
# Vor der Einordnungs-Box: Das ist die erste inhaltliche Aussage der Seite, und genau
# dorthin gehoert die Antwort laut Massnahme B1 ("ganz nach oben"). Der Anker steht auf
# allen 13 Seiten, geprueft am 01.10.2026.
ANKER = '<div class="verdict-box">'


def block(inhalt):
    return f'<!-- {MARKER}:START -->\n{inhalt}\n<!-- {MARKER}:END -->\n          '


def entferne(s):
    return re.sub(rf'<!-- {MARKER}:START -->.*?<!-- {MARKER}:END -->\n?\s*', '', s, flags=re.S)


def main():
    nur_pruefen = '--check' in sys.argv
    items = json.load(open('assets/data/products.json', encoding='utf-8'))
    geaendert, ohne_block, fehlender_anker = 0, [], []

    for p in items:
        detail = (p.get('detail') or '').strip('/')
        # Nur die handgepflegten Seiten: /produkte/ baut gen_pages.py.
        if not detail or detail.startswith('produkte/'):
            continue
        f = detail + '/index.html'
        if not os.path.exists(f):
            continue
        inhalt = kompat_html(p, esc)
        if not inhalt:
            ohne_block.append(p['slug'])
            continue
        s = open(f, encoding='utf-8').read()
        neu = entferne(s)
        if ANKER not in neu:
            fehlender_anker.append(f)
            continue
        neu = neu.replace(ANKER, block(inhalt) + ANKER, 1)
        if neu != s:
            geaendert += 1
            if not nur_pruefen:
                open(f, 'w', encoding='utf-8').write(neu)
            print(f"  {'wuerde geaendert' if nur_pruefen else 'gesetzt'}: {f}")

    for f in fehlender_anker:
        print(f'  FEHLER: Anker "{ANKER}" fehlt in {f}')
    if ohne_block:
        print(f'  ohne Block (Daten geben nichts her): {", ".join(ohne_block)}')
    print(f"\n{geaendert} Datei(en) {'waeren geaendert' if nur_pruefen else 'geaendert'}")
    return 1 if (fehlender_anker or (nur_pruefen and geaendert)) else 0


if __name__ == '__main__':
    sys.exit(main())
