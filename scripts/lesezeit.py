#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Die eine Rechenregel fuer Wortzahl und Lesezeit einer Seite.

Vorgeschichte: Bis zum 01.10.2026 stand die Lesezeit auf 19 Blog-Seiten als getippte
Zahl in der Byline, ein zweites Mal in den 19 Karten auf /blog/ und ein drittes Mal in
den drei Karten auf der Startseite. Niemand hat sie je nachgerechnet. Die Messung gegen
HEAD ergab: auf 17 von 19 Seiten war die genannte Zeit zu hoch (12x um 1, 3x um 2, 2x um
3 Minuten), nur 2 stimmten, keine Byline war zu niedrig (eine KARTE war es: die Startseite nannte 3 Minuten fuer einen 4-Minuten-Artikel). Es war derselbe Fehler wie die
"4 Fragen" im Finder-Text und die Kabelquote im Hilfe-Artikel -- eine Zahl, die bei der
Entstehung plausibel war und mit jeder Textaenderung falscher wird.

Nachtrag zur Entstehung dieser Zeilen: Hier stand zuerst "15 von 19, einmal um zwei
Minuten". Das war eine Messung VOR dem Ausschluss der Breadcrumb-Navigation, also nach
einer anderen Regel als der, die diese Datei definiert, und sie widersprach der Zahl im
Gate-Kommentar von verify.py. Eine getippte Zahl im Docstring der Datei, die getippte
Zahlen abschaffen soll: Der Pruefer hat sie gefunden, nicht ich.

Die Regel steht hier und nur hier, weil gen_preisfrage.py sie zum Bauen braucht,
sync_lesezeit.py zum Nachziehen und verify.py zum Pruefen. Drei Orte mit je eigener
Formulierung derselben Regel sind an diesem Projekt schon dreimal auseinandergelaufen
(Escaping, Reichweite, Vergleichsregel bei den Spec-Chips).

Gezaehlt wird der Artikeltext: <main> ohne Skripte, Stile und Breadcrumb-Navigation.
Header und Footer bleiben aussen vor, denn niemand liest die Pflichtangaben mit.
200 Woerter pro Minute ist der Wert, mit dem die Preisfrage-Seite seit ihrer Entstehung
rechnet; er bleibt, damit alle Seiten dieselbe Skala benutzen.
"""
import re
from html.parser import HTMLParser

WPM = 200

# Die zwei Orte, an denen eine Lesezeit im Markup steht. Sie gehoeren hierher und nicht
# in zwei Dateien: Der Pruefer hat am 01.10. gemessen, dass die Karten-Muster in
# verify.py und sync_lesezeit.py schon nach einem Tag nicht mehr zeichengleich waren
# (eine Klammer Unterschied, noch ohne Verhaltensunterschied). Genau so sind an diesem
# Projekt dreimal zwei Kopien derselben Regel auseinandergelaufen, und die Rechenregel
# allein zu teilen schuetzt davor nicht.
# BYLINE: Gruppe 1 = alles bis zur Zahl, 2 = die Minuten, 3 = der Rest.
BYLINE = re.compile(r'(article-byline"[^>]*>.*?·\s*)(\d+)(\s*Min\. Lesezeit)', re.S)
# KARTE: Gruppe 1 = Ziel-Pfad, 2 = die Minuten, 3 = der Rest.
KARTE = re.compile(r'<a href="(/blog/[^"]+/)"(?:(?!</a>).)*?'
                   r'article-meta"[^>]*>\s*(\d+)(\s*Min\. Lesezeit)', re.S)

_WEG = re.compile(r'<(script|style|nav)\b[^>]*>.*?</\1>', re.S)
_TAGS = re.compile(r'<[^>]+>')


def artikel_text(html):
    """Der lesbare Artikeltext, oder None wenn die Seite kein <main> hat."""
    m = re.search(r'<main\b.*?</main>', html, re.S)
    if not m:
        return None
    return _TAGS.sub(' ', _WEG.sub(' ', m.group(0)))


def woerter(html):
    """Wortzahl des Artikeltextes. None, wenn die Seite kein <main> hat."""
    t = artikel_text(html)
    return None if t is None else len(re.findall(r'\w+', t))


def minuten(html):
    """Lesezeit in ganzen Minuten, mindestens 1. None ohne <main>."""
    w = woerter(html)
    return None if w is None else max(1, round(w / WPM))


class _KartenLeser(HTMLParser):
    """Findet Artikel-Karten durch PARSEN, nicht durch Markup-Muster.

    Vorgeschichte: Der Anwesenheits-Anker fuer die Karten war zuerst ein Regex auf
    `<a href="..." class="...article-card...">`. Der Pruefer hat am 02.10.2026 vier
    Umformatierungen gezeigt, die ihn abschalten, waehrend eine falsche Lesezeit sichtbar
    auf der Seite stand: `class` vor `href`, einfache Anfuehrungszeichen, ein Zeilenumbruch
    nach `<a`, und die Karte als `<div class="article-card">` mit innerem `<a>`. Das ist
    genau die Lehre, die der Anker durchsetzen sollte, angewandt auf den Anker selbst:
    Ein Muster ueber Markup ist an eine Schreibweise gebunden.

    Der Parser ist gegen alle vier unempfindlich, weil er Attribute als Attribute liest
    und Verschachtelung mitzaehlt.
    """

    # Void-Elemente haben kein Endtag. Die erste Fassung zaehlte sie als Tiefe mit,
    # womit das <img> in jeder Karte den Zaehler nie wieder auf null brachte und der
    # Parser NULL Karten fand -- eine Pruefung, die stumm nichts geprueft haette.
    VOID = {'img', 'br', 'hr', 'input', 'meta', 'link', 'source', 'area', 'col',
            'embed', 'param', 'track', 'wbr', 'base'}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.karten = []          # (href, text) je Karte
        self._tiefe = None
        self._href = None
        self._text = []
        self._template = 0

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'template':
            # Inhalt in <template> rendert der Browser nicht. Eine Karte dort ist fuer
            # den Leser nicht vorhanden; sie zu zaehlen hiesse, Markup statt Seite zu
            # pruefen (und ohne JS fehlt der Inhalt ganz, §A2).
            self._template += 1
            return
        if self._template:
            return
        if self._tiefe is None:
            if 'article-card' in (d.get('class') or '').split():
                self._tiefe = 1
                self._href = d.get('href')
                self._text = []
            return
        if tag not in self.VOID:
            self._tiefe += 1
        if self._href is None and tag == 'a' and d.get('href'):
            self._href = d['href']   # Karte als <div> mit innerem <a>

    def handle_endtag(self, tag):
        if tag == 'template':
            self._template = max(0, self._template - 1)
            return
        if self._template or self._tiefe is None:
            return
        if tag in self.VOID:
            # HTMLParser ruft fuer `<img ... />` startendtag, und das ruft starttag UND
            # endtag. Die erste Fassung schuetzte nur die Starttag-Seite, womit ein
            # einzelner Schraegstrich im img die Tiefe um eins senkte, die Karte zu frueh
            # schloss und verify mit Exit 1 behauptete, sie trage keine Lesezeit --
            # waehrend sie sichtbar eine trug. Ein Fehlalarm, der jede Arbeit blockiert.
            return
        self._tiefe -= 1
        if self._tiefe <= 0:
            self.karten.append((self._href, ''.join(self._text)))
            self._tiefe, self._href, self._text = None, None, []

    def handle_data(self, data):
        if not self._template and self._tiefe is not None:
            self._text.append(data)


def karten(html_text):
    """Alle Artikel-Karten als (href, sichtbarer Text). Geparst, nicht gematcht."""
    p = _KartenLeser()
    p.feed(html_text)
    return p.karten
