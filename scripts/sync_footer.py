#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schreibt den statischen Pflicht-Footer in jede Seite (§A2/§C2), abgeleitet aus main.js.

Vorgeschichte: Bis zum 30.09.2026 wurde der Footer ausschliesslich per JavaScript
injiziert. Ohne JS gab es auf 109 Seiten weder Impressum noch Datenschutz noch den
Affiliate-Hinweis -- keine Stilfrage, sondern fehlende Pflichtangaben. Der statische
Footer kam damals als Literal in die Seiten und in die Generatoren.

Damit lag derselbe Text an vier Orten (gen_pages, gen_longtail, gen_preisfrage und 111
HTML-Dateien), und ein Gate pruefte nur seine ANWESENHEIT, nicht seine Identitaet. Genau
diese Lage hatte der Header vor sync_header.py, und genau so sind an einem einzigen Tag
dreimal zwei Kopien derselben Regel auseinandergelaufen.

Einzige Quelle ist deshalb main.js: Dieses Script liest den Transparenz-Hinweis und die
Rechtslinks aus buildFooter() und leitet das statische Markup daraus ab. Damit sagen die
Fassung ohne JS und die Fassung mit JS zwangslaeufig dasselbe.

Nicht betroffen sind die 16 Redirect-Stubs: Sie tragen kein footer-Element, leiten sofort
weiter und brauchen keins.

Aufruf:  python3 scripts/sync_footer.py
         python3 scripts/sync_footer.py --check   (nur melden, nichts schreiben)
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
MAIN_JS = 'assets/js/main.js'

# Die Generatoren tragen den Footer als Literal; ohne sie schreibt der naechste
# Generatorlauf die alte Fassung zurueck.
GENERATOREN = ['scripts/gen_pages.py', 'scripts/gen_longtail.py', 'scripts/gen_preisfrage.py']


def aus_mainjs():
    """Transparenz-Hinweis und Rechtslinks aus buildFooter(). Einzige Quelle."""
    s = open(MAIN_JS, encoding='utf-8').read()

    m = re.search(r'<p class="foot-affiliate">\s*(.*?)\s*</p>', s, re.S)
    if not m:
        raise SystemExit(f'FEHLER: foot-affiliate in {MAIN_JS} nicht gefunden')
    hinweis = re.sub(r'\s+', ' ', m.group(1)).strip()

    m2 = re.search(r'<div class="foot-legal">(.*?)</div>', s, re.S)
    if not m2:
        raise SystemExit(f'FEHLER: foot-legal in {MAIN_JS} nicht gefunden')
    links = re.findall(r'<a href="([^"]+)">([^<]+)</a>', m2.group(1))
    schluss = re.search(r'<span>([^<]+)</span>', m2.group(1))
    if not links or not schluss:
        raise SystemExit(f'FEHLER: foot-legal in {MAIN_JS} ist leer oder anders notiert')
    return hinweis, links, schluss.group(1).strip()


def footer_html(hinweis, links, schluss):
    teile = [f'<a href="{href}">{text}</a>' for href, text in links]
    teile.append(schluss)
    return ('\n  <div class="container">\n'
            f'    <p class="foot-affiliate">{hinweis}</p>\n'
            f'    <p class="foot-legal">{" · ".join(teile)}</p>\n'
            '  </div>\n')


def ziele():
    z = sorted(glob.glob('**/index.html', recursive=True))
    z = [f for f in z if not f.startswith(('brain/', 'node_modules/'))]
    if os.path.exists('404.html'):
        z.append('404.html')
    return z + [g for g in GENERATOREN if os.path.exists(g)]


def main():
    nur_pruefen = '--check' in sys.argv
    hinweis, links, schluss = aus_mainjs()
    inhalt = footer_html(hinweis, links, schluss)
    muster = re.compile(r'(<footer[^>]*id="site-footer"[^>]*>)(.*?)(</footer>)', re.S)

    geaendert, ohne = 0, 0
    for f in ziele():
        t = open(f, encoding='utf-8').read()
        if not muster.search(t):
            ohne += 1
            continue
        neu = muster.sub(lambda m: m.group(1) + inhalt + m.group(3), t)
        if neu != t:
            geaendert += 1
            if not nur_pruefen:
                open(f, 'w', encoding='utf-8').write(neu)
            print(f"  {'wuerde geaendert' if nur_pruefen else 'gesetzt'}: {f}")
    print(f'{len(links)} Rechtslinks aus {MAIN_JS}, Hinweis mit {len(hinweis)} Zeichen')
    print(f"{geaendert} Datei(en) {'waeren geaendert' if nur_pruefen else 'geaendert'}, "
          f'{ohne} ohne footer-Element (Redirect-Stubs)')
    return 1 if (nur_pruefen and geaendert) else 0


if __name__ == '__main__':
    sys.exit(main())
