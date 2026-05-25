---
type: reference
title: "Validate Grimoire Portability"
aliases: ["validate-grimoire-portability"]
tags: [arcana/invocations, type/reference, scope/grimoire]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Validate Grimoire Portability

## Purpose

Validate that every active-grimoire path is safe to clone on Windows, Linux, and macOS.

## Invocation

```
/grm-validate-portability
```

## Workflow

Run against the resolved active grimoire:

```bash
python3 ARCANA_HOME/rites/validate_portability.py --grimoire GRIMOIRE_ROOT
```

Any violation should be fixed before sharing the grimoire with other machines.
