---
name: {{SKILL_PREFIX}}-validate
description: Run Arcana mechanical validators, optionally narrowed by selector
when_to_use: Before committing Arcana changes; after editing Arcana docs, invocations, rites, skills, or command metadata; user asks whether Arcana validates, whether links/frontmatter/format/security are clean, or wants a targeted mechanical check.
argument-hint: "[all|smart|auto|summary|parallel|links|frontmatter|format|...]"
arguments: selector
user-invocable: true
allowed-tools: Bash Read
---

# Validate Arcana

You are running deterministic, script-backed validation against Arcana itself.
Validation is mechanical: it should run a rite and report pass/fail diagnostics
with file:line citations when available. Judgment-based review belongs to audit
workflows, not this skill.

## Selectors

- No selector or `all`: run the full Arcana validator suite.
- `smart`: show validators relevant to the current git changes.
- `auto`: run the smart-selected validators.
- `summary`: run the full suite with summary-only output.
- `parallel`: run the full suite in parallel.
- Validator selectors such as `structure`, `encoding`, `portability`, `naming`,
  `semantics`, `format`, `frontmatter`, `links`, `orphans`, `provenance`,
  `skill-refs`, `security`, and `doc-trees` run only those validators.
- Multiple validators may be space-separated or comma-separated.

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate.py $selector
```

Examples:

```bash
python3 {{ARCANA_PATH}}/rites/validate.py
python3 {{ARCANA_PATH}}/rites/validate.py links frontmatter
python3 {{ARCANA_PATH}}/rites/validate.py smart
python3 {{ARCANA_PATH}}/rites/validate.py parallel
```

## Procedural Detail

!`cat {{ARCANA_PATH}}/invocations/arc/validators/validate.md`
