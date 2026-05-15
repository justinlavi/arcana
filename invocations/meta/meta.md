---
type: hub
title: "Meta Invocations"
aliases: ["meta-invocations"]
tags: [arcana/invocations, type/hub, scope/meta, hub/chapter]
---

# Meta Invocations

System documentation and meta-operations — invocations *about* Grimoire that don't modify any grimoire or Arcana itself.

## Available

- **[help.md](help.md)** — `/grm-meta-help`. Dynamically scans every invocation file and renders the catalog on-the-fly. Single source: the invocation files themselves.
- **[base_invocation.md](base_invocation.md)** — Generic invocation execution template. Used as a starting point when building a custom workflow that doesn't match any existing invocation.
- **[grimoire_directory_guard.md](grimoire_directory_guard.md)** — Shared precondition included via `!cat` by every `/grm-domain-*` skill that operates on the active grimoire (cwd). Single-sourced so the guard contract stays consistent across skills.

## Related

- Domain operations: [`../grimoire/grimoire.md`](../grimoire/grimoire.md)
- Arcana maintenance (maintainer only): [`../arcana/arcana.md`](../arcana/arcana.md)
- Canonical skill catalog: [`../../docs/skills.md`](../../docs/skills.md)
