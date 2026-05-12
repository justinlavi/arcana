# Grimoire Operating Model

## Universal Principles

The following principles apply whether you're using Grimoire for various domains and organizations.

## What Grimoire Is
- A deterministic knowledge router for any knowledge-based tasks (code, documentation, policies, templates, processes, etc.).
- Minimal-read invariant: `INDEX.md` -> `chapters/<chapter>/INDEX.md` -> 1-2 leaf docs.
- Routers are maps; leaf docs store invariants, stable patterns, and source pointers.
- Keep canonical rules in one leaf and link to it from related docs.

## How To Route (7 Steps)
1) Start at `INDEX.md`.
2) Classify the request: which chapter does it fall into? Is it shared or scoped to a particular project / use case?
3) Follow one explicit route to `chapters/<chapter>/INDEX.md`.
4) Read one primary leaf doc (+ one related leaf only when the router says so).
5) For subject-specific work, follow the subject's chapter router (e.g. `chapters/recipes/INDEX.md` in a cooking grimoire, `chapters/onboarding/INDEX.md` in an HR grimoire).
6) For project / scope-specific overrides, route through `chapters/projects/INDEX.md` (or whatever the grimoire calls its scope folder) then the specific scope router.
7) When adding knowledge, update routers with explicit pointers; no exploratory wording.

## Scope Rules
- **Shared chapters** store rules that apply across all scopes the grimoire covers (e.g. company-wide policies in an HR grimoire, kitchen-wide techniques in a cooking grimoire).
- **Scope-specific chapters** (often under a `projects/`, `clients/`, `teams/`, or similar folder) store overrides and values that only apply to one scope.
- Never place scope-specific values in shared chapters.
- Never duplicate shared invariants in scope-specific docs — link to the shared canonical page instead.

## Templates And Snippets
- Chapter-local assets live with their chapter:
  - `chapters/<chapter>/templates/`
  - `chapters/<chapter>/snippets/`
- Use `chapters/shared/templates/` only for cross-chapter reusable assets.
- Routers should point to concrete files (not "search" instructions).
- **Templates are prescriptive standards**: they define how content should be structured across the grimoire (not drift sources).

## Content Types And Drift Management

### Core Principle
**Grimoire supports multiple authority modes.** It can route to external sources, act as canonical source of truth for domain-owned knowledge, or combine both in hybrid pages.

Implementation details owned by active code/config systems should remain externally authoritative.
Operational procedures, policy, tribal knowledge normalization, and domain standards can be authoritative in Grimoire when explicitly declared.

### Knowledge Authority Model

Every knowledge page must declare one authority model:

**External**
- Use when truth is owned outside Grimoire (repos, services, platforms).
- Page role: deterministic router + contextual guidance.
- Requires external source pointers and query-first extraction patterns.

**Grimoire**
- Use when the page itself is intended to be canonical truth for the domain.
- Page role: authoritative record in Grimoire.
- Requires explicit scope and change control.

**Hybrid**
- Use when Grimoire owns canonical synthesis while external systems still own implementation details.
- Page role: policy/process authority + external source map.
- Requires both change control and external pointers.

**How to choose**: If changing source code/config in another repo changes truth → External. If editing this page is how truth changes → Grimoire. If both → Hybrid.

### Content Type Taxonomy

**Type 1: Source Pointers (Zero Drift Risk)**
- Pure file/line references to authoritative sources
- Example: "CMake options live in `CP_Framework/CMakeLists.txt` lines 10-25"
- Validation: File exists, lines exist
- No duplication of implementation details

**Type 2: High-Level Invariants (Low Drift Risk)**
- Behavioral contracts and architectural patterns
- Example: "`configure_package()` only includes if `CMakeLists.txt` exists"
- Validation: Behavioral test (does it still work this way?)
- Rarely changes; represents stable architecture

**Type 3: Policy Documents (Low Drift Risk)**
- Domain standards and conventions
- Example: "Platform-specific code must live behind `ops` abstractions"
- Validation: Domain agreement and code review enforcement
- Changes require deliberate policy decisions

**Type 4: Observed Patterns (Medium Drift Risk)**
- Snapshots of current state with source references
- Example: "Observed brace style: Allman (as of SHA xyz)"
- Validation: SHA-stamped, must be revalidated periodically
- Must be labeled "as of [date] - VERIFY BEFORE USE"
- Include query commands to extract current values

**Type 5: Prescriptive Templates (Controlled Drift)**
- Code/CMake templates in `chapters/*/formulae/`
- These ARE the standard (not a snapshot of it)
- Purpose: Ensure consistency across projects
- Updates to templates propagate standard changes across projects
- Exception to "no source of truth" rule by design

**Type 6: Canonical Operational Knowledge (Grimoire Authority, Controlled Drift)**
- Domain-owned procedures, handover playbooks, and policy-like guidance whose source of truth is the Grimoire page
- Example: VM handover runbook that exists only in Grimoire
- Validation: Review cadence + change authority + explicit scope boundaries
- Must include change control and provenance metadata

**Type 7: FORBIDDEN (High Drift Risk)**
- Stored implementation values without query instructions
- Example: Storing `SYS_LOG_FORMAT = INLINE` without extraction command
- This type should never exist in Grimoire
- Always convert to Type 4 (Observed Patterns with queries)

### Query-First Pattern
When documenting project-specific values or configuration in **External** or **Hybrid** pages:
1. Provide bash/grep commands to extract current values from source
2. Include "Primary Sources" with exact file paths
3. Show example values labeled "as of [date] - VERIFY BEFORE USE"
4. Use query instructions that can be run to get current values

### Canonical-in-Grimoire Pattern
When documenting **Grimoire** authority pages:
1. Add explicit source-of-truth statement ("this page is canonical for X")
2. Define in-scope vs out-of-scope boundaries
3. Define change control (triggers, cadence, approval path)
4. Link external inputs as evidence only (not required as primary authority)


---
