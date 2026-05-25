---
type: reference
title: "Public Command Surface"
aliases: ["command-surface", "command-matrix", "skill-command-contract"]
tags: [type/reference, arcana/docs, scope/skills]
authority: grimoire
last_verified: 2026-05-25
---

# Public Command Surface

Arcana's public slash-command contract lives in
[`../rites/data/command_surface.json`](../rites/data/command_surface.json).
That file is the source of truth for the operational matrix:

```text
command -> skill source -> invocation leaf -> rite/judgment owner ->
guard/preconditions -> mutation/log behavior -> validation profile ->
generated docs impact
```

`/arc-validate-skill-refs` validates the matrix. It checks that every
Arcana-shipped public skill appears exactly once, that each listed skill,
invocation, guard, and rite path exists, and that every contract entry uses a
known owner and mutation profile.
`docs/skills.md` renders the same matrix as the generated skill catalog.

## Fields

| Field | Meaning |
|---|---|
| `command` | Public slash command, such as `/grm-ingest`. |
| `family` | Command family from `arcana.json`. |
| `skill_source` | Source `SKILL.md` that registers the command. |
| `invocation` | Primary workflow home. |
| `guard` | Shared guard fragment, or `null` when no shared guard applies. |
| `owner_type` | `rite`, `judgment`, or `hybrid`. |
| `rite_owner` | Deterministic rite path, or `null` for judgment-owned workflows. |
| `preconditions` | Conditions the command must establish before acting. |
| `mutation_profile` | `read_only`, `plan_apply`, `apply_only`, `append_only`, or `judgment_gated`. |
| `mutation_behavior` | Plain-language write behavior. |
| `log_behavior` | Whether the command appends or creates a grimoire log entry. |
| `validation_profile` | Checks that prove the command's work. |
| `generated_docs_impact` | How generated docs reflect the command. |

## Maintenance

When adding, removing, or renaming a public Arcana-shipped command:

1. Update `skills/<family>/<slug>/SKILL.md`.
2. Update or create the invocation leaf.
3. Update `rites/data/command_surface.json`.
4. Run `python3 rites/validate_skill_refs.py`.
5. Run `python3 rites/sync_docs.py --apply`.

## Related

- Skill schema: [[docs/skill_schema|skill schema]]
- Generated skill catalog: [[docs/skills|skills]]
- Validator: [[invocations/arcana/validators/validate_skill_refs|validate skill refs]]
