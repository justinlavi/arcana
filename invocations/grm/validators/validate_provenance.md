---
type: reference
title: "Validate Grimoire Provenance"
aliases: ["validate-grimoire-provenance"]
tags: [arcana/invocations, type/reference, scope/grimoire]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Validate Grimoire Provenance

## Purpose

Validate that active-grimoire pages with `authority: external` or
`authority: hybrid` cite real source artifacts. Also validate source wrapper
Markdown under `sources/`: wrappers must be `type: source`,
`authority: external`, cite their original URL, capture origin, or sibling raw
artifact, and avoid self-citation.

## Invocation

```
/grm-validate provenance
```

## Workflow

Run against the resolved active grimoire:

```bash
python3 ARCANA_HOME/rites/validate_provenance.py --grimoire GRIMOIRE_ROOT
```

Pages must not cite transient `inbox/` paths. Stable source artifacts and
source wrappers belong under `sources/`; authored synthesis belongs under
`chapters/`.
