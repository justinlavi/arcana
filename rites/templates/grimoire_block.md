## Grimoire Knowledge Base

**Library**: `~/grimoires/library.json` — read this file to resolve named grimoire keys and their paths.

**Arcana key**: `GRIMOIRE_ARCANA` — resolved from library or defaults to `~/grimoires/arcana/`

**Skills**: Arcana operations are available as `/grm-*` skills (e.g., `/grm-meta-help`, `/grm-domain-improve`). Domain grimoire skills use the namespace declared in each grimoire's `grimoire.json`.

**Routing**:
1. Determine the active grimoire from working directory or project context; look up its `local_path` in the library.
2. Read `{active grimoire}/INDEX.md` first; route deterministically: `INDEX.md` > chapter `INDEX.md` > 1-2 page docs.
3. For Grimoire meta-knowledge: read `GRIMOIRE_ARCANA/INDEX.md`.
4. Do not modify Grimoire files unless a `/grm-*` skill, a domain skill, or explicit instruction asks for it.
