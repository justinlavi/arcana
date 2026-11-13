---
type: hub
title: "Arcana Invocations"
aliases: ["arcana-invocations", "maintainer-ops"]
tags: [arcana/invocations, type/hub, scope/arcana, hub/chapter]
---

# Arcana Invocations

Maintainer and platform operations: invocations that modify Arcana itself, the local grimoire library, user agent files, and agent skill directories. Five `/arc-*` verbs.

For grimoire operations, route to [[invocations/grm/grm|grm]]. For the canonical skill catalog, see [[docs/skills|skills]].

## Available

### Improvement

- Arcana improvement -> [[invocations/arc/improve_arcana|improve arcana]]

Boundary enforcement lives in the grimoire layer: `/grm-check boundaries --arcana` runs it against Arcana itself ([[invocations/grm/check|check]]).

### Update

- Bring Arcana and every grimoire current, or reconcile one surface (`skills`, `library`, `agentfile`) at platform scope -> [[invocations/arc/update|update]]. Mirror of `/grm-update`; the canonical, skill-less procedure is [[UPDATE|UPDATE]].
- Register an unmanaged directory as a grimoire -> `/grm-setup <folder>` ([[invocations/grm/setup|setup]]).
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
