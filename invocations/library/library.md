---
type: hub
title: "Library Invocations"
aliases: ["library-invocations", "library-ops"]
tags: [arcana/invocations, type/hub, scope/library, hub/chapter]
---

# Library Invocations

Library operations - invocations that read or update `~/grimoires/library.json`, the local registry of installed grimoires.

## Available

| Invocation | Skill | What it does |
|---|---|---|
| [sync.md](sync.md) | `/arc-library-sync` | Reconcile the local library against actual grimoire directories under `~/grimoires/` |
| [adopt.md](adopt.md) | `/arc-library-adopt` | Add a `grimoire.json` manifest to an unmanaged grimoire directory |

## Related

- Agent skill registration: [`../agent/register_skills.md`](../agent/register_skills.md)
- Grimoire creation: [`../grimoire/create_grimoire.md`](../grimoire/create_grimoire.md)
- Library schema: [`../../docs/reference.md`](../../docs/reference.md)
