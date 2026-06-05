---
type: reference
title: "Validate Grimoire Doc Trees"
aliases: ["validate-grimoire-doc-trees", "grimoire-validate-doc-trees", "validate-tree-diagrams"]
tags: [arcana/invocations, type/reference, scope/grimoire]
authority: grimoire
last_verified: 2026-05-28
---

# Invocation: Validate Grimoire Doc Trees

## Purpose

Detect drift between ASCII directory-tree diagrams (in fenced code blocks)
and the actual filesystem of the active grimoire. Catches the failure mode
where a README, hub, or how-to lists a chapter, skill, or folder that has
been renamed, added, or removed without updating the doc.

## Invocation

```
/grm-validate doc-trees
```

## Workflow

Run against the resolved active grimoire:

```bash
python3 ARCANA_HOME/rites/validate_doc_trees.py --grimoire GRIMOIRE_ROOT
```

Exit code 0 means every diagram with a resolvable filesystem anchor matches
reality.

## What it checks

For every fenced code block in every grimoire markdown file (excluding
`sources/`, `inbox/`, `log.md`, `CHANGELOG.md`), the validator looks for
trees that use the box-drawing characters `├──`, `└──`, `│`. It parses the
diagram, resolves the root line to a real directory inside the grimoire when
possible, and emits:

- `DOC_TREE_MISSING_ENTRY` — the diagram lists a path that doesn't exist on
  disk under that anchor.
- `DOC_TREE_UNLISTED_ENTRY` (warning) — the actual directory has top-level
  children the diagram (when structurally exhaustive) doesn't mention.

## What it skips (and why)

A diagram is treated as illustrative and skipped when ANY of the following
apply, because diffing illustration against reality would emit noise:

- The root line contains a placeholder (`<name>`, `{name}`, `[name]`, `...`)
- The diagram contains an `...` or `…` marker indicating the listing is not
  exhaustive (only the `UNLISTED_ENTRY` warning is suppressed; missing-entry
  errors still fire)
- The doc lives under a `templates/`, `snippets/`, `scripts/`, `examples/`,
  `sources/`, or `inbox/` folder
- The doc's path contains a placeholder segment (`{app_name}`, `<plugin>`,
  etc.)
- No filesystem anchor can be resolved for the diagram's root

Per-entry, lines that themselves contain a placeholder (`<...>`, `{...}`)
are skipped while the rest of the diagram is still validated.

## Fix template

When the validator reports drift:

1. Open the cited file at the cited line.
2. Compare the diagram to the actual layout of the anchor directory.
3. Update the diagram (preferred for routine drift) OR update the filesystem
   (when the diagram describes the intended layout and the filesystem has
   drifted from it).
4. Re-run `/grm-validate doc-trees` to confirm.

## Related

- Validators hub: [[invocations/grimoire/validators/validators|validators]]
- Improvement playbook: [[invocations/grimoire/improve_grimoire|improve grimoire]]
- Format validator (tree branch-marker style): [[invocations/grimoire/validators/validate_format|validate format]]
