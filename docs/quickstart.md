# Grimoire Quickstart

A 5-minute smoke test to verify your install and prove the routing model works end-to-end.

If you haven't installed Arcana yet, start with [installation.md](installation.md). For per-agent configuration nuances, see [agent_configuration.md](agent_configuration.md).

---

## 1. Verify the install

Confirm Arcana and at least one grimoire are present:

```bash
ls ~/grimoire/                  # arcana/ + at least one *-grimoire/
cat ~/grimoire/catalog.json     # lists each grimoire and its local_path
```

Confirm Grimoire skills registered to your agent:

```bash
ls ~/.claude/skills/ | grep ^grm-     # Claude Code
ls ~/.codex/skills/  | grep ^grm-     # Codex / ChatGPT CLI
```

If any of these are missing, see the troubleshooting section in [installation.md](installation.md#troubleshooting) before continuing.

---

## 2. Smoke-test routing in your agent

Open a new Claude Code (or Codex) session and run:

```
/grm-meta-help
```

The skill should enumerate every installed `grm-*` and domain-namespaced skill (e.g. `oly-*`). If you see a populated list, the agent has loaded the catalog and skill directory correctly.

---

## 3. Smoke-test a domain grimoire

Pick any grimoire from your catalog and ask the agent (paraphrase as needed):

> "Read the {grimoire-name} INDEX.md and tell me what chapters it routes to."

The agent should:
1. Resolve the grimoire's `local_path` via `~/grimoire/catalog.json`.
2. Read `{grimoire}/INDEX.md`.
3. Report the chapter list — exactly what's in the file, no invention.

If it makes things up or can't find the file, your agent's instruction block is missing the routing rules. Re-check [agent_configuration.md](agent_configuration.md#agent-instruction-files).

---

## 4. (Optional) Walk a full route

For a deeper test, ask:

> "What's the canonical document for {topic} in {grimoire-name}?"

The agent should follow the `INDEX.md → chapter INDEX.md → leaf doc` model and cite the exact file path it read. Three reads, one answer.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `/grm-meta-help` not recognized | Skills not registered, or agent session opened before install | Run `/grm-skills-register` and start a new session |
| Agent guesses instead of reading files | Missing instruction block | See [agent_configuration.md](agent_configuration.md#agent-instruction-files) |
| Catalog entry exists but agent can't find grimoire | `local_path` doesn't resolve | Run `/grm-catalog-sync` to detect drift |
| Skill names appear as `{{NAMESPACE}}-...` | Grimoire missing manifest | Add `grimoire.json` per [reference.md](reference.md#grimoire-manifest) |

---

## Next steps

- **Browse the skill catalog**: [skills.md](skills.md)
- **Create your first chapter**: invoke `/grm-domain-create-chapter [topic]` (or read [invocations/grimoire/create_chapter.md](../invocations/grimoire/create_chapter.md))
- **Learn the routing model in depth**: [operating_model.md](operating_model.md)
- **Look up terminology / catalog / manifest schemas**: [reference.md](reference.md)
