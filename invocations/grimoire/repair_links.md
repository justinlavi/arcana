---
type: playbook
title: "Repair Wikilinks"
aliases: ["repair-links", "domain-repair-links", "fix-wikilinks"]
tags: [arcana/invocations, type/playbook, scope/domain]
authority: grimoire
last_verified: 2026-05-19
---

# Invocation: Repair Wikilinks

## Purpose

Promote filename-only wikilinks (`[[foo]]`, `[[parent_sibling|sibling]]`) to canonical full-path form (`[[chapters/path/to/foo|foo]]`). Arcana wikilinks must resolve as repository-root relative paths; this rite mechanizes the bulk rewrite.

Use this after a structural migration, after `/grm-domain-ingest` finds drift, or any time `/grm-domain-lint` reports a wave of broken wikilinks of the form "must resolve as a repository path".

## Invocation

From the active domain grimoire's root:

```
/grm-domain-repair-links
```

The skill runs a dry-run first, surfaces the proposed changes plus any ambiguities, and asks before applying.

## Preconditions

1. Working directory must be a registered domain grimoire (its key in `~/grimoires/library.json`).
2. The grimoire should be under version control so changes can be reviewed/reverted via diff.

## Workflow

### Phase 1: Dry-run scan

Run the rite without `--apply` to enumerate every proposed change:

```bash
python3 GRIMOIRE_ARCANA/rites/repair_links.py --grimoire .
```

The output has four sections:

- **Repairs** — unambiguous fixes the rite would apply. Each line shows source file, original wikilink, and the proposed full-path replacement.
- **Ambiguous** — targets that resolve to multiple candidate files. The rite refuses to guess; these need human judgment using surrounding context.
- **Unresolvable** — targets that match no file anywhere (typos, removed pages, or genuinely broken intent).
- **Skipped** — partial-path forms (`[[foo/bar]]`) that aren't simple basenames; left alone because they may be intentional typos worth investigating manually.

### Phase 2: Review the dry-run

Read every reported repair and check for surprises:

- Bulk patterns that resolve sensibly via sibling preference (good).
- Resolutions marked `(via display-label fallback)` — these came from the `[[parent_sibling|sibling]]` anti-pattern; sanity-check that the display label was the intended target.
- Any ambiguous case where neither candidate looks right (might mean the page itself needs to be split or moved before linking).

If the dry-run looks clean, proceed to apply. If there are ambiguities you want auto-resolved, open the relevant chapter files and read surrounding context to choose; never let the rite guess.

### Phase 3: Apply

Run with `--apply` to write changes:

```bash
python3 GRIMOIRE_ARCANA/rites/repair_links.py --grimoire . --apply
```

Edits are per-file and atomic. The rite preserves existing display labels (`[[xxx|My Label]]` becomes `[[chapters/path/xxx|My Label]]`) and adds a stem label when none is present.

### Phase 4: Resolve ambiguities

For each `[AMBI]` entry from the dry-run:

1. Open the source file at the reported line.
2. Read the surrounding paragraph for context about which candidate is meant.
3. Edit the wikilink directly to the chosen full path: `[[chapters/path/to/intended|label]]`.

For each `[MISS]` entry: the target genuinely doesn't exist. Either delete the reference, file a new page, or fix a typo. Don't fabricate a target just to satisfy the validator.

### Phase 5: Re-validate

Confirm the change set is clean:

```bash
python3 GRIMOIRE_ARCANA/rites/validate_links.py --grimoire .
python3 GRIMOIRE_ARCANA/rites/validate_orphans.py --grimoire .
```

Orphan count should drop significantly — every reconnected page joins the routing graph.

### Phase 6: Log

Append an entry to `log.md` recording:
- Skill used
- Files touched (count is fine; full list available via `git diff --name-only`)
- Number of mechanical repairs, ambiguities resolved manually, any unresolvable misses left
- Before/after broken-link counts

## Resolution Rules (reference)

The rite tries these in order; first hit wins:

1. **Sibling** — `<source_dir>/<basename>.md` exists
2. **Descendant-of-source-dir** — unique match under `<source_dir>/**/`
3. **Descendant-of-source-chapter** — unique match under the source's chapter root
4. **Globally unique** — exactly one match anywhere under `chapters/`
5. **Display-label fallback** — when the body doesn't match any file but the display label does, retry resolution using the display as the target basename. Covers `[[parent_sibling|sibling]]` where the author synthesized a basename that doesn't exist on disk.

If none of these yield a unique target, the link is reported and skipped — never auto-rewritten.

## Safety

- Default is dry-run. `--apply` must be passed explicitly.
- Per-file atomic writes (read → patch → write once).
- Skips code-fence blocks and inline-backtick spans (won't rewrite links inside code samples).
- Skips placeholder tokens (`{{...}}`, `<chapter_name>`, etc.) in formula files.
- Path containing `/` in the wikilink body is treated as intentional and never auto-rewritten.

## Related

- Validator that detects the broken links: `GRIMOIRE_ARCANA/rites/validate_links.py`
- Wikilink rules: `GRIMOIRE_ARCANA/docs/obsidian.md` (Full-path wikilinks section)
- Health-check umbrella: `/grm-domain-lint`
