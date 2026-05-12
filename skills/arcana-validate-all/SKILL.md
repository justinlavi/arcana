---
name: {{NAMESPACE}}-arcana-validate-all
description: Run the full Arcana validator suite (structure, naming, semantics, format, links, security, skill-refs) via the orchestrator rite
when_to_use: Before committing changes to Arcana itself; after bulk edits to Arcana docs/invocations/rites/skills; as a pre-release gate; user mentions "validate Arcana" or "check before commit". Cheap and read-only — safe to run liberally.
user-invocable: true
allowed-tools: Bash Read
---

# Validate Arcana (All)

You are running the full validator suite against the Arcana repository. The orchestrator rite (`rites/validate.py`) executes each individual validator and aggregates results.

For a single concern, use the focused skill:
- `/grm-arcana-validate-structure`
- `/grm-arcana-validate-naming`
- `/grm-arcana-validate-semantics`
- `/grm-arcana-validate-format`
- `/grm-arcana-validate-links`
- `/grm-arcana-validate-security`
- `/grm-arcana-validate-boundaries`

## Run

Default (sequential):
```bash
python3 {{ARCANA_PATH}}/rites/validate.py
```

The orchestrator supports four optional modes — pick the one that matches user intent:
- `--parallel` — run all validators concurrently (faster on a clean repo)
- `--smart` — git-aware: only show validators relevant to the working-tree changes (no execution)
- `--auto` — `--smart` plus auto-execute the relevant validators
- `--summary` — collapsed output, only pass/fail per validator

Report aggregated pass/fail status to the user. Exit code 0 means every validator passed.

## When to use

- Before an Arcana release
- After bulk doc/rite edits
- As the validation phase of `/grm-arcana-improve`
