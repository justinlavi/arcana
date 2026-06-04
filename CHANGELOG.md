# Changelog

## [1.3.0] - 2026-06-04

MINOR. Existing grimoire content stays valid. This release changes Arcana's
public command surface and requires skill re-registration so agents see the new
commands.

### Changed

- **Validation is now one command per target.** The many individual validation
  skills collapse into `/arc-validate [selector]` and
  `/grm-validate [selector]`. Omitting the selector runs the full mechanical
  suite; selectors such as `links`, `frontmatter`, `structure`, `smart`,
  `auto`, `summary`, and `parallel` route through `rites/validate.py`.
- **Audit is now the word for judgment work.** `/grm-analyze-semantics` is now
  `/grm-audit-semantics`, and `/grm-validate-boundaries` is now
  `/grm-audit-boundaries`. Mechanical validation remains script-backed and
  exit-code based; audit workflows remain AI/judgment based.
- **Validator selection moved into the rite.** `rites/validate.py` now accepts
  positional selectors, comma-separated selectors, `--only`, and `--exclude`,
  for both Arcana and grimoire profiles.
- **Skill semantics were tightened across Arcana and Grimoire.** User-facing
  skills now read left to right by scope and intent: `/grm-file-answer` became
  `/grm-capture-answer`, `/grm-ingest` became `/grm-import`, `/grm-lint`
  became `/grm-health-check`, `/grm-register-skills` became
  `/grm-sync-skills`, `/arc-agent-register-skills` became
  `/arc-agent-sync-skills`, and `/arc-agent-update` became
  `/arc-agent-sync-instructions`. `/grm-update` remains the primary
  grimoire-user entry point for updating Arcana, following `UPDATE.md`, and
  re-syncing skills. The backing rite is renamed `rites/register_skills.py` →
  `rites/sync_skills.py` so the implementation name matches the `*-sync-skills`
  commands it serves; no skill ↔ rite name drift remains.
- **Both judgment audits are human-gated.** `/grm-audit-semantics` and
  `/grm-audit-boundaries` both set `disable-model-invocation` so a read-only
  judgment audit is run deliberately, not auto-fired; `/grm-validate` stays
  model-invocable.

### Improved

- **Validator selection is hardened.** Unknown selectors and a selection that
  resolves to zero validators (e.g. `--only x --exclude x`) now exit non-zero
  with a clear message instead of silently passing; the unknown-selector hint
  lists one canonical token per validator.
- **Redundancy reduction.** `summon_core.git()` is now a thin adapter over
  `git_capture()` (one env/timeout body); the SKILL.md frontmatter reader, the
  arcana.json skill-family loader, the command discovery, and the `$HOME`-token
  path resolver — previously re-implemented across five rites — now share one
  core in `rites/_lib.py`; the duplicated rite-profile table in
  `docs/script_vs_ai.md` and the hand-listed validators/quality entries in the
  Arcana invocations hub now point at their single canonical homes
  (`docs/rite_profiles.md`, the validator and quality sub-hubs).
- **Fork-aware update language.** The update process and `UPDATE.md` now say
  "Arcana" is whatever is installed — the upstream project or a fork you or your
  team maintain — pulled from whatever remote it tracks, rather than implying a
  single always-public source. A pull that fails (e.g. a private fork the
  current credentials can't reach) is a clean STOP-and-report.
- **Contract accuracy.** `rites/data/summon_contract.json` now documents the
  `--update` pull-and-heal surface; `append_log` drops the legacy `ingest` /
  `lint` / `file-answer` ops it had retained, matching its own documented set.

## [1.2.0] - 2026-06-02

MINOR. Existing grimoires stay valid and are brought current by the update process itself (skill re-registration plus the mechanical heal), so no hand migration is required — per the compatibility-based, self-healing-aware policy in `docs/governance.md`.

### Changed

- **Restoration → Update.** The maintenance concept that brings Arcana, agent skills, the library, agent instructions, and grimoires back to a current, validated, synchronized state is now **Update** — the term names what it does. `RESTORATION.md` is renamed to **`UPDATE.md`**; the mirrored thin pointer skills become **`/grm-update`** and **`/arc-update`** (from `/grm-restore` / `/arc-restore`; `/grm-update` continues the `/grm-update-arcana` → `/grm-restore` lineage). The grimoire formula README block markers become `<!-- BEGIN/END ARCANA UPDATE -->` and the heading `## Out of date? Update.`. The summon engine surfaces the new `--update` flag and the `arcana_update` action; the former `--restore` alias of `--reconcile` is removed.

### Added

- **Library-wide, branch-aware grimoire pull (`summon.py --update`).** A new rite, `rites/update_grimoires.py`, brings **every** grimoire in `~/grimoires/library.json` current before any heal — not just the active one. Per grimoire it fetches, detects the tracking branch and ahead/behind, and fast-forwards a clean branch that is behind. The load-bearing invariant is **pull-before-heal**: a grimoire that is dirty, diverged, detached, without an upstream, or behind on a host it cannot reach is reported and left **untouched** (healing a stale tree would re-derive upstream work and diverge). `rites/summon_core.py` gains `git_capture()` (returns stderr) so a fetch failure is classified as `auth_failed` / `offline` / `fetch_error`.
- **Private-host auth fallback.** Arcana is public and always pullable; grimoires may live on a private host needing a token. The update tries each grimoire with existing credentials (`GIT_TERMINAL_PROMPT=0`, the git credential store, `GITLAB_TOKEN`/`GITHUB_TOKEN`), and on failure collects it into a `needs_manual_pull` list and continues — so a teammate updates the grimoires they can reach and gets an exact, copy-pasteable manual-pull ask for the rest. A per-grimoire failure never aborts the run.

### Improved

- **The update is deterministic, not luck-dependent.** `summon.py --update --apply` orchestrates the whole update in one command — validate Arcana, reconcile the library, pull every grimoire, re-register skills, heal only the grimoires confirmed current — emitting one machine-readable envelope. Skill re-registration now always runs `register_skills.py --reset-managed` (the path that removes stale namespaces), and `UPDATE.md` instructs agents to report each rite's own `--format json` counts rather than self-counted claims. The grimoire heal — managed-scaffold re-sync, README update-block injection, wikilink repair — runs mechanically inside the rite.

### Fixed

- **Release-binary GUI now launches instead of falling back to CLI.** The OpenGL probe ran its `import dearpygui` check in a child process started by `system_python()`, which a frozen binary resolves to a *system* `python3` that has no Dear PyGui — so the probe failed with `ModuleNotFoundError` and the GUI dropped to CLI even though the binary's own bundled Dear PyGui was fine. The probe now runs in the interpreter that owns the GUI: a frozen binary re-invokes itself, while a source run still tests the `GRIMOIRE_SUMMON_PY_DEPS` cache. The probe body is shared through `run_gl_probe()` in `rites/summon_gui.py`, re-entered via the `GRIMOIRE_SUMMON_GL_PROBE` hook in `rites/summon.py`.
- **Accurate message when Dear PyGui is missing.** A missing-module probe failure no longer reports "no usable OpenGL/GLX context" with XWayland/Mesa advice; it states that Dear PyGui is unavailable and how to install it.
- **The build refuses to ship a GUI-less binary.** `rites/build_summon_binary.py` requires Dear PyGui to be importable in the build interpreter before running PyInstaller (`--collect-all` only warns on a missing module), and after building runs the artifact with `GRIMOIRE_SUMMON_GL_PROBE=import` to confirm the bundled Dear PyGui imports inside the binary. Both checks need no display and run in CI.

## [1.1.0] - 2026-06-02

First release after the 1.0.0 architecture snapshot. Backward compatible: existing grimoires stay valid and need no migration (see `RESTORATION.md` → Version Migrations).

### Changed

- **Activity log → content change log.** `log.md` is now an append-only history of *content* changes (pages and sources added, removed, or changed), not a journal of version-control mechanics. The log-entry formula forbids branch-scoped or merge/rebase/push-framed entries (there is no `merge` op); `rites/append_log.py` and the grimoire scaffold (`formulae/grimoire/log.md`, `formulae/grimoire/README.md`, `formulae/log_entry.formula.md`) carry the rule. Existing logs remain valid.
- **Versioning is compatibility-based and self-healing-aware.** `docs/governance.md` §Versioning now leads with a Compatibility Rule (compatibility, not change size, decides the bump), Arcana-specific PATCH/MINOR/MAJOR examples, and an explicit decision procedure for humans and AI agents. It records that Arcana's self-healing — repair rites, `/grm-restore`, and the skill-less `RESTORATION.md` procedure — absorbs most transitions: a break Arcana can auto-heal is a MINOR that ships its heal, and only a migration needing human judgment is MAJOR. `docs/release.md`, `CONTRIBUTING.md`, and the `/arc-improve` invocation now defer the bump decision to this policy.
- **Recovery → Restoration.** The maintenance concept that brings Arcana, agent skills, the library, agent instructions, and grimoires back to a current, validated, synchronized state is now **Restoration**. `RECOVERY.md` is renamed to **`RESTORATION.md`**, and the concept is exposed through two mirrored, thin pointer skills over that one canonical doc: **`/arc-restore`** (new; maintainer / fork side) and **`/grm-restore`** (renamed from `/grm-update-arcana`; the grimoire-user side that restores the grimoire and, by extension, its Arcana). The summon engine's reconcile vocabulary follows suit (`--restore` flag, `arcana_restore` action). The granular maintenance skills (`/arc-agent-update`, `/arc-agent-register-skills`, `/grm-register-skills`, `/arc-library-sync`) stay independent.
- **Restoration has two entry points.** Run the skill (`/grm-restore` / `/arc-restore`), or tell an AI agent *"pull the latest Arcana, then follow its restoration process"*. Both are codified as a block in the Arcana README and the grimoire formula README (`formulae/grimoire/README.md`) that every new grimoire ships; restoration injects that block into an existing grimoire's README when it is missing (see `RESTORATION.md` → Version Migrations).

### Improved

- **`RESTORATION.md` is the canonical restoration entry point.** It brings both Arcana and any grimoire current with a deterministic, rite-only grimoire-heal procedure (re-sync managed scaffold, repair links, re-validate) and a **Version Migrations** section recording any future version-specific heal steps. The `/arc-restore` and `/grm-restore` skills and the `arcana.md` / `README.md` routing surfaces point at it.

## [1.0.0] - 2026-06-01

Arcana 1.0.0 defines Arcana as a framework for creating, installing, routing,
validating, and maintaining grimoires: structured, AI-navigable knowledge
bases the LLM can keep current over time.

This entry is the release architecture snapshot. The live canonical rules
remain in `docs/`, `invocations/`, `formulae/`, `rites/`, and generated
indexes such as `docs/skills.md`.

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
Under `chapters/` the convention is an enforced if-and-only-if - a page is a hub
exactly when its filename stem equals its folder name - so an agent tells hubs
from leaves by path alone; `validate_grimoire_structure` checks both directions.
Page and folder names are lowercase `snake_case` (enforced by `validate_naming`);
depth is open-ended by design, bounded by topic structure rather than a fixed
cap.

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
`rites/validate_frontmatter.py`. `last_verified` must be a real verification
date: the validator rejects implausibly early sentinels (any date before a fixed
`2020-01-01` floor, such as the Unix epoch `1970-01-01`). The floor is a static
constant rather than the current date, so frontmatter validation stays
reproducible. `rites/new_page.py` stamps a schema-valid leaf from
`formulae/page.formula.md` with today's `last_verified`, so authored pages never
ship the formula's placeholder date. Tags are `/`-namespaced facets (`chapter/`,
`type/`, `hub/`, and optional owner-defined `domain/<...>`): the hub tree is the
primary navigation axis and a topical facet is an optional second lexical axis
for cross-cutting subjects.

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
holds shared fragments such as the active-grimoire directory guard, the
optional subagent review-lane protocol, and the skill-orphan reconcile step.

Skills are thin pointer files. Source `SKILL.md` files use placeholders such
as `{{SKILL_PREFIX}}` and `{{ARCANA_PATH}}`; `rites/register_skills.py`
substitutes them when installing skills into agent directories.

### Arcana-shipped skills

| Skill | Purpose |
|---|---|
| `/arc-improve` | Maintainer workflow for improving Arcana itself through validation plus architecture, rite, and documentation quality review. |
| `/arc-validate-all` | Run the full Arcana validator suite. |
| `/arc-validate-doc-trees` | Validate that ASCII directory diagrams in Arcana docs match the filesystem. |
| `/arc-validate-encoding` | Validate UTF-8, LF line endings, BOMs, mojibake markers, and repair artifacts in Arcana. |
| `/arc-validate-format` | Validate Markdown formatting in Arcana. |
| `/arc-validate-frontmatter` | Validate Arcana page frontmatter. |
| `/arc-validate-links` | Validate Arcana links and layer-aware internal page style. |
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
| `/arc-workspace-clean` | Remove temporary rite artifacts under Arcana's `rites/.artifacts`. |
| `/arc-help` | Display the Arcana skill catalog and installed grimoire skill guide. |

### Universal grimoire skills

| Skill | Purpose |
|---|---|
| `/grm-help` | Show the `/grm-*` command family and the active grimoire's own skills; the grimoire-author counterpart to `/arc-help`. |
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
| `/grm-validate-all` | Run the full deterministic validator profile against the active grimoire. |
| `/grm-validate-boundaries` | Ensure grimoires do not use Arcana-only system terminology. |
| `/grm-validate-doc-trees` | Validate that ASCII directory diagrams in the active grimoire match the filesystem. |
| `/grm-validate-encoding` | Validate UTF-8/LF policy in the active grimoire. |
| `/grm-validate-format` | Validate Markdown formatting in the active grimoire. |
| `/grm-validate-frontmatter` | Validate page frontmatter in the active grimoire. |
| `/grm-validate-links` | Validate links and layer-aware internal page style in the active grimoire. |
| `/grm-validate-orphans` | Detect orphan pages in the active grimoire. |
| `/grm-validate-portability` | Validate filesystem portability in the active grimoire. |
| `/grm-validate-provenance` | Validate source provenance in the active grimoire. |
| `/grm-validate-structure` | Validate grimoire structure and Arcana-managed scaffold files. |

Focused Arcana validators and grimoire validators are separate skills. The
aggregate `/arc-validate-all` is the default Arcana validation entry point;
`/grm-validate-all` is the default active-grimoire mechanical validation entry
point.

### Validated contracts

Several machine-readable contracts are the single source of truth for their
domains and are cross-checked against the repository by rites and tests:

- `rites/data/validators.json` - the Arcana and grimoire validator sequences
  that `rites/validate.py` runs.
- `rites/data/command_surface.json` - every public command mapped to its skill
  source, invocation, workflow owner, guard, mutation profile, and validation
  profile.
- `rites/data/rite_profiles.json` - the plan/apply/append/idempotency profile of
  every write-capable rite, cross-checked against an AST write-detector.
- `rites/data/summon_contract.json` - the Summoning Rite's modes, pipeline,
  release assets, and bootstrap environment variables.
- `rites/data/agent_targets.json` - the agent instruction files and
  skill-registration modes Arcana writes to.
- `formulae/grimoire/scaffold_contract.json` - the grimoire scaffold inventory
  consumed by creation, audit, validation, and tests.

`/arc-validate-skill-refs` asserts that a rite-owned command's mutation profile
matches its rite profile, keeping the command-surface and rite-profile contracts
aligned.

### Structured rite output

Two reporters in `rites/diagnostics.py` give every rite a machine-readable
interface alongside its human output. Validators emit findings through
`DiagnosticReporter`. The mutating rites - `append_log`, `new_page`,
`repair_links`, `sync_library`, `adopt_grimoire`, `clean_artifacts`,
`register_skills`, and the summon state surface - emit an outcome envelope
through `ResultReporter`
(`rite`, `status`, `mode`, `summary`, `mutations`, `messages`) under
`--format human|json|jsonl`. A `mutation` is a change made on disk: plan and
dry-run modes record none and report pending work through `messages` and summary
counts, so an orchestrator can run a rite and verify the outcome instead of
parsing prose. Human output and exit codes are independent of the format flag.

### Validation suite

Mechanical rites are independently invocable and orchestrated by
`rites/validate.py`, which loads its validator sequences from
`rites/data/validators.json`:

- `validate_structure` - Arcana layout, required hub files, and documentation
  index coverage (every `docs/*.md` and `CONTRIBUTING.md` is reachable from both
  routing surfaces, `arcana.md` and `README.md`, so a new doc never drifts out
  of the primer).
- `validate_grimoire_structure` - grimoire layout, manifest schema, the
  folder-named hub if-and-only-if (folder-named pages declare `type: hub` and
  hubs are folder-named), Obsidian app settings, and Arcana-managed scaffold
  compliance.
- `validate_naming` - snake_case paths, kebab-case skill slugs, and
  command-family skill schema.
- `validate_format` - Markdown formatting, invocation/formula shape, hub
  length, unclosed fences, and invalid tree branch markers.
- `validate_frontmatter` - page schema compliance.
- `validate_links` - canonical page wikilinks plus external, anchor, and non-page Markdown links.
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
- `validate_doc_trees` - ASCII directory diagrams in docs and hubs match the
  actual filesystem.

The orchestrator runs sequentially, in parallel, or in smart mode against
working-tree changes. Smart mode reads `git diff --name-status`, so deleting a
required file still selects the structure and reference validators.

### Maintenance model

`/arc-improve` is Arcana's maintainer entry point. It starts with the
mechanical validator suite, then runs judgment-based quality passes for:

- Whole-repository architecture: layout, naming, source-of-truth boundaries,
  AI-agent read paths, scalability, and future maintainability.
- Rite quality: script purpose, error handling, exit codes, idempotency,
  portability, and auditability.
- Documentation quality: duplication, clarity, canonical homes, generated
  views, and user-facing navigation.
- Contract coherence
  (`invocations/arcana/quality/audit_contract_coherence.md`): a subagent reads
  each rite and asserts that the free-text contract fields in
  `command_surface.json` and `rite_profiles.json` are true of the code -
  behaviorally probing the `ResultReporter`-wired rites via `--format json` on
  disposable temp targets - the semantic layer the mechanical validators cannot
  reach. Prose-wrong claims are corrected in the contract JSON; code-wrong
  findings defer to the rite-quality pass.

The architecture pass lives in
`invocations/arcana/quality/review_architecture.md`. It treats every Arcana
surface as in scope: root files, docs, invocations, formulae, rites, skills,
tests, release automation, Obsidian settings, and resources.

The judgment-based analysis passes of `/arc-improve`, `/grm-improve`, and
`/grm-lint` may optionally fan out into isolated read-only review lanes when
subagents are available (the shared contract in
`invocations/meta/subagent_lanes.md`), falling back to the linear flow
otherwise; the orchestrator always keeps apply, confirmation, and log phases.
`docs/governance.md` defines an autonomous-maintainer contract: a four-part gate
(deterministic, verifiable, non-destructive, not on the sign-off list) bounds
what an agent may do unattended, with library/skill writes and large changes
propose-then-confirm and semver bumps, breaking changes, deprecations, and
deletions reserved for a human.

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
- The injector treats the block as present when either the
  `## Grimoire Knowledge Base` heading or the BEGIN/END markers are found, so a
  re-run never double-injects; the same sentinels drive the summon drift detector.
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
  It writes the reconciled `library.json` under a compare-and-swap: reconciling
  the library is a read-modify-write, so if the file changed since it was read
  the rite re-reads, rebuilds, and retries, and a persistent conflict fails
  loudly - a concurrent sync or adopt is never silently clobbered.
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
4. Prefer the release binary on every platform (Linux, macOS, Windows); source
   mode is the automatic fallback when any release step fails, and
   `GRIMOIRE_SUMMON_BINARY=never` forces it.
5. Probe Dear PyGui/OpenGL startup before opening the source GUI; fall back to
   CLI on failure.
6. Read prompts from the controlling terminal when launched through
   `curl | bash`.
7. Install Python, pip, and Dear PyGui only after explicit confirmation.
8. Discover grimoires from explicit GitHub or GitLab scopes.
9. Clone Arcana and selected grimoires under `~/grimoires/`.
10. Write `~/grimoires/library.json`.
11. Inject the marked Grimoire instruction block into agent instruction files.
12. Run skill registration even when no domain grimoires are selected.

The bootstrap includes release-asset progress, byte-count reporting, explicit
retry logs, connection/stall safeguards, Python download fallback for flaky
Git Bash curl/wget behavior, and normalized LF checksum files. Windows Git
Bash platforms (`MINGW*`, `MSYS*`, `CYGWIN*`) resolve to the Windows `.zip`
asset and run `grimoire-summon.exe`.

The implementation is split for auditability:

- `rites/summon.py` - dispatcher and mode selection.
- `rites/summon_core.py` - pure-stdlib install engine.
- `rites/summon_gui.py` - Dear PyGui front end.
- `rites/summon_state.py` - agent-legible state surface.

`python3 rites/summon.py --check` reports Arcana, library, agent-block, and skill
drift read-only (exit 1 on drift); `--reconcile [--apply] [--prune]` reconciles
the local library and re-registers skills, refusing a base that fails
`validate.py` and recording every library removal as a mutation. Both emit the
`ResultReporter` envelope under `--format json|jsonl`, and every install, check,
and reconcile writes a transcript to `~/.cache/grimoire/summon-last.json` (steps,
`final_state`, and tier-tagged `next_actions`) so an orchestrator can diff intent
against outcome. The mode is registered in `summon_contract.json`
(`agent_reconcile`) and backs the offline core of `RECOVERY.md`; the agent block
is reported, never rewritten, and detected by either the heading or the
BEGIN/END markers.

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
- `docs/command_surface.md` - public command-surface contract.
- `docs/rite_profiles.md` - mutating-rite profile contract.
- `docs/summoning_contract.md` - Summoning Rite behavior contract.
- `docs/agent_targets.md` - agent target and skill-registration registry.
- `docs/architecture_backlog.md` - deferred architecture work queue.
- `docs/skills.md` - generated Arcana skill catalog.
- `RECOVERY.md` - stable recovery bridge for stale installations.
- `invocations/arcana/quality/review_architecture.md` - judgment-based
  whole-repo architecture review used by `/arc-improve`.
- Installation and scaffold docs identify both `/arc-*` and `/grm-*` skill
  sets, and placeholder examples use the canonical cooking, HR, and Project
  Alpha names.
- `/grm-validate-structure` and `/grm-improve` treat `.obsidian/graph.json` as
  managed scaffold alongside `.obsidian/app.json`, preserving the opinionated
  Obsidian graph-view color groups during grimoire audits and upgrade checks.
- The `/arc-improve` architecture review follows a repeatable S-tier protocol:
  parallel review lanes, synthesis, AI read-path tracing, and deferred
  architecture opportunities.
- Public validator skills route through invocation leaves, and `/grm-create`
  copies the managed Obsidian scaffold files.

### Public readiness

- `LICENSE` - MIT.
- `CONTRIBUTING.md` - contributor onramp.
- `pyproject.toml` - pure-stdlib runtime (Python 3.10+) with optional `[dev]`,
  `[gui]`, and `[build]` extras.
- `tests/` - pytest suite with fixture grimoires and validator coverage,
  including a generative negative-coverage gate: every validator carries a
  minimal violating fixture (base64-encoded so the spec stays inert to validators
  that scan `tests/`), and a completeness check fails unless every diagnostic
  code a validator can emit is triggered by a fixture or a documented allowlist.
- An invocation eval tier (`tests/eval_harness.py`, `docs/evals.md`) gives the
  judgment-half playbooks model-in-the-loop behavioral coverage through an
  injectable model seam: deterministic scaffolding runs in the fast gate with no
  model, while the model run is opt-in behind a `pytest` `eval` marker (deselected
  by default) and `ARCANA_EVAL_MODEL`, never reached by `rites/validate.py`.
- `.github/workflows/ci.yml` - runs the test suite and validator orchestrator on
  pull requests and pushes to main.
- `.github/workflows/summon-release.yml` - release binary build workflow.
- `.gitattributes` and `.editorconfig` - repository text-file policy.
