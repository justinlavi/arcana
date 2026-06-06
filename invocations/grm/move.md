---
type: playbook
title: "Move or Rename Grimoire Content"
aliases: ["move", "rename", "move-content"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-06-06
---

# Invocation: Move or Rename Grimoire Content

## Purpose

Rename or move a page or chapter within the active grimoire and keep the wiki consistent. The deterministic rite moves the file(s) and retargets every full-path wikilink that pointed at them; this invocation handles the judgment around it - the chapter hubs, display labels, and the activity log.

## Invocation

```
/grm-move [from-path] [to-path]
```

## Preconditions

!`cat ARCANA_HOME/invocations/meta/grimoire_directory_guard.md`

## Workflow

### 1. Resolve source and destination

Take `$source` and `$destination` as grimoire-relative paths under `chapters/` (for example `chapters/setup/intro.md` -> `chapters/onboarding/intro.md`). If the user described the change in prose, resolve the exact paths and confirm them. A rename is a move whose destination is a new name in the same folder; moving a whole chapter means moving its folder.

### 2. Plan the move

```bash
python3 ARCANA_HOME/rites/restructure_grimoire.py --grimoire GRIMOIRE_ROOT --move SRC DST
```

Review the planned file moves and wikilink rewrites. The rite refuses when the destination already exists, the target is outside `chapters/`, or the target is a chapter hub on its own (move the whole chapter folder instead). Moving a chapter folder also renames its folder-named hub so the convention holds.

### 3. Apply

```bash
python3 ARCANA_HOME/rites/restructure_grimoire.py --grimoire GRIMOIRE_ROOT --move SRC DST --apply
```

### 4. Wire the hubs and labels (judgment)

The rite retargets link paths but does not edit hubs or display labels. After the move:

- **Source chapter hub**: remove the moved page's pointer if it left that chapter.
- **Destination chapter hub**: add a full-path wikilink pointer to the moved page. If the destination chapter does not exist yet, create its hub from `ARCANA_HOME/formulae/chapter_hub.formula.md` and wire it into the parent hub.
- **Display labels**: fix any label that named the old location (the rite preserves labels verbatim, so a renamed page may still read with its old label).

### 5. Log and validate

Append one entry to the grimoire log, then re-validate:

```bash
python3 ARCANA_HOME/rites/append_log.py --grimoire GRIMOIRE_ROOT --op move --title "moved SRC to DST" --skill /grm-move
python3 ARCANA_HOME/rites/validate.py --grimoire GRIMOIRE_ROOT links orphans structure
```

## Related

- Delete content: [[invocations/grm/remove|remove]]
- Repair filename-only wikilinks: [[invocations/grm/repair_links|repair links]]
- Add content: [[invocations/grm/add|add]]
