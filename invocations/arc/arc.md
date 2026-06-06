---
type: hub
title: "Arcana Invocations"
aliases: ["arcana-invocations", "maintainer-ops"]
tags: [arcana/invocations, type/hub, scope/arcana, hub/chapter]
---

# Arcana Invocations

Maintainer and platform operations: invocations that modify Arcana itself, the local grimoire library, user agent files, and agent skill directories.

For grimoire operations, route to [[invocations/grm/grm|grm]]. For the canonical skill catalog, see [[docs/skills|skills]].

## Available

### Improvement

- Arcana improvement -> [[invocations/arc/improve_arcana|improve arcana]]

Boundary enforcement lives in the grimoire layer: [[invocations/grm/audit_boundaries|audit boundaries]]. It can scan Arcana itself with the `--arcana` flag.

### Update

- Update Arcana and grimoires to a current, validated, synchronized state -> [[invocations/arc/update|update]]. Mirror of `/grm-update`; the canonical, skill-less procedure is [[UPDATE|UPDATE]].

### Sync and environment

- Sync skills, the library, or the agent file -> [[invocations/arc/sync|sync]]. One command with a positional sub-target: `/arc-sync skills`, `/arc-sync library`, `/arc-sync agentfile`. Active-grimoire-only skill sync is `/grm-sync`.
- Adopt an unmanaged grimoire directory -> [[invocations/arc/adopt|adopt]]
- Clean transient workspace artifacts -> [[invocations/arc/clean|clean]]

### Validators

Mechanical, exit-code validators, run via `/arc-validate [selector]`. Full list and selectors -> [[invocations/arc/validators/validators|validators]]

### Quality

Judgment-based quality audits and their orchestrator -> [[invocations/arc/quality/quality|quality]]

### Help

- Show the Arcana skill catalog and installed grimoire skills -> [[invocations/arc/help|help]]

## When to run

- Before any Arcana release
- After bulk doc/rite changes
- Monthly drift audit
- As phases of `/arc-improve`

## Related

- Grimoire operations -> [[invocations/grm/grm|grm]]
- Meta support -> [[invocations/meta/meta|meta]]
