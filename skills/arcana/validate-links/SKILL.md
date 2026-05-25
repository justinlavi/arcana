---
name: {{SKILL_PREFIX}}-validate-links
description: Validate Arcana links and require wikilinks for internal Markdown pages
when_to_use: After moving or renaming any markdown file; as a phase of `/arc-improve`; user mentions "broken link", "dead link", or "did I break any references". Cheap and read-only.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Arcana Links

You are running the link validator against the Arcana repository (not against grimoires - this is an Arcana-internal check).

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_links.py
```

Report broken links and internal Markdown-page style violations to the user with file:line citations. Exit code 0 means clean; non-zero means at least one checked link or page reference is invalid.

Be aware: template formula files (under `formulae/`) intentionally contain placeholder paths like `ARCANA_HOME/...` that don't resolve - these are not failures. The rite knows how to skip them; if it doesn't, treat as a rite bug, not a content bug.

## Procedural detail

!`cat {{ARCANA_PATH}}/invocations/arcana/validators/validate_links.md`
