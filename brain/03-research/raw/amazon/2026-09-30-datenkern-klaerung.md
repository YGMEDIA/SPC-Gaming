# Amazon-Abgleich 30.09.2026 — Klärung der drei Datenkern-Widersprüche

**Anlass:** Der Faktencheck der Marken-Keyword-Offensive fand drei Stellen, an denen
products.json und unsere eigenen Review-Seiten sich widersprechen. Yasin: "öffne selbst
in chrome amazon und schau selber nach."

**Methode:** Amazon-Produktseiten in Yasins Chrome geöffnet (P-8/P-9-Weg), Titel,
Feature-Bullets, Preis und Bewertung per DOM-Abfrage aus der Seite gelesen. Für die
Tablet-Frage zusätzlich geprüft, ob "iPad"/"Tablet" im EIGENEN Produkttext steht oder
nur in Fremdempfehlungen und Varianten-Listings weiter unten auf der Seite. Dieser
Unterschied war entscheidend.

---

## Befund je Produkt

### 1. 8BitDo Ultimate 2C — ASIN B0D72WYT8Z · products.json war FALSCH

| Feld | products.json (Stand 21.07.) | Amazon 30.09.2026 |
|---|---|---|
| Name | Ultimate 2C **Wireless** | Ultimate 2C **Wired** |
| Verbindung | Bluetooth | **kabelgebunden (abnehmbar)**, 1000 Hz Polling |
| Plattform | android, ios, universal | **Windows PC und Android** |
| Switch | im claim behauptet | **nicht genannt** |
| Preis | 20 € | **29,99 €** |
| Bewertung | 4,5 (854) | **4,6 (2.188)** |

Originaltitel: "8Bitdo Ultimate 2C **Wired** Controller for **Windows PC and Android**,
with 1000Hz Polling Rate, Hall Effect Joysticks and Hall Triggers, and Remappable L4/R4
Bumpers (Mint)". Erstes Feature-Bullet: "**Kabelgebundene Verbindung (abnehmbar)** und
kompatibel mit **Windows und Android**."

→ **Unsere Review-Seite hatte recht** ("Wired", "kabelgebunden", "Kein iOS-Support",
"nicht Switch"). products.json muss korrigiert werden: Name, Verbindung, worksOn, claim,
Preis, Bewertung.

### 2. GameSir X3 Pro — ASIN B0DCVZWNMY · products.json war FALSCH

| Feld | products.json | Amazon 30.09.2026 |
|---|---|---|
| Plattform | android, ios, universal | Titel sagt **"Android Controller"** |
| Preis | 90 € | **44,99 €** (halber Preis!) |
| Bewertung | 3,9 (283) | **4,0 (306)** |

Originaltitel: "GameSir X3 Pro Moblie Game Controller, **Android Controller**, Zero Delay
Mobile Controller ... unterstützen Cloudy Gaming, Stadia". Kühlung bestätigt:
"900 mm² große Kühlplatte mit einer maximalen Kühlleistung von 12 W".

→ **Unsere Review-Seite hatte recht** ("Nur Android USB-C (kein iOS)"). `worksOn` muss
`ios` verlieren. Die Preisabweichung ist die größte im Abgleich.

### 3. Razer Kishi V3 — ASIN B0F2JFWSJ5 · products.json war RICHTIG, Review-Seite FALSCH

| Feld | products.json | Amazon 30.09.2026 |
|---|---|---|
| Tablet | `worksOn` ohne `tablet` | Titel: "für iPhone und Android **Smartphones**" |
| Preis | 93 € | **88,29 €** |
| Bewertung | 4,4 (126) | **4,4 (153)** |

Feature: "innovative Teleskopbrücke, die **iPhones (iPhone 15 series und höher) und
Android Geräte** überstützt". Kein iPad, kein Tablet im eigenen Produkttext.

→ Die iPad-Treffer auf der Seite stammen **ausschließlich aus Fremdempfehlungen**
(GameSir G8 Plus, abxylute S9) im "Ähnliche Produkte"-Bereich. Unsere Review-Seite
behauptet "iPad Mini" in der Kompatibilitätsliste. **Das ist falsch und muss dort weg.**
Der Tablet-Blog erbt den Fehler.

### 4. Razer Kishi V3 Pro — ASIN B0F2JGV9NK · products.json war FALSCH

| Feld | products.json | Amazon 30.09.2026 |
|---|---|---|
| Tablet | `worksOn` ohne `tablet` | Titel: "und **Tablets 8\"**" |
| Preis | 149 € | **151,90 €** |
| Bewertung | 4,4 (125) | **4,2 (151)** |

Titel: "Razer Kishi V3 Pro - Full-Size-Mobile-Controller für iPhone, Android-Smartphones
**und Tablets 8\"**". Feature: "**Für iPads & Android-Tablets bis zu 8 Zoll**".

Anmerkung: Ein weiteres Feature auf derselben Seite spricht von "iPads und
Android-Tablets **bis zu 13 Zoll**". Amazon widerspricht sich hier selbst. Titel und
Hauptfeature sagen 8 Zoll, das ist die belastbarere Angabe, und sie deckt sich mit der
Größenangabe des Kishi Ultra.

→ Der V3 Pro **kann** Tablets. `worksOn` braucht `tablet`. Die Bewertung ist von 4,4 auf
**4,2** gefallen, das verschiebt die Razer-Markenstatistik.

### 5. GameSir X5 Lite — ASIN B0DXPMVCWC · products.json war RICHTIG, Review-Seite FALSCH

| Feld | products.json | Amazon 30.09.2026 |
|---|---|---|
| Tablet | `worksOn` ohne `tablet` | **kein iPad/Tablet im eigenen Text** (maschinell geprüft) |
| Preis | 45 € | **44,99 €** |
| Bewertung | 4,2 (1.655) | **4,2 (1.953)** |

Titel: "GameSir X5 Lite Mobile Gaming Controller für **Android & iPhone 15/16 Serie
(USB-C)**". Feature: "funktioniert mit den meisten Android Telefonen und iphone 15/16
Serien mit Abmessungen zwischen **105 mm und 213 mm**".

Maschinelle Prüfung von Titel plus Feature-Bullets: `ipad_im_eigenen_text: false`,
`tablet_im_eigenen_text: false`. Die iPad-Treffer kamen aus einem anderen Listing
("GameSir X5 Lite ... iPad Mini 6/7 (USB-C), PC Controller") und aus Fremdempfehlungen.

→ Unsere Review-Seite nennt "iPad Mini 6/7". Das gehört **nicht zu dieser ASIN** und
muss dort korrigiert werden.

---

## Konsequenzen

**Die drei Widersprüche sind aufgelöst, aber nicht einseitig:** Zweimal hatte die
Review-Seite recht (8BitDo 2C, X3 Pro), zweimal products.json (Kishi V3, X5 Lite),
einmal lagen beide daneben (Kishi V3 Pro: Tablet fehlte in products.json).

**Nebenbefund, gravierender als der Anlass:** Bei 5 von 5 geprüften Produkten weichen
Preis oder Bewertung ab, teils erheblich (X3 Pro 90 statt 45 Euro, 8BitDo 2C 2.188 statt
854 Bewertungen, Kishi V3 Pro von 4,4 auf 4,2 gefallen). Der Belegstand von products.json
ist der 21.07.2026, über zwei Monate alt. Wenn 5 von 5 Stichproben abweichen, ist der
Vollabgleich über alle 42 Produkte überfällig, nicht optional.
