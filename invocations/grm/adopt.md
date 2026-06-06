---
type: playbook
title: "Adopt an Existing Folder as a Grimoire"
aliases: ["adopt", "adopt-grimoire", "register-folder"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-06-06
---

# Invocation: Adopt an Existing Folder as a Grimoire

## Purpose

Turn an existing folder under `~/grimoires/` into a registered grimoire by writing its `grimoire.json` manifest. Use this when you have a folder with content but no `grimoire.json` — for example notes you dragged in through Obsidian or a file manager, or a folder `/grm-sync library` flagged as unmanaged. This is the everyday user mirror of `/arc-adopt`.

For a brand-new grimoire from scratch, use `/grm-create` instead — it scaffolds the root hub, README, manifest, storage layers, and starter docs.

## Invocation

```
/grm-adopt [directory-name]
```

## Preconditions

!`cat ARCANA_HOME/invocations/meta/grimoire_directory_guard.md`

The guard does not block adoption: this command operates on a folder that is not yet a grimoire. If the working directory is not inside a registered grimoire, take the target from `$directory` or from the `/grm-sync library` unmanaged list rather than auto-selecting.

## Workflow

### 1. Identify the target

If the user passed `$directory`, use it. Otherwise run `/grm-sync library` to list unmanaged directories and ask which one to adopt.

### 2. Gather the skill prefix

Ask for a short lowercase slug (2-4 letters) matching `^[a-z][a-z0-9]*$` — the prefix for every command this grimoire ships (for example `lus-grimoire` -> `lus`). It must be unique across installed grimoires if the folder has a `skills/` directory.

### 3. Gather a description

Ask for a one-line description. Default to `"<name> grimoire"` if the user does not have one yet.

### 4. Run the rite

```bash
python3 ARCANA_HOME/rites/adopt_grimoire.py <directory> --skill-prefix <prefix> --description "<desc>"
```

The rite refuses to overwrite an existing `grimoire.json` and refuses skill prefix collisions.

### 5. Register it

```bash
python3 ARCANA_HOME/rites/sync_library.py --apply
```

Or run `/grm-sync library`. If the grimoire ships skills, also run `/grm-sync skills`.

## Notes

- This skill only writes the manifest; it is for folders that already have content. For a grimoire started from scratch, prefer `/grm-create`.

## Related

- Reconcile the library and register skills: [[invocations/grm/sync|sync]]
- Create a new grimoire from scratch: [[invocations/grm/create_grimoire|create grimoire]]
- Maintainer mirror: [[invocations/arc/adopt|adopt]]
