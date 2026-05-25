---
type: playbook
title: "Update Arcana From A Grimoire"
aliases: ["update-arcana", "arcana-update", "upgrade-arcana"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Update Arcana From A Grimoire

## Purpose

Update the local Arcana installation from the active grimoire user's point of view, then refresh the pieces normal users actually rely on: the local library, agent skill registrations, agent routing block, Arcana validation status, and active-grimoire scaffold health.

This is the "one command after Arcana changed upstream" workflow for normal grimoire users. It is not a maintainer workflow and must not edit Arcana source files except through `git pull --ff-only`.

## Invocation

From a registered grimoire, or from a workspace where the active grimoire can be resolved from `~/grimoires/library.json`:

```
/grm-update-arcana
```

## Preconditions

!`cat ARCANA_HOME/invocations/meta/grimoire_directory_guard.md`

## Workflow

### 1. Inspect Arcana git state

Run:

```bash
git -C ARCANA_HOME status --short
git -C ARCANA_HOME remote -v
```

If Arcana is not a Git checkout, stop and explain that it cannot be updated with this skill. If Arcana has local changes, do not pull automatically; report the changed files and ask the user whether they want to handle them first.

### 2. Pull the latest Arcana

Only when the Arcana worktree is clean:

```bash
git -C ARCANA_HOME pull --ff-only
```

Use `--ff-only` so the update never creates merge commits or rewrites local history.

### 3. Reconcile the local grimoire library

```bash
python3 ARCANA_HOME/rites/sync_library.py --apply
```

On Windows, use `python` instead of `python3`.

### 4. Validate Arcana after the pull

```bash
python3 ARCANA_HOME/rites/validate.py --summary
```

If this fails, stop and report the failing validators. Do not continue to skill registration from a broken Arcana installation.

### 5. Register skills for Arcana plus the active grimoire

```bash
python3 ARCANA_HOME/rites/register_skills.py --grimoire GRIMOIRE_ROOT
```

This refreshes Arcana-shipped `/arc-*` and `/grm-*` commands and the active grimoire's own `<skill prefix>-*` commands without scanning every installed grimoire.

### 6. Refresh the agent routing block if needed

Read `ARCANA_HOME/rites/data/agent_targets.json` and compare
`ARCANA_HOME/rites/templates/grimoire_block.md` against the marked Grimoire
block in automatic instruction targets (`instruction_mode: auto`).

If a marked block exists and differs, replace only the marked block. If the block boundaries are ambiguous, stop and ask. Preserve all non-Grimoire content exactly. This follows the same safety rules as `/arc-agent-update`, but is included here so the normal update workflow stays one command.

### 7. Check active-grimoire health

Run the current deterministic grimoire validator profile against the active grimoire:

```bash
python3 ARCANA_HOME/rites/validate.py --grimoire GRIMOIRE_ROOT --summary
```

If it reports missing or stale managed scaffold files, tell the user that Arcana updated successfully but the grimoire needs `/grm-improve` to apply scaffold/schema upgrades. Do not perform broad grimoire edits inside this command.

### 8. Report summary

End with:

- Whether Arcana was already current or updated to a new revision.
- Whether Arcana validation passed.
- Whether skills were registered.
- Whether agent instruction blocks were updated, already current, skipped, or need a user decision.
- Whether the active grimoire passed the structure check, or should run `/grm-improve`.
Include the resolved active grimoire path in the summary.

## Related

- Active-grimoire improvement: [[invocations/grimoire/improve_grimoire|improve grimoire]]
- Active-grimoire skill registration: [[invocations/grimoire/register_skills|register skills]]
- Global agent registration: [[invocations/agent/register_skills|register skills]]
- Agent block update: [[invocations/agent/update_agent_block|update agent block]]
- Agent targets: [[docs/agent_targets|agent targets]]
