# Changelog

## [1.0.0] — 2026-05-13

First release of Arcana.

Arcana is the engine for **grimoires** — structured, AI-navigable knowledge bases the LLM keeps current. A grimoire combines deterministic hub-based routing, a layered storage model, mechanical validators, and slash-command skills. Arcana ships universally; each domain grimoire contributes its own content, sources, and skills.

### Knowledge structure

**Hub-based routing.** Every folder F has a hub at `F/<basename(F)>.md`. Hubs route to sub-hubs, to leaf documents, or both — depth is open-ended. The grimoire root hub is `<grimoire>/<grimoire>.md`. Each hop narrows the search; the agent stops at the leaf that answers the question. Folder-named hubs make Obsidian's graph view legible (every node has a meaningful, unique label).

**Page frontmatter.** Every authored markdown page in `docs/`, `invocations/`, `formulae/`, or `chapters/` carries YAML frontmatter:

```yaml
---
type: hub | concept | entity | source | playbook | reference | log-entry
title: "..."
aliases: [...]
tags: [...]
sources: [...]            # required when authority is external/hybrid
authority: external | grimoire | hybrid
last_verified: YYYY-MM-DD
---
```

The schema is documented canonically in `docs/page_schema.md` and enforced mechanically by `rites/validate_frontmatter.py`.

**Storage layers.** Every grimoire (Arcana included) is organized into:

| Layer | Directory | Owner | Purpose |
|---|---|---|---|
| Sources | `sources/` | LLM reads, never modifies | Immutable source artifacts: articles, transcripts, papers, screenshots. Citation-stable: pages with `authority: external` cite paths under here. |
| Inbox | `inbox/` | LLM and user both write | Optional transient drop zone for mixed content awaiting classification. Cleared by `/grm-domain-ingest`. Pages must NOT cite `inbox/` paths in `sources:` (validator enforces). |
| Wiki | `chapters/`, root hub | LLM authors and maintains | Synthesized knowledge with required frontmatter. |
| Schema | `grimoire.json` + injected agent block | User co-evolves | Tells the agent how to operate this grimoire. |

Plus the per-grimoire `log.md` — append-only activity log. Each entry begins `## [YYYY-MM-DD HH:MM] <op> | <title>` so recent activity is `grep`-scannable.

**Wikilinks for in-grimoire references.** Hubs use Obsidian-style `[[wikilinks]]` for in-grimoire pointers. `rites/validate_links.py` resolves them against filename stems and `aliases:` frontmatter. Cross-grimoire references stay as path placeholders (`GRIMOIRE_ARCANA/...`).

### Identity and library

- Each grimoire declares its identity in a `grimoire.json` manifest at the repository root: `name`, `namespace`, `description`. This is the single source of truth for skill namespacing.
- Two libraries coexist: a global `library.json` (shipped with Arcana, lists discoverable grimoires for the summoning rite) and a per-user `~/grimoires/library.json` (records where each installed grimoire lives on disk).
- Domain grimoires are pure content repositories — no engine code, no Arcana submodules, no copies of framework files.

### Operations (domain-facing skills)

| Skill | Purpose |
|---|---|
| `/grm-domain-create-grimoire` | Conversational scaffolding for a new grimoire (root hub, manifest, `sources/`, `inbox/`, `chapters/`, `log.md`, skills folder). |
| `/grm-domain-create-chapter` | Add a knowledge chapter with proper frontmatter and hub naming. |
| `/grm-domain-ingest` | Polymorphic. Single file → file under `sources/` and synthesize. Folder or `inbox/` (default) → classify each item into `sources/`, `chapters/`, or leave for review. |
| `/grm-domain-file-answer` | Promote a substantive chat answer into a properly-frontmattered wiki page. |
| `/grm-domain-lint` | Health-check: orphans, provenance, frontmatter, stale (`last_verified` >90d), ghost references, contradictions, missing cross-refs. |
| `/grm-domain-improve` | Comprehensive grimoire audit and improvement orchestrator. |
| `/grm-domain-analyze-semantics` | Judgment-based naming and organization audit. |
| `/grm-domain-validate-structure` | Structural compliance against Arcana formulae and conventions. |

### Validation suite

Mechanical rites, each independently invocable and orchestrated by `rites/validate.py`:

- `validate_structure` — Arcana directory layout and required hub files.
- `validate_domain_structure` — domain grimoire layout (root hub, `sources/`, `chapters/`, `log.md`, `grimoire.json`).
- `validate_naming` — snake_case for paths, kebab-case for skills.
- `validate_format` — invocation/formula schema; hubs are thin routers (<200 lines).
- `validate_frontmatter` — page schema compliance (type, required fields per type, aliases/tags shape, `last_verified` parses).
- `validate_links` — markdown links resolve; wikilinks resolve via filename or `aliases:` frontmatter.
- `validate_orphans` — every page is reachable from at least one other page.
- `validate_provenance` — pages with `authority: external` or `hybrid` cite real artifacts under `sources/`; never cite `inbox/`.
- `validate_security` — credential patterns and unsafe Python constructs.
- `validate_semantics` — deprecated terminology and hyphenated path examples.
- `validate_skill_refs` — every `/grm-*` reference in prose resolves to a real skill folder.
- `validate_boundaries` — magical/practical boundary compliance (system terminology in Arcana, practical terminology in domain content).

The full suite runs sequentially or in parallel; smart mode picks only validators relevant to the working tree's git changes.

### Skill system

- Skills are thin SKILL.md pointer files registered into agent skill directories. No logic embedded in the skill itself.
- Arcana ships `/grm-*` skills; each domain grimoire contributes `/<namespace>-*` skills.
- `rites/register_skills.py` (`/grm-skills-register`) discovers and installs skills from Arcana and every library entry to Claude Code (`~/.claude/skills/`) and Codex/ChatGPT (`~/.codex/skills/`).
- Source SKILL.md files use `{{NAMESPACE}}` and `{{ARCANA_PATH}}` placeholders resolved at registration time.
- `when_to_use` frontmatter enables Claude Code auto-invocation by intent.
- `disable-model-invocation` frontmatter prevents auto-invocation for destructive skills.
- `rites/sync_docs.py` regenerates `docs/skills.md` (the canonical Arcana skill catalog) from each `SKILL.md`'s frontmatter.

### Library management

- `rites/sync_library.py` (`/grm-library-sync`) — reconciles the local library against disk. Detects missing, stale, mismatched, and unmanaged grimoires.
- `rites/adopt_grimoire.py` (`/grm-library-adopt`) — writes a `grimoire.json` manifest for an existing unmanaged directory.
- `/grm-meta-help` enumerates every installed skill across Arcana and all domain grimoires.

### Summoning rite (one-command install)

`rites/summon.sh` + `rites/summon.py` — release-first binary bootstrap with Python source fallback. Steps:

1. Detects OS / architecture, downloads the matching `grimoire-summon-*` release asset from GitHub Releases (with checksum verification), and runs the binary.
2. Falls back to the Python source bootstrap if the release asset is unavailable.
3. Discovers grimoires via GitHub or GitLab API (or static `library.json`); presents an interactive menu.
4. Clones Arcana and selected grimoires under `~/grimoires/`.
5. Updates `~/grimoires/library.json`.
6. Injects the canonical Grimoire instruction block into `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`.
7. Always runs `register_skills.py` — including when zero domain grimoires were selected, so Arcana's own `/grm-*` skills register regardless. Surfaces both stdout and stderr from the registration subprocess so failures are never silent. Spot-checks the agent skill directories afterward and reports counts.

The launcher GUI uses Dear PyGui with:

- DPI-aware font scaling (auto-detected from tkinter / xrandr; honors `GRIMOIRE_GUI_SCALE` env var override). Loads a system TTF when available so text stays crisp at high resolutions.
- A vaporwave-leaning theme (hot pink, cyan, purple, lavender) consistent with the Obsidian graph color palette.
- Auto-fit viewport that grows after the first render to fit content (no scroll for primary actions).
- The Arcana icon bound as the small + large viewport icons (extracted from the resources/ directory or the PyInstaller bundle).
- Copyable log window where every subprocess line (git, register_skills) is captured so users can paste failure output back to the maintainer.
- Summon button stays disabled until at least one grimoire is selected, drawing the eye to Discover as the first action.

`rites/build_summon_binary.py` builds the release artifact via PyInstaller, bundling the resources/ directory so the runtime icon works in the frozen binary. Native executable icons (`.ico` on Windows, `.icns` on macOS) are picked up automatically if present in `resources/`.

### Formulae (templates)

- `formulae/grimoire/` — full grimoire scaffold (root hub, README, manifest, `sources/`, `inbox/`, `chapters/`, `log.md`, `.obsidian/graph.json`).
- `formulae/chapter_hub.formula.md` — chapter hub template with frontmatter scaffolding.
- `formulae/page.formula.md` — knowledge page template.
- `formulae/source.formula.md` — source artifact template.
- `formulae/log_entry.formula.md` — log entry format reference.
- `formulae/invocation.formula.md` — generic invocation skeleton (for new invocation authors).

### Obsidian integration

- Folder-named hubs render as meaningful graph-view nodes; wikilinks and `aliases:` frontmatter make backlinks first-class.
- Hub-level tags (`hub/root`, `hub/chapter`, `hub/sub`) plus `type/*` tags drive Obsidian graph color groups.
- Each grimoire ships `.obsidian/graph.json` with a vaporwave color palette: hot pink for the grimoire root, cyan for chapter hubs, purple for sub-hubs, lavender for source pages, electric blue for playbooks, pale pink for references.
- `.gitignore` policy ignores per-user Obsidian state but tracks the shareable `graph.json`, `app.json`, `core-plugins.json`, `community-plugins.json`.
- `docs/obsidian.md` documents the conventions and explains common gotchas (e.g. alias-resolved wikilinks creating empty stubs on Ctrl+click).

### Documentation

- `arcana.md` — root hub, lists every doc / invocation / formula / rite.
- `README.md` — project overview, what a grimoire is, install command, layout diagram.
- `docs/installation.md` — summoning rite walkthrough plus manual install.
- `docs/quickstart.md` — 5-minute smoke test.
- `docs/agent_configuration.md` — per-agent setup (Claude Code, Codex/ChatGPT, GitHub Copilot, Cursor).
- `docs/operating_model.md` — storage layers, hub convention, routing model.
- `docs/page_schema.md` — canonical frontmatter specification.
- `docs/reference.md` — terminology, library/manifest schemas, path keys, formula placeholders.
- `docs/script_vs_ai.md` — architectural principle for when to use rites (mechanical) vs invocations (judgment).
- `docs/obsidian.md` — vault setup and graph-view configuration.
- `docs/governance.md` — maintenance policies and versioning.
- `docs/release.md` — release workflow for the summoning rite binaries.
- `docs/skills.md` — canonical Arcana skill catalog (auto-generated from each `SKILL.md`).

### Supported agents

- **Claude Code** — full skill registration; `when_to_use` auto-invocation; `CLAUDE.md` instruction block injection.
- **Codex / ChatGPT (CLI)** — pointer-only SKILL.md registration; `AGENTS.md` instruction block injection.
- **GitHub Copilot, Cursor, ChatGPT (hosted)** — via the agent instruction block in `CLAUDE.md` / `AGENTS.md`.
