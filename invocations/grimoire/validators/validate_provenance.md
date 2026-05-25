---
type: reference
title: "Validate Grimoire Provenance"
aliases: ["validate-grimoire-provenance"]
tags: [arcana/invocations, type/reference, scope/grimoire]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Validate Grimoire Provenance

## Purpose

Validate that active-grimoire pages with `authority: external` or `authority: hybrid` cite real source artifacts.

## Invocation

```
/grm-validate-provenance
```

## Workflow

Run from the active grimoire root:

```bash
python3 ARCANA_HOME/rites/validate_provenance.py --grimoire .
```

Pages must not cite transient `inbox/` paths. Stable source artifacts belong under `sources/`.
