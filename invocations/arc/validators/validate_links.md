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

Detect broken internal references in Arcana documentation and enforce layer-aware internal page link style.

## Invocation

```
/arc-validate links
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

The rite scans Markdown files, verifies resolvable internal references, and enforces page-link style by layer:

- Public documentation (`README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `docs/**`, and README index files) uses relative Markdown links so Git-host browsing remains clickable.
- Vault and AI-routing surfaces use repository-root relative wikilinks for internal Markdown-page pointers.
- External URLs, same-page anchors, and local non-Markdown artifacts use standard Markdown links in every layer.
- Wikilink display labels should match the target filename stem, normalized for reading.

**Link types validated**:

- Full-path wikilinks: `[[docs/page_schema|page schema]]`
- Internal Markdown links in public docs: `[page schema](page_schema.md)`
- Intra-document anchors: `[text](#section)` (skipped as local anchors)
- Non-Markdown local artifacts: `[script](../rites/validate_links.py)`

**Layer style enforced**:

- Valid public-doc page reference: `[Installation](docs/installation.md)`
- Invalid public-doc page reference: `[[docs/installation|installation]]`
- Valid vault/AI page reference: `Topic -> [[chapters/path/to/page|page]]`
- Invalid vault/AI page reference: `Topic -> [page](../path/to/page.md)`

**Link types skipped**:

- External URLs: `https://`, `http://`, `mailto:`
- Placeholder paths: `ARCANA_HOME/`, `GRIMOIRE_PATH`, template variables, and similar formula tokens
- Anchor-only links: `#section`

### Step 3: Fix Findings

For each finding:

1. If the target is broken, update the path or remove the reference.
2. If a public document uses a wikilink, replace it with a relative Markdown link.
3. If a vault or AI-routing surface uses a Markdown link to an internal page, replace it with a repository-root relative wikilink.
4. If a wikilink label is verbose, shorten the display label to the target filename stem.
5. Re-run the validator.

Example:

```markdown
<!-- Invalid in a vault/AI surface -->
Quickstart -> [quickstart](../docs/quickstart.md)

<!-- Valid in a vault/AI surface -->
Quickstart -> [[docs/quickstart|quickstart]]

<!-- Valid in public docs -->
[Quickstart](docs/quickstart.md)
```

## Outputs

**Console output**:

- Broken links with source file and line where available
- Layer-specific style violations with source file and line
- Wikilink label warnings
- Exit code: 0 (clean) or 1 (errors found)

**Structured diagnostics**:

- `LINK_MARKDOWN_BROKEN`
- `LINK_MARKDOWN_INTERNAL`
- `LINK_WIKILINK_PUBLIC_DOC`
- `LINK_WIKILINK_BROKEN`
- `LINK_LABEL_VERBOSE`

## Link Standards

### Public Documentation

Public documentation uses portable Markdown links for internal pages:

```markdown
[Installation](docs/installation.md)
[Page schema](page_schema.md)
```

### Vault And AI Surfaces

Root hubs, chapter pages, invocation files, skill sources, and formula templates use full-path wikilinks for internal Markdown pages:

```markdown
- Create a grimoire -> [[invocations/grm/create_grimoire|create grimoire]]
- Travel planning -> [[chapters/travel/travel|travel]]
```

### Standard Markdown Links

Markdown links remain valid for external URLs, same-page anchors, and local non-Markdown artifacts in every layer.

```markdown
See [the external project](https://example.com/project).
See [this section](#link-standards).
See [the validator script](../../../rites/validate_links.py).
```

### Wikilink Targets

Wikilink targets must be repository-root relative paths. The `.md` suffix is optional for Obsidian compatibility. Aliases and filename-only shortcuts are invalid unless they also resolve as real repository-root paths.

```markdown
[[docs/page_schema|page schema]]
[[invocations/arc/validators/validate_links|validate links]]
[[README|README]]
```

## Related

- Rite: `rites/validate_links.py`
- Path conventions -> [[docs/obsidian|obsidian]]
- Operating model -> [[docs/operating_model|operating model]]
- Orchestrator -> [[invocations/arc/improve_arcana|improve arcana]]
