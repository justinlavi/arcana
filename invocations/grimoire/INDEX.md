# 📖 Grimoire Invocations Catalog

**Domain operations - invocations that create and improve domain grimoires**

---

## Single Source Architecture

**This catalog is a THIN ROUTER** - invocation files are the single source of truth.

For dynamic invocation catalog with full details, use: **`/grm-help`**

For detailed documentation, read the invocation file directly.

---

## Available Grimoire Invocations

### 🎨 Creation

- **[create_grimoire.md](create_grimoire.md)** - Create new grimoire for your domain
- **[create_chapter.md](create_chapter.md)** - Add new knowledge chapter to your grimoire

### 🔧 Improvement

- **[improve_grimoire.md](improve_grimoire.md)** - Comprehensive grimoire optimization and quality improvement

### 📊 Analysis

- **[analyze_semantics.md](analyze_semantics.md)** - Deep semantic analysis of naming and organization
- **[validate_structure.md](validate_structure.md)** - Validate formula template compliance

---

## Quick Reference

| Name | Command | Purpose |
|------|---------|---------|
| create-grimoire | `/grm-create-grimoire` | Create new domain grimoire |
| create-chapter | `/grm-create-chapter [topic]` | Add knowledge chapter |
| improve-grimoire | `/grm-improve` | Comprehensive optimization |
| analyze-semantics | `/grm-analyze-semantics` | Naming quality audit |
| validate-structure | `/grm-arcana-validate` | Formula compliance check |

---

## How to Use

**For invocation catalog**: Invoke `/grm-help` (dynamically generated)

**For invocation details**: Read individual invocation .md files

**For new invocations**: Add invocation .md file to this directory - automatically discovered by `/grm-help`

---

## Invocation Relationships

### Comprehensive Improvement Flow
```
/grm-improve
  ├── Automatically invokes: analyze-semantics
  ├── Automatically invokes: validate-boundaries
  └── Automatically invokes: validate-structure
```

### Standalone Analysis
- `/grm-analyze-semantics` - Just semantic analysis
- `/grm-arcana-validate` - Just structure validation
- `/grm-arcana-validate-boundaries` - Just boundary validation (Arcana invocation)

### Creation Flow
1. `/grm-create-grimoire` - Create grimoire first
2. `/grm-create-chapter [topic]` - Add chapters
3. `/grm-improve` - Optimize periodically

---

## Related Documentation

- **Invocation execution help**: `/grm-help`
- **Arcana invocations** (maintainer): `GRIMOIRE_ARCANA/invocations/arcana/INDEX.md`
- **Meta invocations**: `../meta/INDEX.md`
- **Operating model**: `../../docs/operating_model.md`

---

## For Invocation Authors

**When creating a new grimoire invocation**:

1. Create `invocations/grimoire/your_invocation.md` from template
2. Required sections: Purpose, Invocation, Workflow
3. Save file

**NOT required**:
- ~~Add entry to this INDEX.md~~ (auto-discovered)
- ~~Update invocation count~~ (auto-calculated)
- ~~Update help.md~~ (dynamic generation)

**Validation**: Run `/grm-arcana-validate` to verify

---

**Invocation count**: Auto-validated by `validate-arcana-structure` invocation

**Architecture**: Single-source + dynamic generation
