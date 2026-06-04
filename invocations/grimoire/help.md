---
type: playbook
title: "Grimoire Help"
aliases: ["grimoire-help", "grm-skill-catalog"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-06-01
---

# Invocation: Grimoire Help

## Purpose

Show a grimoire author the commands they reach for from inside a grimoire: the `/grm-*` family (Arcana's grimoire operations) and the active grimoire's own skills. For the full platform catalog - every `/arc-*` command and every installed grimoire - use `/arc-help`.

## Invocation

```
/grm-help
```

## Preconditions

!`cat ARCANA_HOME/invocations/meta/grimoire_directory_guard.md`

## Workflow

### 1. Show the /grm-* command family

Read [[docs/skills|skills]] and present its `/grm-*` rows - the grimoire operations. It is the canonical, sync-generated list. If `docs/skills.md` is missing, fall back to scanning `skills/grimoire/*/SKILL.md` and warn that it should be regenerated with `python3 rites/sync_docs.py --apply`.

### 2. Show the active grimoire's own skills

For the resolved `GRIMOIRE_ROOT`:

1. Read `GRIMOIRE_ROOT/grimoire.json` for the grimoire's `name` and `skill_prefix`.
2. List `GRIMOIRE_ROOT/skills/*/SKILL.md`. For each, parse the frontmatter `name` and `description`.
3. If `skills/` is absent or empty, say the grimoire ships no skills of its own yet.

### 3. Present the catalog

Render two terse tables - skill on the left, description on the right. No ASCII boxes, no decorative separators.

```
Grimoire commands (/grm-*) - N skills
| Skill | Description |
|---|---|
| /grm-... | ... |

<Grimoire Name> skills (<prefix>-*) - N skills
| Skill | Description |
|---|---|
| /<prefix>-... | ... |
```

### 4. Point to the full catalog

End with one line: `For every Arcana command and all installed grimoires, run /arc-help.`

## Related

- **Full Arcana + grimoire catalog**: [[invocations/help/help|help]]
- **Canonical skill catalog**: [[docs/skills|skills]]
- **Active-grimoire skill sync**: [[invocations/grimoire/agent_sync_skills|agent sync skills]]
