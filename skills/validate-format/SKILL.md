---
name: {{SKILL_PREFIX}}-validate-format
description: Mechanically validate Markdown formatting (headings, code fences, tables, tree examples)
when_to_use: Before committing changes that touched docs, invocations, formulae, or README files; as a phase of `/arc-improve`; user mentions "format check" or "is this markdown well-formed". Cheap and read-only.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Arcana Format

You are running the format validator against the Arcana repository. It can also scan a grimoire root when passed `--grimoire`.

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_format.py
```

For a grimoire:

```bash
python3 {{ARCANA_PATH}}/rites/validate_format.py --grimoire .
```

Report violations to the user with file:line citations from the rite output. Exit code 0 means clean; non-zero means violations were found.

## Procedural detail

For full workflow guidance (when to run, how to interpret violations, fix patterns):

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_format.md`
