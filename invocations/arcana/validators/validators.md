---
type: hub
title: "Arcana Validators"
aliases: ["validators", "arcana-validators"]
tags: [arcana/invocations, type/hub, scope/validators, hub/sub]
---

# Arcana Validators

Mechanical, deterministic checks against the Arcana repository. Each validator has its own dedicated skill, and all of them run together via the orchestrator.

For the aggregate command, see [validate_all.md](validate_all.md).

Each validator supports structured diagnostics:

```bash
python3 ../../../rites/<validator>.py --format json
python3 ../../../rites/<validator>.py --format jsonl
```

Every diagnostic carries `code`, `severity`, `path`, `line`, `message`,
`hint`, `validator`, and `docs_reference`. The default human output is for
terminal use; JSON and JSONL are for agents, editor integrations, and issue
reports.

## Available

| Validator | Skill | What it checks |
|---|---|---|
| [validate_structure.md](validate_structure.md) | `/arc-validate-structure` | Required directories and files exist; layout matches conventions |
| [validate_encoding.md](validate_encoding.md) | `/arc-validate-encoding` | UTF-8, LF line endings, BOMs, and mojibake markers |
| [validate_portability.md](validate_portability.md) | `/arc-validate-portability` | No Windows-reserved characters or basenames in any path |
| [validate_naming.md](validate_naming.md) | `/arc-validate-naming` | snake_case for paths; kebab-case for skills |
| [validate_format.md](validate_format.md) | `/arc-validate-format` | Invocation/formula schema compliance |
| [validate_frontmatter.md](validate_frontmatter.md) | `/arc-validate-frontmatter` | Every page declares its `type` and the schema's required fields |
| [validate_semantics.md](validate_semantics.md) | `/arc-validate-semantics` | Hyphenated path examples in markdown prose |
| [validate_links.md](validate_links.md) | `/arc-validate-links` | Internal markdown links resolve |
| [validate_orphans.md](validate_orphans.md) | `/arc-validate-orphans` | Every page is reachable from at least one other page |
| [validate_provenance.md](validate_provenance.md) | `/arc-validate-provenance` | Every external/hybrid page cites real sources under `sources/` |
| [validate_security.md](validate_security.md) | `/arc-validate-security` | Credential patterns and unsafe Python constructs in rites |
| [validate_skill_refs.md](validate_skill_refs.md) | `/arc-validate-skill-refs` | Slash-command references and command-surface entries resolve |

## Run them all

```bash
python3 ../../../rites/validate.py            # sequential, default
python3 ../../../rites/validate.py --parallel  # concurrent
python3 ../../../rites/validate.py --smart     # only validators relevant to git changes
python3 ../../../rites/validate.py --auto      # smart + execute
python3 ../../../rites/validate.py --format json
```

Or invoke `/arc-validate-all`, whose workflow home is [validate_all.md](validate_all.md).

## Related

- Orchestrator invocation: [`../improve_arcana.md`](../improve_arcana.md)
- Rite scripts: [`../../../rites/`](../../../rites/)
- Canonical terminology: [`../../../docs/reference.md`](../../../docs/reference.md)
