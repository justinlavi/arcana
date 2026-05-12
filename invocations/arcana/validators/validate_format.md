# 🔮 Invocation: Validate Arcana Format

## Purpose

Validate invocation and formula format compliance (required sections and schema).

## Invocation

```
/grm-arcana-validate-format
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

### Step 3: Review INDEX.md Files

Validates INDEX.md files are **thin routers**:

**Thin router criteria**:
- < 200 lines total
- Simple file list with one-line descriptions
- NO detailed invocation metadata (that belongs in invocation files)
- NO duplicated content from invocation files

**Example of thin router** (✅ correct):
```markdown
## Available Invocations

### Creation
- **[create_grimoire.md](create_grimoire.md)** - Create new domain grimoire
- **[create_chapter.md](create_chapter.md)** - Add knowledge chapter
```

**Example of thick router** (❌ wrong):
```markdown
### create_grimoire.md
**Invocation**: /grm-domain-create-grimoire
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

**INDEX.md too long**:
1. Remove duplicate content
2. Simplify descriptions to one line
3. Move detailed content to invocation files

**Formula missing structure**:
1. Add title heading
2. Document placeholders
3. Add usage instructions

## Outputs

**Console output**:
- Invocation files with missing sections
- INDEX.md files exceeding size limit
- Formulae with format issues
- Exit code: 0 (compliant) or 1 (violations found)

**On success**:
```
✅ All invocations have required sections
✅ All INDEX.md files are appropriately sized
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
# 🔮 Invocation: [Invocation Name]

## ⚡ The Magical Boundary ⚡
[Optional: Magical boundary guidance if needed]

## Purpose
[What this invocation does]

## Invocation
```
/grm-meta-help
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

### INDEX.md Template (Thin Router)

```markdown
# [Category] Invocations

## Available Invocations

- **[invocation_name.md](invocation_name.md)** - One-line description
- **[other_invocation.md](other_invocation.md)** - One-line description
```

## Related

- **Rite**: [rites/validate_format.py](../../../rites/validate_format.py)
- **Formula template**: [formulae/invocation.formula.md](../../../formulae/invocation.formula.md)
- **Reference**: [docs/operating_model.md](../../../docs/operating_model.md#single-source-architecture)
- **Orchestrator**: [improve_arcana.md](../improve_arcana.md)

## Notes

**Exclusions**: The rite automatically skips:
- `base_invocation.md` (meta-template, not user-invocable)

**Benefits of format validation**:
- Ensures consistent user experience across all invocations
- Prevents documentation drift
- Enforces single-source architecture (no duplicate metadata)
