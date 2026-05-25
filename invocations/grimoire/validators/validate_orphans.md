---
type: reference
title: "Validate Grimoire Orphans"
aliases: ["validate-grimoire-orphans"]
tags: [arcana/invocations, type/reference, scope/grimoire]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Validate Grimoire Orphans

## Purpose

Detect authored grimoire pages that no other page links to.

## Invocation

```
/grm-validate-orphans
```

## Workflow

Run from the active grimoire root:

```bash
python3 ARCANA_HOME/rites/validate_orphans.py --grimoire .
```

Orphans are candidates to wire into a hub, merge, or delete after review.
