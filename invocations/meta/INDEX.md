# 🔮 Meta Invocations Catalog

**System documentation and meta-operations - invocations about Grimoire itself**

These invocations provide information about Grimoire — they don't modify grimoires or Arcana.

---

## Single Source Architecture

**This catalog is a THIN ROUTER** - invocation files are the single source of truth.

For dynamic invocation catalog with full details, use: **`/grm-help`**

For detailed documentation, read the invocation file directly.

---

## Available Meta Invocations

### 📖 Documentation

- **[help.md](help.md)** - Display invocation catalog (dynamically generated from invocation files)

### ⚙️ Arcana

- **[base_invocation.md](base_invocation.md)** - Generic invocation execution template for custom requests

---

## Quick Reference

| Name | Command | Purpose |
|------|---------|---------|
| help | `/grm-help` | Show dynamically-generated invocation catalog |
| base-invocation | `/grm-help` | Generic invocation execution framework |

---

## How These Invocations Work

### help - Dynamic Catalog Generation
```
User: /grm-help
Claude:
  1. Scans invocations/grimoire/*.md, invocations/arcana/*.md, invocations/meta/*.md
  2. Extracts Purpose, Invocation from each invocation
  3. Generates formatted catalog on-the-fly
  4. Displays to user

Single source: Individual invocation files ✅
Zero duplication ✅
```

### base-invocation - Generic Request Routing
```
User: /grm-help
Claude:
  1. Parses request to determine intent
  2. Routes to appropriate invocation OR
  3. Creates custom workflow if no invocation matches
  4. Provides magical boundary guidance
```

---

## Meta vs Grimoire vs Arcana Invocations

**Meta Invocations** (`invocations/meta/`):
- Provide information about Grimoire
- Don't modify grimoires or Arcana
- Documentation and help tools
- Available to everyone

**Grimoire Invocations** (`invocations/grimoire/`):
- Operate on domain grimoires
- Create and improve domain knowledge
- Available to all users
- See: `../grimoire/INDEX.md`

**Arcana Invocations** (`invocations/arcana/`):
- Operate on Arcana itself
- Modify universal components
- Arcana maintainer only
- See: `../arcana/INDEX.md`

---

## Common Use Cases

**Most common use cases**:

→ **Need help?** Invoke `/grm-help` (shows all invocations)
→ **Create grimoire?** Invoke `/grm-create-grimoire` (grimoire invocation)
→ **Improve grimoire?** Invoke `/grm-improve` (grimoire invocation)
→ **Need something else?** Use `/grm-help` to see all available skills

See `../grimoire/INDEX.md` for domain operations.

---

## For Invocation Authors

**When creating a new meta invocation**:

1. Create `invocations/meta/your_invocation.md` from template
2. Required sections: Purpose, Invocation
3. Save file

**NOT required**:
- ~~Add entry to this INDEX.md~~ (auto-discovered)
- ~~Update invocation count~~ (auto-calculated)
- ~~Update help.md~~ (it's the invocation, not a catalog!)

**Validation**: Run `/grm-arcana-validate` to verify

---

## Related

- **Full invocation list**: Invoke `/grm-help`
- **Grimoire invocations**: `../grimoire/INDEX.md`
- **Arcana invocations**: `../arcana/INDEX.md`

---

**Invocation count**: Auto-validated by `validate-arcana-structure` invocation

**Architecture**: Single-source + dynamic generation
