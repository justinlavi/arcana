---
type: hub
title: "Arcana Invocations"
aliases: ["arcana-invocations", "maintainer-ops"]
tags: [arcana/invocations, type/hub, scope/arcana, hub/chapter]
---

# Arcana Invocations

Invocations that modify Arcana itself. Maintainer only.

For grimoire operations, route to [[invocations/grimoire/grimoire|grimoire]]. For agent, library, help, workspace, and shared support docs, route through their invocation hubs. For the canonical skill catalog, see [[docs/skills|skills]].

## Available

### Improvement

- Arcana improvement -> [[invocations/arcana/improve_arcana|improve arcana]]

Boundary enforcement lives in the grimoire layer: [[invocations/grimoire/audit_boundaries|audit boundaries]]. It can scan Arcana itself with the `--arcana` flag.

### Update

- Update Arcana and grimoires to a current, validated, synchronized state -> [[invocations/arcana/update|update]]. Mirror of `/grm-update`; the canonical, skill-less procedure is [[UPDATE|UPDATE]].

### Validators

Mechanical, exit-code validators, run via `/arc-validate [selector]`. Full list and selectors -> [[invocations/arcana/validators/validators|validators]]

### Quality

Judgment-based quality audits and their orchestrator -> [[invocations/arcana/quality/quality|quality]]

## When to run

- Before any Arcana release
- After bulk doc/rite changes
- Monthly drift audit
- As phases of `/arc-improve`
