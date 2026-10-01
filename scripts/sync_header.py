#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schreibt eine statische Fassung der Hauptnavigation in jede Seite (§A2).

Bis zum 30.09.2026 stand auf allen 109 Seiten nur <header id="site-header"></header>,
gefuellt erst von main.js. Ohne JavaScript hatte damit KEINE Seite eine Navigation: die
zehn wichtigsten internen Links der Domain existierten fuer jeden Crawler nicht, der kein
JS ausfuehrt. Das ist derselbe Fehler wie beim Footer, nur eine Ebene hoeher und mit mehr
SEO-Gewicht.

Einzige Quelle bleibt main.js: dieses Script liest das nav-Array aus buildHeader() und
leitet das statische Markup daraus ab. Aendert sich die Navigation in main.js, laeuft
dieses Script erneut; verify.py meldet jede Abweichung.

main.js ueberschreibt den Header beim Laden weiterhin mit der vollen, interaktiven Fassung
(Suchfeld, Icons, aktiver Zustand). Das statische Markup ist der Unterbau, nicht ein
zweiter Pflegeort.

Aufruf:  python3 scripts/sync_header.py
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
MAIN_JS = 'assets/js/main.js'


def nav_aus_mainjs():
    """Das nav-Array aus buildHeader() lesen. Einzige Quelle der Navigation."""
    s = open(MAIN_JS, encoding='utf-8').read()
    m = re.search(r'function buildHeader\([^)]*\)\s*\{\s*const nav\s*=\s*\[(.*?)\];',
                  s, re.S)
    if not m:
        raise SystemExit(f'FEHLER: nav-Array in {MAIN_JS} nicht gefunden — '
                         f'Struktur von buildHeader() geaendert?')
    eintraege = []
    for zeile in re.finditer(r'\{([^{}]*)\}', m.group(1)):
        feld = dict(re.findall(r"(\w+)\s*:\s*'([^']*)'", zeile.group(1)))
        if 'href' in feld and 'label' in feld:
            eintraege.append(feld)
    if not eintraege:
        raise SystemExit(f'FEHLER: nav-Array in {MAIN_JS} ist leer oder anders notiert')
    return eintraege


def trust_aus_mainjs():
    """Die drei Trust-Strip-Aussagen aus buildHeader() lesen."""
    s = open(MAIN_JS, encoding='utf-8').read()
    i = s.find('<div class="trust-strip">')
    j = s.find('</div>\n</div>', i)
    return [t.strip() for t in re.findall(r'</svg>\s*\n\s*([^<\n]+)\n', s[i:j]) if t.strip()]


def esc(t):
    """In main.js stehen die Texte als JS-Literal, hier landen sie im Markup:
    'Unabhängig & herstellerneutral' braucht ein &amp;."""
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def header_html(nav, trust):
    zeilen = ['<div class="trust-strip"><div class="container">']
    zeilen += [f'<span class="ts">{esc(t)}</span>' for t in trust]
    zeilen.append('</div></div>')
    zeilen.append('<div class="header-main">')
    zeilen.append('<a href="/" class="logo" aria-label="smartphone-controller.com – '
                  'Startseite"><span class="logo-text">smartphone-controller'
                  '<span class="logo-tld">.com</span></span></a>')
    zeilen.append('</div>')
    zeilen.append('<nav class="main-nav" aria-label="Hauptnavigation"><div class="container">')
    for n in nav:
        icon = (esc(n['icon']) + ' ') if n.get('icon') else ''
        badge = (f'<span class="nav-badge">{esc(n["badge"])}</span>') if n.get('badge') else ''
        zeilen.append(f'<a href="{n["href"]}" class="nav-link">{icon}'
                      f'{esc(n["label"])}{badge}</a>')
    zeilen.append('</div></nav>')
    return '\n' + '\n'.join(zeilen) + '\n'


def main():
    nav = nav_aus_mainjs()
    trust = trust_aus_mainjs()
    inhalt = header_html(nav, trust)
    muster = re.compile(r'(<header[^>]*id="site-header"[^>]*>)(.*?)(</header>)', re.S)
    n = 0
    for f in sorted(glob.glob('**/index.html', recursive=True)):
        if f.startswith(('brain/', 'node_modules/')):
            continue
        t = open(f, encoding='utf-8').read()
        if not muster.search(t):
            continue
        neu = muster.sub(lambda m: m.group(1) + inhalt + m.group(3), t, count=1)
        if neu != t:
            open(f, 'w', encoding='utf-8').write(neu)
            n += 1
    # Die Generatoren tragen das leere Header-Element als Literal; sonst schreibt der
    # naechste Generatorlauf die Navigation wieder heraus.
    for g in ['scripts/gen_pages.py', 'scripts/gen_longtail.py', 'scripts/gen_hubs.py']:
        if not os.path.exists(g):
            continue
        t = open(g, encoding='utf-8').read()
        neu = muster.sub(lambda m: m.group(1) + inhalt + m.group(3), t)
        if neu != t:
            open(g, 'w', encoding='utf-8').write(neu)
            n += 1
            print(f'  Generator nachgezogen: {g}')
    print(f'{len(nav)} Navigationslinks aus {MAIN_JS}, {len(trust)} Trust-Aussagen')
    print(f'{n} Datei(en) mit statischer Navigation versehen')
    return 0


if __name__ == '__main__':
    sys.exit(main())
