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
| [[invocations/agent/sync_skills|sync skills]] | `/arc-sync-skills` | Sync Arcana-shipped skills and installed grimoire skills into supported agent skill directories |
| [[invocations/agent/sync_agentfile|sync agentfile]] | `/arc-sync-agentfile` | Refresh the canonical Grimoire instruction block in agent instruction files |

## Related

- Help -> [[invocations/help/help|help]]
- Library operations -> [[invocations/library/library|library]]
- Grimoire active-scope skill sync -> [[invocations/grimoire/sync_skills|sync skills]]
- Agent configuration -> [[docs/agent_configuration|agent configuration]]
