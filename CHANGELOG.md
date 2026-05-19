# Changelog

## [1.0.0] — 2026-05-19

Current Arcana 1.0.0 state.

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

**Storage layers.** Every domain grimoire is organized into:

| Layer | Directory | Owner | Purpose |
|---|---|---|---|
| Sources | `sources/` | LLM reads, never modifies | Immutable source artifacts: articles, transcripts, papers, screenshots. Citation-stable: pages with `authority: external` cite paths under here. |
| Inbox | `inbox/` | LLM and user both write | Optional transient drop zone for mixed content awaiting classification. Cleared by `/grm-domain-ingest`. Pages must NOT cite `inbox/` paths in `sources:` (validator enforces). |
| Wiki | `chapters/`, root hub | LLM authors and maintains | Synthesized knowledge with required frontmatter. |
| Schema | `grimoire.json` + injected agent block | User co-evolves | Tells the agent how to operate this grimoire. |

Plus the per-grimoire `log.md` — append-only activity log. Each entry begins `## [YYYY-MM-DD HH:MM] <op> | <title>` so recent activity is `grep`-scannable. Arcana itself is the framework repository and does not keep root-level grimoire content layers such as `sources/`, `inbox/`, or `log.md`; those live in the domain grimoire scaffold under `formulae/grimoire/`.

**Wikilinks for in-grimoire references.** Hubs use full-path Obsidian-style wikilinks for in-grimoire pointers, e.g. `[[chapters/build_system/cmake|cmake]]`. `rites/validate_links.py` resolves wikilink targets only as repository-root relative paths; alias-based and filename-stem-only wikilinks are invalid. Display labels should name only the target filename, normalized for reading, because the path already carries parent context. `validate_links` warns when a display label repeats folder/project/trip context. Cross-grimoire references stay as path placeholders (`GRIMOIRE_ARCANA/...`).

The shared `_lib.resolve_wikilink_path` resolver tries `<body>.md` first, then `<body>` as-given, so multi-dot stems like `[[plugin_ICD.template]]` correctly resolve to `plugin_ICD.template.md`. This supports the deliverable-suffix conventions `<name>.<ACRONYM>.md` (e.g. ICD, IDD, SDK) and `<name>.<role>.md` (e.g. `.template`, `.example`) without misreading the suffix as a file extension.

When a wikilink fails to resolve, the bundled `.obsidian/app.json` (`newLinkFormat: "absolute"`, `useMarkdownLinks: false`) prevents Obsidian's default `"shortest"` behavior from silently spawning a recursive directory tree on Ctrl-click. `rites/repair_links.py` (skill: `/grm-domain-repair-links`) bulk-promotes legacy filename-only wikilinks to canonical full-path form.

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
| `/grm-domain-repair-links` | Bulk-promotes filename-only and `[[parent_sibling\|sibling]]` wikilinks to canonical full-path form. Resolution order: sibling → descendant-of-source-dir → descendant-of-source-chapter → globally-unique → display-label fallback for the synthesized-basename anti-pattern. Code-fence and inline-backtick aware, dry-run by default, refuses to guess on ambiguous targets. |
| `/grm-domain-improve` | Comprehensive grimoire audit and improvement orchestrator. |
| `/grm-domain-analyze-semantics` | Judgment-based naming and organization audit. |
| `/grm-domain-validate-structure` | Structural compliance against Arcana formulae and conventions. |
| `/grm-domain-validate-boundaries` | Magical/practical boundary enforcement — ensures domain grimoires use practical terminology, not Arcana's system vocabulary. Optional `--arcana` flag scans Arcana itself. |

Every domain skill that operates on the active grimoire (everything except `create-grimoire`) shares a single precondition fragment at `invocations/meta/grimoire_directory_guard.md`, included via `!cat`. Skills are pointer-only; the guard text lives in one place.

### Validation suite

Mechanical rites, each independently invocable and orchestrated by `rites/validate.py`:

- `validate_structure` — Arcana directory layout and required hub files.
- `validate_domain_structure` — domain grimoire layout (root hub, `sources/`, `chapters/`, `log.md`); validates `grimoire.json` via the shared `_lib.load_manifest` (catches missing `name`, missing/invalid `namespace`, parse errors); enforces `.obsidian/app.json` with `newLinkFormat: "absolute"` so wikilinks cannot silently spawn recursive directory trees on Ctrl-click.
- `validate_naming` — snake_case for paths, kebab-case for skills.
- `validate_format` — invocation/formula schema; hubs are thin routers (<200 lines).
- `validate_frontmatter` — page schema compliance (type, required fields per type, aliases/tags shape, `last_verified` parses).
- `validate_links` — markdown links resolve; wikilinks resolve only as repository-root relative paths; verbose wikilink display labels warn.
- `validate_orphans` — every page is reachable from at least one other page, including full-path wikilink inbound references.
- `validate_provenance` — pages with `authority: external` or `hybrid` cite real artifacts under `sources/`; never cite `inbox/`.
- `validate_security` — credential patterns and unsafe Python constructs.
- `validate_semantics` — hyphenated path examples in markdown prose (Arcana convention is snake_case for paths).
- `validate_skill_refs` — every `/grm-*` reference in prose resolves to a real skill folder.

The full suite runs sequentially or in parallel; smart mode picks only validators relevant to the working tree's git changes.

### Shared library (`rites/_lib.py`)

Every validator and library utility imports from a single shared module:

- Logger functions (`info`, `ok`, `warn`, `err`) — uniform `[LEVEL]` prefix in 2-space indent.
- Frontmatter parser (`parse_frontmatter`) — canonical YAML subset handling inline + multi-line lists.
- Markdown helpers (`strip_code_blocks`, `LINK_RE`, `WIKILINK_RE`, `CODE_FENCE_RE`).
- Manifest / library loaders (`load_manifest`, `load_library`, `resolve_local_path`).
- Grimoire root resolution (`default_arcana_root`, `add_grimoire_arg`, `resolve_grimoire_arg`).
- Page discovery (`iter_pages`).
- Regex constants (`NAMESPACE_RE`, `SKILL_SLUG_RE`, `DATE_RE`, `FRONTMATTER_RE`).

Adding a new validator is now a ~30-line affair: import from `_lib`, run the check, exit 0 or 1.

### Skill system

- Skills are thin SKILL.md pointer files registered into agent skill directories. No logic embedded in the skill itself.
- Arcana ships `/grm-*` skills; each domain grimoire contributes `/<namespace>-*` skills.
- `rites/register_skills.py` (`/grm-skills-register`) discovers and installs skills from Arcana and every library entry to Claude Code (`~/.claude/skills/`) and Codex/ChatGPT (`~/.codex/skills/`).
- Source SKILL.md files use `{{NAMESPACE}}` and `{{ARCANA_PATH}}` placeholders resolved at registration time.
- `when_to_use` frontmatter enables Claude Code auto-invocation by intent; every Arcana skill has it.
- `disable-model-invocation: true` is set on each individual `arcana-validate-*` skill and on `arcana-clean`. The aggregate `arcana-validate-all` is the single auto-invoke target for "run validation"; the focused validators stay manually callable but no longer compete for picker attention.
- `rites/sync_docs.py` regenerates `docs/skills.md` (the canonical Arcana skill catalog) from each `SKILL.md`'s frontmatter.
- `/grm-meta-update-agent-block` refreshes the canonical Grimoire block in user agent instruction files (`CLAUDE.md`, `AGENTS.md`, and user-specified files) while preserving unrelated user instructions. The canonical block carries begin/end markers so future replacements can touch only the Grimoire section.

### Library management

- `rites/sync_library.py` (`/grm-library-sync`) — reconciles the local library against disk. Detects missing, stale, mismatched, and unmanaged grimoires.
- `rites/adopt_grimoire.py` (`/grm-library-adopt`) — writes a `grimoire.json` manifest for an existing unmanaged directory.
- `/grm-meta-help` enumerates every installed skill across Arcana and all domain grimoires.

### Summoning rite (one-command install)

`rites/summon.sh` + a three-module Python implementation. Release-first binary bootstrap with Python source fallback. Steps:

1. Detects OS / architecture, downloads the matching `grimoire-summon-*` release asset from GitHub Releases (with checksum verification), and runs the binary. PyInstaller bundles all three Python modules into one executable.
2. Uses Python source mode by default for Linux GUI sessions, avoiding frozen GLFW/GLX library drift across distro render stacks. Linux CLI/headless installs, macOS, Windows, and `GRIMOIRE_SUMMON_BINARY=always` still use the release-binary path.
3. Falls back to the Python source bootstrap if the release asset is unavailable or exits abnormally. In source mode, downloads `summon.py` + `summon_core.py` always; downloads `summon_gui.py` only when GUI mode is possible (skipped for `--cli`/`-h`/`--help`).
4. Probes Dear PyGui/OpenGL startup in a subprocess before opening the full source GUI. If GLX/GLFW fails, the rite falls back to CLI cleanly.
5. Reads prompts from the controlling terminal when launched through `curl | bash`, so the curl pipe does not cause `EOFError`.
6. Installs Python, pip, and Dear PyGui only after explicit `y` confirmation. Dear PyGui installs into the Grimoire-managed dependency cache, never into the Arcana repository.
7. Discovers grimoires via GitHub or GitLab API (or static `library.json`); presents an interactive menu.
8. Clones Arcana and selected grimoires under `~/grimoires/`.
9. Updates `~/grimoires/library.json`.
10. Injects the canonical marked Grimoire instruction block into `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`.
11. Always runs `register_skills.py` — including when zero domain grimoires were selected, so Arcana's own `/grm-*` skills register regardless. Surfaces both stdout and stderr from the registration subprocess so failures are never silent. Spot-checks the agent skill directories afterward and reports counts.

The Python implementation is split for auditability and headless friendliness:

- `rites/summon.py` (~90 lines) — pure dispatcher: argparse, GUI/CLI mode detection, lazy import of the GUI module.
- `rites/summon_core.py` (~830 lines) — install engine: constants, Logger, git/HTTP helpers, GitHub/GitLab discovery, install pipeline, interactive CLI flow. Pure stdlib.
- `rites/summon_gui.py` (~2,480 lines) — Dear PyGui front end: settings persistence, threaded workers with cancellation, theme system, four tabs (Install / Manage / Settings / Diagnostics), live log panel.

The launcher GUI uses Dear PyGui with:

- DPI-aware font scaling (auto-detected from tkinter / xrandr; honors `GRIMOIRE_GUI_SCALE` env var override). Loads a system TTF when available so text stays crisp at high resolutions.
- A vaporwave-leaning theme (hot pink, cyan, purple, lavender) consistent with the Obsidian graph color palette.
- Auto-fit viewport that grows after the first render to fit content (no scroll for primary actions).
- The Arcana icon bound as the small + large viewport icons (extracted from the resources/ directory or the PyInstaller bundle).
- Copyable log window where every subprocess line (git, register_skills) is captured so users can paste failure output back to the maintainer.
- Summon button stays disabled until at least one grimoire is selected, drawing the eye to Discover as the first action.

`rites/build_summon_binary.py` builds the release artifact via PyInstaller, bundling the resources/ directory so the runtime icon works in the frozen binary. PyInstaller follows imports automatically, so all three Python modules end up in one executable. Native executable icons (`.ico` on Windows, `.icns` on macOS) are picked up automatically if present in `resources/`.

### Formulae (templates)

- `formulae/README.md` — one-line description per template; orients new contributors to which template is expanded by which skill.
- `formulae/grimoire/` — full grimoire scaffold (root hub, README, manifest, `sources/`, `inbox/`, `chapters/`, `log.md`, `.obsidian/graph.json`). The scaffolded `README.md` ships with an `## Installation` section keyed off a `{{GRIMOIRE_REPO_URL}}` placeholder, so any downstream consumer who finds a grimoire on a git host (private GitLab, public GitHub, internal Gitea) is routed through the Arcana summoning rite first instead of cloning the grimoire standalone. The `/grm-domain-create-grimoire` flow captures `repo_url` during Step 1 (Discovery) and substitutes it during Step 4.
- `formulae/chapter_hub.formula.md` — chapter hub template with frontmatter scaffolding.
- `formulae/page.formula.md` — knowledge page template.
- `formulae/source.formula.md` — source artifact template.
- `formulae/log_entry.formula.md` — log entry format reference.
- `formulae/invocation.formula.md` — generic invocation skeleton (for new invocation authors).

### Obsidian integration

- Folder-named hubs render as meaningful graph-view nodes; full-path wikilinks make backlinks deterministic.
- Hub-level tags (`hub/root`, `hub/chapter`, `hub/sub`) plus `type/*` tags drive Obsidian graph color groups.
- Each grimoire ships `.obsidian/graph.json` with a vaporwave color palette: hot pink for the grimoire root, cyan for chapter hubs, purple for sub-hubs, lavender for source pages, electric blue for playbooks, pale pink for references.
- Each grimoire also ships `.obsidian/app.json` with `{"newLinkFormat": "absolute", "useMarkdownLinks": false}` — mandatory settings (not preferences) that prevent the recursive-directory Ctrl-click footgun and keep wikilinks in `[[...]]` form so the rest of Arcana (validators, repair rite, ingest skills) operates on a single canonical link syntax. `validate_domain_structure` enforces both at validation time.
- `.gitignore` policy ignores per-user Obsidian state but tracks the shareable `graph.json`, `app.json`, `core-plugins.json`, `community-plugins.json`.
- `docs/obsidian.md` documents the full-path wikilink convention, the required `app.json` settings, the multi-dot filename conventions (`<name>.<ACRONYM>.md`, `<name>.<role>.md`), and editor behavior.
- `docs/vscode.md` documents the parallel setup VS Code needs to avoid the same recursive-directory class of bug. Root cause: the **Markdown Preview Enhanced** extension ships a `DocumentLinkProvider` whose wikilink Ctrl-click handler resolves targets relative to the current file, with no per-workspace override. Recommended fix: uninstall MPE (VS Code's built-in markdown preview is sufficient and has no wikilink bug) and install `foam.foam-vscode` for workspace-root wikilink resolution. A disable-only fallback (`markdown-preview-enhanced.enableWikiLinkSyntax: false` in user settings) is documented for users who need MPE's advanced rendering.

### Documentation

- `arcana.md` — root hub, lists every doc / invocation / formula / rite.
- `README.md` — project overview, what a grimoire is, install command, layout diagram. Links to canonical docs rather than re-explaining hub convention or storage layers.
- `docs/installation.md` — summoning rite walkthrough, manual install, 5-minute smoke test, troubleshooting. Includes a "When a grimoire is discovered first" subsection covering the reverse case (user finds a grimoire repo before Arcana).
- `docs/agent_configuration.md` — per-agent setup (Claude Code, Codex/ChatGPT, GitHub Copilot, Cursor).
- `docs/operating_model.md` — canonical home for storage layers, hub convention, and routing rules. Other docs link here.
- `docs/page_schema.md` — canonical frontmatter specification, including the authority models table.
- `docs/reference.md` — terminology, the magical boundary, library/manifest schemas, path keys, formula placeholders.
- `docs/script_vs_ai.md` — architectural principle for when to use rites (mechanical) vs invocations (judgment).
- `docs/obsidian.md` — vault setup and graph-view configuration.
- `docs/vscode.md` — VS Code setup for wikilink Ctrl-click navigation (uninstall Markdown Preview Enhanced, install Foam).
- `docs/governance.md` — maintenance policies and versioning.
- `docs/release.md` — release workflow for the summoning rite binaries (uses the `[build]` extra in `pyproject.toml`).
- `docs/skills.md` — canonical Arcana skill catalog (auto-generated from each `SKILL.md`).

### Public-readiness

- `LICENSE` — MIT.
- `CONTRIBUTING.md` — contributor onramp covering the four working layers (`docs/`, `formulae/`, `invocations/`, `rites/`, `skills/`), local setup, validator + test suites, code style, and PR expectations.
- `pyproject.toml` — pure-stdlib runtime; optional groups `[dev]` (pytest), `[gui]` (DearPyGui for the launcher), `[build]` (PyInstaller for release artifacts).
- `tests/` — pytest suite with fixture grimoires (`good_grimoire`, `bad_frontmatter`, `bad_links`) covering `_lib`, installer prompt fallback behavior, and every validator end-to-end via subprocess. The full suite runs in under a second.
- `.github/workflows/summon-release.yml` — builds the release binary; uses `pip install '.[build]'` (single canonical dep declaration).

### Sub-hub organization

Inside `invocations/arcana/`:

- `validators/` holds the mechanical validator docs that each have a corresponding `/grm-arcana-validate-*` skill.
- `quality/` holds the judgment-based quality docs (`improve_documentation.md`, `validate_rites.md`).

### Supported agents

- **Claude Code** — full skill registration; `when_to_use` auto-invocation; `disable-model-invocation` to keep focused validators out of auto-pick; `CLAUDE.md` instruction block injection.
- **Codex / ChatGPT (CLI)** — pointer-only SKILL.md registration; `AGENTS.md` instruction block injection.
- **GitHub Copilot, Cursor, ChatGPT (hosted)** — via the agent instruction block in `CLAUDE.md` / `AGENTS.md`.
