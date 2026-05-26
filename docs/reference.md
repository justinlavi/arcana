---
type: reference
title: "Arcana Reference Guide"
aliases: ["terminology", "glossary", "reference"]
tags: [type/reference, arcana/docs]
authority: grimoire
last_verified: 2026-05-12
---

# Arcana Reference Guide

**Terminology, symbols, and conventions for Arcana**

---

## ⚡ The Magical Boundary ⚡

**IMPORTANT**: Arcana and grimoires have two vocabulary layers with different jobs:

### 🔮 The System (Context) = Magical
When **using** Arcana or talking about the framework layer:
- Use playful, magical language
- "Perform an invocation", "consult your grimoire", "Arcana"
- AI agents may use the magical vocabulary when operating Arcana-managed workflows

### 📝 The Content = Practical
When **creating knowledge** inside chapters:
- Use natural, subject-specific terminology
- Personal / hobby: `recipes/`, `techniques/`, `equipment/`, `notes/`
- Operations / HR: `policies/`, `guides/`, `checklists/`, `forms/`
- Engineering: `templates/`, `scripts/`, `snippets/`, `configs/`
- **Never** create `invocations/`, `formulae/`, or `rites/` in grimoires

**Why?** Discoverability and clarity. A cook searches for "sourdough recipe" not "bread formula".

### AI Agents
- **Magical language** for Arcana-managed operations: "performing invocation", "consulting grimoire", "routing to chapter", `/arc-*` skills
- **Practical language** for content creation: standard domain terminology, real folder names (`templates/`, `scripts/`), no magical terms in chapter content
- The magic is in the **system**, not the **content**

---

## Core Concepts

| Concept | Magical Term | Directory/File |
|--------|-------------|---------------|
| Universal foundation | **Arcana** | Standalone at `~/grimoires/arcana/`, referenced via `ARCANA_HOME` |
| Knowledge base instance | **Grimoire** | grimoire repository root |
| Grimoire identity | **Manifest** | `grimoire.json` at grimoire root (declares name, skill prefix, description) |
| Knowledge category | **Chapter** | `chapters/` |
| Sub-category | **Sub-chapter** | `chapters/{name}/{sub}/` |
| Knowledge document | **Page** | `*.md` files |
| Executable workflow | **Invocation** | `invocations/grimoire/*.md` and `invocations/arcana/*.md` |
| Template/blueprint | **Formula** | `formulae/*.md` (Arcana only) |
| Automation script | **Rite** | `rites/*.py` (Arcana only) |

**Note**: Invocations, Formulae, and Rites exist **only in Arcana**. Grimoires use practical terminology.

---

## Authority Models

Every page declares one of `external`, `grimoire`, or `hybrid` to indicate where truth lives. Full table, required-fields matrix, and rules of thumb in [page schema](page_schema.md#authority-models).

Page template: `ARCANA_HOME/formulae/page.formula.md`

---

## Skills

The current Arcana skill catalog lives in **[skills](skills.md)** (auto-generated from each Arcana `skills/<family>/<slug>/SKILL.md`). To enumerate every skill installed for an agent — Arcana plus every grimoire — invoke `/arc-help`.

Skill names use command-family prefixes: Arcana ships `arc-*` for platform operations and `grm-*` for universal grimoire operations. Each grimoire ships `{skill prefix}-*` from its own manifest. The canonical schema is [skill schema](skill_schema.md).

Source `SKILL.md` files use `name: {{SKILL_PREFIX}}-<registered-slug>` and the registration rite substitutes the command-family or grimoire skill prefix at install time. Skill targets and copy modes are defined in [agent targets](agent_targets.md).

---

## Local Library

Arcana uses one local library: `~/grimoires/library.json`. It is a **pure registry**: it records *where* installed grimoires live, nothing else. Each grimoire's identity (name, skill prefix, description) lives in its own [manifest](#grimoire-manifest).

`~/grimoires/library.json`, created by the summoning rite or `/arc-library-sync`. Lists grimoires the user has cloned and where they live on disk.

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

To add a grimoire, run `/arc-library-sync` after cloning into `~/grimoires/`. To detect drift (stale entries, missing grimoires, unmanaged directories), run the same skill in dry-run mode.

---

## Grimoire Manifest

Every grimoire declares its identity in a `grimoire.json` file at its repository root:

```json
{
  "name": "cooking-grimoire",
  "skill_prefix": "cook",
  "description": "Personal cooking knowledge: recipes, techniques, equipment"
}
```

Fields:
- `name` — canonical grimoire name; should match the library key.
- `skill_prefix` — short lowercase slug (`^[a-z][a-z0-9]*$`) used as the skill prefix. Required if the grimoire has a `skills/` directory.
- `description` — one-line description.

Arcana is not a grimoire and uses `arcana.json` instead:

```json
{
  "name": "arcana",
  "kind": "arcana",
  "skill_prefix": "arc",
  "skill_families": {
    "arcana": {"skill_prefix": "arc", "path": "skills/arcana", "slug_prefix": ""},
    "grimoire": {"skill_prefix": "grm", "path": "skills/grimoire", "slug_prefix": ""},
    "agent": {"skill_prefix": "arc", "path": "skills/agent", "slug_prefix": "agent"},
    "library": {"skill_prefix": "arc", "path": "skills/library", "slug_prefix": "library"},
    "workspace": {"skill_prefix": "arc", "path": "skills/workspace", "slug_prefix": "workspace"},
    "help": {"skill_prefix": "arc", "path": "skills/help", "slug_prefix": ""}
  },
  "description": "Framework for creating and maintaining grimoires"
}
```

`skill_prefix` remains as the default Arcana prefix for tooling that needs a compact identity, while `skill_families` defines the user-facing command families that Arcana itself ships.

**Why not in the library?** The grimoire owns its own identity. A cloned grimoire knows its skill prefix without needing a library entry, the registration rite reads skill prefix directly from the grimoire, and there is no way for library and grimoire to drift out of sync.

When creating a new grimoire, `/grm-create` prompts for the skill prefix and writes `grimoire.json` as part of scaffolding.

---

## Path Reference Convention

**IMPORTANT**: When referencing Grimoire paths, use named keys defined in the agent instruction file:

| Key | Purpose | Example |
|----|--------|--------|
| `ARCANA_HOME` | Reference Arcana from anywhere | `ARCANA_HOME/docs/installation.md` |
| `{domain}-grimoire` | Reference a specific grimoire | `cooking-grimoire/chapters/breads/sourdough.md` |

**Why?** Library keys match the actual folder slug. `cooking-grimoire` resolves to `~/grimoires/cooking-grimoire/`. `ARCANA_HOME` is the exception — Arcana is the engine, not a grimoire.

**In automatic agent instruction files**, the library maps keys to actual filesystem paths:
```markdown
**Library**: `~/grimoires/library.json`

**Arcana key**: `ARCANA_HOME` = path to Arcana installation (e.g., `~/grimoires/arcana/`)
```

---

## Placeholders in Formulae

When creating new grimoires, use these placeholders in formula templates:

| Placeholder | Description | Example value |
|------------|------------|--------------|
| `{{GRIMOIRE_NAME}}` | Display name; brand only - used in the root-hub H1 | `Cooking`, `HR`, `Project Alpha` |
| `{{GRIMOIRE_NAME_LOWER}}` | Lowercase display name for aliases and prose | `cooking`, `hr`, `project alpha` |
| `{{GRIMOIRE_TOKEN}}` | All-caps token | `COOKING`, `HR` |
| `{{GRIMOIRE_DOMAIN}}` | Subject area / category | `cooking`, `human resources` |
| `{{GRIMOIRE_PURPOSE}}` | Short tagline, 2–5 words; used in the manifest `description` and as an italic subtitle in the root hub | `personal cooking knowledge`, `HR runbooks and policies`, `Project Alpha knowledge` |
| `{{GRIMOIRE_PURPOSE_DETAILED}}` | Long-form description; lives **only** in `README.md`; never duplicated to manifest or hub | `recipes, techniques, equipment, and ingredient inventories — the full personal cooking reference` |
| `{{GRIMOIRE_DIRECTORY}}` | Filesystem name | `cooking-grimoire`, `hr-grimoire` |
| `{{GRIMOIRE_REPO_URL}}` | Canonical git URL for installing this grimoire | `https://git.example.com/you/cooking-grimoire.git` |
| `{{SKILL_PREFIX}}` | Short slug for skill prefix | `cook`, `hr` |
| `{{CHAPTER_ROUTES}}` | Generated routing pointers (filled by create_grimoire) | - |
| `{{CHAPTER_LIST}}` | List of chapters with descriptions | - |
| `{{CHAPTER_TREE}}` | Directory tree of chapters | - |
| `{{EXAMPLE_CHAPTER}}` | One example chapter name | `recipes`, `onboarding` |
| `{{OWNER_DOMAIN}}` | Who maintains this grimoire | `Personal`, `People Ops` |
| `{{CREATION_DATE}}` | ISO date the grimoire was created | `2026-05-13` |

**Description-duplication policy.** Three description-shaped placeholders, each with a single canonical home:

- `GRIMOIRE_NAME` — brand only, used in the root-hub H1 and as the manifest `name` field.
- `GRIMOIRE_PURPOSE` — short tagline, 2–5 words. Lives in the manifest `description` and as an italic subtitle under the root hub's H1. Surfaces in skill pickers, library listings, and at-a-glance scans.
- `GRIMOIRE_PURPOSE_DETAILED` — long-form paragraph. Lives in `README.md` only; never duplicated to the manifest, the root hub, the log, or any skill file. If another page needs the description, link to README.

This prevents the same description from drifting across three files while still letting the manifest and hub carry a one-line tagline that's useful at a glance.

---

## Text File Standard

Arcana and every grimoire use the same repository text standard:

- UTF-8 without BOM.
- LF line endings.
- Unicode is allowed when useful for readability, including emoji, em dashes, arrows, and box-drawing characters.
- Mojibake and repair artifacts are not allowed.

This is enforced by `.gitattributes`, `.editorconfig`, `/arc-validate-encoding`, and `/grm-validate-encoding`.

---
