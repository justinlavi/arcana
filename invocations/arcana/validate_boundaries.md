# 🔍 Invocation: Validate Magical Boundaries

## ⚡ Purpose

Enforce the magical boundary between Grimoire's system (magical) and content (practical) to maintain clarity and prevent confusion.

This invocation validates:
- Magical terms stay in system operations only
- No `invocations/`, `formulae/`, `rites/` in domain grimoires
- No platform-specific language (Slack, SharePoint, Teams)
- No team/department buzzwords (HR, Marketing, Legal, Sales)
- Examples use generic names only
- Arcana remains universally applicable

**This invocation is safe to rerun at any time.**

---

## When to Invoke

- Before publishing grimoire to other domains
- After adding new chapters or content
- During code review of Grimoire updates
- Quarterly as part of quality validation
- Before releasing Arcana updates (maintainer)

---

## Invocation

From your domain grimoire's root directory, invoke:

```
/grm-arcana-validate-boundaries
```

Or for Arcana:

```
/grm-arcana-validate-boundaries --arcana
```

---

## What This Invocation Does

### Phase 1: Magical Contamination Check

**Detects magical terminology in practical content:**

#### ❌ Forbidden Magical Directories in Domain Grimoires

Domain grimoires must NOT contain:
- `invocations/` (only in Arcana)
- `formulae/` (only in Arcana)
- `rites/` (only in Arcana)

**Allowed practical alternatives:**
- `templates/` ✅ (not formulae)
- `scripts/` ✅ (not rites)
- `snippets/` ✅
- `configs/` ✅
- `policies/` ✅
- `guides/` ✅

#### ❌ Magical Terms in Chapter Content

Magical terms should NOT appear in chapter docs or leaf pages:
- "Perform the invocation" → "Execute the command"
- "Consult the formula" → "Reference the template"
- "Perform the rite" → "Run the script"

**Exception**: References to Arcana itself are allowed:
- ✅ "Use `/grm-improve` to optimize the grimoire"
- ✅ "See Arcana for universal invocations"

---

### Phase 2: Platform Assumption Check

**Detects platform-specific language that should be generic:**

Scans for platform-specific terms across three categories:

- **Communication**: Slack, Teams, Discord, etc. -> "domain communication channel"
- **Storage**: SharePoint, Confluence, Google Drive, etc. -> "document repository", "cloud storage"
- **Development**: GitHub, Jira, Bitbucket, etc. -> "version control system", "issue tracker"

> Full terminology mapping: `GRIMOIRE_ARCANA/docs/reference.md` (Magical Boundary section)

#### ✅ Allowed Platform References

Platform names ARE allowed when:
- Documenting actual integration (e.g., "GitLab CI configuration")
- In project-specific chapters (not shared chapters)
- As one example among multiple: "e.g., Slack, Teams, or Discord"

---

### Phase 3: Team Buzzword Check

**Detects team/department names that should be generic:**

Scans for department names and role titles that should be generic:

- **Departments**: HR, Legal, Marketing, Sales, Finance, IT, etc. -> "Domain A", "Knowledge Domain", "your domain"
- **Roles**: "HR Manager", "VP of Engineering", etc. -> "domain lead", "contributor", "knowledge owner"

> Full terminology mapping: `GRIMOIRE_ARCANA/docs/reference.md` (Magical Boundary section)

#### ✅ Allowed in Project-Specific Content

Department names ARE allowed in:
- `chapters/projects/` (project-specific overrides)
- Project router documentation
- When documenting actual organizational structure

---

### Phase 4: Example Name Check

**Validates that examples use generic, non-identifying names:**

#### ❌ Real Company/Product Names

**Forbidden**: Real company names, product names, person names, or project codenames (unless documenting actual integration or tool-specific documentation).

#### ✅ Generic Example Names

Use placeholder patterns: `Domain A`, `Project Alpha`, `Alice/Bob`, `System A`, or `{Your Domain}` / `{Your Project}` / `{Your System}`.

---

### Phase 5: Arcana Universality Check

**Ensures Arcana contains ZERO domain-specific content.** Applies Phases 1-4 at the strictest level: no specific domains, no platform assumptions, no hardcoded paths, no environment assumptions.

> For full Arcana improvement workflows, see `/grm-arcana-improve`.

#### ❌ Common Arcana Violations:

- "Deploy to SharePoint" -> "Deploy to cloud storage"
- "Share in #engineering" -> "Share in domain channel"
- "For HR teams" -> "For knowledge management domains"
- "VP approval required" -> "Domain lead approval required"

---

## Deliverables

### 1. Boundary Validation Report

Contains:

#### Overall Status
```
Magical Boundary Compliance: PASS ✅ | FAIL ❌

- Magical contamination:    N violations
- Platform assumptions:     N violations
- Team buzzwords:           N violations
- Example genericity:       PASS/FAIL
- Arcana universality:   PASS/FAIL
```

#### Example Violations (one per severity)

```
🔴 CRITICAL: Magical directories in domain grimoire

File: olympus-grimoire/invocations/custom_build.md
Issue: Domain grimoire contains "invocations/" directory
Fix: Rename to "scripts/" or move to Arcana
```

```
🟡 WARNING: Magical terminology in practical content

File: chapters/build_system/cmake.md:156
Text: "Invoke this to configure CMake"
Fix: "Run this command to configure CMake"
```

```
🟢 INFO: Generic example could be clearer

File: chapters/projects/atlas.md:12
Text: "Project Alpha uses this pattern"
Suggestion: "{Your Project} uses this pattern"
```

### 2. Quick Fix Script (auto-generated)

When run with `--fix`, the invocation generates a `sed`-based shell script to apply simple text replacements. Review before executing.

---

## Detection Patterns

### Pattern: Magical Directory Detection

```bash
# Scan for forbidden directories in domain grimoires
find GRIMOIRE_{DOMAIN}/ -type d -name "invocations" -o -name "formulae" -o -name "rites"
```

### Pattern: Platform Language Detection

```bash
# Search for platform-specific terms
grep -r "Slack\|SharePoint\|Confluence\|Teams\|Discord" chapters/
```

### Pattern: Team Buzzword Detection

```bash
# Search for department/role names
grep -ri "\bHR\b\|Legal\|Marketing\|Sales\|Finance" chapters/
```

### Pattern: Magical Term in Content

```bash
# Find magical language in practical content
grep -r "invoke.*invocation\|consult.*formula\|perform.*rite" chapters/
```

---

## Common Boundary Violations

### Violation: Magical Folders in Domain Grimoire

**Before**:
```
GRIMOIRE_MYTEAM/
├── chapters/
├── invocations/              ❌ Wrong!
│   └── deploy.md
└── formulae/             ❌ Wrong!
    └── k8s-template.yml
```

**After**:
```
GRIMOIRE_MYTEAM/
├── chapters/
├── scripts/             ✅ Correct
│   └── deploy.sh
└── templates/           ✅ Correct
    └── k8s-template.yml
```

---

### Violation: Platform Assumptions

**Before**:
```markdown
Share your changes in the #engineering-team Slack channel
and upload documentation to the SharePoint site.
```

**After**:
```markdown
Share your changes in the engineering domain communication channel
and upload documentation to the shared document repository.
```

---

### Violation: Team Buzzwords in Universal Content

**Before** (in Arcana):
```markdown
- **HR Teams**: Onboarding policies, employee handbooks
- **Marketing**: Brand guidelines, campaign templates
```

**After**:
```markdown
- **Policy Domains**: Onboarding guides, organizational handbooks
- **Brand Domains**: Visual standards, campaign frameworks
```

---

### Violation: Magical Language in Chapter Content

**Before**:
```markdown
# CMake Configuration

To configure your build, run the cmake-configure invocation:

`/grm-help`
```

**After**:
```markdown
# CMake Configuration

To configure your build, run the configuration command:

`cmake -B build -S .`

(Or use `/grm-help` for available Grimoire skills)
```

---

## Boundary Enforcement Levels

### Level 1: Arcana (Strictest)

**Arcana must be:**
- ✅ 100% generic (no specific domains/platforms)
- ✅ 100% universal (works anywhere)
- ✅ 0 violations allowed

**Violations in Arcana are ALWAYS critical.**

### Level 2: Domain Grimoires - Shared Chapters (Strict)

**Shared chapters (not in `chapters/projects/`) must:**
- ✅ Use generic examples
- ✅ Avoid platform-specific language where possible
- ✅ Use magical terminology correctly

**Violations in shared chapters are critical or warnings.**

### Level 3: Domain Grimoires - Project Chapters (Relaxed)

**Project-specific chapters (`chapters/projects/`) can:**
- ✅ Mention specific platforms if project uses them
- ✅ Reference actual teams/departments
- ✅ Use real project names

**Violations in project chapters are warnings or info.**

---

## Integration with Other Invocations

This invocation is automatically invoked by:

- `/grm-improve` - Validates boundaries in Phase 3.5
- `/grm-arcana-improve` - Ensures Arcana universality
- `/grm-create-grimoire` - Validates new grimoires at creation

Can be run standalone:

- `/grm-arcana-validate-boundaries` - Full validation
- `/grm-arcana-validate-boundaries --fix` - Apply automated fixes
- `/grm-arcana-validate-boundaries --strict` - Zero tolerance mode

---

## Tips

- **Magical language**: only when talking ABOUT Arcana, invocations, formulae, rites, or `/grm-*` skills. Never in chapter content, templates, or code examples.
- **Generic names**: always in Arcana and shared chapters. Specific names only in `chapters/projects/`, actual configs, and integration docs.

---

## Related Invocations

- Semantic clarity check: `/grm-analyze-semantics`
- Structure validation: `/grm-improve`
- Full grimoire improvement: `/grm-improve`
- Arcana evolution: `/grm-arcana-improve` (maintainer)

---

