# 2026-10-06 · Daten · Die acht offenen Spec-Chips, selbst bei Amazon nachgesehen

## Was

Yasin: „geh selber mit chrome auf amazon und mach alles selber." Damit ist §A5
(„Produktdaten NUR aus Yasins Screenshots") für diesen Pass aufgehoben. Gelesen wurde mit
dem Browser auf amazon.de, jede Angabe als wörtliches Zitat mit ASIN protokolliert:
`03-research/raw/amazon/2026-10-06-spec-chips-selbst-geprueft.md`. Keine Bot-Prüfung, kein
Login, nichts gekauft.

**Von acht Chip-Aussagen waren zwei belegt, drei falsch und drei unbelegt.**

| Chip | Ergebnis | Was jetzt dasteht |
|---|---|---|
| X5 Lite „Gew. 135 g" | belegt („nur 135,4 g") | in products.json |
| Kishi V3 Pro „Sticks TMR+Haptik" | belegt („Fullsize-TMR-Analogsticks", „Sensa HD-Haptik") | in products.json als `TMR + Sensa-HD-Haptik` |
| Kishi V3 „Extra 4 Rücktasten" | **falsch** | `2 Rücktasten` (Seite: „Zwei programmierbare Zurück-Tasten (M1/M2)"; die 4 sind 2 Rücktasten + 2 Bumper) |
| Kishi V3 Pro „Extra 4 Rücktasten" | **falsch** | `2 Rücktasten` |
| Ultimate 2C „Multi Switch/PC" | **falsch** | `PC + Android` (Titel: „Wired Controller for Windows PC and Android"; die Switch-Version ist ein anderes Produkt) |
| G8 Galileo „Gewicht ~230 g" | **unbelegt** | Chip entfernt (kein Produktgewicht auf der Seite) |
| Backbone Pro „Akku ~40 h" | **unbelegt** | Chip entfernt (kein Akku-Hinweis; Seite nicht verfügbar) |
| G8 Plus „Multi Switch/PC" | **unbelegt** | Chip entfernt (Listing nennt iPhone/iPad/Android) |

Die fünf belegten bzw. korrigierten Werte stehen jetzt **in products.json**, nicht nur auf
der Karte. Damit vergleicht `sync_product_values` sie ab sofort, und sie können nicht mehr
auseinanderlaufen. Gemessen: **0 ungedeckte Chip-Werte** auf allen Karten der Site.

## Zwei Befunde, größer als die Chips (für Yasin)

**1 · Der Backbone Pro ist nicht kaufbar, und die ASIN ist nicht mehr unsere.** Die Seite
sagt „Derzeit nicht verfügbar. Ob und wann dieser Artikel wieder vorrätig sein wird, ist
unbekannt", und `canonical` wie `#ASIN` nennen **B0GN92GV2Z** statt unserer B0DQM23MLZ.
Unsere Seiten bewerben ihn mit 190 € und „Verfügbar". Das ist eine Sortiments- und
Geldfrage und gehört dir.

**2 · „Verfügbar" steht 234 Mal im Markup und kommt aus nichts.** `products.json` hat kein
Verfügbarkeits-Feld; die Aussage ist hartkodiert und von keinem Gate geprüft. In einem
nachgewiesenen Fall ist sie falsch. Das ist dieselbe Klasse wie die Spec-Chips, nur
234-fach, und es ist ein eigenes Arbeitspaket.

## Warum die Preise nicht mitgeändert wurden

Nebenbei abgelesen weichen **alle sieben** Preise ab, teils deutlich (Kishi V3 Pro 123,72 €
statt 152 €, G8 Galileo 67,99 € statt 80 €), und sechs Bewertungszahlen sind gestiegen.
Eingetragen ist davon **nichts**: Der Datenstand ist eine Konstante für das ganze Repo
(`DATENSTAND_MONAT`, heute „September 2026"). Sieben Preise auf Oktober zu ziehen würde die
anderen 35 falsch ausweisen. Entweder Vollabgleich über alle 42 oder keiner. Die Zahlen
liegen im Beleg-Protokoll bereit.

## Verify

- **Vierzehn Gates exit 0**; die neuen Werte fließen über `gen_bestenliste` in die
  Bestenlisten nach
- **0 ungedeckte Chip-Werte** auf allen Karten (vorher 14, davon 5 ohne Beleg lösbar und
  8 beleg­pflichtig)
- Das TMR-Gate aus dem S1-Pass musste mitwachsen: Es verlangte **genau einen** Controller
  mit TMR; mit dem belegten Spec des V3 Pro sind es zwei. Jetzt prüft es
  **Vollständigkeit** (jedes TMR-Modell muss im Satz stehen) und die **Verbform**
  (nutzt/nutzen). Vier Formen gemessen, 0 falsch
- `links_batterie.py` unverändert grün

## Gelernt

1. **Ein Massen-Replace über zwei Produkte ist eine Behauptung über beide.** Ich habe
   „Multi: Switch/PC" in einem Rutsch durch „PC + Android" ersetzt — für den Ultimate 2C
   belegt, für den G8 Plus frei erfunden, weil dessen Listing gar keinen PC nennt.
   Aufgefallen ist es nur, weil ich nach dem Schreiben noch einmal gemessen habe. Zwei
   Produkte, zwei Belege, zwei Edits.
2. **Ein Beleg kann eine Zahl halbieren.** „4 Rücktasten" stand auf zwei Karten und war auf
   beiden falsch: Es sind 2 Rücktasten plus 2 Bumper. Niemand hätte das bemerkt, weil die
   Zahl plausibel klingt und die Quelle nie gelesen wurde.
3. **Ein Gate, das die Welt zum Zeitpunkt seiner Entstehung beschreibt, altert mit den
   Daten.** Mein TMR-Gate von gestern verlangte genau einen TMR-Controller. Heute gibt es
   zwei — und das Gate hat korrekt gemeldet, statt stumm zu bleiben. Die Lehre ist nicht,
   dass es falsch war, sondern dass die Korrektur wieder in beide Richtungen geprüft
   gehört: Der neue Satz wäre sonst durch das alte Muster gefallen und ungeprüft gewesen.
