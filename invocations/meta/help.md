# 🔮 Invocation: Grimoire Help

## ⚡ Purpose

Display available Grimoire invocations dynamically by reading invocation files - ensures always-current catalog with zero duplication.

**This invocation is safe to run anytime.**

---

## Invocation

```
/grm-help
```

Or:

```
/grm-help
```

---

## How This Invocation Works (Dynamic Generation)

### Single Source of Truth Architecture

Unlike static documentation, `/grm-help` generates the invocation catalog **dynamically** by reading invocation files. This ensures:
- ✅ **Zero duplication** - invocation .md files are the only source
- ✅ **Always current** - new invocations automatically appear
- ✅ **Self-maintaining** - no manual catalog updates needed

### Execution Algorithm

When a user casts `/grm-help`, execute this workflow:

#### Step 1: Scan Invocation Directories

Read all invocation files from:
```bash
GRIMOIRE_ARCANA/invocations/grimoire/*.md
GRIMOIRE_ARCANA/invocations/arcana/*.md
GRIMOIRE_ARCANA/invocations/meta/*.md
```

Exclude INDEX.md files (routers only).

---

#### Step 2: Extract Metadata from Each Invocation

For each invocation .md file, extract:

**Required Sections** (read from markdown):
- **Invocation Title**: First `# ` heading (e.g., "# 📐 Invocation: Validate Structure")
- **Purpose**: Content under `## Purpose` or `## ⚡ Purpose` heading
- **Invocation**: Content under `## Invocation` heading
- **Category**: Infer from directory:
  - `invocations/grimoire/` → Grimoire Invocation
  - `invocations/arcana/` → Arcana Invocation
  - `invocations/meta/` → Meta Invocation

**Optional Sections**:
- **When to Use**: Content under `## When to Cast` or `## When to Use`
- **Related Invocations**: Content under `## Related Invocations`

---

#### Step 3: Categorize Invocations

Group invocations by type and category:

**Grimoire Invocations** (from `invocations/grimoire/`):
- 🎨 **Creation**: Invocations that create new grimoires/chapters
- 🔧 **Improvement**: Invocations that enhance existing grimoires
- 📊 **Analysis**: Invocations that audit/validate grimoires

**Arcana Invocations** (from `invocations/arcana/`):
- 🧙‍♂️ **Arcana Operations**: Invocations that modify Arcana itself
- 🔍 **Validation**: Invocations that enforce Arcana quality gates

**Meta Invocations** (from `invocations/meta/`):
- 🔮 **Documentation**: Invocations that provide information
- ⚙️ **Arcana**: Invocation execution templates

**Category Detection**:
Infer category from invocation content or file patterns:
- Contains "create" → Creation
- Contains "improve" → Improvement
- Contains "analyze" or "validate" → Analysis
- File: help.md, base_invocation.md → Meta

---

#### Step 4: Generate Formatted Catalog

Display invocation catalog using this template:

```
╔═══════════════════════════════════════════════════════════════╗
║                  🔮 GRIMOIRE INVOCATION CATALOG                    ║
╚═══════════════════════════════════════════════════════════════╝

📚 GRIMOIRE INVOCATIONS (Domain Operations)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎨 CREATION INVOCATIONS

🪄 [invocation-name]
   Invocation: [invocation syntax]
   Purpose: [purpose summary]
   When: [when to use - if available]

[Repeat for all creation invocations]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 IMPROVEMENT INVOCATIONS

[... similar format ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 ANALYSIS INVOCATIONS

[... similar format ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧙‍♂️ ARCANA INVOCATIONS (Maintainer Only)

[... similar format ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔮 META INVOCATIONS

[... similar format ...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📖 QUICK REFERENCE

Invocation                    | Invocation                        | Category
------------------------|-----------------------------------|-------------
[invocation-1]                | [invocation-1]                   | [category-1]
[invocation-2]                | [invocation-2]                   | [category-2]
[...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 COMMON WORKFLOWS

First time using Grimoire?
  1. /grm-help (read this guide)
  2. /grm-create-grimoire (create your domain grimoire)
  3. /grm-create-chapter [topic] (add chapters)
  4. /grm-improve (optimize periodically)

Improving existing grimoire?
  1. /grm-improve (comprehensive improvement)
     OR
  2. /grm-analyze-semantics (just naming analysis)
  3. /grm-arcana-validate-boundaries (just boundary check)
  4. /grm-arcana-validate (just structure check)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 DETAILED DOCUMENTATION

For detailed documentation on each invocation, read the invocation file directly:
  - Grimoire invocations: GRIMOIRE_ARCANA/invocations/grimoire/[invocation-name].md
  - Arcana invocations: GRIMOIRE_ARCANA/invocations/arcana/[invocation-name].md
  - Meta invocations: GRIMOIRE_ARCANA/invocations/meta/[invocation-name].md

Invocation catalogs (thin routers):
  - invocations/grimoire/INDEX.md
  - invocations/arcana/INDEX.md
  - invocations/meta/INDEX.md

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Cast `/grm-help` anytime for this dynamically-generated catalog!** 🔮

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

#### Step 5: Auto-Count Invocations

Display invocation counts dynamically:
```
Total Invocations: [count all .md files]
  - Grimoire Invocations: [count invocations/grimoire/*.md]
  - Arcana Invocations: [count invocations/arcana/*.md]
  - Meta Invocations: [count invocations/meta/*.md]
```

No manual counting needed! ✅

---

## Example Execution

### User Input
```
/grm-help
```

### Claude's Process
```python
# Pseudo-code for clarity
grimoire_invocations = scan_directory("invocations/grimoire/")
arcana_invocations = scan_directory("invocations/arcana/")
meta_invocations = scan_directory("invocations/meta/")

for invocation in all_invocations:
    metadata = extract_metadata(invocation)
    categorize(metadata)

catalog = generate_formatted_catalog(categorized_invocations)
display(catalog)
```

### User Sees
```
╔═══════════════════════════════════════════════════════════════╗
║                  🔮 GRIMOIRE INVOCATION CATALOG                    ║
╚═══════════════════════════════════════════════════════════════╝

📚 GRIMOIRE INVOCATIONS (Domain Operations)

🎨 CREATION INVOCATIONS

🪄 create-grimoire
   Invocation: /grm-create-grimoire
   Purpose: Create new grimoire for your domain
   When: Starting new knowledge base, new department/team

[... dynamic catalog continues ...]
```

---

## Invocation File Requirements

For `/grm-help` to extract properly, invocation files must have:
- `# ` title heading (first line or near top)
- `## Purpose` section
- `## Invocation` section

Optional: `## When to Cast`, `## Category`, `## Related Invocations`

---

## Related Invocations

- **base-invocation**: Generic invocation execution template
