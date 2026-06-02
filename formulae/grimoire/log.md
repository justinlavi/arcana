# Activity Log - {{GRIMOIRE_NAME}}

Append-only history of changes to this grimoire's **content** - pages and sources added, removed, or changed. It records *what* changed in the wiki, not version-control mechanics (branches, merges, commits). Format documented in `ARCANA_HOME/formulae/log_entry.formula.md`.

Scan recent activity:

```bash
grep '^## \[' log.md | tail -20
```

---

## [{{CREATION_DATE}} 00:00] create | {{GRIMOIRE_NAME}}
- skill: /grm-create
- pages: {{GRIMOIRE_DIRECTORY}}.md, log.md, sources/.gitkeep
- note: Initial grimoire scaffold.
