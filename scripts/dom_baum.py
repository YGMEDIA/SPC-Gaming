#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parst eine HTML-Datei zu einem Baum, den scripts/finder_probe.js als DOM bedient.

Warum das noetig wurde: Die Pruefung des Vertrags zwischen `controller-finder/index.html`
und `assets/js/finder.js` war drei Runden lang eine Sammlung von Mustern ueber Markup,
und jede Runde hat eine Nachbarform gefunden, die durchlief, waehrend der Finder auf der
Seite tot war:

  Runde 18  Script-Tag entfernt · fuenf Element-Namen umbenannt
  Runde 19  Script-Tag auskommentiert · in <noscript> gewickelt · `data-step` umbenannt ·
            Klasse mit Suffix umbenannt (`\\b` trifft `finder-step-alt`) · `data-back` nur
            noch als Wort in einem CSS-Kommentar
  Runde 20  `data-step` an den FALSCHEN Elementen (Anwesenheit irgendwo genuegte) ·
            `data-step` gedoppelt · Klassen-ZAEHLUNG benutzte weiter `\\b` · Script-Tag in
            den <head> ohne `defer` verschoben · Startzustand `is-active` entfernt

Das Muster ist deutlich: Ein Vertrag zwischen zwei Dateien laesst sich nicht durch Suchen
nach Schreibweisen pruefen. Geprueft wird deshalb, was HERAUSKOMMT -- finder.js laeuft
gegen die wirkliche Struktur dieser Seite, und verify.py prueft die Zustaende, die dabei
entstehen (welcher Schritt ist aktiv, wie viele Karten erscheinen, welche Antwort wird
gesetzt). Alle fuenf Formen aus Runde 20 sind damit keine Muster-Frage mehr, sondern eine
Messung.

Der Parser steht hier und nicht im JS-Harness, weil html.parser aus der Standardbibliothek
die Eigenheiten echten Markups kennt (Void-Elemente, Attribute ohne Wert, einfache
Anfuehrungszeichen, Grossschreibung) und ein handgeschriebener Parser im Harness genau die
Fehlerklasse zurueckbraechte, die wir hier loswerden.
"""
import json
import sys
from html.parser import HTMLParser

VOID = {'img', 'br', 'hr', 'input', 'meta', 'link', 'source', 'area', 'col',
        'embed', 'param', 'track', 'wbr', 'base'}
# Inhalt, der fuer den Finder nicht existiert: <template> rendert der Browser nicht,
# <noscript> wird mit aktivem JS nicht ausgefuehrt. Ein darin liegendes Element darf den
# Vertrag deshalb nicht erfuellen (Runde 19: Script-Tag in <noscript> gewickelt).
UNSICHTBAR = {'template', 'noscript'}


class _Baum(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.wurzel = {'tag': '#root', 'attrs': {}, 'children': [], 'text': ''}
        self._stapel = [self.wurzel]
        self._tot = 0          # Tiefe innerhalb von template/noscript
        self.reihenfolge = []  # Tag-Namen in Dokumentreihenfolge, fuer die Ladeordnung

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if self._tot:
            if tag in UNSICHTBAR:
                self._tot += 1
            return
        if tag in UNSICHTBAR:
            self._tot = 1
            return
        _k = {'tag': tag, 'attrs': {k.lower(): (v if v is not None else '')
                                    for k, v in attrs},
              'children': [], 'text': ''}
        self.reihenfolge.append(_k)
        self._stapel[-1]['children'].append(_k)
        if tag not in VOID:
            self._stapel.append(_k)

    def handle_startendtag(self, tag, attrs):
        # `<img ... />`: HTMLParser ruft hier, nicht start+end. Ohne eigene Behandlung
        # haette der Stapel sich verschoben -- derselbe Fehler wie im Karten-Parser.
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID and len(self._stapel) > 1:
            self._stapel.pop()

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in UNSICHTBAR:
            self._tot = max(0, self._tot - 1)
            return
        if self._tot or tag in VOID:
            return
        for _i in range(len(self._stapel) - 1, 0, -1):
            if self._stapel[_i]['tag'] == tag:
                del self._stapel[_i:]
                return

    def handle_data(self, data):
        if not self._tot and data.strip():
            self._stapel[-1]['text'] += data


def baum(html_text):
    """Der DOM-Baum der Datei, ohne template- und noscript-Inhalt."""
    p = _Baum()
    p.feed(html_text)
    return p.wurzel


def ladeordnung(html_text, src_teil):
    """Wie das Skript geladen wird: ('fehlt'|'defer'|'async'|'nach'|'vor', Position).

    'nach' heisst: das Script-Tag steht hinter dem Element, das es sucht, laeuft also
    nach dessen Parsen. 'vor' ist der Schadensfall aus Runde 20 -- im <head> ohne `defer`
    kehrt finder.js in Zeile 6 wortlos zurueck, kein Klick wirkt, keine Fehlermeldung.
    """
    p = _Baum()
    p.feed(html_text)
    _skript = None
    _finder = None
    for _i, _k in enumerate(p.reihenfolge):
        if _k['tag'] == 'script' and src_teil in (_k['attrs'].get('src') or ''):
            _skript = (_i, _k)
        if _k['attrs'].get('id') == 'finder' and _finder is None:
            _finder = _i
    if _skript is None:
        return ('fehlt', -1)
    _i, _k = _skript
    if 'defer' in _k['attrs']:
        return ('defer', _i)
    if 'async' in _k['attrs']:
        return ('async', _i)
    if _finder is not None and _i > _finder:
        return ('nach', _i)
    return ('vor', _i)


if __name__ == '__main__':
    print(json.dumps(baum(open(sys.argv[1], encoding='utf-8').read())))
