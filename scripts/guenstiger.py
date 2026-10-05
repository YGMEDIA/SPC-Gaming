#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B10: Wo das teurere Modell schlechter bewertet ist, steht das auf seiner Seite.

DIE ANNAHME, DIE GEBROCHEN WIRD
"Teurer ist besser" ist die stillste Annahme beim Controller-Kauf, und sie ist am
staerksten genau dann, wenn der Leser vor dem teuren Modell steht. Heath (Made to Stick)
nennt das Unerwartete als das, was haengenbleibt: Eine Information, die eine Erwartung
bricht, wird gelesen; eine, die sie bestaetigt, wird ueberblaettert.

GEMESSEN AM 05.10.2026 ueber die 28 Controller mit Preis und Bewertung:
  Sechs Produkte haben ein GUENSTIGERES Geschwister DERSELBEN MARKE mit BESSERER
  Bewertung. Keine einzige ihrer Seiten sagte das:
    Razer Kishi V3 Pro      152 €  4,2   <--  Kishi V3              88 €  4,4
    GameSir G8 Plus          76 €  4,1   <--  X5 Lite               45 €  4,2
    Backbone One PlayStation 76 €  4,1   <--  Backbone One (2. Gen) 63 €  4,3
    GameSir X2s Bluetooth    53 €  3,9   <--  X5 Lite               45 €  4,2
    8BitDo Ultimate Mobile   45 €  4,3   <--  Ultimate 2C Wired     30 €  4,6
    Mars Gaming MGPX         34 €  4,1   <--  MGP-BT2               30 €  4,2
  Vier der sechs nannten das guenstigere Modell irgendwo im Text, keine sagte, dass es
  BESSER BEWERTET ist. Die Daten lagen also vor, die Ueberraschung nicht.

WARUM DIESELBE MARKE
Ein markenuebergreifender Vergleich ("dieser 152-Euro-Razer ist schlechter bewertet als
ein 30-Euro-8BitDo") waere zwar wahr, aber kein Vergleich: Andere Bauform, andere
Plattform, anderer Zweck. Innerhalb einer Marke faellt das weg -- derselbe Hersteller,
dieselbe Linie, und der Leser steht wirklich vor der Wahl zwischen diesen zwei. Deshalb
ist die Regel eng, und sie liefert lieber nichts als einen schiefen Vergleich.

Gewaehlt wird das GUENSTIGSTE passende Geschwister: Wer den Hinweis liest, soll den
groessten Preisunterschied sehen, nicht den kleinsten.

Verwendet von gen_pages.py (die 29 generierten Seiten) und sync_guenstiger.py (die 13
handgepflegten Reviews) -- eine Quelle fuer beide, wie bei kompat.py.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from produktdaten import (A6_SCHWELLE, bewertung, preis_zahl, text as pfeld,
                          sterne_text, anzahl_text)
from hublinks import taxonomie_karte

MARKER = 'GUENSTIGER'


_KARTE = None


def _kategorien(detail):
    """Die Uebersichtsseiten, die dieses Produkt fuehren (B7/P-15, eine Quelle)."""
    global _KARTE
    if _KARTE is None:
        _KARTE = taxonomie_karte()[0]
    return {u for u, _ in _KARTE.get((detail or '').rstrip('/'), [])}


def finden(p, items):
    """Das guenstigste Geschwister DERSELBEN KATEGORIE und Marke, billiger UND besser.

    Gibt None zurueck, wenn es keines gibt -- und das ist der Normalfall. Ein Hinweis,
    der auf jeder Seite stuende, waere keiner.

    "Dieselbe Kategorie" heisst: beide stehen auf mindestens einer gemeinsamen
    Uebersichtsseite (dieselbe Ableitung wie der Rueckweg aus B7). `type` allein genuegt
    NICHT: Darunter faellt das ganze Zubehoer, und die erste Fassung verglich deshalb
    einen RISOKA-Trigger mit RISOKA-Finger-Sleeves als "guenstiger und besser bewertet" --
    zwei Produkte, zwischen denen niemand waehlt. Genau der schiefe Vergleich, den der
    Abschnitt oben ausschliessen will, eine Zeile weiter unten gebaut.

    Produkte UNTER der §A6-Schwelle bekommen hier nichts: Sie tragen schon den
    Warnkasten, und der nennt bereits eine besser bewertete Alternative. Zwei Kaesten
    uebereinander sagen nicht mehr, sie sagen weniger.
    """
    st, _ = bewertung(p)
    pr = preis_zahl(p)
    marke = pfeld(p, 'brand')
    if st is None or pr is None or not marke or st < A6_SCHWELLE:
        return None
    eigene = _kategorien(pfeld(p, 'detail'))
    if not eigene:
        return None
    kandidaten = []
    for q in items:
        if q is p or pfeld(q, 'brand') != marke or pfeld(q, 'type') != pfeld(p, 'type'):
            continue
        qst, _ = bewertung(q)
        qpr = preis_zahl(q)
        if qst is None or qpr is None or qst < A6_SCHWELLE:
            continue
        if qpr < pr and qst > st and (eigene & _kategorien(pfeld(q, 'detail'))):
            kandidaten.append(q)
    if not kandidaten:
        return None
    # Bei Preisgleichheit entscheidet die bessere Bewertung, danach der Slug. Vorher hiess
    # es `min(kandidaten, key=preis_zahl)`, und damit hing die Wahl an der Reihenfolge in
    # products.json: Der X2s hat ZWEI passende Geschwister zu je 45 € (X5 Lite 4,2 und
    # X3 Pro 4,0). Heute gewinnt zufaellig das besser bewertete -- ein Umsortieren der
    # Datei haette den schwaecheren Hinweis gesetzt, ohne dass ein Gate etwas merkt.
    return min(kandidaten, key=lambda q: (preis_zahl(q), -bewertung(q)[0],
                                          pfeld(q, 'slug')))


_EXAKT = re.compile(r'^\d+(?:\.\d{3})*\s*€$')


def _ungefaehr(*produkte):
    """Wahr, sobald products.json einen der Preise nicht als genaue Zahl fuehrt.

    Acht der 42 Preise lauten "ca. 34 €" oder "ab 50 €". Die erste Fassung hat daraus
    `preis_zahl()` gerendert und "kostet 30 €" geschrieben, wo die gepflegte Wahrheit
    "ca. 30 €" lautet -- und die Differenz aus zwei solchen Zahlen als exakte Aussage
    ("kostet 4 € mehr"). Eine Seite darf nicht genauer klingen als ihre Quelle.
    """
    return not all(_EXAKT.match(pfeld(x, 'price').strip()) for x in produkte)


def html(p, items, esc):
    """Der Hinweis-Kasten, oder '' wenn es nichts zu sagen gibt.

    Beide Bewertungen stehen MIT ihrer Anzahl da (B8): "4,4 aus 153" und "4,2 aus 151"
    sind zwei Signale, und bei 153 gegen 151 Bewertungen ist der Abstand ohnehin knapp --
    wer nur die Sterne zeigt, laesst den Leser das nicht einschaetzen.
    """
    q = finden(p, items)
    if q is None:
        return ''
    pst, pc = bewertung(p)
    qst, qc = bewertung(q)
    diff = preis_zahl(p) - preis_zahl(q)
    rund = 'rund ' if _ungefaehr(p, q) else ''
    name = pfeld(q, 'name')
    marke = pfeld(q, 'brand')
    voll = name if marke.lower() in name.lower() else f'{marke} {name}'
    ziel = (pfeld(q, 'detail') or '').rstrip('/') + '/'
    return (f'<div class="note note-info"><strong>Günstiger und besser bewertet:</strong> '
            f'Der <a href="{esc(ziel)}">{esc(voll)}</a> kostet '
            f'{esc(pfeld(q, "price").strip())} und kommt '
            f'auf {sterne_text(qst)} Sterne aus {anzahl_text(qc)} Bewertungen. Dieses '
            f'Modell hier liegt bei {sterne_text(pst)} aus {anzahl_text(pc)} und kostet '
            f'{rund}{diff} € mehr. Wer die Unterschiede nicht ausdrücklich braucht, fährt '
            f'mit dem günstigeren Modell besser.</div>')


def block(inhalt):
    """Leerer Inhalt ergibt KEINEN Block.

    Die erste Fassung umhuellte auch den leeren String und schrieb damit auf jede Seite
    ohne Hinweis ein leeres Markerpaar. Fuer den Leser unsichtbar, fuer das Gate aber ein
    Hinweis, der da nicht sein soll -- und genau daran ist der erste Lauf des
    B10-Gates rot geworden, mit 27 Meldungen.
    """
    if not inhalt:
        return ''
    return f'<!-- {MARKER}:START -->\n{inhalt}\n<!-- {MARKER}:END -->'
