# Amazon-Ist-Stand aller 42 Produkte, gezogen 2026-07-21 via Chrome-Extension
# GROUND TRUTH — Rohdaten, nie überschreiben. Beleg für die Rating-Welle.
# Format: ASIN | slug | Preis | Rating | Bewertungen

B0BR7LGZ8W | shanwan-bt-white         | 39,99 € | 4,1 | 981
B0DVLTX8SX | trust-gxt-rgb            | 29,99 € | 4,2 | 322
B0C9J45XCV | shanwan-teleskop-black   | 33,99 € | 4,3 | 781
B0D97VQGFT | easysmx-m15              | 44,99 € | 4,2 | 719
B0FJ1GGMMZ | abxylute-s8              | 39,09 € | 4,4 | 255
B0D72WYT8Z | 8bitdo-ultimate-2c       | 19,99 € | 4,5 | 854
B0DXPMVCWC | gamesir-x5-lite          | 44,99 € | 4,2 | 1655
B0CTJ45GLG | backbone-one-2           | 63,00 € | 4,1 | 51
B0CXHVCTW9 | gamesir-g8-galileo       | 79,99 € | 4,2 | 688
B0F2JFWSJ5 | razer-kishi-v3           | 93,49 € | 4,4 | 126
B0FWBYDF8Y | abxylute-m4-snapon       | 49,99 € | 4,4 | 382
B0DK36N98Q | 8bitdo-ultimate-mobile   | 44,99 € | 4,4 | 517
B0FYQ1SHHS | gamesir-g8-plus          | 89,99 € | 4,1 | 457
B0F5WRZ3LJ | viture-8bitdo            | 67,15 € | 4,1 | 241
B0BRYX6RQR | asus-rog-tessen          | 73,90 € | 4,0 | 125
B0BHH8DT37 | backbone-one-ps          | 58,99 € | 4,2 | 312   <-- KORRIGIERTE ASIN, siehe Nachtrag
B0DQM23MLZ | backbone-pro             | 189,99 € | 4,4 | 459
B0D1KFNLLM | shanwan-metallic         | 33,99 € | 4,3 | 781
B0D5GTM2PL | gamesir-x2s              | 45,99 € | 3,8 | 100
B0DCVZWNMY | gamesir-x3-pro           | 89,99 € | 3,9 | 283
B0F4JPSWDT | hellcool-controller      | 49,99 € | 4,1 | 100
B0F3P8L1B8 | marsgaming-mgp-bt2       | 29,90 € | 4,1 | 27
B0D9HGJ1ZB | marsgaming-mgpx          | 26,80 € | 4,0 | 382
B0G8JXCNB3 | marsgaming-mgpxpro       | 35,50 € | 3,6 | 9
B0F2JGV9NK | razer-kishi-v3-pro       | 149,00 € | 4,4 | 125
B0BDXSWZMF | turtle-beach-atom        | 86,83 € | 4,0 | 1896
B0CXY4MWKR | razer-kishi-ultra        | 119,00 € | 4,0 | 110
B0D7D83HBN | scuf-nomad               | 72,94 € | 4,0 | 157
B0DTTT23P7 | wllhyf-sleeves           | 7,49 € | 4,4 | 64
B0C9D8BB9B | ouligay-sleeves          | 6,89 € | 4,2 | 261
B0BN98QRK2 | risoka-finger-sleeves    | 13,99 € | 4,4 | 2835
B0D9Y9116S | rxkfigx-sleeves          | 6,99 € | 3,5 | 36
B0F1FW7BYG | magnet-peltier-cooler    | 17,99 € | 3,4 | 128
B0GWL9QDRG | black-shark-funcooler    | 39,99 € | 4,2 | 91
B09LVF2RYL | razer-phone-cooler       | 39,99 € | 3,2 | 72
B0DPQQJYL4 | risoka-trigger           | 19,99 € | 4,0 | 79
B0CNPVCJCL | ozkak-6finger            | 16,99 € | 3,8 | 111
B086JPTLDD | ozkak-trigger-set        | 26,99 € | 4,2 | 456
B07ZQ9G7ZX | ozkak-mini-portable      |  9,99 € | 3,8 | 325
B0BGR4DGSQ | ozkak-trigger-l1r1       | 17,99 € | 3,9 | 673
B0F3JF5P5J | toaluea-trigger-joystick |  9,49 € | 4,0 | 71
B096S5WV62 | ozkak-trigger-gamepad    | 32,99 € | 3,6 | 277

## Sonderfall Backbone One PS (B0CT17GPNT)
Das Listing zeigt KEINEN Preis und trägt den Titel "BACKBONE One Mobiler Gaming-Controller
für das iPhone (Lightning) - 1st Gen", Verfügbarkeit "Nur noch 1 auf Lager".
Die 4,3 / 16.951 sind die Bewertungen der gesamten Varianten-Familie, nicht dieser Variante.
=> Produkt-Status vor der Datenübernahme klären (Lightning ist für iPhone 15+ obsolet).

## Methode
Pro ASIN: /dp/ASIN in Yasins Chrome, Auslesung von #corePrice_feature_div (a-offscreen),
#acrPopover[title], #acrCustomerReviewText. ASIN-Schlüssel aus der URL, nicht aus #ASIN
(bei Varianten-Listings meldet #ASIN teils die Parent-ASIN).

## Nachtrag 21.07. abends — Backbone One PS Edition: richtige ASIN von Yasin
Yasin lieferte das korrekte Listing: **B0BHH8DT37** (bisher geführt: B0CT17GPNT, ein Familien-Listing ohne Preis).
Ausgelesen: Titel "BACKBONE - One Mobile Gaming Controller for iPhone - Playstation Edition",
Modellnummer BB-02-W-S, **58,99 €**, **4,2 von 5 bei 312 Bewertungen** (produktgenau, nicht Familie),
Verfügbarkeit "Nur noch 1 auf Lager", 1 hiRes-Bild, keine Anschluss-Angabe auf der Seite.
Unsere Review-Seite führt das Modell als "Lightning, iPhone 14 & älter" — konsistent mit BB-02, kein Widerspruch.
