---
type: reference
title: "Grimoire Reference Guide"
aliases: ["terminology", "glossary", "reference"]
tags: [type/reference, arcana/docs]
authority: grimoire
last_verified: 2026-05-12
---

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
- Use natural, subject-specific terminology
- Personal / hobby: `recipes/`, `techniques/`, `equipment/`, `notes/`
- Operations / HR: `policies/`, `guides/`, `checklists/`, `forms/`
- Engineering: `templates/`, `scripts/`, `snippets/`, `configs/`
- **Never** create `invocations/`, `formulae/`, or `rites/` in domain grimoires

**Why?** Discoverability and clarity. A cook searches for "sourdough recipe" not "bread formula".

### AI Agents
- **Magical language** for Grimoire operations: "performing invocation", "consulting grimoire", "routing to chapter", `/grm-*` skills
- **Practical language** for content creation: standard domain terminology, real folder names (`templates/`, `scripts/`), no magical terms in chapter content
- The magic is in the **system**, not the **content**

---

## 🔮 Core Concepts

| Concept | Magical Term | Directory/File |
|---------|--------------|----------------|
| Universal foundation | **Arcana** | Standalone at `~/grimoires/arcana/`, referenced via `GRIMOIRE_ARCANA` |
| Domain knowledge base | **Grimoire** | domain grimoire repository root |
| Grimoire identity | **Manifest** | `grimoire.json` at grimoire root (declares name, namespace, description) |
| Knowledge category | **Chapter** | `chapters/` |
| Sub-category | **Sub-chapter** | `chapters/{name}/{sub}/` |
| Knowledge document | **Page** | `*.md` files |
| Executable workflow | **Invocation** | `invocations/grimoire/*.md` and `invocations/arcana/*.md` |
| Template/blueprint | **Formula** | `formulae/*.md` (Arcana only) |
| Automation script | **Rite** | `rites/*.py` (Arcana only) |

**Note**: Invocations, Formulae, and Rites exist **only in Arcana**. Domain grimoires use practical terminology.

---

## Authority Models

Every page declares one of `external`, `grimoire`, or `hybrid` to indicate where truth lives. Full table, required-fields matrix, and rules of thumb in [page_schema.md § Authority Models](page_schema.md#authority-models).

Page template: `GRIMOIRE_ARCANA/formulae/page.formula.md`

---

## 🪄 Skills

The current Arcana skill catalog lives in **[skills.md](skills.md)** (auto-generated from each `skills/<slug>/SKILL.md`). To enumerate every skill installed for an agent — Arcana plus every domain grimoire — invoke `/grm-meta-help`.

Skill names use namespace roots: Arcana ships `grm-*` (declared in `arcana/grimoire.json`); each domain grimoire ships `{namespace}-*` from its own manifest. Source `SKILL.md` files use `name: {{NAMESPACE}}-<slug>` and the registration rite substitutes the namespace at install time. Skills register to `~/.claude/skills/` (Claude Code) and `~/.codex/skills/` (Codex/ChatGPT, pointer-only).

---

## Libraries

Grimoire uses two library files. The library is a **pure registry** — it records *where* grimoires live, nothing else. Each grimoire's identity (name, namespace, description) lives in its own [manifest](#grimoire-manifest).

### Global library (Arcana repo)

`library.json` at the Arcana repo root. Lists grimoires available for the summoning rite to install. Each deployment of Arcana populates it with the grimoires that fork distributes.

```json
{
  "grimoires": {
    "cooking-grimoire": {
      "name": "Cooking",
      "description": "Personal cooking knowledge: recipes, techniques, equipment",
      "online_path": "https://git.example.com/you/cooking-grimoire.git"
    },
    "hr-grimoire": {
      "name": "HR",
      "description": "Onboarding, policies, benefits, performance reviews",
      "online_path": "https://git.example.com/your-team/hr-grimoire.git"
    }
  }
}
```

Fields:
- `name` — display name for the summoning menu.
- `description` — short description shown during selection.
- `online_path` — git clone URL (any git-compatible host).

### Local library (per-user)

`~/grimoires/library.json`, created by the summoning rite or `/grm-library-sync`. Lists grimoires the user has cloned and where they live on disk.

```json
{
  "grimoires": {
    "cooking-grimoire": {
      "local_path": "$HOME/grimoires/cooking-grimoire",
      "online_path": "https://git.example.com/you/cooking-grimoire.git"
    },
    "hr-grimoire": {
      "local_path": "$HOME/grimoires/hr-grimoire",
      "online_path": "https://git.example.com/your-team/hr-grimoire.git"
    }
  }
}
```

Fields:
- `local_path` — absolute filesystem path to the grimoire root (supports `$HOME`).
- `online_path` — git clone URL; set to `null` if not applicable.

To add a grimoire, run `/grm-library-sync` after cloning into `~/grimoires/`. To detect drift (stale entries, missing grimoires, unmanaged directories), run the same skill in dry-run mode.

---

## Grimoire Manifest

Every grimoire (and Arcana itself) declares its identity in a `grimoire.json` file at its repository root:

```json
{
  "name": "cooking-grimoire",
  "namespace": "cook",
  "description": "Personal cooking knowledge: recipes, techniques, equipment"
}
```

Fields:
- `name` — canonical grimoire name; should match the library key.
- `namespace` — short lowercase slug (`^[a-z][a-z0-9]*$`) used as the skill prefix. Required if the grimoire has a `skills/` directory.
- `description` — one-line description.

**Why not in the library?** The grimoire owns its own identity. A cloned grimoire knows its namespace without needing a library entry, the registration rite reads namespace directly from the grimoire, and there is no way for library and grimoire to drift out of sync.

When creating a new grimoire, `/grm-domain-create-grimoire` prompts for the namespace and writes `grimoire.json` as part of scaffolding.

---

## Path Reference Convention

**IMPORTANT**: When referencing Grimoire paths, use named keys defined in the agent instruction file:

| Key | Purpose | Example |
|-----|---------|---------|
| `GRIMOIRE_ARCANA` | Reference Arcana from anywhere | `GRIMOIRE_ARCANA/docs/installation.md` |
| `{domain}-grimoire` | Reference a specific domain grimoire | `cooking-grimoire/chapters/breads/sourdough.md` |

**Why?** Library keys match the actual folder slug. `cooking-grimoire` resolves to `~/grimoires/cooking-grimoire/`. `GRIMOIRE_ARCANA` is the exception — Arcana is the engine, not a domain grimoire.

**In `CLAUDE.md` and `AGENTS.md`**, the library maps keys to actual filesystem paths:
```markdown
**Library**: `~/grimoires/library.json`

**Arcana key**: `GRIMOIRE_ARCANA` = path to Arcana installation (e.g., `~/grimoires/arcana/`)
```

---

## Placeholders in Formulae

When creating new grimoires, use these placeholders in formula templates:

| Placeholder | Description | Example value |
|-------------|-------------|---------------|
| `{{GRIMOIRE_NAME}}` | Display name; brand only — used in the root-hub H1 | `Cooking`, `HR`, `Olympus` |
| `{{GRIMOIRE_TOKEN}}` | All-caps token | `COOKING`, `HR` |
| `{{GRIMOIRE_DOMAIN}}` | Subject area / category | `cooking`, `human resources` |
| `{{GRIMOIRE_PURPOSE}}` | Short tagline, 2–5 words; used in the manifest `description` and as an italic subtitle in the root hub | `Olympus knowledge`, `personal cooking knowledge`, `HR runbooks and policies` |
| `{{GRIMOIRE_PURPOSE_DETAILED}}` | Long-form description; lives **only** in `README.md`; never duplicated to manifest or hub | `recipes, techniques, equipment, and ingredient inventories — the full personal cooking reference` |
| `{{GRIMOIRE_DIRECTORY}}` | Filesystem name | `cooking-grimoire`, `hr-grimoire` |
| `{{SKILL_NAMESPACE}}` | Short slug for skill prefix | `cook`, `hr` |
| `{{CHAPTER_ROUTES}}` | Generated routing pointers (filled by create_grimoire) | — |
| `{{CHAPTER_LIST}}` | List of chapters with descriptions | — |
| `{{CHAPTER_TREE}}` | Directory tree of chapters | — |
| `{{EXAMPLE_CHAPTER}}` | One example chapter name | `recipes`, `onboarding` |
| `{{OWNER_DOMAIN}}` | Who maintains this grimoire | `Personal`, `People Ops` |
| `{{CREATION_DATE}}` | ISO date the grimoire was created | `2026-05-13` |

**Description-duplication policy.** Three description-shaped placeholders, each with a single canonical home:

- `GRIMOIRE_NAME` — brand only, used in the root-hub H1 and as the manifest `name` field.
- `GRIMOIRE_PURPOSE` — short tagline, 2–5 words. Lives in the manifest `description` and as an italic subtitle under the root hub's H1. Surfaces in skill pickers, library listings, and at-a-glance scans.
- `GRIMOIRE_PURPOSE_DETAILED` — long-form paragraph. Lives in `README.md` only; never duplicated to the manifest, the root hub, the log, or any skill file. If another page needs the description, link to README.

This prevents the same description from drifting across three files while still letting the manifest and hub carry a one-line tagline that's useful at a glance.

---
