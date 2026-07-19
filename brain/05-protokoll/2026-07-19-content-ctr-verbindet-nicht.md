# 2026-07-19 · content · CTR-Rettung controller-verbindet-nicht

**Was:** Title + Meta-/OG-/Twitter-Description + Article-Schema-description von `/blog/controller-verbindet-nicht/` neu geschrieben (content-loop Punkt 2, aus gsc-loop Lauf 1). Prosa, H1, Lead und FAQs unangetastet. Sitemap-lastmod auf 2026-07-19.

**Vorher (Baseline GSC 11.-17.07.):** 0 Klicks / 47 Impressionen — zweithöchste Impressionszahl der Site, aber niemand klickt.
- Title alt: "Controller verbindet nicht mit Handy? 5 Lösungen die helfen" (generisch, "die helfen" ist Füllmaterial)
- Description alt: "Dein Controller lässt sich nicht… Wir gehen die 5 häufigsten Ursachen durch — von Bluetooth-Konflikt bis defektem Kabel." (beschreibt Vorgehen statt Nutzen, enthielt Em-Dash)

**Nachher:**
- Title: "Controller verbindet nicht mit Handy? Meist in 2 Min. gelöst" (60 Z. Kern + Brand-Suffix)
- Description: "Handy findet den Controller nicht? Meist ist es kein Defekt, sondern eine von 5 typischen Ursachen. Unsere Checkliste löst jede davon Schritt für Schritt." (154 Z.)

**Warum so:** Suchintention ist akuter Frust (neues Gerät funktioniert nicht). Die zwei stärksten Klick-Trigger dafür: Zeitversprechen im Title ("in 2 Min. gelöst") und Angst-Nehmer in der Description ("kein Defekt"). Beide Claims stehen wörtlich gedeckt in der Prosa ("In den allermeisten Fällen steckt kein Defekt dahinter", "meist ist das Problem in ein paar Minuten gelöst"); "meist" hält beide ehrlich (§A6-Geist). Query-Match "Controller verbindet nicht mit Handy" bleibt vorn für SERP-Fettdruck. Keine Em-Dashes in der neuen Copy.

**Verify:** Eigen-Check (Title-Kern 60 ≤ 62, 4 Meta-Stellen konsistent, Lead-Prosa byte-identisch erhalten, kein Em-Dash) + `scripts/verify.py` GRÜN (98 Seiten, 218 Schemas). Article-dateModified bewusst NICHT angehoben (Artikelinhalt unverändert; nur Sitemap-lastmod signalisiert den Recrawl).

**Erfolgskontrolle:** gsc-loop Lauf 2, Checklisten-Punkt 6 (Baseline 0/47). Erwartung: CTR > 0 im Fenster nach Recrawl; Titel-Rewrite durch Google möglich — dann im Lauf 2 SERP-Darstellung prüfen.

**Gelernt:** GSC-Snippet-Arbeit ist vom Prosa-Standard trennbar: 4 Meta-Stellen (title, og, twitter, Schema-description) müssen synchron laufen, die sichtbare Lead-Zeile darf bewusst abweichen — sie arbeitet auf der Seite, nicht im SERP.
