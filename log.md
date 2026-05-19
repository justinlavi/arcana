# Activity Log — Arcana

Append-only record of every operation that mutates this grimoire. Format documented in [formulae/log_entry.formula.md](formulae/log_entry.formula.md).

Scan recent activity:

```bash
grep '^## \[' log.md | tail -20
```

---

## [2026-05-18 23:20] improve | Agent block refresh skill
- skill: /grm-arcana-improve
- pages: skills/meta-update-agent-block/SKILL.md, invocations/meta/update_agent_block.md, rites/templates/grimoire_block.md, docs/agent_configuration.md, docs/skills.md
- note: Added /grm-meta-update-agent-block for AI-guided updates of Grimoire blocks in user agent instruction files while preserving non-Grimoire content.

## [2026-05-18 23:13] improve | Wikilink display-label warnings
- skill: /grm-arcana-improve
- pages: rites/validate_links.py, docs/obsidian.md, invocations/arcana/validators/validate_links.md, tests/fixtures/warn_labels/
- note: Added non-blocking warnings for wikilink labels that repeat parent-folder context instead of naming only the target filename.

## [2026-05-18 23:05] improve | Full-path-only wikilinks
- skill: /grm-arcana-improve
- pages: rites/_lib.py, rites/validate_links.py, rites/validate_orphans.py, docs/, formulae/, invocations/, tests/
- note: Removed alias and filename-stem wikilink resolution. Wikilinks now resolve only as repository-root relative paths; aliases remain metadata only.

## [2026-05-18 22:52] improve | Path-form wikilink validation
- skill: /grm-arcana-improve
- pages: rites/_lib.py, rites/validate_links.py, rites/validate_orphans.py, docs/obsidian.md, CHANGELOG.md
- note: Added validator support for Obsidian path-form wikilinks so editor-safe links using the path-plus-label form resolve mechanically.

## [2026-05-13 12:00] create | Arcana 1.0.0
- skill: manual
- pages: arcana.md, log.md, sources/.gitkeep
- note: Inaugural Arcana release. Storage layers: sources/ (immutable source artifacts), inbox/ (transient drop zone), chapters-equivalent content under docs/invocations/formulae, schema. Folder-named hub convention. Required page frontmatter. Ingest/lint/file-answer operations.
