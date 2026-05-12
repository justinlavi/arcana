# Changelog

Arcana is still pre-1.0. This changelog tracks only meaningful changes made while preparing the first public Arcana release.

Historical notes from earlier private GitLab iterations were intentionally removed because they no longer describe this repository's public release history.

## [Unreleased]

### Added
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

### Removed
- `rites/summon.bat`; Windows users can use Git Bash or WSL for the shell bootstrap, and Windows release binaries are still produced.
