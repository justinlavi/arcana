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
| `grm` | `grm` | Universal operations from the active grimoire context | `/grm-check links` |
| `arc` | `arc` | Arcana platform and maintainer operations: the engine, the home library, agent files, and agent skill directories | `/arc-validate links` |

Each family maps to one source directory (`skills/grm/`, `skills/arc/`) and one slash-command prefix. Normal grimoires still declare exactly one `skill_prefix` in `grimoire.json`, such as `cook` or `dnd`. Arcana is special because it ships both platform commands (`arc`) and universal grimoire-context commands (`grm`).

## Source Names

Source skill files use the placeholder form:

```yaml
name: {{SKILL_PREFIX}}-<registered-slug>
```

The registration rite substitutes `{{SKILL_PREFIX}}` with the command family's prefix. For example, `skills/grm/check/SKILL.md` declares `{{SKILL_PREFIX}}-check` and registers as `/grm-check`.

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
| `paths` | optional | Glob patterns, relative to the session's working directory, that make Claude Code load the skill automatically when the user works on matching files (`chapters/travel/trips/**`). Scope it narrowly: a matching edit loads the whole skill into context. Grimoire skills declare it in their own `SKILL.md`; registration copies it through. |

The auto-invocation policy and per-agent support matrix live in
[agent configuration](agent_configuration.md).

The body either runs a rite or loads an invocation, following the same boundary
that separates rites from invocations:

- **Rite-backed**: the body runs `{{ARCANA_PATH}}/bin/arcana <name>` and reports the result.
- **Invocation-backed**: the body names its invocation with a `cat` directive, and the registration rite inlines that file into the generated skill:

```text
!`cat {{ARCANA_PATH}}/invocations/<area>/<name>.md`
```

The directive is a build-time instruction, not a runtime one. `sync_skills.py`
replaces it with the invocation's body (frontmatter dropped, wrapped in
`BEGIN INLINED` / `END INLINED` comments naming the file), substitutes
`{{ARCANA_PATH}}`, `{{GRIMOIRE_PATH}}`, and `ARCANA_HOME/`, and repeats the
expansion for directives inside the inlined text. A generated skill is therefore
self-contained: no shell command runs when it loads, so it works from any
working directory and under an agent policy that disables skill shell
execution. Agents only honour a runtime `cat` for files inside the session's
working directories, which the engine almost never is; that is why the rite
inlines rather than defers. Keep each generated skill under 500 lines, the
Agent Skills guidance; the rite's tests enforce it for the shipped catalog.

## Reusable Rites

A rite may support more than one target through flags such as `--grimoire`, but user-facing skills must not be target-polymorphic. Expose one clear skill per target and let both skills call the same rite when reuse is appropriate.

Good:

```text
/arc-validate frontmatter
/grm-check frontmatter
```

Avoid when the operation can target both Arcana and a grimoire:

```text
/arc-validate frontmatter
```

That name is correct for Arcana only. If users also need to validate a grimoire, provide the grimoire-targeted skill as a separate command.

## Source Layout

Arcana skill source folders are grouped by command family, then flattened during registration:

```text
skills/arc/validate/SKILL.md            -> /arc-validate
skills/arc/update/SKILL.md              -> /arc-update
skills/grm/check/SKILL.md               -> /grm-check
skills/grm/add/SKILL.md                 -> /grm-add
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
invocations/grm/...   -> /grm-*
invocations/arc/...    -> /arc-*
invocations/meta/...   -> shared fragments and templates only
```

Shared rites may live once under `rites/` and accept flags such as `--grimoire`; user-facing skills and invocation docs remain target-specific.
