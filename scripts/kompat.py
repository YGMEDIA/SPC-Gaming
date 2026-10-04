#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kompatibilitaets-Antwort je Produkt: "Passt an / Passt nicht an" (Massnahme B1).

Warum: Die Buecher-Synthese vom 30.09. nennt als gemeinsame Aussage von Jaeckel und
Sheridan, dass der Wert einer Affiliate-Seite in der Information liegt, die der Shop
nicht gibt. Amazon zeigt Sterne und Specs; es zeigt nicht, ob dieser Controller an das
Telefon in der Hand des Lesers passt. Diese Antwort stand bei uns bisher verstreut im
Fliesstext oder gar nicht.

Warum abgeleitet statt getextet: 42 handgepflegte Kompatibilitaetsbloecke wuerden genauso
altern wie alles andere, was diese Session an veralteten Handtexten gefunden hat. Der
Block entsteht deshalb ausschliesslich aus zwei Feldern von products.json:

  worksOn   welche Plattformen das Produkt bedient
  Verb.     die Anschlussart (Spec-Feld)

Nichts davon ist erfunden (§A5). Die sechs Controller, denen `Verb.` fehlte, haben den
Wert am 01.10. aus ihrer EIGENEN Review-Seite bekommen, wo er laengst stand.

Die eine Schlussfolgerung, die der Code zieht, ist Geraetegeschichte und keine
Produktbehauptung: Das iPhone 15 ist das erste mit USB-C. Ein kabelgebundener
USB-C-Controller passt daher nicht an iPhone 14 und aelter, ein Lightning-Controller
nicht an iPhone 15 und neuer. Dieselbe Herleitung steht seit Juli in den FAQ mehrerer
Review-Seiten.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Derselbe Leser wie in verify.py. Die eigene Fassung hier hat verify.py am 02.10. mit
# ValueError abbrechen lassen, sobald `specs` ein Objekt statt einer Liste war: Dieses
# Modul ist Teil des Gates, weil verify.py es importiert.
from produktdaten import spec as _spec, liste as _liste   # noqa: E402


def kompat(p):
    """(passt_an, passt_nicht_an, hinweis) oder None, wenn die Daten nichts hergeben.

    None ist ausdruecklich ein gueltiges Ergebnis: Neun Zubehoerteile fuehren keine
    Massangabe, und "passt an alle Smartphones" waere eine Behauptung, die wir nicht
    belegen koennen. Lieber kein Block als ein beliebiger.
    """
    verb = _spec(p, 'Verb.') or ''
    # str(): Ein Nicht-String-Wert (Zahl, None, Liste) liess `in` hier mit TypeError
    # statt einer Meldung abbrechen.
    verb = str(verb or '')
    hat_bt = 'BT' in verb or 'Bluetooth' in verb
    lightning = 'Lightning' in verb
    usb_nur = ('USB' in verb) and not hat_bt

    if p.get('type') == 'zubehoer':
        mass = _spec(p, 'Für') or _spec(p, 'Kompatibel')
        if not mass:
            return None
        return ([mass], [],
                'Die Angabe ist die Gehäusedicke, gemessen mit aufgesetzter Hülle.')

    # _liste(): worksOn als Zahl oder bool liess den `in`-Test hier mit TypeError
    # abbrechen, und weil verify.py dieses Modul AUFRUFT, starb der ganze Lauf.
    # Die letzte der 13 Abbruchstellen aus den Runden 17 und 18.
    w = _liste(p, 'worksOn')
    ja, nein, hinweis = [], [], None

    if 'android' in w:
        ja.append('Android-Smartphones' + (' mit USB-C' if usb_nur else ''))
    else:
        nein.append('Android-Smartphones')

    if 'ios' in w:
        if lightning:
            ja.append('iPhone bis 14 (Lightning)')
            nein.append('iPhone 15 und neuer (USB-C)')
        elif usb_nur:
            ja.append('iPhone ab 15 (USB-C)')
            nein.append('iPhone 14 und älter (Lightning)')
        else:
            ja.append('iPhone')
    else:
        nein.append('iPhone')

    if 'tablet' in w:
        ja.append('Tablets')

    if not nein and hat_bt:
        hinweis = ('Der Controller koppelt per Bluetooth und ist damit an keine '
                   'Anschlussart gebunden.')
    return (ja, nein, hinweis)


def kompat_html(p, esc):
    """Der fertige Block, oder '' wenn die Daten nichts hergeben.

    `esc` wird hereingereicht, damit Generator und Sync dieselbe Escaping-Regel benutzen —
    zwei Kopien derselben Regel sind am 30.09./01.10. dreimal auseinandergelaufen.
    """
    r = kompat(p)
    if not r:
        return ''
    ja, nein, hinweis = r
    zeilen = [f'<div class="kompat-zeile kompat-ja"><span class="kompat-label">Passt an</span>'
              f'<span class="kompat-werte">{esc(" · ".join(ja))}</span></div>']
    if nein:
        zeilen.append(f'<div class="kompat-zeile kompat-nein">'
                      f'<span class="kompat-label">Passt nicht an</span>'
                      f'<span class="kompat-werte">{esc(" · ".join(nein))}</span></div>')
    if hinweis:
        zeilen.append(f'<p class="kompat-hinweis">{esc(hinweis)}</p>')
    return ('<div class="kompat-box" aria-label="Kompatibilität">\n  '
            + '\n  '.join(zeilen) + '\n</div>')
