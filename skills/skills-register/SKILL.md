---
name: {{NAMESPACE}}-skills-register
description: Register all Grimoire skills from Arcana and domain grimoires into supported agent skill directories
user-invocable: true
allowed-tools: Bash Read
---

# Register Grimoire Skills

You are registering all Grimoire skills from Arcana and every installed domain grimoire into supported agent skill directories:

- Claude Code: `~/.claude/skills/`
- Codex/ChatGPT: `~/.codex/skills/`

This cleans each namespace (e.g., `grm-*`, `jpn-*`) and re-registers fresh copies, ensuring the agent skill directories always match the latest source. Each namespace is read from the `namespace` field of the grimoire's own `grimoire.json` (Arcana included). Codex/ChatGPT registrations are pointer-only and copy only `SKILL.md`; the real instructions remain in Arcana invocations, rites, or domain guides.

## Steps

1. Run the registration rite:

```bash
python3 {{ARCANA_PATH}}/rites/register_skills.py
```

On Windows, use `python` instead of `python3`.

2. Report the output to the user — show how many skills were registered and from which sources.

3. If the user wants to preview without making changes, run with `--dry-run`:

```bash
python3 {{ARCANA_PATH}}/rites/register_skills.py --dry-run
```

To target one agent explicitly:

```bash
python3 {{ARCANA_PATH}}/rites/register_skills.py --agent codex
python3 {{ARCANA_PATH}}/rites/register_skills.py --agent claude
```
