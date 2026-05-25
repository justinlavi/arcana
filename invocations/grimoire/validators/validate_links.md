---
type: reference
title: "Validate Grimoire Links"
aliases: ["validate-grimoire-links"]
tags: [arcana/invocations, type/reference, scope/grimoire]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Validate Grimoire Links

## Purpose

Validate that markdown links and full-path Obsidian wikilinks resolve inside the active grimoire.

## Invocation

```
/grm-validate-links
```

## Workflow

Run from the active grimoire root:

```bash
python3 ARCANA_HOME/rites/validate_links.py --grimoire .
```

Report broken links with file and line citations. Exit code 0 means all checked links resolve.
