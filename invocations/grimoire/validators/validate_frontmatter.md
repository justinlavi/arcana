---
type: reference
title: "Validate Grimoire Frontmatter"
aliases: ["validate-grimoire-frontmatter"]
tags: [arcana/invocations, type/reference, scope/grimoire]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Validate Grimoire Frontmatter

## Purpose

Validate active-grimoire page frontmatter against
`ARCANA_HOME/docs/page_schema.md`, including the rule that `type: source` is
reserved for source wrappers under `sources/`.

## Invocation

```
/grm-validate frontmatter
```

## Workflow

Run against the resolved active grimoire:

```bash
python3 ARCANA_HOME/rites/validate_frontmatter.py --grimoire GRIMOIRE_ROOT
```

Use this when pages were added, imported, or edited. For Arcana itself, use `/arc-validate frontmatter`.
