---
type: reference
title: "Skill Naming Schema"
aliases: ["skill-schema", "skill-naming"]
tags: [arcana/docs, type/reference]
authority: grimoire
last_verified: 2026-05-25
---

# Skill Naming Schema

Arcana uses command-family prefixes. The prefix tells the user which operational surface the command belongs to:

```text
/<family-prefix>-<verb>-<object>
```

The families are declared in `arcana.json`.

## Command Families

| Family | Prefix | Use For | Example |
|---|---|---|---|
| `arcana` | `arc` | Arcana platform and maintainer operations | `/arc-validate-links` |
| `grimoire` | `grm` | Universal operations from the active grimoire context | `/grm-validate-links` |
| `library` | `arc` | Operations that affect `~/grimoires/library.json` | `/arc-library-sync` |
| `agent` | `arc` | Operations that affect agent files or agent skill directories | `/arc-agent-update` |
| `workspace` | `arc` | Operations that intentionally affect Arcana plus installed grimoires | `/arc-workspace-clean` |
| `help` | `arc` | Skill discovery and help | `/arc-help` |

Normal grimoires still declare exactly one `skill_prefix` in `grimoire.json`, such as `jpn` or `oly`. Arcana is special because it ships both platform commands and universal grimoire-context commands.

## Source Names

Source skill files use the placeholder form:

```yaml
name: {{SKILL_PREFIX}}-<registered-slug>
```

The registration rite substitutes `{{SKILL_PREFIX}}` with the command family's prefix. For example, `skills/grimoire/validate-links/SKILL.md` declares `{{SKILL_PREFIX}}-validate-links` and registers as `/grm-validate-links`.

Some `/grm-*` commands intentionally maintain Arcana from the active grimoire context. For example, `/grm-update-arcana` updates Arcana, refreshes agent integration, and then checks the active grimoire against the updated framework. Keep these rare and name the external target explicitly. These commands may resolve the active grimoire from `~/grimoires/library.json`; they should not require terminal cwd when an unambiguous grimoire can be selected.

## Reusable Rites

A rite may support more than one target through flags such as `--grimoire`, but user-facing skills must not be target-polymorphic. Expose one clear skill per target and let both skills call the same rite when reuse is appropriate.

Good:

```text
/arc-validate-frontmatter
/grm-validate-frontmatter
```

Avoid when the operation can target both Arcana and a grimoire:

```text
/arc-validate-frontmatter
```

That name is correct for Arcana only. If users also need to validate a grimoire, provide the grimoire-targeted skill as a separate command.

## Source Layout

Arcana skill source folders are grouped by command family, then flattened during registration:

```text
skills/arcana/validate-links/SKILL.md      -> /arc-validate-links
skills/grimoire/validate-links/SKILL.md    -> /grm-validate-links
skills/agent/register-skills/SKILL.md      -> /arc-agent-register-skills
```

The naming validator enforces folder/frontmatter agreement and rejects skill files outside the declared command families.

Every public Arcana-shipped command also has an entry in
[[docs/command_surface|command surface]]. That contract links the command to
its source skill, invocation leaf, workflow owner, guard, mutation behavior,
logging behavior, and validation profile. `/arc-validate-skill-refs` checks
the contract whenever command references are validated.

## Invocation Layout

Invocation files follow the same target boundary:

```text
invocations/arcana/...     -> /arc-*
invocations/grimoire/...   -> /grm-*
invocations/agent/...      -> /arc-agent-*
invocations/help/...       -> /arc-help
invocations/library/...    -> /arc-library-*
invocations/workspace/...  -> /arc-workspace-*
invocations/meta/...       -> shared fragments and templates only
```

Shared rites may live once under `rites/` and accept flags such as `--grimoire`; user-facing skills and invocation docs remain target-specific.
