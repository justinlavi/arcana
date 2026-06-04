---
type: reference
title: "Temporary 1.3.0 Handoff"
aliases: ["1.3.0-handoff", "temporary-release-handoff"]
tags: [type/reference, arcana/docs, release/1.3.0]
authority: grimoire
last_verified: 2026-06-04
---

# Temporary 1.3.0 Handoff

This is a temporary handoff note for continuing the Arcana 1.3.0 work on another machine or with another AI agent. Remove it before final release if it is no longer useful.

## Branch

The working branch is:

```bash
1.3.0
```

No commit has been made yet. The working tree contains the full in-progress 1.3.0 change set.

## Goal

Arcana 1.3.0 tightens the public slash-command surface so commands read left-to-right by scope and intent, and separates pure mechanical validation from AI/judgment work.

The intended semantics are:

- `validate` means deterministic, mechanical, script-backed checks with exit codes.
- `audit` means judgment-based review where an AI agent evaluates intent, boundaries, naming, or structure.
- `sync` means refresh local agent state from source-of-truth files.
- `import` means bring outside material into a grimoire.
- `capture` means preserve an answer or derived insight from chat into wiki form.
- `health-check` means inspect a grimoire for structural and knowledge-quality issues.

## Main Command Changes

Validation and audit:

- Many granular `/arc-validate-*` skills collapsed into `/arc-validate [selector]`.
- Many granular `/grm-validate-*` skills collapsed into `/grm-validate [selector]`.
- `grm-analyze-semantics` became `/grm-audit-semantics`.
- `grm-validate-boundaries` became `/grm-audit-boundaries`.

Broader skill semantic cleanup:

- `grm-file-answer` became `/grm-capture-answer`.
- `grm-ingest` became `/grm-import`.
- `grm-lint` became `/grm-health-check`.
- `grm-register-skills` became `/grm-agent-sync-skills`.
- `arc-agent-register-skills` became `/arc-agent-sync-skills`.
- `arc-agent-update` became `/arc-agent-sync-instructions`.

Keep `/grm-update` as the primary update entry point for normal users. It is the command most grimoire users should run to update Arcana, follow `UPDATE.md`, reconcile the library, pull grimoires, sync skills, refresh agent blocks, and heal current grimoires. `/arc-update` remains the Arcana-maintainer mirror.

## Implementation State

The work has already updated:

- `VERSION` to `1.3.0`.
- `CHANGELOG.md` with a 1.3.0 entry dated 2026-06-04.
- Skill source directories under `skills/`.
- Invocation files under `invocations/`.
- `rites/data/command_surface.json`.
- `rites/data/summon_contract.json`.
- `rites/validate.py` selector handling.
- `rites/append_log.py` operation vocabulary.
- Docs, templates, and generated `docs/skills.md`.
- Tests and eval fixtures for the new command names.

The old installed skill names were cleaned from the local Claude and Codex targets on this machine, and the new names were registered.

## Important Notes

- The underlying implementation script remains `rites/register_skills.py`. Public wording now says "sync skills"; do not rename this rite unless doing a separate implementation pass.
- `rites/append_log.py` accepts new log ops (`import`, `health-check`, `capture-answer`) and keeps legacy ops (`ingest`, `lint`, `file-answer`) for compatibility.
- Historical old command names may remain in `CHANGELOG.md`. Current docs and installed skill surfaces should use the new names.
- A final release cleanup should decide whether this temporary handoff file should be removed before tagging.

## Verification Already Run

These passed on 2026-06-04:

```bash
python3 rites/validate.py --summary
python3 rites/validate.py --parallel
python3 -m pytest tests/test_append_log.py tests/test_register_skills.py tests/test_agent_targets.py tests/test_command_surface.py tests/test_sync_docs.py tests/test_eval_scaffolding.py
python3 -m pytest
```

Results:

- Targeted rename-sensitive tests: `71 passed`.
- Full suite: `311 passed, 3 deselected`.
- Parallel validation passed after running outside the sandbox restriction.
- Final stale-command scans found no old command names in source or installed skill directories, excluding historical changelog references.

## Resume Checklist

On another machine:

1. Confirm branch and status:

   ```bash
   git branch --show-current
   git status --short
   ```

2. Review the diff:

   ```bash
   git diff --stat
   git diff -- README.md CHANGELOG.md rites/data/command_surface.json docs/skills.md
   ```

3. Run validation and tests:

   ```bash
   python3 rites/validate.py --summary
   python3 rites/validate.py --parallel
   python3 -m pytest
   ```

4. Sync local agent skills on that machine:

   ```bash
   python3 rites/register_skills.py --dry-run
   python3 rites/register_skills.py
   ```

5. Re-run a stale command scan:

   ```bash
   rg -n 'grm-file-answer|grm-ingest|grm-lint|grm-register-skills|arc-agent-register-skills|arc-agent-update|skills/(grimoire/(file-answer|ingest|lint|register-skills)|agent/(register-skills|update))|invocations/grimoire/(file_answer|ingest|lint|register_skills)|invocations/agent/(register_skills|update_agent_block)|sync_skills\.py' . --glob '!CHANGELOG.md'
   ```

6. Decide whether to remove this temporary handoff doc before committing the release branch.
