---
type: reference
title: "Validate Links"
aliases: ["validate-links"]
tags: [arcana/invocations, type/reference, scope/validators]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Validate Arcana Links

## Purpose

Detect broken internal references in Arcana documentation and enforce wikilink-only internal Markdown-page references everywhere.

## Invocation

```
/arc-validate-links
```

## When to Cast

- Before Arcana releases
- After renaming or moving Markdown files
- During `/arc-improve`
- After documentation or routing changes

## Workflow

### Step 1: Run Automation

```bash
python3 rites/validate_links.py
```

### Step 2: Review Link Findings

The rite scans Markdown files, verifies resolvable internal references, and enforces page-link style:

- Internal Markdown-page references must use repository-root relative wikilinks.
- Standard Markdown links are limited to external URLs, same-page anchors, and local non-Markdown artifacts.
- Wikilink display labels should match the target filename stem, normalized for reading.

**Link types validated**:

- Full-path wikilinks: `[[docs/page_schema|page schema]]`
- Intra-document anchors: `[text](#section)` (skipped as local anchors)
- Non-Markdown local artifacts: `[script](../rites/validate_links.py)`

**Internal-page style enforced**:

- Valid page reference: `Topic -> [[chapters/path/to/page|page]]`
- Invalid page reference: `Topic -> [page](../path/to/page.md)`

**Link types skipped**:

- External URLs: `https://`, `http://`, `mailto:`
- Placeholder paths: `ARCANA_HOME/`, `GRIMOIRE_PATH`, template variables, and similar formula tokens
- Anchor-only links: `#section`

### Step 3: Fix Findings

For each finding:

1. If the target is broken, update the path or remove the reference.
2. If an internal Markdown-page reference uses Markdown link syntax, replace it with a repository-root relative wikilink.
3. If a wikilink label is verbose, shorten the display label to the target filename stem.
4. Re-run the validator.

Example:

```markdown
<!-- Invalid for an internal Markdown page -->
Quickstart -> [quickstart](../docs/quickstart.md)

<!-- Valid -->
Quickstart -> [[docs/quickstart|quickstart]]
```

## Outputs

**Console output**:

- Broken links with source file and line where available
- Internal Markdown-page style violations with source file and line
- Wikilink label warnings
- Exit code: 0 (clean) or 1 (errors found)

**Structured diagnostics**:

- `LINK_MARKDOWN_BROKEN`
- `LINK_MARKDOWN_INTERNAL`
- `LINK_WIKILINK_BROKEN`
- `LINK_LABEL_VERBOSE`

## Link Standards

### Internal Page References

All internal Markdown-page references use full-path wikilinks:

```markdown
- Create a grimoire -> [[invocations/grimoire/create_grimoire|create grimoire]]
- Travel planning -> [[chapters/travel/travel|travel]]
```

### Standard Markdown Links

Markdown links remain valid for external URLs, same-page anchors, and local non-Markdown artifacts. They are not valid for internal Markdown pages.

```markdown
See [the external project](https://example.com/project).
See [this section](#link-standards).
See [the validator script](../../../rites/validate_links.py).
```

### Wikilink Targets

Wikilink targets must be repository-root relative paths. The `.md` suffix is optional for Obsidian compatibility. Aliases and filename-only shortcuts are invalid unless they also resolve as real repository-root paths.

```markdown
[[docs/page_schema|page schema]]
[[invocations/arcana/validators/validate_links|validate links]]
[[README|README]]
```

## Related

- Rite: `rites/validate_links.py`
- Path conventions -> [[docs/obsidian|obsidian]]
- Operating model -> [[docs/operating_model|operating model]]
- Orchestrator -> [[invocations/arcana/improve_arcana|improve arcana]]
