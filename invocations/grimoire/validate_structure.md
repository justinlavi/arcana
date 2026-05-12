# 📐 Invocation: Validate Grimoire Structure Compliance

## ⚡ Purpose

Validate grimoire chapter routers and page structure against Arcana formulae.

This invocation ensures:
- Chapter routers follow `chapter_index.formula.md`
- Pages follow `page.formula.md`
- Required sections are present

---

## Preconditions

Before executing, verify the current working directory is a registered domain grimoire (check `~/grimoires/library.json`). If it is not, list available grimoires and tell the user to `cd` to one. Arcana is not a grimoire. **Stop** if the check fails.

---

## When to Cast

- After creating or editing chapters/pages
- During periodic grimoire quality reviews
- Before publishing or handoff

---

## Invocation

From your grimoire directory, cast:

```
/grm-domain-validate-structure
```

Optional scopes:

```
/grm-domain-validate-structure --chapter=<chapter_name>
/grm-domain-validate-structure --arcana
```

---

## Required Templates

- Chapter routers: `formulae/chapter_index.formula.md`
- Pages: `formulae/page.formula.md`

---

## Validation Workflow

### Phase 1: File Classification

1. Identify chapter routers (`**/INDEX.md`, excluding root/README-only contexts)
2. Identify knowledge pages (`**/*.md` excluding routers and README docs)

### Phase 2: Chapter Router Checks

Required sections:
- `Purpose` (critical)
- `When to Use` (critical)
- `Routes` (critical)
- `Related Chapters` (recommended)

### Phase 3: Page Checks

Every page should include:
- `Purpose` (critical)
- `When to Use` (critical)
- `Primary Sources` (recommended for pages referencing external systems)
- `Gotchas` (recommended)
- `Related Docs` (recommended)

### Phase 4: Content Quality Flags

- Pages with snapshot values but no extraction command: warning
- Pages referencing external files that don't exist: warning

---

## Compliance Matrix

### Chapter Routers

| Check | Priority |
|---|---|
| Purpose | Critical |
| When to Use | Critical |
| Routes | Critical |
| Related Chapters | Recommended |

### Pages

| Check | Priority |
|---|---|
| Purpose | Critical |
| When to Use | Critical |
| Primary Sources (when referencing external systems) | Recommended |
| Gotchas | Recommended |
| Related Docs | Recommended |

---

## Outputs

- Compliance summary by chapter/page
- Critical/recommended findings list
- Suggested fixes

---

## Related Docs

- `docs/operating_model.md`
- `formulae/page.formula.md`
