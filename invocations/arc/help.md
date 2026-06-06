---
type: playbook
title: "Help"
aliases: ["help", "skill-catalog"]
tags: [arcana/invocations, type/playbook, scope/help]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Arcana Help

## Purpose

Show the user the Arcana skill catalog plus any skills shipped by grimoires registered in `~/grimoires/library.json`. The Arcana list lives in [[docs/skills|skills]] (auto-generated); grimoire skills must be enumerated live from the local library because Arcana does not maintain a central list of downstream grimoires.

## Invocation

```
/arc-help
```

## Workflow

### 1. Show Arcana skills

Read [[docs/skills|skills]] and present its tables to the user as-is. It is the canonical, sync-generated list. Do not re-derive it by scanning `skills/<family>/<slug>/SKILL.md` unless `docs/skills.md` is missing - in that case fall back to the scan and warn the user it should be regenerated with `python3 rites/sync_docs.py --apply`.

### 2. Enumerate grimoire skills

Read `~/grimoires/library.json`. For each entry under `grimoires`:

1. Resolve `local_path` (expand `$HOME`).
2. Read `<local_path>/grimoire.json` to get the grimoire's `name` and `skill_prefix`.
3. List `<local_path>/skills/*/SKILL.md`. For each, parse the YAML frontmatter and capture `name` and `description`.
4. Skip the grimoire (with a one-line note) if `grimoire.json` is missing, `skills/` is absent, or no `SKILL.md` files exist.

### 3. Present the catalog

Group by source. For each group, render a simple table - skill on the left, description on the right. Keep it terse; no ASCII boxes, no decorative separators.

```
Arcana skills (arc-* and grm-*) - N skills
<table from docs/skills.md, or summary linking to it>

<Grimoire Name> skills (<skill prefix>-*) - N skills
| Skill | Description |
|---|---|
| /<skill prefix>-... | ... |
```

If only Arcana is installed, say so and point the user at `/grm-create` to start a grimoire.

### 4. Counts

End with a one-line total: `Total: N skills across M sources (Arcana + <list>)`.

## Related

- **Arcana skill catalog (canonical)**: [[docs/skills|skills]]
- **Global skill registration**: `/arc-sync skills`
- **Active-grimoire skill registration**: `/grm-sync`
- **Catalog reconciliation**: `/arc-sync library`
- **Skill system mechanics**: [[docs/agent_configuration|agent configuration]]
