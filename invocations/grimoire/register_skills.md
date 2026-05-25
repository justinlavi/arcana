---
type: playbook
title: "Register Active Grimoire Skills"
aliases: ["register-grimoire-skills", "refresh-active-grimoire-skills"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Register Active Grimoire Skills

## Purpose

Register Arcana-shipped skills and the active grimoire's own skills into supported agent skill directories.

Use this day-to-day when the user is working inside one grimoire and has added, renamed, or edited that grimoire's `skills/` directory. It refreshes Arcana command families at the same time so the agent remains aligned after Arcana updates, but it does not scan or clean skills for every installed grimoire.

## Invocation

```
/grm-register-skills
```

## Preconditions

!`cat ARCANA_HOME/invocations/meta/grimoire_directory_guard.md`

## Workflow

Mutation profile: `plan_apply` via `rites/register_skills.py`. This
invocation may apply directly when the user asks to register active-grimoire
skills; use `--dry-run` when the user asks for a preview or when reviewing
target changes.
The plan reports creates, updates, owned stale cleanups, unowned preserves,
and collisions. Apply mode refuses to overwrite unowned skill directories.
Generated pointer skills without ownership metadata are rewritten when their
provenance points back to an Arcana or grimoire skill source.

### 1. Run the registration rite for the active grimoire

```bash
python3 ARCANA_HOME/rites/register_skills.py --grimoire GRIMOIRE_ROOT
```

On Windows, use `python` instead of `python3`.

### 2. Report the result

Tell the user how many Arcana and active-grimoire skills were registered, how
many owned stale registrations were cleaned, how many unowned directories were
preserved, any collisions, and which agent targets were written.

### 3. Optional flags

Preview without writing:

```bash
python3 ARCANA_HOME/rites/register_skills.py --grimoire GRIMOIRE_ROOT --dry-run
```

Target one supported agent:

```bash
python3 ARCANA_HOME/rites/register_skills.py --grimoire GRIMOIRE_ROOT --agent codex
python3 ARCANA_HOME/rites/register_skills.py --grimoire GRIMOIRE_ROOT --agent claude
```

Supported `--agent` values come from
`ARCANA_HOME/rites/data/agent_targets.json`; see
`ARCANA_HOME/docs/agent_targets.md` for the human-readable matrix.

## Related

- Global registration: [`../agent/register_skills.md`](../agent/register_skills.md)
- Agent targets: [`../../docs/agent_targets.md`](../../docs/agent_targets.md)
- Agent configuration: [`../../docs/agent_configuration.md`](../../docs/agent_configuration.md)
