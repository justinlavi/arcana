---
type: playbook
title: "Update"
aliases: ["update", "arc-update"]
tags: [arcana/invocations, type/playbook, scope/arcana]
authority: grimoire
last_verified: 2026-06-02
---

# Invocation: Update (Arcana + grimoires)

## Purpose

Bring an Arcana install — engine source, library, agent skills, agent routing block — and every grimoire that references it back to a current, validated, synchronized state. This is the Arcana-prefix mirror of `/grm-update`; both run the one canonical Update procedure.

## Invocation

```
/arc-update
```

## Procedure

The canonical, skill-less procedure is **[[UPDATE|UPDATE]]** at the Arcana root. Read it and follow the AI Update Playbook — it resolves and pulls Arcana, validates the source, then runs `summon.py --update --apply`, which reconciles the library, pulls every grimoire (branch-aware, with a manual-pull fallback for private hosts), re-registers skills, and heals only the grimoires it confirmed current.

```bash
cat ARCANA_HOME/UPDATE.md
```

## Notes

- `/arc-update` (this command) and `/grm-update` are mirrors over the same `UPDATE.md` procedure. Most users only ever use `/grm-*`; `/arc-update` exists for maintainers and fork owners working on Arcana directly.

## Related

- **Canonical procedure**: [[UPDATE|UPDATE]]
- **Grimoire mirror**: [[invocations/grm/update|update]]
