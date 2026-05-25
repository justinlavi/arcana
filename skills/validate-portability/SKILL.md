---
name: {{SKILL_PREFIX}}-validate-portability
description: Detect Windows-reserved characters (< > : " | ? *) and reserved basenames in any grimoire path - prevents catastrophic git checkout failures on Windows clones
when_to_use: Before pushing a new chapter, after bulk renames, when authoring template scaffolds whose filenames intentionally contain placeholders. Cheap and read-only.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Portability

You are running the filesystem-portability checker against the Arcana repository (or, when the working directory is a grimoire, against that grimoire).

The check exists because `git checkout` on Windows fails fatally - with a partial working tree and an `invalid path` error - when any path in the repository contains a Windows-reserved character (`< > : " | ? *`), a reserved basename (CON, PRN, AUX, NUL, COM1-9, LPT1-9), or a trailing dot or space. Once that failure happens, subsequent clones report success but leave the working tree in a partial state, which is hard to diagnose. Catching the issue at validation time prevents the problem from ever reaching a Windows machine.

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_portability.py --grimoire .
```

Report each violation with its relative path and the offending segment. Exit code 0 means all paths are Windows-safe; non-zero means at least one path will break on Windows.

## Procedural detail

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_portability.md`
