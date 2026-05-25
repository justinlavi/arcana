---
name: {{SKILL_PREFIX}}-skills-register
description: Register Arcana skills and installed grimoire skills into supported agent skill directories
when_to_use: A skill isn't appearing in the slash-command picker; user just added, renamed, or edited a SKILL.md; user installed a new grimoire; user mentions "skill not recognized" or "after editing skills". Run after any change in skills/ that the agent needs to pick up.
user-invocable: true
allowed-tools: Bash Read
---

# Register Grimoire Skills

You are registering Arcana skills and every installed grimoire's skills into supported agent skill directories:

- Claude Code: `~/.claude/skills/`
- Codex/ChatGPT: `~/.codex/skills/`

This cleans each skill prefix (e.g., `arc-*` for Arcana, `cook-*` for a cooking grimoire, `hr-*` for an HR grimoire) and re-registers fresh copies, ensuring the agent skill directories always match the latest source. Arcana's prefix is read from `arcana.json`; each grimoire's prefix is read from the `skill_prefix` field of its own `grimoire.json`. Codex/ChatGPT registrations are pointer-only and copy only `SKILL.md`; the real instructions remain in Arcana invocations, rites, or grimoire guides.

## Steps

1. Run the registration rite:

```bash
python3 {{ARCANA_PATH}}/rites/register_skills.py
```

On Windows, use `python` instead of `python3`.

2. Report the output to the user - show how many skills were registered and from which sources.

3. If the user wants to preview without making changes, run with `--dry-run`:

```bash
python3 {{ARCANA_PATH}}/rites/register_skills.py --dry-run
```

To target one agent explicitly:

```bash
python3 {{ARCANA_PATH}}/rites/register_skills.py --agent codex
python3 {{ARCANA_PATH}}/rites/register_skills.py --agent claude
```
