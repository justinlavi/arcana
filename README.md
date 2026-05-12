![arcana_icon](./resources/arcana_icon_512.png)

![arcanaheader](./resources/arcana_header.png)

**A framework for building grimoires** — structured, AI-navigable knowledge bases.

---

Give your AI agent a map, not a maze.

Most knowledge lives in scattered files that AI has to search through, interpolate between, and ultimately guess at. **Grimoires** give AI agents an explicit routing map: a layered index that leads from any question to the exact document that answers it — deterministically, every time.

**Arcana** is the engine you install once to build and maintain grimoires for any subject.

---

## What's a Grimoire?

A grimoire is a structured knowledge base built around a single subject — personal recipes, team runbooks, HR policies, research notes, a campaign's lore. It has two layers that work together.

### Knowledge layer: deterministic routing

A grimoire's content is organized by a layered `INDEX.md` router. When your agent gets a question, it reads:

1. Root `INDEX.md` — finds the right chapter
2. Chapter `INDEX.md` — finds the right document
3. That document — answers the question

Three reads. One answer. No guessing.

```
"What's the cure time for sourdough?"
                    ↓
cooking-grimoire/INDEX.md → chapters/breads/INDEX.md → sourdough.md
                    ↓
Authoritative answer, from your own documented notes.
```

### Skills layer: actionable commands

Every grimoire can also ship its own slash-command skills — domain-specific commands namespaced to that grimoire. Where the knowledge layer answers questions, the skills layer makes things happen:

| Grimoire | Skill | What it does |
|---|---|---|
| `cooking-grimoire` | `/cook-recipe-add` | Creates a new recipe from the grimoire's own template |
| `cooking-grimoire` | `/cook-meal-plan` | Builds a plan from your documented ingredient inventory |
| `hr-grimoire` | `/hr-onboarding-checklist` | Walks through the onboarding process step by step |
| `hr-grimoire` | `/hr-policy-lookup` | Routes to the right policy document for a situation |

Knowledge and skills compound: the better your documentation, the smarter your skills. A skill that scaffolds a new recipe already knows your format; one that runs onboarding already knows your policies. Any recurring task documented in a grimoire can become a skill that executes it.

Every chapter you add is one less thing your agent will hallucinate — and every skill you add is one more task your agent can carry out reliably.

---

## What's Arcana?

Arcana is the engine that powers all your grimoires. You install it once; your grimoires reference it forever.

Arcana ships the universal framework layer. Your grimoires contribute everything domain-specific.

**Arcana provides** (shared across every grimoire):
- `/grm-*` skills for creating, improving, validating, and managing grimoires
- Formula templates for scaffolding new grimoires and chapters
- Validation rites and library management automation
- Framework documentation and governance

**Your grimoires contribute**:
- Their chapters, pages, and content
- Their own `/{namespace}-*` skills — the actionable, domain-specific commands
- Their `grimoire.json` manifest declaring their identity and skill namespace

When you update Arcana, all your grimoires benefit — because they reference it rather than copy from it.

---

## Supported Agents

Arcana registers skills to:

- **Claude Code** — full skill registration; Arcana's `/grm-*` commands plus each grimoire's own domain commands (e.g. `/cook-recipe-add`, `/hr-onboarding-checklist`)
- **Codex / ChatGPT** — pointer-only registration from the same source files
- **GitHub Copilot, Cursor** — via the agent instruction block injected into `CLAUDE.md` / `AGENTS.md`

---

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash
```

The summoning rite installs Arcana, walks you through selecting grimoires to clone, and configures your agent instruction file automatically.

Open a new agent session and run `/grm-meta-help` to see every available command.

→ [Full installation guide](docs/installation.md) · [5-minute smoke test](docs/quickstart.md)

---

## Layout

```
~/grimoires/
├── arcana/              # The engine — install once, reference forever
│   ├── invocations/     # AI-guided workflows (create, improve, validate)
│   ├── formulae/        # Templates for chapters and pages
│   ├── rites/           # Python automation scripts
│   ├── skills/          # Slash-command source files
│   └── docs/            # Framework documentation
│
├── cooking-grimoire/    # A personal grimoire
│   ├── INDEX.md         # Root router
│   ├── grimoire.json    # namespace: cook  →  /cook-* skills
│   ├── skills/          # Domain skills: /cook-recipe-add, /cook-meal-plan, ...
│   └── chapters/        # recipes/, techniques/, equipment/, ...
│
├── hr-grimoire/         # A workplace grimoire
│   ├── INDEX.md
│   ├── grimoire.json    # namespace: hr  →  /hr-* skills
│   ├── skills/          # Domain skills: /hr-onboarding-checklist, /hr-policy-lookup, ...
│   └── chapters/        # onboarding/, policies/, benefits/, ...
│
└── library.json         # Registry of installed grimoires and their paths
```

Create as many grimoires as you need. Arcana provides the framework; each grimoire supplies its own knowledge and skills.

---

## Documentation

| | |
|---|---|
| [Installation](docs/installation.md) | One-command setup, manual setup, troubleshooting |
| [Quickstart](docs/quickstart.md) | Verify your install in 5 minutes |
| [Agent Configuration](docs/agent_configuration.md) | Claude Code, Codex, Copilot, Cursor |
| [Skill Catalog](docs/skills.md) | Every `/grm-*` command with descriptions |
| [Operating Model](docs/operating_model.md) | The routing model in depth |
| [Reference](docs/reference.md) | Terminology, schemas, path conventions |
| [Governance](docs/governance.md) | Maintaining and versioning Arcana |
| [Full Index](INDEX.md) | Navigate everything |
