# SPEC · Q4-Saat: Geschenke-Guide + Black-Friday-Struktur

> Status: **FREIGEGEBEN 07.08.2026 (Yasin, Chat) · UMGESETZT 07.08.2026** (Lauf-3-Entscheidung: Q4 vorgezogen)
> Ziel: Bis Anfang November ranken. Reifezeit 2-3 Monate → Bau sofort nach Freigabe.

## 1 · Warum jetzt
Black Friday (27.11.) + Weihnachten sind der Umsatz-Peak im Affiliate-Jahr. Content braucht bei unserer jungen Domain 2-3 Monate zum Ranken. Der 25.07.-Einbruch betrifft den Bestand, nicht diese Chance — und der Meta-Freeze gilt nur für Bestands-Metas, neue Seiten sind erlaubt.

**Ehrlicher Keyword-Befund:** Der Keyword-Master (937 Keywords) enthält KEINE Saison-Keywords (geschenk/black friday/weihnachten — nie erhoben). Die Keyword-Wahl unten ist daher aus Produktlogik + bekannten Suchmustern abgeleitet, nicht volumen-belegt. Validierung: Saison-Queries erscheinen ab Oktober in der GSC → gsc-loop schärft Titles/Descriptions dann nach (Ausnahme vom Freeze, weil neue Seiten).

## 2 · Was gebaut wird (3 Seiten, alle Muster vorhanden)

### 2a · `/geschenke/` — transaktionaler Geschenke-Hub (Muster: P-6/Hub-Statik)
"Geschenke für Mobile-Gamer 2026" — kuratiert aus unseren **42 belegten Produkten** nach Geschenk-Preisklassen (Bestand deckt alle ab):
- **Unter 20 € (Wichtel-Klasse):** 9 Produkte (Sleeves ab 7 €, Trigger, Mini-Gamepad, Magnet-Kühler) — die Wichtelgeschenk-Nische gehört hierhin als eigene Sektion, keine eigene Seite (zu dünn)
- **20-50 € (sicheres Geschenk):** 18 Produkte (8BitDo 2C 20 €, X5 Lite 45 €, Kühler …)
- **50-100 € (Hauptgeschenk):** 12 Produkte (G8 Galileo 80 €, Scuf Nomad 73 €, G8 Plus 90 € …)
- **Ab 100 € (Premium):** 3 Produkte (Kishi Ultra 119, V3 Pro 149, Backbone Pro)
Je Klasse 3-4 kuratierte Empfehlungen mit ehrlicher Begründung (§A6: auch "für wen NICHT"), statische Karten (sync-Muster), ItemList + FAQPage, Empfänger-Logik als Text ("für Sohn/Freundin/Kollegen" = natürliche Longtail-Abdeckung ohne eigene Thin-Pages).
Ziel-Keywords: geschenke für gamer handy · geschenk mobile gamer · wichtelgeschenk gamer (Ableitung, s. o.)

### 2b · `/blog/geschenke-fuer-mobile-gamer/` — redaktioneller Ratgeber (Muster: P-5, Frage/Hub-Paar wie Budget + Tablet)
750+ Wörter: Wie schenkt man richtig (Plattform des Beschenkten klären iOS/Android!, Teleskop vs. Gamepad, Fehlkauf-Klassiker Lightning vs. USB-C), 3 Preisklassen-Empfehlungen mit Begründung, 4 FAQs. Verlinkt Hub als "Antwort-Liste" (bewährtes Paar-Muster aus Lauf 6/7).

### 2c · `/black-friday/` — Saison-Landingpage (NEU als Muster, ehrlichkeits-kritisch)
"Handy-Controller Black Friday 2026: Guide + Live-Deals ab 27.11."
**Vor dem Event (August-November) ehrlich als Vorbereitung:** Welche Modelle sich bei welchem Rabatt lohnen (belegte Regulärpreise aus products.json als Referenz: "G8 Galileo unter 65 € = zuschlagen"), worauf achten (Fake-Rabatte, alte Generationen wie Kishi V2/X2 als BF-Köder), Preisklassen-Matrix. **KEINE erfundenen Deals, KEINE "war mal"-Preishistorien (§A5)** — wir haben keine Preisverlaufs-Daten und behaupten keine.
**Am Event:** Yasin liefert BF-Wochenende Amazon-Screenshots echter Preise → ich pflege eine "Aktuelle Deals"-Sektion (dann greift der bewährte preis-loop-Sync). Diese Arbeitsteilung steht sichtbar auf der Seite ("Deals werden am 27.11. mit belegten Preisen gepflegt").
Ziel-Keywords: handy controller black friday · gamesir black friday · backbone black friday (Nische, DE kaum besetzt)

## 3 · Was bewusst NICHT gebaut wird
Kein Countdown-Widget (JS-only, §A2) · keine eigene Weihnachts-Seite (BF-Seite + Geschenke-Hub decken die Intention; Doppelung wäre Thin-Content) · keine Empfänger-Einzelseiten ("geschenk für freund" etc. = Thin-Page-Risiko) · keine Preis-Historien-Behauptungen · Longtail-Batches bleiben geparkt.

## 4 · Technik & Gesetze
Statik zuerst (§A2), Karten über sync_new_products-Muster bzw. Hand nach P-6 · Schemas: ItemList + FAQPage + BreadcrumbList, KEIN Product-Schema ohne offers (§A4-Lehre vom 20.07.) · alle Preise/Ratings aus products.json (§A1, Stand Rating-Welle 21.07.) · Sitemap +3 URLs · Blog-Index + interne Verlinkung (Hubs → Geschenke-Hub ab Oktober prominent, vorher dezent im Footer/Blog) · Key-Visuals: 2 Prompts an Yasin nach bewährtem Muster (Geschenke-Motiv, BF-Motiv), SVG-Platzhalter bis dahin.

## 5 · Verify & Erfolgskontrolle
verify.py grün (Schemas, Links, Sitemap, §A6-Check der Kuratierung) · Browser-Sichtung · Rich-Results-Test der 3 Seiten nach Deploy (autonom) · gsc-loop ab Oktober: "geschenk"/"black friday"-Queries beobachten, Titles nachschärfen · Erfolgskriterium: erste Saison-Impressionen bis Mitte Oktober, Klicks in BF-Woche.

## 6 · Freigabe
[x] Yasin: freigegeben am 07.08.2026 (Chat "ok") / Änderungen: keine · Umsetzung: gleiche Session, alle 3 Seiten deployed
Aufwand nach Freigabe: 1 Session (alle 3 Seiten + Verlinkung + Doku). Yasins Beiträge: 2 Bild-Prompts generieren (jederzeit) · BF-Wochenende Screenshots (27.11.).
