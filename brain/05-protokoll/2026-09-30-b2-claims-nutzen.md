# 2026-09-30 · Content · B2: Produktkarten von Merkmal auf Nutzen

## Was

Alle 42 `claim`-Felder in products.json neu geschrieben: von Merkmalsaufzählung auf
Nutzenaussage. Maßnahme B2 aus der Bücher-Synthese (Quelle: Edwards, *Copywriting
Secrets*), von Yasin direkt beauftragt.

Beispiel für den Unterschied:

| vorher | jetzt |
|---|---|
| "Kabelgebundener Controller für Android und Windows-PC mit Hall-Effect-Sticks und Hall-Triggern." | "Driftfreie Hall-Sticks zum Einstiegspreis. Kabelgebunden, also ohne Funkverzögerung, für Android und Windows." |
| *(leer)* | "Der einzige Controller bei uns mit eingebauter Peltier-Kühlung: hält das Handy bei langen Sessions kühl. Nur Android." |

## Zwei Befunde, die beim Öffnen herausfielen

**Sieben Produkte hatten gar keinen Claim.** ASUS ROG Tessen, Backbone Pro, Backbone One
PS Edition, GameSir X2s, GameSir X3 Pro, Razer Kishi V3 Pro und Turtle Beach Atom standen
auf allen Karten ohne eine Zeile Beschreibung. Ein Besucher sah Name, Specs, Preis und
keinen Grund zu klicken.

**Zwei Claims trugen einen Preis im Text** ("für 45 €", "10 Stück für 14 €"). Die driften
bei jeder Preisänderung, und das Audit prüfte Claims bisher gar nicht.

## Drei Blindflecken im eigenen Audit

Das ist der eigentliche Ertrag dieses Pakets. Alle drei fand der Prüflauf, keinen davon ich.

**1. Der Kartenscan begann an der falschen Stelle.** `sync_cards()` und `audit()` scannten
ab der Position von `data-product`. In **29 von 202 Karten** sitzt dieses Attribut erst im
Kauf-Button, also hinter Claim und Preiszeile. Diese Karten wurden weder gesynct noch
geprüft.

Folge: **23 falsche Preise standen seit dem Vollabgleich live** (Kishi Ultra 119 statt
63 €, G8 Plus 90 statt 76 €, Razer Phone Cooler 40 statt 70 €), und 32 Claims blieben
veraltet. `verify.py` meldete durchgehend grün. Nach der Umstellung auf einen Scan ab
`<article class="pcard` meldete das Audit sofort 57 Abweichungen.

**2. Verwaiste Slugs wurden stumm übersprungen.** Drei Karten trugen `data-product`-Werte,
die products.json nicht kennt (`backbone-one` statt `backbone-one-2`,
`ozkak-trigger-joystick` statt `toaluea-trigger-joystick`). Sie fielen durch jede Prüfung
und trugen Claims von vor Monaten, inklusive der letzten drei Em-Dashes im Repo. Das Audit
meldet unbekannte Slugs jetzt als harten Fehler.

**3. Der Claim wird zweimal gerendert.** `gen_pages.py` setzt ihn zusätzlich als
`<p class="lead">` in den Hero jeder Detailseite, außerhalb jeder Karte. **42 von 42 Leads**
trugen alte Claims, 26 mit Em-Dash, 6 mit Preis. Darunter zwei Aussagen, die auf der
Kartenebene bereits zurückgezogen waren: "Der stärkste der drei Kühler" und "10 Stück für
14 €". Die Karte sagte das eine, die Produktseite drei Klicks weiter das andere.

Alle drei geschlossen. `sync_product_values.py` hat jetzt `karten_bloecke()`, `sync_leads()`
und `audit_leads()`.

## Eigene Fehler in den Claims

| Fehler | Was es war |
|---|---|
| **Zwei Produkte vertauscht** | Ich folgte den Slug-Namen statt dem Feld `name`. `ozkak-mini-portable` heißt "L1R1 Trigger-Aufsatz" (2 Auslöser), `ozkak-trigger-l1r1` heißt "Mobile Controller 4-Trigger" (4 Auslöser). Die Karten widersprachen dem Spec-Chip daneben |
| **G8 Plus: Geltungsbereich geweitet** | Satz aus `marken/gamesir` übernommen, wo er "innerhalb GameSir" galt, und auf "bei uns" ausgedehnt. Fünf Produkte können BT und USB-C, mehrere können Switch |
| **Grammatikfehler** | "schwächst bewerteter" gibt es im Deutschen nicht |
| **Zwei unmessbare Superlative** | "günstigster Trigger-Einstieg" (der Toaluea kostet 9 statt 10 €) und "einer der leichtesten" (nur ein Controller hat überhaupt eine Gewichtsangabe) |
| **Uneinheitlicher Maßstab** | Ich strich beim Black Shark einen unmessbaren Superlativ und ließ bei ozkak-mini-portable denselben Typ stehen |
| **Falsche Zuordnung** | Key-Mapping als Cloud-Gaming-Feature beschrieben; laut eigener Seite dient es Spielen OHNE native Controller-Unterstützung |

## Ein Datenkern-Fehler mitgeklärt

Der Turtle Beach Atom stand in products.json mit `worksOn: [android, ios, universal]`,
während die Review-Seite "Kein iOS-Support" sagte. Statt zu raten auf Amazon nachgesehen:
Der Titel lautet **"Turtle Beach Atom Mobil-Gaming-Controller Für Android 8.0+ Geräte"**,
iOS kommt weder im Titel noch in den Feature-Bullets vor. products.json war falsch.
`worksOn` korrigiert, Karte aus dem iPhone-Hub entfernt (ItemList und Zähler auf 25), und
die Review-Tabelle trug noch 4,0 aus 1.896 sowie 87 Euro aus der Zeit vor dem Vollabgleich.

## Verify

- `python3 scripts/verify.py` grün: 125 Seiten, 247 JSON-LD-Blöcke, 42 Produkte
- §A1-Audit: 0 harte Abweichungen
- **201 von 201 Produktkarten** deckungsgleich mit products.json (Claim und Preis)
- **42 von 42 Hero-Leads** deckungsgleich
- 0 Em-Dashes, 0 Preise in Claims und Leads (vorher 22 + 26 beziehungsweise 8 + 6)
- 0 verwaiste Karten-Slugs (vorher 3)
- products.json: kein Claim leer, keiner über 135 Zeichen, längster 117
- Drei unabhängige Prüfrunden in frischem Kontext, Freigabe in Runde 3

## Gelernt

1. **Ein Gate deckt nur ab, was es kennt, und man merkt die Lücke nicht am grünen Haken.**
   Drei Blindflecken in einem Paket, alle drei meldeten grün, während 23 falsche Preise
   live waren. Grün heißt "keine Abweichung in den geprüften Stellen", nicht "korrekt".
   Bei jedem neuen Gate gehört deshalb die Frage dazu: Welche Renderstellen gibt es für
   diese Daten, und erreiche ich sie alle?

2. **Produkte über `name` identifizieren, nie über den Slug.** Die Slugs sind historisch
   gewachsen und teils irreführend. Wer beim Texten dem Slug folgt, vertauscht Produkte.

3. **Ein Superlativ, den man nicht nachrechnen kann, gehört nicht in den Text.** Und wenn
   man einen streicht, muss man alle desselben Typs streichen. Der Prüfer hat den
   uneinheitlichen Maßstab zu Recht angemerkt.

4. **Bei widersprüchlichen Repo-Quellen entscheidet der Hersteller, nicht die Mehrheit.**
   Beim Turtle Beach stand products.json gegen die Review-Seite. Ein Blick auf den
   Amazon-Titel klärte es in einer Minute.

## Offen (in STATUS als Befund)

Der Prüflauf fand drei weitere Renderstellen, die veraltete Produktdaten tragen und älter
als B2 sind: die "Technische Daten"-Tabelle jeder Detailseite, die CTA-Kaufleiste und die
Empfehlungskacheln. Für 18 Produkte sieht ein Besucher auf dem Hub einen anderen Preis als
auf der Produktseite. Das ist das nächste Paket, mit Vorrang, weil es Geld-Content betrifft.
