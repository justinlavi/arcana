# Invocation: Improve Arcana Quality

## Purpose

Manual, judgment-based pass over Arcana docs and invocations to find duplication and clarity issues. Pairs with the mechanical validators (`/grm-arcana-validate-*`) — validators answer "is it correct?", this invocation answers "is it excellent?"

## Invocation

Runs as a phase of `/grm-arcana-improve`. There is no standalone slash command — the work is judgment-based and benefits from the broader context the orchestrator provides.

## When to cast

- Before an Arcana release
- After bulk doc changes or feature additions
- As part of `/grm-arcana-improve` (this invocation is one phase)
- When something feels repetitive, unclear, or hard to navigate

## Workflow

### 1. Find duplication

Treat the same fact appearing in two places as a maintenance bug. Common smells in Arcana:

- Skill lists, file trees, or schema examples copy-pasted across docs
- The same concept explained twice with slightly different wording
- A "block of text" (instruction template, code snippet) in multiple files

Quick scans:

```bash
# Lines (5+ words) repeated across .md files in arcana/
find . -name "*.md" -not -path "./formulae/*" -exec cat {} \; \
  | grep -v '^#' | grep -E '.{40,}' | sort | uniq -cd | sort -rn | head -20

# Same heading appearing in multiple files
grep -rh "^## " --include="*.md" | sort | uniq -cd | sort -rn | head -20
```

For each hit, decide:

- **Intentional**: different audiences genuinely need the same info → keep both, but link them so future edits propagate
- **Drift risk**: same data should be sourced from one place → move to a canonical home and link from the rest, OR add a generator (see [`rites/sync_docs.py`](../../../rites/sync_docs.py) for the pattern)
- **Stale**: one is wrong → fix or delete the wrong one

### 2. Find clarity issues

Read each doc as if it's the first thing you've ever seen about Arcana. Watch for:

- Jargon used before it's defined
- Pronouns ("it", "this") without a clear antecedent
- Code/config examples that lack the surrounding context to interpret them
- Long paragraphs that could be lists or tables
- Sections that don't answer a question the reader would actually ask

Mechanical aids:

```bash
# Long lines (often hard to read)
find docs -name "*.md" -exec grep -l '.\{160,\}' {} \;

# Acronyms (candidates for first-use definition)
grep -rho '\b[A-Z][A-Z]+\b' --include="*.md" docs | sort | uniq -c | sort -rn | head
```

### 3. Find structural issues

- Documents doing more than one job (split them)
- Documents with nothing other docs need (consider deleting)
- Cross-references that go through too many hops to reach the answer
- Missing or stale entries in [`INDEX.md`](../../../INDEX.md), [`docs/skills.md`](../../../docs/skills.md), or other auto-generated indexes (regenerate with `python3 rites/sync_docs.py --apply`)

### 4. Apply fixes

For each issue:

1. Decide the canonical home for the content.
2. Edit the canonical and replace duplicates with links.
3. Run the validator suite (`/grm-arcana-validate-all`) to make sure structural and link checks still pass.
4. If you moved a section, update any docs that linked to its old anchor.

## What this invocation is NOT

- Not a replacement for the mechanical validators — run those too.
- Not a place to enforce rules; this is human judgment work. Codify recurring rules as validator checks once you've seen them three times.

## Related

- **Validators**: [`validators/INDEX.md`](../validators/INDEX.md) and `/grm-arcana-validate-all`
- **Rite quality**: [`validate_rites.md`](validate_rites.md) (rite-specific checks; complementary)
- **Doc generator**: [`rites/sync_docs.py`](../../../rites/sync_docs.py) (the pattern for replacing prose-as-data with single-source views)
- **Orchestrator**: [`improve_arcana.md`](../improve_arcana.md)
