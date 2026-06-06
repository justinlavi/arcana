---
type: playbook
title: "Sync Active Grimoire Agent Skills"
aliases: ["sync-grimoire-skills", "refresh-active-grimoire-skills"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Sync Active Grimoire Agent Skills

## Purpose

Sync Arcana-shipped skills and the active grimoire's own skills into supported agent skill directories.

Use this day-to-day when the user is working inside one grimoire and has added, renamed, or edited that grimoire's `skills/` directory. It refreshes Arcana command families at the same time so the agent remains aligned after Arcana updates, but it does not scan or clean skills for every installed grimoire.

## Invocation

```
/grm-sync
```

## Preconditions

!`cat ARCANA_HOME/invocations/meta/grimoire_directory_guard.md`

## Workflow

Mutation profile: `plan_apply` via `rites/sync_skills.py`. This
invocation may apply directly when the user asks to sync active-grimoire
skills; use `--dry-run` when the user asks for a preview or when reviewing
target changes.
The plan reports creates, updates, owned stale cleanups, unowned preserves,
and collisions. Apply mode refuses to overwrite unowned skill directories.
Generated pointer skills without ownership metadata are rewritten when their
provenance points back to an Arcana or grimoire skill source.

For major Arcana command-family changes or stale active-grimoire command
families, use `--reset-managed` to replace Arcana's namespaces and the active
grimoire's skill prefix from current source. This is the supported version of
manually deleting old registered skill directories before re-registering.

### 1. Run the sync rite for the active grimoire

```bash
python3 ARCANA_HOME/rites/sync_skills.py --grimoire GRIMOIRE_ROOT
```

On Windows, use `python` instead of `python3`.

### 2. Report the result

Tell the user how many Arcana and active-grimoire skills were registered, how
many owned stale registrations were cleaned, how many unowned directories were
preserved, any collisions, and which agent targets were written.

### 3. Reconcile orphaned skill directories (optional)

If the rite reported `Preserve unowned` entries or `without Arcana ownership
marker` collisions under this grimoire's prefix, some may be stale Arcana
artifacts the rite could not prove it owns - most often a skill whose source was
renamed (`oly-standards-audit` -> `oly-audit-standards`) or removed, leaving the
old registration behind. Apply the propose-then-confirm judgment in
[[invocations/meta/skill_orphan_reconcile|skill orphan reconcile]] to classify
and, on one confirmation, remove them - then re-register. Skip this when the rite
reported no preserved or collided managed-prefix directories.

### 4. Optional flags

Preview without writing:

```bash
python3 ARCANA_HOME/rites/sync_skills.py --grimoire GRIMOIRE_ROOT --dry-run
```

Preview a managed-namespace reset:

```bash
python3 ARCANA_HOME/rites/sync_skills.py --grimoire GRIMOIRE_ROOT --reset-managed --dry-run
```

Replace managed namespaces and register fresh copies:

```bash
python3 ARCANA_HOME/rites/sync_skills.py --grimoire GRIMOIRE_ROOT --reset-managed
```

Target one supported agent:

```bash
python3 ARCANA_HOME/rites/sync_skills.py --grimoire GRIMOIRE_ROOT --agent codex
python3 ARCANA_HOME/rites/sync_skills.py --grimoire GRIMOIRE_ROOT --agent claude
```

Supported `--agent` values come from
`ARCANA_HOME/rites/data/agent_targets.json`; see
`ARCANA_HOME/docs/agent_targets.md` for the human-readable matrix.

Add `--format json` (or `jsonl`) for the shared `ResultReporter` outcome
envelope - registered/cleaned mutations, collisions and preserved-unowned dirs as
messages, and summary counts - so an orchestrator can verify the result instead
of parsing prose.

## Related

- Global skill sync: [[invocations/arc/sync|sync]]
- Reconcile stale/renamed skill orphans: [[invocations/meta/skill_orphan_reconcile|skill orphan reconcile]]
- Agent targets: [[docs/agent_targets|agent targets]]
- Agent configuration: [[docs/agent_configuration|agent configuration]]
