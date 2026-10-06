# Amazon-Beleg · 06.10.2026 · die acht offenen Spec-Chips, selbst nachgesehen

> **Abweichung von §A5, auf Yasins Anweisung:** „geh selber mit chrome auf amazon und mach
> alles selber". Bisher galt „Produktdaten NUR aus Yasins Screenshots". Gelesen wurde mit
> dem Browser auf amazon.de, jede Angabe unten ist ein wörtliches Zitat der Produktseite
> mit ASIN. Keine Bot-Prüfung, kein Login, nichts gekauft.

## Ergebnis in einem Satz

**Von acht Chip-Aussagen waren zwei belegt, drei falsch und drei unbelegt.**

| # | Produkt | Chip | Was die Amazon-Seite sagt | Ergebnis |
|---|---|---|---|---|
| 1 | GameSir X5 Lite `B0DXPMVCWC` | Gew. 135 g | „Mit einem Gewicht von nur **135,4 g**" · „Produktabmessungen: 19 x 8,5 x 4,6 cm; **135,4 Gramm**" | **belegt** |
| 2 | GameSir G8 Galileo `B0CXHVCTW9` | Gewicht ~230 g | kein Produktgewicht. Einzige Gewichtsangabe: „Produktabmessungen: **1 x 1 x 1 cm; 520 Gramm**" (Versandgewicht, Maße offensichtlich Platzhalter). Volltextsuche nach „23x g": null Treffer | **unbelegt** |
| 3 | Backbone Pro `B0DQM23MLZ` | Akku ~40 h | kein Akku-Hinweis. Die Seite hat **einen einzigen Bullet** (Kompatibilität) und meldet „**Derzeit nicht verfügbar**" | **unbelegt** |
| 4 | Razer Kishi V3 `B0F2JFWSJ5` | Extra: 4 Rücktasten | „mit **2 Rücktasten**, die in die ergonomischen Griffe eingebaut sind" · „**Zwei programmierbare Zurück-Tasten (M1/M2)**" · „Duale Mausklick-Rücktasten **& Klauengriff-Bumper** – 4 frei belegbare Tasten" | **falsch**: 2 Rücktasten + 2 Bumper |
| 5 | Razer Kishi V3 Pro `B0F2JGV9NK` | Extra: 4 Rücktasten | identischer Wortlaut wie beim V3 | **falsch** |
| 6 | Razer Kishi V3 Pro `B0F2JGV9NK` | Sticks: TMR+Haptik | „**Fullsize-TMR-Analogsticks** mit austauschbaren Kappen" · „Razer **Sensa HD-Haptik** & Razer Chroma RGB" | **belegt** |
| 7 | 8BitDo Ultimate 2C `B0D72WYT8Z` | Multi: Switch/PC | Titel: „**Wired** Controller for **Windows PC and Android**" · „Plattform: **Windows, Android**" · „Kabelgebundene Verbindung (abnehmbar) und kompatibel mit **Windows und Android**". Die Switch-Version ist ein **anderes Produkt** („8Bitdo Ultimate 2C **Bluetooth** Controller for Switch") | **falsch**: PC ja, Switch nein |
| 8 | GameSir G8 Plus `B0FYQ1SHHS` | Multi: Switch/PC | Titel: „Mfi Phone Controller für **iPhone 15/16/17/iPad Mini & Android**". Switch erscheint nur in Fremdinhalten: Amazon-Navigationsleiste und einer **anderen Variante** („G8 Plus **Bluetooth** … für Switch") | **unbelegt** |

## Zwei Befunde, die größer sind als die Chips

### 1 · Backbone Pro ist nicht kaufbar, und die ASIN ist nicht mehr unsere

```
Seite:      "Derzeit nicht verfügbar. Ob und wann dieser Artikel wieder
             vorrätig sein wird, ist unbekannt."
canonical:  amazon.de/BACKBONE-Controller-.../dp/B0GN92GV2Z
#ASIN:      B0GN92GV2Z          (unsere: B0DQM23MLZ)
```

Unser Affiliate-Link zeigt auf ein Listing, das auf eine **andere ASIN** umleitet und
**nicht verfügbar** ist. Unsere Seiten bewerben das Produkt mit „190 €" und „Verfügbar".

### 2 · „Verfügbar" steht 234 Mal im Markup und kommt aus nichts

`products.json` hat **kein Verfügbarkeits-Feld**. Die Aussage ist hartkodiert, von keinem
Gate geprüft und in mindestens einem Fall nachweislich falsch. Das ist dieselbe Klasse wie
die Spec-Chips, nur 234-fach.

## Preise und Bewertungen, nebenbei mitgelesen (NICHT eingetragen)

| Produkt | products.json | Amazon 06.10. |
|---|---|---|
| GameSir X5 Lite | 45 € · 4,2 (1.953) | 35,99 € (statt 44,99 €) · 4,2 (1.977) |
| GameSir G8 Galileo | 80 € · 4,2 (706) | 67,99 € · 4,2 (705) |
| Backbone Pro | 190 € · 4,4 (459) | nicht verfügbar |
| Razer Kishi V3 | 88 € · 4,4 (153) | 78,22 € · 4,4 (157) |
| Razer Kishi V3 Pro | 152 € · 4,2 (151) | 123,72 € · 4,2 (152) |
| 8BitDo Ultimate 2C | 30 € · 4,6 (2.188) | 28,17 € · 4,6 (2.205) · „Nur noch 1 auf Lager" |
| GameSir G8 Plus | 76 € · 4,1 (557) | 71,99 € · 4,1 (564) |

**Bewusst nicht eingetragen:** Der Datenstand ist eine Konstante für das ganze Repo
(`DATENSTAND_MONAT` in verify.py, heute „September 2026"). Würde ich sieben Preise auf
Oktober ziehen, wären die anderen 35 falsch ausgewiesen. Entweder Vollabgleich über alle
42 Produkte oder keiner — das ist der preis-loop, nicht dieser Pass.
