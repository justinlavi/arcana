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

### 1. Run the registration rite

```bash
python3 ARCANA_HOME/rites/register_skills.py
```

On Windows, use `python` instead of `python3`.

### 2. Report the result

Tell the user how many skills were registered, how many stale registrations were cleaned, and which agent targets were written.

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

## Related

- Active-grimoire registration: [`../grimoire/register_skills.md`](../grimoire/register_skills.md)
- Agent block update: [`update_agent_block.md`](update_agent_block.md)
- Agent configuration: [`../../docs/agent_configuration.md`](../../docs/agent_configuration.md)
