---
type: reference
title: "Summoning Rite Contract"
aliases: ["summon-contract", "summoning-contract", "installer-contract"]
tags: [type/reference, arcana/docs, scope/install]
authority: grimoire
last_verified: 2026-11-11
---

# Summoning Rite Contract

## Purpose

The Summoning Rite installs Arcana, optionally discovers and clones grimoires,
updates local routing state, configures supported agents, and registers skills.
It is terminal-only and runs from source on a stock Python; the agent holds
the onboarding conversation through `/grm-setup`.

The machine-readable source is
[`rites/data/summon_contract.json`](../rites/data/summon_contract.json).
This page is the human reading path for that contract.

## Ownership

| Surface | Role | Required behavior |
|---|---|---|
| `rites/summon.sh` | Shell bootstrap | Find Python 3.10+ (install only with consent), fetch the dispatcher and its companion files when run from the public one-liner, and pass arguments to Python. A local checkout uses its own files. |
| `rites/summon.py` | Dispatcher | Run the terminal installer; route `--check`, `--reconcile`, and `--update` to the state surface when it is available. |
| `rites/summon_core.py` | Install engine | Own git checks, discovery, Arcana install/update, grimoire install/update, library writes, agent block injection, skill registration, and the terminal summary. |
| `rites/summon_state.py` | Agent-legible state surface | Own `--check`/`--reconcile`/`--update`, the install/check/reconcile transcript, and the offline reconciliation that backs [Update](../UPDATE.md). |

## Required Pipeline

Every install path must preserve this order:

1. Check `git`.
2. Install or update Arcana.
3. Optionally discover grimoires from a GitHub/GitLab scope.
4. Optionally install selected grimoires.
5. Update `~/grimoires/library.json` for installed grimoires.
6. Inject supported agent routing blocks.
7. Register Arcana and grimoire skills.
8. Report completion or update instructions.

## Source Selection

The public piped one-liner downloads the dispatcher, the install engine, the
agent-target registry, and the routing block template into a temporary
directory and runs them. A local checkout (`bash rites/summon.sh` from inside
Arcana) uses the working tree, which keeps development loops pointed at it.

## Bootstrap Environment Controls

The canonical set of environment variables the shell bootstrap honors (mirrors
`bootstrap_environment` in `rites/data/summon_contract.json`). `installation.md`
links here rather than restating these.

| Variable | Purpose |
|---|---|
| `ARCANA_URL` | Override the Arcana repository URL. |
| `ARCANA_REF` | Branch or tag of Arcana to bootstrap: the companion-script downloads and the engine clone both use it. |
| `GRIMOIRE_SUMMON_DOWNLOAD_ATTEMPTS` | Companion-script download retry count. |
| `GRIMOIRE_SUMMON_RETRY_DELAY` | Delay (seconds) between download attempts. |
| `GRIMOIRE_SUMMON_CONNECT_TIMEOUT` | Connection timeout (seconds) for downloads. |

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
`~/.cache/grimoire/summon-last.json` - the stdout envelope as a superset, plus
`operation`, `run_id`, `started_at`/`ended_at`, `steps`, and `final_state` - so a
later session can diff intent against outcome.

Boundaries the surface keeps:

- **Refuses to reconcile a broken base** - `--apply` runs `validate.py` first and
  reports `blocked` if Arcana is red (mirrors [Update](../UPDATE.md) step 2).
- **No silent deletion** - stale library entries are preserved unless `--prune`;
  each removal is recorded as a mutation.
- **Agent blocks are reconciled deterministically** - a routing block is matched
  solely by its BEGIN/END markers; an absent or block-less file is created or has
  a block inserted, and one clean marked region is refreshed in place. A
  block-like file that is not one clean region (duplicate or malformed markers, or
  a pre-marker heading-only block) is left untouched and reported for the
  `/grm-update agentfile` (maintainer: `/arc-update agentfile`) judgment edit, so a
  second block is never appended.
- **Network pull is out of scope** - updating Arcana itself stays the human step
  from [Update](../UPDATE.md).

## Review Checklist

Before changing summon behavior:

- Update `rites/data/summon_contract.json` when a summon mode, environment
  variable, or required pipeline step changes.
- Confirm the terminal install path and the state surface still use the same
  core primitives for discovery, install, library update, agent configuration,
  and skill registration.
- Confirm the piped bootstrap still fetches exactly the companion files the
  dispatcher needs.
- Run `python -m pytest tests/test_summon_core.py tests/test_summon_contract.py tests/test_summon_state.py`.

## Related

- [installation](installation.md)
- [release](release.md)
- [agent configuration](agent_configuration.md)
