# Activity Log — Arcana

Append-only record of every operation that mutates this grimoire. Format documented in [formulae/log_entry.formula.md](formulae/log_entry.formula.md).

Scan recent activity:

```bash
grep '^## \[' log.md | tail -20
```

---

## [2026-05-13 12:00] create | Arcana 1.0.0
- skill: manual
- pages: arcana.md, log.md, sources/.gitkeep
- note: Inaugural Arcana release. Storage layers: sources/ (immutable source artifacts), inbox/ (transient drop zone), chapters-equivalent content under docs/invocations/formulae, schema. Folder-named hub convention. Required page frontmatter. Ingest/lint/file-answer operations.
