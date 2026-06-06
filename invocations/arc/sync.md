---
type: playbook
title: "Sync Arcana Environment"
aliases: ["sync", "arc-sync"]
tags: [arcana/invocations, type/playbook, scope/arcana]
authority: grimoire
last_verified: 2026-06-05
---

# Invocation: Sync Arcana Environment

## Purpose

Sync the local environment to current Arcana. One command, three scopes, selected
by a single positional sub-target so the platform-wide surfaces (the home library
and user agent files) stay distinct from the active-grimoire surface:

- `skills` — register Arcana-shipped skills and every installed grimoire's skills
  into supported agent skill directories. Rite: `rites/sync_skills.py`.
- `library` — reconcile `~/grimoires/library.json` against the actual state of
  `~/grimoires/`. Rite: `rites/sync_library.py`.
- `agentfile` — refresh the marked Grimoire instruction block inside user agent
  instruction files. AI-guided judgment edit; no rite.

For active-grimoire-only skill registration, use `/grm-sync` instead.

## Invocation

```
/arc-sync skills
/arc-sync library
/arc-sync agentfile
```

## Routing

Read the positional sub-target and run only that section below.

- **No sub-target given:** do not run anything. Tell the user the sub-target is
  required and list `skills`, `library`, and `agentfile` with a one-line summary of
  each, then ask which to run. Never default to "all": `agentfile` rewrites user
  agent instruction files and stays opt-in, so a bare `/arc-sync` must never act.
- **Unknown sub-target:** report it and list the three valid sub-targets.

---

## Sub-target: `skills`

Mutation profile: `plan_apply` via `rites/sync_skills.py`. Apply directly when the
user asks to sync skills; use `--dry-run` for a preview or when reviewing target
changes. The plan reports creates, updates, owned stale cleanups, unowned
preserves, and collisions. Apply mode refuses to overwrite unowned skill
directories. Generated pointer skills without ownership metadata are rewritten when
their provenance points back to an Arcana or grimoire skill source.

For major Arcana command-family changes, use `--reset-managed` to replace the
registered Arcana and grimoire skill namespaces from current source. This is the
supported version of manually deleting old `/arc-*`, `/grm-*`, and domain-prefixed
skill directories before re-registering.

### 1. Run the sync rite

```bash
python3 ARCANA_HOME/rites/sync_skills.py
```

On Windows, use `python` instead of `python3`.

### 2. Report the result

Tell the user how many skills were registered, how many owned stale registrations
were cleaned, how many unowned directories were preserved, any collisions, and
which agent targets were written.

### 3. Reconcile orphaned skill directories (optional)

If the rite reported `Preserve unowned` entries or `without Arcana ownership
marker` collisions under a managed prefix, some may be stale Arcana artifacts the
rite could not prove it owns - most often a skill whose source was renamed or
removed, leaving the old registration behind. Apply the propose-then-confirm
judgment in [[invocations/meta/skill_orphan_reconcile|skill orphan reconcile]] to
classify and, on one confirmation, remove them - then re-register. Skip this when
the rite reported no preserved or collided managed-prefix directories.

### 4. Optional flags

```bash
python3 ARCANA_HOME/rites/sync_skills.py --dry-run                  # preview, no writes
python3 ARCANA_HOME/rites/sync_skills.py --reset-managed --dry-run  # preview a managed-namespace reset
python3 ARCANA_HOME/rites/sync_skills.py --reset-managed            # replace managed namespaces, register fresh
python3 ARCANA_HOME/rites/sync_skills.py --agent codex              # target one supported agent
python3 ARCANA_HOME/rites/sync_skills.py --agent claude
```

Supported `--agent` values come from `ARCANA_HOME/rites/data/agent_targets.json`;
see `ARCANA_HOME/docs/agent_targets.md` for the human-readable matrix.

Add `--format json` (or `jsonl`) for the shared `ResultReporter` outcome envelope -
registered/cleaned mutations, collisions and preserved-unowned dirs as messages,
and summary counts - so an orchestrator can verify the result instead of parsing
prose.

---

## Sub-target: `library`

Mutation profile: `plan_apply` via `rites/sync_library.py`. Reconcile the local
grimoire library (`~/grimoires/library.json`) against the actual state of
`~/grimoires/`. The rite walks the home directory, identifies every valid grimoire,
and reports missing, stale, mismatched, and unmanaged entries.

### 1. Run a dry-run report first

```bash
python3 ARCANA_HOME/rites/sync_library.py
```

### 2. Show the report

Call out:

- Missing, stale, or mismatched entries, which the rite can fix with `--apply`.
- Unmanaged directories, which need either `/arc-adopt` or manual cleanup.
- Skill prefix collisions, which would overwrite each other during skill registration.

### 3. Apply fixes only when requested

```bash
python3 ARCANA_HOME/rites/sync_library.py --apply
```

### 4. Sync skills after successful changes

Run `/arc-sync skills` (or `python3 ARCANA_HOME/rites/sync_skills.py`) to pick up
any newly registered grimoires.

### Notes

- Arcana itself is excluded from the library scan; it is the engine, not a grimoire.
- An unmanaged directory will not be auto-registered. To register it, use
  `/arc-adopt`, add a valid `grimoire.json`, or move it out of `~/grimoires/`.
- The rite preserves unknown fields on existing library entries and only updates
  `local_path` and `online_path`.
- Library entries are sorted alphabetically by key on write.
- `--home /path/to/alt/home` is available for testing.

---

## Sub-target: `agentfile`

Refresh the Grimoire instruction block inside user agent instruction files,
preserving all non-Grimoire content. This is AI-guided judgment work, not a pure
mechanical rewrite: users often keep unrelated project, style, safety, or personal
instructions in the same files. There is no rite for this sub-target.

Canonical block: `ARCANA_HOME/rites/templates/grimoire_block.md`.

Optional user text may name explicit files to update.

### Default targets

Inspect existing files only unless the user explicitly asks to create missing ones.
Default automatic targets come from `ARCANA_HOME/rites/data/agent_targets.json`
entries with `instruction_mode: auto`; see `ARCANA_HOME/docs/agent_targets.md` for
the current matrix.

If the user provides paths, inspect those too. If the current repository contains
`AGENTS.md`, `CLAUDE.md`, `.github/copilot_instructions.md`, or similarly named
agent instruction files, mention them as candidates but ask before modifying
project-level files unless the user explicitly included them.

Do not scan all of `$HOME` by default. If the user asks for "everything on this
machine", ask before running a bounded search and explain the scope.

### 1. Load the canonical block

Read `ARCANA_HOME/rites/templates/grimoire_block.md`. This is the source of truth.
Preserve it exactly when inserting or replacing, aside from surrounding blank lines
needed to fit the target document.

### 2. Inspect each target

For each candidate file:

1. If the file does not exist, skip it by default and report that it was absent.
2. Read the full file before editing.
3. Determine whether it contains a Grimoire block:
  - Preferred: text between `<!-- BEGIN GRIMOIRE KNOWLEDGE BASE -->` and
    `<!-- END GRIMOIRE KNOWLEDGE BASE -->`.
  - Ambiguous: multiple Grimoire sections, malformed markers, or surrounding text
    that looks user-authored. Stop and ask before editing that file.

### 3. Patch conservatively

Apply the smallest safe edit:

- Existing marked block: replace only the marked region with the canonical block.
- No existing block in an existing default target: insert the canonical block after
  the first top-level heading if there is one, otherwise append it to the end. If
  the file is project-level or user-specified but not a default target, ask before
  inserting.

Never rewrite, sort, reflow, or deduplicate non-Grimoire content. Preserve
frontmatter, comments, headings, personal instructions, project rules, and
unrelated agent configuration exactly.

### 4. Review after editing

After editing each file:

- Re-read the file.
- Confirm exactly one Grimoire block is present.
- Confirm the canonical block text appears exactly once.
- Summarize whether the operation was `updated`, `inserted`, `skipped`, or
  `needs user decision`.

### Safety rules

1. Preserve all non-Grimoire content.
2. Do not create missing instruction files unless the user explicitly asks.
3. Do not edit project-level instruction files without explicit user confirmation.
4. Do not replace a whole file when a block-level edit is possible.
5. Ask before editing when the Grimoire block boundaries are ambiguous.
6. Report every file touched.

This sub-target updates instruction files only. If newly added skills also need to
appear in slash-command pickers, run `/arc-sync skills` separately.

## Related

- Active-grimoire skill sync: [[invocations/grm/sync|sync]]
- Reconcile stale/renamed skill orphans: [[invocations/meta/skill_orphan_reconcile|skill orphan reconcile]]
- Adopt an unmanaged directory: [[invocations/arc/adopt|adopt]]
- Agent targets: [[docs/agent_targets|agent targets]]
- Agent configuration: [[docs/agent_configuration|agent configuration]]
- Canonical block: `ARCANA_HOME/rites/templates/grimoire_block.md`
