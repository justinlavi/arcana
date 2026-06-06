---
type: reference
title: "Validate Grimoire Links"
aliases: ["validate-grimoire-links"]
tags: [arcana/invocations, type/reference, scope/grimoire]
authority: grimoire
last_verified: 2026-05-25
---

# Invocation: Validate Grimoire Links

## Purpose

Validate that internal references resolve inside the active grimoire and that internal page link style follows the grimoire layer model.

## Invocation

```
/grm-validate links
```

## Workflow

Run against the resolved active grimoire:

```bash
python3 ARCANA_HOME/rites/validate_links.py --grimoire GRIMOIRE_ROOT
```

Report broken links and layer-specific style violations with file and line citations. Exit code 0 means all checked links resolve and internal page references use the right syntax for their layer.

## Standards Checked

- Public docs such as `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, and `docs/**` use relative Markdown links.
- Vault and AI-routing surfaces use full-path wikilinks, such as `[[chapters/travel/travel|travel]]`.
- Standard Markdown links are also allowed for external URLs, same-page anchors, and local non-Markdown artifacts.
- Wikilink labels should match the target filename stem, normalized for reading.
- Alias-only or filename-only wikilinks are invalid unless they resolve as repository-root relative paths.

## Related

- Arcana link validator -> [[invocations/arc/validators/validate_links|validate links]]
- Obsidian wikilink standard -> [[docs/obsidian|obsidian]]
- Operating model -> [[docs/operating_model|operating model]]
