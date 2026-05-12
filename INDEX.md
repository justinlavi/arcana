# Arcana

Meta-knowledge about Grimoire itself — invocations, formulae, rites, governance. For actual domain knowledge, route to your grimoire's `INDEX.md` instead.

---

## Documentation
- **[README.md](README.md)** - Overview and architecture
- **[docs/quickstart.md](docs/quickstart.md)** - 10-minute setup guide
- **[docs/operating_model.md](docs/operating_model.md)** - Core principles and routing model
- **[docs/agent_configuration.md](docs/agent_configuration.md)** - AI agent setup (Claude, GPT, Cursor) 🤖
- **[docs/governance.md](docs/governance.md)** - Maintenance policies and versioning
- **[docs/release.md](docs/release.md)** - Release workflow for Summoning Rite binaries
- **[CHANGELOG.md](CHANGELOG.md)** - Version history
- **[docs/reference.md](docs/reference.md)** - Reference (terminology, conventions, path keys)
- **[docs/script_vs_ai.md](docs/script_vs_ai.md)** - Architectural principle: When to use scripts vs AI ⭐

### Invocations (What Grimoire Can Do)

**Grimoire Invocations** (Domain Operations):
- **[invocations/grimoire/create_grimoire.md](invocations/grimoire/create_grimoire.md)** - Create new grimoire (AI-guided)
- **[invocations/grimoire/create_chapter.md](invocations/grimoire/create_chapter.md)** - Create new knowledge chapter
- **[invocations/grimoire/improve_grimoire.md](invocations/grimoire/improve_grimoire.md)** - Improve your domain grimoire (/grm-improve)
- **[invocations/grimoire/analyze_semantics.md](invocations/grimoire/analyze_semantics.md)** - Semantic clarity and naming analysis ✨

**Arcana Invocations** (Maintainer Only):
- **[invocations/arcana/improve_arcana.md](invocations/arcana/improve_arcana.md)** - Improve Arcana (/grm-arcana-improve)
- **[invocations/arcana/validate_boundaries.md](invocations/arcana/validate_boundaries.md)** - Magical boundary enforcement ✨

**Meta Invocations** (System Documentation):
- **[invocations/meta/help.md](invocations/meta/help.md)** - Show invocation catalog and usage guide (/grm-help) 🔮
- **[invocations/meta/base_invocation.md](invocations/meta/base_invocation.md)** - Generic invocation execution template

### Formulae (Blueprints)
- **[formulae/grimoire/](formulae/grimoire/)** - Grimoire template (copy for new domains)
- **[formulae/chapter_index.formula.md](formulae/chapter_index.formula.md)** - Chapter router formula
- **[formulae/page.formula.md](formulae/page.formula.md)** - Knowledge page template
- **[formulae/invocation.formula.md](formulae/invocation.formula.md)** - Custom invocation formula

### Skills (User-Facing Operations)
- **[skills/](skills/)** - Skill source directory (registered to `~/.claude/skills/` via `rites/register_skills.py`)
- `/grm-create-grimoire` — Create new domain grimoire
- `/grm-create-chapter` — Create new knowledge chapter
- `/grm-improve` — Comprehensive grimoire improvement
- `/grm-arcana-validate` — Validate structure compliance
- `/grm-analyze-semantics` — Semantic naming analysis
- `/grm-arcana-validate-boundaries` — Magical boundary validation
- `/grm-arcana-improve` — Improve Arcana (maintainer)
- `/grm-help` — Show skill catalog and usage guide
- `/grm-register-skills` — Re-register all skills from Arcana and domain grimoires

### Summoning & Catalog
- **[rites/summon.sh](rites/summon.sh)** - Grimoire summoning rite (one-command setup)
- **[rites/register_skills.py](rites/register_skills.py)** - Skill registration rite
- **[catalog.json](catalog.json)** - Company-wide grimoire catalog

### Tools
- **[resources/](resources/)** - Branding assets (icon, etc.)
