---
type: hub
title: "Arcana Validators"
aliases: ["validators", "arcana-validators"]
tags: [arcana/invocations, type/hub, scope/validators, hub/sub]
---

# Arcana Validators

Mechanical, deterministic checks against the Arcana repository. Each validator has its own dedicated skill, and all of them run together via the orchestrator.

## Available

| Validator | Skill | What it checks |
|---|---|---|
| [validate_structure.md](validate_structure.md) | `/grm-arcana-validate-structure` | Required directories and files exist; layout matches conventions |
| [validate_naming.md](validate_naming.md) | `/grm-arcana-validate-naming` | snake_case for paths; kebab-case for skills |
| [validate_format.md](validate_format.md) | `/grm-arcana-validate-format` | Invocation/formula schema compliance |
| [validate_semantics.md](validate_semantics.md) | `/grm-arcana-validate-semantics` | Hyphenated path examples in markdown prose |
| [validate_links.md](validate_links.md) | `/grm-arcana-validate-links` | Internal markdown links resolve |
| [validate_security.md](validate_security.md) | `/grm-arcana-validate-security` | Credential patterns and unsafe Python constructs in rites |

Plus a non-validator skill that runs the same scan over `/grm-*` references in prose: `/grm-arcana-validate-skill-refs`.

## Run them all

```bash
python3 ../../../rites/validate.py            # sequential, default
python3 ../../../rites/validate.py --parallel  # concurrent
python3 ../../../rites/validate.py --smart     # only validators relevant to git changes
python3 ../../../rites/validate.py --auto      # smart + execute
```

Or invoke `/grm-arcana-validate-all`.

## Related

- Orchestrator invocation: [`../improve_arcana.md`](../improve_arcana.md)
- Rite scripts: [`../../../rites/`](../../../rites/)
- Canonical terminology: [`../../../docs/reference.md`](../../../docs/reference.md)
