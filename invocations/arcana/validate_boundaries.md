# Invocation: Validate Magical Boundaries

## Purpose

Judgment-based scan that enforces the magical/practical boundary: magical terminology (Invocation, Formula, Rite, Grimoire, `/grm-*`) is reserved for Arcana's system layer; domain grimoires use practical terminology (templates, scripts, snippets, guides).

Canonical definition and full term mapping: [`docs/reference.md`](../../docs/reference.md) § "The Magical Boundary". Do not redefine the rules here — read that section first, then apply it.

## Invocation

```
/grm-arcana-validate-boundaries          # validate domain grimoire (cwd)
/grm-arcana-validate-boundaries --arcana # validate Arcana itself (strictest)
```

Also runs as part of `/grm-domain-improve` and `/grm-arcana-improve`.

## When to cast

- Before publishing or releasing a grimoire
- After adding or restructuring chapters
- During code review of Grimoire updates

## Rules enforced

1. **No magical directories in domain grimoires.** `invocations/`, `formulae/`, `rites/` exist only inside Arcana. Domain equivalents: `templates/`, `scripts/`, `snippets/`, `configs/`, `policies/`, `guides/`.
2. **No magical terminology in chapter prose.** Phrases like "perform the invocation" or "consult the formula" belong in Arcana docs only. Referencing Arcana by name (e.g. "run `/grm-domain-improve`") is fine.
3. **No platform-specific assumptions in shared content.** Slack, SharePoint, Confluence, Teams, Jira, GitHub etc. should be generic ("communication channel", "document repository", "issue tracker") unless documenting an actual integration.
4. **No team/department buzzwords in shared content.** HR, Marketing, Legal, Sales, Finance etc. become "domain", "knowledge area", "your team".
5. **Generic example names.** Use `Domain A`, `Project Alpha`, `Alice/Bob`, `{Your Project}`. Real company / product / person names only when documenting actual integrations.
6. **Arcana is universal.** When `--arcana` is set, rules 1–5 apply at zero tolerance. No specific domains, platforms, hardcoded paths, or environment assumptions anywhere.

## Where the rules relax

`chapters/projects/` (project-specific overrides) may name actual platforms, teams, products, and people. Shared chapters and Arcana may not.

## Workflow

### 1. Magical directories

```bash
find . -type d \( -name invocations -o -name formulae -o -name rites \) -not -path './.git/*'
```

Inside a domain grimoire, any hit is a critical violation. Rename to the practical equivalent (rule 1) or, if it's genuine system-layer logic, move it to Arcana.

### 2. Magical terminology in prose

```bash
grep -rniE 'invoke .*invocation|consult .*formula|perform .*rite|cast .*spell' chapters/ templates/ scripts/ 2>/dev/null
```

Skip references to Arcana itself (`/grm-*` skill names, "see Arcana", etc.). Rewrite the rest in practical voice.

### 3. Platform / department language in shared content

```bash
# Platforms
grep -rniE '\b(Slack|Teams|Discord|SharePoint|Confluence|Google Drive|Jira|Bitbucket)\b' chapters/ \
  | grep -v chapters/projects/

# Departments / roles
grep -rniE '\b(HR|Legal|Marketing|Sales|Finance)\b|\b(VP|Director|Manager) of\b' chapters/ \
  | grep -v chapters/projects/
```

Hits outside `chapters/projects/` should be rewritten generically (see `docs/reference.md` for the mapping table). Hits inside `chapters/projects/` are allowed.

### 4. Example names

Skim the same files for real company / product / person names used as examples. Replace with the generic placeholders listed in rule 5.

### 5. Arcana mode (`--arcana`)

Run all of the above against Arcana itself (`~/grimoires/arcana/`). Any violation is critical — Arcana must work for every domain, so it cannot mention any specific one.

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
- **Warning**: magical terminology or platform/department language in shared chapters
- **Info**: example names that work but could be more generic

## Enforcement levels

| Scope | Tolerance |
|---|---|
| Arcana | Zero — every violation is critical |
| Shared chapters in a domain grimoire | Strict — critical or warning |
| `chapters/projects/` | Relaxed — warning or info, real names allowed |

## Related

- **Reference**: [`docs/reference.md`](../../docs/reference.md) § "The Magical Boundary" (canonical rules and term mapping)
- **Operating model**: [`docs/operating_model.md`](../../docs/operating_model.md) (why the boundary exists)
- **Semantic naming**: `/grm-domain-analyze-semantics` (judgment-based naming review)
- **Orchestrator (Arcana)**: `/grm-arcana-improve`
- **Orchestrator (domain)**: `/grm-domain-improve`
