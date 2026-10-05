# 2026-10-05 · Content · X2s-Retro-Winkel: geprüft, nicht gebaut

## Was

Warteschlangen-Punkt aus dem Markt-Signal vom 21.07.2026
(`03-research/2026-07-21-markt-youtube-rankings.md`): Zwei YouTube-Rankings nennen den
GameSir X2s „günstig/Retro", wir führen ihn nur als Bluetooth-Teleskop. Auftrag:
„X2s-Review/Karten um Retro-/Emulator-Winkel ergänzen (kleiner Edit)."

**Die Prämisse hält der eigenen Datenlage nicht stand. Der Winkel ist nicht gebaut.**

## Die Messung

**Der X2s in unseren Daten:** 53 €, **3,9 Sterne aus 103 Bewertungen**, `Verb.: Bluetooth`.
Einen `Sticks`-Eintrag führt products.json **nicht** — die Hall-Effect-Aussage steht nur im
`claim` und im Spec-Chip der Seite und ist einer der 14 unbelegten Chips, die seit B6 auf
Yasins Liste stehen (§A5).

**Unter den 17 Bluetooth-Controllern im Sortiment:**

| | Zahl |
|---|---|
| günstiger als der X2s | 14 |
| günstiger **und** besser bewertet | **12** |
| Rang des X2s nach Bewertung | **15 von 17** |
| schlechter bewertet als er | 2 (Turtle Beach Atom 3,5 · Scuf Nomad 3,8) |

Die zwei, die für Emulation naheliegen, sind beide besser: **8BitDo Ultimate Mobile**
45 €, 4,3 aus 566 · **abxylute M4 SnapOn** 50 €, 4,3 aus 417. Der M4 trägt im `claim`
sogar genau diese Aussage: „Für Retro-Emulatoren unterwegs gebaut."

**Die Site deckt das Thema längst ab:** 19 Stellen auf 127 Seiten nennen Retro oder
Emulation. `blog/usb-c-vs-bluetooth` führt eine Entscheidungstabelle („Emulation/Casual →
Bluetooth OK", „Tablet/Multi-Device → Bluetooth ideal"), der 8BitDo-Hub ist als
„Multi-Plattform und Retro-Gaming" positioniert, und der M4 SnapOn trägt die
Retro-Aussage auf sechs Seiten.

**Und der X2s ist längst positioniert:** 45 Stellen nennen ihn, darunter vier
Longtail-Seiten ausgelaufener Modelle (GameSir X2, G4s, ipega 9023, ipega 9083s), die ihn
als „beste Alternative" und „zeitgemäßen Teleskop-Nachfolger" führen. Das ist seine Rolle
im Sortiment, und sie ist belegt.

## Warum nicht gebaut

Ihn als Retro-/Emulator-Empfehlung zu positionieren hieße, für diesen Zweck unseren
**zweitschlechtesten** Bluetooth-Controller zu empfehlen, während zwei besser bewertete
und günstigere danebenstehen. Das verstößt gegen §A6 und gegen das, was seine eigene Seite
seit B10 sagt: Dort steht der Hinweis, dass der X5 Lite günstiger und besser bewertet ist.

Ein YouTube-Ranking ist ein Grund **nachzusehen**, kein Beleg. Hier hat das Nachsehen die
Prämisse widerlegt: „günstig" ist der X2s in unserem Sortiment nicht (14 Bluetooth-Modelle
sind billiger), und „Retro" belegt bei ihm nichts in den Daten.

## Was die Messung stattdessen gefunden hat

Auf `marken/gamesir/index.html`, einem der zehn Impressions-Träger, stand:

> „X3 Pro (4,0) und **X2s (3,8)** liegen unter dem **gleich teuren** X5 Lite (4,2)."

Zwei Fehler in einem Satz: Der X2s hat **3,9**, und mit 53 € gegen 45 € ist er auch nicht
gleich teuer. Zwei Absätze weiter sagt dieselbe Seite korrekt „der X2s bei 3,9" — die
Seite widersprach sich selbst.

**Warum kein Gate das gesehen hat:** `audit_prosa.py` prüft die Fließtext-Werte, die es
kennt, und das Drift-Gate der Marken-Sektionen fragt, ob eine Zahl irgendwo in den Daten
**vorkommt**. 3,8 kommt vor: als §A6-Schwelle und als Bewertung des Scuf Nomad. Eine Zahl,
die anderswo gedeckt ist, besteht jede Abdeckungsprüfung. Geprüft werden muss die **Rolle**.

**Neues Gate (§A1):** Eine Bewertung in Klammern hinter einem Produktlink muss die
Bewertung **dieses** Produkts sein. Repoweit gab es genau eine Stelle dieser Form, und sie
war falsch. Satz korrigiert.

## Verify

- **Vierzehn Gates, jedes exit 0**
- Neues §A1-Gate in beide Richtungen: Bewertung verfälscht und um eine Stelle daneben →
  rot; richtige Bewertung hinter einem Produktlink, Zahl in Klammern ohne Produktlink,
  Link auf eine Nicht-Produktseite mit Zahl dahinter → grün
- **`scripts/links_batterie.py` von 98 auf 102 Fälle**, 0 falsch
- Die Zahlen oben stammen alle aus products.json und den ausgelieferten Seiten, gemessen
  am 05.10.2026; die Mengen sind reproduzierbar (17 Bluetooth-Controller über
  `Verb.`-Spec, 19 Retro-Stellen über den sichtbaren Text aller 127 Seiten)

## Gelernt

1. **Ein Markt-Signal ist ein Grund nachzusehen, kein Beleg.** Der Punkt stand zweieinhalb
   Monate in der Warteschlange und klang plausibel. Zehn Minuten Messen haben ihn
   widerlegt. Die Reihenfolge „erst messen, dann bauen" hat hier nicht einen Fehler im Bau
   verhindert, sondern den Bau selbst.
2. **Ein Nein gehört genauso dokumentiert wie ein Ja.** Ohne diesen Eintrag steht derselbe
   Punkt beim nächsten Markt-Signal wieder da, und jemand baut ihn.
3. **Eine Zahl kann gedeckt und trotzdem falsch sein.** 3,8 ist eine echte Zahl aus den
   Daten, nur nicht die dieses Produkts. Abdeckung ist nicht Richtigkeit, und das ist
   dieselbe Lehre wie bei den Teilstring-Prüfungen aus B10 und B11 — hier aber einmal
   gegen eine Zahl, die live auf einer der zehn sichtbarsten Seiten stand.
