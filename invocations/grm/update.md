---
type: playbook
title: "Update"
aliases: ["update", "grm-update", "sync", "refresh-setup"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-11-12
---

# Invocation: Update (bring everything current)

## Purpose

One verb for "make my setup current". Bare, it runs the canonical Update
procedure: pull Arcana, validate it, pull every grimoire in the library,
re-register skills, refresh the agent routing blocks, and heal every grimoire
it confirmed current. With a scope it reconciles one local surface without
pulling anything, for the moments when only that surface drifted: a skill
missing from the picker, a grimoire folder moved by hand, a routing block
gone stale.

## Invocation

```
/grm-update              # everything: pull, validate, re-register, refresh, heal
/grm-update skills       # register Arcana's and the active grimoire's skills
/grm-update library      # reconcile ~/grimoires/library.json with the folders on disk
/grm-update agentfile    # create or refresh the Grimoire routing block in the agent files
```

## Preconditions

!`cat ARCANA_HOME/invocations/meta/grimoire_directory_guard.md`

The guard resolves `GRIMOIRE_ROOT` for the `skills` scope. The bare update,
`library`, and `agentfile` operate on the whole `~/grimoires/` home and the
user's agent files, so the current directory does not have to be a grimoire.

## Routing

Read the positional scope and run only its section.

---

## Bare: the full update

The canonical, skill-less procedure is **[[UPDATE|UPDATE]]** at the Arcana
root. Read it and follow the AI Update Playbook exactly: it resolves and
pulls Arcana, validates the source, then runs `summon.py --update --apply`,
which reconciles the library, pulls every grimoire (branch-aware, with a
manual-pull fallback for private hosts), re-registers skills, refreshes the
marked routing blocks, and heals only the grimoires it confirmed current.

```bash
cat ARCANA_HOME/UPDATE.md
```

Report from the rite envelopes, never from counts of your own: the
`grimoire_summary`, each grimoire's `status`, the `sync_skills` counts, and
every grimoire under `needs_manual_pull` verbatim, with the one-line
instruction to pull it by hand.

---

## Scope: `skills`

Mutation profile: `plan_apply` via `rites/sync_skills.py`.

```bash
ARCANA_HOME/bin/arcana sync_skills --grimoire GRIMOIRE_ROOT
```

Tell the user how many Arcana and active-grimoire skills were registered,
how many stale skills were cleaned, any collisions, and which agent targets
were written. The `arc-`, `grm-`, and grimoire prefixes are Arcana-owned
namespaces: a skill in one that is not in the current catalog is removed;
skills outside every managed prefix are never touched. Flags: `--dry-run`
(preview), `--reset-managed` (clear the managed namespaces and write the
catalog fresh), `--agent claude|codex`, `--format json`. Ask the user to open
a fresh agent session afterwards; agents cache skill listings.

---

## Scope: `library`

Mutation profile: `plan_apply` via `rites/sync_library.py`. The fix when a
grimoire folder was moved or renamed and the agent can no longer find it.

1. Report the drift: `ARCANA_HOME/bin/arcana sync_library`.
2. Call out missing, stale, and mismatched entries (fixable with `--apply`)
   and any unmanaged directory. An unmanaged directory has no
   `grimoire.json`: `/grm-setup <folder>` makes it a grimoire, or move it out
   of `~/grimoires/` if it is not one.
3. Apply on request: `ARCANA_HOME/bin/arcana sync_library --apply`,
   then run the `skills` scope so a newly resolved grimoire's skills register.

---

## Scope: `agentfile`

Mutation profile: `plan_apply` via `rites/inject_agent_file.py`. The fix when
the agent stopped following the library because its routing block went stale
or the file was deleted (a new machine, a removed `~/.codex/`).

1. Plan: `ARCANA_HOME/bin/arcana inject_agent_file`. The routing block
   is the region between `<!-- BEGIN GRIMOIRE KNOWLEDGE BASE -->` and
   `<!-- END GRIMOIRE KNOWLEDGE BASE -->`; the markers are the whole
   contract. A missing file is **created** with the block; one clean marked
   region is **refreshed** in place; anything else (no block, a pre-marker
   block, duplicate or malformed markers) is reported for **review** and left
   untouched.
2. Apply the deterministic actions:
   `ARCANA_HOME/bin/arcana inject_agent_file --apply`
   (`--agent claude|codex` for one target).
3. Resolve `review` targets by judgment, caring only about the marked region:
   replace any existing routing block in any form with the canonical block
   from `ARCANA_HOME/rites/templates/grimoire_block.md`; if there is none,
   insert the block after the first top-level heading or at the end. Preserve
   every line outside the markers exactly. Stop and ask if the file's intent
   is unclear, and never edit a project-level instruction file without
   confirmation.

---

## Related

- Canonical procedure: [[UPDATE|UPDATE]]
- Maintainer mirror (platform scope): [[invocations/arc/update|update]]
- First-time setup and joining a grimoire: [[invocations/grm/setup|setup]]
- Share your own changes: [[invocations/grm/save|save]]
- Agent targets: [[docs/agent_targets|agent targets]]
- Agent configuration: [[docs/agent_configuration|agent configuration]]
