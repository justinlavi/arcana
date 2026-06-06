---
name: {{SKILL_PREFIX}}-validate
description: Run mechanical validators against the active grimoire, optionally narrowed by selector
when_to_use: Before committing grimoire changes; after editing pages, sources, links, or scaffold files; user asks whether a grimoire validates, whether links/frontmatter/format are clean, or wants a targeted mechanical check.
argument-hint: "[all|smart|auto|summary|parallel|links|frontmatter|format|...]"
arguments: selector
user-invocable: true
allowed-tools: Bash Read
---

# Validate Grimoire

You are running deterministic, script-backed validation against the resolved
active grimoire. Validation is mechanical: it should run a rite and report
pass/fail diagnostics with file:line citations when available. Judgment-based
reviews such as semantic naming and magical-boundary checks belong to
`/grm-audit-*` skills, not this validator.

## Precondition

!`cat {{ARCANA_PATH}}/invocations/meta/grimoire_directory_guard.md`

## Selectors

- No selector or `all`: run the full mechanical grimoire validator suite.
- `smart`: show validators relevant to the current git changes.
- `auto`: run the smart-selected validators.
- `summary`: run the full suite with summary-only output.
- `parallel`: run the full suite in parallel.
- Validator selectors such as `structure`, `encoding`, `portability`, `format`,
  `frontmatter`, `links`, `orphans`, `provenance`, and `doc-trees` run only
  those validators.
- Multiple validators may be space-separated or comma-separated.

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate.py --grimoire {{GRIMOIRE_PATH}} $selector
```

Examples:

```bash
python3 {{ARCANA_PATH}}/rites/validate.py --grimoire {{GRIMOIRE_PATH}}
python3 {{ARCANA_PATH}}/rites/validate.py --grimoire {{GRIMOIRE_PATH}} links frontmatter
python3 {{ARCANA_PATH}}/rites/validate.py --grimoire {{GRIMOIRE_PATH}} smart
python3 {{ARCANA_PATH}}/rites/validate.py --grimoire {{GRIMOIRE_PATH}} parallel
```

## Procedural Detail

!`cat {{ARCANA_PATH}}/invocations/grm/validators/validate.md`
