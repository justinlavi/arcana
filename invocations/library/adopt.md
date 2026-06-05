---
type: playbook
title: "Adopt Grimoire"
aliases: ["library-adopt", "adopt-grimoire"]
tags: [arcana/invocations, type/playbook, scope/library]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Adopt Grimoire

## Purpose

Turn an unmanaged directory under `~/grimoires/` into a registered grimoire by writing its `grimoire.json` manifest.

Use this when `/arc-library-sync` reports an unmanaged directory: a folder under `~/grimoires/` that lacks `grimoire.json` and is therefore invisible to library and registration rites.

## Invocation

```
/arc-library-adopt [directory-name]
```

## Workflow

### 1. Identify the target

If the user passed `$directory`, use it. Otherwise run `/arc-library-sync` to enumerate unmanaged directories and ask which one to adopt.

### 2. Gather the skill prefix

Ask for a 2-4 letter lowercase slug that matches `^[a-z][a-z0-9]*$`. Suggest one based on the directory name, such as `lus-grimoire` -> `lus`.

Explain that every skill the grimoire ships will be prefixed `<skill prefix>-`, and that the prefix must be unique across installed grimoires if the directory has a `skills/` folder.

### 3. Gather a description

Ask for a one-line description. Default to `"<name> grimoire"` if the user does not have one yet.

### 4. Run the rite

```bash
python3 ARCANA_HOME/rites/adopt_grimoire.py <directory> --skill-prefix <prefix> --description "<desc>"
```

The rite refuses to overwrite an existing `grimoire.json` and refuses skill prefix collisions.

### 5. Register the grimoire

```bash
python3 ARCANA_HOME/rites/sync_library.py --apply
```

If the grimoire ships skills, also run `/grm-sync-skills` from inside that grimoire or `/arc-agent-sync-skills` globally.

## Notes

- For grimoires started from scratch, prefer `/grm-create`. It scaffolds the root hub, README, manifest, storage layers, and starter docs.
- This skill only writes the manifest and is intended for directories that already have content.

## Related

- Sync library: [[invocations/library/sync|sync]]
- Create new grimoire: [[invocations/grimoire/create_grimoire|create grimoire]]
