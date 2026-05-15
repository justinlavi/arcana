---
type: hub
title: "Quality Invocations"
aliases: ["quality-invocations", "judgment-passes"]
tags: [arcana/invocations, type/hub, scope/quality, hub/sub]
---

# Quality Enhancement Invocations

Judgment-based invocations for improving Arcana quality beyond what mechanical validators catch. Validators answer "is it correct?"; these invocations answer "is it excellent?"

## Available

- **[improve_documentation.md](improve_documentation.md)** — Find duplication and clarity issues across docs and invocations. Decide canonical homes; replace duplicates with links.
- **[validate_rites.md](validate_rites.md)** — Rite-specific quality checks (shellcheck, portability, error handling, docstrings). Complements the security validator.

## When to use

- Before an Arcana release.
- After bulk doc/rite changes.
- As part of `/grm-arcana-improve` (these invocations are phases of that workflow).

## Related

- **Mechanical validators**: [`../validators/validators.md`](../validators/validators.md) — run these first; they're cheap and deterministic.
- **Orchestrator**: [`../improve_arcana.md`](../improve_arcana.md)
