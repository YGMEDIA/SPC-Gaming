# 2026-07-19 · dev · Key-Visuals für alle Blog-Artikel

> Kategorie: dev/design · Auftrag Yasin: jeder Artikel ein passendes, emotionales Bild statt Icons; kein Text im Bild; Konzept-Look

## Was
8 SVG-Illustrationen (1600x900, je ~8 KB) im Corporate-Design erstellt (`assets/img/blog/`): was-ist-controller (Teleskop-Controller ikonisch), iphone-usb-c (Port-Glow + Stecker), handy-verbinden (Pairing-Wellen), verbindet-nicht (unterbrochene Wellen + Amber-Bruch), finger-sleeves (Gewebe-Fingerkuppe + Touch-Ripple), handy-kuehler (Lüfter-Disk + Kälte-Bögen), huellen (Klemmbacken + Amber-Spalt), gaming-setup-flat (Zubehör-Konstellation). Einheitliche Sprache: Navy-Verlauf, Punktraster, Glow-Radialgradienten, helle Gerätekörper, Blau/Cyan-Akzente, Amber NUR für Problem/Spalt. Eingebaut als article-hero-img in die 8 Artikel ohne Bild + als Thumbs im Blog-Index (Emoji-Platzhalter ersetzt, alt = Artikeltitel wie bestehende Karten). Nebenfix: 2x "30 Min. Lesezeit" → 5 Min.

## Wie
SVGs per Script generiert (gemeinsame defs, Punktraster-Funktion), Browser-Sichtprüfung aller 8 Kompositionen über lokale Prüfseite (danach gelöscht). qlmanage-PNG-Rendering verworfen: rendert ins Quadrat mit Zoom-Crop (Motive abgeschnitten), cairosvg/rsvg nicht installiert → SVG direkt im <img> (crisp, winzig, überall unterstützt); og:image/Schema behalten JPG (SVG für Social-Cards/Google-Images ungeeignet).

## Verify
verify.py GRÜN (98 Seiten, 218 Schemas) · Browser: alle 8 SVGs naturalWidth 1600, Kompositionen gesichtet · Blog-Index rendert Foto- und SVG-Thumbs kohärent · Alt-Audit-Regeln eingehalten (beschreibend, "Illustration:"-Präfix, kein Dateiname).

## Gelernt
1. qlmanage taugt nicht als SVG-Rasterizer für Nicht-Quadrate (Zoom-Crop). Wenn PNG-Ableitungen nötig werden (Social Cards): cairosvg installieren oder Browser-Screenshot-Pipeline bauen.
2. SVG-Key-Visuals sind der richtige Standard für Ratgeber-Artikel ohne Foto: eigenes Bildrecht (§C3), Corporate-Farben exakt, 8 KB statt 2 MB. Echte Fotos bleiben erste Wahl, wo vorhanden (Yasin-Liste Punkt 7).

---

## Nachtrag (19.07. vormittags): SVGs durch fotoreale KI-Bilder ersetzt

**Was:** Yasin generierte mit den 8 Prompts aus `03-research/bild-prompts-blog.md` fotoreale Bilder (perfekt slug-benannt in Downloads). Claude Code: PNG (1,4-2,2 MB) → JPG 1600x900 bei Qualität 82 (130-270 KB), Hero-Tausch in den 8 Artikeln, Blog-Index-Thumbs, og:image + twitter:image + Article-Schema-image jeweils auf das eigene Bild (vorher og-default), neue Foto-Alt-Texte (beschreibend statt "Illustration:"), SVGs gelöscht (Git-Historie behält sie).

**Anmerkung an Yasin übergeben:** Bild "verbindet-nicht" enthält ein Warndreieck-Piktogramm, Bild "huellen" ein kleines "X" mit Maßpfeil — streng genommen Symbole im Bild. Eingebaut wie geliefert; bei Bedarf regenerieren (Prompt-Zusatz "no symbols, no icons, no arrows").

**Verify:** verify.py GRÜN · 0 verbleibende SVG-Referenzen · og/Schema-URLs absolut · Live-Check nach Deploy.

**Gelernt:** Der Prompt→Yasin→Integration-Workflow funktioniert als Standard für alle künftigen Bild-Bedarfe (Look-Suffix hält die Konsistenz). Publisher-Logo im Article-Schema heißt "url", Artikel-Bild "image" — Regex-Swap ist dadurch kollisionsfrei.

**Nachtrag 19.07. abends — die 4 restlichen Key-Visuals (Content-Kalender-Artikel):** Yasin hat die 4 Prompts aus STATUS Punkt 5 generiert (gleicher Chat wie die ersten 8, slug-benannt in Downloads geliefert, 1672x941). Einbau nach bewährtem Ablauf: sips auf exakt 1600x900 JPG (q80, 120-253 KB), Hero + Blog-Index-Thumb + og:image/twitter:image/Article-Schema-image je Artikel aufs eigene Foto (publisher.logo bewusst unangetastet), beschreibende Foto-Alts nach Sichtung (u. a. Hall-Magnet vs. TMR-Schichtstapel korrekt benannt), 4 SVG-Platzhalter gelöscht, Sitemap 5 lastmods. Assertions-Pass, verify GRÜN, deployed (783005a), IndexNow 200. **Damit haben alle 17 Blog-Artikel fotoreale Key-Visuals; der Prompt-zu-Bild-Workflow ist Routine** (Prompt in STATUS → Yasin generiert slug-benannt → Einbau autonom).
