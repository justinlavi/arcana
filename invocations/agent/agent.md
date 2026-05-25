---
type: hub
title: "Agent Invocations"
aliases: ["agent-invocations", "agent-ops"]
tags: [arcana/invocations, type/hub, scope/agent, hub/chapter]
---

# Agent Invocations

Agent operations that update local agent configuration or agent skill directories.

## Available

| Invocation | Skill | What it does |
|---|---|---|
| [[invocations/agent/register_skills|register skills]] | `/arc-agent-register-skills` | Register Arcana-shipped skills and installed grimoire skills into supported agent skill directories |
| [[invocations/agent/update_agent_block|update agent block]] | `/arc-agent-update` | Refresh the canonical Grimoire instruction block in agent instruction files |

## Related

- Help -> [[invocations/help/help|help]]
- Library operations -> [[invocations/library/library|library]]
- Grimoire active-scope registration -> [[invocations/grimoire/register_skills|register skills]]
- Agent configuration -> [[docs/agent_configuration|agent configuration]]
