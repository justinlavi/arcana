---
type: playbook
title: "Restore"
aliases: ["restore", "grm-restore", "restoration"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-06-02
---

# Invocation: Restore (grimoire + Arcana)

## Purpose

Bring the active grimoire and the Arcana it references back to a current, validated, synchronized state. This is the grimoire-prefix entry point to Arcana's canonical **Restoration** process — the one command a grimoire user runs to re-sync everything.

## Invocation

```
/grm-restore
```

## Procedure

The canonical, skill-less procedure is **[[RESTORATION|RESTORATION]]** at the Arcana root. Read it and follow the AI Restoration Playbook — it resolves Arcana, inspects and (if asked) pulls, reconciles the library, validates the source, resets and re-registers skills, refreshes the marked agent block, and brings the active grimoire current.

```bash
cat ARCANA_HOME/RESTORATION.md
```

## Notes

- Resolve the active grimoire from `~/grimoires/library.json` when the current directory is not a grimoire root.
- `/grm-restore` and `/arc-restore` are mirrors: both run the one `RESTORATION.md` procedure. Use `/grm-restore` from the grimoire-user side; `/arc-restore` is the Arcana-maintainer mirror.

## Related

- **Canonical procedure**: [[RESTORATION|RESTORATION]]
- **Arcana mirror**: [[invocations/arcana/restore|restore]]
