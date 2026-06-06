---
type: playbook
title: "Remove Grimoire Content"
aliases: ["remove", "delete", "remove-content"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-06-06
---

# Invocation: Remove Grimoire Content

## Purpose

Delete a page or chapter from the active grimoire without leaving the wiki pointing at content that no longer exists. The deterministic rite deletes the file(s) and reports every inbound wikilink that would break; this invocation handles the judgment - confirming the deletion, dropping the parent hub pointer, repairing or removing the broken links, and the activity log.

## Invocation

```
/grm-remove [path]
```

## Preconditions

!`cat ARCANA_HOME/invocations/meta/grimoire_directory_guard.md`

## Workflow

### 1. Resolve the target and plan

Take `$target` as a grimoire-relative path under `chapters/` (a page or a whole chapter folder). Plan first - this is destructive:

```bash
python3 ARCANA_HOME/rites/restructure_grimoire.py --grimoire GRIMOIRE_ROOT --remove PATH
```

The plan lists what would be deleted and every inbound wikilink that would break. The rite refuses to remove a chapter hub on its own (remove the whole chapter folder instead) or anything outside `chapters/`.

### 2. Confirm

Show the user what will be deleted and which inbound links will break. Removal is destructive and not reversible by this rite - get explicit confirmation before applying. If important pages link to the target, consider `/grm-move` (to relocate) instead of deletion.

### 3. Apply

```bash
python3 ARCANA_HOME/rites/restructure_grimoire.py --grimoire GRIMOIRE_ROOT --remove PATH --apply
```

### 4. Heal the references (judgment)

For each inbound link the rite reported:

- Drop the pointer from the **parent chapter hub**.
- For other inbound links, either repoint them to a sensible replacement page or remove the reference - never leave a wikilink targeting deleted content.

### 5. Log and validate

```bash
python3 ARCANA_HOME/rites/append_log.py --grimoire GRIMOIRE_ROOT --op remove --title "removed PATH" --skill /grm-remove
python3 ARCANA_HOME/rites/validate.py --grimoire GRIMOIRE_ROOT links orphans structure
```

## Related

- Rename or move content: [[invocations/grm/move|move]]
- Repair filename-only wikilinks: [[invocations/grm/repair_links|repair links]]
