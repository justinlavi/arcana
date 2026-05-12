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

Pages fall into one of three categories based on where truth lives:

| Model | When to Use |
|-------|-------------|
| **External** | Truth lives outside Grimoire (repos, services, platforms). Page routes and summarizes. |
| **Grimoire** | This page IS the source of truth. Knowledge is owned in Grimoire. |
| **Hybrid** | Grimoire owns the synthesis; external systems own implementation details. |

Page template: `GRIMOIRE_ARCANA/formulae/page.formula.md`

---

## 🪄 Skills

The complete, current Arcana skill catalog lives in **[skills.md](skills.md)** (auto-generated from each `skills/<slug>/SKILL.md` — single source of truth). For each skill the catalog shows the `/grm-...` command, a one-line description, and a link to the source `SKILL.md`.

To enumerate every skill installed for an agent (Arcana plus every domain grimoire), invoke `/grm-meta-help`.

Skills are registered to supported agent skill roots:

- Claude Code: `~/.claude/skills/`
- Codex/ChatGPT: `~/.codex/skills/`

Codex/ChatGPT registrations are pointer-only `SKILL.md` copies that resolve to Arcana or grimoire invocations and rites.

Skill command names use explicit namespace roots:
- Arcana: `grm-*` (declared in `arcana/grimoire.json`)
- Domain grimoires: `{namespace}-*`, declared in each grimoire's `grimoire.json`

Domain skill folders provide the subcommand after the namespace root. For example, a grimoire with `"namespace": "jpn"` in its `grimoire.json` plus `skills/travel-create-trip/` registers `/jpn-travel-create-trip`. Source `SKILL.md` files use `name: {{NAMESPACE}}-<slug>` and the registration rite substitutes the namespace at install time.

---

## Libraries

Grimoire uses two library files. The library is a **pure registry** — it records *where* grimoires live, nothing else. Each grimoire's identity (name, namespace, description) lives in its own [manifest](#grimoire-manifest).

### Global library (Arcana repo)

`library.json` at the Arcana repo root. Lists grimoires available for the summoning rite to install. Each deployment populates it with its own grimoires and URLs.

```json
{
  "grimoires": {
    "olympus-grimoire": {
      "name": "Olympus",
      "description": "Olympus domain grimoire",
      "online_path": "https://git.example.com/grimoire/olympus-grimoire.git"
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
    "olympus-grimoire": {
      "local_path": "$HOME/grimoires/olympus-grimoire",
      "online_path": "https://git.example.com/grimoire/olympus-grimoire.git"
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
  "name": "olympus-grimoire",
  "namespace": "oly",
  "description": "Olympus engineering domain grimoire"
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
| `GRIMOIRE_ARCANA` | Reference Arcana from anywhere | `GRIMOIRE_ARCANA/docs/quickstart.md` |
| `{domain}-grimoire` | Reference a specific domain grimoire | `olympus-grimoire/chapters/build_system/INDEX.md` |

**Why?** Library keys match the actual folder slug. `olympus-grimoire` resolves to `~/grimoires/olympus-grimoire/`. `GRIMOIRE_ARCANA` is the exception — Arcana is the engine, not a domain grimoire.

**In `CLAUDE.md` and `AGENTS.md`**, the library maps keys to actual filesystem paths:
```markdown
**Library**: `~/grimoires/library.json`

**Arcana key**: `GRIMOIRE_ARCANA` = path to Arcana installation (e.g., `~/grimoires/arcana/`)
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
