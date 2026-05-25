---
type: hub
title: "Meta Invocations"
aliases: ["meta-invocations"]
tags: [arcana/invocations, type/hub, scope/meta, hub/chapter]
---

# Meta Invocations

Shared invocation fragments and templates. User-facing operations belong in their target family folders: `agent/`, `arcana/`, `grimoire/`, `help/`, `library/`, or `workspace/`.

## Available

- **[base_invocation.md](base_invocation.md)** - Generic invocation execution template. Used as a starting point when building a custom workflow that doesn't match any existing invocation.
- **[grimoire_directory_guard.md](grimoire_directory_guard.md)** - Shared precondition included via `!cat` by every `/grm-*` skill that operates on the active grimoire (cwd). Single-sourced so the guard contract stays consistent across skills.

## Related

- Grimoire operations: [`../grimoire/grimoire.md`](../grimoire/grimoire.md)
- Arcana maintenance (maintainer only): [`../arcana/arcana.md`](../arcana/arcana.md)
- Agent operations: [`../agent/agent.md`](../agent/agent.md)
- Help: [`../help/help.md`](../help/help.md)
- Library operations: [`../library/library.md`](../library/library.md)
- Workspace operations: [`../workspace/workspace.md`](../workspace/workspace.md)
- Canonical skill catalog: [`../../docs/skills.md`](../../docs/skills.md)
