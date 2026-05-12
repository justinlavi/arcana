# Changelog

Arcana is still pre-1.0. This changelog tracks only meaningful changes made while preparing the first public Arcana release.

Historical notes from earlier private GitLab iterations were intentionally removed because they no longer describe this repository's public release history.

## [Unreleased]

### Added
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

### Removed
- `rites/summon.bat`; Windows users can use Git Bash or WSL for the shell bootstrap, and Windows release binaries are still produced.
