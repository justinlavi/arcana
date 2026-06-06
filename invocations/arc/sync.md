---
type: playbook
title: "Sync Arcana Environment"
aliases: ["sync", "arc-sync"]
tags: [arcana/invocations, type/playbook, scope/arcana]
authority: grimoire
last_verified: 2026-06-05
---

# Invocation: Sync Arcana Environment

## Purpose

Sync the local environment to current Arcana. One command, three scopes, selected
by a single positional sub-target so the platform-wide surfaces (the home library
and user agent files) stay distinct from the active-grimoire surface:

- `skills` — register Arcana-shipped skills and every installed grimoire's skills
  into supported agent skill directories. Rite: `rites/sync_skills.py`.
- `library` — reconcile `~/grimoires/library.json` against the actual state of
  `~/grimoires/`. Rite: `rites/sync_library.py`.
- `agentfile` — create or refresh the marked Grimoire routing block inside user
  agent instruction files. Rite: `rites/inject_agent_file.py` for the deterministic
  cases (create a missing file, refresh one clean marked region); judgment edit for
  the review cases (a file with no block, a pre-marker block, or malformed markers)
  and project-level files.

For the everyday user mirror of this command — active-grimoire skills plus the
library and agent files for the user's own setup — use `/grm-sync` instead.

## Invocation

```
/arc-sync skills
/arc-sync library
/arc-sync agentfile
```

## Routing

Read the positional sub-target and run only that section below.

- **No sub-target given:** do not run anything. Tell the user the sub-target is
  required and list `skills`, `library`, and `agentfile` with a one-line summary of
  each, then ask which to run. Never default to "all": `agentfile` rewrites user
  agent instruction files and stays opt-in, so a bare `/arc-sync` must never act.
- **Unknown sub-target:** report it and list the three valid sub-targets.

---

## Sub-target: `skills`

Mutation profile: `plan_apply` via `rites/sync_skills.py`. Apply directly when the
user asks to sync skills; use `--dry-run` for a preview or when reviewing target
changes. The plan reports creates, updates, stale cleanups, and collisions. The
`arc-`, `grm-`, and grimoire prefixes are Arcana-owned namespaces: any directory
under one of them that is not in the current catalog is a stale Arcana skill and is
removed or overwritten - no ownership marker required. Directories outside every
managed prefix are never touched, so a re-register never leaves a deprecated
`/arc-*` or `/grm-*` skill behind while leaving the user's own skills alone.

For major Arcana command-family changes, use `--reset-managed` to clear the managed
namespaces entirely and write the current catalog fresh.

### 1. Run the sync rite

```bash
python3 ARCANA_HOME/rites/sync_skills.py
```

On Windows, use `python` instead of `python3`.

### 2. Report the result

Tell the user how many skills were registered, how many stale skills were cleaned,
any collisions, and which agent targets were written.

### 3. Optional flags

```bash
python3 ARCANA_HOME/rites/sync_skills.py --dry-run                  # preview, no writes
python3 ARCANA_HOME/rites/sync_skills.py --reset-managed --dry-run  # preview a managed-namespace reset
python3 ARCANA_HOME/rites/sync_skills.py --reset-managed            # replace managed namespaces, register fresh
python3 ARCANA_HOME/rites/sync_skills.py --agent codex              # target one supported agent
python3 ARCANA_HOME/rites/sync_skills.py --agent claude
```

Supported `--agent` values come from `ARCANA_HOME/rites/data/agent_targets.json`;
see `ARCANA_HOME/docs/agent_targets.md` for the human-readable matrix.

Add `--format json` (or `jsonl`) for the shared `ResultReporter` outcome envelope -
registered/cleaned mutations and collisions as messages, and summary counts - so an
orchestrator can verify the result instead of parsing prose.

---

## Sub-target: `library`

Mutation profile: `plan_apply` via `rites/sync_library.py`. Reconcile the local
grimoire library (`~/grimoires/library.json`) against the actual state of
`~/grimoires/`. The rite walks the home directory, identifies every valid grimoire,
and reports missing, stale, mismatched, and unmanaged entries.

### 1. Run a dry-run report first

```bash
python3 ARCANA_HOME/rites/sync_library.py
```

### 2. Show the report

Call out:

- Missing, stale, or mismatched entries, which the rite can fix with `--apply`.
- Unmanaged directories, which need either `/arc-adopt` or manual cleanup.
- Skill prefix collisions, which would overwrite each other during skill registration.

### 3. Apply fixes only when requested

```bash
python3 ARCANA_HOME/rites/sync_library.py --apply
```

### 4. Sync skills after successful changes

Run `/arc-sync skills` (or `python3 ARCANA_HOME/rites/sync_skills.py`) to pick up
any newly registered grimoires.

### Notes

- Arcana itself is excluded from the library scan; it is the engine, not a grimoire.
- An unmanaged directory will not be auto-registered. To register it, use
  `/arc-adopt`, add a valid `grimoire.json`, or move it out of `~/grimoires/`.
- The rite preserves unknown fields on existing library entries and only updates
  `local_path` and `online_path`.
- Library entries are sorted alphabetically by key on write.
- `--home /path/to/alt/home` is available for testing.

---

## Sub-target: `agentfile`

Mutation profile: `plan_apply` via `rites/inject_agent_file.py` for the automatic
instruction targets, with a judgment edit for the cases a rite cannot safely
decide. Create or refresh the marked Grimoire routing block, preserving all
non-Grimoire content. Canonical block: `ARCANA_HOME/rites/templates/grimoire_block.md`.

### 1. Run the rite on the automatic targets

```bash
python3 ARCANA_HOME/rites/inject_agent_file.py            # plan: classify each target
python3 ARCANA_HOME/rites/inject_agent_file.py --apply    # create / refresh
```

The routing block is defined solely by its `<!-- BEGIN GRIMOIRE KNOWLEDGE BASE -->`
and `<!-- END GRIMOIRE KNOWLEDGE BASE -->` markers. The rite reads the
`instruction_mode: auto` targets from `ARCANA_HOME/rites/data/agent_targets.json`
and classifies each from those markers: a missing file is **created** with
`# <title>` and the block; a single clean marked region is **refreshed** in place
(idempotent — a block already matching the template is left unchanged); anything
else — a file with no block, a pre-marker block, or duplicate/malformed markers —
is reported for **review** and left untouched. Creating a missing automatic target
is deterministic and is the desired recovery for a deleted agent file. Target one
agent with `--agent claude|codex`; add `--format json` for the structured envelope.

### 2. Resolve review and out-of-registry files by judgment

The rite hands two kinds of file to judgment. Handle them by hand:

- **Review automatic targets** the rite reported — a file with no block, a
  pre-marker `## Grimoire Knowledge Base` section, or duplicate/malformed markers.
- **User-specified or project-level files** not in the automatic registry — for
  example a repository `AGENTS.md`, `CLAUDE.md`, or
  `.github/copilot_instructions.md`. Mention these as candidates but do not edit a
  project-level file without explicit user confirmation.

For each such file, care only about the marked region: if there is a routing block
in any form (a malformed marked region, or a pre-marker `## Grimoire Knowledge Base`
section), replace it with the canonical block; if there is none, insert the block
after the first top-level heading or append it; if the file's intent is unclear,
stop and ask. Never rewrite, sort, reflow, or deduplicate the content outside the
markers — the user's own instructions live there. Do not scan all of `$HOME`; if
the user asks for "everything on this machine", confirm a bounded search first.

### 3. Review

Re-read each file the rite or the judgment edit touched, confirm exactly one
Grimoire routing block is present and the canonical text appears once, and summarize each
file as `created`, `inserted`, `refreshed`, `skipped`, or `needs user decision`.

This sub-target updates instruction files only. If newly added skills also need to
appear in slash-command pickers, run `/arc-sync skills` separately.

## Related

- User mirror (active-grimoire skills plus library and agent files for the user's own setup): [[invocations/grm/sync|sync]]
- Adopt an unmanaged directory: [[invocations/arc/adopt|adopt]]
- Agent targets: [[docs/agent_targets|agent targets]]
- Agent configuration: [[docs/agent_configuration|agent configuration]]
- Canonical block: `ARCANA_HOME/rites/templates/grimoire_block.md`
