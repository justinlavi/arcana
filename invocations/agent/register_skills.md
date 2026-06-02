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

For major Arcana command-family changes, use `--reset-managed` to replace the
registered Arcana and grimoire skill namespaces from current source. This is
the supported version of manually deleting old `/arc-*`, `/grm-*`, and
domain-prefixed skill directories before re-registering.

### 1. Run the registration rite

```bash
python3 ARCANA_HOME/rites/register_skills.py
```

On Windows, use `python` instead of `python3`.

### 2. Report the result

Tell the user how many skills were registered, how many owned stale
registrations were cleaned, how many unowned directories were preserved, any
collisions, and which agent targets were written.

### 3. Reconcile orphaned skill directories (optional)

If the rite reported `Preserve unowned` entries or `without Arcana ownership
marker` collisions under a managed prefix, some may be stale Arcana artifacts the
rite could not prove it owns - most often a skill whose source was renamed or
removed, leaving the old registration behind. Apply the propose-then-confirm
judgment in [[invocations/meta/skill_orphan_reconcile|skill orphan reconcile]] to
classify and, on one confirmation, remove them - then re-register. Skip this when
the rite reported no preserved or collided managed-prefix directories.

### 4. Optional flags

Preview without writing:

```bash
python3 ARCANA_HOME/rites/register_skills.py --dry-run
```

Preview a managed-namespace reset:

```bash
python3 ARCANA_HOME/rites/register_skills.py --reset-managed --dry-run
```

Replace managed namespaces and register fresh copies:

```bash
python3 ARCANA_HOME/rites/register_skills.py --reset-managed
```

Target one supported agent:

```bash
python3 ARCANA_HOME/rites/register_skills.py --agent codex
python3 ARCANA_HOME/rites/register_skills.py --agent claude
```

Supported `--agent` values come from
`ARCANA_HOME/rites/data/agent_targets.json`; see
`ARCANA_HOME/docs/agent_targets.md` for the human-readable matrix.

Add `--format json` (or `jsonl`) for the shared `ResultReporter` outcome
envelope - registered/cleaned mutations, collisions and preserved-unowned dirs as
messages, and summary counts - so an orchestrator can verify the result instead
of parsing prose.

## Related

- Active-grimoire registration: [[invocations/grimoire/register_skills|register skills]]
- Reconcile stale/renamed skill orphans: [[invocations/meta/skill_orphan_reconcile|skill orphan reconcile]]
- Agent block update: [[invocations/agent/update_agent_block|update agent block]]
- Agent targets: [[docs/agent_targets|agent targets]]
- Agent configuration: [[docs/agent_configuration|agent configuration]]
