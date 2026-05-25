---
type: reference
title: "Validate Grimoire Encoding"
aliases: ["validate-grimoire-encoding"]
tags: [arcana/invocations, type/reference, scope/grimoire]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Validate Grimoire Encoding

## Purpose

Validate that the active grimoire uses UTF-8 without BOM, LF line endings, and no mojibake or known repair artifacts.

## Invocation

```
/grm-validate-encoding
```

## Workflow

Run from the active grimoire root:

```bash
python3 ARCANA_HOME/rites/validate_encoding.py --grimoire .
```

Report every violation with the path and line number. Exit code 0 means the grimoire is encoding-clean.
