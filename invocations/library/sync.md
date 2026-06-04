---
type: playbook
title: "Sync Grimoire Library"
aliases: ["library-sync", "sync-library"]
tags: [arcana/invocations, type/playbook, scope/library]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Sync Grimoire Library

## Purpose

Reconcile the local grimoire library (`~/grimoires/library.json`) against the actual state of `~/grimoires/`. The rite walks the home directory, identifies every valid grimoire, and reports missing, stale, mismatched, and unmanaged entries.

## Invocation

```
/arc-library-sync
```

## Workflow

### 1. Run a dry-run report first

```bash
python3 ARCANA_HOME/rites/sync_library.py
```

### 2. Show the report

Call out:

- Missing, stale, or mismatched entries, which the rite can fix with `--apply`.
- Unmanaged directories, which need either `/arc-library-adopt` or manual cleanup.
- Skill prefix collisions, which would overwrite each other during skill registration.

### 3. Apply fixes only when requested

```bash
python3 ARCANA_HOME/rites/sync_library.py --apply
```

### 4. Sync skills after successful changes

```bash
python3 ARCANA_HOME/rites/register_skills.py
```

Or invoke `/arc-agent-sync-skills`.

## Notes

- Arcana itself is excluded from the library scan; it is the engine, not a grimoire.
- An unmanaged directory will not be auto-registered. To register it, use `/arc-library-adopt`, add a valid `grimoire.json`, or move it out of `~/grimoires/`.
- The rite preserves unknown fields on existing library entries and only updates `local_path` and `online_path`.
- Library entries are sorted alphabetically by key on write.
- `--home /path/to/alt/home` is available for testing.

## Related

- Adopt unmanaged directory: [[invocations/library/adopt|adopt]]
- Global skill sync: [[invocations/agent/sync_skills|sync skills]]
