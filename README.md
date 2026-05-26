![arcana_icon](./resources/arcana_icon_512.png)

![arcanaheader](./resources/arcana_header.png)

**A framework for building grimoires** — structured, AI-navigable knowledge bases the LLM keeps current.

---

Give your AI agent a map, not a maze.

Most knowledge lives in scattered files that AI has to search through, interpolate between, and ultimately guess at. **Grimoires** give AI agents an explicit routing map: a layered hub structure that leads from any question to the exact document that answers it — deterministically, every time. And the LLM owns the maintenance: it ingests new sources, updates cross-references, flags stale claims, and keeps the wiki compounding.

**Arcana** is the engine you install once to build and maintain grimoires for any subject.

---

## What's a Grimoire?

A grimoire is a structured knowledge base built around a single subject — personal recipes, team runbooks, HR policies, research notes, a campaign's lore.

### Deterministic routing through hubs

Every folder has a **hub** — a markdown file named after the folder. Each hop narrows the search; the agent stops at the leaf that answers the question.

```
"What's the cure time for sourdough?"            (shallow - 2 hops)
cooking-grimoire.md -> breads.md -> sourdough.md

"What's the windowpane test for laminated dough?"   (deeper - 4 hops)
cooking-grimoire.md -> techniques.md -> lamination.md -> windowpane_test.md
```

Both paths are deterministic. The structure stays only as deep as the topic warrants. Full rules in [operating model](docs/operating_model.md).

### Storage layers

A grimoire keeps four kinds of content side-by-side: **`sources/`** holds immutable artifacts the wiki cites; **`chapters/`** holds the LLM-authored wiki; **`inbox/`** is a transient drop zone for things waiting to be classified; **`log.md`** is an append-only record of every mutation. See [operating model](docs/operating_model.md) for ownership rules and the validator-enforced contracts.

### Skills

Every grimoire ships its own slash-command skills — commands prefixed by that grimoire:

| Grimoire | Skill | What it does |
|---|---|---|
| `cooking-grimoire` | `/cook-recipe-add` | Creates a new recipe from the grimoire's own template |
| `cooking-grimoire` | `/cook-meal-plan` | Builds a plan from your documented ingredient inventory |
| `hr-grimoire` | `/hr-onboarding-checklist` | Walks through the onboarding process step by step |
| `hr-grimoire` | `/hr-policy-lookup` | Routes to the right policy document for a situation |

Knowledge and skills compound: the better your documentation, the smarter your skills.

---

## The LLM does the maintenance

Arcana ships universal operations every grimoire inherits:

- **`/grm-ingest <source>`** — file a source under `sources/`, scan existing chapters, propose page updates, apply them, append to `log.md`.
- **`/grm-file-answer`** — promote a chat answer (analysis, comparison, derived insight) into a properly-frontmattered wiki page so it doesn't evaporate into chat history.
- **`/grm-lint`** — health-check the wiki: orphans, stale claims (>90 days unverified), ghost references (entities mentioned often but lacking a page), contradictions, missing cross-references.
- **`/grm-improve`** — comprehensive normalize-and-optimize pass.
- **`/grm-validate-all`** — run the full deterministic validator profile for the active grimoire.
- **`/grm-update-arcana`** — pull the latest Arcana and refresh the local agent/skill setup.
- **`/grm-register-skills`** — refresh Arcana skills plus the active grimoire's own skills.
- **`/grm-create-chapter`**, **`/grm-analyze-semantics`** — and more.

Arcana command families are prefix-explicit: `/arc-*` acts on Arcana/platform surfaces, `/grm-*` acts on an active grimoire, `/arc-library-*` acts on `~/grimoires/library.json`, `/arc-agent-*` acts on agent configuration, and `/arc-workspace-*` intentionally spans the local workspace. Full rules live in [skill schema](docs/skill_schema.md).

The human curates sources and asks questions. The LLM does the bookkeeping.

---

## What's Arcana?

Arcana is the engine that powers all your grimoires. You install it once; your grimoires reference it forever.

**Arcana provides** (shared across every grimoire):
- `/arc-*` platform skills and `/grm-*` universal grimoire skills
- The page schema (`type`, `authority`, `sources`, `last_verified` frontmatter) that makes wikis machine-checkable
- Formula templates for scaffolding new grimoires, chapters, and pages
- Validation rites: structure, naming, format, links, frontmatter, orphans, provenance, security, semantics, skill-refs, boundaries
- Library management automation
- Framework documentation and governance

**Your grimoires contribute**:
- Their `chapters/` (LLM-authored content) and `sources/` (immutable sources)
- Their own `/<skill prefix>-*` skills — actionable, domain-specific commands
- Their `grimoire.json` manifest declaring their identity and skill prefix
- Their `log.md` — the append-only activity record

When you update Arcana, all your grimoires benefit — because they reference it rather than copy from it.

---

## Supported Agents

Arcana automatically configures the agents it can safely write to. The current
target matrix lives in [agent targets](docs/agent_targets.md):

- **Claude Code** — full skill registration; Arcana's `/arc-*` and `/grm-*` commands plus each grimoire's own commands
- **Codex / ChatGPT** — pointer-only registration from the same source files
- **GitHub Copilot, Cursor, hosted ChatGPT, and other agents** — manual instruction-block setup; see [agent configuration](docs/agent_configuration.md) for setup notes

---

## Install

```bash
curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash
```

The summoning rite installs **Arcana** — the framework — configures your AI agents, and registers the `/arc-*` and `/grm-*` skill sets. If you have existing grimoires hosted on GitHub or GitLab, the rite can discover and clone them too. Otherwise, skip straight to building your first grimoire from scratch after Arcana is up.

Detailed installer mode rules live in [summoning contract](docs/summoning_contract.md).

Open a new agent session and run `/arc-help` to see every available command, or run `/grm-create` to start your first grimoire.

-> [installation](docs/installation.md) - [installation](docs/installation.md#verify-your-install-5-minute-smoke-test)

---

## Layout

```
~/grimoires/
|-- arcana/                       # The engine - install once, reference forever
|   |-- arcana.md                 # Root hub
|   |-- invocations/              # AI-guided workflows
|   |-- formulae/                 # Templates for hubs, chapters, pages, sources
|   |-- rites/                    # Python automation scripts
|   |-- skills/                   # Slash-command source files
|   |-- docs/                     # Framework documentation (page_schema.md is canonical)
|   |-- resources/                # Branding assets
|
|-- cooking-grimoire/             # A personal grimoire
|   |-- cooking-grimoire.md       # Root hub
|   |-- grimoire.json             # skill_prefix: cook -> /cook-* skills
|   |-- log.md                    # Activity log
|   |-- sources/                  # Articles, transcripts, recipe screenshots
|   |-- inbox/                    # Drop zone for content awaiting classification
|   |-- chapters/                 # recipes/, techniques/, equipment/, ...
|   |   |-- recipes/recipes.md    # Chapter hub (folder-name convention)
|   |   |-- recipes/sourdough.md  # Leaf
|   |   |-- techniques/
|   |       |-- techniques.md     # Chapter hub
|   |       |-- lamination/       # Sub-chapter (nests as deep as needed)
|   |           |-- lamination.md # Sub-chapter hub (same convention)
|   |           |-- book_folds.md # Leaf
|   |           |-- windowpane_test.md
|   |-- skills/                   # Grimoire skills
|
|-- hr-grimoire/                  # A workplace grimoire
|   |-- hr-grimoire.md            # Root hub
|   |-- grimoire.json             # skill_prefix: hr -> /hr-* skills
|   |-- log.md
|   |-- sources/
|   |-- inbox/
|   |-- chapters/                 # onboarding/, policies/, benefits/, ...
|   |-- skills/
|
|-- library.json                  # Local registry of installed grimoires and their paths
```

Create as many grimoires as you need. Arcana provides the framework; each grimoire supplies its own knowledge, skills, and source artifacts.

---

## Documentation

| | |
|---|---|
| [Installation](docs/installation.md) | One-command setup, manual setup, 5-minute smoke test, troubleshooting |
| [Agent Targets](docs/agent_targets.md) | Supported agent target registry |
| [Agent Configuration](docs/agent_configuration.md) | Claude Code, Codex, Copilot, Cursor |
| [Skills](docs/skills.md) | Every `/arc-*` command with descriptions |
| [Skill Schema](docs/skill_schema.md) | Command-family naming rules |
| [Operating Model](docs/operating_model.md) | Storage layers and routing |
| [Page Schema](docs/page_schema.md) | Frontmatter spec for every page |
| [Obsidian](docs/obsidian.md) | Open as a vault; graph-view color groups |
| [Reference](docs/reference.md) | Terminology, schemas, path conventions |
| [Script Vs Ai](docs/script_vs_ai.md) | When to use rites vs invocations |
| [Governance](docs/governance.md) | Maintaining and versioning Arcana |
| [Arcana](arcana.md) | Navigate everything |
