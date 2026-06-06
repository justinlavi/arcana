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
| `arcana` | `arc` | Arcana platform and maintainer operations | `/arc-validate links` |
| `grimoire` | `grm` | Universal operations from the active grimoire context | `/grm-validate links` |
| `library` | `arc` | Operations that affect `~/grimoires/library.json` | `/arc-library-sync` |
| `agent` | `arc` | Operations that affect agent files or agent skill directories | `/arc-sync-agentfile` |
| `workspace` | `arc` | Operations that intentionally affect Arcana plus installed grimoires | `/arc-workspace-clean` |
| `help` | `arc` | Skill discovery and help | `/arc-help` |

Normal grimoires still declare exactly one `skill_prefix` in `grimoire.json`, such as `jpn` or `oly`. Arcana is special because it ships both platform commands and universal grimoire-context commands.

## Source Names

Source skill files use the placeholder form:

```yaml
name: {{SKILL_PREFIX}}-<registered-slug>
```

The registration rite substitutes `{{SKILL_PREFIX}}` with the command family's prefix. For example, `skills/grimoire/validate/SKILL.md` declares `{{SKILL_PREFIX}}-validate` and registers as `/grm-validate`.

Some `/grm-*` commands intentionally maintain Arcana from the active grimoire context. For example, `/grm-update` brings the active grimoire and its Arcana back to a current, validated, synchronized state. Keep these rare and name the external target explicitly. These commands may resolve the active grimoire from `~/grimoires/library.json`; they should not require terminal cwd when an unambiguous grimoire can be selected.

## SKILL.md Structure

Every source skill is a `SKILL.md` with YAML frontmatter and a Markdown body.

| Frontmatter field | Required | Purpose |
|---|---|---|
| `name` | yes | `{{SKILL_PREFIX}}-<registered-slug>`; the registration rite substitutes the family prefix. |
| `description` | yes | One line shown in the agent's slash-command picker. |
| `when_to_use` | optional | Natural-language triggers that let an agent surface the skill for a matching problem. |
| `user-invocable` | optional | `true` exposes the command for explicit user invocation. |
| `disable-model-invocation` | optional | `true` stops an agent from auto-invoking the skill; only user-typed commands trigger it. Set it on destructive or maintainer-only skills and judgment audits that should not auto-trigger. |
| `allowed-tools` | optional | Space-separated tools the skill may use, e.g. `Bash Read`. |

The auto-invocation policy and per-agent support matrix live in
[agent configuration](agent_configuration.md).

The body either runs a rite or loads an invocation, following the same boundary
that separates rites from invocations:

- **Rite-backed**: the body runs `python3 {{ARCANA_PATH}}/rites/<name>.py` and reports the result.
- **Invocation-backed**: the body inlines its invocation at runtime with a `!cat` directive so the agent reads and follows it:

```text
!`cat {{ARCANA_PATH}}/invocations/<area>/<name>.md`
```

`{{ARCANA_PATH}}` and `{{GRIMOIRE_PATH}}` are resolved by the registration rite.

## Reusable Rites

A rite may support more than one target through flags such as `--grimoire`, but user-facing skills must not be target-polymorphic. Expose one clear skill per target and let both skills call the same rite when reuse is appropriate.

Good:

```text
/arc-validate frontmatter
/grm-validate frontmatter
```

Avoid when the operation can target both Arcana and a grimoire:

```text
/arc-validate frontmatter
```

That name is correct for Arcana only. If users also need to validate a grimoire, provide the grimoire-targeted skill as a separate command.

## Source Layout

Arcana skill source folders are grouped by command family, then flattened during registration:

```text
skills/arcana/validate/SKILL.md            -> /arc-validate
skills/grimoire/validate/SKILL.md          -> /grm-validate
skills/grimoire/audit-semantics/SKILL.md   -> /grm-audit-semantics
skills/agent/sync-skills/SKILL.md          -> /arc-sync-skills
```

The naming validator enforces folder/frontmatter agreement and rejects skill files outside the declared command families.

Every public Arcana-shipped command also has an entry in
[command surface](command_surface.md). That contract links the command to
its source skill, invocation leaf, workflow owner, guard, mutation behavior,
logging behavior, and validation profile. `/arc-validate skill-refs` checks
the contract whenever command references are validated.

## Invocation Layout

Invocation files follow the same target boundary:

```text
invocations/arcana/...     -> /arc-*
invocations/grimoire/...   -> /grm-*
invocations/agent/...      -> /arc-* (e.g. /arc-sync-skills, /arc-sync-agentfile)
invocations/help/...       -> /arc-help
invocations/library/...    -> /arc-library-*
invocations/workspace/...  -> /arc-workspace-*
invocations/meta/...       -> shared fragments and templates only
```

Shared rites may live once under `rites/` and accept flags such as `--grimoire`; user-facing skills and invocation docs remain target-specific.
