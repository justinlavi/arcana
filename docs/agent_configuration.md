---
type: reference
title: "Agent Configuration"
aliases: ["agent-config", "agent-setup"]
tags: [type/reference, arcana/docs]
authority: grimoire
last_verified: 2026-05-12
---

# Arcana Agent Configuration

Per-agent setup for using Arcana and grimoire skills (Claude Code, Codex/ChatGPT, Copilot, etc.). The summoning rite ([installation.md](installation.md)) configures the supported agents automatically — this doc is for manual configuration, additional agents, and per-platform nuances.

For installation, see [installation.md](installation.md). For library and manifest schemas, see [reference.md](reference.md). For the current Arcana skill catalog, see [skills.md](skills.md). For command naming rules, see [skill_schema.md](skill_schema.md).

---

## Agent Instruction Files

Each agent reads a "system instructions" file. Grimoire needs a small block in that file so the agent knows how to route through the library.

**Canonical block**: [`rites/templates/grimoire_block.md`](../rites/templates/grimoire_block.md) — single source of truth for the instructions text. Copy this into the agent's instruction file. Do not duplicate the block in any other file — edit the canonical and the change propagates wherever it's referenced.

| Agent | Instruction file | Auto-configured by summoning rite? |
|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` | Yes |
| Codex / ChatGPT (CLI) | `~/.codex/AGENTS.md` | Yes |
| ChatGPT (hosted) | "Custom Instructions" field | No (paste manually) |
| GitHub Copilot | `.github/copilot_instructions.md` | No (add manually; trim to the four key sections if length-limited) |

The block never changes when grimoires are added or removed — those changes happen in the library, not the agent file. When Arcana itself changes the block, use `/arc-agent-update` to refresh existing `CLAUDE.md`, `AGENTS.md`, or other agent instruction files while preserving unrelated user instructions.

---

## Skill Registration

Skills are `SKILL.md` files registered into agent-specific skill directories:

| Agent | Skill directory | Files copied per skill |
|---|---|---|
| Claude Code | `~/.claude/skills/<name>/` | All files under `skills/<family>/<slug>/` for Arcana, or `skills/<slug>/` for a grimoire |
| Codex / ChatGPT | `~/.codex/skills/<name>/` | `SKILL.md` only (pointer-only) |

Both targets are written by the same rite:

```bash
python3 ~/grimoires/arcana/rites/register_skills.py            # all targets
python3 ~/grimoires/arcana/rites/register_skills.py --agent claude
python3 ~/grimoires/arcana/rites/register_skills.py --agent codex
python3 ~/grimoires/arcana/rites/register_skills.py --grimoire . # Arcana + active grimoire
```

Invoke `/arc-agent-register-skills` for a global refresh of Arcana plus every installed grimoire. Invoke `/grm-register-skills` from inside one grimoire to refresh Arcana plus that active grimoire only. The summoning rite runs the global registration for you on install.

For the normal "bring this machine up to date" workflow, run `/grm-update-arcana` from inside a grimoire. It pulls Arcana, validates it, refreshes the local library, updates agent integration when needed, re-registers skills, and checks the active grimoire against the current structure rules.

For Codex/ChatGPT, the registered directory must contain only `SKILL.md` — never bundle scripts, references, or copies of invocation content. The skill remains a thin pointer to Arcana invocations or rites.

---

## How Skills Work

A skill is a **thin pointer**. It delegates to one of:

- **Invocation-backed**: skill loads a markdown guide via `` `!cat {{ARCANA_PATH}}/invocations/...` ``. The AI follows the instructions.
- **Rite-backed**: skill tells the AI to run a Python script via `python3 {{ARCANA_PATH}}/rites/...`. The script does the work.

Skills must never embed implementation logic directly. This separation keeps them portable across agent platforms.

For when to choose rite-backed vs invocation-backed (and the anti-patterns to avoid), see [`script_vs_ai.md` — Applying this to skills](script_vs_ai.md#applying-this-to-skills).

---

## SKILL.md Frontmatter Reference

Every `SKILL.md` declares its skill in YAML frontmatter. Required fields are minimal; optional fields tune how the agent presents and auto-invokes the skill.

| Field | Required | Used by | Notes |
|---|---|---|---|
| `name` | Yes | Both | Final registered command name. Source files use `{{SKILL_PREFIX}}-<slug>`; the registration rite substitutes `{{SKILL_PREFIX}}` with the grimoire's skill prefix at install time. |
| `description` | Yes | Both | One-line summary. Codex/ChatGPT renders it next to the command in the picker UI. Claude Code loads it into the model's reasoning context (see "Auto-invocation" below). |
| `argument-hint` | No | Both | Bracketed hint shown during `/` autocomplete (e.g. `[topic]`, `[directory-name]`). |
| `arguments` | No | Both | Comma-separated argument names available as `$name` in the SKILL.md body. |
| `allowed-tools` | No | Both | Space-separated list of tools the skill needs (e.g. `Bash Read Write`). |
| `user-invocable` | No | Both | `true` = appears in the `/` picker. Default depends on agent. |
| `when_to_use` | No | **Claude Code** | Helps Claude auto-invoke the skill without the user typing `/`. Phrase as natural-language scenarios ("User asks X", "User mentions Y"). Codex/ChatGPT ignores this field. |
| `disable-model-invocation` | No | **Claude Code** | `true` prevents Claude from ever auto-invoking the skill — only user-typed slash commands trigger it. Use for destructive ops (deletions, irreversible changes). Codex/ChatGPT ignores this field. |

Cross-agent safety: any field Codex/ChatGPT doesn't recognize is silently ignored. The same source `SKILL.md` works for both targets — no per-agent compilation needed.

### Auto-invocation policy in this Arcana

Adding `when_to_use` makes a skill discoverable by intent in Claude Code (the user describes a problem; Claude routes to the right skill). The current Arcana settings:

- **All user-facing operations** (`/grm-*`, `/arc-library-*`, `/arc-agent-register-skills`, `/arc-help`, `/arc-validate-all`) declare `when_to_use` so Claude can auto-suggest them.
- **One destructive skill** (`/arc-workspace-clean`) declares `disable-model-invocation: true` because it deletes artifacts; users must invoke it explicitly.
- **Individual validators** (`/arc-validate-format`, `-links`, etc.) and the heavy maintainer orchestrator (`/arc-improve`) deliberately omit `when_to_use` — the orchestrator (`/arc-validate-all` or `/arc-improve`) is the right entry point for normal flows; auto-invoking individual validators would over-activate.

When adding a new skill, decide: does the user describe a *problem* that maps to this skill? If yes, give it a `when_to_use`. If the skill is destructive or maintainer-only, set `disable-model-invocation: true`.

Arcana declares command families in `arcana.json`:
- `arc-*` for Arcana platform operations, including maintainer validation, library, agent, workspace, and help commands.
- `grm-*` for universal grimoire operations that act on the active grimoire.

Normal grimoires declare one skill prefix in their own `grimoire.json`, such as `jpn-*` or `oly-*`.

Source `SKILL.md` files use `name: {{SKILL_PREFIX}}-<registered-slug>` in their frontmatter. The registration rite substitutes `{{SKILL_PREFIX}}` with the declaring command family's prefix for Arcana, or with the grimoire's `skill_prefix` for grimoire-owned skills. See [skill_schema.md](skill_schema.md) and [reference.md](reference.md#grimoire-manifest) for manifest details.

---

## Grimoire Skills

Grimoires contribute skills via their own `skills/` directory. Place each skill at `<grimoire>/skills/<area>-<verb>-<object>/SKILL.md`. The folder name is the subcommand after the skill prefix. Use `{{ARCANA_PATH}}` and `{{GRIMOIRE_PATH}}` as path placeholders — the registration rite resolves both to absolute paths at install time.

To register new or updated skills in the active grimoire, run `/grm-register-skills`. To refresh all installed grimoires, run `/arc-agent-register-skills`.

---

## Troubleshooting

**Agent doesn't see new skills**
- Run `/grm-register-skills` from the active grimoire, or `/arc-agent-register-skills` for a global refresh. Then open a new agent session (Claude Code / Codex caches skill listings).

**Arcana may be stale**
- Run `/grm-update-arcana` from inside a registered grimoire.

**Agent has stale Grimoire routing instructions**
- Run `/arc-agent-update`. It compares existing agent instruction files against the canonical block and updates only the Grimoire section.

**Agent can't find a grimoire**
- Verify the grimoire is in `~/grimoires/library.json` and the `local_path` resolves. Run `/arc-library-sync` to detect and reconcile drift.

**Skill names look wrong (`{{SKILL_PREFIX}}-...`)**
- The grimoire is missing a `grimoire.json` or its `skill_prefix` field. See [reference.md](reference.md#grimoire-manifest).
