---
name: {{SKILL_PREFIX}}-library-sync
description: Scan ~/grimoires/ for valid grimoires and reconcile against the local library (detect missing, stale, mismatched, and unmanaged entries)
when_to_use: User cloned, moved, or removed a grimoire by hand; agent can't find a grimoire that should be installed; library mentions a grimoire that doesn't exist on disk; user mentions "library drift", "missing grimoire", "unmanaged directory", or "after manual git changes in ~/grimoires/". Defaults to a dry-run report; only writes when --apply is passed.
user-invocable: true
allowed-tools: Bash Read
---

# Sync Grimoire Library

You are reconciling the local grimoire library (`~/grimoires/library.json`) against the actual state of `~/grimoires/`. The rite walks the home directory, identifies every valid grimoire (any subdirectory with a well-formed `grimoire.json`), and reports four kinds of drift:

- **Missing** - grimoire on disk but not registered in the library
- **Stale** - library entry whose `local_path` no longer exists or no longer points at a valid grimoire
- **Mismatched** - library entry whose `local_path` differs from where the grimoire actually lives
- **Unmanaged** - directory under `~/grimoires/` with no `grimoire.json` (cannot be auto-registered; reported for cleanup)

It also surfaces structural issues that don't block sync: skill prefix collisions across grimoires, and `grimoire.json` `name` fields that disagree with the directory name.

## Workflow

1. **Run a dry-run report first** so the user can see what would change:

   ```bash
   python3 {{ARCANA_PATH}}/rites/sync_library.py
   ```

2. **Show the user the report**, especially:
  - Any missing/stale/mismatched entries (these will be auto-fixed)
  - Any unmanaged directories (these need manual attention - the rite cannot create a `grimoire.json` for them)
  - Any skill prefix collisions (these will overwrite each other during skill registration)

3. **If the report shows drift and the user wants to apply the fixes**, run with `--apply`:

   ```bash
   python3 {{ARCANA_PATH}}/rites/sync_library.py --apply
   ```

4. **After a successful apply, re-register skills** so newly discovered grimoires are wired into the agent skill directories:

   ```bash
   python3 {{ARCANA_PATH}}/rites/register_skills.py
   ```

   Or invoke `/arc-skills-register`.

## Notes

- Arcana itself is excluded from the library scan (it's the engine, not a grimoire) - the rite recognizes it by `name: "arcana"` in `arcana/arcana.json`.
- An "unmanaged" directory will not be auto-registered. To register it, either add a valid `grimoire.json` to it (then re-run sync) or move it out of `~/grimoires/`.
- The rite preserves any unknown fields on existing library entries (forward-compat); it only updates `local_path` and `online_path`.
- Library entries are sorted alphabetically by key on write for deterministic output.
- An override flag is available for testing: `--home /path/to/alt/home`.
