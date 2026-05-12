# Changelog

Arcana is still pre-1.0. This changelog tracks only meaningful changes made while preparing the first public Arcana release.

Historical notes from earlier private GitLab iterations were intentionally removed because they no longer describe this repository's public release history.

## [Unreleased]

### Added
- Comprehensive Arcana audit cleanup (Tier 1 + Tier 2):
  - **Single-source skill catalog**: new `rites/sync_docs.py` generator emits `docs/skills.md` from each `skills/<slug>/SKILL.md` frontmatter. INDEX.md, README.md, agent_configuration.md, and reference.md no longer enumerate skills — they all link to the canonical catalog.
  - **Single-source instruction block**: the canonical Grimoire instruction text now lives at `rites/templates/grimoire_block.md`. `summon.py` reads it at runtime instead of embedding it; `agent_configuration.md` references it instead of inlining.
  - **7 new validator skills** exposing what was previously buried inside `/grm-arcana-improve`:
    - `/grm-arcana-validate-format`, `-links`, `-naming`, `-security`, `-semantics`, `-structure`, `-all` (the `validate-all` skill drives `rites/validate.py` orchestrator).
  - **Doc reorganization**: extracted summoning + manual install into a dedicated `docs/installation.md`. `agent_configuration.md` is now focused on per-agent setup. Catalog and grimoire.json schemas moved into `docs/reference.md`. README trimmed to "what + why + where to read next." Quickstart refocused as a 5-minute smoke test (install procedure no longer duplicated).
  - **Quality invocations consolidated**: merged `quality/detect_duplication.md` into a leaner `quality/improve_documentation.md` covering both duplication and clarity audits.
  - **Validator contract fix**: `rites/validate_semantics.py` now actually performs the deprecated-term scan its invocation always promised. Deprecated-term list moved to single-source data file at `rites/data/deprecated_terms.txt`.
- Catalog sync rite and skill:
  - `rites/sync_catalog.py` walks `~/grimoire/`, classifies every subdirectory by manifest validity, and diffs the result against `~/grimoire/catalog.json`.
  - Reports four kinds of drift (missing, stale, mismatched, unmanaged) plus structural warnings (namespace collisions, name/directory mismatches).
  - Defaults to a dry-run report; `--apply` writes the reconciled catalog with deterministic alphabetical ordering and preserves unknown fields on existing entries.
  - Exposed as `/grm-catalog-sync` for AI-driven maintenance.
- Release-first Summoning Rite bootstrap:
  - Public curl flow downloads `rites/summon.sh`, then prefers GitHub Release binaries.
  - Release binary downloads are checksum-verified before execution.
  - Python source bootstrap remains available as a fallback.
- PyInstaller release infrastructure for `grimoire-summon` binaries:
  - `rites/build_summon_binary.py`
  - `requirements-summon-build.txt`
  - `.github/workflows/summon-release.yml`
  - `docs/release.md`
- Dear PyGui app mode for the Summoning Rite.
- Smarter grimoire discovery:
  - Direct GitHub/GitLab repository URLs are trusted explicitly.
  - Namespace discovery supports `-grimoire` names, `grimoire` topics/tags, and description metadata.
- Release controls for bootstrap testing:
  - `GRIMOIRE_SUMMON_BINARY`
  - `GRIMOIRE_SUMMON_RELEASE_TAG`
- Focused `.gitignore` for Arcana-local editor noise, Python caches, build output, validation artifacts, logs, and temporary files.

### Changed
- `rites/summon.sh` is the single supported bootstrap entry point.
- Public setup documentation now describes the release-first binary workflow and source fallback.
- Summoning Rite GUI dependency handling now uses a Grimoire-managed dependency cache when source fallback is needed.
- Skill registration now uses explicit namespace roots plus functional subcommands:
  - Arcana commands use `grm-<area>-<action>`.
  - Domain grimoire commands use the namespace declared in the grimoire's own `grimoire.json`, such as `jpn-travel-create-trip`.
  - Source `SKILL.md` files use `name: {{NAMESPACE}}-<slug>`; the registration rite substitutes `{{NAMESPACE}}` with the grimoire's declared namespace at install time.
- Grimoire identity is now self-declared in a `grimoire.json` manifest at each grimoire's root (Arcana included). Fields: `name`, `namespace`, `description`. The catalog (`~/grimoire/catalog.json` and the global Arcana catalog) is now a pure registry — it records *where* grimoires live, not what they're named or how they're prefixed.

### Removed (breaking)
- `skill_namespace` field in catalog entries. Move it into each grimoire's `grimoire.json` as `namespace`. The registration rite no longer reads it from the catalog. No compatibility shim.
- `rites/analyze_health.py` — orphaned dead code with no entry point.
- `invocations/arcana/quality/detect_duplication.md` — merged into `quality/improve_documentation.md`.
- Inlined skill list duplicates in `INDEX.md`, `README.md`, `docs/reference.md`, `docs/agent_configuration.md`. Replaced by links to the canonical `docs/skills.md`.
- Inlined Grimoire instruction block duplicates in `docs/agent_configuration.md` (the verbatim copy and the diverged Copilot variant). Replaced by references to `rites/templates/grimoire_block.md`.

### Removed
- `rites/summon.bat`; Windows users can use Git Bash or WSL for the shell bootstrap, and Windows release binaries are still produced.
