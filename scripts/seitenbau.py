#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
seitenbau.py — gemeinsame Bausteine generierter Seitenbloecke (Pattern P-19, 01.11.2026)

Zahlwort, Substantiv, Artikel und Verb kommen aus DERSELBEN Zahl. Von Hand
gebeugt wird nichts. Entstanden in sieben Pruefrunden am Zubehoer-Ast, wo
"Ein der sieben Sets liegt unter 3,8 Sternen" und "bei ein Sets steht keine
Massangabe" die haeufigste Einzelklasse waren: Die Zahl kam aus products.json,
Substantiv und Verb standen fest im Text, und beide Saetze waren am Tag des
Baus richtig und beim naechsten Preisabgleich falsch.

Hier und nicht im Generator, weil die Regeln an EINE Stelle gehoeren -- dieselbe
Begruendung wie bei produktdaten.py. Wer einen zweiten Generator baut, importiert
sie, statt sie nachzubauen.

Zwei Teile: die Grammatik (Pattern P-19) und die HTML-Bausteine, die bei jedem
generierten Block gleich sind -- FAQ-Liste, FAQPage- und ItemList-Schema, beide aus
dem ENDSTAND gerendert, damit Schema und sichtbarer Text nicht auseinanderlaufen.

Benutzt von: gen_zubehoer_sections.py, gen_tablet_hub.py
"""

import json
import re
from decimal import Decimal, ROUND_HALF_UP

import produktdaten as pd


ZAHLWORT = {1: 'ein', 2: 'zwei', 3: 'drei', 4: 'vier', 5: 'fünf', 6: 'sechs',
            7: 'sieben', 8: 'acht', 9: 'neun', 10: 'zehn', 11: 'elf', 12: 'zwölf',
            13: 'dreizehn', 14: 'vierzehn'}


def zw(n):
    """Zahlwort vor einem Substantiv: "ein Set", "zwei Sets"."""
    keine_null(n, 'zw')
    return ZAHLWORT.get(n, str(n))


def zwn(n):
    """Zahlwort ALLEIN stehend: "eins der vier Sets", nicht "ein der vier Sets".

    Dieselbe Zahl, zwei Formen. Die erste Fassung nutzte ueberall zw() und schrieb
    damit auf drei Seiten "Ein der sieben Sets liegt unter 3,8 Sternen".
    """
    keine_null(n, 'zwn')
    return 'eins' if n == 1 else ZAHLWORT.get(n, str(n))


def eur(n):
    """Euro-Betrag ohne Nachkommastellen, so wie products.json ihn fuehrt."""
    return f'{n} €'


def komma(x, dec=2):
    """Deutsche Schreibweise, kaufmaennisch gerundet.

    f'{0.175:.2f}' gibt '0.17' — die Binaerdarstellung von 0,175 liegt knapp
    darunter. Der Preis pro Huelse (7 € / 40 Stueck) stand damit um einen Cent
    unter dem, was ein Leser nachrechnet. Decimal rundet die Zahl, nicht ihre
    Naeherung.
    """
    q = Decimal(1).scaleb(-dec)
    return str(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP)).replace('.', ',')


# ---------------------------------------------------------------- Datenschicht

def gross(text):
    """Ersten Buchstaben gross, Rest unangetastet. `str.capitalize()` kleint den
    Rest und haette aus "Ein Set" ein "Ein set" gemacht."""
    return text[:1].upper() + text[1:]


def mz(n, singular, plural):
    """Zahlwort plus Substantiv im richtigen Numerus: "ein Set", "zwei Sets".

    Das Substantiv kommt OHNE Artikel. Mit "das Set" als Singular lieferte die
    Funktion "ein das Set" -- ein Aufrufer-Fehler, aber einer, der sich wiederholt,
    wenn er nicht hier steht.
    """
    keine_null(n, 'mz')
    return f'{zw(n)} {singular}' if n == 1 else f'{zw(n)} {plural}'


def mz_dativ(n, singular, plural):
    """Dasselbe im Dativ: "einem Set", "zwei Sets"."""
    keine_null(n, 'mz_dativ')
    return f'einem {singular}' if n == 1 else f'{zw(n)} {plural}'


def keine_null(k, wo):
    """Null ist keine Mengenangabe, sondern ein anderer Satz.

    `anteil(0, 3, "Geräte")` lieferte "0 der drei Geräte", und der Satz drumherum war
    dann inhaltlich leer: Nichts ist "unbequem", wenn kein Produkt unter der Schwelle
    liegt, und die graue Markierung in der Tabelle verwiese auf nichts. Eine Null-Form
    zu erfinden waere die falsche Antwort gewesen; der Satz gehoert weggelassen. Die
    Helfer brechen deshalb ab, damit niemand den leeren Fall stillschweigend
    formuliert (Pruefbericht 01.11., Runde 4).
    """
    if k == 0:
        raise SystemExit(
            f'FEHLER: {wo}(0, ...) aufgerufen. Ein Satz ueber eine leere Menge gehoert '
            f'weggelassen, nicht mit "null" formuliert -- siehe tablet_satz/ohne_satz.')


def anteil(k, n, plural):
    """"vier der sieben Sets", bei Vollstaendigkeit "alle sieben Sets".

    Gibt KLEIN zurueck. Die erste Fassung schrieb immer gross und lieferte damit
    mitten im Satz "Weil Zwei der drei Modelle ...". Wo ein Satz beginnt, steht
    `gross()` jetzt an der Aufrufstelle, und man sieht dort, dass es gewollt ist.
    """
    keine_null(k, 'anteil')
    if k == n:
        # "alle zwei Modelle" ist kein Deutsch, dort heisst es "beide".
        return f'beide {plural}' if n == 2 else f'alle {zw(n)} {plural}'
    return f'{zwn(k)} der {zw(n)} {plural}'


def die_mz(n, singular, plural):
    """"das eine Set" / "die drei Sets" -- bestimmter Artikel plus Zahlwort.

    Nur fuer saechliche Substantive (Set, Gerät). Entstanden, weil der
    Material-Satz seine beiden Haelften unterschiedlich gebaut hatte: Die
    Polyester-Haelfte hatte einen Singular-Zweig, die andere nicht, und schrieb
    bei einem Set "Die ein Sets ohne Polyesterfaser steht bei 4,4 Sternen".
    """
    keine_null(n, 'die_mz')
    return f'das eine {singular}' if n == 1 else f'die {zw(n)} {plural}'


def vb(n, singular, plural):
    """Verbform zur Zahl. Der Pruefbericht hat drei Stellen gefunden, an denen
    Substantiv und Verb fest im Text standen, waehrend die Zahl aus den Daten kam:
    "bei ein Sets steht", "ein nennen gar keine", "drei hat zwei". Alle drei waren
    heute richtig und beim naechsten Abgleich falsch. Ein Gate haette die Zahl nur
    festgenagelt und damit die naechste korrekte Datenpflege blockiert; die Grammatik
    gehoert an die Zahl, nicht in ein Gate (P-13 Mechanismus 6)."""
    keine_null(n, 'vb')
    return singular if n == 1 else plural


def absatz(inhalt):
    """Ein <p> nur, wenn es etwas einzurahmen gibt.

    Der Rahmen stand fest und nur sein Inhalt unter Bedingung: Waren Schwellen-
    und Material-Satz beide leer, blieb ein <p></p> stehen, und `.zub-ext p` macht
    daraus eine sichtbare Luecke von 14 Pixeln.
    """
    return f'    <p>{inhalt}</p>\n' if inhalt.strip() else ''


def spanne(gruppe):
    """"bei 4,2 Sternen" oder "zwischen 4,2 und 4,4 Sternen"."""
    lo = min(r['rating'] for r in gruppe)
    hi = max(r['rating'] for r in gruppe)
    if lo == hi:
        return f'bei {pd.sterne_text(lo)} Sternen'
    return f'zwischen {pd.sterne_text(lo)} und {pd.sterne_text(hi)} Sternen'


def faq_block(paare, titel, klasse):
    """Die FAQ-Sektion eines generierten Blocks.

    `klasse` ist die Seiten-CSS-Klasse des Generators ("zub-ext", "tab-ext"). Sie
    stand hier fest verdrahtet, solange es nur einen Generator gab -- ein geteilter
    Baustein darf die Klasse des ersten Aufrufers nicht mitschleppen.
    """
    items = '\n'.join(
        f'      <details class="faq-item"><summary>{q}</summary>'
        f'<div class="faq-a">{a}</div></details>'
        for q, a in paare)
    return (
        f'  <section class="section"><div class="container {klasse}" '
        f'style="max-width:820px">\n'
        f'    <h2>{titel}</h2>\n'
        '    <div class="faq-list">\n' + items + '\n    </div>\n'
        '  </div></section>\n')


def strip_tags(html):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', html)).strip()


def karten_slugs(html):
    """Die Produktkarten der Seite in ihrer sichtbaren Reihenfolge."""
    out = []
    for m in re.finditer(r'<article class="pcard[^"]*"[^>]*>.*?</article>', html, re.S):
        s = re.search(r'data-product="([^"]+)"', m.group(0))
        if not s:
            raise SystemExit('FEHLER: Produktkarte ohne data-product — Reihenfolge nicht '
                             'bestimmbar')
        out.append(s.group(1))
    return out


def itemlist_schema(html, rows, listenname, canonical):
    """ItemList aus der SICHTBAREN Kartenreihenfolge, Namen aus products.json.

    Nicht aus der Produktliste gerendert, sondern aus der Seite: Ein Schema, das
    eine andere Reihenfolge behauptet als die Karten, ist §A4-Verstoss am Kern.
    """
    slugs = karten_slugs(html)
    nach_slug = {r['slug']: r for r in rows}
    fehlt = [s for s in slugs if s not in nach_slug]
    if fehlt:
        raise SystemExit(f'FEHLER: Karte(n) {fehlt} gehoeren nicht zu dieser Kategorie')
    fehlend = [r['slug'] for r in rows if r['slug'] not in slugs]
    if fehlend:
        raise SystemExit(f'FEHLER: {fehlend} steht in products.json, aber nicht als Karte '
                         f'auf der Seite')
    elemente = [{'@type': 'ListItem', 'position': i,
                 'name': nach_slug[s]['name'],
                 'url': 'https://smartphone-controller.com' + nach_slug[s]['detail']}
                for i, s in enumerate(slugs, 1)]
    return json.dumps({'@context': 'https://schema.org', '@type': 'ItemList',
                       'name': listenname, 'url': canonical,
                       'numberOfItems': len(elemente),
                       'itemListElement': elemente}, ensure_ascii=False)


def faqpage_schema(block):
    """FAQPage aus den sichtbaren details-Bloecken des erzeugten Blocks (§A4)."""
    items = re.findall(
        r'<details class="faq-item"><summary>(.*?)</summary>'
        r'<div class="faq-a">(.*?)</div></details>', block, re.S)
    if not items:
        raise SystemExit('FEHLER: kein FAQ-Eintrag im erzeugten Block')
    return json.dumps(
        {'@context': 'https://schema.org', '@type': 'FAQPage',
         'mainEntity': [{'@type': 'Question', 'name': strip_tags(q),
                         'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(a)}}
                        for q, a in items]}, ensure_ascii=False)


# Masseinheiten, bei denen die Zahl ALLEIN nichts beweist: "40" steht als Set-Groesse
# in den Daten, "40 Stunden Akku" steht nirgends -- und genau diese Form ist in diesem
# Projekt schon live gegangen. Fuer diese Einheiten wird das PAAR geprueft.
#
# GRENZE, benannt statt verschwiegen: Das ist und bleibt eine von Hand gepflegte
# Positivliste. Eine Einheit, die hier fehlt, wird NICHT geprueft -- die Zahl muss dann
# nur fuer sich belegt sein. Der Pruefbericht vom 01.11. hat das an "18 Dezibel"
# gezeigt; die Einheit steht seitdem drin, das Prinzip bleibt. Wer eine neue Einheit in
# den Text schreibt, traegt sie hier ein.
#
# Zwei Versuche, die Liste ueberfluessig zu machen, sind gescheitert und stehen hier,
# damit sie niemand ein drittes Mal unternimmt:
#   1. Jedes Wort hinter einer Zahl als Einheit lesen. Meldete "3,3 aus", "6 weg" und
#      "77 Controller" und waere mit Ausnahmen aufgeweicht worden, bis nichts bleibt.
#   2. Die Liste aus dem Datenkern ernten. Liefert aus "Smartphone bis 11mm" und
#      "L1R1/L2R2" die Pseudo-Einheiten "bis" und "r" und machte damit den eigenen,
#      korrekten Satz "3 bis 13 Millimetern" rot.
_EINHEIT_NORM = {
    'mm': 'millimeter', 'millimeter': 'millimeter', 'millimetern': 'millimeter',
    'cm': 'zentimeter', 'zentimeter': 'zentimeter',
    'g': 'gramm', 'gramm': 'gramm', 'kg': 'kilogramm', 'kilogramm': 'kilogramm',
    'w': 'watt', 'watt': 'watt', 'v': 'volt', 'volt': 'volt',
    'mah': 'mah', 'wh': 'wattstunden',
    'std': 'stunden', 'stunde': 'stunden', 'stunden': 'stunden',
    'minute': 'minuten', 'minuten': 'minuten', 'min': 'minuten',
    'sekunde': 'sekunden', 'sekunden': 'sekunden', 'ms': 'millisekunden',
    'tag': 'tage', 'tage': 'tagen', 'tagen': 'tagen',
    'monat': 'monate', 'monate': 'monate', 'monaten': 'monate',
    'jahr': 'jahre', 'jahre': 'jahre', 'jahren': 'jahre',
    'grad': 'grad', '°c': 'grad', '°': 'grad', 'kelvin': 'kelvin',
    '%': 'prozent', 'prozent': 'prozent',
    'hz': 'hertz', 'hertz': 'hertz', 'fps': 'fps',
    'db': 'dezibel', 'dezibel': 'dezibel',
    'zoll': 'zoll',
}


def masse(text):
    """Alle (Zahl, Mass)-Paare eines Textes, Bereiche aufgeloest.

    "5-13mm" liefert (5, millimeter) UND (13, millimeter): Eine Spanne belegt beide
    Enden. Ohne diese Zeile waere die Obergrenze aus den Trigger-Specs unbelegt und
    das Gate haette den eigenen, korrekten Satz rot gemacht.
    """
    t = re.sub(r'<[^>]+>', ' ', text).lower().replace('\u2009', ' ')
    zahl = r'(\d+(?:[.,]\d+)?)'
    wort = r'([a-zäöüß°%]{1,12})'
    paare = set()
    for a_, b_, u in re.findall(zahl + r'\s*(?:–|-|bis)\s*' + zahl + r'\s*' + wort, t):
        if u in _EINHEIT_NORM:
            paare |= {(a_, _EINHEIT_NORM[u]), (b_, _EINHEIT_NORM[u])}
    for z, u in re.findall(zahl + r'\s*(?:≥|≤|<|>)?\s*' + wort, t):
        if u in _EINHEIT_NORM:
            paare.add((z, _EINHEIT_NORM[u]))
    return paare


def check_units(block, rows, extra, wo, zusatz=''):
    """Jedes Mass im Text muss als dasselbe Mass in den Quellen stehen.

    `zusatz` nimmt Belegtexte auf, die NICHT aus products.json stammen -- etwa die
    "ausziehbare Bruecke bis 215 mm" aus der eigenen Testseite. Ohne diesen Weg
    muesste eine belegte Angabe entweder in den Datenkern wandern oder das Gate
    waere fuer sie blind; beides ist schlechter als eine zweite benannte Quelle.
    """
    quelle = ' '.join(
        ' '.join(v for _k, v in r['specs']) + ' ' + r['claim']
        for r in list(rows) + list(extra)) + ' ' + zusatz
    offen = sorted(masse(block) - masse(quelle))
    if offen:
        raise SystemExit(
            f'MASS-GATE ({wo}): Angabe(n) ohne Deckung in den Quellen '
            f'(products.json und benannte Belege): '
            + ', '.join(f'{z} {u}' for z, u in offen))


def beleg_umgebung(raum, suchtext):
    """Steht der Treffer in einer NACHTEILS-Umgebung? None, wenn er fehlt.

    Herausgeloest aus `gen_vergleich.py`, wo diese Pruefung in Runde 5/6 des
    Vergleichs-Prueflaufs entstanden ist: Dort belegte ein Haekchen fuer
    "RGB: ✓ Chroma" mit einer Zeile aus dem SCHWAECHEN-Block der eigenen
    Produktseite -- der Beleg bewies das Gegenteil. Ein zweiter Generator darf das
    nicht nachbauen, sondern importiert es (§A5 (3)).

    GRENZE: Das Fenster ist 160 Zeichen vor dem Treffer. Eine Ueberschrift weiter
    weg sieht die Pruefung nicht.
    """
    negativ = None
    for m in re.finditer(re.escape(suchtext), raum):
        davor = raum[max(0, m.start() - 160):m.start()]
        n = (('✗' in davor and '✓' not in davor.rsplit('✗', 1)[1])
             or 'con-item' in davor[-90:]
             or bool(re.search(r'<h3>\s*Schwächen', davor)))
        negativ = n if negativ is None else (negativ or n)
        if n:
            break
    return negativ


def und_liste(teile):
    """"A", "A und B", "A, B und C" -- eine Aufzaehlung, die sich liest."""
    teile = list(teile)
    if len(teile) == 1:
        return teile[0]
    return ', '.join(teile[:-1]) + ' und ' + teile[-1]


def rest_phrase(n, singular, plural):
    """"das übrige Modell" / "die zwei übrigen Modelle".

    Nicht ueber `mz()`: Das Substantiv traegt hier Artikel und Adjektiv, und `mz()`
    setzt das Zahlwort davor. Genau diese Verwechslung hat im ersten Entwurf dieser
    Seite viermal zugeschlagen ("ein ein Modell", "zwei zwei Modellen").

    Singular UND Plural kommen vom Aufrufer. Die erste Fassung haengte ein "e" an
    und haette aus "Controller" ein "Controllere" gemacht -- von Hand gebeugt wird
    nichts (P-19).
    """
    keine_null(n, 'rest_phrase')
    if n == 1:
        return f'das übrige {singular}'
    return f'die {zw(n)} übrigen {plural}'
