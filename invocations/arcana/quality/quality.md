---
type: hub
title: "Quality Invocations"
aliases: ["quality-invocations", "judgment-passes"]
tags: [arcana/invocations, type/hub, scope/quality, hub/sub]
---

# Quality Enhancement Invocations

Judgment-based invocations for improving Arcana quality beyond what mechanical validators catch. Validators answer "is it correct?"; these invocations answer "is it excellent?"

## Available

- **[review_architecture.md](review_architecture.md)** - Review Arcana's whole layout, source-of-truth boundaries, naming, scalability, and AI-agent efficiency.
- **[improve_documentation.md](improve_documentation.md)** — Find duplication and clarity issues across docs and invocations. Decide canonical homes; replace duplicates with links.
- **[validate_rites.md](validate_rites.md)** — Rite-specific quality checks (portability, error handling, docstrings). Complements the security validator.
- **[architecture_backlog.md](../../../docs/architecture_backlog.md)** - Deferred S-tier architecture opportunities that need maintainer approval before implementation.

## When to use

- Before an Arcana release.
- After bulk doc/rite changes.
- As part of `/arc-improve` (these invocations are phases of that workflow).

## Related

- **Mechanical validators**: [`../validators/validators.md`](../validators/validators.md) — run these first; they're cheap and deterministic.
- **Orchestrator**: [`../improve_arcana.md`](../improve_arcana.md)
- **Architecture backlog**: [`../../../docs/architecture_backlog.md`](../../../docs/architecture_backlog.md)
