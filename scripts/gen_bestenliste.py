#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B6: Die vier Bestenlisten als Seitentyp, mit begruendeter und nachrechenbarer Ordnung.

WAS DIESE SEITEN VORHER WAREN
Vier handgeschriebene Seiten (/controller/beste/ und drei unter /vergleich/), zusammen
1.783 Woerter, mit 23 Produktpositionen. Gemessen am 04.10.2026:

  · Die eine genannte Sortier-Regel lautete "Preis, Sticks, Ergonomie und Kompatibilitaet".
    "Ergonomie" kommt in products.json NICHT vor -- unter keinem Spec-Schluessel, bei
    keinem der 42 Produkte. Eine Regel, deren Kriterium keine Datengrundlage hat, ist
    keine Regel: Der Leser kann keine einzige Position nachpruefen.
  · Die drei /vergleich/-Seiten nannten ueberhaupt keine Regel.
  · Auf keiner der vier Seiten stand eine einzige Bewertung. Null sichtbare Sterne auf
    Seiten, deren Zweck eine Rangfolge ist.
  · Die drei /vergleich/-Seiten trugen kein ItemList-Schema (nur BreadcrumbList), obwohl
    ihre Titel "Top 5" und "Top-Auswahl" versprechen.
  · 14 Spec-Chips auf den Karten nannten Werte, die products.json nicht fuehrt (siehe
    UNGEDECKTE SPECS unten).

Das war damit die siebte Renderstelle fuer Produktdaten -- und die einzige ungegatete.
Sechs andere sind am 30.09. geschlossen worden.

WAS DIE ORDNUNG IST UND WAS NICHT
Die Reihenfolge bleibt redaktionell und steht als Liste in `LISTEN`. Sie wurde NICHT
umgerechnet, und das ist eine Entscheidung mit Begruendung: Nach Sternen allein laesst
sich diese Liste nicht ordnen. 27 der 28 Controller liegen zwischen 3,8 und 4,6 Sternen,
allein sieben teilen sich 4,2 -- eine Rangfolge aus Differenzen von 0,1 Sternen waere
Scheingenauigkeit. Zusaetzlich gemessen: Der heutige Spitzenplatz der Gesamtliste ist nach
geglaetteter Bewertung Platz 12 von 28, und sieben Controller, die auf keiner Liste
stehen, liegen nach Sternen ueber mindestens drei gelisteten. Ob umgerankt wird, ist eine redaktionelle und
kommerzielle Entscheidung und steht als Punkt fuer Yasin in STATUS.

Was dieses Skript stattdessen tut: Es macht die Ordnung PRUEFBAR. Jede Zahl auf den
Seiten kommt aus products.json, jede Position nennt ihre Bewertung mit Anzahl, und ein
eigener Abschnitt sagt offen, welches Produkt nach Sternen vorn laege und was in seinen
DATEN gegen den Spitzenplatz spricht. Das ist der Sheridan-Punkt hinter B6: Die Liste
gewinnt Glaubwuerdigkeit, wenn sie die Zahl nennt, die gegen sie spricht.

UNGEDECKTE SPECS (§A5, nicht hier geloest)
14 Chips nannten Werte ohne Grundlage in products.json. Jeder einzelne steht auch auf der
Review-Seite des Produkts, die Behauptungen sind also seitenweit konsistent -- nur fehlen
sie im Datenkern. Sie werden hier NICHT nach products.json geschrieben: Das waere eine
unbelegte Produktaussage in den Datenkern zu waschen, und §A5 verbietet genau das. Dieser
Generator rendert nur, was products.json fuehrt; die ungedeckten Chips fallen damit weg.
Welche es sind, steht in STATUS als Punkt fuer Yasin (er braucht Screenshots):
  Gew. 135 g (x5-lite) · Extra 4 Ruecktasten (kishi-v3) · Sticks TMR+Haptik und
  Extra Haptik (kishi-v3-pro) · Sticks Hall-Effect (x2s) · Sticks Hall-Effect
  (ultimate-mobile) · Fokus Shooter (rog-tessen) · Akku 40 h (backbone-pro)

WAS DIESER GENERATOR NICHT PRUEFT, ausdruecklich und nicht geschlossen (R31):
  · Der BADGE-Text ist freier redaktioneller Text und voellig ungegatet. Proben des
    Pruefers: "Hall-Effect-Sieger" auf ein Produkt ohne `Sticks`-Spec, "Guenstigster" auf
    das 152-€-Modell -- beides bleibt gruen. Ein Gate muesste jede moegliche Behauptung
    eines freien Etiketts verstehen; das ist dieselbe Aufgabe, an der die Mengenaussagen
    in Prosa acht Pruefrunden lang gescheitert sind (P-13 Mechanismus 7). Die Badges
    stehen deshalb bewusst in dieser Datei und nicht im HTML: eine Zeile, die man liest.
  · `menge` (die Filter-Funktion) und `menge_dativ` (der Text daneben) sind nicht
    aneinander gebunden. Wer den Budget-Filter auf `< 200` setzt oder den Text auf "unter
    allen Produkten" aendert, bekommt einen Regelsatz, der zum Seitentitel nicht passt,
    und alles bleibt gruen. Das ist woertlich die §A6-Klasse "richtige Zahl, falscher
    Bezugsrahmen", nur im Generator statt im Text. Beide stehen hier untereinander, damit
    der Zusammenhang beim Lesen auffaellt; maschinell gebunden sind sie nicht.
  · Das Positions-Gate in verify.py erfasst Top-Level- und `@graph`-Knoten. Eine tiefer
    verschachtelte ItemList (etwa unter `WebPage.mainEntity`) faellt heraus. Gemessen:
    124 Listen-Schemas, 0 verschachtelt.
  · `ordnung` und `menge` sind ebenfalls nicht aneinander gebunden: Nimmt man einem
    gelisteten Produkt die Plattform aus `worksOn`, bleibt es auf der Plattform-Liste
    stehen, und kein B6-Gate sagt etwas (verify.py wird rot, aber ueber `platformLabel`
    und zwei Mengenzaehlungen).
  · Das Top-N-Gate in verify.py greift ueber die Zusagestellen (title, og, twitter,
    Ueberschrift). Gemessen: /vergleich/beste-budget-controller/ nennt an keiner davon
    eine Zahl -- dort traegt allein der `topn`-Befund in diesem Modul.
  · Das Ueberschriften-Gate meldet je Seite nur den ERSTEN Sprung und sieht eine Seite
    nicht, die ganz ohne h1 bei h2 beginnt.

Aufruf:  python3 scripts/gen_bestenliste.py
         python3 scripts/gen_bestenliste.py --check   (nur melden, nichts schreiben)
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'scripts'))
os.chdir(ROOT)

from gen_hubs import esc                      # dieselbe Escaping-Regel wie die Hub-Karten
from produktdaten import (A6_SCHWELLE, bewertung, preis_zahl, spec_paare, spec_wie,
                          sterne_text, anzahl_text, text as pfeld, liste as pliste)

MARKER = 'BESTEN'

# Die Plattform-Etiketten, in der Reihenfolge, in der sie im Text erscheinen.
PLATTFORM_TEXT = [('ios', 'iPhone'), ('android', 'Android'), ('tablet', 'Tablet'),
                  ('mini', 'kleine Handys')]


# --------------------------------------------------------------------------- Listen
# Redaktioneller Input, und nur dieser: WELCHE Produkte, in welcher REIHENFOLGE, mit
# welchem BADGE. Alles andere -- Name, Claim, Preis, Bewertung, Specs, Bild, Detail-Link
# -- kommt aus products.json. Die Reihenfolge ist der Stand vom 04.10.2026, unveraendert
# uebernommen, damit der erste Lauf die Empfehlung nicht verschiebt.
#
# `menge` ist die Grundmenge, gegen die die Superlative dieser Seite gerechnet werden
# (§A6-Superlativ-Regel: jeder Superlativ nennt seinen Geltungsbereich). Sie ist eine
# PRUEFBARE Funktion, kein Satz: Der Ehrlichkeits-Abschnitt rechnet darin den
# bestbewerteten Controller aus, und verify.py rechnet dasselbe nach.
LISTEN = [
    {
        'datei': 'controller/beste/index.html',
        'listenname': 'Bester Handy Controller 2026',
        'topn': 10,             # die Zahl, die Titel und h2 dieser Seite versprechen
        'kartenebene': 'h3',    # ueber dem Block steht die h2 "Die Top 10 im Ueberblick"
        'menge_dativ': 'unter allen Controllern im Sortiment',
        'fokus': (),            # keine Plattform-Einschränkung
        'menge': lambda p: pfeld(p, 'type') == 'controller',
        'ordnung': [
            ('gamesir-g8-galileo', 'Testsieger', 'badge-top', ' featured'),
            ('gamesir-x5-lite', 'Preistipp', 'badge-budget', ''),
            ('razer-kishi-v3', 'Premium', 'badge-top', ''),
            ('backbone-one-2', 'iOS-Klassiker', 'badge-top', ''),
            ('8bitdo-ultimate-2c', 'Android + Windows', 'badge-new', ''),
            ('gamesir-g8-plus', '', '', ''),
            ('razer-kishi-v3-pro', '', '', ''),
            ('gamesir-x2s', '', '', ''),
            ('asus-rog-tessen', 'Shooter', '', ''),
            ('backbone-pro', 'Wireless', '', ''),
        ],
    },
    {
        'datei': 'vergleich/beste-android-controller/index.html',
        'listenname': 'Beste Android Controller Top 5',
        'topn': 5,
        'kartenebene': 'h2',    # diese Seite hat keine andere h2; h3 waere ein Sprung
        'menge_dativ': 'unter den Android-Controllern im Sortiment',
        'fokus': ('android',),  # iOS ist auf dieser Liste kein Argument
        'menge': lambda p: (pfeld(p, 'type') == 'controller'
                            and 'android' in pliste(p, 'worksOn')),
        'ordnung': [
            ('gamesir-g8-galileo', 'Android-Testsieger', 'badge-top', ' featured'),
            ('gamesir-x5-lite', 'Budget-King', 'badge-budget', ''),
            ('8bitdo-ultimate-2c', 'Android + Windows', 'badge-top', ''),
            ('gamesir-g8-plus', 'Bluetooth-Allrounder', 'badge-new', ''),
            ('asus-rog-tessen', 'Shooter-Spezialist', 'badge-top', ''),
        ],
    },
    {
        'datei': 'vergleich/beste-budget-controller/index.html',
        'listenname': 'Beste Budget Controller unter 50 €',
        'topn': 3,
        'kartenebene': 'h2',
        'menge_dativ': 'unter den Controllern unter 50 €',
        'fokus': (),
        'menge': lambda p: (pfeld(p, 'type') == 'controller'
                            and (preis_zahl(p) or 10 ** 6) < 50),
        'ordnung': [
            ('gamesir-x5-lite', 'Budget-Testsieger', 'badge-top', ' featured'),
            ('8bitdo-ultimate-2c', 'Android + Windows', 'badge-top', ''),
            ('8bitdo-ultimate-mobile', 'Solider Allrounder', 'badge-new', ''),
        ],
    },
    {
        'datei': 'vergleich/beste-iphone-controller/index.html',
        'listenname': 'Beste iPhone Controller Top 5',
        'topn': 5,
        'kartenebene': 'h2',
        'menge_dativ': 'unter den iPhone-Controllern im Sortiment',
        'fokus': ('ios',),      # Android ist auf dieser Liste kein Argument
        'menge': lambda p: (pfeld(p, 'type') == 'controller'
                            and 'ios' in pliste(p, 'worksOn')),
        'ordnung': [
            ('gamesir-g8-galileo', 'iOS-Testsieger', 'badge-top', ' featured'),
            ('backbone-one-2', 'iOS-Klassiker', 'badge-top', ''),
            ('razer-kishi-v3', 'Shooter-Wahl', 'badge-top', ''),
            ('gamesir-x5-lite', 'Preistipp', 'badge-budget', ''),
            ('backbone-pro', 'Premium', 'badge-new', ''),
        ],
    },
]


# --------------------------------------------------------------------------- Ableitungen
def plattformen(p):
    """Die Plattform-Etiketten eines Produkts, als Text. Leer, wenn worksOn leer ist."""
    w = pliste(p, 'worksOn')
    return [t for k, t in PLATTFORM_TEXT if k in w]


def stickart(p):
    """"Hall-Effect" / "TMR" / '' -- nur was in `Sticks` wirklich steht.

    Positiv abgeleitet, nicht negativ: Mechanismus 8 aus P-13. Was products.json nicht
    fuehrt, gilt hier als unbekannt und wird nicht genannt -- nicht als "normale Sticks".
    """
    s = spec_wie(p, 'Sticks')
    if 'Hall' in s:
        return 'Hall-Effect'
    if 'TMR' in s:
        return 'TMR'
    return ''


def vollname(p):
    """Marke plus Name, ohne die Marke zu doppeln.

    "Backbone" + "Backbone Pro" ergab "Backbone Backbone Pro". Drei der 42 Namen tragen
    ihre Marke schon im Namen, deshalb wird geprueft statt zusammengeklebt.
    """
    marke, name = pfeld(p, 'brand').strip(), pfeld(p, 'name').strip()
    if not marke or name.lower().startswith(marke.lower()):
        return name or marke
    return f'{marke} {name}'


def ist_kabelgebunden(p):
    return 'kabelgebunden' in spec_wie(p, 'Verb').lower()


def faktenzeile(p):
    """Die nachrechenbare Zeile unter dem Claim: Bewertung, Preis, Plattformen, Sticks.

    Das ist der Kern von B6. Vorher stand auf diesen Seiten keine einzige Bewertung --
    eine Rangfolge ohne die Zahl, an der man sie messen koennte. Jeder Teil kommt aus
    products.json; fehlt ein Teil, faellt er weg statt geraten zu werden.
    """
    st, n = bewertung(p)
    teile = []
    if st is not None:
        teile.append(f'<strong>{sterne_text(st)} Sterne</strong> aus '
                     f'{anzahl_text(n)} Bewertungen')
    # Der Preis steht BEWUSST nicht hier: Er steht zwei Zeilen tiefer in der price-row
    # derselben Karte. Dieselbe Zahl zweimal auf einer Karte ist genau die Form, die in
    # diesem Repo reihenweise auseinandergelaufen ist (sechs Renderstellen, 30.09.).
    pl = plattformen(p)
    if pl:
        teile.append(', '.join(pl))
    sa = stickart(p)
    if sa:
        teile.append(f'{sa}-Sticks')
    if ist_kabelgebunden(p):
        teile.append('kabelgebunden')
    return ' · '.join(teile)


def regeltext(liste_def, menge):
    """Die Sortier-Regel, mit der an DIESER Menge gemessenen Begruendung.

    Hier stand "Preis, Sticks, Ergonomie und Kompatibilitaet" -- ein Kriterium ohne
    Datengrundlage ("Ergonomie" kommt in products.json unter keinem Spec-Schluessel vor).
    Die Zahlen in diesem Satz werden gerechnet, damit der Satz nicht veraltet, wenn ein
    Produkt dazukommt.

    "Von den N Modellen, aus denen diese Liste gewaehlt ist" statt "in dieser Liste": Die
    Zahl ist die GRUNDMENGE, nicht die Zahl der Plaetze. Die erste Fassung schrieb "Von 14
    Modellen in dieser Liste" auf eine Seite mit drei Plaetzen.
    """
    # Waehlbar ist nur, was ueber der §A6-Schwelle liegt. Die erste Fassung rechnete
    # ueber die ganze Grundmenge und schrieb "Von den 28 Modellen, aus denen diese Liste
    # gewaehlt ist, liegen alle zwischen 3,5 und 4,6" -- das 3,5-Modell darf nie gewaehlt
    # werden. Richtig sind 27 und 3,8 bis 4,6, was die Begruendung sogar staerkt.
    sterne = sorted(s for s in (bewertung(p)[0] for p in menge)
                    if s is not None and s >= A6_SCHWELLE)
    if not sterne:
        return ''
    haeufigster = max(set(sterne), key=sterne.count)
    wie_oft = sterne.count(haeufigster)
    gleich = (f', allein {wie_oft} davon teilen sich {sterne_text(haeufigster)}'
              if wie_oft > 1 else '')
    return (f'Sortiert nach Plattform-Reichweite, Stick-Technik, Verbindung und Preis, '
            f'<strong>nicht nach der Sternzahl</strong>. Warum nicht: Von den '
            f'{len(sterne)} Modellen, aus denen diese Liste gewählt ist, liegen alle '
            f'zwischen {sterne_text(min(sterne))} und {sterne_text(max(sterne))} '
            f'Sternen{gleich}. Eine Rangfolge aus Zehntelsternen wäre erfunden. '
            f'Deshalb steht bei jedem Platz die Bewertung mit ihrer Anzahl '
            f'dabei, und du kannst die Reihenfolge selbst gegenrechnen.')


def ehrlichtext(liste_def, menge, erster):
    """Der Abschnitt, der die Zahl nennt, die gegen die eigene Reihenfolge spricht.

    Vollstaendig abgeleitet: Wer in der Grundmenge die beste Bewertung hat, was er
    kostet, wo er in dieser Liste steht, und was in seinen DATEN gegen Platz 1 spricht.
    Erfunden wird nichts: "kabelgebunden" steht wortwoertlich in `Verb.`, die fehlende
    Plattform in `worksOn`. Findet sich kein Nachteil in den Daten, sagt der Abschnitt
    genau das, statt einen zu behaupten.

    `fokus` begrenzt das Plattform-Argument auf die Plattformen, um die es auf DIESER
    Seite geht. Die erste Fassung meldete auf der Android-Liste "laeuft nicht an iPhone"
    als Grund gegen Platz 1 -- auf einer Android-Seite ist das kein Argument, sondern
    Rauschen. Der Fokus macht aus derselben Ableitung je Seite die richtige Aussage.
    """
    mit_bew = [p for p in menge if bewertung(p)[0] is not None]
    if not mit_bew:
        return ''
    bst = max(bewertung(p)[0] for p in mit_bew)
    # GLEICHSTAND. Die erste Fassung brach ihn still ueber die Bewertungsanzahl
    # (`max(..., key=(sterne, anzahl))`) und behauptete damit Alleinstellung, wo keine
    # ist: Auf der iPhone-Liste teilen sich Razer Kishi V3 (4,4 aus 153) und Backbone Pro
    # (4,4 aus 459) die beste Bewertung, und BEIDE stehen auf derselben Seite mit
    # sichtbaren 4,4. Ein Superlativ, den die eigene Seite zwei Karten hoeher widerlegt --
    # genau die Klasse, fuer die die Superlativ-Regel in §A6 geschrieben wurde.
    spitze = [p for p in mit_bew if bewertung(p)[0] == bst]
    spitze.sort(key=lambda p: -bewertung(p)[1])
    best = spitze[0]
    bn = bewertung(best)[1]
    est, _ = bewertung(erster)
    if est is None:
        # Platz 1 ohne lesbare Bewertung: Das ist ein Datenbefund, kein Grund zum
        # Abbrechen. Die erste Fassung gab `None` an `sterne_text()` weiter und starb mit
        # TypeError -- mitten im Schreiben, nachdem zwei der vier Seiten schon neu
        # geschrieben waren.
        return ''
    name = vollname(best)
    if len(spitze) > 1:
        # Jede Zahl steht BEI ihrem Produkt. Die erste Fassung sammelte die Namen vorn
        # und die Bewertungszahlen hinten ("A und B kommen beide auf 4,4 (459, 153)") --
        # nicht zuordenbar, und der §A1-Fliesstext-Gate hat es sofort als "Razer Kishi V3:
        # 459 statt 153 Bewertungen" gemeldet. Die Meldung war richtig.
        #
        # Und: Die Zahlwoerter werden GERECHNET. Die zweite Fassung verzweigte auf
        # `len(spitze) > 1`, formulierte aber fuer genau zwei ("teilen sich zwei",
        # "beide", "der beiden"). Bei drei gleichauf stand dann "A und B und C kommen
        # beide auf 4,4" -- erreichbar durch ein einziges Screenshot-Update, mit gruenem
        # Gate-Set. Dieselbe §A6-Klasse, fuer die diese Verzweigung gebaut wurde.
        ZAHLWORT = {2: 'zwei', 3: 'drei', 4: 'vier', 5: 'fuenf', 6: 'sechs'}
        n = len(spitze)
        wort = ZAHLWORT.get(n, str(n))
        # Nach Platz sortiert, nicht nach Bewertungsanzahl: Ein Satz ueber eine Rangfolge
        # nennt die Plaetze in der Reihenfolge, in der sie auf der Seite stehen.
        def _platz(q):
            return next((i for i, (s, *_) in enumerate(liste_def['ordnung'], 1)
                         if s == q['slug']), 10 ** 6)
        teile = []
        for q in sorted(spitze, key=_platz):
            pl = _platz(q)
            wo = f'Platz {pl}' if pl < 10 ** 6 else 'nicht auf dieser Liste'
            teile.append(f'{esc(vollname(q))} ({wo}, '
                         f'{anzahl_text(bewertung(q)[1])} Bewertungen)')
        aufzaehlung = (' und '.join(teile) if n == 2
                       else ', '.join(teile[:-1]) + ' und ' + teile[-1])
        return (f'<p><strong>Die beste Bewertung teilen sich {wort}:</strong> '
                + aufzaehlung
                + f' kommen {"beide" if n == 2 else f"alle {wort}"} auf '
                + f'{sterne_text(bst)} Sterne und liegen damit '
                + f'{liste_def["menge_dativ"]} vorn. Platz 1 hat {sterne_text(est)}. '
                + f'{"Welcher der beiden" if n == 2 else "Welches davon"} besser '
                + f'passt, hängt an den Daten in ihren Zeilen, '
                + f'nicht an der Sternzahl.</p>')
    if best['slug'] == erster['slug']:
        return (f'<p><strong>Nach Sternen führt derselbe:</strong> {esc(name)} hat mit '
                f'{sterne_text(bst)} Sternen aus {anzahl_text(bn)} Bewertungen die beste '
                f'Bewertung {liste_def["menge_dativ"]}, und er steht hier auf Platz 1.</p>')

    # Was in den DATEN gegen Platz 1 spricht. Nur gemessene Unterschiede.
    nachteile = []
    if ist_kabelgebunden(best):
        nachteile.append('er ist kabelgebunden, hat also keine Funkverbindung')
    fokus = liste_def['fokus']
    fehlt = [etikett for schluessel, etikett in PLATTFORM_TEXT
             if (not fokus or schluessel in fokus)
             and schluessel in pliste(erster, 'worksOn')
             and schluessel not in pliste(best, 'worksOn')]
    if fehlt:
        nachteile.append('er läuft laut unserer Kompatibilitätsliste nicht an '
                         + ' und nicht an '.join(fehlt))
    bp, ep = preis_zahl(best), preis_zahl(erster)

    platz = next((i for i, (s, *_) in enumerate(liste_def['ordnung'], 1)
                  if s == best['slug']), None)
    wo = (f'Er steht hier auf Platz {platz}' if platz
          else 'Er steht nicht einmal auf dieser Liste')
    # Der Preis zaehlt in BEIDE Richtungen. Die erste Fassung nannte ihn nur, wenn er
    # fuer den Kandidaten sprach -- auf der iPhone-Liste stand dann "in den Daten spricht
    # nichts gegen Platz 1" ueber ein Modell, das 110 € mehr kostet. Ein Abschnitt, der
    # die eigene Reihenfolge in Frage stellt, muss die Gegenzahl genauso nennen.
    preisteil, teurer = '', None
    if bp is not None and ep is not None:
        if bp < ep:
            preisteil = f' und kostet mit {bp} € dabei {ep - bp} € weniger als Platz 1'
        elif bp > ep:
            teurer = f'er kostet mit {bp} € ganze {bp - ep} € mehr als Platz 1'
            nachteile.append(teurer)

    if nachteile:
        grund = ('Was in seinen Daten gegen Platz 1 spricht: '
                 + '; '.join(nachteile) + '.')
        # Der Schlusssatz muss zur ART des Nachteils passen. "Wer darauf verzichten kann"
        # ergibt bei einem reinen PREIS-Nachteil keinen Sinn: Auf einen hoeheren Preis
        # verzichtet man nicht, man zahlt ihn. Genau so stand es in der ersten Fassung
        # auf der iPhone-Liste, wo der Kandidat 110 € teurer ist.
        schluss = ('Wer das Geld ausgeben will, bekommt die bessere Bewertung.'
                   if nachteile == [teurer] else
                   'Wer darauf verzichten kann, kauft ihn.')
    else:
        # Kein messbarer Nachteil: Das wird gesagt, nicht ueberspielt. Genau dieser Fall
        # tritt auf der Android-Liste ein, sobald der Fokus das iPhone-Argument streicht.
        grund = ('In den Daten dieser Liste spricht nichts gegen Platz 1. Die '
                 'Reihenfolge ist an dieser Stelle ein redaktionelles Urteil, kein '
                 'Rechenergebnis.')
        schluss = 'Wer nach Bewertung kauft, nimmt ihn.'
    return (f'<p><strong>Die Zahl, die gegen unsere Reihenfolge spricht:</strong> Die '
            f'beste Bewertung {liste_def["menge_dativ"]} hat nicht Platz 1, sondern '
            f'{esc(name)} mit {sterne_text(bst)} Sternen aus {anzahl_text(bn)} '
            f'Bewertungen (Platz 1: {sterne_text(est)}). {wo}{preisteil}. {grund} '
            f'{schluss}</p>')


# --------------------------------------------------------------------------- Rendern
def _detail_label(detail):
    """"Zum Test" nur dort, wo wir wirklich getestet haben.

    Unter /produkte/ liegen generierte Datenblaetter, keine Tests. Genau ein Produkt der
    23 Positionen faellt darunter (8bitdo-ultimate-mobile), und die Handfassung hatte das
    richtig: Dort stand "Zum Kurzcheck". Meine erste Generator-Fassung schrieb pauschal
    "Zum Test" und haette damit auf einer Seite, deren Thema Glaubwuerdigkeit ist, einen
    Test behauptet, den es nicht gibt.

    Sichtbar ist dieses Etikett nur ohne JavaScript: main.js benennt jeden .btn-detail
    zur Laufzeit in "Mehr erfahren" um. Fuer §A2 (und damit fuer die KI-Crawler, die kein
    JS ausfuehren) ist es trotzdem die ausgelieferte Wahrheit.
    """
    return 'Zum Kurzcheck' if detail.startswith('/produkte/') else 'Zum Test'


def karte(p, nummer, label, badge_klasse, art_klasse, ebene='h3'):
    """Eine Position. Markup wie bisher, Werte aus products.json, plus Faktenzeile.

    Der Preis wird als ROHSTRING aus `price` gerendert, nicht als Zahl aus
    `preis_zahl()`. Die erste Fassung schrieb `{preis_zahl(p)} €` und erzeugte damit
    einen zweiten Schreiber fuer dieselbe Stelle: `sync_product_values.py` setzt dort den
    Rohstring. Bei einem Preis mit "ca." (7 der 42) gab es danach KEINEN Zustand, in dem
    beide Gates gruen sind -- wer zuletzt lief, machte den anderen rot. Heute steht kein
    solcher Preis auf einer Liste, der Patt war also latent und genau deshalb gefaehrlich.
    Derselbe Fehler schrieb bei unlesbarem Preis "None €" auf die Seite, und `--check`
    blieb gruen, weil der Generator mit sich selbst konsistent war.

    `ebene`: In HEAD trugen die drei /vergleich/-Seiten `h2`, die Gesamtliste `h3` (dort
    steht eine h2 darueber). Fest verdrahtetes `h3` hat daraus auf drei Seiten einen
    Sprung h1 -> h3 gemacht.
    """
    badge = (f'<span class="pcard-badge {badge_klasse}">#{nummer} {esc(label)}</span>'
             if label else f'<span class="pcard-badge">#{nummer}</span>')
    chips = ''.join(f'<span class="spec-tag"><span class="k">{esc(k)}</span> '
                    f'{esc(v)}</span>'
                    for k, v in _chips(p))
    detail = (pfeld(p, 'detail') or '').rstrip('/') + '/'
    img = pfeld(p, 'img')
    return f'''<article class="pcard{art_klasse}">
  <div class="pcard-img">{badge}<div class="product-icon">🎮</div></div>
  <div class="pcard-body">
    <div class="pcard-brand">{esc(pfeld(p, 'brand'))}</div><{ebene} class="pcard-name">\
{esc(pfeld(p, 'name'))}</{ebene}>
    <p class="pcard-claim">{esc(pfeld(p, 'claim'))}</p>
    <p class="pcard-fakten">{faktenzeile(p)}</p>
    <div class="pcard-specs">{chips}</div>
    <div class="pcard-foot">
      <div class="price-row"><span class="price">{esc(pfeld(p, 'price'))}\
<span class="price-approx">UVP</span></span><span class="in-stock">Verfügbar</span></div>
      <div class="pcard-actions">
        <a href="{esc(detail)}" class="btn-detail">{_detail_label(detail)}</a>
        <a class="btn-amazon" data-asin="{esc(pfeld(p, 'asin'))}" \
data-product="{esc(pfeld(p, 'slug'))}" href="#" data-img="{esc(img)}">Kaufen →</a>
      </div>
    </div>
  </div>
</article>'''


# Welche Spec-Chips eine Karte zeigt: die aus products.json, ohne `Bew.` (steht jetzt in
# der Faktenzeile) und ohne Leerwerte. Die 14 ungedeckten Chips der Handfassung fallen
# damit weg -- absichtlich, siehe UNGEDECKTE SPECS im Modul-Docstring.
_CHIP_AUS = ('Bew.',)


def _chips(p):
    return [(k, v) for k, v in spec_paare(p) if k not in _CHIP_AUS and v.strip()][:3]


def schema(liste_def, produkte):
    """ItemList ueber die SICHTBARE Reihenfolge, vollstaendig.

    Die drei /vergleich/-Seiten hatten gar kein ItemList, obwohl ihre Titel "Top 5"
    versprechen. /controller/beste/ fuehrte 3 von 10 -- das ist laut verify.py Z. 687
    bei Seiten mit Top-Auswahl ausdruecklich erlaubt, hier aber IST die Rangfolge der
    Inhalt der Seite, also wird sie vollstaendig ausgezeichnet.
    """
    eintraege = [{'@type': 'ListItem', 'position': i,
                  'name': vollname(p),
                  'url': 'https://smartphone-controller.com'
                         + (pfeld(p, 'detail') or '').rstrip('/') + '/'}
                 for i, p in enumerate(produkte, 1)]
    obj = {'@context': 'https://schema.org', '@type': 'ItemList',
           'name': liste_def['listenname'], 'numberOfItems': len(eintraege),
           'itemListOrder': 'https://schema.org/ItemListOrderDescending',
           'itemListElement': eintraege}
    return ('<script type="application/ld+json">'
            + json.dumps(obj, ensure_ascii=False) + '</script>')


def block(inhalt):
    return f'<!-- {MARKER}:START -->\n{inhalt}\n<!-- {MARKER}:END -->'


ANF, END = f'<!-- {MARKER}:START -->', f'<!-- {MARKER}:END -->'


# Der Anker ist das Karten-Gitter. `<div>` verschachtelt, und ein Regex kann das nicht --
# P-13 Mechanismus 23, in diesem Repo fuenfmal dieselbe Klasse. Deshalb gezaehlt.
# Gemessen am 04.10.2026: genau EIN `grid-auto` je Bestenlisten-Seite, und es enthaelt
# alle Karten (10 / 5 / 3 / 5 article). Mehr als eines ist ein Befund, nicht eine Wahl.
ANKER_AUF = '<div class="grid-auto">'


# Der Generator fasst das `sec-head` davor NICHT an. Zwei Versuche, zwei Befunde:
# Erst sollte der Block den "Ergonomie"-Satz mituebernehmen und rutschte dafuer ueber
# alles, was "strukturell aussieht" -- und verschluckte das `</div>`, das `sec-head`
# schliesst ("laesst 1 <div> offen", gefunden von der HTML-Pruefung in verify.py). Dann
# haette der Block sein eigenes `</div>` mitschreiben muessen, aber nur auf der einen
# Seite, die ein `sec-head` hat: Markup, dessen Form von der Umgebung abhaengt.
# Jetzt: Der Block beginnt immer am Gitter, die Regel steht als erster Absatz DARIN, und
# ein stehengebliebener Sortier-Satz ausserhalb ist ein Gate in verify.py (§A6) statt
# eine Textoperation hier.
def gitter(s):
    """(Start, Ende) des Karten-Gitters inklusive seines </div>, oder None.

    Ende heisst: hinter dem </div>, das ANKER_AUF schliesst. Gezaehlt werden oeffnende
    und schliessende div-Tags; `<div/>` gibt es in HTML nicht, selbstschliessende
    Elemente sind keine div.
    """
    if s.count(ANKER_AUF) != 1:
        return None
    start = s.index(ANKER_AUF)
    i, tiefe = start + len(ANKER_AUF), 1
    for m in re.finditer(r'<div\b|</div\s*>', s[i:]):
        tiefe += 1 if not m.group(0).startswith('</') else -1
        if tiefe == 0:
            return start, i + m.end()
    return None


def baue(liste_def, items):
    """Der ganze generierte Abschnitt einer Liste, plus die Befunde dieser Liste."""
    nach_slug = {pfeld(p, 'slug'): p for p in items}
    befunde, produkte, zeilen = [], [], []

    for i, (slug, label, bklasse, aklasse) in enumerate(liste_def['ordnung'], 1):
        p = nach_slug.get(slug)
        if p is None:
            befunde.append(f'{liste_def["datei"]}: Platz {i} nennt "{slug}", '
                           f'products.json kennt den Slug nicht')
            continue
        st, _ = bewertung(p)
        if st is None:
            # P-14 Mechanismus 3 verlangt, dass JEDE Position ihre Zahlen zeigt. Ohne
            # diesen Befund rutschte eine Position ohne lesbare `Bew.` still durch: Die
            # Faktenzeile liess die Sterne einfach weg, und alle B6-Gates blieben gruen.
            # Der Pflicht-Mechanismus, um den dieses Paket gebaut ist, war nicht gegatet.
            befunde.append(f'{liste_def["datei"]}: Platz {i} ({slug}) hat keine lesbare '
                           f'`Bew.` — eine Position ohne Bewertung kann der Leser nicht '
                           f'gegenrechnen (P-14 Mechanismus 3)')
            continue
        if st < A6_SCHWELLE:
            befunde.append(f'{liste_def["datei"]}: Platz {i} ({slug}) hat '
                           f'{sterne_text(st)} Sterne, unter der §A6-Schwelle '
                           f'{sterne_text(A6_SCHWELLE)} — eine Bestenliste fuehrt das '
                           f'nicht')
            continue
        if preis_zahl(p) is None:
            # Sonst stand frueher "None €" auf der Seite, und `--check` blieb gruen, weil
            # der Generator mit seinem eigenen Fehler konsistent war.
            befunde.append(f'{liste_def["datei"]}: Platz {i} ({slug}) hat keinen lesbaren '
                           f'Preis ("{pfeld(p, "price")}")')
            continue
        produkte.append(p)
        zeilen.append(karte(p, i, label, bklasse, aklasse,
                            liste_def.get('kartenebene', 'h3')))

    # Die Seite verspricht in Titel, og:title, twitter:title und Ueberschrift eine Zahl
    # ("Top 10", "Top 5"). Wer eine Position aus `ordnung` nimmt, bricht dieses
    # Versprechen -- und nichts hat das gemerkt: Nach dem Entfernen standen viermal
    # "Top 10" ueber neun Karten, alle Gates gruen. Schlimmer, die eigene Batterie fuehrte
    # genau diesen Vorgang als LEGITIMEN Fall. Dieselbe Gate-Klasse gibt es fuer den
    # Finder laengst (verify.py, "verspricht 'Top-{n}'").
    if liste_def.get('topn') is not None and len(zeilen) != liste_def['topn']:
        befunde.append(f'{liste_def["datei"]}: die Seite verspricht '
                       f'"Top {liste_def["topn"]}", der Block fuehrt aber '
                       f'{len(zeilen)} Positionen. Entweder `topn` und die Texte der '
                       f'Seite nachziehen oder die Position wieder aufnehmen')

    menge = [p for p in items if liste_def['menge'](p)]
    kopf = (f'<p class="sec-sub">{regeltext(liste_def, menge)}</p>' if menge else '')
    ehrlich = (f'<div class="besten-ehrlich">{ehrlichtext(liste_def, menge, produkte[0])}'
               f'</div>' if menge and produkte else '')
    inhalt = '\n'.join([x for x in [kopf, ANKER_AUF,
                                    '\n'.join(zeilen), '</div>', ehrlich,
                                    schema(liste_def, produkte)] if x])
    return inhalt, befunde


def main():
    nur_pruefen = '--check' in sys.argv
    items = json.load(open('assets/data/products.json', encoding='utf-8'))
    geaendert, alle_befunde = [], []

    for ld in LISTEN:
        f = ld['datei']
        if not os.path.exists(f):
            alle_befunde.append(f'{f}: Datei fehlt')
            continue
        inhalt, befunde = baue(ld, items)
        alle_befunde += befunde
        if befunde:
            # Nicht schreiben, wenn diese Liste Befunde hat. Die erste Fassung schrieb
            # trotzdem -- und weil `karte()` aus `ordnung` zaehlt und `schema()` aus den
            # ueberlebenden Produkten, standen danach Badge-Nummern wie 1..9, 11 neben
            # ItemList-Positionen 1..10. Live kam das nie an (Gate rot), der Arbeitsbaum
            # war trotzdem kaputt.
            continue
        s = open(f, encoding='utf-8').read()
        # ZWEI Faelle, beide ausdruecklich -- nicht "entfernen, dann einsetzen".
        # Der Block enthaelt sein eigenes Gitter; wuerde man ihn erst entfernen, waere
        # der Anker mit weg und Lauf 2 faende nichts mehr. Das war der erste Entwurf,
        # und er waere beim zweiten Lauf mit "Anker kommt 0x vor" gestorben.
        #   Lauf 1   : die Handfassung (das Gitter) wird ersetzt
        #   Lauf 2..n: der eigene Block wird ersetzt
        if s.count(ANF) == 1 and s.count(END) == 1 and s.index(ANF) < s.index(END):
            a, b = s.index(ANF), s.index(END) + len(END)
        else:
            if s.count(ANF) or s.count(END):
                alle_befunde.append(f'{f}: Marker {MARKER} unvollstaendig oder doppelt '
                                    f'({s.count(ANF)}x START, {s.count(END)}x END)')
                continue
            stelle = gitter(s)
            if stelle is None:
                n = s.count(ANKER_AUF)
                alle_befunde.append(
                    f'{f}: Anker {ANKER_AUF} ' +
                    (f'kommt {n}x vor — eindeutig muss er sein' if n != 1
                     else 'wird nicht geschlossen (div-Zaehlung laeuft aus)'))
                continue
            a, b = stelle
        neu = s[:a] + block(inhalt) + s[b:]
        if neu != s:
            geaendert.append(f)
            if not nur_pruefen:
                open(f, 'w', encoding='utf-8').write(neu)
            print(f'  {"wuerde geaendert" if nur_pruefen else "geschrieben"}: {f}')

    for b in alle_befunde:
        print(f'  FEHLER: {b}')
    print(f'\n{len(LISTEN)} Bestenlisten, {sum(len(l["ordnung"]) for l in LISTEN)} '
          f'Positionen, {len(geaendert)} Datei(en) '
          f'{"abweichend" if nur_pruefen else "geschrieben"}, '
          f'{len(alle_befunde)} Befund(e)')
    if alle_befunde:
        return 1
    if nur_pruefen and geaendert:
        print('  Fix: python3 scripts/gen_bestenliste.py')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
