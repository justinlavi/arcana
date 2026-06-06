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
| `rites/summon_state.py` | Agent-legible state surface | Own `--check`/`--reconcile`, the install/check/reconcile transcript, and the offline reconciliation that backs [Update](../UPDATE.md). |
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
6. Inject supported agent routing blocks.
7. Register Arcana and grimoire skills.
8. Report completion or update instructions.

The GUI may let the user skip selected agent targets or skill registration via
settings, but the default GUI path should match the CLI post-install shape.

## Release And Source Selection

Public piped shell installs are release-first by default on every platform —
Linux, macOS, and Windows alike. The bootstrap tries the matching release
archive, verifies its checksum, extracts it, and runs the binary. If any release
step fails (download, checksum, extraction, or execution), it falls back to
Python source. Set `GRIMOIRE_SUMMON_BINARY=never` to force source mode, or
`always` to skip the local-source shortcut below.

Local checkout runs use local source by default. This keeps Arcana development
loops pointed at the working tree.

## Bootstrap Environment Controls

The canonical set of environment variables the shell bootstrap honors (mirrors
`bootstrap_environment` in `rites/data/summon_contract.json`). `installation.md`
and `release.md` link here rather than restating these.

| Variable | Purpose |
|---|---|
| `ARCANA_URL` | Override the Arcana repository URL. |
| `ARCANA_REF` | Override the raw-source ref for companion-script downloads. |
| `GRIMOIRE_SUMMON_BINARY` | Release-binary behavior: `auto` (default - release-first on every platform, source fallback; a local checkout uses source), `always` (force release-binary lookup), or `never` (force the Python source bootstrap). |
| `GRIMOIRE_SUMMON_RELEASE_TAG` | Download release assets from a specific tag instead of `latest`. |
| `GRIMOIRE_SUMMON_DOWNLOAD_ATTEMPTS` | Release and companion-script download retry count. |
| `GRIMOIRE_SUMMON_RETRY_DELAY` | Delay between download attempts. |
| `GRIMOIRE_SUMMON_CONNECT_TIMEOUT` | Connection timeout (seconds) for downloads. |
| `GRIMOIRE_SUMMON_STALL_TIMEOUT` | Stall timeout (seconds) before a slow download is aborted. |
| `GRIMOIRE_SUMMON_QUIET_STALL_TIMEOUT` | Stall timeout (seconds) for quiet downloads such as checksums and companion scripts. |
| `GRIMOIRE_SUMMON_MIN_SPEED` | Minimum download speed (bytes/sec) below which a transfer counts as stalled. |
| `GRIMOIRE_SUMMON_PY_DEPS` | Python dependency cache used by source GUI mode. |

When curl/wget cannot fetch a file after the configured attempts, the bootstrap
tries a Python `urllib` download fallback if Python is already on PATH.

## Agent-Legible State Surface

`rites/summon.py --check`, `--reconcile`, and `--update` route to
`rites/summon_state.py` instead of the interactive installer, giving an
orchestrator a machine-readable view of an installation. These run against the
installed Arcana checkout (`python3 rites/summon.py --check`), not the shell
bootstrap.

| Command | Effect | Exit code |
|---|---|---|
| `--check` (alias `--plan`) | Read-only: report Arcana, library, agent-block, and skill drift. | `0` in sync, `1` drift |
| `--reconcile` | Propose the offline repair (no writes). | `0` in sync, `1` drift |
| `--reconcile --apply` | Reconcile the library additively, sync skills, and create/insert/refresh the marked Grimoire routing block in each agent instruction file. | `0` converged, `1` error/blocked/residual |
| `--reconcile --apply --prune` | Also remove stale library entries (deletes them). | as above |
| `--update` | Fetch every library grimoire (branch-aware) and report currency; no writes. | `0` all current, `1` any behind/diverged/dirty/unreachable |
| `--update --apply` | Reconcile the library, fast-forward every clean grimoire that is behind, sync skills (reset), reconcile the agent routing blocks, and heal only the grimoires confirmed current. Grimoires it could not bring current (private-host auth, offline, dirty, diverged) are reported for manual pull and never modified. | `0` converged, `1` error/residual/needs-manual-pull |

Add `--format json` (or `jsonl`) for the shared
[`ResultReporter`](../rites/diagnostics.py) envelope; `--home` and
`--arcana-root` override the defaults.

`--home` scopes only the library scan and inspection. The transcript still lands
at `~/.cache/grimoire/summon-last.json` unless `--transcript-path` redirects it,
and `--reconcile --apply` re-registers skills into the agent directories under
your real home (`sync_skills.py` is home-global). Point `--home` at a sandbox
for read-only `--check`; use `--transcript-path` to keep its transcript local.

Every install, `--check`, and `--reconcile` writes a durable transcript to
`~/.cache/grimoire/summon-last.json` — the stdout envelope as a superset, plus
`operation`, `run_id`, `started_at`/`ended_at`, `steps`, and `final_state` — so a
later session can diff intent against outcome.

Boundaries the surface keeps:

- **Refuses to reconcile a broken base** — `--apply` runs `validate.py` first and
  reports `blocked` if Arcana is red (mirrors [Update](../UPDATE.md) step 4).
- **No silent deletion** — stale library entries are preserved unless `--prune`;
  each removal is recorded as a mutation.
- **Agent blocks are reconciled deterministically** — a routing block is matched
  solely by its BEGIN/END markers; an absent or block-less file is created or has
  a block inserted, and one clean marked region is refreshed in place. A
  block-like file that is not one clean region (duplicate or malformed markers, or
  a pre-marker heading-only block) is left untouched and reported for the
  `/grm-sync agentfile` (maintainer: `/arc-sync agentfile`) judgment edit, so a
  second block is never appended.
- **Network pull is out of scope** — updating Arcana itself stays the human step
  from [Update](../UPDATE.md).

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
- Run `python -m pytest tests/test_summon_core.py tests/test_summon_contract.py tests/test_summon_state.py`.

## Related

- [installation](installation.md)
- [release](release.md)
- [agent configuration](agent_configuration.md)
