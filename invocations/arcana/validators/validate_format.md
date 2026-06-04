---
type: reference
title: "Validate Format"
aliases: ["validate-format"]
tags: [arcana/invocations, type/reference, scope/validators]
authority: grimoire
last_verified: 2026-05-12
---

# Invocation: Validate Arcana Format

## Purpose

Validate Markdown, invocation, formula, and hub format compliance. The rite checks required invocation sections, thin hubs, formula headings, table delimiter rows, fenced code blocks, and pipe-only Markdown tree examples.

## Invocation

```
/arc-validate format
```

## When to Cast

- Before Arcana releases
- After creating or modifying invocations
- During improve-arcana workflow (Phase 2-3)
- After updating formula templates

## Workflow

### Step 1: Run Automation

Execute the validation rite:

```bash
python3 rites/validate_format.py
```

For an active grimoire, use `/grm-validate format`.

### Step 2: Review Invocation Format

The rite validates all invocation files have required sections:

**Required sections for invocations**:
- `# ` (title heading with invocation name)
- `## Purpose` or `## ⚡ Purpose` (what this invocation does)
- `## Invocation` (how to cast the invocation)

**Recommended sections** (not enforced):
- `## When to Cast` (use cases)
- `## Workflow` (step-by-step process)
- `## Outputs` (deliverables)
- `## Related` (cross-references)

### Step 3: Review Hub Files

Validates hub files are **thin routers**:

**Thin router criteria**:
- < 200 lines total
- Simple route list with one-line descriptions
- Full-path wikilinks for internal Markdown-page pointers
- NO detailed invocation metadata (that belongs in invocation files)
- NO duplicated content from invocation files

**Example of thin router** (✅ correct):
```markdown
## Available Invocations

### Creation
- Create new grimoire -> [[invocations/grimoire/create_grimoire|create grimoire]]
- Add knowledge chapter -> [[invocations/grimoire/create_chapter|create chapter]]
```

**Example of thick router** (❌ wrong):
```markdown
### create_grimoire.md
**Invocation**: /grm-create
**Purpose**: Long description here...
**What it does**: Detailed workflow...
[This duplicates invocation file content - violation]
```

### Step 4: Review Formula Format

Validates formulae have basic structure:

**Required for formulae**:
- `# ` (title heading)
- Placeholder documentation (what to replace)
- Usage instructions

### Step 5: Fix Violations

For each format violation:

**Missing invocation section**:
1. Add required section using formula template as guide
2. Ensure section has meaningful content (not placeholder)

**Hub too long**:
1. Remove duplicate content
2. Simplify descriptions to one route per line
3. Move detailed content to invocation files

**Formula missing structure**:
1. Add title heading
2. Document placeholders
3. Add usage instructions

**Unclosed code fence**:
1. Add the matching closing fence using the same marker (` ``` ` or ` ~~~ `).
2. If the example must show fenced Markdown inside a fenced block, use a longer outer fence.

**Backtick tree branch marker**:
1. Replace legacy tree markers like `` `-- child `` with pipe markers like `|-- child`.
2. Keep indentation aligned so the tree remains readable in plain text.

## Outputs

**Console output**:
- Invocation files with missing sections
- hub files exceeding size limit
- hub routes that use Markdown links (reported by `validate_links.py`)
- Formulae with format issues
- Markdown table delimiter rows with fewer than 3 hyphens
- Unclosed fenced code blocks
- Markdown tree examples that use backtick branch markers
- Exit code: 0 (compliant) or 1 (violations found)

**On success**:
```
✅ All invocations have required sections
✅ All hub files are appropriately sized
✅ All formulae have proper format
✅ Format validation passed
```

**On violations**:
```
⚠️  Format violations in: invocations/grimoire/create_chapter.md
   Missing section: ^## .*Invocation
❌ Format validation failed with 1 issues
```

## Format Standards

### Invocation File Template

```markdown
# Invocation: [Invocation Name]

## ⚡ The Magical Boundary ⚡
[Optional: Magical boundary guidance if needed]

## Purpose
[What this invocation does]

## Invocation
```
/arc-help
```

## When to Cast
[Use cases]

## Workflow
[Step-by-step process]

## Outputs
[Deliverables]

## Related
[Cross-references]
```

### Hub Template (Thin Router)

```markdown
# [Category] Invocations

## Available Invocations

- **[invocation_name.md](invocation_name.md)** - One-line description
- **[other_invocation.md](other_invocation.md)** - One-line description
```

## Related

- **Rite**: [rites/validate_format.py](../../../rites/validate_format.py)
- **Formula template**: [[formulae/invocation.formula|invocation.formula]]
- **Reference**: [[docs/operating_model#single-source-architecture|operating model]]
- **Orchestrator**: [[invocations/arcana/improve_arcana|improve arcana]]

## Notes

**Exclusions**: The rite automatically skips:
- `base_invocation.md` (meta-template, not user-invocable)
