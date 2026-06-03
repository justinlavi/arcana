---
type: playbook
title: "Update"
aliases: ["update", "grm-update"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-06-02
---

# Invocation: Update (grimoire + Arcana)

## Purpose

Bring Arcana and every grimoire in the library back to a current, validated, synchronized state. This is the grimoire-prefix entry point to Arcana's canonical **Update** process — the one command a grimoire user runs to re-sync everything.

## Invocation

```
/grm-update
```

## Procedure

The canonical, skill-less procedure is **[[UPDATE|UPDATE]]** at the Arcana root. Read it and follow the AI Update Playbook — it resolves and pulls Arcana, validates the source, then runs `summon.py --update --apply`, which reconciles the library, pulls every grimoire (branch-aware, with a manual-pull fallback for private hosts), re-registers skills, and heals only the grimoires it confirmed current.

```bash
cat ARCANA_HOME/UPDATE.md
```

## Notes

- The update covers every grimoire in `~/grimoires/library.json`, not only the one you are in; the current directory does not have to be a grimoire root.
- `/grm-update` and `/arc-update` are mirrors: both run the one `UPDATE.md` procedure. Use `/grm-update` from the grimoire-user side; `/arc-update` is the Arcana-maintainer mirror.

## Related

- **Canonical procedure**: [[UPDATE|UPDATE]]
- **Arcana mirror**: [[invocations/arcana/update|update]]
