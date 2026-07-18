# DEPLOY-LOOP (pro Release)

**Zweck:** Kein kaputter oder unvollständiger Stand geht live (§B2, Governance 5).
**Ablauf (Claude Code bereitet vor, Felgen führt aus):**
1. `python3 scripts/verify.py` → muss grün sein (Gate).
2. STATUS.md aktuell? Befunde eingetragen?
3. Commit + Push durch Felgen. Deploy läuft über GitHub Actions (.github/workflows/deploy.yml): veröffentlicht ALLES AUSSER brain/, scripts/, CLAUDE.md, .github, README.md. Dadurch: Gelöschtes verschwindet wirklich (Ratgeber-Lehre!), Brain bleibt privat.
4. **Einmalig beim ersten Actions-Deploy:** GitHub → Settings → Pages → Source = "GitHub Actions" (statt "Deploy from branch"). Ohne diese Umstellung würde der Branch-Deploy brain/ VERÖFFENTLICHEN.
5. Nach Deploy (Felgen): Stichprobe live (Startseite, 1 neue Seite, smartphone-controller.com/brain/ → muss 404 sein) · bei neuen Seiten Sitemap in GSC neu einreichen · llms.txt erreichbar.
**Fertig-Kriterium:** Actions-Run grün + /brain/ liefert 404 + Stichproben-Seite zeigt neuen Stand (Cmd+Shift+R).
**Läufe:** —
