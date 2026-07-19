# 2026-07-19 · dev · E-E-A-T-Autoren-Paket: Yannick Gerber (Pseudonym, Yasins Entscheidung)

**Was:** Yasins Entscheidung aus dem Chat ("bau weiter, Autoren-Namen: Pseudonym") umgesetzt — der Recherche-Hebel Nr. 1 aus der Wachstums-Recherche vom 18.07. (Erste-Hand-Erfahrung = stärkstes E-E-A-T-Signal). Sitewide einheitliche Autoren-Identität: **Yannick Gerber** (Pseudonym; Initialen YG = bewusster Anker an YG MEDIA).

**Gebaut:**
1. **/redaktion/**: neue Sektion "Wer hier testet" mit Autoren-Box (Monogramm-Avatar, Name, Rolle "Tester & Redakteur", Bio) + Person-Schema (`@id .../redaktion/#autor`, jobTitle, worksFor, knowsAbout — jeder Schema-Wert steht sichtbar im Text, §A4).
2. **17 Blog-Artikel**: Byline "smartphone-controller.com · …" → "Von [Yannick Gerber](/redaktion/) · …" + Article-Schema author von Organization auf Person (name + url) umgestellt. Script-Pass mit Assertions (je Datei genau 1 Byline, ≥1 author).
3. **13 Review-Seiten**: Hero-Byline "Getestet von Yannick Gerber · Redaktion smartphone-controller.com" nach dem Lead + Autoren-Box vor "Ähnliche Modelle" (Anker in allen 13 uniform, vorher bewiesen). KEINE Schema-Änderung an den Reviews: author gehört nicht ins Product-Schema, und ein Review-Schema mit Eigenbewertung bleibt wegen §A4-Risiko bewusst draußen.
4. **Avatar**: `assets/img/autor-yg.svg` — Monogramm "YG" in Corporate-Farben (navy #0b2540, Ring blue #0a6ed1). CSS `.author-box` zentral in style.css.

**Ehrlichkeits-Rahmen (wichtig):** Pseudonym ja, Täuschung nein. KEIN KI-generiertes fotoreales Gesicht (wäre ein Fake-Mensch), KEINE erfundenen Credentials/Jahreszahlen/Abschlüsse — die Bio beschreibt ausschließlich die real existierende Testpraxis der Site (Kriterien decken sich mit der Testmethodik-Sektion) und verweist auf YG MEDIA als presserechtlich Verantwortlichen (Impressum bleibt die rechtliche Wahrheit). Publizieren unter Pseudonym ist presserechtlich zulässig, solange das Impressum stimmt. Falls Yasin später ein Foto will (eigenes oder bewusst gewähltes), ist der Tausch ein Einzeiler (Avatar-Datei ersetzen).

**Verify:** Assertions aller Pässe grün (17+17, 13+13) · verify.py GRÜN (102 Seiten, 231 Schemas — +1 Person) · Browser-Sichtung /redaktion/ (Box + Avatar rendern) und G8-Review (Hero-Byline sichtbar, Box vor "Ähnliche Modelle", Avatar lädt nach lazy-Trigger, SVG HTTP 200) · Stichprobe Blog-Byline + Person-author · Sitemap-lastmod 31/31 · Commit 0d56e55, deployed, IndexNow 101 URLs HTTP 200.

**Namensänderung später:** Der Name steht an 3 Stellen-Klassen (Bylines, Boxen, Schemas) — ein deterministischer Suchen/Ersetzen-Pass, kein Architektur-Thema.

**Gelernt:** (1) Uniforme Anker VOR dem Bau beweisen (Zähl-Pass über alle Zieldateien) macht Hand-Seiten-Batches so sicher wie Generator-Läufe. (2) Die beiden Review-Generationen (9 alte ohne FAQ/Divider, 4 neue mit) teilen trotzdem die "Ähnliche Modelle"-Überschrift — bei heterogenen Beständen nach dem kleinsten gemeinsamen Anker suchen statt nach Struktur-Gleichheit.
