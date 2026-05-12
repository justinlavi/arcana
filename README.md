![grimoire](./resources/grimoire_icon_512.png)

# Grimoire Arcana: Build AI-Navigable Knowledge Bases

---

## What is Arcana?

**Arcana is the meta-knowledge backbone** for all grimoires across your company.

- **What it contains**: Invocations, formulae, rites, and documentation about Grimoire itself.
- **What it doesn't contain**: Actual business knowledge — that lives in domain grimoires.
- **Who uses it**: Every domain references this single Arcana installation. No copying, no drift.

**Think of it as**: the canonical reference that all grimoires draw structure from.

---

## Why It Matters

Grimoire provides **deterministic routing** to authoritative knowledge — typically 3 file reads, under 3 seconds, no hallucination. Without it, AI searches scattered files and guesses. With it, AI reads documented truth.

```
Your question:    "What's the PTO policy?"
                       ↓
Routing:          grimoire_hr/INDEX.md → chapters/policies/INDEX.md → pto_policy.md
                       ↓
Answer:           Authoritative, sourced from your company's documented truth.
```

Every chapter you add is one less thing AI will guess about. The more comprehensive your grimoire, the more accurate AI becomes.

---

## Get Started

- **Install**: see [docs/installation.md](docs/installation.md) for the one-command summoning rite (and manual setup).
- **Verify your install**: see [docs/quickstart.md](docs/quickstart.md) for the 5-minute smoke test.
- **Create your first grimoire**: invoke `/grm-domain-create-grimoire` after install — the skill walks you through it conversationally. See [invocations/grimoire/create_grimoire.md](invocations/grimoire/create_grimoire.md) for the full procedure.

---

## Architecture

```
~/grimoire/
├── arcana/                      # The engine (standalone)
│   ├── invocations/             # AI procedures (markdown guides)
│   ├── formulae/                # Templates / blueprints
│   ├── rites/                   # Automation scripts (Python)
│   ├── skills/                  # Slash-command pointers (registered to agents)
│   ├── docs/                    # Reference documentation
│   └── grimoire.json            # Manifest (namespace: grm)
│
├── olympus-grimoire/            # Domain grimoire (pure content)
│   ├── INDEX.md
│   ├── grimoire.json            # Manifest (namespace: oly)
│   ├── skills/                  # Domain-specific skills
│   └── chapters/
│
└── catalog.json                 # Local catalog (maps grimoire key → local_path)
```

Arcana lives once at `~/grimoire/arcana/`. Domain grimoires are pure content — no engine code, no submodules. Every domain references the single Arcana installation via the `GRIMOIRE_ARCANA` key. Each grimoire's identity (name + namespace) lives in its own [`grimoire.json` manifest](docs/reference.md#grimoire-manifest); the catalog is a pure registry.

---

## Where to Read Next

| If you want to… | Start here |
|---|---|
| Install Grimoire | [docs/installation.md](docs/installation.md) |
| Verify your install | [docs/quickstart.md](docs/quickstart.md) |
| Configure an agent (Claude / Codex / Copilot) | [docs/agent_configuration.md](docs/agent_configuration.md) |
| Browse the full skill catalog | [docs/skills.md](docs/skills.md) |
| Understand the routing model | [docs/operating_model.md](docs/operating_model.md) |
| Look up terminology / catalog / manifest schemas | [docs/reference.md](docs/reference.md) |
| Understand scripts vs AI | [docs/script_vs_ai.md](docs/script_vs_ai.md) |
| Maintain Arcana itself | [docs/governance.md](docs/governance.md), [docs/release.md](docs/release.md) |
| Navigate everything | [INDEX.md](INDEX.md) |
