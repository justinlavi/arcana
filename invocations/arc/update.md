---
type: playbook
title: "Update"
aliases: ["update", "arc-update", "sync"]
tags: [arcana/invocations, type/playbook, scope/arcana]
authority: grimoire
last_verified: 2026-11-12
---

# Invocation: Update (Arcana + grimoires, platform scope)

## Purpose

Bring an Arcana install (engine source, library, agent skills, agent routing
blocks) and every grimoire that references it to a current, validated,
synchronized state. This is the maintainer mirror of `/grm-update`: both run
the one canonical Update procedure, and both take the same scopes for
reconciling one local surface without pulling. The difference is reach: the
`skills` scope here registers every installed grimoire's skills, not only the
active grimoire's.

## Invocation

```
/arc-update              # everything: pull, validate, re-register, refresh, heal
/arc-update skills       # register Arcana's skills and every installed grimoire's skills
/arc-update library      # reconcile ~/grimoires/library.json with the folders on disk
/arc-update agentfile    # create or refresh the Grimoire routing block in the agent files
```

## Routing

Read the positional scope and run only its section.

---

## Bare: the full update

The canonical, skill-less procedure is **[[UPDATE|UPDATE]]** at the Arcana
root. Read it and follow the AI Update Playbook exactly.

```bash
cat ARCANA_HOME/UPDATE.md
```

---

## Scope: `skills`

Mutation profile: `plan_apply` via `rites/sync_skills.py`.

```bash
ARCANA_HOME/bin/arcana sync_skills                          # Arcana + every library grimoire
ARCANA_HOME/bin/arcana sync_skills --dry-run                # preview
ARCANA_HOME/bin/arcana sync_skills --reset-managed          # replace the managed namespaces, register fresh
ARCANA_HOME/bin/arcana sync_skills --agent claude|codex     # one target
```

Report the registered and cleaned counts, any collisions, and the targets
written, from the `--format json` envelope when an orchestrator needs it.
The `arc-`, `grm-`, and grimoire prefixes are Arcana-owned namespaces: any
directory under one that is not in the current catalog is removed; skills
outside every managed prefix are never touched. Supported `--agent` values
come from `ARCANA_HOME/rites/data/agent_targets.json`.

---

## Scope: `library`

Mutation profile: `plan_apply` via `rites/sync_library.py`.

1. Dry run: `ARCANA_HOME/bin/arcana sync_library`.
2. Call out missing, stale, or mismatched entries (fixable with `--apply`),
   unmanaged directories (`/grm-setup <folder>` registers one, or move it out
   of the home), and skill-prefix collisions.
3. Apply on request: `ARCANA_HOME/bin/arcana sync_library --apply`,
   then the `skills` scope. Arcana itself is excluded from the scan; unknown
   fields on existing entries are preserved; entries are sorted by key.
   `--home <path>` targets an alternate home for testing.

---

## Scope: `agentfile`

Mutation profile: `plan_apply` via `rites/inject_agent_file.py`, with a
judgment edit for the cases a rite cannot decide.

1. Plan: `ARCANA_HOME/bin/arcana inject_agent_file`. Targets come from
   the `instruction_mode: auto` entries of
   `ARCANA_HOME/rites/data/agent_targets.json`. A missing file is created
   with the block; one clean marked region is refreshed; anything else is
   reported for review.
2. Apply: `ARCANA_HOME/bin/arcana inject_agent_file --apply`
   (`--agent claude|codex`, `--format json`).
3. Review targets and user-specified or project-level files (a repository
   `AGENTS.md`, `CLAUDE.md`, `.github/copilot_instructions.md`): replace any
   routing block in any form with the canonical block from
   `ARCANA_HOME/rites/templates/grimoire_block.md`, or insert it after the
   first top-level heading when there is none. Never rewrite anything outside
   the markers; never edit a project-level file without explicit confirmation;
   do not scan all of `$HOME`.

---

## Related

- Canonical procedure: [[UPDATE|UPDATE]]
- Grimoire-user mirror: [[invocations/grm/update|update]]
- Agent targets: [[docs/agent_targets|agent targets]]
- Agent configuration: [[docs/agent_configuration|agent configuration]]
- Canonical routing block: `ARCANA_HOME/rites/templates/grimoire_block.md`
