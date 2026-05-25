---
name: {{SKILL_PREFIX}}-library-sync
description: Scan ~/grimoires/ for valid grimoires and reconcile against the local library (detect missing, stale, mismatched, and unmanaged entries)
when_to_use: User cloned, moved, or removed a grimoire by hand; agent can't find a grimoire that should be installed; library mentions a grimoire that doesn't exist on disk; user mentions "library drift", "missing grimoire", "unmanaged directory", or "after manual git changes in ~/grimoires/". Defaults to a dry-run report; only writes when --apply is passed.
user-invocable: true
allowed-tools: Bash Read
---

# Sync Grimoire Library

You are reconciling the local grimoire library (`~/grimoires/library.json`) against the actual state of `~/grimoires/`.

## Context

- **Arcana**: `{{ARCANA_PATH}}`
- **Invocation**: `{{ARCANA_PATH}}/invocations/library/sync.md`

## Invocation

!`cat {{ARCANA_PATH}}/invocations/library/sync.md`
