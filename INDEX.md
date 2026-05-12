# Arcana

Meta-knowledge about Grimoire itself — invocations, formulae, rites, governance. For actual domain knowledge, route to your grimoire's `INDEX.md` instead.

---

## Documentation
- **[README.md](README.md)** — Overview and architecture
- **[docs/installation.md](docs/installation.md)** — Summoning rite + manual install
- **[docs/quickstart.md](docs/quickstart.md)** — 5-minute smoke test after install
- **[docs/agent_configuration.md](docs/agent_configuration.md)** — Per-agent setup (Claude / Codex / Copilot)
- **[docs/skills.md](docs/skills.md)** — Canonical Arcana skill catalog (auto-generated)
- **[docs/reference.md](docs/reference.md)** — Terminology, library/manifest schemas, path keys, formula placeholders
- **[docs/operating_model.md](docs/operating_model.md)** — Routing model and authority models
- **[docs/script_vs_ai.md](docs/script_vs_ai.md)** — Architectural principle: when to use scripts vs AI
- **[docs/governance.md](docs/governance.md)** — Maintenance policies and versioning
- **[docs/release.md](docs/release.md)** — Release workflow for Summoning Rite binaries
- **[CHANGELOG.md](CHANGELOG.md)** — Version history

### Invocations (What Grimoire Can Do)

**Grimoire Invocations** (Domain Operations):
- **[invocations/grimoire/create_grimoire.md](invocations/grimoire/create_grimoire.md)** - Create new grimoire (AI-guided)
- **[invocations/grimoire/create_chapter.md](invocations/grimoire/create_chapter.md)** - Create new knowledge chapter
- **[invocations/grimoire/improve_grimoire.md](invocations/grimoire/improve_grimoire.md)** - Improve your domain grimoire (/grm-domain-improve)
- **[invocations/grimoire/analyze_semantics.md](invocations/grimoire/analyze_semantics.md)** - Semantic clarity and naming analysis ✨

**Arcana Invocations** (Maintainer Only):
- **[invocations/arcana/improve_arcana.md](invocations/arcana/improve_arcana.md)** - Improve Arcana (/grm-arcana-improve)
- **[invocations/arcana/validate_boundaries.md](invocations/arcana/validate_boundaries.md)** - Magical boundary enforcement ✨

**Meta Invocations** (System Documentation):
- **[invocations/meta/help.md](invocations/meta/help.md)** - Show invocation catalog and usage guide (/grm-meta-help) 🔮
- **[invocations/meta/base_invocation.md](invocations/meta/base_invocation.md)** - Generic invocation execution template

### Formulae (Blueprints)
- **[formulae/grimoire/](formulae/grimoire/)** - Grimoire template (copy for new domains)
- **[formulae/chapter_index.formula.md](formulae/chapter_index.formula.md)** - Chapter router formula
- **[formulae/page.formula.md](formulae/page.formula.md)** - Knowledge page template
- **[formulae/invocation.formula.md](formulae/invocation.formula.md)** - Custom invocation formula

### Skills (User-Facing Operations)
- **[docs/skills.md](docs/skills.md)** — Canonical Arcana skill catalog (auto-generated from `skills/*/SKILL.md`)
- **[skills/](skills/)** — Skill source directory; registered into agent skill roots via `rites/register_skills.py`

### Summoning & Library
- **[rites/summon.sh](rites/summon.sh)** - Grimoire summoning rite (one-command setup)
- **[rites/register_skills.py](rites/register_skills.py)** - Skill registration rite
- **[rites/sync_library.py](rites/sync_library.py)** - Library sync rite (reconcile library with disk)
- **[rites/sync_docs.py](rites/sync_docs.py)** - Docs sync rite (regenerate `docs/skills.md` from sources)
- **[rites/adopt_grimoire.py](rites/adopt_grimoire.py)** - Adopt an unmanaged directory by writing its `grimoire.json`
- **[library.json](library.json)** - Top-level grimoire library shipped with Arcana (lists discoverable domain grimoires for the summoning rite)

### Tools
- **[resources/](resources/)** - Branding assets (icon, etc.)
