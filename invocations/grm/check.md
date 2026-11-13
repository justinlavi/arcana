---
type: playbook
title: "Check"
aliases: ["check", "grm-check", "health-check", "validate-grimoire", "audit"]
tags: [arcana/invocations, type/playbook, scope/grimoire]
authority: grimoire
last_verified: 2026-11-12
---

# Invocation: Check (evaluate the grimoire)

## Purpose

One verb for every question of the form "is my grimoire in good shape?". A
bare `check` is the full health pass: the mechanical validators plus the
judgment passes that keep an LLM wiki honest as it grows (stale claims, ghost
references, contradictions, missing cross-references). Scopes narrow it to
the mechanical subset, to one validator, to a naming review, to a boundary
review, or to applying the mechanical repairs.

## Invocation

```
/grm-check                   # full health pass
/grm-check quick             # mechanical validators only
/grm-check <validator> ...   # one or more validators: structure encoding portability format frontmatter links orphans provenance doc-trees
/grm-check smart | auto | summary | parallel
/grm-check naming            # judgment review of names, terminology, discoverability
/grm-check boundaries        # judgment review of the magical/practical boundary
/grm-check fix               # apply the mechanical repairs (wikilink promotion and casing)
```

Flags: `--since <window>` for the stale window (default 90 days);
`--chapter=<name>` to narrow `naming`; `--arcana` to run `naming` or
`boundaries` against Arcana itself.

## Preconditions

1. Resolve `GRIMOIRE_ROOT` with the shared grimoire directory guard. Refuse
   for Arcana itself unless the scope is `naming --arcana` or
   `boundaries --arcana`.
2. The grimoire must have `chapters/` and a root hub.

## Routing

Read the first positional argument:

- none -> [Full health pass](#full-health-pass).
- `quick`, `smart`, `auto`, `summary`, `parallel`, or validator names ->
  [Mechanical validators](#mechanical-validators) with that selector.
- `naming` -> [Naming review](#naming-review).
- `boundaries` -> [Boundary review](#boundary-review).
- `fix` -> [Mechanical repairs](#mechanical-repairs).

Mechanical rites' output is the source of truth for structure, frontmatter,
link, orphan, and provenance findings; never override it. Contradictions and
stale claims are surfaced, never silently fixed. The check operates on the
active grimoire only.

---

## Mechanical validators

```bash
ARCANA_HOME/bin/arcana validate --grimoire GRIMOIRE_ROOT            # quick: the full mechanical suite
ARCANA_HOME/bin/arcana validate --grimoire GRIMOIRE_ROOT links frontmatter
ARCANA_HOME/bin/arcana validate --grimoire GRIMOIRE_ROOT smart     # which validators the current git changes need
ARCANA_HOME/bin/arcana validate --grimoire GRIMOIRE_ROOT auto      # run those
ARCANA_HOME/bin/arcana validate --grimoire GRIMOIRE_ROOT summary
ARCANA_HOME/bin/arcana validate --grimoire GRIMOIRE_ROOT parallel
```

| Selector | Rite | Checks |
|---|---|---|
| `structure` | `validate_grimoire_structure.py` | Required files and directories, folder-named hubs, managed scaffold parity, Obsidian config |
| `encoding` | `validate_encoding.py` | UTF-8 without BOM, LF line endings, no mojibake or repair artifacts |
| `portability` | `validate_portability.py` | Windows-safe paths, no case collisions |
| `format` | `validate_format.py` | Markdown tables, code fences, tree examples |
| `frontmatter` | `validate_frontmatter.py` | Page frontmatter schema |
| `links` | `validate_links.py` | Links resolve, match on-disk casing, and use the right style per layer |
| `orphans` | `validate_orphans.py` | Every page is reachable from another page |
| `provenance` | `validate_provenance.py` | External and hybrid pages cite real sources |
| `doc-trees` | `validate_doc_trees.py` | ASCII directory diagrams match the filesystem |

Per-validator detail: [[invocations/grm/validators/validators|validators]].
Report failed validators with diagnostics grouped by file and line. Exit 0
means the selected validators passed, 1 means one or more failed, 2 means the
selector was invalid.

---

## Full health pass

### Phase 1: Mechanical rites

Run the full mechanical suite (above) and capture the output. Stop and
report if structure or frontmatter has hard errors; they invalidate the later
phases.

### Phase 2: Stale claims

For every page with `last_verified` older than the stale window:

- List page, `last_verified`, and chapter.
- Categorize: critical (referenced by hubs), normal (leaf), historical
  (`status/deprecated` tag).
- Surface for review; never auto-update `last_verified`. Verification is a
  human or LLM judgment act.

### Phase 3: Ghost references

Scan chapter markdown for entity-shaped tokens (capitalized phrases, code
identifiers, recurring proper nouns). For any token that appears in three or
more pages and has no page of its own, propose creating one; list frequency
and source pages. The user picks which to promote.

### Phase 4: Contradictions

For pages that share tags (especially the same `chapter/<chapter>`), look
for opposing claims: numerical (different version numbers or counts),
procedural (different steps for the same task), definitional (different
meanings for one term). Flag each with file:line citations. Resolution is the
user's call.

### Phase 5: Missing cross-references

For each pair of pages in the same chapter or sharing a `domain/<...>` tag
that discuss the same entity or concept, make sure each links to the other;
suggest the full-path wikilinks that close the gap.

### Optional: parallel judgment lanes

Phases 2-5 are independent read-only scans. If, and only if, this agent can
spawn subagents, run them as parallel read-only lanes; otherwise run them in
order. The orchestrator always owns Phases 1, 6, 7, and 8; lanes only surface
and propose. Lane mechanics and the serial fallback:
[[invocations/meta/subagent_lanes|subagent lanes]].

| Lane | Covers | Primary question |
|---|---|---|
| stale-claims | Phase 2 | Which pages are past the stale window, categorized critical / normal / historical? Surface only. |
| ghost-references | Phase 3 | Which entity-shaped tokens appear in 3+ pages with no page of their own? |
| contradictions | Phase 4 | Where do numerical, procedural, or definitional claims conflict, with file:line citations? |
| missing-cross-refs | Phase 5 | Which page pairs discuss the same concept but lack reciprocal full-path wikilinks? |

### Phase 6: Apply fixes

Group findings by category and ask the user:

- **Auto-apply**: clearly mechanical fixes (broken links the rite located,
  missing wikilinks whose target exists, frontmatter format issues). The
  wikilink promotion is the [Mechanical repairs](#mechanical-repairs) flow.
- **Confirm-then-apply**: orphan wiring (which hub should own this orphan?),
  terminology standardization, page promotions.
- **Surface only**: contradictions, stale claims, ghost references. List
  them; act only on explicit approval.

### Phase 7: Recent activity

```bash
ARCANA_HOME/bin/arcana recent_changes --grimoire GRIMOIRE_ROOT --since 90d
```

Relate findings to recent edits. If the grimoire is not a git repository the
rite says `no history`; report that plainly rather than inventing a timeline.

### Phase 8: Re-validate

Re-run the mechanical suite. It must pass before the check is complete.

### Health report

| Category | Count | Status |
|---|---|---|
| Structure errors | n | pass/fail |
| Frontmatter violations | n | pass/fail |
| Broken links / wikilinks | n | pass/fail |
| Orphans | n | listed |
| Provenance violations | n | listed |
| Stale (past window) | n | listed |
| Ghost references | n | listed |
| Contradictions | n | listed |
| Missing cross-refs | n | listed |
| Fixes applied | n | itemized |

Every page touched in Phase 6 is listed.

---

## Mechanical repairs

Promote filename-only wikilinks (`[[foo]]`, `[[parent_sibling|sibling]]`)
to canonical full-path form (`[[chapters/path/to/foo|foo]]`), and respell
full-path wikilinks whose casing differs from the file on disk. The engine is
`rites/repair_links.py`; the agent dry-runs, surfaces, gets approval, applies,
and resolves ambiguities by reading context. The grimoire should be under
version control so the change set can be reviewed as a diff.

1. **Dry run.** `ARCANA_HOME/bin/arcana repair_links --grimoire GRIMOIRE_ROOT`
   reports four sections: repairs (unambiguous), ambiguous (several
   candidates; the rite never guesses), unresolvable (no file matches), and
   skipped (partial-path forms left alone).
2. **Review.** Check bulk patterns resolve sensibly, sanity-check any
   `(via display-label fallback)` resolution, and look at ambiguous cases
   where neither candidate fits (the page may need splitting or moving first).
3. **Apply.** `ARCANA_HOME/bin/arcana repair_links --grimoire GRIMOIRE_ROOT --apply`.
   Edits are per-file and atomic; existing display labels are preserved and a
   stem label is added where none exists.
4. **Resolve ambiguities by hand.** Open each `[AMBI]` source line, read the
   surrounding paragraph, and edit the wikilink to the intended full path.
   For each `[MISS]` entry the target does not exist: delete the reference,
   file a page, or fix the typo; never fabricate a target.
5. **Re-validate** with `links` and `orphans`; the orphan count should drop as
   reconnected pages rejoin the routing graph.
6. **Report**: files touched, mechanical repairs, ambiguities resolved,
   unresolvable misses left, broken-link counts before and after.

Resolution order the rite tries (first hit wins): sibling in the source
directory; unique descendant of the source directory; unique descendant of
the source chapter; globally unique under `chapters/`; display-label fallback.
The rite skips code fences, inline code, placeholder tokens, and any body that
already contains a `/`.

---

## Naming review

Judgment-based analysis of naming and organization: are chapter and file
names clear, discoverable, terminologically consistent, and token-efficient?
Grimoires have no mechanical semantics validator; this review reads meaning.

1. **Load context.** Read the root hub, the chapter list, and
   `docs/reference.md` if present for the canonical vocabulary. Read
   `naming` from `grimoire.json` (`snake_case` when absent); if none is
   recorded, note the dominant pattern and propose recording it.
2. **Score each chapter and file name** on four dimensions, 0-100 each:
   specificity (penalize `misc`, `stuff`, version-stamped names; reward
   domain-specific compounds), searchability (terms a user or agent would
   query; reachable from a hub), comprehension (self-explanatory,
   unambiguous abbreviations, right jargon level), token efficiency (name
   length against knowledge contained, hop count to reach it). Grades: A
   80-100 keep; B 70-79 optional polish; C 60-69 consider rename; D 50-59
   should rename; F below 50 must rename.
3. **Terminology drift.** Build a synonym map across names, headings, and
   prose (`config` / `configuration` / `cfg`, `repo` / `repository`, case
   variants). Pick a canonical form; `docs/reference.md` is authoritative
   when it exists. Filenames that deviate from the recorded naming
   convention are advisory findings, never errors; under `preserve` imported
   casing is intentional and is not a finding.
4. **Discoverability.** For five to ten plausible queries, is the hop count
   proportionate to the topic's depth? Flag orphans, single points of
   failure (critical knowledge with one route in), and hot paths buried
   behind extra hops.
5. **Structure.** Depth is open-ended; flag gratuitous nesting and missed
   grouping, bloated chapters (split candidates), tiny ones (merge
   candidates), more than eight siblings under one hub, incoherent
   parent/child composition, and hubs with a single child (collapse
   candidates).
6. **Recommendations**, grouped by priority: critical renames (score below
   50), suggested renames (50-69), terminology standardization, structure
   changes, and quick wins (under 30 minutes for a 10-point gain). For each
   rename give current name, proposed name, files affected, what breaks,
   effort, and predicted gain.

Deliver in chat: the analysis report (grades, top and bottom five, conflicts
with chosen canonical forms, renames with impact), the quick-wins list, and a
terminology registry (JSON of canonical terms, abbreviations, per-chapter
scores). Do not write files unless asked. Apply critical renames,
terminology standardization, and quick wins on confirmation; weigh
refactors over two hours or renames touching more than ten files carefully;
defer cosmetic changes and anything that conflicts with conventions the user
has set. Naming heuristics: nouns or noun phrases, domain vocabulary over
casual paraphrase, no temporal or version-specific names, clarity over
brevity, the recorded naming convention for paths.

---

## Boundary review

Judgment-based scan of the magical/practical boundary: magical terminology
(Invocation, Formula, Rite, `/arc-*`) is reserved for Arcana's system layer;
grimoires use practical terminology (templates, scripts, snippets, guides).
The canonical rules and term mapping are in [[docs/reference|reference]]
under "The Magical Boundary"; read that section first, then apply it.

Rules: no magical directories in a grimoire (`invocations/`, `formulae/`,
`rites/` exist only in Arcana); no magical terminology in chapter prose
(naming an Arcana command is fine); no platform-specific assumptions in
shared content (name the generic role, not the vendor, unless documenting an
integration); no department buzzwords acting as scope assumptions about the
reader; generic example names in Arcana (`cooking-grimoire`, `dnd-grimoire`,
`Alice`/`Bob`, `Project Alpha`). `chapters/projects/` may name real platforms,
teams, products, and people. Under `--arcana` every rule applies at zero
tolerance.

1. Magical directories:
   `find . -type d \( -name invocations -o -name formulae -o -name rites \) -not -path './.git/*'`.
   Any hit inside a grimoire is critical: rename to the practical equivalent
   or move genuine system logic to Arcana.
2. Magical terminology in prose:
   `grep -rniE 'invoke .*invocation|consult .*formula|perform .*rite|cast .*spell' chapters/ templates/ scripts/`.
   Skip references to Arcana itself; rewrite the rest in practical voice.
3. Platform and scope-assumption language outside `chapters/projects/`:
   `grep -rniE '\b(Slack|Teams|Discord|SharePoint|Confluence|Google Drive|Jira|Bitbucket)\b' chapters/`
   and `grep -rniE '\b(HR|Legal|Marketing|Sales|Finance)\b|\b(VP|Director|Manager) of\b' chapters/`.
   If the grimoire's subject is that department, the terms are the subject
   and are fine.
4. Example names: real company, product, or person names used as examples
   outside an integration page are replaced with the generic placeholders.
5. `--arcana`: run every step against `~/grimoires/arcana/`; any violation is
   critical because Arcana must work for every domain.

Report `Magical Boundary Compliance: PASS | FAIL` with counts for magical
directories, magical terminology, platform assumptions, team buzzwords, and
example genericity (plus Arcana universality under `--arcana`); for each
violation give file, line, offending text, and the fix. Severity: critical
(magical directories in a grimoire; anything in Arcana), warning (magical
terminology or unwarranted platform or scope language in shared chapters),
info (example names that could be more generic).

## Related

- Validator detail: [[invocations/grm/validators/validators|validators]]
- Structure validator detail: [[invocations/grm/validate_structure|validate structure]]
- Parallel analysis: [[invocations/meta/subagent_lanes|subagent lanes]]
- Page schema: `ARCANA_HOME/docs/page_schema.md`
- Boundary rules: [[docs/reference|reference]]
- Bring the scaffold current: [[invocations/grm/update|update]]
