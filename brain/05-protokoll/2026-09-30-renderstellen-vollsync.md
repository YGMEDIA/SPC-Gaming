# 2026-09-30 · Daten · Sechs Renderstellen, ein Sync

## Was

Produktdaten werden im Repo an **sechs Stellen** gerendert. Bis heute kannte das
Sync- und Audit-Werkzeug nur eine davon. Dieses Paket bringt alle sechs unter das Gate
und behebt, was in den fünf unerfassten Stellen an veralteten Werten stand.

| # | Renderstelle | Zustand vorher |
|---|---|---|
| 1 | Produktkarte `<article class="pcard">` | gesynct, aber 29 Karten im Blindfleck |
| 2 | Hero-Lead `<p class="lead">` der Detailseite | 42 von 42 veraltet |
| 3 | Product-Schema | gesynct |
| 4 | "Technische Daten"-Tabelle + CTA-Kaufleiste | 16 Preise, 28 Bewertungen, 17 CTA veraltet |
| 5 | Empfehlungskacheln `rc-price` / `cat-count` | 35 falsche Preise |
| 6 | Vergleichstabellen `vs-table` | 8 Abweichungen, eine mit gekipptem Urteil |

Dazu: Meta-Descriptions (20 Werte auf 10 Seiten) und FAQPage-Schemas (4 Stellen).

## Der schwerwiegendste Einzelfund

`vergleich/kishi-ultra-vs-g8-plus/` markierte den **teureren** Controller als Preissieger.
Nach dem Amazon-Vollabgleich kostet der Kishi Ultra 63 Euro, der G8 Plus 76. Die Tabelle
zeigte 119 gegen 90 und setzte den Haken beim GameSir.

Das war nicht mit einer Zahl zu beheben: Die gesamte Seite argumentierte über
"29 Euro günstiger", im Lead, im Fazit, in der Sieger-Box und im Schlusssatz. Neu
geschrieben. Das Urteil bleibt beim G8 Plus, ruht jetzt aber auf Stick-Technik und
Bewertung statt auf dem Preis: "gewinnt, aber nicht mehr über den Preis, er kostet
inzwischen 13 Euro mehr."

Dieselbe Umkehr stand im FAQ-Schema von `marken/gamesir`: "der teurere Kishi Ultra".

## Was mein eigenes Werkzeug angerichtet hat

`sync_kacheln` ordnete Kacheln über den **Produktnamen** zu. Ein Label wie
"G8 Galileo vs. **Kishi V3**" endet auf einen Produktnamen, also griff die Ersetzung
mitten in den redaktionellen Teaser. Vier Untertitel auf `vergleich/index.html` wurden
durch Preise ersetzt, zwei Auszeichnungen abgeschnitten ("80 € · Testsieger" → "80 €").

Mein Code-Kommentar an dieser Stelle lautete: *"Längste Namen zuerst, damit Kishi V3
nicht in Kishi V3 Pro hineingreift."* Der Schutz war gegen Präfixe gerichtet. Das Risiko
waren Suffixe. Der Kommentar beschrieb die falsche Gefahr und hat mich in Sicherheit
gewiegt.

Behoben: Inhalt aus HEAD zurückgeholt, Zuordnung auf den **href-Slug** des umschließenden
`<a>` umgestellt, und ersetzt wird nur noch der Preis-Teil der Zelle. Zellen ohne
Euro-Betrag werden gar nicht angefasst. Dieselbe Umstellung im Audit, das sechs
Fehlalarme derselben Ursache produzierte.

## Die fünfte Renderstelle und 25 §A4-Verstöße

Die Technik-Tabelle führt das Bewertungs-Label in **zwei Varianten**: `Bewertung` (13 mal)
und `Amazon-Bewertung` (31 mal). Der Sync kannte nur die erste. 28 Zellen blieben
veraltet, und weil das Schema den korrekten Wert trug, standen auf 25 Detailseiten
gleichzeitig Schema-Werte ohne sichtbare Entsprechung. Genau das Rich-Results-Risiko,
das §A4 abwenden soll.

Behoben über eine Label-Alternation `(?:Amazon-)?Bewertung`, dazu alle Tabellen-Regexe
whitespace-tolerant. §A4-Verstöße jetzt 0, maschinell gegengeprüft.

## Weitere Funde

- **Namensdublette:** `ozkak-trigger-l1r1` und `toaluea-trigger-joystick` trugen denselben
  `name`. Jedes namensbasierte Matching war ein Münzwurf. Auf "(vergoldete Kontakte)" und
  "(Clip mit Polster)" präzisiert.
- **Gekippter Superlativ:** "das bestbewertete Mini-Gamepad" ist nach dem Abgleich ein
  Gleichstand (Ultimate Mobile und M4 Snap-On je 4,3). Auf "das meistbewertete" geändert,
  das trägt über 566 gegen 417 Bewertungen.
- **Verwaiste Detailseiten:** Zehn Longtail-Datenblätter unter `/produkte/` haben keinen
  products.json-Eintrag und liefen deshalb an jeder Prüfung vorbei. Zwei nannten den
  Ultimate 2C mit 20 statt 30 Euro. Korrigiert.

## Neue Gates

**`verify.py` Abschnitt 8: sieben datenabgeleitete Superlative.** Mehrere Claims und
Marken-Texte behaupten Spitzen- oder Alleinstellungen, die sich aus products.json
berechnen lassen. Der Amazon-Abgleich hat fünf davon stumm gekippt, obwohl jede einzelne
Zahl im Text belegt war. Die Invariante rechnet sie bei jedem Lauf neu: bestbewerteter
Razer, meistbewertetes Zubehör, am schwächsten bewerteter Controller, schwächste Bewertung
im Kühler-Segment, einziger GameSir mit BT und USB-C, Tablet-Zuordnung, und ob der
Kishi V3 noch mindestens gleichauf mit dem V3 Pro liegt. Rot/grün bewiesen.

**`audit_vergleich`** prüft zusätzlich, ob die `winner`-Markierung beim Preis noch zum
günstigeren Produkt passt.

## Verify

- `python3 scripts/verify.py` grün: 125 Seiten, 247 JSON-LD-Blöcke, 42 Produkte
- §A1-Audit: 0 harte Abweichungen
- Karten 201/201 · Hero-Leads 42/42 · Technik-Tabellen 42/42 · CTA-Leisten 42/42 ·
  Meta-Descriptions 42/42 · alle fünf Vergleichstabellen korrekt inklusive Markierung
- §A4: 0 Verstöße (vorher 25)
- Weiche Fließtext-Hinweise von 149 über 95 auf 72 gefallen, jedes Mal weil ein Teil davon
  gar kein Fließtext war, sondern generierte Struktur
- Superlativ-Invariante rot/grün bewiesen
- Drei unabhängige Prüfrunden in frischem Kontext

## Gelernt

1. **Ein Sync-Werkzeug, das über Namen matcht, zerstört früher oder später Inhalt.**
   Zuordnung gehört über eine ID, hier den Slug im href. Und es darf immer nur den Teil
   einer Zelle ersetzen, für den es zuständig ist, nie `[^<]*`.

2. **Ein Code-Kommentar, der die falsche Gefahr benennt, ist schlimmer als keiner.**
   Meiner behauptete, gegen Präfixe zu schützen, und lenkte damit von der echten
   Suffix-Falle ab. Beim nächsten Lesen habe ich ihm geglaubt statt zu prüfen.

3. **Dieselbe Information kann unter zwei Labels stehen.** `Bewertung` und
   `Amazon-Bewertung` in derselben Tabellenart, 13 zu 31. Wer eine Renderstelle erfasst,
   prüft, ob sie nur eine Schreibweise hat.

4. **Ein gekipptes Urteil ist keine Zahlenkorrektur.** Beim Kishi-Ultra-Duell hing die
   gesamte Argumentation am Preisvorsprung. Zahlen zu tauschen hätte eine Seite ergeben,
   die sich selbst widerspricht.
