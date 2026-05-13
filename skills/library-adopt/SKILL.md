---
name: {{NAMESPACE}}-library-adopt
description: Adopt an unmanaged directory under ~/grimoires/ as a domain grimoire by writing its grimoire.json manifest
when_to_use: /grm-library-sync reported an "unmanaged directory" the user wants to register; user has an existing folder under ~/grimoires/ without a grimoire.json that they want to make a real grimoire; user says "register this directory as a grimoire" or "adopt this folder". Use /grm-domain-create-grimoire instead if starting from scratch.
argument-hint: [directory-name]
arguments: [directory]
user-invocable: true
allowed-tools: Bash Read
---

# Adopt Grimoire

You are turning an unmanaged directory under `~/grimoires/` into a registered domain grimoire by writing its `grimoire.json` manifest.

Use this skill when `/grm-library-sync` reports an "unmanaged directory" — i.e. a folder under `~/grimoires/` that lacks a `grimoire.json` and so isn't recognized by the registration or library rites.

## Workflow

1. **Identify the target.** If the user passed `$directory`, use it. Otherwise run `/grm-library-sync` to enumerate unmanaged directories and ask the user which to adopt.

2. **Gather the namespace.** Ask the user for a 2–4 letter lowercase slug (must match `^[a-z][a-z0-9]*$`). Suggest one based on the directory name (e.g., `lus-grimoire` → `lus`). Make sure the user understands every skill the grimoire ships will be prefixed `<namespace>-` (e.g., `/lus-foo-bar`). Mention that if the directory already has a `skills/` folder, the namespace must be unique across all installed grimoires — the rite will refuse a collision.

3. **Gather a one-line description.** Ask the user briefly what the grimoire is for. Default to `"<name> domain grimoire"` if they don't have one yet.

4. **Run the rite:**

   ```bash
   python3 {{ARCANA_PATH}}/rites/adopt_grimoire.py <directory> --namespace <ns> --description "<desc>"
   ```

   The rite refuses to overwrite an existing `grimoire.json` and refuses if the namespace collides with another grimoire in `~/grimoires/`. Report any errors back to the user.

5. **Register the grimoire.** Run:

   ```bash
   python3 {{ARCANA_PATH}}/rites/sync_library.py --apply
   ```

   This adds the new grimoire to `~/grimoires/library.json`. If it ships skills, also run `/grm-skills-register` so its `<namespace>-*` commands appear.

## Notes

- For grimoires you're starting from scratch, prefer `/grm-domain-create-grimoire` — it does scaffolding (root hub, README.md, sources/, log.md, chapters/) in addition to the manifest. This skill only writes the manifest, intended for directories that already have content but were cloned by hand.
- The rite never modifies anything outside the target directory; it just writes one file.
