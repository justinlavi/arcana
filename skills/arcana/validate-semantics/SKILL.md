---
name: {{SKILL_PREFIX}}-validate-semantics
description: Mechanically scan Arcana for hyphenated path examples written in prose (Arcana convention is snake_case)
when_to_use: Before committing changes that touched docs, invocations, or formulae; as a phase of `/arc-improve`; user mentions "snake_case", "path examples", or "I think I wrote a hyphenated path somewhere". Cheap and read-only.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Arcana Semantics

You are running the semantics validator against the Arcana repository. It scans markdown body text for hyphenated paths inside `chapters/...` (for example a folder or filename written with a dash where Arcana expects snake_case).

This is a mechanical pattern scan that's distinct from `/arc-validate-naming` (which enforces snake_case on actual filenames). For *intelligent* semantic analysis (naming quality, organizational discoverability), use `/grm-analyze-semantics`.

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_semantics.py
```

Report violations with file:line citations. Exit code 0 means clean; non-zero means at least one hyphenated example exists.

## Procedural detail

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_semantics.md`
