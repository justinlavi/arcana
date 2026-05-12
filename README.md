![grimoire](./resources/grimoire_icon_512.png)

# Grimoire Arcana: Build AI-Navigable Knowledge Bases

---

## What is Arcana?

**Arcana is the meta-knowledge backbone** for all grimoires across your company.

- **What it contains**: Invocations, formulae, rites, and documentation about Grimoire itself
- **What it doesn't contain**: Actual business knowledge (that lives in domain grimoires)
- **Who uses it**: All domains reference this single Arcana installation — no copying, no drift

**Think of it as**: The ancient tome that all grimoires draw power from.

---

## 🎯 Core Purpose

Grimoire provides **deterministic routing** to authoritative knowledge — 3 file reads, <3 seconds, no hallucination. Without it, AI searches scattered files and guesses. With it, AI reads documented truth.

Every chapter you add is one less thing AI will guess about. The more comprehensive your grimoire, the more accurate AI becomes.

---

## 📚 What's Inside

- **`invocations/`** - Universal workflows for creating and improving grimoires
  - `grimoire/` - Domain operations (create, improve, analyze)
  - `arcana/` - Arcana maintenance (maintainer only)
  - `meta/` - System documentation and help

- **`formulae/`** - Blueprint templates for chapters, pages, and invocations

- **`formulae/grimoire/`** - Ready-to-copy template for new grimoires

- **`docs/`** - Reference documentation (terminology, operating model, governance)

- **`catalog.json`** - Company-wide grimoire catalog

- **`rites/`** - Validation and automation scripts

- **`resources/`** - Branding assets

**To explore**: Read [INDEX.md](INDEX.md) which provides routing to all Arcana content.

---

## ✨ Quick Start: Creating Your First Grimoire

### Option 0: Summoning Rite (Fastest)

One command summons Arcana and any grimoires in its catalog:

```bash
curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash
```

This downloads the public summoning rite from GitHub, installs Arcana to `~/grimoire/arcana/`, and then uses the interactive flow to discover or select grimoires.

When run from the public curl command, the summoning rite first tries to download the latest GitHub Release binary for your platform, verifies its checksum, and runs it. If no matching binary is available, it falls back to the Python source bootstrap.

For forks or private mirrors, pass the Arcana repository URL explicitly:

```bash
curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | GRIMOIRE_ARCANA_URL=https://github.com/your-org/arcana.git bash
```

To pin a specific release instead of the latest published release:

```bash
curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | GRIMOIRE_SUMMON_RELEASE_TAG=v1.0.0 bash
```

This clones Arcana and selected grimoires to `~/grimoire/`, sets up the local catalog, registers slash-command skills for Claude Code and Codex/ChatGPT, and configures `CLAUDE.md` and `AGENTS.md` automatically.

### Option 1: AI-Guided (Recommended) ⭐

**Easiest way** - just have a conversation:

1. Tell your AI: `/grm-domain-create-grimoire`
2. Answer questions about your domain and goals
3. AI suggests relevant chapters
4. AI creates everything automatically

**Time**: ~10 minutes (mostly conversation)

### Option 2: Manual (Advanced)

Create a new git repo and copy the grimoire template from Arcana:

```bash
mkdir {your-domain}-grimoire && cd {your-domain}-grimoire
git init
cp ~/grimoire/arcana/formulae/grimoire/INDEX.md .
cp ~/grimoire/arcana/formulae/grimoire/README.md .
mkdir chapters
# Edit INDEX.md and README.md to replace {{PLACEHOLDERS}}
```

**See**: [invocations/grimoire/create_grimoire.md](invocations/grimoire/create_grimoire.md) for full details

---

## 🔮 How Grimoire Works

**Simple routing model**: `INDEX.md` → `chapter INDEX.md` → `page docs`

```
Your Question: "What's the PTO policy?"
    ↓
grimoire_hr/INDEX.md → chapters/policies/INDEX.md → pto_policy.md
    ↓
Answer!
```

**Total**: 3 file reads, <2 seconds, accurate company-specific answer

**Why this matters**: Without Grimoire, AI might search 15+ files, take 45+ seconds, and still hallucinate the answer. With Grimoire, AI finds the authoritative source immediately.

For deep dive: See [docs/operating_model.md](docs/operating_model.md)

---

## 🏗️ Architecture

```
~/grimoire/
├── arcana/                      # The engine (standalone)
│   ├── invocations/             # AI procedures
│   ├── formulae/                # Templates
│   ├── rites/                   # Shell scripts
│   └── docs/                    # Reference docs
│
├── olympus-grimoire/            # Domain grimoire (pure content)
│   ├── INDEX.md
│   └── chapters/
│
├── domain-a-grimoire/           # Another domain grimoire
│   ├── INDEX.md
│   └── chapters/
│
└── catalog.json                 # Local catalog (maps keys → paths)
```

Arcana lives once at `~/grimoire/arcana/`. Domain grimoires are pure content — no engine code, no submodules. All domains reference the single Arcana installation via `GRIMOIRE_ARCANA`.

---

For full navigation, see [INDEX.md](INDEX.md).
