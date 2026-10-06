# Amazon-Beleg · 06.10.2026 · Vollabgleich über alle 42 Produkte

> **Abweichung von §A5, auf Yasins Anweisung:** „geh selber mit chrome auf amazon und mach
> alles selber" und „mach den vollabgleich für alle 42". Bisher galt „Produktdaten NUR aus
> Yasins Screenshots". Gelesen wurde mit dem Browser auf amazon.de, jedes Produkt über
> `amazon.de/dp/[ASIN]`, abgefragt wurden Buybox-Preis, Sternwert, Bewertungszahl,
> Verfügbarkeitstext und `#ASIN` + `canonical` (um Weiterleitungen zu erkennen).
> Keine Bot-Prüfung, kein Login, nichts gekauft.

## Ergebnis in Zahlen

| | |
|---|---|
| Produkte gelesen | **42 von 42** |
| Preise geändert | **12** |
| Bewertungen geändert | **29** |
| nicht neu kaufbar | **6** |
| Preis GESTIEGEN | **1** (Scuf Nomad, 40 € → 75 €) |

Der Datenstand ist von **September 2026 (30.09.)** auf **Oktober 2026 (06.10.)** gezogen.
Das war die Bedingung aus dem Vorlauf: Der Datenstand ist eine Konstante für das ganze
Repo, also entweder alle 42 oder keiner.

## Die vier auffälligen Fälle

**1 · Der Scuf Nomad kostet fast das Doppelte: 40 € → 75 €.** Der einzige gestiegene
Preis, und mit 35 € der größte Einzelbetrag der ganzen Welle. Belegt mit Titel und
Buybox: „Scuf NOMAD Kabelloser iPhone Controller …", `75,00 €`, Add-to-cart vorhanden,
„Nur noch 2 auf Lager". Damit kippen drei Aussagen, die bei 40 € stimmten: „mit 75 €
günstig für die Ausstattung", „günstiger als die meisten iPhone-Controller im Sortiment"
(tatsächlich sind 18 von 23 anderen günstiger) und „Für 36 € mehr bietet der G8 Plus"
(der G8 Plus ist jetzt 3 € BILLIGER). Alle drei sind nachgezogen.

**2 · Sechs von 42 Produkten sind nicht neu kaufbar.** Das ist eine Sortimentsfrage und
gehört Yasin:

| Produkt | Lage auf amazon.de |
|---|---|
| backbone-pro | „Derzeit nicht verfügbar", und `canonical`/`#ASIN` nennen **B0GN92GV2Z** statt unserer B0DQM23MLZ |
| gamesir-x3-pro | „Derzeit nicht verfügbar", kein Add-to-cart |
| hellcool-controller | „Derzeit nicht verfügbar", kein Add-to-cart |
| toaluea-trigger-joystick | „Derzeit nicht verfügbar", kein Add-to-cart |
| turtle-beach-atom | **nur gebraucht** („Kaufen Gebraucht: 10,55 €"), kein Neuangebot |
| shanwan-metallic | **keine Buybox**, kein Add-to-cart, nur „Alle Angebote" (Drittanbieter) |

**3 · „Verfügbar" kommt jetzt aus dem Datenkern.** Die Aussage stand 197 Mal als Literal
im Markup und kam aus nichts; für diese sechs Produkte war sie nachweislich falsch.
products.json hat jetzt ein Feld `stock` mit vier Werten (`ja` · `nein` · `gebraucht` ·
`drittanbieter`), alle fünf Renderer und das Product-Schema lesen es, und ein Gate hält
Karte, Schema und Datenkern zusammen. Die Werte sind absichtlich grob: Amazons „Nur noch
2 auf Lager" ist morgen falsch, deshalb heißt `ja` „neu kaufbar, Knappheitshinweis
eingeschlossen".

**4 · Zwei Produkte teilen eine Bewertung.** `shanwan-teleskop-black` (B0C9J45XCV) und
`shanwan-metallic` (B0D1KFNLLM) tragen beide 4,2 (830): Es sind Farbvarianten desselben
Listings, Amazon führt die Rezensionen gemeinsam. Das ist kein Fehler, aber ein Grund,
warum eine globale Ersetzung dieses Werts beide Produkte trifft (und hier auch soll).

## Alle 42, wie gelesen

Fett = geändert. Bewertungen in der Form `Sterne (Anzahl)`.

| Produkt | ASIN | Preis | Bewertung | Verfügbarkeit |
|---|---|---|---|---|
| 8bitdo-ultimate-2c | `B0D72WYT8Z` | 30 € → **28 €** | 4,6 (2.188) → **4,6 (2.205)** | Nur noch 1 auf Lager |
| 8bitdo-ultimate-mobile | `B0DK36N98Q` | 45 € | 4,3 (566) → **4,3 (571)** | Auf Lager |
| abxylute-m4-snapon | `B0FWBYDF8Y` | 50 € | 4,3 (417) → **4,3 (427)** | Auf Lager |
| abxylute-s8 | `B0FJ1GGMMZ` | 46 € | 4,3 (273) | Auf Lager |
| asus-rog-tessen | `B0BRYX6RQR` | 83 € | 3,9 (135) → **3,9 (134)** | Auf Lager |
| backbone-one-2 | `B0CTJ45GLG` | 63 € | 4,3 (57) → **4,3 (58)** | Auf Lager |
| backbone-one-ps | `B0BHH8DT37` | 76 € → **75 €** | 4,1 (331) | Auf Lager |
| backbone-pro | `B0DQM23MLZ` | 190 € | 4,4 (459) | **nicht verfügbar** · ASIN → B0GN92GV2Z |
| easysmx-m15 | `B0D97VQGFT` | ca. 50 € → **ca. 42 €** | 4,1 (767) → **4,1 (772)** | Auf Lager |
| gamesir-g8-galileo | `B0CXHVCTW9` | 80 € → **68 €** | 4,2 (706) → **4,2 (705)** | Auf Lager |
| gamesir-g8-plus | `B0FYQ1SHHS` | 76 € → **72 €** | 4,1 (557) → **4,1 (564)** | Auf Lager |
| gamesir-x2s | `B0D5GTM2PL` | 53 € | 3,9 (103) | Auf Lager |
| gamesir-x3-pro | `B0DCVZWNMY` | 45 € | 4,0 (306) → **4,0 (308)** | **nicht verfügbar** |
| gamesir-x5-lite | `B0DXPMVCWC` | 45 € → **36 €** | 4,2 (1.953) → **4,2 (1.977)** | Auf Lager |
| hellcool-controller | `B0F4JPSWDT` | ab 50 € | 4,0 (64) | **nicht verfügbar** |
| marsgaming-mgp-bt2 | `B0F3P8L1B8` | ca. 30 € | 4,2 (40) → **4,2 (41)** | Auf Lager · Lieferung erst 3. November |
| marsgaming-mgpx | `B0D9HGJ1ZB` | ca. 34 € → **ca. 23 €** | 4,1 (430) → **4,1 (433)** | Auf Lager |
| marsgaming-mgpxpro | `B0G8JXCNB3` | ca. 36 € | 4,3 (16) | Auf Lager |
| razer-kishi-ultra | `B0CXY4MWKR` | 63 € | 4,0 (119) | Nur noch 6 auf Lager |
| razer-kishi-v3 | `B0F2JFWSJ5` | 88 € → **78 €** | 4,4 (153) → **4,4 (157)** | Auf Lager |
| razer-kishi-v3-pro | `B0F2JGV9NK` | 152 € → **124 €** | 4,2 (151) → **4,2 (152)** | Auf Lager |
| scuf-nomad | `B0D7D83HBN` | 40 € → **75 €** | 3,8 (156) → **3,9 (157)** | Nur noch 2 auf Lager |
| shanwan-bt-white | `B0BR7LGZ8W` | ca. 40 € | 4,1 (996) → **4,1 (998)** | Auf Lager |
| shanwan-metallic | `B0D1KFNLLM` | ca. 45 € | 4,2 (826) → **4,2 (830)** | **nur Drittanbieter** |
| shanwan-teleskop-black | `B0C9J45XCV` | ca. 40 € | 4,2 (826) → **4,2 (830)** | Auf Lager |
| trust-gxt-rgb | `B0DVLTX8SX` | 40 € → **37 €** | 4,2 (355) → **4,2 (361)** | Auf Lager |
| turtle-beach-atom | `B0BDXSWZMF` | 45 € | 3,5 (649) → **3,5 (653)** | **nur gebraucht** (10,55 €) |
| viture-8bitdo | `B0F5WRZ3LJ` | 64 € | 3,9 (254) → **3,9 (253)** | Nur noch 12 auf Lager |
| black-shark-funcooler | `B0GWL9QDRG` | 32 € → **30 €** | 4,1 (185) → **4,2 (195)** | Auf Lager |
| magnet-peltier-cooler | `B0F1FW7BYG` | 16 € | 3,6 (165) → **3,6 (166)** | Auf Lager |
| ouligay-sleeves | `B0C9D8BB9B` | 7 € | 4,2 (267) | Auf Lager |
| ozkak-6finger | `B0CNPVCJCL` | 17 € | 3,7 (110) → **3,8 (112)** | Auf Lager |
| ozkak-mini-portable | `B07ZQ9G7ZX` | 10 € | 3,8 (328) → **3,9 (330)** | Auf Lager |
| ozkak-trigger-gamepad | `B096S5WV62` | 33 € | 3,6 (279) → **3,7 (280)** | Auf Lager |
| ozkak-trigger-l1r1 | `B0BGR4DGSQ` | 18 € | 4,0 (687) | Auf Lager |
| ozkak-trigger-set | `B086JPTLDD` | 27 € | 4,2 (478) | Auf Lager |
| razer-phone-cooler | `B09LVF2RYL` | 70 € | 3,3 (74) | Auf Lager |
| risoka-finger-sleeves | `B0BN98QRK2` | 14 € | 4,4 (3.147) → **4,4 (3.167)** | Auf Lager |
| risoka-trigger | `B0DPQQJYL4` | 20 € | 4,0 (87) → **4,0 (88)** | Auf Lager |
| rxkfigx-sleeves | `B0D9Y9116S` | 7 € | 3,6 (39) | Auf Lager |
| toaluea-trigger-joystick | `B0F3JF5P5J` | 9 € | 4,1 (85) | **nicht verfügbar** |
| wllhyf-sleeves | `B0DTTT23P7` | 7 € | 4,2 (86) → **4,2 (89)** | Auf Lager |

## Nachtrag: Hall-Effect, am selben Tag nachgeschlagen

Aufgefallen im zweiten Prüflauf: `blog/hall-effect-erklaert` nannte „Fünf der 28
Controller" mit Hall-Effect, während **zehn Claims** damit werben. Am Listing geklärt,
wörtlich zitiert:

| Produkt | ASIN | Was die Amazon-Seite sagt | Ergebnis |
|---|---|---|---|
| 8BitDo Ultimate Mobile | `B0DK36N98Q` | Titel: „Bluetooth Mobile Game Controller with **Hall Effect Joysticks and Hall Triggers**" · „**Hall-Effekt**" | **belegt** |
| abxylute S8 | `B0FJ1GGMMZ` | Titel: „Drahtloses Gamepad mit **Hall-Sensor** Joystick" · „Ausgestattet mit **driftfreien Hall-Effekt**" | **belegt** |
| EasySMX M15 | `B0D97VQGFT` | Titel: „mit **Hall Effekt** Trigger&Joystick" · „**HALL EFFEKT JOYSTICK & TRIGGER**" | **belegt** |
| GameSir X2s | `B0D5GTM2PL` | Titel: „Gen 2 - **Hall-Effekt**" · „Verbessern Sie Ihr Gameplay mit **Hall-Effekt**" | **belegt** |
| HELLCOOL | `B0F4JPSWDT` | „Präzise **Joysticks mit Hall-Effekt**" | **belegt** |
| Mars Gaming MGPXPRO | `B0G8JXCNB3` | Titel: „**Hall Effect**" · „verfügt über **Hall Effect** TRIGGER" | **belegt** |
| ASUS ROG Tessen | `B0BRYX6RQR` | **kein Hall, kein TMR** — nur „mechanische Schalter", „Konsolen-Joystick" | **nicht belegt** |

Die sechs belegten Specs stehen jetzt im Datenkern. Der ROG Tessen bleibt ohne; sein
eigener Claim sagt ausdrücklich „Ohne Hall-Sticks" (meine erste Zählung hatte die
Verneinung mitgezählt). **Damit führen elf von 28 Controllern Hall-Effect**, und das
S1-Gate hat die Folge sofort gemeldet. Der günstigste Hall-Controller bleibt der
8BitDo Ultimate 2C mit 28 €.

## Preisregel

Auf ganze Euro gerundet, der vorhandene Präfix (`ca.` / `ab`) bleibt stehen. Die sechs
nicht kaufbaren Produkte behalten ihren letzten belegten Preis; die Wahrheit steht im
Feld `stock`, nicht im Preis. Einen Preis zu löschen wäre keine Verbesserung: Die Karte
zeigt dann „—" und sagt dem Leser nichts darüber, in welcher Liga das Produkt spielt.

## Zwei Dinge, die erst beim Nachziehen aufgefallen sind

**Die „4 Rücktasten" des Kishi V3 standen 11 Mal auf der Site.** Beim Spec-Chip-Pass am
Morgen des 06.10. war belegt: Amazon nennt **2 Rücktasten (M1/M2) plus 2
Klauengriff-Bumper**, zusammen „4 frei belegbare Tasten". Korrigiert wurden damals nur
die Chips in products.json, nicht die Prosa. Jetzt steht überall „vier frei belegbare
Zusatztasten" bzw. „zwei Rücktasten plus zwei Bumper", und in der Vergleichstabelle
„2 Rücktasten + 2 Bumper" statt „4 Rücktasten".

**Die Black-Friday-Schwellen waren sechsfach gekippt.** Die Seite nennt ihre eigene Regel
(„stark, wenn er rund 20 Prozent unter dem Regulärpreis liegt") und leitet daraus pro
Produkt eine Schwelle ab. Der Regulärpreis in Spalte 2 wurde vom Preis-Sync nachgezogen,
die berechnete Spalte 3 nicht: Beim G8 Galileo stand „68 € regulär, starker Deal unter
65 €" — das sind 4 Prozent, nicht 20. Alle sechs sind neu gerechnet, und ein neues Gate
rechnet sie ab jetzt nach (12 Fälle gemessen, 0 falsch).
