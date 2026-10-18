#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""gen_vergleich.py — die Direktvergleiche aus products.json bauen (Massnahme 9).

Vorgeschichte
-------------
Die fuenf Duelle unter `/vergleich/` waren handgeschrieben und die ACHTE Renderstelle
fuer Produktdaten ohne Generator. Gemessen am 06.10.2026:

  backbone-one-vs-gamesir-g8      103 Woerter
  backbone-pro-vs-kishi-v3-pro    110 Woerter
  g8-galileo-vs-kishi-v3          206 Woerter
  g8-plus-vs-kishi-v3-pro         275 Woerter
  kishi-ultra-vs-g8-plus          428 Woerter

Drei davon sind Thin Pages nach demselben Massstab, den B6 an die Bestenlisten angelegt
hat (die lagen bei 123-190 Woertern). Dazu dieselben Befunde wie dort:

  · Die Zeilen-Labels liefen auseinander ("Pass-Through" gegen "Pass-Through-Charging",
    "Plattform" gegen "Plattformen", "Ruecktasten" gegen "Zusatztasten").
  · Nur "Preis" und "Sticks" standen auf allen fuenf. **Die Amazon-Bewertung stand auf
    zwei von fuenf** -- auf einer Vergleichsseite fehlte also das Signal, das Cialdini
    als das staerkste benennt und das B8 ueberall sonst nach vorn geholt hat.
  · Verfuegbarkeit stand auf keiner, obwohl seit dem 06.10. sechs Produkte nicht neu
    kaufbar sind und eines davon (Backbone Pro) in einem Duell steht.
  · Keine Seite trug ein ItemList- oder Product-Schema, nur BreadcrumbList. Das
    bleibt so, und zwar bewusst: Ein Product-Schema gehoert der Produktseite, nicht
    einem Duell, und eine aggregateRating-Angabe auf einer Vergleichsseite waere
    genau die Doppelung, die §A4 verhindern soll. Geschlossen wurde dafuer, dass
    jede Seite GENAU EINE BreadcrumbList traegt (vorher: keine mehr als eine).

Was redaktionell bleibt
-----------------------
Die PAARUNG, der SIEGER und das URTEIL. Das sind Entscheidungen, keine Rechnungen, und
sie gehoeren einem Menschen. Alles andere -- Preis, Bewertung, Verfuegbarkeit, Sticks,
Verbindung, Plattformen, die Haekchen, der Preisabstand und die Gegenrede -- kommt aus
products.json und wird bei jedem Lauf neu gerechnet.

Die Gegenrede ist der Pflicht-Mechanismus aus P-14: Was in den DATEN gegen den
gewaehlten Sieger spricht, steht auf der Seite. Ohne sie ist ein Duell eine Behauptung
mit Tabelle drumherum.

Aufruf:
  python3 scripts/gen_vergleich.py            schreiben
  python3 scripts/gen_vergleich.py --check    nur melden (Gate)
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gen_hubs import esc                      # dieselbe Escaping-Regel wie die Karten
from produktdaten import (bewertung, preis_zahl, spec_wie, sterne_text, anzahl_text,
                          stock, STOCK_LABEL, text as pfeld, liste as pliste)

CHECK = '--check' in sys.argv
START, END = '<!-- VS:START -->', '<!-- VS:END -->'
_STYLE_CSS = ''

# Zahl plus Einheit. Bewusst NICHT jede Ziffer: "G8" und "V3" sind Modellnamen, und die
# Jahreszahl im Titel ist keine Messung.
# Einheiten mit optionalem Plural-n: "1 Stunde" ist durchgelaufen, weil die Liste nur
# "Stunden" kannte. Nicht die Deckung war zu weit, die Erkennung war zu eng.
# Physikalische Einheiten. Bei ihnen muss im Belegtext Zahl UND Einheit stehen: "157
# Bewertungen" belegt keine "157 Stunden", "von 5" keine "5 Zoll". Sterne und
# Bewertungszahlen sind ausgenommen, weil die Quellen sie anders formulieren ("4,4 von 5").
_EINHEIT = re.compile(r'(\d+(?:[.,]\d+)?)\s*(€|EUR\b|Euro\b|g\b|Gramm|mAh|mm|Zoll|'
                      r'Stunden?|Std|Minuten?|Prozent|%)')

_MESSZAHL = re.compile(r'(\d+(?:[.,]\d+)?)\s*(?:€|EUR\b|Euro\b|g\b|Gramm|mAh|mm|Zoll|'
                       r'Stunden?|Std|h\b|Minuten?|Prozent|%|Sterne?n?\b|'
                       r'Bewertungen?)')

# Markennamen, die genau einem Geraet gehoeren. Wer sie auf einer Vergleichsseite nennt,
# an der das Geraet nicht teilnimmt, schreibt ein Merkmal dem falschen Produkt zu.
_MARKENNAMEN = {
    'Sensa': ('razer-kishi-v3-pro',),
    'Chroma': ('razer-kishi-ultra', 'razer-phone-cooler'),
    'TPSiV': ('razer-kishi-ultra',),
    'Backbone+': ('backbone-one-2', 'backbone-pro'),
}

# Plattform-Etiketten, dieselbe Reihenfolge wie in den Hubs.
PLATTFORM_TEXT = (('ios', 'iPhone'), ('android', 'Android'), ('tablet', 'Tablet'))


# ---------------------------------------------------------------- Die Duelle
# `merkmale` sind die Zeilen, die NICHT aus products.json folgen: Urteile ueber Design,
# Abo-Modelle, Bauform. Sie stehen als (Label, Wert A, Wert B) und werden unveraendert
# uebernommen -- inklusive ihrer Haekchen, denn ein "Premium-Look" ist keine Messung.
VERGLEICHE = [
    {
        'datei': 'vergleich/backbone-one-vs-gamesir-g8/index.html',
        'a': 'backbone-one-2', 'b': 'gamesir-g8-galileo',
        'sieger': 'gamesir-g8-galileo',
        'urteil': 'Hall-Effect-Sticks und Pass-Through-Charging. '
                  'Für die meisten Spieler ist der G8 Galileo die überlegene Wahl.',
        'merkmale': [
            ('Pass-Through', '✗ Nein', '✓ Ja'),
            ('3,5-mm-Klinke', 'keine Angabe', '✓ Ja'),
            # Das Label "Abo noetig?" plus ✗ behauptete eine Pflicht. Die eigene FAQ sagt
            # "du kannst den Controller problemlos ohne Abo nutzen", der Spec heisst
            # App: kostenlos, und der eigene Beleg traegt den Qualifier "fuer
            # Cloud-Gaming", den die Zelle weggelassen hat.
            ('Abo', 'Backbone+ nur für Cloud-Gaming', '✓ Kein Abo'),
            # Die Site dokumentiert "Keine Hall-Effect-Sticks" fuer den Backbone One
            # an vier Stellen; die gerechnete Sticks-Zeile zeigte "keine Angabe" und
            # damit weniger -- auf der Zeile, die die Seite zur Entscheidungszeile
            # erklaert. Gleiche Loesung wie beim Backbone Pro ein Duell weiter.
            ('Stick-Technik', '✗ Keine Hall-Effect-Sticks', '✓ Hall-Effect'),
            # 230 g fuer den G8 Galileo ist seit dem 06.10.2026 als unbelegt
            # protokolliert: Die Amazon-Seite nennt kein Produktgewicht.
            ('Gewicht', '138 g laut Datenblatt', 'keine Angabe'),
            ('Design', 'Premium-Look', 'Funktional'),
        ],
        'ersetzt': {'Stick-Technik': ['Sticks']},
        'belege': {
            'Pass-Through': {'a': ('controller/ios/backbone-one-2-review/index.html', 'Kein Pass-Through-Charging'), 'b': ('assets/data/products.json', 'Laden während des Spielens')},
            '3,5-mm-Klinke': {'b': ('assets/data/products.json', 'eine Klinkenbuchse fürs Headset')},
            'Abo': {'a': ('controller/ios/backbone-one-2-review/index.html', 'Backbone+-Abo für Cloud-Gaming nötig'), 'b': ('controller/universal/gamesir-g8-galileo-review/index.html', 'Keine App-Pflicht, kein Abo')},
            'Stick-Technik': {'a': ('controller/ios/backbone-one-2-review/index.html', 'Keine Hall-Effect-Sticks'), 'b': ('assets/data/products.json', 'Hall-Effect')},
            'Gewicht': {'a': ('assets/data/products.json', '138 g')},
            'Design': 'EINSCHAETZUNG',
        },
    },
    {
        'datei': 'vergleich/backbone-pro-vs-kishi-v3-pro/index.html',
        'a': 'backbone-pro', 'b': 'razer-kishi-v3-pro',
        'sieger': 'razer-kishi-v3-pro',
        'urteil': 'Haptisches Feedback und vier frei belegbare Zusatztasten schlagen das '
                  'Backbone-Abo-Modell. Für Hardcore-Gamer ist der V3 Pro die '
                  'konsequentere Wahl.',
        'merkmale': [
            ('Haptik', 'keine Angabe', '✓ Sensa HD'),
            ('Zusatztasten', 'keine Angabe', '✓ 4 frei belegbare'),
            # Der Datenkern fuehrt fuer den Backbone Pro keinen Sticks-Wert, die eigene
            # Testseite sagt es aber ausdruecklich. Die abgeleitete Zeile haette hier
            # "keine Angabe" gezeigt und damit weniger, als die Site weiss.
            ('Stick-Technik', '✗ Keine Hall-Effect-Sticks', '✓ TMR'),
            ('Abo', '✗ Backbone+ für volle Funktionen', '✓ Kein Abo'),
        ],
        # Die redaktionelle Zeile sagt mehr: Der Datenkern fuehrt fuer den
        # Backbone Pro keinen Sticks-Wert, seine Testseite sagt ausdruecklich
        # "Keine Hall-Effect-Sticks". Sie ersetzt die gerechnete Sticks-Zeile.
        'ersetzt': {'Stick-Technik': ['Sticks']},
        'belege': {
            'Haptik': {'b': ('assets/data/products.json', 'Sensa-HD-Haptik')},
            'Zusatztasten': {'b': ('controller/universal/razer-kishi-v3-pro-review/index.html', '4 frei belegbare Zusatztasten')},
            'Stick-Technik': {'a': ('controller/ios/backbone-pro-review/index.html', 'Keine Hall-Effect-Sticks'), 'b': ('assets/data/products.json', 'TMR')},
            'Abo': {'a': ('controller/ios/backbone-pro-review/index.html', 'Backbone+-Abo nötig für volle Funktionalität'), 'b': ('controller/universal/razer-kishi-v3-pro-review/index.html', 'Nexus-App kostenlos')},
        },
    },
    {
        'datei': 'vergleich/g8-galileo-vs-kishi-v3/index.html',
        'a': 'gamesir-g8-galileo', 'b': 'razer-kishi-v3',
        'sieger': 'gamesir-g8-galileo',
        'urteil': 'Pass-Through-Charging und der niedrigere Preis entscheiden das Duell '
                  'für die meisten Spieler. Wer vier frei belegbare Zusatztasten '
                  'braucht, nimmt den Kishi V3.',
        'merkmale': [
            ('Pass-Through-Charging', '✓ Ja', '✗ Nein'),
            ('Zusatztasten', 'keine Angabe', '✓ 4 frei belegbare'),
            ('3,5-mm-Klinke', '✓ Ja', 'keine Angabe'),
            # "GameSir Nexus" stand nirgends sonst im Repo; die eigene Testseite sagt
            # ausdruecklich "Keine App-Pflicht, kein Abo".
            ('App', 'Keine App-Pflicht', 'Nexus App (kostenlos)'),
        ],
        'belege': {
            'Pass-Through-Charging': {'a': ('assets/data/products.json', 'Laden während des Spielens'), 'b': ('controller/universal/razer-kishi-v3-review/index.html', 'Kein Pass-Through-Charging')},
            'Zusatztasten': {'b': ('controller/universal/razer-kishi-v3-review/index.html', '4 frei belegbare Zusatztasten')},
            '3,5-mm-Klinke': {'a': ('assets/data/products.json', 'eine Klinkenbuchse fürs Headset')},
            'App': {'a': ('controller/universal/gamesir-g8-galileo-review/index.html', 'Keine App-Pflicht, kein Abo'), 'b': ('controller/universal/razer-kishi-v3-review/index.html', 'Nexus-App kostenlos (kein Abo)')},
        },
    },
    {
        'datei': 'vergleich/g8-plus-vs-kishi-v3-pro/index.html',
        'a': 'gamesir-g8-plus', 'b': 'razer-kishi-v3-pro',
        'sieger': 'gamesir-g8-plus',
        # Nicht "mehr Einsatzfaelle": Die Plattformen-Zeile ist auf beiden Seiten
        # identisch, und der Kishi V3 Pro laeuft zusaetzlich an Windows 11. TMR nennt
        # dieselbe Seite "die feineren" Sticks. Was wirklich fuer den G8 Plus spricht,
        # steht in der Tabelle: 52 Euro weniger und die zweite Verbindungsart.
        'urteil': '52 Euro weniger, und kabellos spielen kann von den beiden nur er. '
                  'Wer haptisches Feedback und die feineren TMR-Sticks will, zahlt '
                  'beim Kishi V3 Pro dafür.',
        'merkmale': [
            ('Haptik', 'keine Angabe', '✓ Sensa HD'),
            ('Zusatztasten', 'keine Angabe', '✓ 4 frei belegbare'),
            ('Windows-Betrieb', 'keine Angabe', '✓ Windows 11'),
        ],
        'belege': {
            'Haptik': {'b': ('assets/data/products.json', 'Sensa-HD-Haptik')},
            'Zusatztasten': {'b': ('controller/universal/razer-kishi-v3-pro-review/index.html', '4 frei belegbare Zusatztasten')},
            'Windows-Betrieb': {'b': ('controller/universal/razer-kishi-v3-pro-review/index.html', 'Windows 11')},
        },
    },
    {
        'datei': 'vergleich/kishi-ultra-vs-g8-plus/index.html',
        'a': 'razer-kishi-ultra', 'b': 'gamesir-g8-plus',
        'sieger': 'gamesir-g8-plus',
        'urteil': 'Driftfreie Hall-Sticks und Bluetooth als zweite Verbindungsart. Wer '
                  'die Razer-Extras wirklich braucht, bekommt beim Kishi Ultra ein '
                  'durchdachtes Gerät.',
        'merkmale': [
            ('Hall bei den Sticks', '✗ Nur bei den Triggern', '✓ Sticks und Trigger'),
            ('3,5-mm-Klinke', '✓ Ja', 'keine Angabe'),
            # Die drei Razer-Extras, die der Kaufgrund-Absatz nennt, standen in keiner
            # Zeile. Alle drei stehen woertlich in der Staerken-Liste der eigenen
            # Produktseite, gehoeren also in die Tabelle und nicht nur in die Prosa.
            ('Steuerkreuz', '✓ Mecha-taktil', 'keine Angabe'),
            ('App', '✓ Nexus ohne Abo', 'keine Angabe'),
            ('PC Remote Play', '✓ Ja', 'keine Angabe'),
        ],
        # Die redaktionelle Zeile sagt mehr als die gerechnete: Der Datenkern fuehrt
        # fuer den Ultra nur einen Trigger-Wert, die Produktseite nennt TPSiV bei den
        # Sticks. Deshalb ersetzt sie die abgeleitete Sticks-Zeile ausdruecklich.
        'ersetzt': {'Hall bei den Sticks': ['Sticks']},
        'belege': {
            'Hall bei den Sticks': {'a': ('produkte/razer-kishi-ultra/index.html', 'Nur die Trigger arbeiten mit Hall'), 'b': ('controller/universal/gamesir-g8-plus-review/index.html', 'Hall-Effect-Sticks und -Trigger')},
            '3,5-mm-Klinke': {'a': ('produkte/razer-kishi-ultra/index.html', 'Klinkenbuchse')},
            'Steuerkreuz': {'a': ('produkte/razer-kishi-ultra/index.html', 'Mecha-taktiles Steuerkreuz')},
            'App': {'a': ('produkte/razer-kishi-ultra/index.html', 'Razer Nexus App ohne Abo')},
            'PC Remote Play': {'a': ('produkte/razer-kishi-ultra/index.html', 'PC Remote Play')},
        },
    },
    # --- Neu am 06.10.2026 (Massnahme 9) -------------------------------------------
    # Beide Paarungen sind MARKENINTERN: die Frage, die jemand stellt, nachdem er sich
    # fuer eine Marke entschieden hat. Und beide tragen eine Bewertungs-Umkehr -- das
    # teurere Modell ist schwaecher bewertet. Genau die Faelle, auf die B10 die Site
    # positioniert hat, und sie standen bisher nirgends als Duell.
    {
        'datei': 'vergleich/kishi-v3-vs-kishi-v3-pro/index.html',
        'a': 'razer-kishi-v3', 'b': 'razer-kishi-v3-pro',
        'sieger': 'razer-kishi-v3',
        'titel': 'Razer Kishi V3 vs. Kishi V3 Pro',
        'kurzname': 'Kishi V3 vs. V3 Pro',
        'beschreibung': 'Razer Kishi V3 gegen Kishi V3 Pro: 46 € Unterschied, und das '
                        'günstigere Modell ist besser bewertet. Wofür der Aufpreis geht.',
        'lead': 'Dieselbe Marke, dieselbe Bauform, 46 € Unterschied. Lohnt der Aufpreis?',
        'kurzurteil': 'Für die meisten Spieler reicht der Kishi V3. Er ist 46 € '
                      'günstiger und bei Amazon <strong>besser</strong> bewertet als das '
                      'Pro-Modell. Der V3 Pro lohnt sich, wenn du haptisches Feedback '
                      'willst oder an einem Tablet spielst.',
        'merkmale': [
            ('Haptik', '✗ Nein', '✓ Sensa HD'),
            ('Mecha-Buttons', '✗ Nein', '✓ Ja'),
            # Chroma ist im Repo nur fuer den Kishi ULTRA belegt, nicht fuer den V3 Pro.
            # Die Zeile ist deshalb ganz entfallen, nicht auf "keine Angabe" gesetzt:
            # Ein Merkmal, das keine der beiden Seiten belegt, gehoert in keine Tabelle.
            ('Zusatztasten', '✓ 4 frei belegbare', '✓ 4 frei belegbare'),
        ],
        'belege': {
            'Haptik': {'a': ('controller/universal/razer-kishi-v3-review/index.html', 'Nur wenn du haptisches Feedback und Mecha-Buttons wirklich willst'), 'b': ('assets/data/products.json', 'Sensa-HD-Haptik')},
            'Mecha-Buttons': {'a': ('controller/universal/razer-kishi-v3-review/index.html', 'Nur wenn du haptisches Feedback und Mecha-Buttons wirklich willst'), 'b': ('controller/universal/razer-kishi-v3-pro-review/index.html', 'Mecha-Micro-Buttons')},
            'Zusatztasten': {'a': ('controller/universal/razer-kishi-v3-review/index.html', '4 frei belegbare Zusatztasten'), 'b': ('controller/universal/razer-kishi-v3-pro-review/index.html', '4 frei belegbare Zusatztasten')},
        },
        'abschnitte': """      <h2>Der Unterschied, der das Duell entscheidet</h2>
      <p>Technisch trennt die beiden weniger, als der Preis vermuten lässt. Beide laufen über USB-C, beide haben <a href="/blog/hall-effect-vs-tmr/">TMR-Sticks</a>, beide dieselben vier frei belegbaren Zusatztasten. Was der Pro zusätzlich mitbringt, ist Ausstattung: haptisches Feedback nach Konsolen-Art, mecha-taktile Buttons und Platz für ein Tablet. Das sind 46 Euro oder 59 Prozent Aufpreis für Komfortmerkmale, nicht für bessere Grundfunktion.</p>

      <h2>Warum der günstigere besser bewertet ist</h2>
      <p>Das ist der ungewöhnliche Teil. Der Kishi V3 steht bei 4,4 Sternen aus 157 Bewertungen, der V3 Pro bei 4,2 aus 152, also fast dieselbe Datenbasis, und das teurere Modell liegt zurück. Wir wissen nicht, woran das liegt; Amazon liefert keine Begründung mit. Was wir sagen können: Wer 46 Euro mehr ausgibt, kauft messbar nicht die zufriedeneren Käufer mit. Wer die Haptik nicht ausdrücklich will, nimmt den V3.</p>
      <div class="cta-row" style="margin-top:20px">
        <a class="btn btn-secondary" href="/controller/universal/razer-kishi-v3-review/">Kishi V3 im Test →</a>
        <a class="btn btn-secondary" href="/controller/universal/razer-kishi-v3-pro-review/">Kishi V3 Pro im Test →</a>
      </div>""",
        'urteil': 'Er kostet 46 € weniger und ist besser bewertet. Der Aufpreis zum Pro '
                  'kauft Haptik, mecha-taktile Buttons und Tablet-Breite, keine bessere '
                  'Grundfunktion.',
    },
    {
        'datei': 'vergleich/g8-galileo-vs-g8-plus/index.html',
        'a': 'gamesir-g8-galileo', 'b': 'gamesir-g8-plus',
        'sieger': 'gamesir-g8-galileo',
        'titel': 'GameSir G8 Galileo vs. G8 Plus',
        'kurzname': 'G8 Galileo vs. G8 Plus',
        'beschreibung': 'GameSir G8 Galileo gegen G8 Plus: vier Euro Unterschied. Welcher '
                        'der beiden GameSir passt zu welchem Spieler.',
        'lead': 'Vier Euro trennen die beiden GameSir. Die Entscheidung fällt woanders.',
        # Beide G8 laden durch (B0FYQ1SHHS: "unterstuetzt das Durchladen"). Damit ist
        # Pass-Through kein Unterscheidungsmerkmal mehr und darf keines der Urteile
        # tragen -- der erste Fix hatte nur den Absatz geaendert, nicht diese zwei Felder.
        # Weder der Preis (der Lead sagt "Die Entscheidung faellt woanders") noch die
        # Klinke (der Absatz sagt "wir behaupten es in keine Richtung") duerfen hier
        # stehen. Was bleibt, ist die Bewertung -- und die steht in der Tabelle.
        'kurzurteil': 'Wer am Handy spielt, nimmt den G8 Galileo: Er ist besser '
                      'bewertet, und das auf mehr Stimmen. Wer Bluetooth oder ein '
                      'Tablet braucht, nimmt den G8 Plus. Beide haben driftfreie '
                      'Hall-Sticks, und beide laden das Handy während des Spielens.',
        'merkmale': [
            ('Pass-Through-Charging', '✓ Ja', '✓ Ja'),
            ('3,5-mm-Klinke', '✓ Ja', 'keine Angabe'),
        ],
        'belege': {
            'Pass-Through-Charging': {'a': ('assets/data/products.json', 'Laden während des Spielens'), 'b': ('controller/universal/gamesir-g8-plus-review/index.html', 'Pass-Through-Charging')},
            '3,5-mm-Klinke': {'a': ('assets/data/products.json', 'eine Klinkenbuchse fürs Headset')},
        },
        'abschnitte': """      <h2>Der Unterschied, der das Duell entscheidet</h2>
      <p>Nicht der Preis: vier Euro sind bei einem Gerät für Jahre keine Entscheidung. Beide führen <a href="/blog/hall-effect-erklaert/">Hall-Effect-Sticks</a>, beide laden das Handy während des Spielens, beide stammen aus derselben Serie. Getrennt werden sie durch die Verbindung. Der G8 Galileo ist ein reines USB-C-Gerät fürs Handy und hat eine Klinkenbuchse fürs Headset. Der G8 Plus ist der einzige GameSir im Sortiment, der kabelgebunden und kabellos kann, und seine Brücke spannt bis zum Tablet. Ob er eine Klinkenbuchse hat, gibt GameSir auf der Produktseite nicht an; wir behaupten es deshalb in keine Richtung.</p>

      <h2>Wer sollte den G8 Plus wählen?</h2>
      <p>Wer mehr als ein Gerät bedienen will. Bluetooth heißt: derselbe Controller am Handy und am Tablet, ohne Kabel. Das kann der G8 Galileo nicht, er deckt das Tablet nicht ab, der G8 Plus schon. Ehrlich dazu: Der G8 Plus steht mit 4,1 Sternen aus 564 Bewertungen minimal unter dem Galileo mit 4,2 aus 705, er kostet vier Euro mehr, und Bluetooth kostet Latenz. Für kompetitive Shooter bleibt die Kabelverbindung die bessere.</p>
      <div class="cta-row" style="margin-top:20px">
        <a class="btn btn-secondary" href="/controller/universal/gamesir-g8-galileo-review/">G8 Galileo im Test →</a>
        <a class="btn btn-secondary" href="/controller/universal/gamesir-g8-plus-review/">G8 Plus im Test →</a>
      </div>""",
        # Jede Zahl hinter IHREM Produktnamen (P-18 Mechanismus 3). Die erste Fassung
        # schrieb "4,2 aus 705 gegen 4,1 aus 564" ohne Namen, und das Fliesstext-Audit
        # hat die 705 dem G8 Plus zugeordnet und den Satz zu Recht rot gemacht.
        'urteil': 'Der G8 Galileo steht bei 4,2 Sternen aus 705 Bewertungen, der '
                  'G8 Plus bei 4,1 aus 564. Die bessere Bewertung auf der größeren '
                  'Datenbasis entscheidet; wer Bluetooth oder ein Tablet braucht, '
                  'nimmt den G8 Plus.',
    },
]


# ---------------------------------------------------------------- Ableitungen

def _plattformen(p):
    """Die Plattformen eines Produkts als Text, aus worksOn."""
    w = pliste(p, 'worksOn')
    namen = [t for s, t in PLATTFORM_TEXT if s in w]
    return ', '.join(namen) if namen else 'keine Angabe'


def _zelle(wert, gewinnt):
    """Eine Tabellenzelle. Das Haekchen steht NUR an einem gemessenen Vorteil."""
    return (f"<td class='winner'>✓ {esc(wert)}</td>" if gewinnt
            else f"<td class=''>{esc(wert)}</td>")


def _zeile(label, wa, wb, besser):
    """besser: 'a', 'b' oder None -- wer bei diesem Merkmal messbar vorn liegt."""
    return (f'<tr><td>{esc(label)}</td>'
            + _zelle(wa, besser == 'a') + _zelle(wb, besser == 'b') + '</tr>')


def abgeleitete_zeilen(a, b):
    """Die Zeilen, die aus products.json folgen. Reihenfolge ist Absicht:
    Preis und Bewertung zuerst, weil das die beiden Zahlen sind, nach denen jemand
    entscheidet -- und weil die Bewertung vorher auf drei von fuenf Seiten fehlte."""
    zeilen = []

    pa, pb = preis_zahl(a), preis_zahl(b)
    if pa is not None and pb is not None:
        d = abs(pa - pb)
        wa = f"{pfeld(a, 'price')}" + (f', {d} € günstiger' if pa < pb else '')
        wb = f"{pfeld(b, 'price')}" + (f', {d} € günstiger' if pb < pa else '')
        zeilen.append(_zeile('Preis', wa, wb,
                             'a' if pa < pb else ('b' if pb < pa else None)))

    (sa, ca), (sb, cb) = bewertung(a), bewertung(b)
    if sa is not None and sb is not None:
        wa = f'{sterne_text(sa)} aus {anzahl_text(ca)} Bewertungen'
        wb = f'{sterne_text(sb)} aus {anzahl_text(cb)} Bewertungen'
        zeilen.append(_zeile('Amazon-Bewertung', wa, wb,
                             'a' if sa > sb else ('b' if sb > sa else None)))

    # Verfuegbarkeit nur zeigen, wenn sie etwas zu sagen hat. Zwei kaufbare Geraete
    # brauchen keine Zeile "Verfügbar / Verfügbar"; sobald eines NICHT kaufbar ist, ist
    # es die wichtigste Zeile der Tabelle.
    if stock(a) != 'ja' or stock(b) != 'ja':
        zeilen.append(_zeile('Verfügbarkeit',
                             STOCK_LABEL.get(stock(a), 'unbekannt'),
                             STOCK_LABEL.get(stock(b), 'unbekannt'),
                             'a' if stock(a) == 'ja' else
                             ('b' if stock(b) == 'ja' else None)))

    ha, hb = spec_wie(a, 'Sticks'), spec_wie(b, 'Sticks')
    if ha or hb:
        drift = lambda s: 'Hall' in s or 'TMR' in s
        zeilen.append(_zeile('Sticks', ha or 'keine Angabe', hb or 'keine Angabe',
                             'a' if drift(ha) and not drift(hb) else
                             ('b' if drift(hb) and not drift(ha) else None)))

    va, vb = spec_wie(a, 'Verb'), spec_wie(b, 'Verb')
    if va or vb:
        zeilen.append(_zeile('Verbindung', va or 'keine Angabe', vb or 'keine Angabe',
                             None))

    # ZAHL der Plattformen vergleichen, nicht die Zeichenlaenge des Textes. Die erste
    # Fassung nahm `len(la) > len(lb)` -- damit gewann "keine Angabe" (12 Zeichen) gegen
    # "Android" (7). Heute folgenlos, in einem Generator, der wachsen soll, eine Mine.
    la, lb = _plattformen(a), _plattformen(b)
    na = len([t for s, t in PLATTFORM_TEXT if s in pliste(a, 'worksOn')])
    nb = len([t for s, t in PLATTFORM_TEXT if s in pliste(b, 'worksOn')])
    zeilen.append(_zeile('Plattformen', la, lb,
                         'a' if na > nb else ('b' if nb > na else None)))
    return zeilen


def gegenrede(a, b, sieger):
    """Was in den DATEN gegen den gewaehlten Sieger spricht (P-14, Pflicht).

    Nur gemessene Unterschiede, nie ein Urteil. Spricht nichts dagegen, steht das
    ausdruecklich da -- ein leerer Absatz waere dieselbe Luecke wie eine fehlende
    Bewertung.
    """
    s = a if pfeld(a, 'slug') == sieger else b
    v = b if s is a else a
    punkte = []

    ps, pv = preis_zahl(s), preis_zahl(v)
    if ps is not None and pv is not None and ps > pv:
        punkte.append(f'er kostet {ps - pv} € mehr')

    # Jede Zahl steht direkt hinter IHREM Produktnamen. Die erste Fassung schrieb
    # "schwächer bewertet als der Backbone Pro mit 4,4 und seine Bewertung ruht auf 152
    # Stimmen" -- das Fliesstext-Audit hat die 152 dem Backbone Pro zugeordnet und den
    # Satz zu Recht rot gemacht. Ein Vergleichssatz braucht beide Namen, nicht ein
    # Pronomen und einen Namen.
    (ss, cs), (sv, cv) = bewertung(s), bewertung(v)
    if ss is not None and sv is not None and ss < sv:
        punkte.append(f'der {esc(pfeld(s, "name"))} steht bei {sterne_text(ss)} Sternen, '
                      f'der {esc(pfeld(v, "name"))} bei {sterne_text(sv)}')
    if cs is not None and cv is not None and cs < cv / 2:
        punkte.append(f'der {esc(pfeld(s, "name"))} hat {anzahl_text(cs)} Bewertungen, '
                      f'der {esc(pfeld(v, "name"))} {anzahl_text(cv)}; die Datenbasis '
                      f'ist deutlich dünner')

    if stock(s) != 'ja':
        punkte.append(f'er ist bei Amazon derzeit '
                      f'{STOCK_LABEL.get(stock(s), "nicht verfügbar").lower()}')

    ws, wv = set(pliste(s, 'worksOn')), set(pliste(v, 'worksOn'))
    fehlt = [t for k, t in PLATTFORM_TEXT if k in wv - ws]
    if fehlt:
        # "er lässt Tablet aus" holperte im Browser-Check. Mit Artikel und Verb liest es
        # sich wie ein Satz und nicht wie eine Feldliste.
        was = ' und '.join(('das Tablet' if t == 'Tablet' else 'das ' + t) for t in fehlt)
        punkte.append(f'er deckt {was} nicht ab, der {esc(pfeld(v, "name"))} schon')

    drift = lambda p: 'Hall' in spec_wie(p, 'Sticks') or 'TMR' in spec_wie(p, 'Sticks')
    if drift(v) and not drift(s):
        punkte.append(f'er führt keine driftfreien Sticks, der '
                      f'{esc(pfeld(v, "name"))} schon')

    if not punkte:
        return (f'<p><strong>Was gegen den Sieger spricht:</strong> In den Daten nichts. '
                f'Der {esc(pfeld(s, "name"))} ist hier weder teurer noch schwächer '
                f'bewertet noch schmaler aufgestellt.</p>')
    rede = punkte[0] if len(punkte) == 1 else \
        '; '.join(punkte[:-1]) + '; und ' + punkte[-1]
    return (f'<p><strong>Was gegen den Sieger spricht:</strong> '
            f'{rede[0].upper() + rede[1:]}. Das steht hier, weil eine Empfehlung ohne '
            f'ihre Gegenrechnung keine ist.</p>')


def _abgeleitet(tabellenzahlen, preise):
    """Zahlen, die sich aus den TABELLENWERTEN rechnen lassen. Eng, und zwar gemessen.

    Drei Fassungen, jede von einer Messung verworfen:
      1. Basis = Tabelle UND JSON-Dump beider Produkte (also auch ASINs, Bild-URLs,
         Video-Hashes), alle Differenzen, dann alle Prozente aller Differenzen:
         bis zu 13.709 zulaessige Werte, **96 bis 100 Prozent aller Zahlen 1..2000**.
         "9000 mAh", "999 Euro", "230 g", "40 Stunden" liefen durch. Das war kein Gate,
         das war ein Freibrief -- und meine eigene Gegenprobe hat es nicht gesehen, weil
         sie den Exitcode gelesen hat statt der Befundzahl (in --check ist er bei jeder
         Urteilsaenderung 1, weil der Block driftet).
      2. Basis nur Tabelle, Prozente ans Paar gebunden: 3 bis 6 Prozent Abdeckung, aber
         "93 Prozent" und "40 Stunden" blieben gruen -- Prozente entstanden auch aus
         Bewertungszahlen und aus "Windows 11".
      3. Jetzt: Differenzen aus allen Tabellenpaaren, Prozente NUR aus dem Preispaar.
         Das ist genau die eine Aussage, die es gibt ("46 Euro oder 59 Prozent").
    """
    #   4. Auch Differenzen aus ALLEN Tabellenpaaren waren zu viel: "40 Stunden" liess
    #      sich aus irgendeinem Paar bilden. Gebraucht werden nur die Ableitungen des
    #      PREISPAARS -- jede abgeleitete Zahl in der Prosa der sieben Seiten ist eine
    #      Preisdifferenz oder ein Aufpreis in Prozent. Nachgemessen: 1,1 Prozent
    #      Abdeckung statt 96 bis 100.
    basis = set(tabellenzahlen)
    werte = set(basis)
    p = sorted({int(z) for z in preise})
    if len(p) == 2 and p[0]:
        d = p[1] - p[0]
        werte.update({d, round(d / p[0] * 100), round(d / p[1] * 100)})
    return {str(w) for w in werte}


def _label(zeile):
    """Das Label einer gerenderten Tabellenzeile, also die erste Zelle."""
    m = re.search(r'<td>(.*?)</td>', zeile)
    return m.group(1) if m else ''


def block(v, by):
    """Der generierte Abschnitt einer Vergleichsseite."""
    a, b = by[v['a']], by[v['b']]
    s = by[v['sieger']]
    zweiter = b if s is a else a

    # <th>, nicht <td>: Der erste Umbau hat drei Seiten ihre Header-Zellen gekostet,
    # die Regel `.vs-table th{background:var(--navy)}` lief damit ins Leere, und eine
    # Vergleichstabelle ohne Header-Zellen ist auch fuer Screenreader keine Tabelle.
    kopf = (f'<tr><th scope="col">Merkmal</th>'
            f'<th scope="col">{esc(pfeld(a, "name"))}</th>'
            f'<th scope="col">{esc(pfeld(b, "name"))}</th></tr>')
    eigene = [_zeile(lab, wa, wb, None) for lab, wa, wb in v['merkmale']]
    # Eine abgeleitete Zeile faellt weg, wenn eine redaktionelle Zeile dieselbe
    # Komponente behandelt. Sonst steht in einer Tabelle zweimal etwas anderes ueber
    # dasselbe Bauteil: Auf kishi-ultra-vs-g8-plus sagte "Sticks" noch "keine Angabe"
    # (der Datenkern fuehrt fuer den Ultra nur einen Trigger-Wert), waehrend zwei Zeilen
    # tiefer "Hall bei den Sticks: nur bei den Triggern" stand.
    # AUSDRUECKLICH, nicht per Teilstring. Die erste Fassung suchte Begriffe im Label,
    # und damit haette ein Label wie "Preis-Leistung" die gerechnete Preiszeile STILL
    # geloescht (Pruefbericht, Probe 8). Jetzt sagt die Definition selbst, welche
    # abgeleitete Zeile eine redaktionelle Zeile ersetzt, und ein Eintrag fuer eine
    # Zeile, die es nicht gibt, ist ein Befund.
    begriffe = [x for liste in v.get('ersetzt', {}).values() for x in liste]
    # Die redaktionellen Zeilen tragen ihre Haekchen im Text, deshalb ohne winner-Klasse:
    # sonst stuende zweimal ein Haken in derselben Zelle.
    tabelle = ('<table class="vs-table" aria-label="Specs-Vergleich '
               + esc(pfeld(a, 'name')) + ' vs ' + esc(pfeld(b, 'name')) + '">'
               + kopf
               + ''.join(z for z in abgeleitete_zeilen(a, b)
                         if not any(w in _label(z) for w in begriffe))
               + ''.join(eigene)
               + '</table>')

    kaufen = ''.join(
        f'<a class="btn {kl}" data-asin="{esc(pfeld(p, "asin"))}" '
        f'data-product="{esc(pfeld(p, "slug"))}" href="#">'
        # Produktnamen koennen selbst eine Klammer tragen ("Backbone One (2. Gen)") --
        # dann stand "Backbone One (2. Gen) (63 €) kaufen" auf dem Knopf.
        f'{esc(pfeld(p, "name"))} für {esc(pfeld(p, "price"))} kaufen</a>'
        for p, kl in ((s, 'btn-primary'), (zweiter, 'btn-secondary')))

    # Die Ueberschrift gehoert IN den Block. Von Hand geschrieben fehlte sie auf zwei
    # von sieben Seiten -- genau die Divergenz, die dieser Generator beseitigen soll.
    return (f'{START}\n'
            f'      <h2 style="margin-top:32px">Specs-Vergleich</h2>\n'
            f'    {tabelle}\n'
            f'    <div class="winner-box">\n'
            f'      <div style="font-size:11px;font-weight:800;color:var(--good);'
            f'text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px">'
            f'🏆 Sieger dieses Vergleichs</div>\n'
            f'      <h2>{esc(pfeld(s, "name"))}</h2><p>{v["urteil"]}</p>\n'
            f'      {gegenrede(a, b, v["sieger"])}\n'
            f'      <div class="cta-pair">\n        {kaufen}\n      </div>\n'
            f'    </div>\n'
            f'    {END}')



# ---------------------------------------------------------------- Neue Seiten
# Ein neues Duell entsteht als DEFINITION, nicht als kopierte HTML-Datei. Die fuenf
# vorhandenen Seiten sind so entstanden -- durch Kopieren -- und genau daran sind die
# Zeilen-Labels auseinandergelaufen und die Bewertung auf drei von fuenf Seiten
# verschwunden. Header und Footer kommen aus `sync_header`/`sync_footer`, damit die
# neue Seite dieselbe Navigation traegt wie die 128 anderen (§A2).
DOMAIN = 'https://smartphone-controller.com'

SEITEN_STIL = """<style>
.vs-table{width:100%;border-collapse:collapse;margin:20px 0}
.vs-table th,.vs-table td{padding:12px 14px;border:1px solid var(--line);font-size:14px;text-align:left}
.vs-table th{background:var(--navy);color:#fff;font-weight:700}
.vs-table tr:nth-child(even) td{background:var(--surface-2)}
.vs-table .winner{background:var(--good-bg);color:var(--good);font-weight:700}
.vs-table .loser{color:var(--ink-dim)}
.winner-box{background:var(--good-bg);border:2px solid var(--good);border-radius:var(--radius-lg);padding:24px;text-align:center;margin:28px 0}
.winner-box .wb-label{font-size:11px;font-weight:800;color:var(--good);text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px}
.winner-box h2{font-size:24px;font-weight:800;color:var(--ink);margin-bottom:8px}
.winner-box p{color:var(--ink-soft);font-size:14px;line-height:1.6}
</style>"""


def neue_seite(v, by):
    """Das vollstaendige Geruest eines neuen Duells."""
    import json as _json
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import sync_header as _sh
    import sync_footer as _sf

    url = DOMAIN + '/' + os.path.dirname(v['datei']).replace(os.sep, '/') + '/'
    kurz = v['kurzname']
    titel = f"{v['titel']}: Vergleich 2026"
    besch = v['beschreibung']
    bc = _json.dumps({'@context': 'https://schema.org', '@type': 'BreadcrumbList',
                      'itemListElement': [
                          {'@type': 'ListItem', 'position': 1, 'name': 'Home',
                           'item': DOMAIN + '/'},
                          {'@type': 'ListItem', 'position': 2, 'name': 'Vergleiche',
                           'item': DOMAIN + '/vergleich/'},
                          {'@type': 'ListItem', 'position': 3, 'name': kurz,
                           'item': url}]}, ensure_ascii=False)
    kopf = _sh.header_html(_sh.nav_aus_mainjs(), _sh.trust_aus_mainjs())
    hinweis, links, schluss = _sf.aus_mainjs()
    fuss = _sf.footer_html(hinweis, links, schluss)
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(titel)}</title>
  <meta name="description" content="{esc(besch)}">
  <link rel="canonical" href="{url}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="smartphone-controller.com">
  <meta property="og:locale" content="de_DE">
  <meta property="og:title" content="{esc(titel)}">
  <meta property="og:description" content="{esc(besch)}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{DOMAIN}/assets/img/og-default.jpg">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(titel)}">
  <meta name="twitter:description" content="{esc(besch)}">
  <meta name="twitter:image" content="{DOMAIN}/assets/img/og-default.jpg">
  <link rel="stylesheet" href="/assets/css/style.css">
{SEITEN_STIL}
<script type="application/ld+json">
{bc}
</script>
</head>
<body>
<header class="site-header" id="site-header" data-active="/vergleich/">{kopf}</header>
<main>
  <section class="page-hero">
    <div class="container">
      <nav class="breadcrumb" aria-label="Breadcrumb"><a href="/">Home</a><span class="sep" aria-hidden="true">›</span><a href="/vergleich/">Vergleiche</a><span class="sep" aria-hidden="true">›</span><span class="cur">{esc(kurz)}</span></nav>
      <span class="eyebrow">⚔️ Direktvergleich</span>
      <h1>{esc(v['titel'])} <span class="hl">2026</span></h1>
      <p class="lead">{v['lead']}</p>
    </div>
  </section>
  <section class="section">
    <div class="container" style="max-width:860px">
      <p><strong>Kurz-Urteil vorab:</strong> {v['kurzurteil']}</p>

      {START}{END}
{v['abschnitte']}
    <p style="text-align:center;margin-top:24px"><a href="/controller/" class="btn btn-secondary">← Alle Controller vergleichen</a></p>
    </div>
  </section>
</main>
<footer class="site-footer" id="site-footer">{fuss}</footer>
<script src="/assets/js/main.js"></script>
</body>
</html>
"""

def main():
    global _STYLE_CSS
    _STYLE_CSS = open(os.path.join(ROOT, 'assets/css/style.css'),
                      encoding='utf-8').read()
    items = json.load(open(os.path.join(ROOT, 'assets/data/products.json'),
                           encoding='utf-8'))
    by = {p['slug']: p for p in items}
    befunde, geschrieben = [], 0

    for v in VERGLEICHE:
        _vorher = len(befunde)
        pfad = os.path.join(ROOT, v['datei'])
        # Erst die Slugs, DANN die Datei. Umgekehrt hat der --check-Pfad bei einer noch
        # nicht existierenden Seite "wuerde NEU angelegt" gemeldet und das continue
        # ausgefuehrt, bevor jemals jemand nachgesehen hat, ob die Slugs stimmen: ein
        # vertipptes Produkt waere erst beim echten Lauf aufgefallen (Pruefbericht 5).
        for schluessel in ('a', 'b', 'sieger'):
            if v[schluessel] not in by:
                befunde.append(f"{v['datei']}: {v[schluessel]} steht nicht in "
                               f"products.json")
        if v['sieger'] not in (v['a'], v['b']):
            befunde.append(f"{v['datei']}: Sieger {v['sieger']} ist keiner der beiden")

        for lab, ziele in v.get('ersetzt', {}).items():
            if lab not in {x[0] for x in v.get('merkmale', [])}:
                befunde.append(f"{v['datei']}: 'ersetzt' nennt „{lab}“, dazu gibt es "
                               f"keine merkmale-Zeile")
            for ziel in ziele:
                if ziel not in ('Preis', 'Amazon-Bewertung', 'Verfügbarkeit', 'Sticks',
                                'Verbindung', 'Plattformen'):
                    befunde.append(f"{v['datei']}: 'ersetzt' nennt die abgeleitete "
                                   f"Zeile „{ziel}“, die es nicht gibt")
                # Die redaktionelle Zeile muss dasselbe Bauteil betreffen. Sonst loescht
                # `ersetzt` still eine fremde Zeile -- Probe des Pruefers:
                # {'Haptik': ['Amazon-Bewertung']} entfernte die Bewertungszeile.
                # Stammvergleich, nicht Wortgleichheit: "Stick-Technik" und "Sticks"
                # gehoeren zusammen, "Haptik" und "Amazon-Bewertung" nicht.
                elif not any(a.startswith(b[:4]) or b.startswith(a[:4])
                             for a in re.findall(r'\w{4,}', ziel.lower())
                             for b in re.findall(r'\w{4,}', lab.lower())):
                    befunde.append(f"{v['datei']}: 'ersetzt' laesst „{lab}“ die "
                                   f"abgeleitete Zeile „{ziel}“ entfernen, die ein "
                                   f"anderes Merkmal betrifft — eine Zeile darf nur "
                                   f"ersetzen, was sie selbst behandelt")

        # JEDE merkmale-Zeile braucht einen Beleg, und zwar PRO SEITE.
        #
        # Entwicklung dieser Pruefung in sechs Pruefrunden, jede Stufe von einem echten
        # Fehler erzwungen:
        #   1. gar keine Pruefung  -> "Pass-Through ✗ Nein" beim G8 Plus, obwohl das
        #      Listing "unterstuetzt das Durchladen" sagt
        #   2. Pflicht nur bei "✗"  -> "Chroma-RGB ✓ Ja" fuer den Kishi V3 Pro, wo Chroma
        #      im Repo nur fuer den Kishi ULTRA belegt ist
        #   3. Teilstring-Beleg     -> dieselbe Zelle belegt mit "✗ Chroma-RGB ist
        #      Geschmackssache und fuer das Spielgefuehl ohne Nutzen"
        #   4. Datei-Herkunft per `in` -> die Seite des V3 PRO belegte eine Aussage ueber
        #      den V3, weil der Slug Praefix des laengeren ist
        #   5. Datei-Herkunft exakt -> ein Beleg von der Seite des EINEN Produkts trug
        #      eine Behauptung ueber das ANDERE, und products.json war als Datei mit allen
        #      42 Produkten ein Freifahrtschein fuer jede Zeichenfolge
        #   6. jetzt: seitengebunden. {'a': (Datei, Text), 'b': (...)} -- jede Seite, die
        #      etwas behauptet, braucht ihren eigenen Beleg, der Ordnername muss zu IHREM
        #      Produkt passen, und in products.json wird nur das Objekt DIESES Produkts
        #      durchsucht, nicht die ganze Datei.
        belege = v.get('belege', {})
        for lab in belege:
            if lab not in {x[0] for x in v.get('merkmale', [])}:
                befunde.append(f"{v['datei']}: Beleg für „{lab}“ hat keine Zeile mehr "
                               f"in merkmale — verwaist, bitte entfernen")
        for lab, wa, wb in v.get('merkmale', []):
            if lab not in belege:
                befunde.append(f"{v['datei']}: Zeile „{lab}“ hat keinen Beleg — jede "
                               f"merkmale-Zeile braucht {{'a': (Datei, Suchtext), ...}} "
                               f"oder 'EINSCHAETZUNG'")
                continue
            eintrag = belege[lab]
            if eintrag == 'EINSCHAETZUNG':
                if '✓' in wa + wb or '✗' in wa + wb:
                    befunde.append(f"{v['datei']}: Zeile „{lab}“ ist als Einschätzung "
                                   f"geführt, trägt aber ein Häkchen oder Kreuz — das "
                                   f"behauptet einen gemessenen Vorteil")
                if re.search(r'\d', wa + wb):
                    befunde.append(f"{v['datei']}: Zeile „{lab}“ ist als Einschätzung "
                                   f"geführt, nennt aber eine Zahl — Zahlen brauchen "
                                   f"einen Beleg, Einschätzungen tragen keine")
                # Auch kein Ja/Nein/Kein: Das ist eine Tatsachenbehauptung, kein Urteil.
                # Probe des Pruefers: ('Wasserdicht', 'Ja', 'Nein') lief durch.
                if re.search(r'\b(?:ja|nein|kein|keine|keinen|nicht|ohne)\b',
                             wa + ' ' + wb, re.I):
                    befunde.append(f"{v['datei']}: Zeile „{lab}“ ist als Einschätzung "
                                   f"geführt, behauptet aber mit Ja/Nein/Kein eine "
                                   f"Tatsache — die braucht einen Beleg")
                continue
            if not isinstance(eintrag, dict):
                befunde.append(f"{v['datei']}: Beleg für „{lab}“ hat die falsche Form — "
                               f"erwartet {{'a': (Datei, Suchtext), 'b': ...}} oder "
                               f"'EINSCHAETZUNG'")
                continue
            for seite, wert in (('a', wa), ('b', wb)):
                # "keine Angabe" behauptet ausdruecklich nichts und braucht nichts.
                behauptet = wert.strip() and wert.strip() != 'keine Angabe'
                if not behauptet:
                    if seite in eintrag:
                        befunde.append(f"{v['datei']}: Zeile „{lab}“ hat einen Beleg für "
                                       f"Seite {seite}, die Zelle sagt aber nur "
                                       f"„{wert}“ — überflüssiger Beleg")
                    continue
                if seite not in eintrag:
                    befunde.append(f"{v['datei']}: Zeile „{lab}“ behauptet für "
                                   f"{v[seite]} „{wert}“ und hat dafür keinen Beleg")
                    continue
                paar = eintrag[seite]
                if not (isinstance(paar, tuple) and len(paar) == 2
                        and all(isinstance(x, str) and x.strip() for x in paar)):
                    befunde.append(f"{v['datei']}: Beleg für „{lab}“/{seite} ist kein "
                                   f"(Datei, Suchtext) mit Inhalt: {paar!r}")
                    continue
                quelle, suchtext = paar
                slug = v[seite]
                qpfad = os.path.join(ROOT, quelle)
                if not os.path.exists(qpfad):
                    befunde.append(f"{v['datei']}: Beleg für „{lab}“/{seite} verweist "
                                   f"auf {quelle}, die Datei gibt es nicht")
                    continue
                if quelle.endswith('products.json'):
                    # NUR das Objekt dieses Produkts, nicht die ganze Datei. Vorher war
                    # products.json mit 42 Produkten ein Freibrief: "138 g" (Backbone One)
                    # hat eine Gewichtsangabe fuer den Kishi V3 Pro belegt.
                    raum = json.dumps(by.get(slug, {}), ensure_ascii=False)
                    wo = f"dem products.json-Eintrag von {slug}"
                else:
                    ordner = os.path.basename(os.path.dirname(quelle))
                    if ordner not in {slug, f"{slug}-review"}:
                        befunde.append(f"{v['datei']}: Beleg für „{lab}“/{seite} liegt "
                                       f"in {quelle}, gehört aber nicht zu {slug} — "
                                       f"belegen darf nur die eigene Seite des Produkts "
                                       f"oder sein products.json-Eintrag")
                        continue
                    raum = open(qpfad, encoding='utf-8').read()
                    wo = quelle
                if suchtext not in raum:
                    befunde.append(f"{v['datei']}: Beleg für „{lab}“/{seite} findet "
                                   f"„{suchtext}“ nicht in {wo}")
                    continue
                # Jede Zahl der Zelle muss im Belegtext stehen, als ganze Zahl.
                # Eigenstaendiges Token, nicht `\b`. Mit `\b` belegte die "4" aus "4,4
                # von 5 aus 157 Bewertungen" eine erfundene Trigger-Zahl, die "157" eine
                # Akkulaufzeit und die "5" eine Zollangabe. Das ist §A5 v1.6 Vorschrift 3,
                # in diesem Paket geschrieben und hier 130 Zeilen weiter oben verletzt.
                # Zahl MIT Einheit, wo eine steht: Sonst belegt "157 Bewertungen" eine
                # erfundene Laufzeit von "157 Stunden" (Pruefbericht, Probe 16).
                for zahl, einheit in _EINHEIT.findall(wert):
                    if not re.search(rf'(?<![\w,.-]){re.escape(zahl)}\s*'
                                     rf'{re.escape(einheit)}', suchtext):
                        befunde.append(f"{v['datei']}: Zeile „{lab}“/{seite} nennt "
                                       f"„{zahl} {einheit}“, der Belegtext "
                                       f"„{suchtext}“ nennt diese Angabe nicht")
                for zahl in set(re.findall(r'(?<![\w,.-])\d+(?![\w,.-])', wert)):
                    if not re.search(rf'(?<![\w,.-]){re.escape(zahl)}(?![\w,.-])',
                                     suchtext):
                        befunde.append(f"{v['datei']}: Zeile „{lab}“/{seite} nennt die "
                                       f"Zahl {zahl}, die im Belegtext „{suchtext}“ "
                                       f"nicht vorkommt")
                # Ein Haken behauptet einen VORTEIL. Steht der Belegtext in einer
                # Nachteils-Umgebung, belegt er das Gegenteil.
                # In BEIDE Richtungen. Die erste Fassung prueefte nur das Haekchen;
                # damit liess sich ein ✗ mit einer Zeile aus der VORTEILE-Liste belegen
                # (Pruefbericht, Befund 9). Ein Kreuz braucht eine Nachteils-Umgebung,
                # ein Haken darf keine haben.
                # Auch ohne Zeichen: "Kein Bluetooth" behauptet eine Abwesenheit
                # genauso wie "✗ Nein" (Pruefbericht, Probe 7).
                negativwort = re.match(r'\s*(?:kein|keine|keinen|ohne|nicht)\b', wert,
                                       re.I)
                if not quelle.endswith('products.json') and (wert[:1] in '✓✗'
                                                             or negativwort):
                    negativ = None
                    for m in re.finditer(re.escape(suchtext), raum):
                        davor = raum[max(0, m.start() - 160):m.start()]
                        n = (('✗' in davor and '✓' not in davor.rsplit('✗', 1)[1])
                             or 'con-item' in davor[-90:]
                             or bool(re.search(r'<h3>\s*Schwächen', davor)))
                        negativ = n if negativ is None else (negativ or n)
                        if n:
                            break
                    if wert.startswith('✓') and negativ:
                        befunde.append(
                            f"{v['datei']}: Zeile „{lab}“/{seite} setzt ein Häkchen, "
                            f"aber der Beleg „{suchtext}“ steht in {quelle} in einer "
                            f"Nachteils-Umgebung — er belegt das Gegenteil")
                    # Ein Kreuz darf seine Einschraenkung auch im TEXT tragen statt im
                    # Markup: "Nur die Trigger arbeiten mit Hall" steht in einem
                    # Prosa-Absatz, "Nur wenn du haptisches Feedback willst" in einer FAQ.
                    # Die erste Fassung verlangte eine Nachteilsliste und hat diese drei
                    # korrekten Zeilen gemeldet.
                    einschraenkend = re.search(
                        r'\b(?:kein|keine|keinen|nicht|nur|ohne|statt)\b', suchtext, re.I)
                    if ((wert.startswith('✗') or negativwort)
                            and negativ is False and not einschraenkend):
                        befunde.append(
                            f"{v['datei']}: Zeile „{lab}“/{seite} setzt ein Kreuz, aber "
                            f"der Beleg „{suchtext}“ steht in {quelle} NICHT in einer "
                            f"Nachteils-Umgebung — er belegt keine Abwesenheit")

        if len(befunde) > _vorher:
            continue

        if not os.path.exists(pfad):
            # Neues Duell: Seite anlegen, nicht melden. Dafuer braucht die Definition
            # die Rahmen-Felder; fehlen sie, ist das ein Befund und kein stilles
            # Ueberspringen.
            fehlend = [k for k in ('titel', 'kurzname', 'beschreibung', 'lead',
                                   'kurzurteil', 'abschnitte') if k not in v]
            if fehlend:
                befunde.append(f"{v['datei']}: Datei fehlt und die Definition hat "
                               f"keine Rahmen-Felder ({', '.join(fehlend)}) — eine neue "
                               f"Seite braucht sie, eine bestehende nicht")
                continue
            if CHECK:
                print(f"  {v['datei']}: wuerde NEU angelegt")
                geschrieben += 1
                continue
            os.makedirs(os.path.dirname(pfad), exist_ok=True)
            open(pfad, 'w', encoding='utf-8').write(neue_seite(v, by))
            print(f"  {v['datei']}: NEU angelegt")
        # Nur die Befunde DIESES Duells pruefen. `if befunde:` gegen die globale Liste
        # hat nach dem ersten Fund alle weiteren Duelle uebersprungen: Ein zweiter Defekt
        # weiter hinten tauchte erst nach dem Fix des ersten auf (Pruefbericht, Befund 7).
        if len(befunde) > _vorher:
            continue

        h = open(pfad, encoding='utf-8').read()

        # Die redaktionellen Abschnitte stehen AUSSERHALB des Markerblocks: Der
        # Generator schreibt sie einmal beim Anlegen und fasst sie danach nicht mehr an.
        # Damit kann die Definition von der Seite abdriften, und wer die Datei loescht,
        # bekaeme die alte Fassung zurueck. Beim Korrigieren einer sachlich falschen
        # Passage ist mir genau das passiert. Also gemeldet statt stillschweigend.
        # Der TITEL steht in <title>, og:title und twitter:title und wird ebenfalls nur
        # beim Anlegen geschrieben. Als ich den Em-Dash im Generator durch einen
        # Doppelpunkt ersetzt habe, blieb er in sechs Meta-Tags der zwei neuen Seiten
        # stehen, und drei gleichzeitig gruene Gates haben das nicht gesehen:
        # `idempotenzprobe` prueft "baumstabil" und meint damit nur den Markerblock.
        if 'titel' in v:
            soll = f"{v['titel']}: Vergleich 2026"
            for feld, muster in (('<title>', r'<title>(.*?)</title>'),
                                 ('og:title', r'<meta property="og:title" content="(.*?)"'),
                                 ('twitter:title',
                                  r'<meta name="twitter:title" content="(.*?)"')):
                m = re.search(muster, h)
                if m and m.group(1) != esc(soll):
                    befunde.append(f"{v['datei']}: {feld} lautet „{m.group(1)[:58]}“, "
                                   f"aus der Definition folgt „{soll[:58]}“ — der "
                                   f"Seitenrahmen wird nur beim Anlegen geschrieben und "
                                   f"ist abgedriftet")

        # Nicht nur `abschnitte`: `lead` und `kurzurteil` werden genauso einmal beim
        # Anlegen geschrieben und danach nie wieder abgeglichen. Der Switch-Satz, den
        # der Pruefbericht gefunden hat, stand genau dort (Pruefbericht, Befund 4).
        # Die URTEILE waren die einzigen Felder ohne jede Sachpruefung -- also genau
        # die Zeile, die den Kauf traegt. Der Pruefbericht hat vorgefuehrt, dass ein
        # urteil mit "9000 mAh Akku, Chroma-RGB und wiegt 12 g" null Befunde erzeugt.
        #
        # Geprueft werden MESSENDE Zahlen (Zahl plus Einheit), nicht jede Ziffer: Sonst
        # schlaegt die Pruefung auf Modellnamen an ("G8", "V3") und auf die Jahreszahl.
        # Gedeckt sein muss jede davon in der eigenen Tabelle oder im products.json-
        # Eintrag eines der beiden Produkte.
        # Die Tabelle aus der SEITE lesen, nicht aus  -- das wird erst weiter
        # unten gebaut.
        # URLs raus: Bild- und Video-Adressen tragen Ziffern, die nichts ueber das
        # Produkt sagen. "40 Stunden" galt durch `a40cb261`, "1 Stunde" durch
        # `eu-west-1-prod` als gedeckt.
        # URLs und Zeitcodes raus: Bild-/Videoadressen und eine Video-Laufzeit
        # ("duration": "0:30") tragen Ziffern, die nichts ueber das Produkt sagen.
        # "40 Stunden" galt durch `a40cb261`, "1 Stunde" durch `eu-west-1-prod`,
        # "30 Minuten" durch die Laufzeit als gedeckt.
        kerntext = re.sub(r'https?://\S+|\d+:\d+', ' ',
                          json.dumps([by.get(v[s], {}) for s in ('a', 'b')],
                                     ensure_ascii=False))
        tabtext = ' '.join(re.findall(r'<t[hd][^>]*>(.*?)</t[hd]>', h, re.S))
        # NUR die Tabelle. Der JSON-Dump der Produkte traegt ASINs, Bild-URLs und
        # Video-Hashes und hat die Ableitung zu einem Freibrief gemacht.
        # Dieselbe Token-Regel wie unten: `\d+` auf "4,1" liefert 4 und 1, und
        # damit galten "1 Stunde" und "2 g" als gedeckt.
        basiszahlen = {int(x) for x in re.findall(r'(?<![\w,.-])\d+(?![\w,.-])', tabtext)
                       if len(x) <= 5}
        preispaar = [re.sub(r'\D', '', pfeld(by.get(v[s], {}), 'price'))
                     for s in ('a', 'b')]
        preispaar = [z for z in preispaar if z]
        for feld in ('lead', 'kurzurteil', 'urteil', 'abschnitte'):
            if feld not in v:
                continue
            klar = re.sub(r'<[^>]+>', ' ', v[feld])
            for zahl in set(_MESSZAHL.findall(klar)):
                # Mit Wortgrenzen, nicht mit `in`. "40 Stunden" galt als gedeckt,
                # weil "40" als Teilstring in einer Bild-URL des JSON-Dumps steckt
                # (`a40cb261-...`). Vierter Praefix-Fehler derselben Art in diesem Paket.
                # Eigenstaendiges Token, nicht Teil einer Dezimalzahl: Sonst gilt die
                # "1" aus "4,1 Sterne" als Deckung fuer "1 Stunde".
                # Weder Wortzeichen noch Dezimalnachbarn. `\b` allein liess "40" in
                # "a40cb261" gelten, `(?<![,.\d])` allein ebenfalls -- es braucht beides:
                # "4,1" deckt keine "1", eine Bild-URL deckt keine "40".
                g = rf'(?<![\w,.-]){re.escape(zahl)}(?![\w,.-])'
                if (re.search(g, tabtext) or re.search(g, kerntext)
                        or zahl in _abgeleitet(basiszahlen, preispaar)):
                    continue
                befunde.append(f"{v['datei']}: {feld} nennt den Messwert {zahl}, der "
                               f"weder in der Tabelle noch im Datenkern von {v['a']} "
                               f"oder {v['b']} steht und sich auch nicht daraus "
                               f"ableiten lässt")

        # Beide Produktseiten muessen von hier erreichbar sein. Auf drei von sieben
        # Seiten verlinkte nur der VERLIERER seinen Test -- auf einer Seite, deren Zweck
        # eine Kaufentscheidung ist, fehlte der Weg zum empfohlenen Geraet.
        for seite in ('a', 'b'):
            ziel = (by.get(v[seite], {}) or {}).get('detail', '')
            if ziel and ziel not in h:
                befunde.append(f"{v['datei']}: verlinkt die Produktseite von "
                               f"{v[seite]} nicht ({ziel}) — beide Geräte eines Duells "
                               f"brauchen den Weg zu ihrem eigenen Test")

        # Marken- und Technologienamen gehoeren ihrem Geraet. Zweimal in diesem Paket
        # habe ich einen fremden vergeben: "Chroma" an den Kishi V3 Pro (gehoert dem
        # Kishi Ultra und dem Phone Cooler) und "Sensa HD" an den Kishi Ultra (gehoert
        # dem V3 Pro). Beide Male beim Beheben des jeweils anderen Falls.
        for name, eigner in _MARKENNAMEN.items():
            if name in h and not (set(eigner) & {v['a'], v['b']}):
                befunde.append(f"{v['datei']}: nennt „{name}“, das im Repo zu "
                               f"{' oder '.join(eigner)} gehört — keines der beiden "
                               f"Produkte dieses Duells")

        for feld in ('lead', 'kurzurteil'):
            if feld in v and v[feld] not in h:
                befunde.append(f"{v['datei']}: das Feld {feld} der Definition steht so "
                               f"nicht mehr auf der Seite — Definition und Seite sind "
                               f"auseinandergelaufen: "
                               f"{re.sub(r'<[^>]+>', '', v[feld])[:58]}…")
        if 'abschnitte' in v:
            for absatz in re.findall(r'<(?:p|h2)(?:\s[^>]*)?>.*?</(?:p|h2)>',
                                     v['abschnitte'], re.S):
                if absatz not in h:
                    befunde.append(f"{v['datei']}: ein Absatz der Definition steht so "
                                   f"nicht mehr auf der Seite — Definition und Seite "
                                   f"sind auseinandergelaufen: "
                                   f"{re.sub(r'<[^>]+>', '', absatz)[:60]}…")

        neu = block(v, by)
        # Genau EIN Markerpaar, sonst Befund. `find()` nimmt nur das erste Paar: Ein
        # zweiter Block (durch Kopieren leicht entstanden) bliebe dauerhaft ungepflegt
        # und wuerde alte Preise zeigen, ohne dass ein Gate je rot wird.
        na, nz = h.count(START), h.count(END)
        if na > 1 or nz > 1 or na != nz:
            befunde.append(f"{v['datei']}: {na}x VS:START und {nz}x VS:END — der "
                           f"Generator pflegt genau ein Paar, jedes weitere bliebe "
                           f"unbemerkt stehen")
            continue
        i, j = h.find(START), h.find(END)
        if i >= 0 and j > i:
            aus = h[:i] + neu + h[j + len(END):]
        else:
            # Erstlauf: den handgeschriebenen Bereich von der Tabelle bis zum Ende der
            # winner-box ersetzen. Faellt das Muster aus, wird NICHT geraten.
            m = re.search(r'<table class="vs-table".*?</div>\s*</div>', h, re.S)
            if not m:
                befunde.append(f"{v['datei']}: weder Marker noch ein erkennbarer "
                               f"Vergleichsblock (Tabelle bis winner-box) — von Hand "
                               f"auflösen, der Generator rät hier nicht")
                continue
            aus = h[:m.start()] + neu + h[m.end():]

        # Diese drei Pruefungen lesen die ENDFASSUNG, nicht die Datei auf der
        # Platte: Bei einer frisch angelegten Seite ist der Markerblock noch leer,
        # und der Markennamen-Check hat sonst erst im Folgelauf gegriffen.
        pruef = aus
        # Die zwei Knopfreihen-Klassen: benutzt <-> Regel vorhanden, und zwar genau
        # einmal global. Bewusst NICHT alle Klassen -- `.vs-table`, `.winner-box` und
        # `.winner` stehen absichtlich im Seiten-<style>, weil sie nur hier gebraucht
        # werden. Der erste Kommentar hier behauptete "jede Klasse" und versprach damit
        # mehr als die Schleife tut. `.cta-pair` fehlte auf fuenf von sieben Seiten
        # (Blocker B3), und nach dessen Behebung hatte `.cta-row` drei Zustaende: Regel
        # plus Markup, Markup ohne Regel, Regel ohne Markup. Beide Male klebten die
        # Kauf- bzw. Test-Knoepfe aneinander, und kein Gate hat es gesehen.
        for klasse in ('cta-pair', 'cta-row'):
            benutzt = f'class="{klasse}"' in pruef
            lokal = f'.{klasse}{{' in pruef
            global_ = f'.{klasse}{{' in _STYLE_CSS
            if benutzt and not global_:
                befunde.append(f"{v['datei']}: nutzt .{klasse} im Markup, aber "
                               f"assets/css/style.css hat dafür keine Regel")
            if lokal:
                befunde.append(f"{v['datei']}: definiert .{klasse} im Seiten-<style>; "
                               f"die Regel gehört genau einmal in style.css")
            if global_ and not benutzt:
                befunde.append(f"{v['datei']}: style.css definiert .{klasse}, die Seite "
                               f"nutzt sie nicht — entweder auszeichnen oder die "
                               f"Knopfreihe anders bauen")

        # Die Kopfzeile traegt drei <th scope="col">. Das war bisher nur im Generator
        # erzeugt und nirgends GEPRUEFT -- die Dokumentation behauptete einen Schutz, den
        # es nicht gab (Pruefbericht Runde 11, Blocker 2). Ohne Header-Zellen laeuft die
        # Regel `.vs-table th` ins Leere und die Tabelle ist fuer Screenreader keine.
        if pruef.count('<th scope="col">') != 3:
            befunde.append(f"{v['datei']}: hat {pruef.count('<th scope=\"col\"')} "
                           f"Header-Zellen, erwartet 3 — ohne <th> verliert die Tabelle "
                           f"ihre Navy-Kopfzeile und ihre Bedeutung für Screenreader")


        if aus != h:
            geschrieben += 1
            if not CHECK:
                open(pfad, 'w', encoding='utf-8').write(aus)
            print(f"  {v['datei']}: {'wuerde sich aendern' if CHECK else 'geschrieben'}")

    print(f"\n{len(VERGLEICHE)} Direktvergleiche, {geschrieben} "
          f"{'abweichend' if CHECK else 'geschrieben'}, {len(befunde)} Befund(e)")
    for b in befunde:
        print(f'  {b}')
    return 1 if (befunde or (CHECK and geschrieben)) else 0


if __name__ == '__main__':
    sys.exit(main())
