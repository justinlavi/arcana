# Changelog

## [1.0.0] - 2026-05-25

Arcana 1.0.0 defines Arcana as a framework for creating, installing, routing,
validating, and maintaining grimoires: structured, AI-navigable knowledge
bases the LLM can keep current over time.

This entry is the current architecture source of truth for the release.

### Release highlights

- Arcana is modeled by `arcana.json`; grimoires are modeled by
  `grimoire.json`.
- Arcana commands use command families: `/arc-*` for Arcana, agent, library,
  workspace, and help operations; `/grm-*` for universal active-grimoire
  operations.
- Grimoire manifests use `skill_prefix` for domain skill names.
- Arcana skill sources live under `skills/<family>/<slug>/`, mirrored by
  family-specific invocation folders under `invocations/`.
- The Arcana path placeholder is `ARCANA_HOME`.
- `~/grimoires/library.json` is the only persistent local grimoire registry;
  remote grimoire discovery uses explicit GitHub or GitLab scopes.
- UTF-8 without BOM and LF line endings are enforced through repository
  guardrails and `/arc-validate-encoding` / `/grm-validate-encoding`.
- The Summoning Rite provides release installs, Windows Git Bash support,
  checksum normalization, progress reporting, retry behavior, and fallback
  downloads.

### Architecture

Arcana is the engine for grimoires. A grimoire combines deterministic
hub-based routing, layered storage, page frontmatter, provenance rules,
mechanical validators, and slash-command skills. Arcana ships the universal
framework; each domain grimoire contributes its own content, sources, and
optional skills.

Arcana itself is the framework repository. It does not keep root-level domain
storage layers such as `sources/`, `inbox/`, `chapters/`, or `log.md`; those
live in grimoire repositories and in the scaffold under `formulae/grimoire/`.

### Knowledge structure

**Hub-based routing.** Every folder F that acts as a router has a hub at
`F/<basename(F)>.md`. Hubs route to sub-hubs, leaf pages, or both, with
open-ended depth. The grimoire root hub is `<grimoire>/<grimoire>.md`. Each
hop narrows the search until the agent reaches the leaf that answers the
question. Folder-named hubs keep Obsidian graph nodes meaningful and unique.

**Page frontmatter.** Authored markdown pages in Arcana docs, invocations,
formulae, and grimoire chapters carry YAML frontmatter:

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

The canonical schema lives in `docs/page_schema.md` and is enforced by
`rites/validate_frontmatter.py`.

**Storage layers.** Every grimoire is organized into:

| Layer | Directory | Owner | Purpose |
|---|---|---|---|
| Sources | `sources/` | LLM reads, never modifies | Immutable source artifacts: articles, transcripts, papers, screenshots. Citation-stable pages cite paths here. |
| Inbox | `inbox/` | LLM and user both write | Optional transient drop zone for mixed content awaiting classification. Cleared by `/grm-ingest`; pages must not cite `inbox/`. |
| Wiki | `chapters/`, root hub | LLM authors and maintains | Synthesized knowledge with required frontmatter. |
| Schema | `grimoire.json` + injected agent block | User co-evolves | Tells agents how to operate this grimoire. |

Every grimoire also has an append-only `log.md`. Each entry begins
`## [YYYY-MM-DD HH:MM] <op> | <title>` so recent activity is easy to scan.

**Wikilinks.** In-grimoire pointers use full-path Obsidian wikilinks, e.g.
`[[chapters/build_system/cmake|cmake]]`. `rites/validate_links.py` resolves
wikilink targets as repository-root relative paths; alias-only and filename
stem-only wikilinks are invalid. Display labels should name only the target
file, normalized for reading, because the path already carries parent context.

The shared `_lib.resolve_wikilink_path` resolver tries `<body>.md` first and
then `<body>` as given, so multi-dot stems such as
`[[plugin_ICD.template]]` correctly resolve to `plugin_ICD.template.md`.
This supports deliverable suffixes such as `<name>.<ACRONYM>.md` and
`<name>.<role>.md` without misreading the suffix as a file extension.

When a wikilink fails to resolve, the bundled `.obsidian/app.json`
(`newLinkFormat: "absolute"`, `useMarkdownLinks: false`) prevents Obsidian's
default shortest-link behavior from silently spawning recursive directory
trees on Ctrl-click. `rites/repair_links.py` (`/grm-repair-links`) normalizes
filename-only wikilinks to canonical full-path form.

Cross-grimoire references use path placeholders, especially `ARCANA_HOME/...`
for Arcana and library keys such as `cooking-grimoire/...` for installed
grimoires.

### Identity and library

- Arcana declares framework identity in `arcana.json` with `kind: "arcana"`,
  default `skill_prefix: "arc"`, and a `skill_families` map.
- Each grimoire declares domain identity in root `grimoire.json`: `name`,
  `skill_prefix`, and `description`.
- Grimoire skills use the `skill_prefix` from their own manifest.
- The local library at `~/grimoires/library.json` records installed grimoire
  paths and optional clone URLs. It does not define grimoire identity.
- Remote grimoires are discovered from explicit GitHub or GitLab scopes during
  summoning, not from a bundled static catalog.
- Domain grimoires are pure content repositories: no engine code, Arcana
  submodules, or copied framework files.

### Command families and skills

Arcana source skills follow a canonical schema:

```text
skills/<family>/<slug>/SKILL.md
```

`arcana.json` defines the shipped families:

| Family | Source path | Public commands |
|---|---|---|
| Arcana | `skills/arcana/` | `/arc-*` |
| Grimoire | `skills/grimoire/` | `/grm-*` |
| Agent | `skills/agent/` | `/arc-agent-*` |
| Library | `skills/library/` | `/arc-library-*` |
| Workspace | `skills/workspace/` | `/arc-workspace-*` |
| Help | `skills/help/` | `/arc-help` |

The same family split exists under `invocations/`: `arcana/`, `grimoire/`,
`agent/`, `library/`, `workspace/`, `help/`, and `meta/`. The `meta/` folder
is reserved for shared fragments such as the active-grimoire directory guard.

Skills are thin pointer files. Source `SKILL.md` files use placeholders such
as `{{SKILL_PREFIX}}` and `{{ARCANA_PATH}}`; `rites/register_skills.py`
substitutes them when installing skills into agent directories.

### Arcana-shipped skills

| Skill | Purpose |
|---|---|
| `/arc-improve` | Maintainer workflow for improving Arcana itself through validation plus architecture, rite, and documentation quality review. |
| `/arc-validate-all` | Run the full Arcana validator suite. |
| `/arc-validate-encoding` | Validate UTF-8, LF line endings, BOMs, mojibake markers, and repair artifacts in Arcana. |
| `/arc-validate-format` | Validate Markdown formatting in Arcana. |
| `/arc-validate-frontmatter` | Validate Arcana page frontmatter. |
| `/arc-validate-links` | Validate Arcana Markdown links and wikilinks. |
| `/arc-validate-naming` | Validate Arcana naming conventions. |
| `/arc-validate-orphans` | Detect orphan pages in Arcana. |
| `/arc-validate-portability` | Detect filesystem-portability issues in Arcana paths. |
| `/arc-validate-provenance` | Validate source provenance in Arcana. |
| `/arc-validate-security` | Scan Arcana for credential patterns and unsafe Python constructs. |
| `/arc-validate-semantics` | Scan Arcana prose for hyphenated path examples. |
| `/arc-validate-skill-refs` | Validate that Arcana-shipped slash commands mentioned in docs resolve to real skills. |
| `/arc-validate-structure` | Validate Arcana's directory structure and required hubs. |
| `/arc-agent-register-skills` | Register Arcana skills and installed grimoire skills into supported agent directories. |
| `/arc-agent-update` | Refresh marked Grimoire instruction blocks in agent files while preserving user content. |
| `/arc-library-adopt` | Adopt an unmanaged directory under `~/grimoires/` as a grimoire. |
| `/arc-library-sync` | Reconcile `~/grimoires/library.json` against installed directories. |
| `/arc-workspace-clean` | Remove temporary rite artifacts across Arcana and installed grimoires. |
| `/arc-help` | Display the Arcana skill catalog and installed grimoire skill guide. |

### Universal grimoire skills

| Skill | Purpose |
|---|---|
| `/grm-create` | Create a new grimoire with scaffold, manifest, library entry, and agent setup. |
| `/grm-create-chapter` | Add a knowledge chapter with frontmatter and hub naming. |
| `/grm-ingest` | Bring content into the active grimoire: single source, folder, or inbox sweep. |
| `/grm-file-answer` | Promote a chat answer into a properly frontmattered wiki page. |
| `/grm-lint` | Health-check the active grimoire. |
| `/grm-improve` | Audit, normalize, validate, and upgrade the active grimoire against current Arcana. |
| `/grm-analyze-semantics` | Judgment-based naming and organization audit. |
| `/grm-repair-links` | Promote filename-only wikilinks to canonical full-path form. |
| `/grm-register-skills` | Register Arcana skills plus the active grimoire's own skills. |
| `/grm-update-arcana` | Pull/update Arcana, validate it, refresh agent integration, register skills, and check active-grimoire health. |
| `/grm-validate-boundaries` | Ensure grimoires do not use Arcana-only system terminology. |
| `/grm-validate-encoding` | Validate UTF-8/LF policy in the active grimoire. |
| `/grm-validate-format` | Validate Markdown formatting in the active grimoire. |
| `/grm-validate-frontmatter` | Validate page frontmatter in the active grimoire. |
| `/grm-validate-links` | Validate Markdown links and wikilinks in the active grimoire. |
| `/grm-validate-orphans` | Detect orphan pages in the active grimoire. |
| `/grm-validate-portability` | Validate filesystem portability in the active grimoire. |
| `/grm-validate-provenance` | Validate source provenance in the active grimoire. |
| `/grm-validate-structure` | Validate grimoire structure and Arcana-managed scaffold files. |

Focused Arcana validators and grimoire validators are separate skills. The
aggregate `/arc-validate-all` is the default Arcana validation entry point.

### Validation suite

Mechanical rites are independently invocable and orchestrated by
`rites/validate.py`:

- `validate_structure` - Arcana layout and required hub files.
- `validate_grimoire_structure` - grimoire layout, manifest schema, Obsidian
  app settings, and Arcana-managed scaffold compliance.
- `validate_naming` - snake_case paths, kebab-case skill slugs, and
  command-family skill schema.
- `validate_format` - Markdown formatting, invocation/formula shape, hub
  length, unclosed fences, and invalid tree branch markers.
- `validate_frontmatter` - page schema compliance.
- `validate_links` - Markdown links and full-path wikilinks.
- `validate_orphans` - inbound-reference reachability.
- `validate_provenance` - `external` and `hybrid` pages cite stable sources,
  never `inbox/`.
- `validate_security` - credential patterns and unsafe Python constructs.
- `validate_semantics` - hyphenated path examples in prose.
- `validate_skill_refs` - Arcana-shipped slash command references resolve to
  real skill sources.
- `validate_portability` - reserved path characters and reserved basenames.
- `validate_encoding` - invalid UTF-8, BOMs, CRLF drift, mojibake markers,
  numeric range question-mark artifacts, and repair artifacts.

The orchestrator runs sequentially, in parallel, or in smart mode against
working-tree changes.

### Maintenance model

`/arc-improve` is Arcana's maintainer entry point. It starts with the
mechanical validator suite, then runs judgment-based quality passes for:

- Whole-repository architecture: layout, naming, source-of-truth boundaries,
  AI-agent read paths, scalability, and future maintainability.
- Rite quality: script purpose, error handling, exit codes, idempotency,
  portability, and auditability.
- Documentation quality: duplication, clarity, canonical homes, generated
  views, and user-facing navigation.

The architecture pass lives in
`invocations/arcana/quality/review_architecture.md`. It treats every Arcana
surface as in scope: root files, docs, invocations, formulae, rites, skills,
tests, release automation, Obsidian settings, and resources.

### Shared library

`rites/_lib.py` is the shared utility layer used by validators and library
tools:

- Logger functions (`info`, `ok`, `warn`, `err`).
- Frontmatter parsing (`parse_frontmatter`).
- Markdown helpers (`strip_code_blocks`, `LINK_RE`, `WIKILINK_RE`,
  `CODE_FENCE_RE`).
- Manifest and library loaders (`load_manifest`, `load_library`,
  `resolve_local_path`).
- Grimoire root resolution (`default_arcana_root`, `add_grimoire_arg`,
  `resolve_grimoire_arg`).
- Page discovery (`iter_pages`).
- Regex constants for dates, frontmatter, skill slugs, and skill prefixes.

Adding a new validator is intentionally small: import from `_lib`, perform the
check, and exit 0 or 1.

### Agent integration

- `rites/register_skills.py` installs generated pointer skills into Claude
  Code (`~/.claude/skills/`) and Codex/ChatGPT (`~/.codex/skills/`), writing
  generated files as UTF-8/LF.
- `/arc-agent-register-skills` registers Arcana plus every installed grimoire.
- `/grm-register-skills` registers Arcana plus only the active grimoire.
- `/arc-agent-update` refreshes the canonical marked Grimoire block in
  `CLAUDE.md`, `AGENTS.md`, and user-specified files while preserving
  unrelated instructions.
- `rites/templates/grimoire_block.md` is the only source for the injected
  agent block. Source bootstrap downloads it and release binaries bundle it.
- `rites/sync_docs.py` regenerates `docs/skills.md` from skill frontmatter.

Supported agents:

- Claude Code - skill registration, auto-invocation metadata, and `CLAUDE.md`
  instruction block injection.
- Codex / ChatGPT CLI - pointer-only skill registration and `AGENTS.md`
  instruction block injection.
- GitHub Copilot, Cursor, and hosted ChatGPT - via copied or injected agent
  instruction blocks.

### Library management

- `rites/sync_library.py` (`/arc-library-sync`) reconciles the local library
  against disk, detecting missing, stale, mismatched, and unmanaged grimoires.
- `rites/adopt_grimoire.py` (`/arc-library-adopt`) writes a `grimoire.json`
  manifest for an existing unmanaged directory.
- `/arc-help` enumerates the Arcana catalog and installed grimoire skill guide.

### Summoning Rite

`rites/summon.sh` and the Python implementation provide a one-command install
path:

1. Detect OS and architecture.
2. Download the matching `grimoire-summon-*` GitHub Release asset with
   checksum verification.
3. Run the binary, or fall back to Python source bootstrap when needed.
4. Use Python source mode by default for Linux GUI sessions to avoid frozen
   GL/GLX library drift.
5. Probe Dear PyGui/OpenGL startup before opening the source GUI; fall back to
   CLI on failure.
6. Read prompts from the controlling terminal when launched through
   `curl | bash`.
7. Install Python, pip, and Dear PyGui only after explicit confirmation.
8. Discover grimoires from explicit GitHub or GitLab scopes.
9. Clone Arcana and selected grimoires under `~/grimoires/`.
10. Write `~/grimoires/library.json`.
11. Inject the marked Grimoire instruction block into agent instruction files.
12. Run skill registration even when no domain grimoires were selected.

The bootstrap includes release-asset progress, byte-count reporting, explicit
retry logs, connection/stall safeguards, Python download fallback for flaky
Git Bash curl/wget behavior, and normalized LF checksum files. Windows Git
Bash platforms (`MINGW*`, `MSYS*`, `CYGWIN*`) resolve to the Windows `.zip`
asset and run `grimoire-summon.exe`.

The implementation is split for auditability:

- `rites/summon.py` - dispatcher and mode selection.
- `rites/summon_core.py` - pure-stdlib install engine.
- `rites/summon_gui.py` - Dear PyGui front end.

`rites/build_summon_binary.py` builds PyInstaller release artifacts, bundles
`resources/`, and reports build failures clearly. The release workflow uses
Node 24-backed GitHub Actions and pins Windows builds to
`windows-2025-vs2026`.

### Formulae

- `formulae/README.md` - index of templates.
- `formulae/grimoire/` - complete grimoire scaffold: root hub, README,
  manifest, `sources/`, `inbox/`, `chapters/`, `log.md`, `.obsidian/`
  settings, `.gitattributes`, and `.editorconfig`.
- `formulae/chapter_hub.formula.md` - chapter hub template.
- `formulae/page.formula.md` - authored knowledge page template.
- `formulae/source.formula.md` - source artifact template.
- `formulae/log_entry.formula.md` - activity log entry reference.
- `formulae/invocation.formula.md` - generic invocation skeleton.

Newly created grimoires inherit the same UTF-8/LF guardrails and Obsidian link
settings Arcana validates.

### Obsidian and editor integration

- Folder-named hubs render as meaningful graph-view nodes.
- Full-path wikilinks make backlinks deterministic.
- Hub-level tags (`hub/root`, `hub/chapter`, `hub/sub`) and `type/*` tags
  drive Obsidian graph color groups.
- Each grimoire ships shareable `.obsidian/graph.json` and `.obsidian/app.json`.
- `.obsidian/app.json` enforces `newLinkFormat: "absolute"` and
  `useMarkdownLinks: false`.
- Per-user Obsidian state is ignored; shareable vault settings are tracked.
- `docs/obsidian.md` documents the full-path wikilink convention.
- `docs/vscode.md` documents VS Code setup to avoid recursive-directory
  wikilink navigation bugs.

### Documentation

- `arcana.md` - root hub for docs, invocations, formulae, and rites.
- `README.md` - project overview and install entry point.
- `docs/installation.md` - summoning rite walkthrough, manual install,
  smoke test, and troubleshooting.
- `docs/agent_configuration.md` - agent setup.
- `docs/operating_model.md` - storage layers, hub convention, and routing.
- `docs/page_schema.md` - frontmatter and authority models.
- `docs/reference.md` - terminology, manifests, path keys, and placeholders.
- `docs/skill_schema.md` - command-family skill schema.
- `docs/script_vs_ai.md` - when to use rites vs invocations.
- `docs/obsidian.md` - vault setup and graph configuration.
- `docs/vscode.md` - VS Code wikilink setup.
- `docs/governance.md` - maintenance and versioning.
- `docs/release.md` - release workflow.
- `docs/skills.md` - generated Arcana skill catalog.
- `invocations/arcana/quality/review_architecture.md` - judgment-based
  whole-repo architecture review used by `/arc-improve`.
- Installation and scaffold docs identify both `/arc-*` and `/grm-*` skill
  sets, and placeholder examples use the canonical cooking, HR, and Project
  Alpha names.
- `/grm-validate-structure` and `/grm-improve` now treat
  `.obsidian/graph.json` as managed scaffold alongside `.obsidian/app.json`,
  preserving the opinionated Obsidian graph-view color groups during grimoire
  audits and Arcana upgrade checks.

### Public readiness

- `LICENSE` - MIT.
- `CONTRIBUTING.md` - contributor onramp.
- `pyproject.toml` - pure-stdlib runtime with optional `[dev]`, `[gui]`, and
  `[build]` extras.
- `tests/` - pytest suite with fixture grimoires and validator coverage.
- `.github/workflows/summon-release.yml` - release binary build workflow.
- `.gitattributes` and `.editorconfig` - repository text-file policy.
