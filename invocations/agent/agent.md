---
type: hub
title: "Agent Invocations"
aliases: ["agent-invocations", "agent-ops"]
tags: [arcana/invocations, type/hub, scope/agent, hub/chapter]
---

# Agent Invocations

Agent operations - invocations that update local agent configuration or agent skill directories.

## Available

| Invocation | Skill | What it does |
|---|---|---|
| [register_skills.md](register_skills.md) | `/arc-agent-register-skills` | Register Arcana-shipped skills and every installed grimoire's own skills into supported agent skill directories |
| [update_agent_block.md](update_agent_block.md) | `/arc-agent-update` | Refresh the canonical Grimoire instruction block in agent instruction files |

## Related

- Help: [`../help/help.md`](../help/help.md)
- Library operations: [`../library/library.md`](../library/library.md)
- Grimoire active-scope registration: [`../grimoire/register_skills.md`](../grimoire/register_skills.md)
- Agent configuration: [`../../docs/agent_configuration.md`](../../docs/agent_configuration.md)
