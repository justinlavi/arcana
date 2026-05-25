---
type: reference
title: "Summoning Rite Contract"
aliases: ["summon-contract", "summoning-contract", "installer-contract"]
tags: [type/reference, arcana/docs, scope/install]
authority: grimoire
last_verified: 2026-05-25
---

# Summoning Rite Contract

## Purpose

The Summoning Rite installs Arcana, optionally discovers and clones grimoires,
updates local routing state, configures supported agents, and registers skills.
Its behavior spans shell bootstrap, Python CLI, Python GUI, release binary, and
GitHub Actions release paths.

The machine-readable source is
[`rites/data/summon_contract.json`](../rites/data/summon_contract.json).
This page is the human reading path for that contract.

## Ownership

| Surface | Role | Required behavior |
|---|---|---|
| `rites/summon.sh` | Shell bootstrap | Select release or source mode, download companion scripts, verify release checksums, fall back to source, and pass arguments to Python. |
| `rites/summon.py` | Dispatcher | Choose GUI or CLI mode, respect `--cli` and `--gui`, and fall back to CLI when GUI startup fails. |
| `rites/summon_core.py` | Install engine | Own git checks, discovery, Arcana install/update, grimoire install/update, library writes, agent block injection, skill registration, and CLI summary. |
| `rites/summon_gui.py` | GUI frontend | Use core primitives from worker threads, honor settings, expose install/manage/settings/diagnostics views, and keep GUI-only concerns out of the install engine. |
| `rites/build_summon_binary.py` | Release builder | Build PyInstaller artifacts, bundle required resources/templates, archive per platform, and write checksums. |
| `.github/workflows/summon-release.yml` | Release workflow | Build each supported release platform and optionally create/update GitHub Release assets. |

## Required Pipeline

Every source install path, CLI or GUI, must preserve this install order:

1. Check `git`.
2. Install or update Arcana.
3. Optionally discover grimoires from a GitHub/GitLab scope.
4. Optionally install selected grimoires.
5. Update `~/grimoires/library.json` for installed grimoires.
6. Inject supported agent instruction blocks.
7. Register Arcana and grimoire skills.
8. Report completion or recovery instructions.

The GUI may let the user skip selected agent targets or skill registration via
settings, but the default GUI path should match the CLI post-install shape.

## Release And Source Selection

Public piped shell installs are release-first by default. The bootstrap tries
the matching release archive, verifies its checksum, extracts it, and runs the
binary. If any release step fails, it falls back to Python source.

Linux GUI sessions are source-first by default because frozen GUI/OpenGL
libraries drift across distributions. Set `GRIMOIRE_SUMMON_BINARY=always` to
test the Linux release binary directly, or `GRIMOIRE_SUMMON_BINARY=never` to
force source mode.

Local checkout runs use local source by default. This keeps Arcana development
loops pointed at the working tree.

## Review Checklist

Before publishing or changing summon behavior:

- Update `rites/data/summon_contract.json` when a summon mode, release asset,
  environment variable, or required pipeline step changes.
- Confirm CLI and GUI install paths still use the same core primitives for
  discovery, install, library update, agent configuration, and skill
  registration.
- Confirm the shell bootstrap still falls back to source after release
  download, checksum, extraction, or binary execution failure.
- Confirm release assets and checksums match the platform matrix in the
  contract.
- Run `python -m pytest tests/test_summon_core.py tests/test_summon_contract.py`.

## Related

- [Installation](installation.md)
- [Release](release.md)
- [Agent Configuration](agent_configuration.md)
