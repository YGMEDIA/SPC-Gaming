#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Die Leseregeln fuer products.json, je einmal.

Vorgeschichte: `specs` ist eine LISTE von Paaren, kein Objekt. Jede Stelle, die sie liest,
hat das auf eigene Weise getan, und beide gaengigen Schreibweisen brechen bei einem
Eintrag ab, der nicht genau zwei Elemente hat: `dict(specs)` mit ValueError, und
`for k, v in specs` beim Entpacken. Der Pruefer hat es am 02.10.2026 mit einem
einelementigen Spec-Eintrag gezeigt: verify.py brach in Zeile 430 ab, und der gesamte Lauf
dahinter fand nie statt. Ein Gate, das bei kaputten Daten abbricht statt zu melden, prueft
genau die kaputten Daten nicht -- und meldet dafuer auch die 200 Dinge nicht mehr, die
dahinter gestanden haetten.

Dass die Regel hierher gehoert und nicht in jede Datei, ist an diesem Projekt teuer
gelernt: sechs Gates in verify.py haben rohes Markup gelesen, jedes mit eigener Fassung
derselben Regel, und jeder Fehler musste sechsmal gefunden werden (_klartext). Die
Lesezeit stand in drei Dateien mit drei Formulierungen (lesezeit.py). Und beim Schliessen
GENAU DIESES Befundes habe ich erst eine Fassung in verify.py gebaut, obwohl kompat.py
schon eine hatte -- die elfte Kopie, beim Aufraeumen der zehn.

Noch nicht umgestellt (eigener Befund, nicht hier mitgeloest): die Lesestellen in
audit_prosa.py (Z. 37), gen_longtail.py (56), gen_hubs.py (81), gen_pages.py (38, 171),
sync_product_values.py (78, 133, 421), gen_brand_sections.py -- dazu die zwei eigenen
`Bew.`-Parser in gen_preisfrage.py (54) und verify.py (575), die beim Anlegen von
`bewertung()` hier schon existierten und absichtlich nicht im selben Schritt umgebaut
wurden: Beide sind in Gates verankert, deren Rot/Gruen-Proben an ihren heutigen Zahlen
haengen. Der Umbau ist ein eigenes Arbeitspaket mit eigener Probe -- und gen_preisfrage.py, das
eigene `preis()`, `spec()` und `bewertung()` fuehrt. Dessen `preis()` kennt die
Tausenderpunkt-Regel aus `preis_zahl()` nicht: "1.299 €" waere dort 1 und hier 1299. Heute
hat kein Preis einen Tausenderpunkt (gemessen: 0 von 42; die 7 Preise mit Punkt tragen alle
nur den Abkuerzungspunkt in "ca.", in 6 Schreibweisen von "ca. 30 €" bis "ca. 50 €"), der
Unterschied ist also latent -- und genau diese Liste ist der Ort, an dem die Klasse schon
einmal zu dritt uebersehen wurde (`platformLabel`, `gallery`, `video`, R26). Sie entpacken direkt und
brechen bei denselben Daten ab. gen_brand_sections.py tut das schon heute sichtbar: Es
bricht mit Traceback ab, wenn ein Spec-Wert eine Liste ist. Das ist seit dem 01.10. als
offener Befund in STATUS notiert; verify.py MELDET diesen Abbruch inzwischen als Fehler
("Generator-Abgleich abgebrochen") statt selbst mitzusterben, und das ist der Grund, warum
der Rest dieses Laufs trotzdem prueft.
"""
import re


# §A6-Schwelle: Produkte darunter bekommen eine Warnung statt einer Kaufempfehlung.
# Stand bis zum 04.10.2026 dreimal als Literal im Repo (verify.py, assets/js/finder.js,
# und beim Bau der Bestenlisten waere es das vierte Mal geworden). verify.py prueft die
# Fassung in finder.js gegen diese hier; Python-Seite importiert.
A6_SCHWELLE = 3.8


def spec_paare(p):
    """Die lesbaren (Schluessel, Wert)-Paare eines Produkts, beide als String.

    Kaputte Eintraege werden uebersprungen, aber NICHT stumm geschluckt: `formfehler()`
    meldet jeden einzelnen, und verify.py ruft das auf. Nur ueberspringen waere derselbe
    Blindfleck, den `unerfasst()` in sync_lesezeit.py schon einmal hatte -- zaehlen, was
    man findet, und das Gefundene fuer vollstaendig erklaeren.
    """
    if not isinstance(p, dict) or not isinstance(p.get('specs'), (list, tuple)):
        return []
    return [(str(e[0]), '' if e[1] is None else str(e[1]))
            for e in p['specs'] if isinstance(e, (list, tuple)) and len(e) == 2]


def spec(p, feld, default=''):
    """Das Spec-Feld mit genau diesem Schluessel, als String."""
    return next((v for k, v in spec_paare(p) if k == feld), default)


def spec_wie(p, anfang, default=''):
    """Das erste Spec-Feld, dessen Schluessel so beginnt ("Bew" trifft "Bew.")."""
    return next((v for k, v in spec_paare(p) if k.startswith(anfang)), default)


def preis_zahl(p):
    """Der Preis als ganze Zahl, oder None wenn keiner lesbar ist.

    str(): Ein Zahlenwert in `price` liess `re.search` mit TypeError abbrechen. Das stand
    an zwei Stellen noch offen, und mein eigener Beweis dafuer hat sie uebersehen, weil
    das Probe-Produkt die Filter davor nicht passierte. Eine Probe an EINEM Produkt
    beweist nichts ueber eine Stelle, die nur bestimmte Produkte erreichen.

    GRENZE: `.replace('.', '')` liest "1.299 €" als 1299; so rechnete die Mehrheit der
    Aufrufstellen schon. Heute traegt kein Preis einen Tausenderpunkt, die Regel ist also
    an keiner Stelle sichtbar. Der Satz hat hier bis R30 "die einzigen Punkte stehen in
    'ca. 40 €'" gelautet und damit eine vollstaendige Aufzaehlung behauptet; gemessen
    tragen 7 der 42 Preise einen Punkt, in 6 Schreibweisen, und keiner davon ist ein
    Tausenderpunkt -- richtig war die Aussage nur in dem, was sie nicht sagte. Darum
    zaehlt der Satz jetzt nicht mehr auf, sondern verify.py prueft die Eigenschaft
    ("Tausenderpunkt im Preis"): Bei einem vierstelligen Preis liest der Textvergleich in
    §A1 auf der SEITENseite weiter "299" und meldete dann einen Fehlalarm, und
    gen_preisfrage.py rechnete STILL mit 1. Dann gehoeren beide Stellen mitgeaendert.
    """
    m = re.search(r'(\d+)', str((p or {}).get('price') or '').replace('.', ''))
    return int(m.group(1)) if m else None


def bewertung(p):
    """(Sterne als float, Anzahl als int) aus `Bew.`, oder (None, None).

    Dasselbe Muster `([\\d,]+)\\s*\\(([\\d.]+)\\)` stand beim Anlegen dieser Funktion an
    drei Stellen einzeln: gen_preisfrage.py, verify.py und die Marken-Tabelle. Die
    Tausenderpunkt-Behandlung der Anzahl ("2.188" -> 2188) ist dabei dieselbe Klasse, die
    `preis_zahl()` als GRENZE fuehrt -- nur dass sie hier NOETIG ist, weil
    vierstellige Bewertungszahlen der Normalfall sind (gemessen: 7 der 28 Controller).

    Die Typsicherheit liegt eine Ebene tiefer: `spec_paare()` gibt jeden Wert schon als
    String zurueck, deshalb steht hier KEIN eigenes `str()`. Der Docstring hat bis R31
    eines begruendet, das im Code nicht steht -- eine Begruendung fuer eine Zeile, die es
    nicht gibt, ist genauso falsch wie eine fehlende Zeile.
    """
    m = re.match(r'([\d,]+)\s*\(([\d.]+)\)', spec_wie(p, 'Bew'))
    if not m:
        return None, None
    return float(m.group(1).replace(',', '.')), int(m.group(2).replace('.', ''))


def sterne_text(wert):
    """4.2 -> "4,2". Deutsche Schreibweise, damit die Zahl im Text der im JSON gleicht."""
    return f'{wert:.1f}'.replace('.', ',')


def anzahl_text(wert):
    """2188 -> "2.188". Dieselbe Schreibweise, in der `Bew.` die Anzahl fuehrt."""
    return f'{wert:,}'.replace(',', '.')


# Felder, die ueberall als String gelesen werden. Der achtzehnte Pruefbericht hat fuenf
# weitere Abbruchstellen gezeigt, alle derselben Klasse wie die Spec-Werte: `name` als
# Zahl liess `sorted()` mit TypeError abbrechen, `name` als Liste mit "cannot use 'tuple'
# as a set element", `brand` als Zahl dito, `claim` als Zahl liess `re.search` abbrechen,
# `img` als Zahl `.startswith`. Einzeln zu haerten hat in Runde 17 nicht gereicht -- es
# gibt keinen Grund, warum die naechste Lesestelle es besser machen sollte. Deshalb wird
# die FORM hier zentral gemeldet, und die Lesestellen nehmen str().
TEXTFELDER = ('slug', 'asin', 'name', 'brand', 'type', 'platform', 'platformLabel',
              'price', 'detail', 'claim', 'img')
LISTENFELDER = ('worksOn', 'specs', 'gallery')
OBJEKTFELDER = ('video',)
# Jedes Feld in products.json MUSS in einer der drei Listen stehen. Ohne diese Regel ist
# die Haertung ein Hase-und-Igel-Spiel: Runde 18 hat die Listen eingefuehrt, Runde 19 hat
# `platformLabel`, `gallery` und `video` darin vermisst und dafuer elf weitere
# Abbruchstellen belegt -- dieselbe Klasse, nur in den Feldern, die ich nicht aufgezaehlt
# hatte. Ein neues Feld erzwingt jetzt eine Entscheidung statt stillschweigend
# ungeprueft zu bleiben.


def text(p, feld, default=''):
    """Ein Textfeld als String. Nie None, nie eine Zahl, nie eine Liste.

    Die breite Typprobe hat nach dem Haerten von vier Einzelstellen weitere Abbrueche
    gefunden, die dasselbe Muster haben:
    `name` als Zahl in einem len(), `name` als None in einem `in`-Test, `platform` und
    `type` als Liste oder Objekt als dict-Schluessel, `worksOn` als Zahl in einem set().
    Zwei Runden Einzelflicken haben gezeigt, dass es keinen Grund gibt, warum die
    naechste Lesestelle es besser machen sollte.
    """
    w = (p or {}).get(feld) if isinstance(p, dict) else None
    return default if w is None else str(w)


def liste(p, feld):
    """Ein Listenfeld als Liste von Strings. Ein Nicht-Listenwert ergibt []."""
    w = (p or {}).get(feld) if isinstance(p, dict) else None
    return [str(x) for x in w] if isinstance(w, (list, tuple)) else []


def formfehler(items):
    """Jede Form, die die Leser oben ueberspringen muessen, als Meldungstext.

    Ohne diese Funktion waere die Haertung ein Blindfleck: Die Leser liefern dann
    stillschweigend '' fuer ein Feld, das in Wahrheit kaputt ist, und jede Aussage
    darueber faellt lautlos aus.
    """
    aus = []
    for p in items or []:
        if not isinstance(p, dict):
            continue   # unten eigene Meldung
        for f in TEXTFELDER:
            if f in p and p[f] is not None and not isinstance(p[f], str):
                aus.append(f"§A1: {p.get('slug')} fuehrt {f} als "
                           f"{type(p[f]).__name__} statt als Text ({p[f]!r}) — jede "
                           f"Aussage, die dieses Feld liest, wird dadurch unzuverlaessig")
        for f in LISTENFELDER:
            if f in p and p[f] is not None and not isinstance(p[f], (list, tuple)):
                aus.append(f"§A1: {p.get('slug')} fuehrt {f} als "
                           f"{type(p[f]).__name__} statt als Liste")
        for f in OBJEKTFELDER:
            if f in p and p[f] is not None and not isinstance(p[f], dict):
                aus.append(f"§A1: {p.get('slug')} fuehrt {f} als "
                           f"{type(p[f]).__name__} statt als Objekt")
        for f in p:
            if f not in TEXTFELDER + LISTENFELDER + OBJEKTFELDER:
                aus.append(f"§A1: {p.get('slug')} fuehrt das Feld \"{f}\", das in "
                           f"scripts/produktdaten.py in keiner Feldliste steht — sein Typ "
                           f"wird dadurch nicht geprueft, und jede Lesestelle kann daran "
                           f"abbrechen. Entweder in TEXTFELDER/LISTENFELDER/OBJEKTFELDER "
                           f"aufnehmen oder das Feld entfernen")
    for p in items or []:
        if not isinstance(p, dict):
            aus.append(f"§A1: products.json enthaelt einen Eintrag, der kein Objekt ist "
                       f"({type(p).__name__}) — er wird von allen Produkt-Gates "
                       f"uebersprungen")
            continue
        if p.get('specs') is not None and not isinstance(p.get('specs'), (list, tuple)):
            aus.append(f"§A1: {p.get('slug')} fuehrt specs als "
                       f"{type(p['specs']).__name__}, erwartet ist eine Liste von Paaren "
                       f"— damit faellt JEDE Spec-Aussage ueber dieses Produkt stumm aus "
                       f"(Bewertung, Verb., Sticks)")
            continue
        for e in (p.get('specs') or []):
            if not (isinstance(e, (list, tuple)) and len(e) == 2):
                aus.append(f"§A1: {p.get('slug')} hat den Spec-Eintrag {e!r}, der kein "
                           f"Paar aus Schluessel und Wert ist — er wird von allen "
                           f"Spec-Gates uebersprungen")
    return aus
