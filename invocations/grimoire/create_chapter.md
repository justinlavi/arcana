# 🪄 Invocation: Create Your First Grimoire Chapter

## ⚡ The Magical Boundary ⚡

**Use magical language** when describing Grimoire operations:
- "Cast this invocation to create a new chapter in your grimoire"
- "Consult Arcana for formula templates"

**Use practical language** for chapter content:
- File/folder names inside chapters: `templates/`, `scripts/`, `snippets/`, `policies/`, `guides/`
- **NEVER** create `invocations/`, `formulae/`, or `rites/` folders in your domain grimoire
- These exist **only** in Arcana for universal Grimoire operations
- Keep content searchable and domain-appropriate for your domain

**Remember**: The magic is in the system, not the content.

---

## Purpose

Guide you through creating a well-structured knowledge chapter in your domain's grimoire.

## Invocation

```
/grm-create-chapter
```

Or provide a topic directly:
```
/grm-create-chapter for [topic]
```

## When to Use

- You've identified a knowledge area your domain frequently asks about
- You want to make that knowledge accessible to AI agents
- You have source documents, wikis, or tribal knowledge to organize

## Preconditions

Before executing, verify the current working directory is a registered domain grimoire (check `~/grimoire/catalog.json`). If it is not, list available grimoires and tell the user to `cd` to one. Arcana is not a grimoire. **Stop** if the check fails.

## Prerequisites

- You've completed `docs/quickstart.md`
- You have write access to your domain's Grimoire folder (file sharing platform or local copy)
- You've identified a chapter name (e.g., "onboarding", "expense-policies", "prd-templates")

## Step-by-Step Process

### Step 1: Choose a Chapter Name (5 minutes)

**Good chapter names are**:
- **Specific**: "onboarding" not "hr-stuff"
- **Searchable**: "prd-templates" not "product-docs"
- **Scope-appropriate**: "employee-benefits" not "all-hr-things"
- **Hyphen-separated**: "expense-policies" not "expense_policies" or "ExpensePolicies"

**Examples by Domain**:
- Engineering: `code-standards`, `build_system`, `ci-cd-pipeline`
- Domain: `onboarding`, `performance-reviews`, `pto-policies`
- Product: `prd-templates`, `user-research`, `roadmap-planning`
- Compliance: `contract-templates`, `compliance-checklists`, `ip-guidelines`

**Your chapter name**: `_______________________`

### Step 2: Identify Knowledge Sources (10 minutes)

List where the truth currently lives for this chapter:

**Examples**:
- Wiki pages: `https://wiki.company.com/hr/onboarding`
- Shared drives: `file sharing platform/Domain/Onboarding Docs/`
- Email threads: "New Hire Checklist v3.pdf"
- Tribal knowledge: "Ask Sarah in Domain"
- Templates: `Google Drive/Templates/PRD Template.docx`

**Your sources**:
1. `_______________________`
2. `_______________________`
3. `_______________________`

### Step 3: Define Scope and Sub-Topics (10 minutes)

What sub-topics belong in this chapter?

**Example: `onboarding` chapter**:
- First day checklist
- First week checklist
- 30-60-90 day plan
- Manager responsibilities
- IT setup tasks
- Benefits enrollment

**Your sub-topics**:
1. `_______________________`
2. `_______________________`
3. `_______________________`
4. `_______________________`

### Step 4: Create Chapter Folder Structure (5 minutes)

In your Grimoire directory:

```bash
cd chapters/
mkdir [chapter-name]
cd [chapter-name]
```

Copy the chapter INDEX template:

```bash
cp ../../formulae/chapter_index.formula.md INDEX.md
```

### Step 5: Write Chapter INDEX.md (10 minutes)

Edit `chapters/[chapter-name]/INDEX.md`:

1. **Replace placeholders**:
   - `[Chapter Name]` → Your chapter name in title case
   - `[purpose]` → One sentence: what this chapter covers
   - `[when to use]` → When should AI route here?

2. **Add routing pointers** for each sub-topic:
   ```markdown
   - First day checklist → first_day.md
   - First week checklist → first_week.md
   - Manager responsibilities → manager_guide.md
   ```

3. **Save the file**

**Example**:
```markdown
# Onboarding Chapter

## Purpose
Knowledge about new hire onboarding process, checklists, and requirements.

## When to Use
Route here for questions about:
- New hire setup and first day/week/month
- Manager onboarding responsibilities
- IT provisioning and access
- Benefits enrollment process

## Routes
- First day checklist → first_day.md
- First week checklist → first_week.md
- 30-60-90 day plan → 30_60_90.md
- Manager onboarding guide → manager_guide.md
- IT setup requirements → it_setup.md
```

### Step 6: Create Leaf Docs (30 minutes)

For each sub-topic, copy the page template:

```bash
cp ../../formulae/page.formula.md first_day.md
```

Edit the template:
1. **Purpose**: What this doc covers
2. **When to use**: When to read this
3. **Primary Sources**: Include when referencing external files/repos/systems
4. **Content sections**: Name them based on what the page covers (Invariants, Standard Patterns, Rules, etc.)
5. **Gotchas**: Common mistakes, edge cases
6. **Related docs**: Links to other Grimoire docs

3. **Content strategy**:
   - **DO**: Use query-first extraction for External/Hybrid drift-sensitive values
   - **DO**: Use explicit "source of truth statement" for Grimoire canonical pages
   - **DO**: Provide example values labeled "as of [date] - VERIFY BEFORE USE" when snapshotting external state
   - **DON'T**: Force fake external pointers for Grimoire-canonical knowledge
   - **DON'T**: Store implementation values without query instructions
   - **DON'T**: Duplicate knowledge from other chapters (link to it)

Repeat for each sub-topic.

### Step 7: Update Root INDEX.md (5 minutes)

Add your new chapter to the root router:

Edit `INDEX.md` in your Grimoire root:

Find the "Route By Chapter" section and add:
```markdown
- [Your chapter description]:
  - `chapters/[chapter-name]/INDEX.md`
```

**Example**:
```markdown
## Route By Chapter
- New hire onboarding process and checklists:
  - `chapters/onboarding/INDEX.md`
- Employee benefits and compensation:
  - `chapters/benefits/INDEX.md`
```

Save the file.

### Step 8: Test Your Chapter (10 minutes)

Ask your AI agent a question that should route to your new chapter:

**Examples**:
- "What's on the first day checklist for new hires?"
- "How do I create a PRD?"
- "What's the expense reimbursement policy?"

**Verify routing**:
1. AI should read root `INDEX.md`
2. AI should route to `chapters/[chapter-name]/INDEX.md`
3. AI should read the appropriate leaf doc
4. AI should provide accurate answer

**If it doesn't work**:
- Check INDEX.md has explicit pointer
- Verify file names match exactly (case-sensitive)
- Check for typos in paths
- Ensure leaf docs have content (not just formulae)

### Step 9: Publish (5 minutes)

**If using file sharing platform**:
1. Upload your new chapter folder to file sharing platform
2. Verify permissions (domain has read access)
3. Test that URLs work

**If using Git**:
1. Commit and push:
   ```bash
   git add chapters/[chapter-name] INDEX.md
   git commit -m "Add [chapter-name] chapter"
   git push
   ```

**Announce to your domain**:
- Post in Domain communication: "New Grimoire chapter: [chapter-name]"
- Share example questions it can answer
- Invite feedback and contributions

### Step 10: Iterate and Improve (Ongoing)

Your chapter is a living document. Plan to:
- **Monthly**: Verify links and sources still work
- **Quarterly**: Validate metadata is current
- **When policies change**: Update leaf docs immediately
- **When usage grows**: Add more sub-topics as needed

## Success Criteria

Your chapter is successful if:
- ✅ AI can answer questions about this topic in <5 seconds
- ✅ Answers are accurate and match source systems
- ✅ Domain members use it regularly
- ✅ Reduces repetitive questions to subject matter experts
- ✅ New domain members can self-serve onboarding

## Common Pitfalls

### Pitfall 1: Too Broad
**Problem**: Chapter covers too many unrelated topics
**Solution**: Split into multiple focused chapters

### Pitfall 2: Duplicate Content
**Problem**: Copy-pasting from wikis creates drift
**Solution**: Point to sources, don't duplicate

### Pitfall 3: Stale Content
**Problem**: Docs become outdated, AI gives wrong answers
**Solution**: Add metadata, set review schedule, use query patterns

### Pitfall 4: No Clear Entry Point
**Problem**: Root INDEX doesn't mention this chapter
**Solution**: Always update root INDEX when creating chapter

### Pitfall 5: Over-Engineering
**Problem**: Creating complex sub-chapters before you need them
**Solution**: Start simple (1 INDEX + 2-3 leaf docs), expand as usage grows

## Next Steps

After creating your chapter:
1. Monitor usage (ask your domain to try it)
2. Collect feedback (what works, what's missing)
3. Iterate (add sub-topics, improve routing)
4. Share with other domains (inspire cross-pollination)
5. Consider creating a custom invocation (see `formulae/invocation.formula.md`)

## Questions?

- Domain communication: #grimoire_users
- Read: `docs/operating_model.md` for principles
- Review: `formulae/` for more examples
