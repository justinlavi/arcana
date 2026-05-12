# 🧙‍♂️ Arcana Invocations Catalog

**Arcana maintainer only - invocations that modify Arcana itself**

⚠️ **These invocations require maintainer privileges** - they modify the universal Grimoire foundation.

---

## Single Source Architecture

**This catalog is a THIN ROUTER** - invocation files are the single source of truth.

For dynamic invocation catalog with full details, use: **`/grm-help`**

For detailed documentation, read the invocation file directly.

---

## Available Arcana Invocations

### 🔧 Improvement & Validation

- **[improve_arcana.md](improve_arcana.md)** - Comprehensive Arcana improvement (orchestrates all validations and improvements)
- **[validate_boundaries.md](validate_boundaries.md)** - Magical/practical boundary enforcement

### ⚡ Validators

Modular validation invocations (can run independently or via improve-arcana):

- **[validators/validate_structure.md](validators/validate_structure.md)** - Directory/file integrity
- **[validators/validate_naming.md](validators/validate_naming.md)** - Snake_case enforcement
- **[validators/validate_semantics.md](validators/validate_semantics.md)** - Reference-driven terminology
- **[validators/validate_format.md](validators/validate_format.md)** - Invocation/formula schema
- **[validators/validate_links.md](validators/validate_links.md)** - Broken reference detection
- **[validators/validate_security.md](validators/validate_security.md)** - Credential scanning & bash safety

See [validators/INDEX.md](validators/INDEX.md) for details.

### ✨ Quality Enhancement

Advanced quality improvement invocations:

- **[quality/detect_duplication.md](quality/detect_duplication.md)** - DRY principle enforcement
- **[quality/improve_documentation.md](quality/improve_documentation.md)** - Documentation excellence
- **[quality/validate_rites.md](quality/validate_rites.md)** - Rite script quality

See [quality/INDEX.md](quality/INDEX.md) for details.

---

## Quick Reference

| Name | Command | Purpose |
|------|---------|---------|
| improve-arcana | `/grm-arcana-improve` | Evolve Arcana |
| validate-boundaries | `/grm-arcana-validate-boundaries` | Magical boundary enforcement |
| validate-structure | `/grm-arcana-validate` | Directory/file integrity checks |
| validate-semantics | `/grm-arcana-improve` | Reference-driven terminology validation |
| validate-naming | `/grm-arcana-improve` | Snake_case naming enforcement |
| validate-format | `/grm-arcana-improve` | Invocation/formula schema compliance |
| validate-links | `/grm-arcana-improve` | Broken reference detection |
| validate-security | `/grm-arcana-improve` | Security scanning |
| detect-duplication | `/grm-arcana-improve` | DRY principle enforcement |
| improve-documentation | `/grm-arcana-improve` | Documentation quality enhancement |
| validate-rites | `/grm-arcana-improve` | Rite script quality validation |

---

## Arcana vs Grimoire vs Meta Invocations

**Arcana Invocations** (`invocations/arcana/`):
- Operate on Arcana itself
- Modify universal invocations, formulae, rites
- Enforce system-wide quality gates
- Arcana maintainer only

**Grimoire Invocations** (`invocations/grimoire/`):
- Operate on domain grimoires
- Create and improve domain knowledge
- Available to all users
- See: `../grimoire/INDEX.md`

**Meta Invocations** (`invocations/meta/`):
- System documentation and help
- Available to everyone
- See: `../meta/INDEX.md`

---

## For Domain Users

If you're not the Arcana maintainer, you want **grimoire invocations**:

→ Use `/grm-help` to list all available invocations
→ See `../grimoire/INDEX.md` for domain operations

---

## For the Arcana Maintainer

### When to Run Arcana Invocations

**improve-arcana**:
- Monthly: Quick audit to catch drift
- Quarterly: Full improvement cycle
- Before releases: Version preparation
- After major changes: Validate templates

**validate-boundaries**:
- Before Arcana releases (with --arcana flag)
- Quarterly quality validation
- After modifying invocations/formulae

**Validator invocations**:
- Run individually for targeted checks: `/grm-arcana-validate`
- Run all at once: `python3 rites/validate.py`
- Integrated into improve-arcana workflow

---

## For Invocation Authors

**When creating a new Arcana invocation**:

1. Create `invocations/arcana/your_invocation.md` from template
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
