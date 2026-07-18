# 2026-07-18 · system · Brain-Aufbau + Zombie-Bereinigung

**Was:** SPC Brain v1.0 aufgesetzt (Framework, Constitution, Patterns, 4 Loops + LOOP-STATE, Spec #1, Keyword-Rohdaten als Text, Protokoll-System) · verify.py als maschinelles Gate · CLAUDE.md · GitHub-Actions-Deploy (brain/ bleibt privat) · 3 Zombie-Pfade entfernt (/ratgeber/, marken/ipega/, marken/mocute/) · .nojekyll wiederhergestellt · .gitignore.

**Wie:** Muster aus USELY-Framework v1.5 + YOU-Brain übernommen (Loop-Regeln 7.5, Leseregeln 7.6, Governance) und auf Affiliate übersetzt. Repo-Inspektion fand die Zombies: /ratgeber/ manuell beim Stand-Check, ipega/mocute durch den Sitemap-Rückabgleich in verify.py beim allerersten Lauf. Ursache bewiesen: Upload-Deploys ohne Löschung — Gelöschtes blieb auf GitHub liegen. Actions-Workflow (rsync-Ausschlüsse + Abbruch-Sicherung falls brain/ im Artefakt) macht die Fehlerklasse unmöglich.

**Warum so:** Option A (ein Repo, Actions filtert) statt zweitem Brain-Repo — ein Sync-System, Generatoren können später im Deploy laufen. Keywords als Text statt xlsx im Brain — greppbar für Claude Code, Leseregel-konform.

**Verify:** scripts/verify.py grün (88 Seiten, 172 JSON-LD, 40 Produkte, 0 Fehler) · nach Deploy: /brain/ = 404 bestätigt (Felgen).

**Gelernt → Rückfluss:** §B2 um Deploy-Vollzugs-Pflicht ergänzt · P-7 (Verify-Suite) und P-8 (Screenshot-Ground-Truth) als Patterns kodifiziert · Deploy-Loop trägt die Pages-Source-Umstellung als Einmal-Schritt.
