---
type: playbook
title: "Register Agent Skills"
aliases: ["register-agent-skills", "refresh-agent-skills"]
tags: [arcana/invocations, type/playbook, scope/agent]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Register Agent Skills

## Purpose

Register Arcana-shipped skills and every installed grimoire's own skills into supported agent skill directories.

Use this global command after Arcana skill changes, after installing or removing grimoires, or when slash-command pickers are stale across the whole workspace. For active-grimoire-only registration, use `/grm-register-skills`.

## Invocation

```
/arc-agent-register-skills
```

## Workflow

Mutation profile: `plan_apply` via `rites/register_skills.py`. This
invocation may apply directly when the user asks to register skills; use
`--dry-run` when the user asks for a preview or when reviewing target changes.
The plan reports creates, updates, owned stale cleanups, unowned preserves,
and collisions. Apply mode refuses to overwrite unowned skill directories.
Generated pointer skills without ownership metadata are rewritten when their
provenance points back to an Arcana or grimoire skill source.

### 1. Run the registration rite

```bash
python3 ARCANA_HOME/rites/register_skills.py
```

On Windows, use `python` instead of `python3`.

### 2. Report the result

Tell the user how many skills were registered, how many owned stale
registrations were cleaned, how many unowned directories were preserved, any
collisions, and which agent targets were written.

### 3. Optional flags

Preview without writing:

```bash
python3 ARCANA_HOME/rites/register_skills.py --dry-run
```

Target one supported agent:

```bash
python3 ARCANA_HOME/rites/register_skills.py --agent codex
python3 ARCANA_HOME/rites/register_skills.py --agent claude
```

Supported `--agent` values come from
`ARCANA_HOME/rites/data/agent_targets.json`; see
`ARCANA_HOME/docs/agent_targets.md` for the human-readable matrix.

## Related

- Active-grimoire registration: [[invocations/grimoire/register_skills|register skills]]
- Agent block update: [[invocations/agent/update_agent_block|update agent block]]
- Agent targets: [[docs/agent_targets|agent targets]]
- Agent configuration: [[docs/agent_configuration|agent configuration]]
