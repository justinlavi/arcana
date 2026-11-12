---
type: hub
title: "Grimoire Invocations"
aliases: ["grimoire-invocations", "grimoire-ops"]
tags: [arcana/invocations, type/hub, scope/grimoire, hub/chapter]
---

# Grimoire Invocations

Grimoire operations: the nine `/grm-*` verbs. Arcana maintenance routes through [[invocations/arc/arc|arc]].

## Available

| Invocation | Skill | What it does |
|---|---|---|
| [[invocations/grm/setup|setup]] | `/grm-setup` | Join a grimoire by link, turn a folder into a grimoire, or route to create |
| [[invocations/grm/create_grimoire|create grimoire]] | `/grm-create` | Start a grimoire from scratch |
| [[invocations/grm/add|add]] | `/grm-add` | Put knowledge in: author a topic or chat answer, or file a document, folder, or the inbox as cited sources |
| [[invocations/grm/save|save]] | `/grm-save` | Share what you changed: validate, commit, pull, push |
| [[invocations/grm/update|update]] | `/grm-update` | Bring everything current; `skills`, `library`, `agentfile` reconcile one surface |
| [[invocations/grm/check|check]] | `/grm-check` | Evaluate the grimoire: full health pass, `quick` or a validator, `naming`, `boundaries`, `fix` |
| [[invocations/grm/move|move]] | `/grm-move` | Rename or move a page or chapter; fixes every link and hub |
| [[invocations/grm/remove|remove]] | `/grm-remove` | Delete a page or chapter; flags inbound links that would break |
| [[invocations/grm/help|help]] | `/grm-help` | Show the grimoire command catalog and the active grimoire's own skills |

Validator detail behind `check`: [[invocations/grm/validators/validators|validators]] and [[invocations/grm/validate_structure|validate structure]].

## Typical Flow

1. Setup: `/grm-setup` to join your team's grimoire or start one.
2. Add: `/grm-add` whenever there is something worth keeping, authored or filed.
3. Save: `/grm-save` to share it; `/grm-update` to pick up everyone else's.
4. Check: `/grm-check` periodically, and `/grm-check quick` before saving.
5. Reshape: `/grm-move` and `/grm-remove` when the structure needs to change.

## Related

- Canonical skill catalog -> [[docs/skills|skills]]
- Meta operations -> [[invocations/meta/meta|meta]]
- Arcana maintenance -> [[invocations/arc/arc|arc]]
- Operating model -> [[docs/operating_model|operating model]]
