---
name: {{NAMESPACE}}-arcana-validate-skill-refs
description: Mechanically validate that every /grm-* skill mentioned in Arcana docs resolves to a real skill folder
when_to_use: After renaming or removing any skill; after editing docs that mention `/grm-*` commands; as a phase of `/grm-arcana-improve`; user mentions "stale skill reference", "broken slash command", or "did I rename a skill". Cheap and read-only.
user-invocable: true
disable-model-invocation: true
allowed-tools: Bash Read
---

# Validate Arcana Skill References

You are running the skill-references validator against the Arcana repository. It scans every markdown file for `/grm-*` references and verifies each one matches a `skills/<slug>/SKILL.md` folder. Catches drift like:

- A doc mentions `/grm-arcana-foo` after the skill was renamed or deleted.
- A new skill is announced in prose before its source folder is created.
- A typo in a slash-command reference (`/grm-doman-improve` vs `/grm-domain-improve`).

Wildcard and placeholder forms (`/grm-arcana-validate-*`, `/grm-arcana-validate-<name>`) are skipped — they're prose, not real references.

## Run

```bash
python3 {{ARCANA_PATH}}/rites/validate_skill_refs.py
```

Report dangling references with file:line citations. Exit code 0 means clean; non-zero means at least one reference doesn't resolve.

## Procedural detail

If references are stale, choose one of:

1. **The reference is wrong**: rename the doc reference to match an existing skill, or delete the stale mention.
2. **The skill should exist**: create `skills/<slug>/SKILL.md`, then re-run `/grm-skills-register` and `python3 rites/sync_docs.py --apply`.
3. **The skill was intentionally retired**: scan all docs and remove the references, then re-run this validator.

This validator is part of the suite run by `/grm-arcana-validate-all` and the `validate.py` orchestrator.
