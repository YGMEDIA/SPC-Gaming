# 2026-07-18 · dev · Wachstums-Recherche + Emotions-Redesign Startseite

> Kategorie: dev/content · Auftrag Yasin: "qualitativer, SEO-technisch, visuell, mehr Emotion, Apple-artig"

## Was
**Recherche:** Web-Recherche zu drei Feldern, Destillat in `03-research/2026-07-18-wachstums-recherche.md`: (1) AI Overviews fressen Info-CTR, Klicker konvertieren dafür deutlich besser → BOFU-Content + zitierfähige Direktantworten mit Zahlen. (2) E-E-A-T 2026: Erste-Hand-Erfahrung (eigene Fotos, echte Autoren, Testprozess) ist das stärkste Signal und erhöht Zitierwahrscheinlichkeit ~2,3x. (3) Emotionales Design: Storytelling-Bänder, authentische Fotos, Statement-Typografie, eine CTA pro Sektion.

**Umsetzung Startseite, 3 neue Emotions-Bänder (rein statisch, Seiten-<style>, §A7-Farbwelt):**
- Band 1 nach den Bestsellern: Navy→Blau-Gradient, Statement "Echte Konsolen-Spiele. Direkt auf deinem Handy." (Cloud-Gaming-Thema), G8-Produktbild freigestellt auf weißer Karte (mix-blend-mode multiply, Apple-Look), CTA Finder + Textlink Cloud-Artikel.
- Band 2 nach den Testfotos: helles Grau, reine Statement-Typografie "Gute Sticks spürst du sofort. Schlechte leider auch." (Ehrlichkeits-Burggraben §A6), Link /redaktion/.
- Band 3 vor dem Vergleichs-Block: Weiß→Hellblau-Gradient, eigenes G8-Testfoto (bislang ungenutzt auf der Startseite), "Zocken, wo du gerade bist.", CTA Bestenliste.

## Wie
Einbau per Python-Patch mit Asserts an den Sektions-Kommentaren. Browser-Verifikation lokal (http.server + Browser-Pane): Bänder vorhanden, Gradienten aktiv, Grid-Spalten korrekt, CTAs verlinkt; Bild-Dimensionen für CLS gesetzt (sips-gemessen). Screenshot-Pipeline war flaky, deshalb maschineller Computed-Style-Check statt Sichtprüfung.

## Warum so
- Themen-Differenzierung: Die Startseite HATTE bereits eine Emotions-Sektion ("Touch-Steuerung kostet dich Spiele") — erster Band-Entwurf war thematisch doppelt (aufgefallen im Browser-Check, nicht im Code-Diff). Neue Themen-Verteilung: Problem/Lösung (bestehend) · Cloud-Aspiration (Band 1) · Ehrlichkeit (Band 2) · Freiheit/Erfahrung (Band 3).
- Amazon-CDN-Bild auf weißer Karte statt PNG-Freisteller: Wir haben keine transparenten PNGs; multiply auf Weiß erzeugt denselben Effekt mit §C3-konformen Bildern.
- Eigenes Testfoto in Band 3 statt Stock: zahlt direkt auf das E-E-A-T-Rechercheergebnis ein.

## Verify
verify.py GRÜN (98 Seiten, 218 Schemas). Browser: 3 Bänder, Gradienten, Links (/controller-finder/, /blog/cloud-gaming-smartphone/, /redaktion/, /controller/beste/) korrekt. Live-Check nach Deploy: Startseite 200 + .emo-navy im HTML.

## Gelernt
1. **Vor Design-Ergänzungen die GANZE Seite lesen:** Die bestehende Emotions-Sektion lag außerhalb meines gelesenen Ausschnitts, der Duplikat-Fund kam erst im Browser. Für Layout-Arbeit gilt: einmal komplett rendern und ansehen, bevor Neues dazukommt.
2. Statement-Bänder-Muster ist wiederverwendbar (S2 der Recherche: je 1 Band für Hubs/Bestenliste) — CSS-Klassen emo-navy/emo-quote/emo-photo sind bewusst generisch benannt.
