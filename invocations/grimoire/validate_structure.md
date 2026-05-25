---
type: playbook
title: "Validate Grimoire Structure"
aliases: ["validate-structure-domain"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Validate Grimoire Structure Compliance

## Purpose

Validate a grimoire's mechanical structure against current Arcana formulae.

This invocation ensures:

- Required root files and directories exist
- Root and chapter hubs follow the folder-name convention
- `grimoire.json` declares `name` and `skill_prefix`
- Managed scaffold files match the current Arcana formulae
- Obsidian configuration uses absolute wikilink creation

## Preconditions

Before executing, resolve `GRIMOIRE_ROOT` with the shared grimoire directory guard. Arcana is not a grimoire. Stop if no active grimoire can be resolved.

## When to Cast

- After creating or editing chapters/pages
- After pulling a newer Arcana version
- During periodic grimoire quality reviews
- Before running `/grm-improve`
- Before publishing or handoff

## Invocation

From the active grimoire context, cast:

```
/grm-validate-structure
```

Mechanical equivalent:

```bash
python3 ARCANA_HOME/rites/validate_grimoire_structure.py --grimoire GRIMOIRE_ROOT
```

## Validation Workflow

### Phase 1: Root Structure

- Parse `grimoire.json`
- Confirm `README.md`, `log.md`, and `<grimoire-name>.md`
- Confirm `sources/`, `chapters/`, and `inbox/`

### Phase 2: Managed Scaffold Drift

The following files are operational support files, not grimoire-specific authored content. They should match `ARCANA_HOME/formulae/grimoire/` exactly:

- `.editorconfig`
- `.gitattributes`
- `.obsidian/app.json`
- `inbox/README.md`
- `sources/README.md`

If any are missing or stale, copy the current version from Arcana unless the user explicitly wants a custom local variant. Custom local variants should be rare because they create cross-platform and agent-behavior drift.

### Phase 3: Hub Convention

For every folder under `chapters/` that contains Markdown content, confirm the hub file is `F/<basename(F)>.md`. Asset folders such as `templates/`, `snippets/`, `scripts/`, `configs/`, `assets/`, and `media/` are exempt.

### Phase 4: Obsidian Configuration

Confirm `.obsidian/app.json` sets:

```json
{
  "newLinkFormat": "absolute",
  "useMarkdownLinks": false
}
```

This prevents Ctrl-clicking unresolved full-path wikilinks from creating recursive relative folder trees.

## Compliance Matrix

| Check | Priority |
|---|---|
| Manifest has `name` and `skill_prefix` | Critical |
| Root hub exists and matches manifest `name` | Critical |
| Required storage directories exist | Critical |
| Managed scaffold files match Arcana formulae | Critical |
| Chapter hubs follow folder-name convention | Critical |
| Obsidian link config is absolute | Critical |

## Outputs

- Structure pass/fail summary
- Missing root files or directories
- Missing or stale managed scaffold files
- Missing chapter hubs
- Obsidian configuration warnings

## Related Docs

- `docs/operating_model.md`
- `formulae/grimoire/`
- `rites/validate_grimoire_structure.py`
