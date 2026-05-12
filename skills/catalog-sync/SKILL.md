---
name: {{NAMESPACE}}-catalog-sync
description: Scan ~/grimoire/ for valid grimoires and reconcile against the local catalog (detect missing, stale, mismatched, and unmanaged entries)
user-invocable: true
allowed-tools: Bash Read
---

# Sync Grimoire Catalog

You are reconciling the local grimoire catalog (`~/grimoire/catalog.json`) against the actual state of `~/grimoire/`. The rite walks the home directory, identifies every valid grimoire (any subdirectory with a well-formed `grimoire.json`), and reports four kinds of drift:

- **Missing** — grimoire on disk but not registered in the catalog
- **Stale** — catalog entry whose `local_path` no longer exists or no longer points at a valid grimoire
- **Mismatched** — catalog entry whose `local_path` differs from where the grimoire actually lives
- **Unmanaged** — directory under `~/grimoire/` with no `grimoire.json` (cannot be auto-registered; reported for cleanup)

It also surfaces structural issues that don't block sync: namespace collisions across grimoires, and `grimoire.json` `name` fields that disagree with the directory name.

## Workflow

1. **Run a dry-run report first** so the user can see what would change:

   ```bash
   python3 {{ARCANA_PATH}}/rites/sync_catalog.py
   ```

2. **Show the user the report**, especially:
   - Any missing/stale/mismatched entries (these will be auto-fixed)
   - Any unmanaged directories (these need manual attention — the rite cannot create a `grimoire.json` for them)
   - Any namespace collisions (these will overwrite each other during skill registration)

3. **If the report shows drift and the user wants to apply the fixes**, run with `--apply`:

   ```bash
   python3 {{ARCANA_PATH}}/rites/sync_catalog.py --apply
   ```

4. **After a successful apply, re-register skills** so newly discovered grimoires are wired into the agent skill directories:

   ```bash
   python3 {{ARCANA_PATH}}/rites/register_skills.py
   ```

   Or invoke `/grm-skills-register`.

## Notes

- Arcana itself is excluded from the catalog scan (it's the engine, not a domain grimoire) — the rite recognizes it by `name: "arcana"` in `arcana/grimoire.json`.
- An "unmanaged" directory will not be auto-registered. To register it, either add a valid `grimoire.json` to it (then re-run sync) or move it out of `~/grimoire/`.
- The rite preserves any unknown fields on existing catalog entries (forward-compat); it only updates `local_path` and `online_path`.
- Catalog entries are sorted alphabetically by key on write for deterministic output.
- An override flag is available for testing: `--home /path/to/alt/home`.
