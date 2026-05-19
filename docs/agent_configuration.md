---
type: reference
title: "Agent Configuration"
aliases: ["agent-config", "agent-setup"]
tags: [type/reference, arcana/docs]
authority: grimoire
last_verified: 2026-05-12
---

# Grimoire Agent Configuration

Per-agent setup for using Grimoire skills (Claude Code, Codex/ChatGPT, Copilot, etc.). The summoning rite ([installation.md](installation.md)) configures the supported agents automatically — this doc is for manual configuration, additional agents, and per-platform nuances.

For installation, see [installation.md](installation.md). For library and manifest schemas, see [reference.md](reference.md). For the current Arcana skill catalog, see [skills.md](skills.md).

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

The block never changes when grimoires are added or removed — those changes happen in the library, not the agent file. When Arcana itself changes the block, use `/grm-meta-update-agent-block` to refresh existing `CLAUDE.md`, `AGENTS.md`, or other agent instruction files while preserving unrelated user instructions.

---

## Skill Registration

Skills are `SKILL.md` files registered into agent-specific skill directories:

| Agent | Skill directory | Files copied per skill |
|---|---|---|
| Claude Code | `~/.claude/skills/<name>/` | All files under `skills/<slug>/` |
| Codex / ChatGPT | `~/.codex/skills/<name>/` | `SKILL.md` only (pointer-only) |

Both targets are written by the same rite:

```bash
python3 ~/grimoires/arcana/rites/register_skills.py            # all targets
python3 ~/grimoires/arcana/rites/register_skills.py --agent claude
python3 ~/grimoires/arcana/rites/register_skills.py --agent codex
```

Or invoke `/grm-skills-register`. The summoning rite runs this for you on install.

For Codex/ChatGPT, the registered directory must contain only `SKILL.md` — never bundle scripts, references, or copies of invocation content. The skill remains a thin pointer to Arcana invocations or rites.

---

## How Skills Work

A skill is a **thin pointer**. It delegates to one of:

- **Invocation-backed**: skill loads a markdown guide via `` `!cat {{ARCANA_PATH}}/invocations/...` ``. The AI follows the instructions.
- **Rite-backed**: skill tells the AI to run a Python script via `python3 {{ARCANA_PATH}}/rites/...`. The script does the work.

Skills must never embed implementation logic directly. This separation keeps them portable across agent platforms.

For when to choose rite-backed vs invocation-backed (and the anti-patterns to avoid), see [`script_vs_ai.md` § Applying this to skills](script_vs_ai.md#applying-this-to-skills).

---

## SKILL.md Frontmatter Reference

Every `SKILL.md` declares its skill in YAML frontmatter. Required fields are minimal; optional fields tune how the agent presents and auto-invokes the skill.

| Field | Required | Used by | Notes |
|---|---|---|---|
| `name` | Yes | Both | Final registered command name. Source files use `{{NAMESPACE}}-<slug>`; the registration rite substitutes `{{NAMESPACE}}` with the grimoire's namespace at install time. |
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

- **All user-facing operations** (`/grm-domain-*`, `/grm-library-*`, `/grm-skills-register`, `/grm-meta-help`, `/grm-arcana-validate-all`) declare `when_to_use` so Claude can auto-suggest them.
- **One destructive skill** (`/grm-arcana-clean`) declares `disable-model-invocation: true` because it deletes artifacts; users must invoke it explicitly.
- **Individual validators** (`/grm-arcana-validate-format`, `-links`, etc.) and the heavy maintainer orchestrator (`/grm-arcana-improve`) deliberately omit `when_to_use` — the orchestrator (`/grm-arcana-validate-all` or `/grm-arcana-improve`) is the right entry point for normal flows; auto-invoking individual validators would over-activate.

When adding a new skill, decide: does the user describe a *problem* that maps to this skill? If yes, give it a `when_to_use`. If the skill is destructive or maintainer-only, set `disable-model-invocation: true`.

Skills are namespaced by their grimoire's manifest:
- Arcana skills: `grm-*` (declared in `arcana/grimoire.json`).
- Domain grimoire skills: `{namespace}-*` (declared in each grimoire's `grimoire.json`).

Source `SKILL.md` files use `name: {{NAMESPACE}}-<slug>` in their frontmatter; the registration rite substitutes `{{NAMESPACE}}` with the grimoire's declared namespace at install time. See [reference.md](reference.md#grimoire-manifest) for manifest details.

---

## Domain Grimoire Skills

Domain grimoires contribute skills via their own `skills/` directory. Place each skill at `<grimoire>/skills/<area>-<verb>-<object>/SKILL.md`. The folder name is the subcommand after the namespace root. Use `{{ARCANA_PATH}}` and `{{GRIMOIRE_PATH}}` as path placeholders — the registration rite resolves both to absolute paths at install time.

To register new or updated skills, run `/grm-skills-register`.

---

## Troubleshooting

**Agent doesn't see new skills**
- Run `/grm-skills-register` and open a new agent session (Claude Code / Codex caches skill listings).

**Agent has stale Grimoire routing instructions**
- Run `/grm-meta-update-agent-block`. It compares existing agent instruction files against the canonical block and updates only the Grimoire section.

**Agent can't find a grimoire**
- Verify the grimoire is in `~/grimoires/library.json` and the `local_path` resolves. Run `/grm-library-sync` to detect and reconcile drift.

**Skill names look wrong (`{{NAMESPACE}}-...`)**
- The grimoire is missing a `grimoire.json` or its `namespace` field. See [reference.md](reference.md#grimoire-manifest).
