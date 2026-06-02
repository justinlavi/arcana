# Arcana Restoration & Self-Update

This is the stable, **skill-less** entry point for bringing **Arcana and any
grimoire up to the current version**. It is the dependable path when the
installed `/arc-*` / `/grm-*` slash commands are missing, old, renamed,
incorrectly prefixed, or otherwise untrustworthy — and, more generally, the way
to self-update from the source tree when you cannot trust the skill layer.

It needs only the pulled Arcana source and `python3`, and lives at the
repository root.

Start restoration by running `/grm-restore` (or `/arc-restore`), or by following
the Human Quick Start below.

## Human Quick Start

1. Pull Arcana with any Git tool you trust: SmartGit, GitHub Desktop, Git Bash,
   or a terminal.
2. Open a fresh AI-agent session.
3. Tell the agent:

```text
Read ~/grimoires/arcana/RESTORATION.md and follow the AI Restoration Playbook.
Do not rely on installed slash commands until restoration re-registers skills.
```

If Arcana lives somewhere else, give the agent the real path to this file.

## AI Restoration Playbook

The installed slash-command layer may be stale. Treat the pulled Arcana source
tree as the source of truth, not the agent's currently registered skill files.

### Structured shortcut

For a machine-readable view of the offline, deterministic part of this playbook
(steps 3-5), run the engine directly:

```bash
python3 rites/summon.py --check --format json     # report drift, read-only
python3 rites/summon.py --reconcile --apply       # reconcile library + re-register skills
```

`--check` exits non-zero when there is drift; `--reconcile --apply` refuses on a
base that fails `validate.py`, preserves stale library entries unless `--prune`
is given, and reports (never rewrites) agent instruction blocks. Every run writes
`~/.cache/grimoire/summon-last.json`. The network pull (step 2) and agent-block
refresh (step 6) remain manual. The numbered steps below stay authoritative when
the shortcut reports something it cannot fix.

### 1. Resolve Arcana

Prefer the directory containing this file. If the user only gave a conventional
install, use:

```bash
cd ~/grimoires/arcana
```

If that path does not exist, ask the user for the Arcana checkout path.

### 2. Inspect Current State

Run:

```bash
git status --short
git rev-parse --show-toplevel
```

If the worktree has local changes, report them before pulling or overwriting
anything. If the user already pulled Arcana, continue.

If the user explicitly asks you to update Arcana and the worktree is clean:

```bash
git pull --ff-only
```

### 3. Rebuild Local Registry State

Refresh `~/grimoires/library.json` from the grimoires on disk:

```bash
python3 rites/sync_library.py --apply
```

On Windows, use `python` instead of `python3`.

### 4. Validate Arcana Source

Run:

```bash
python3 rites/validate.py --summary
```

If validation fails, stop and report the failing validators. Do not treat
registered skills as repaired until Arcana source validation is understood.

### 5. Reset And Re-register Agent Skills

For major Arcana updates, use reset mode. It replaces currently registered
Arcana and grimoire skill namespaces, then writes fresh skills from current
source.

Preview first:

```bash
python3 rites/register_skills.py --reset-managed --dry-run
```

If the plan is scoped to supported agent skill directories and the user agrees,
apply it:

```bash
python3 rites/register_skills.py --reset-managed
```

This is the supported path for migrations such as old all-`/grm-*` installs
moving to current `/arc-*`, `/grm-*`, and domain-prefixed skill families.

If registration reports `Preserve unowned` entries or `without Arcana ownership
marker` collisions under a managed prefix, those are directories the rite could
not prove it owns - often a skill whose source was renamed or removed. Apply the
propose-then-confirm judgment in
[Reconcile skill orphans](invocations/meta/skill_orphan_reconcile.md): classify
each as a stale Arcana artifact or user-authored, remove the stale ones on one
confirmation, then re-register.

### 6. Refresh Agent Routing Instructions

Do not assume the agent instruction block is current. Read:

- `rites/templates/grimoire_block.md`
- `rites/data/agent_targets.json`
- `invocations/agent/update_agent_block.md`

For automatic instruction targets, replace only the marked Grimoire block:

```text
<!-- BEGIN GRIMOIRE KNOWLEDGE BASE -->
...
<!-- END GRIMOIRE KNOWLEDGE BASE -->
```

Preserve all non-Grimoire content exactly. If block boundaries are ambiguous,
stop and ask the user.

### 7. Bring The Active Grimoire Current (skill-less)

Restoration is not finished until the grimoire itself is current, and this must work
**without** `/grm-*` skills. Resolve the
grimoire root (from the working directory or `~/grimoires/library.json`, whose
`local_path` uses a `$HOME` token — expand it before passing it to `--grimoire`),
then run the deterministic rites directly from the Arcana checkout:

1. See what drifted:

   ```bash
   python3 rites/validate.py --grimoire GRIMOIRE_ROOT --summary
   ```

2. Re-sync managed scaffold. For every `GRIMOIRE_STRUCTURE_STALE_MANAGED` or
   `GRIMOIRE_STRUCTURE_MISSING_MANAGED` finding, copy the current Arcana formula
   over the grimoire's copy — these files are Arcana-owned and safe to overwrite:

   ```bash
   cp formulae/grimoire/<reported/path> GRIMOIRE_ROOT/<reported/path>
   ```

   Only the managed scaffold paths the validator names. The root `README.md`,
   root hub, `grimoire.json`, and `log.md` are customized per grimoire and are
   *not* managed-compared — never overwrite them this way.

3. Repair wikilinks a structural change may have broken:

   ```bash
   python3 rites/repair_links.py --grimoire GRIMOIRE_ROOT            # preview
   python3 rites/repair_links.py --grimoire GRIMOIRE_ROOT --apply    # write unambiguous repairs
   ```

   Ambiguous links are reported, never guessed — resolve those by hand.

4. Apply the heal blocks under [Version Migrations](#version-migrations). Each is
   idempotent, so apply them all — you do not need to know which version the
   grimoire is on.

5. Re-validate until clean:

   ```bash
   python3 rites/validate.py --grimoire GRIMOIRE_ROOT --summary
   ```

Only failures that need **content judgment** (not a mechanical fix) fall back to
the grimoire-improvement workflow in
[invocations/grimoire/improve_grimoire.md](invocations/grimoire/improve_grimoire.md) —
read and follow that invocation's steps directly from source; the `/grm-improve`
skill does **not** need to be registered for you to do so.

### 8. Finish With A Clear Summary

Report:

- Arcana path and git state.
- Whether Arcana validation passed.
- Whether library sync changed anything.
- Whether skills were reset and re-registered.
- Which agent instruction files were updated, skipped, or need user input.
- Which active grimoire was checked and whether it needs follow-up.

Ask the user to open a fresh agent session after skill registration, because
agents may cache skill listings.

## Version Migrations

When an Arcana change alters what a *current* grimoire must look like, its exact,
skill-less heal steps are recorded here, keyed by the version that introduced the
change. Apply **every** heal block below, oldest first, then re-run step 7's
validation. Each block is idempotent and safe to re-run on an already-current
grimoire.

<!-- Add a "### vX.Y.Z - <what changed>" block whenever a release changes the
     shape a current grimoire must have. A release that needs no grimoire-side
     change needs no entry. -->

### v1.1.0 - Restoration block in the grimoire README

Every grimoire README carries a marker-delimited Restoration block (the two entry points: the `/grm-restore` skill, or telling an AI agent to pull Arcana and follow its restoration process). If this grimoire's `README.md` is missing it, inject it from the formula:

1. Read the block between `<!-- BEGIN ARCANA RESTORATION -->` and `<!-- END ARCANA RESTORATION -->` in `formulae/grimoire/README.md`.
2. In the grimoire's root `README.md`: if the markers are absent, insert the block (markers included) **immediately before the first second-level (`##`) heading** — in a standard grimoire README that is the `## Installation` line. If the markers are present, replace everything between them with the formula's current block. (If a `## Out of date? Restore.` heading exists *without* the markers — a degraded earlier injection — replace that heading's section with the marked block instead of adding a second copy.)

Idempotent: re-running converges the grimoire's block to the formula's.

Beyond the blocks above, step 7's mechanical pass (re-sync managed scaffold, repair links, re-validate) brings any grimoire current.

## Last-resort Notes

Avoid manual deletion when `--reset-managed` is available. If a much older
Arcana checkout does not support that flag, pull Arcana again and re-open this
file from the updated checkout. Manual deletion of agent skill directories
should be a user-approved last resort, scoped to known Arcana and grimoire
prefixes only.

## Related Current Source

- [README](README.md)
- [Installation](docs/installation.md)
- [Agent configuration](docs/agent_configuration.md)
- [Skill schema](docs/skill_schema.md)
- [Register agent skills](invocations/agent/register_skills.md)
- [Reconcile skill orphans](invocations/meta/skill_orphan_reconcile.md)
- [Restore from a grimoire](invocations/grimoire/restore.md)
