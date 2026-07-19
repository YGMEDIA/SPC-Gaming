# DEPLOY-LOOP (pro Release)

**Zweck:** Kein kaputter oder unvollständiger Stand geht live (§B2, Governance 5).
**Ablauf (Claude Code führt vollständig selbst aus — Vollautonomie seit 18.07.2026):**
1. `python3 scripts/verify.py` → MUSS grün sein (hartes Maschinen-Gate). Ein roter Stand wird niemals committet oder gepusht.
2. STATUS.md aktuell? Protokoll-Eintrag geschrieben? Befunde eingetragen?
3. Commit + Push durch Claude Code: eine aussagekräftige Commit-Message pro abgeschlossenem Arbeitspaket, dann `git push` auf main. Der Push löst den Live-Deploy automatisch aus (GitHub Actions, .github/workflows/deploy.yml): veröffentlicht ALLES AUSSER brain/, scripts/, CLAUDE.md, .github, README.md. Dadurch: Gelöschtes verschwindet wirklich (Ratgeber-Lehre!), Brain bleibt privat. NIE per GitHub-Web-Upload deployen (hat /ratgeber/ dreimal wiederbelebt und verwirft Dotfiles).
4. **Einmalig beim ersten Actions-Deploy:** GitHub → Settings → Pages → Source = "GitHub Actions" (statt "Deploy from branch"). Ohne diese Umstellung würde der Branch-Deploy brain/ VERÖFFENTLICHEN. (Handgriff Yasin, einmalig.)
5. Nach Push: Claude Code kann Actions-Status prüfen (gh run list); Stichprobe live wo möglich (Startseite, 1 neue Seite, smartphone-controller.com/brain/ → muss 404 sein) · bei neuen Seiten Sitemap in GSC neu einreichen (Yasin) · llms.txt erreichbar.
6. **IndexNow nach inhaltlichen Deploys:** `python3 scripts/indexnow_ping.py --all` (oder gezielt geänderte URLs) — meldet Bing & Co. die Änderungen sofort. Key-Datei liegt im Root, deployt automatisch mit.
**Yasins Rolle:** Gelegentliche Live-Stichproben nach eigenem Ermessen + jederzeitiges Rollback-Recht via `git revert <sha>` und Push.
**Fertig-Kriterium:** Actions-Run grün + /brain/ liefert 404 + Stichproben-Seite zeigt neuen Stand (Cmd+Shift+R).
**Läufe:** —
