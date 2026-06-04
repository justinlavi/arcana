# Arcana Update

This is the stable, **skill-less** entry point for bringing **Arcana and every
grimoire in the library up to the current version**. It is the dependable path
when the installed `/arc-*` / `/grm-*` slash commands are missing, old, renamed,
incorrectly prefixed, or otherwise untrustworthy — and, more generally, the way
to self-update from the source tree when you cannot trust the skill layer.

It needs only the pulled Arcana source and `python3`, and lives at the
repository root. Start the update by running `/grm-update` (or `/arc-update`), or
by following the Human Quick Start below.

## Human Quick Start

1. Pull Arcana with any Git tool you trust: SmartGit, GitHub Desktop, Git Bash,
   or a terminal.
2. Open a fresh AI-agent session.
3. Tell the agent:

```text
Read ~/grimoires/arcana/UPDATE.md and follow the AI Update Playbook.
Do not rely on installed slash commands until the update re-registers skills.
```

If Arcana lives somewhere else, give the agent the real path to this file.

## AI Update Playbook

The installed slash-command layer may be stale. Treat the pulled Arcana source
tree as the source of truth, not the agent's currently registered skill files.
Run every command exactly as written and **report each rite's own machine output
(`--format json`) — never a number you counted yourself.** "Skills
re-registered" is asserted only by quoting `sync_skills`' counts; "a grimoire
is current" only by its pull classification plus a clean validate.

### 0. Resolve Arcana

Prefer the directory containing this file; otherwise `cd ~/grimoires/arcana`. If
neither exists, ask the user for the Arcana checkout path. Pin it:

```bash
ARCANA="$(git -C ~/grimoires/arcana rev-parse --show-toplevel)"
```

### 1. Pull Arcana (public; almost always fast-forwards)

```bash
git -C "$ARCANA" status --short          # if dirty: STOP, report, do not pull or force
GIT_TERMINAL_PROMPT=0 git -C "$ARCANA" pull --ff-only
git -C "$ARCANA" rev-parse HEAD && cat "$ARCANA/VERSION"
```

A non-fast-forward (local commits) or a dirty tree is a STOP: report it and let
the user resolve it. Never force. Run the rest from the now-current source.

### 2. Validate the Arcana source (gate)

```bash
python3 "$ARCANA/rites/validate.py" --summary --format json
```

If status is not `ok` (exit non-zero), STOP and report the failing validators
before any skill or grimoire mutation.

### 3. Update everything — one command

```bash
python3 "$ARCANA/rites/summon.py" --update --apply --format json
```

This is the deterministic core. In one pass it:

- reconciles `~/grimoires/library.json` against disk,
- **pulls every grimoire in the library** — branch-aware: it fetches, and
  fast-forwards a clean branch that is behind its upstream,
- re-registers Arcana and grimoire skills with `--reset-managed` (the path that
  removes stale namespaces, not a best-effort register), and
- **heals only the grimoires it confirmed current** (re-syncs Arcana-owned
  managed scaffold, refreshes each grimoire README's update block, repairs
  wikilinks, re-validates).

**Quote the envelope** in your report: the `grimoire_summary` counts, each
grimoire's `status`, and the `sync_skills` `registered`/`reset`/`cleaned`
counts. If a grimoire appears under `needs_manual_pull`, it could **not** be
brought current (a private host's auth, offline, a dirty or diverged tree). The
update **did not touch it** — healing a stale tree would re-derive upstream work
and cause divergence. List each such grimoire verbatim as:

> NOT updated — pull it yourself with your tokens, then re-run: `git -C <path> pull --ff-only`

A per-grimoire failure never aborts the run; the rest are still brought current.

If the dry run helps first, run `--update` without `--apply` to see the
per-grimoire classification before writing.

### 4. Refresh the agent routing block

The marked Grimoire block is the one step the rite leaves to judgment, because
the BEGIN/END-vs-heading sentinels make injection non-deterministic. Read
`rites/templates/grimoire_block.md`, `rites/data/agent_targets.json`, and
`invocations/agent/sync_instructions.md`, then replace only the marked block in
each automatic instruction target:

```text
<!-- BEGIN GRIMOIRE KNOWLEDGE BASE -->
...
<!-- END GRIMOIRE KNOWLEDGE BASE -->
```

Preserve all non-Grimoire content exactly. If block boundaries are ambiguous,
stop and ask the user. (`/arc-agent-sync-instructions` does this once skills are
registered.)

### 5. Final gate

```bash
python3 "$ARCANA/rites/summon.py" --check --format json
```

It must report no drift for the grimoires that were brought current. Report the
exit status. Ask the user to open a fresh agent session, because agents cache
skill listings.

### Skill-orphan judgment (only if reported)

If skill re-registration reports `Preserve unowned` entries or `without Arcana
ownership marker` collisions under a managed prefix, those are directories the
rite could not prove it owns — often a skill whose source was renamed or removed.
Apply the propose-then-confirm judgment in
[Reconcile skill orphans](invocations/meta/skill_orphan_reconcile.md): classify
each as a stale Arcana artifact or user-authored, remove the stale ones on one
confirmation, then re-run step 3.

### If the one command cannot run

`summon.py --update` is itself skill-less. If a much older checkout lacks it, the
same work runs as individual rites: `sync_library.py --apply`, then per grimoire
`validate.py --grimoire <root> --summary`, copy each
`GRIMOIRE_STRUCTURE_STALE_MANAGED` / `_MISSING_MANAGED` formula file over the
grimoire's copy (managed scaffold only — never the customized README, root hub,
`grimoire.json`, or `log.md`), ensure the README's update block matches
`formulae/grimoire/README.md`, `repair_links.py --grimoire <root> --apply`,
re-validate, then `register_skills.py --reset-managed`. Pull each grimoire first
(`git -C <root> pull --ff-only`); never heal a grimoire you could not bring
current.

## Related Current Source

- [README](README.md)
- [Installation](docs/installation.md)
- [Agent configuration](docs/agent_configuration.md)
- [Summoning contract](docs/summoning_contract.md)
- [Register agent skills](invocations/agent/sync_skills.md)
- [Reconcile skill orphans](invocations/meta/skill_orphan_reconcile.md)
- [Update from a grimoire](invocations/grimoire/update.md)
