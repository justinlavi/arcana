---
type: playbook
title: "Help"
aliases: ["help", "skill-catalog"]
tags: [arcana/invocations, type/playbook, scope/meta]
authority: grimoire
last_verified: 2026-05-12
---

# Invocation: Grimoire Help

## Purpose

Show the user every Grimoire skill currently installed: Arcana's `grm-*` catalog plus the skills shipped by each domain grimoire registered in `~/grimoires/library.json`. The Arcana list lives in [`docs/skills.md`](../../docs/skills.md) (auto-generated); domain skills must be enumerated live since no equivalent static catalog exists across grimoires.

## Invocation

```
/grm-meta-help
```

## Workflow

### 1. Show Arcana skills

Read [`GRIMOIRE_ARCANA/docs/skills.md`](../../docs/skills.md) and present its tables to the user as-is. It is the canonical, sync-generated list. Do not re-derive it by scanning `skills/<slug>/SKILL.md` unless `docs/skills.md` is missing — in that case fall back to the scan and warn the user it should be regenerated with `python3 rites/sync_docs.py --apply`.

### 2. Enumerate domain grimoire skills

Read `~/grimoires/library.json`. For each entry under `grimoires`:

1. Resolve `local_path` (expand `$HOME`).
2. Read `<local_path>/grimoire.json` to get the grimoire's `name` and `skill_namespace`.
3. List `<local_path>/skills/*/SKILL.md`. For each, parse the YAML frontmatter and capture `name` and `description`.
4. Skip the grimoire (with a one-line note) if `grimoire.json` is missing, `skills/` is absent, or no `SKILL.md` files exist.

### 3. Present the catalog

Group by source. For each group, render a simple table — skill on the left, description on the right. Keep it terse; no ASCII boxes, no decorative separators.

```
Arcana skills (grm-*) — N skills
<table from docs/skills.md, or summary linking to it>

<Grimoire Name> skills (<namespace>-*) — N skills
| Skill | Description |
|---|---|
| /<namespace>-... | ... |
```

If only Arcana is installed, say so and point the user at `/grm-domain-create-grimoire` to start a domain grimoire.

### 4. Counts

End with a one-line total: `Total: N skills across M grimoires (Arcana + <list>)`.

## Related

- **Arcana skill catalog (canonical)**: [`docs/skills.md`](../../docs/skills.md)
- **Skill registration**: `/grm-skills-register`
- **Catalog reconciliation**: `/grm-library-sync`
- **Skill system mechanics**: [`docs/agent_configuration.md`](../../docs/agent_configuration.md)
