---
name: {{SKILL_PREFIX}}-validate-all
description: Run the full Arcana validator suite via the orchestrator rite (every mechanical check in one shot)
when_to_use: Before committing changes to Arcana itself; after bulk edits to Arcana docs/invocations/rites/skills; as a pre-release gate; user mentions "validate Arcana" or "check before commit". Cheap and read-only - safe to run liberally.
user-invocable: true
allowed-tools: Bash Read
---

# Validate Arcana (All)

You are running the full validator suite against the Arcana repository. The orchestrator rite (`rites/validate.py`) executes every individual validator and aggregates results.

For a single concern, every validator also has its own focused skill - run `/arc-help` for the full catalog, or browse `{{ARCANA_PATH}}/docs/skills.md`. Run the focused skill if you want faster feedback on one aspect; run this aggregate before commits/releases.

## Run

Default (sequential):
```bash
python3 {{ARCANA_PATH}}/rites/validate.py
```

The orchestrator supports four optional modes - pick the one that matches user intent:
- `--parallel` - run all validators concurrently (faster on a clean repo)
- `--smart` - git-aware: only show validators relevant to the working-tree changes (no execution)
- `--auto` - `--smart` plus auto-execute the relevant validators
- `--summary` - collapsed output, only pass/fail per validator

Report aggregated pass/fail status to the user. Exit code 0 means every validator passed.

## When to use

- Before an Arcana release
- After bulk doc/rite edits
- As the validation phase of `/arc-improve`
