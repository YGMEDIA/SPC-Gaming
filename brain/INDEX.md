# SPC BRAIN — INDEX

> Single Source of Truth für smartphone-controller.com. Lebt im Repo unter `brain/`, versioniert mit Git, öffnbar als Obsidian-Vault (Ordner direkt öffnen — nie iCloud-Sync parallel).
> Lesereihenfolge: dieser Index → `STATUS.md` → gezielt die relevante Datei → Links folgen. Nie alles auf einmal (Framework 7.5).
> Handoff läuft ab jetzt über dieses Brain + Claude Code im Repo — nicht mehr über ZIP-Uploads und Root-STATUS.

## Navigation
| Datei / Ordner | Inhalt | Status |
|---|---|---|
| `STATUS.md` | Lebendiges Session-Gedächtnis: Stand, Befunde, "braucht Yasin", Verlauf. Direkt nach dem Index lesen. | ✓ |
| `SPC-FRAMEWORK.md` | **Kanonische Referenz v1.0** — Leitprinzipien, Keyword-Strategie, Architektur, Datenmodell, Module, Roadmap A–H, Entwicklungssystem, Governance. Gewinnt bei Konflikten. | ✓ |
| `01-constitution/SPC-CONSTITUTION.md` | Gesetze §A Site · §B SEO/GEO · §C Recht · §D Betrieb, mit [bewiesen]-Markern + Befund-Tabelle. Gewinnt bei Baufragen. | ✓ v1.0 |
| `02-patterns/SPC-PATTERNS.md` | Bau-Muster P-1…P-8, aus echtem Projekt erkannt. | ✓ v1.0 |
| `03-research/` | `keyword-strategie.md` (Destillat) · `raw/` (Ground Truth: GSC-/Amazon-Daten, unantastbar). | ✓ |
| `04-loops/` | Selbstkontroll-Loops (Preis, Content, GSC, Deploy) + `LOOP-STATE.md`. Jeder Lauf liest LOOP-STATE zuerst. | ✓ v1.0 |
| `05-protokoll/` | Das Gedächtnis fürs Detail: datierte Einträge (dev/content/marketing/system) — WAS + WIE jeder Arbeit. Dazu `marketing-log.md` als lebende Aktivitäten-Tabelle. | ✓ |
| `06-specs/` | Größere Vorhaben nur nach freigegebenem Spec. | #1 zur Freigabe |

Außerhalb des Brains, gehört zum System: `/CLAUDE.md` (Einstieg für Claude Code, <200 Zeilen) · `/scripts/` (verify.py als Pflicht-Gate, Generatoren) · `/.github/workflows/deploy.yml` (veröffentlicht die Site OHNE brain/, scripts/, CLAUDE.md).

## Site-Stand
LIVE auf GitHub Pages (smartphone-controller.com, non-www kanonisch). 102 HTML-Seiten · 40 Produkte in products.json (alle mit Detailseite, 38 mit Galerie, 19 mit Produktvideo) · 13 Reviews · 18 Blog-Artikel · 10 Longtail-Datenblätter · Sitemap 101 URLs · GTM/GA4 consent-gated aktiv (end-to-end bewiesen 19.07.) · Bing + IndexNow live. GSC-Baseline (11.-17.07.): 5 Klicks / 315 Impressionen / Ø Position 16,8 — Details in STATUS.

## Arbeitsprinzip
Idee → Spec (gegen echtes Repo) → Freigabe (Yasin) → Claude Code baut nach Constitution + Patterns → `scripts/verify.py` grün + Review in frischem Kontext (Macher ≠ Prüfer) → Yasin deployt → Gelerntes zurück ins Brain. Rollen: Yasin entscheidet, Chat-Claude plant und prüft, Claude Code implementiert.

---
*SPC BRAIN · INDEX v1.0 · 2026-07-18*
