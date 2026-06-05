---
type: hub
title: "Library Invocations"
aliases: ["library-invocations", "library-ops"]
tags: [arcana/invocations, type/hub, scope/library, hub/chapter]
---

# Library Invocations

Library operations that read or update `~/grimoires/library.json`, the local registry of installed grimoires.

## Available

| Invocation | Skill | What it does |
|---|---|---|
| [[invocations/library/sync|sync]] | `/arc-library-sync` | Reconcile the local library against actual grimoire directories |
| [[invocations/library/adopt|adopt]] | `/arc-library-adopt` | Add a `grimoire.json` manifest to an unmanaged grimoire directory |

## Related

- Agent skill sync -> [[invocations/agent/sync_skills|sync skills]]
- Grimoire creation -> [[invocations/grimoire/create_grimoire|create grimoire]]
- Library schema -> [[docs/reference|reference]]
