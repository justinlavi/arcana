# Grimoire Reference Guide

**Terminology, symbols, and conventions for Arcana**

---

## ⚡ The Magical Boundary ⚡

**IMPORTANT**: Grimoire has two layers with different terminology:

### 🔮 The System (Context) = Magical
When **using** or **talking about** Grimoire itself:
- Use playful, magical language
- "Perform an invocation", "consult your grimoire", "Arcana"
- AI agents should embody a helpful wizard when operating Grimoire

### 📝 The Content = Practical
When **creating knowledge** inside chapters:
- Use natural, domain-specific terminology
- Engineering: `templates/`, `scripts/`, `snippets/`, `configs/`
- Operations: `policies/`, `guides/`, `checklists/`
- Business: `playbooks/`, `frameworks/`, `worksheets/`
- **Never** create `invocations/`, `formulae/`, or `rites/` in domain grimoires

**Why?** Discoverability and clarity. Engineers search for "CMake template" not "build formula".

### AI Agents
- **Magical language** for Grimoire operations: "performing invocation", "consulting grimoire", "routing to chapter", `/grm-*` skills
- **Practical language** for content creation: standard domain terminology, real folder names (`templates/`, `scripts/`), no magical terms in chapter content
- The magic is in the **system**, not the **content**

---

## 🔮 Core Concepts

| Concept | Magical Term | Directory/File |
|---------|--------------|----------------|
| Universal foundation | **Arcana** | Standalone at `~/grimoire/arcana/`, referenced via `GRIMOIRE_ARCANA` |
| Domain knowledge base | **Grimoire** | domain grimoire repository root |
| Knowledge category | **Chapter** | `chapters/` |
| Sub-category | **Sub-chapter** | `chapters/{name}/{sub}/` |
| Knowledge document | **Page** | `*.md` files |
| Executable workflow | **Invocation** | `invocations/grimoire/*.md` and `invocations/arcana/*.md` |
| Template/blueprint | **Formula** | `formulae/*.md` (Arcana only) |
| Automation script | **Rite** | `rites/*.py` (Arcana only) |

**Note**: Invocations, Formulae, and Rites exist **only in Arcana**. Domain grimoires use practical terminology.

---

## Authority Models

Pages fall into one of three categories based on where truth lives:

| Model | When to Use |
|-------|-------------|
| **External** | Truth lives outside Grimoire (repos, services, platforms). Page routes and summarizes. |
| **Grimoire** | This page IS the source of truth. Knowledge is owned in Grimoire. |
| **Hybrid** | Grimoire owns the synthesis; external systems own implementation details. |

Page template: `GRIMOIRE_ARCANA/formulae/page.formula.md`

---

## 🪄 Skills

| Action | Skill |
|--------|-------|
| Create new grimoire | `/grm-create-grimoire` |
| Create new chapter | `/grm-create-chapter [topic]` |
| Improve domain grimoire | `/grm-improve` |
| Validate structure | `/grm-arcana-validate` |
| Semantic analysis | `/grm-analyze-semantics` |
| Boundary validation | `/grm-arcana-validate-boundaries` |
| Improve Arcana | `/grm-arcana-improve` |
| Show help | `/grm-help` |

Skills are registered to supported agent skill roots:

- Claude Code: `~/.claude/skills/`
- Codex/ChatGPT: `~/.codex/skills/`

Codex/ChatGPT registrations are pointer-only `SKILL.md` copies that resolve to Arcana or grimoire invocations and rites.

---

## Path Reference Convention

**IMPORTANT**: When referencing Grimoire paths, use named keys defined in the agent instruction file:

| Key | Purpose | Example |
|-----|---------|---------|
| `GRIMOIRE_ARCANA` | Reference Arcana from anywhere | `GRIMOIRE_ARCANA/docs/quickstart.md` |
| `{domain}-grimoire` | Reference a specific domain grimoire | `olympus-grimoire/chapters/build_system/INDEX.md` |

**Why?** Catalog keys match the actual folder slug. `olympus-grimoire` resolves to `~/grimoire/olympus-grimoire/`. `GRIMOIRE_ARCANA` is the exception — Arcana is the engine, not a domain grimoire.

**In `CLAUDE.md` and `AGENTS.md`**, the catalog maps keys to actual filesystem paths:
```markdown
**Catalog**: `~/grimoire/catalog.json`

**Arcana key**: `GRIMOIRE_ARCANA` = path to Arcana installation (e.g., `~/grimoire/arcana/`)
```

---

## Placeholders in Formulae

When creating new grimoires, use these placeholders in formula templates:

| Placeholder | Description |
|-------------|-------------|
| `{{GRIMOIRE_NAME}}` | Full grimoire name (e.g., "Knowledge Domain") |
| `{{GRIMOIRE_TOKEN}}` | All caps token (e.g., "DOMAIN") |
| `{{GRIMOIRE_DOMAIN}}` | Domain category (e.g., "engineering") |
| `{{GRIMOIRE_PURPOSE}}` | One-line purpose |
| `{{GRIMOIRE_PURPOSE_DETAILED}}` | Detailed purpose |
| `{{GRIMOIRE_DIRECTORY}}` | Filesystem name (e.g., "grimoire_domain_a") |
| `{{CHAPTER_ROUTES}}` | Generated routing pointers |
| `{{CHAPTER_LIST}}` | List of chapters with descriptions |
| `{{CHAPTER_TREE}}` | Directory tree of chapters |
| `{{EXAMPLE_CHAPTER}}` | Example chapter name |
| `{{OWNER_DOMAIN}}` | Domain that owns the grimoire |
| `{{DOMAIN_CHANNEL}}` | Domain's communication channel |
| `{{CREATION_DATE}}` | Date the grimoire was created |

---
