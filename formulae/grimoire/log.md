# Activity Log — {{GRIMOIRE_NAME}}

Append-only record of every operation that mutates this grimoire. Format documented in [GRIMOIRE_ARCANA/formulae/log_entry.formula.md](../GRIMOIRE_ARCANA/formulae/log_entry.formula.md).

Scan recent activity:

```bash
grep '^## \[' log.md | tail -20
```

---

## [{{CREATION_DATE}} 00:00] create | {{GRIMOIRE_NAME}}
- skill: /grm-domain-create-grimoire
- pages: {{GRIMOIRE_DIRECTORY}}.md, log.md, sources/.gitkeep
- note: Initial grimoire scaffold.
