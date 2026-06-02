---
type: playbook
title: "Restore"
aliases: ["restore", "arc-restore", "restoration"]
tags: [arcana/invocations, type/playbook, scope/arcana]
authority: grimoire
last_verified: 2026-06-02
---

# Invocation: Restore (Arcana + grimoires)

## Purpose

Bring an Arcana install — engine source, library, agent skills, agent instruction block — and any grimoire that references it back to a current, validated, synchronized state. This is the Arcana-prefix mirror of `/grm-restore`; both run the one canonical Restoration procedure.

## Invocation

```
/arc-restore
```

## Procedure

The canonical, skill-less procedure is **[[RESTORATION|RESTORATION]]** at the Arcana root. Read it and follow the AI Restoration Playbook — it resolves Arcana, inspects and (if asked) pulls, reconciles the library, validates the source, resets and re-registers skills, refreshes the marked agent block, and brings any active grimoire current.

```bash
cat ARCANA_HOME/RESTORATION.md
```

## Notes

- `/arc-restore` (this command) and `/grm-restore` are mirrors over the same `RESTORATION.md` procedure. Most users only ever use `/grm-*`; `/arc-restore` exists for maintainers and fork owners working on Arcana directly.

## Related

- **Canonical procedure**: [[RESTORATION|RESTORATION]]
- **Grimoire mirror**: [[invocations/grimoire/restore|restore]]
