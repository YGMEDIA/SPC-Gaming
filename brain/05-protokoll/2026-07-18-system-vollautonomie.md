# 2026-07-18 · system · Vollautonomie + Namenskorrektur + Leak-Fix

> Kategorie: system · Entscheidung Yasin, 18.07.2026 abends

## Was

**1 · Neues Arbeitsmodell (Vollautonomie).** Claude Code committet und pusht künftig selbstständig; Push auf main löst den Live-Deploy via GitHub Actions aus. Das Deploy-Menschen-Gate entfällt, ersetzt durch das harte Maschinen-Gate: `python3 scripts/verify.py` MUSS grün sein vor jedem Commit, ein roter Stand wird niemals gepusht. Verbleibende Menschen-Gates: Geld-/ASIN-Änderungen ohne Screenshot-Beleg · `.github/workflows/` · `.claude/settings.json`. Yasin behält Live-Stichproben und Rollback-Recht via `git revert`. Umgesetzt in: CLAUDE.md (Root + brain, dabei konvergiert), Constitution Teil D (+ Änderungslog v1.1), SPC-FRAMEWORK 7.2/7.3/7.4/Governance 3+5 (+ Änderungslog v1.1, Fußzeile v1.1), deploy-loop.md (kompletter neuer Ablauf), `.claude/settings.json` (neu angelegt: defaultMode acceptEdits; allow git add/commit/push + rm; deny rm -rf + sudo).

**2 · Namenskorrektur.** Der Projektinhaber heißt Yasin; der bisher im gesamten Brain verwendete Rufname war ein Transkriptionsfehler. Projektweit ersetzt (CLAUDE.md + 17 brain-Dateien, inkl. "Braucht Yasin"-Listen, Rollen-Tabellen, Gates, Loop-Zuständigkeiten). Die Änderungslogs dokumentieren die Korrektur bewusst ohne das alte Wort, damit der Verify-Grep (null Treffer) dauerhaft hält. Site-HTML war nicht betroffen (geprüft).

**3 · Ungeplant: kritischer Live-Leak gefunden und geschlossen.** Beim Vorab-Check des ersten autonomen Push entdeckt: GitHub Pages stand auf Legacy-Modus (deployt den KOMPLETTEN main-Branch) und der im Brain dokumentierte Actions-Workflow existierte nie im Repo (.github/ ohne jede Git-Historie — gleiche Fehlerklasse wie .nojekyll: per Web-Upload nie angekommen). Folge: brain/ (Strategie, GSC-Daten, interne Doku), Root-STATUS.md und SPC-Gaming-Visuals/ (Amazon-Screenshot-PDFs) waren öffentlich abrufbar (/brain/STATUS.md → HTTP 200, live verifiziert). Fix mit Yasins Freigabe (Menschen-Gate .github/workflows eingehalten): `deploy.yml` neu erstellt (Option A: rsync-Artefakt OHNE brain/, scripts/, .github/, .claude/, CLAUDE.md, README.md, STATUS.md, SPC-Gaming-Visuals/, .DS_Store) · Pages per `gh api` von "legacy" auf "workflow" umgestellt · Root-STATUS.md-Zombie (Stand 11.07.) gelöscht · Push → Actions-Deploy → Live-Check.

## Wie
Diagnose vor Fix: Pages-Konfiguration per `gh api repos/{owner}/{repo}/pages` (build_type "legacy" bewiesen), Workflow-Nichtexistenz per `git log --all -- .github/` (null Commits), Leak per Live-HTTP-Check (200 auf /brain/STATUS.md). Menschen-Gates respektiert: Workflow-Erstellung + Pages-Umstellung erst nach expliziter Freigabe (AskUserQuestion). Rename per sed über die Treffer-Dateien, danach Grep-Nullprobe.

## Warum so
- verify.py als Gate statt Mensch: maschinell prüfbar, kein Flaschenhals, und die bisherigen Deploy-Fehler (Zombies, fehlende Dotfiles) entstanden ausgerechnet im MANUELLEN Weg (Web-Upload). Autonomie über git push ist hier die sicherere Variante.
- Option-A-Workflow statt .gitignore-Ansätzen: Das Repo behält Brain + Screenshots versioniert, nur das Deploy-Artefakt ist gefiltert. Genau dafür war Option A immer gedacht; sie war nur nie real.
- Änderungslogs ohne das alte Falsch-Wort: Der Abschluss-Verify (grep null Treffer) soll dauerhaft als Regressionstest taugen.

## Verify
`python3 scripts/verify.py` GRÜN · `grep -ri` auf den alten Namen in CLAUDE.md + brain/ = 0 Treffer · settings.json JSON-valide · Pages build_type nach Umstellung = "workflow" · Actions-Run des ersten autonomen Push grün · Live: /brain/STATUS.md → 404, /ratgeber/ → 404, Startseite + Finder → 200.

## Gelernt
1. **Doku kann lügen, das Repo nie:** "Actions-Deploy gebaut" stand im Brain, aber .github/ hatte null Git-Historie. Vor jedem Deploy-relevanten Schritt den Ist-Zustand maschinell prüfen (gh api, git log), nicht der Doku glauben.
2. **Die Web-Upload-Fehlerklasse ist größer als gedacht:** Sie frisst Dotfiles UND Dot-Ordner (.nojekyll, .github/) und belebt Gelöschtes wieder (ratgeber/, Root-STATUS.md). Mit git-only-Deploys ist die Klasse tot.
3. **Erst Konfiguration, dann Push:** Die Pages-Source-Umstellung MUSS vor dem ersten Push passieren, sonst veröffentlicht der Legacy-Build das, was der Workflow gerade ausschließen soll.

---

## Nachtrag (gleiche Session, spät)

**Was:** Yasins Anweisung nach dem ersten Permission-Dialog-Screenshot: keine Genehmigungsanfragen mehr. settings.json auf `defaultMode: bypassPermissions` umgestellt + breite Allow-Regeln (Bash/Read/Edit/Write/WebFetch/WebSearch) als Fallback; deny bleibt `rm -rf` + `sudo`; `skipDangerousModePermissionPrompt: true` gegen den einmaligen Warndialog. Zusätzlich neue **Kontext-Schnitt-Regel** in CLAUDE.md (beide) + Constitution Teil D (v1.2): Kontextfenster selbst überwachen, bei absehbarer Erschöpfung das laufende Teilstück fertigstellen (verify grün, Commit+Push, Doku aktuell), Folgeschritt in STATUS präzisieren, sauberer Schnitt — nie halbfertig, nie uncommittet über Session-Grenzen.

**Verify:** settings.json JSON-valide · verify.py grün · Commit + Push autonom.

**Gelernt:** Die Permission-Dialoge dieser Session kamen daher, dass settings.json erst beim Session-Start geladen wird — die neuen Regeln greifen ab der NÄCHSTEN Session vollständig.
