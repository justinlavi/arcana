# Arcana Recovery

This is the stable recovery entry point for stale Arcana installations.

Use it when slash commands are missing, old, renamed, incorrectly prefixed, or
otherwise untrustworthy after Arcana has changed significantly. This file is
root-level on purpose: after a user pulls Arcana by any Git client, both humans
and AI agents can find it without relying on registered skills.

Do not rename this file without leaving an equivalent root-level replacement.

## Human Quick Start

1. Pull Arcana with any Git tool you trust: SmartGit, GitHub Desktop, Git Bash,
   or a terminal.
2. Open a fresh AI-agent session.
3. Tell the agent:

```text
Read ~/grimoires/arcana/RECOVERY.md and follow the AI Recovery Playbook.
Do not rely on installed slash commands until recovery re-registers skills.
```

If Arcana lives somewhere else, give the agent the real path to this file.

## AI Recovery Playbook

The installed slash-command layer may be stale. Treat the pulled Arcana source
tree as the source of truth, not the agent's currently registered skill files.

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

### 7. Check The Active Grimoire

Resolve the active grimoire from the current working directory or from
`~/grimoires/library.json`, then run:

```bash
python3 rites/validate.py --grimoire GRIMOIRE_ROOT --summary
```

If the grimoire fails because Arcana's scaffold/schema expectations changed,
tell the user recovery succeeded but the grimoire needs `/grm-improve` or the
current source workflow in `invocations/grimoire/improve_grimoire.md`.

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
- [Update Arcana from a grimoire](invocations/grimoire/update_arcana.md)
