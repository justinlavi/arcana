---
type: reference
title: "Validate Grimoire Format"
aliases: ["validate-grimoire-format"]
tags: [arcana/invocations, type/reference, scope/grimoire]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Validate Grimoire Format

## Purpose

Validate portable Markdown formatting in the active grimoire: table delimiters, fenced code blocks, and directory tree examples.

## Invocation

```
/grm-check format
```

## Workflow

Run against the resolved active grimoire:

```bash
ARCANA_HOME/bin/arcana validate_format --grimoire GRIMOIRE_ROOT
```

The grimoire mode uses the shared format rite but only applies checks that make sense for grimoire content. Arcana-specific invocation and formula checks remain under `/arc-validate format`.
