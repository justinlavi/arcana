---
type: playbook
title: "Audit Boundaries"
aliases: ["audit-boundaries", "magical-boundary"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-05-15
---

# Invocation: Audit Magical Boundaries

## Purpose

Judgment-based scan that enforces the magical/practical boundary: magical terminology (Invocation, Formula, Rite, Grimoire, `/arc-*`) is reserved for Arcana's system layer; grimoires use practical terminology (templates, scripts, snippets, guides).

Canonical definition and full term mapping: [[docs/reference|reference]] A "The Magical Boundary". Do not redefine the rules here - read that section first, then apply it.

## Invocation

```
/grm-audit-boundaries          # audit active grimoire (cwd)
/grm-audit-boundaries --arcana # also scan Arcana itself (strictest)
```

Also runs as part of `/grm-improve` and `/arc-improve`.

## When to cast

- Before publishing or releasing a grimoire
- After adding or restructuring chapters
- During code review of Grimoire updates

## Rules enforced

1. **No magical directories in grimoires.** `invocations/`, `formulae/`, `rites/` exist only inside Arcana. Grimoire equivalents: `templates/`, `scripts/`, `snippets/`, `configs/`, `policies/`, `guides/`, `recipes/`, `playbooks/` - whatever fits the subject.
2. **No magical terminology in chapter prose.** Phrases like "perform the invocation" or "consult the formula" belong in Arcana docs only. Referencing Arcana by name (e.g. "run `/grm-improve`") is fine.
3. **No platform-specific assumptions in shared content.** Slack, SharePoint, Confluence, Teams, Jira, GitHub etc. should be generic ("communication channel", "document repository", "issue tracker") unless documenting an actual integration.
4. **No prescriptive team/department buzzwords in shared chapters.** Don't write "the HR team owns this" in shared content unless the grimoire is itself an HR grimoire (in which case department naming is the subject and is fine). Words like HR, Marketing, Legal, Sales, Finance get scrubbed when they're acting as scope assumptions about the *reader*, not the *content*.
5. **Generic example names in Arcana.** When Arcana shows examples, use the canonical pair `cooking-grimoire` (personal) and `hr-grimoire` (workplace). For sub-examples use `Alice/Bob`, `Project Alpha`, `{your-grimoire}`. Real company/product/person names only when documenting an actual integration. (Grimoires may use whatever real names their subject requires.)
6. **Arcana is universal.** When `--arcana` is set, rules 1-5 apply at zero tolerance. No specific domains, platforms, hardcoded paths, or environment assumptions anywhere.

## Where the rules relax

`chapters/projects/` (project-specific overrides) may name actual platforms, teams, products, and people. Shared chapters and Arcana may not.

## Workflow

### 1. Magical directories

```bash
find . -type d \( -name invocations -o -name formulae -o -name rites \) -not -path './.git/*'
```

Inside a grimoire, any hit is a critical violation. Rename to the practical equivalent (rule 1) or, if it's genuine system-layer logic, move it to Arcana.

### 2. Magical terminology in prose

```bash
grep -rniE 'invoke .*invocation|consult .*formula|perform .*rite|cast .*spell' chapters/ templates/ scripts/ 2>/dev/null
```

Skip references to Arcana itself (`/arc-*` skill names, "see Arcana", etc.). Rewrite the rest in practical voice.

### 3. Platform / scope-assumption language in shared content

```bash
# Platforms
grep -rniE '\b(Slack|Teams|Discord|SharePoint|Confluence|Google Drive|Jira|Bitbucket)\b' chapters/ \
  | grep -v chapters/projects/

# Scope-assumption words (only flag when the grimoire's subject isn't itself one of these)
grep -rniE '\b(HR|Legal|Marketing|Sales|Finance)\b|\b(VP|Director|Manager) of\b' chapters/ \
  | grep -v chapters/projects/
```

Hits outside `chapters/projects/` should be reviewed: if the grimoire's subject *is* HR / Sales / etc., these terms are fine; otherwise rewrite generically. Hits inside `chapters/projects/` are always allowed.

### 4. Example names

Skim the same files for real company / product / person names used as examples. Replace with the generic placeholders listed in rule 5.

### 5. Arcana mode (`--arcana`)

Run all of the above against Arcana itself (`~/grimoires/arcana/`). Any violation is critical - Arcana must work for every domain, so it cannot mention any specific one.

## Report format

```
Magical Boundary Compliance: PASS | FAIL

- Magical directories:    N
- Magical terminology:    N
- Platform assumptions:   N
- Team buzzwords:         N
- Example genericity:     PASS/FAIL
- Arcana universality:    PASS/FAIL  (--arcana only)
```

For each violation, report file, line, offending text, and suggested fix. Group by severity:

- **Critical**: magical directories in a domain; any violation in Arcana
- **Warning**: magical terminology or unwarranted platform / scope-assumption language in shared chapters
- **Info**: example names that work but could be more generic

## Enforcement levels

| Scope | Tolerance |
|---|---|
| Arcana | Zero - every violation is critical |
| Shared chapters in a grimoire | Strict - critical or warning |
| `chapters/projects/` | Relaxed - warning or info, real names allowed |

## Related

- **Reference**: [[docs/reference|reference]] A "The Magical Boundary" (canonical rules and term mapping)
- **Operating model**: [[docs/operating_model|operating model]] (why the boundary exists)
- **Semantic naming**: `/grm-audit-semantics` (judgment-based naming review)
- **Orchestrator (Arcana)**: `/arc-improve`
- **Orchestrator (grimoire)**: `/grm-improve`
