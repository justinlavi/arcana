# Arcana Governance
---

## Purpose

This document defines how **Arcana** is maintained, versioned, and updated to ensure consistency and prevent drift across all domain grimoires.

## Core Principle

**Arcana is the single source of truth for all domains.**

- All domains **reference** Arcana (not copy)
- The Arcana maintainer maintains universal content
- Updates propagate to all domains via the shared installation
- Breaking changes follow strict announcement protocol

---

## Arcana Maintainer

### Role Definition

**The Arcana maintainer** is the singular owner and maintainer of Arcana.

**Current maintainer**: [Your Name]

**Responsibilities**:
- Maintain universal invocations, formulae, rites, and documentation
- Review and approve changes to Arcana
- Version releases and maintain CHANGELOG.md
- Announce updates to all domains
- Provide migration guides for breaking changes
- Monitor domain feedback and incorporate improvements

The Arcana maintainer role can be delegated or transferred as needed; announce transitions to all domains.

---

## What Belongs in Arcana

### ✅ Arcana Content (Universal)

**Include in Arcana** if it applies to ALL departments:

- **Documentation**: README, quickstart.md, operating_model.md
- **Invocations**: base-formula, create-chapter, improve
- **Formulae**: chapter-index, knowledge-doc, invocation formulae
- **Rites**: Validation and automation scripts
- **Resources**: Branding assets (icon, logos)
- **Governance**: This file, CHANGELOG.md

### ❌ Domain-Specific Content

**DO NOT include in Arcana**:

- Domain-specific chapters (build_system, onboarding, etc.)
- Project-specific knowledge (Olympus, gcs_foundation, etc.)
- Domain-specific invocations or formulae
- Custom rites that only one domain uses

**Where it belongs**: `grimoire_{domain}/chapters/`

---

## Change Management

### Types of Changes

#### 1. Patch Updates (v1.0.0 → v1.0.1)
**Definition**: Bug fixes, typo corrections, documentation clarifications

**Process**:
- Fix the issue
- Update CHANGELOG.md
- Commit with message: `fix: [description]`
- Push to production (no announcement needed)

**Examples**:
- Fix typo in README
- Correct broken link in quickstart.md
- Bug fix in validation scripts

#### 2. Minor Updates (v1.0.0 → v1.1.0)
**Definition**: New features, new formulae, improvements (backward compatible)

**Process**:
1. Propose change (issue tracker, domain discussion, or doc)
2. The Arcana maintainer reviews (1-2 business days)
3. Approve and merge
4. Update CHANGELOG.md
5. Commit with message: `feat: [description]`
6. Announce in domain communication channel

**Examples**:
- Add new formula (api-endpoint.formula.md)
- Improve base_invocation.md with new section
- Add new invocation (refactor_chapter.md)

#### 3. Major Updates (v1.0.0 → v2.0.0)
**Definition**: Breaking changes that require domain action

**Process**:
1. Propose change with detailed justification
2. The Arcana maintainer + domain champions review (1 week)
3. Create migration guide (MIGRATION.md)
4. Announce 2 weeks in advance with migration path
5. Approve and merge
6. Update CHANGELOG.md
7. Commit with message: `BREAKING: [description]`
8. Monitor domain migrations, offer support

**Examples**:
- Change invocation formula structure (requires domains to update usage)
- Rename Arcana files (breaks existing references)
- Change router format (requires INDEX.md updates)

### Review Process

#### Patch & Minor Updates
- **Reviewer**: The Arcana maintainer
- **Timeline**: 1-2 business days
- **Approval**: Arcana maintainer approval required

#### Major Updates
- **Reviewers**: The Arcana maintainer + domain champions
- **Timeline**: 1 week discussion period
- **Approval**: Arcana maintainer approval + no blocking objections from domains
- **Migration Guide**: Required before approval

---

## Versioning

### Semantic Versioning

Arcana follows [Semantic Versioning 2.0.0](https://semver.org/):

**Format**: `MAJOR.MINOR.PATCH`

- **MAJOR** (v2.0.0): Breaking changes
- **MINOR** (v1.1.0): New features (backward compatible)
- **PATCH** (v1.0.1): Bug fixes

### Version Storage

**Current Version**: Tracked in:
- `VERSION` (single source of truth)
- `CHANGELOG.md`
- Git tags

---

## Update Announcements

- **Patch**: No announcement needed
- **Minor**: Post in domain communication channel — what's new, no action required
- **Major (Breaking)**: Domain communication channel + email to domain champions, 2-week advance notice with migration guide in CHANGELOG.md

---

## Domain Responsibilities

### What Departments Own

Each domain (`grimoire_{domain}/`) is responsible for:

1. **Creating chapters**: Using Arcana's create-chapter invocation
2. **Maintaining chapters**: Keeping knowledge fresh
3. **Validating content**: Reviewing pages for freshness regularly
4. **Reporting issues**: Bugs in Arcana invocations, formulae, or rites
5. **Providing feedback**: Suggestions for Arcana improvements

### What Departments Should NOT Do

❌ **Copy Arcana files** to their grimoire (reference instead)
❌ **Modify Arcana files** directly (propose changes via the Arcana maintainer)
❌ **Create duplicate invocations/formulae** (use Arcana's or propose additions)
❌ **Ignore Arcana updates** (at least review quarterly)

---

## Contribution Guidelines

### Proposing Arcana Improvements

Anyone can propose improvements to Arcana:

**Step 1**: Identify the need
- Does this benefit multiple domains?
- Is it universal enough for Arcana?
- Or is it domain-specific? (then add to your grimoire)

**Step 2**: Propose via one of:
- issue tracker 
- domain communication channel thread
- Direct message to the Arcana maintainer
- Document in `proposals/` (for complex proposals)

**Step 3**: Discussion
- The Arcana maintainer reviews
- Domain champions provide feedback
- Iterate on proposal

**Step 4**: Implementation
- The Arcana maintainer implements (or contributor with supervision)
- Review and approval
- Merge and version bump

### Contribution Types

**Documentation**:
- Clarifications, examples, better explanations
- No approval needed for typos/small fixes
- Larger rewrites require review

**Formulae**:
- New formulae for common chapter types
- Improvements to existing formulae
- Requires review (ensure universality)

**Invocations**:
- New automated workflows
- Improvements to existing invocations
- Requires thorough review (invocations execute code)

**Rites**:
- Validation, automation, utilities
- Requires code review + testing

---

## Arcana Update Workflow

### 1. Make Changes

```bash
cd ~/grimoires/arcana

# Create branch
git checkout -b improve/better-formula

# Make changes
vim formulae/page.formula.md

# Test changes (if applicable)
```

### 2. Update CHANGELOG.md

```markdown
## [1.1.0] - 2026-03-25

### Added
- New section in page.formula.md for "Common Mistakes"

### Changed
- Improved base_invocation.md error handling section

### Fixed
- Typo in quickstart.md step 3
```

### 3. Update Version

```markdown
# In README.md
**Version**: 1.1.0
```

### 4. Commit

```bash
git add .
git commit -m "feat: improve knowledge-doc formula with common mistakes section"
```

### 5. Review (if needed)

- Patch: Self-review OK
- Minor: 1 Arcana maintainer review
- Major: Arcana maintainer + domain champions

### 6. Merge & Tag

```bash
git tag v1.1.0
git push origin main --tags
```

### 7. Announce (if needed)

- Patch: No announcement
- Minor: domain communication channel
- Major: domain communication + email, 2 weeks advance notice

---

## Quality Standards

### Arcana Files Must

✅ **Be universal**: Apply to all domains
✅ **Be tested**: Manually tested or validated before release
✅ **Be documented**: Include clear instructions, examples
✅ **Be versioned**: Track changes in CHANGELOG.md
✅ **Be maintained**: No stale content, update as needed

### Arcana Files Must NOT

❌ **Contain hardcoded paths**: Use relative paths only
❌ **Reference domain-specific content**: Keep generic
❌ **Include secrets or credentials**: Never commit sensitive data
❌ **Duplicate external implementation details**: Link to source of truth instead
❌ **Break existing domain grimoires**: Maintain backward compatibility

---

## Deprecation Policy

### Deprecating Arcana Content

When removing or replacing Arcana content:

**Step 1**: Mark as deprecated (1 version before removal)
```markdown
## Deprecated: old_spell.md

**Status**: Deprecated in v1.5.0, will be removed in v2.0.0
**Replacement**: Use new_spell.md instead
**Migration Guide**: See CHANGELOG.md for migration details
```

**Step 2**: Announce deprecation
- Include in version announcement
- Explain why and what to use instead

**Step 3**: Remove in major version
- Delete deprecated content
- Update all references
- Document in CHANGELOG.md

**Minimum Deprecation Period**: 1 minor version (or 3 months, whichever is longer)

---

## Security & Access Control

### Arcana Repository Access

**Read Access**: All employees (public within company)
**Write Access**: Arcana maintainer only

**File Sharing Permissions**:
- Arcana repo: Read-only for all domains, write for the Arcana maintainer
- Domain grimoire root: Read/Write for domain, Read-only for others (optional)

### Secrets Management

❌ **NEVER** commit to the Arcana repo:
- API keys, passwords, tokens
- Employee names, emails, PII
- Proprietary algorithms or trade secrets
- Customer data

✅ **DO** reference where secrets live:
```markdown
## Primary Sources
- API keys: HashiCorp Vault → path/to/secrets
- Employee data: HRIS system (login required)
```

---
