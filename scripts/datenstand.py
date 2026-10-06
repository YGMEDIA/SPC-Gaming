#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Der Datenstand, einmal.

§A5 verlangt EINE Angabe fuer das ganze Repo. Das Gate in verify.py sagt dazu seit dem
30.09.2026: „Bei jedem Preis-Sync wird hier EINE Zeile geaendert, das Gate haelt den Rest
nach." Das war beim Vollabgleich am 06.10.2026 nicht wahr: Der Wert stand als Literal in
fuenf Zeilen in vier Dateien (verify.py, gen_pages.py, gen_longtail.py, gen_preisfrage.py)
und zusaetzlich in md_to_pdf.py. Nach dem Umstellen der Konstante in verify.py haben die
drei Generatoren den alten Monat in 35 Seiten ZURUECKgeschrieben, und md_to_pdf.py hat
weiter September auf Oktober-PDFs gestempelt.

Das Gate hat den Rueckfall gemeldet -- es prueft auch `scripts/gen_*.py` und
`assets/js/*.js`, nicht nur die Seiten. Die Lehre ist also nicht, dass eine Pruefung
fehlte, sondern dass eine Behauptung ueber die Bauweise ungeprueft blieb: „eine Zeile"
war eine Absicht, kein Zustand. Jetzt ist es ein Zustand.

Zwei Stellen koennen nicht importieren und fuehren eigene Fassungen:
  · `assets/js/main.js` traegt den Trust-Strip (sichtbar auf jeder Seite). Von dort leitet
    `sync_header.py` das statische Markup ab, und das §A5-Gate liest main.js mit.
  · Die Seiten selbst. Dafuer ist das Gate da.
"""

# Sichtbare Form im Text ("Datenstand Oktober 2026").
MONAT = 'Oktober 2026'
# Genaue Form fuer Belege und fuer den Vergleich mit dateModified/lastmod.
TAG = '06.10.2026'
# Maschinenform, aus TAG abgeleitet statt zweitgefuehrt.
ISO = '-'.join(reversed(TAG.split('.')))
