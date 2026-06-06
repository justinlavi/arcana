---
type: playbook
title: "Sync Local Grimoire Setup"
aliases: ["sync", "sync-grimoire", "refresh-grimoire-setup"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-06-06
---

# Invocation: Sync Local Grimoire Setup

## Purpose

Reconcile the user's local Grimoire setup with reality across the three things that drift on a working machine, selected by an optional positional sub-target. This is the everyday user mirror of `/arc-sync`, so a grimoire user never needs the maintainer command:

- `skills` — register Arcana-shipped skills and the active grimoire's own skills into supported agent skill directories. Rite: `rites/sync_skills.py`.
- `library` — reconcile `~/grimoires/library.json` against the actual state of `~/grimoires/` after a grimoire folder is moved, renamed, or removed. Rite: `rites/sync_library.py`.
- `agentfile` — create or refresh the marked Grimoire routing block in the agent instruction files (`~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, ...). Rite: `rites/inject_agent_file.py`, with a judgment fallback for ambiguous files.

A bare `/grm-sync` reconciles all three and reports every scope, including those it leaves unchanged.

## Invocation

```
/grm-sync
/grm-sync skills
/grm-sync library
/grm-sync agentfile
```

## Preconditions

!`cat ARCANA_HOME/invocations/meta/grimoire_directory_guard.md`

The guard resolves `GRIMOIRE_ROOT` for the `skills` scope. The `library` and `agentfile` scopes operate on the whole `~/grimoires/` home and the user's agent files, so they do not depend on which grimoire is active.

## Routing

Read the positional sub-target and run the matching section. With no sub-target, run **all three** in order (skills, library, agentfile) and finish with the combined accounting in [Bare invocation](#bare-invocation).

---

## Sub-target: `skills`

Mutation profile: `plan_apply` via `rites/sync_skills.py`. Apply directly when the user asks to sync skills; use `--dry-run` for a preview.

```bash
python3 ARCANA_HOME/rites/sync_skills.py --grimoire GRIMOIRE_ROOT
```

On Windows, use `python` instead of `python3`. Then tell the user how many Arcana and active-grimoire skills were registered, how many owned stale registrations were cleaned, how many unowned directories were preserved, any collisions, and which agent targets were written.

If the rite reports `Preserve unowned` entries or `without Arcana ownership marker` collisions under this grimoire's prefix, apply the propose-then-confirm judgment in [[invocations/meta/skill_orphan_reconcile|skill orphan reconcile]] to classify and, on one confirmation, remove stale Arcana artifacts - then re-register.

Optional flags: `--dry-run` (preview), `--reset-managed` (replace managed namespaces after major command-family changes), `--agent claude|codex` (one target), `--format json` (structured envelope).

---

## Sub-target: `library`

Mutation profile: `plan_apply` via `rites/sync_library.py`. Reconcile `~/grimoires/library.json` against the actual state of `~/grimoires/` — the fix when a grimoire folder was moved or renamed (in Finder, Obsidian, or a file manager) and the agent can no longer find it.

### 1. Report the drift (dry-run)

```bash
python3 ARCANA_HOME/rites/sync_library.py
```

### 2. Show the report

Call out missing, stale, and mismatched entries (the rite can fix these with `--apply`) and any unmanaged directories. An unmanaged directory has no `grimoire.json`: to make it a grimoire use `/grm-create`, or move it out of `~/grimoires/` if it is not one.

### 3. Apply on request

```bash
python3 ARCANA_HOME/rites/sync_library.py --apply
```

After a successful change, run the `skills` sub-target so any newly resolved grimoire's skills register.

---

## Sub-target: `agentfile`

Mutation profile: `plan_apply` via `rites/inject_agent_file.py`. Create or refresh the marked Grimoire routing block in the agent instruction files. This is the fix when the agent stopped following the library — its routing block went stale, or the file was deleted (for example after deleting `~/.codex/` or moving to a new machine).

### 1. Report what each agent file needs (plan)

```bash
python3 ARCANA_HOME/rites/inject_agent_file.py
```

The rite classifies each automatic instruction target: a missing file will be **created** with the canonical block; a block-less file will get one **inserted**; a single clean marked region will be **refreshed**; a file with duplicate or malformed markers is reported **ambiguous** and left untouched.

### 2. Apply the deterministic changes

```bash
python3 ARCANA_HOME/rites/inject_agent_file.py --apply
```

Creating a missing file and refreshing one clean marked region are deterministic and safe. Target one agent with `--agent claude|codex`.

### 3. Resolve ambiguous targets by judgment

For any target the rite reports as `ambiguous` (duplicate or malformed markers, or a block tangled with hand-authored content), apply the conservative patch procedure in [[invocations/arc/sync|sync]] (the `agentfile` sub-target): replace only the marked region, preserve all non-Grimoire content, and stop and ask if the boundaries are unclear. Never rewrite a project-level instruction file without confirmation.

---

## Bare invocation

With no sub-target, reconcile all three scopes for the user's environment, then report each one in a single accounting — including a scope that changed nothing — so a green run never hides a moved grimoire or a missing routing block:

1. `skills` — apply, then state the registered/cleaned counts.
2. `library` — run the dry-run; if it reports fixable drift, apply it and state what was corrected, otherwise state "in sync".
3. `agentfile` — run the plan; apply the deterministic create/insert/refresh actions and state what changed; name any ambiguous target that still needs the judgment edit.

End with one line per scope, for example: `Skills: registered 23. Library: in sync. Agent file: created AGENTS.md; CLAUDE.md already current.`

## Related

- Maintainer mirror (every installed grimoire, plus library and agent files at platform scope): [[invocations/arc/sync|sync]]
- Bring Arcana and every grimoire fully current: [[invocations/grm/update|update]]
- Reconcile stale/renamed skill orphans: [[invocations/meta/skill_orphan_reconcile|skill orphan reconcile]]
- Agent targets: [[docs/agent_targets|agent targets]]
- Agent configuration: [[docs/agent_configuration|agent configuration]]
