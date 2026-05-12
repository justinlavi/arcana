# 🪄 Invocation: Create New Grimoire

## Purpose

**AI-guided conversational setup** that creates a complete grimoire from zero with minimal user input.

This invocation walks the user through creating their domain's grimoire by having a natural conversation, then automatically:
1. Creates the grimoire directory
2. Populates template files with real values
3. Suggests and creates initial chapters
4. Generates agent instruction configuration

## Invocation

Trigger with: `/grm-domain-create-grimoire` or `/grm-domain-create-grimoire`

## When to Cast

Cast this invocation when:
- You're starting a new domain and want to create your first grimoire
- Your domain has knowledge scattered across wikis, docs, and tribal knowledge
- You want AI agents to access your domain's specific knowledge
- You need to organize domain-specific information for your team
- You want to enable self-service knowledge discovery

**Time investment**: ~30 minutes for initial setup, then grows organically

---

## Non-Negotiable Rules

1. **One grimoire per domain** - Don't create multiple grimoires for the same domain
2. **Reference, don't copy** - Your grimoire references universal invocations/formulae via Arcana
3. **Practical folder names only** - Use `templates/`, `scripts/`, `snippets/` (NEVER `invocations/`, `formulae/`, `rites/`)
4. **No sensitive data** - Don't store credentials, PII, or secrets in your grimoire
5. **Pointers not duplicates** - Link to source systems, don't copy-paste documentation
6. **Clear ownership** - Designate domain members responsible for maintaining the grimoire
7. **Minimal drift** - Keep grimoire content focused on domain knowledge and reference Arcana for universal patterns

**These rules ensure your grimoire stays lightweight, maintainable, and synchronized with Arcana.**

---

## Workflow Overview

```
Step 1: Discovery (Conversational)
  ↓
Step 2: AI Suggests Chapters (Based on conversation)
  ↓
Step 3: Create Grimoire (Copy + customize template)
  ↓
Step 4: Create Chapters (Using create-chapter invocation)
  ↓
Step 5: Generate Agent Instruction Configuration
  ↓
Step 6: Validate and Test
```

---

## Step 1: Discovery Conversation (5-10 minutes)

### Goal
Gather information through natural conversation, not forms.

### AI Instructions

**Do NOT ask the user to fill out a form.** Instead, have a conversation:

1. **Start warmly**:
   ```
   "I'll help you set up a new grimoire! This will take about 10 minutes.
   Let's start with some questions so I can understand what you're building."
   ```

2. **Ask open-ended questions** (one at a time):
   - "What domain is this for?" (e.g., "Domain A", "Domain B", etc.)
   - "What are you hoping to accomplish with this knowledge base? What kind of questions should it answer?"
   - "What types of documents, processes, or knowledge does your domain work with regularly?"
   - "Are there any specific pain points or areas where your domain spends time answering the same questions over and over?"
   - "Who will be the primary users of this grimoire?"

3. **Listen and probe deeper**:
   - If they mention "onboarding" → Ask: "What parts of onboarding? Technical setup, paperwork, training?"
   - If they mention "policies" → Ask: "Which policies? PTO, remote work, expenses, all of them?"
   - If they mention "product" → Ask: "Is this for planning, specs, research, or something else?"

4. **Extract key information**:
   - **Grimoire Name**: Derive from domain (e.g., your domain name)
   - **Purpose**: Summarize in one sentence what this grimoire is for
   - **Chapter**: General category (e.g., "Domain A", "Domain B", etc.)
   - **Owner Domain**: Who maintains this (e.g., "Domain A", "Domain B")
   - **Domain Channel**: Domain's communication channel (e.g., "domain-specific channel")
   - **Skill Namespace**: Short lowercase root slug for this grimoire's skills (e.g., `oly` for Olympus, `dom` for a domain grimoire). Must match `^[a-z][a-z0-9]*$`. Ask the user explicitly: "What 2–4 letter slug should prefix this grimoire's skills? (e.g. `oly` would yield `/oly-area-verb-object` commands)"

### Output Format (Internal - Don't Show to User)

After conversation, internally structure the information as:

```yaml
grimoire_info:
  name: "Knowledge Domain"  # Full name
  directory: "grimoire_domain_a"  # Filesystem name
  token: "Domain"  # All caps token
  skill_namespace: "dom"  # Short lowercase root for domain skills
  purpose: "domain-specific knowledge and resources"
  purpose_detailed: "employee onboarding, company policies, benefits information, and performance review processes"
  chapter: "Domain"  # Category
  owner_team: "Knowledge Domain"
  team_channel: domain channel
  creation_date: "2026-03-22"  # Today's date
  example_chapter: "onboarding"  # Pick one from suggested chapters
```

---

## Step 2: AI Suggests Chapters (Based on Conversation)

### Goal
Analyze the conversation and propose 5-10 relevant chapters.

### AI Instructions

Based on what the user described, suggest chapters using this pattern:

**For Domain Example**:
```
Based on our conversation, I suggest these chapters for your Grimoire:

1. **onboarding** - New hire processes, checklists, first day/week/month guides
2. **policies** - Company policies (PTO, remote work, expenses, code of conduct)
3. **benefits** - Health insurance, 401k, perks, enrollment guides
4. **performance_reviews** - Review cycles, templates, self-assessment guides
5. **offboarding** - Exit processes, knowledge transfer, final paperwork
6. **compliance** - Legal requirements, training certifications, audits
7. **employee_handbook** - Company culture, values, guidelines

Would you like to:
- Add any of these to your grimoire? (I recommend starting with 3-5)
- Modify any chapter names or descriptions?
- Add domains I haven't suggested?
```

### Chapter Name Guidelines

- **Lowercase with underscores (snake_case)**: `user_research` not `UserResearch` or `user-research`
- **Specific, not broad**: `pto_policies` not `hr_stuff`
- **Action or topic**: `onboarding` or `performance_reviews`
- **3-10 domains initially**: Don't overwhelm with 20+ chapters

### User Interaction

Let the user:
- Select which chapters to create (at least 1, recommend 3-5)
- Rename chapters if they want
- Add custom chapters not on the list
- Provide brief descriptions for each chapter they select

### Output Format (Internal)

```yaml
selected_chapters:
  - name: "onboarding"
    description: "New hire processes, checklists, first day/week/month guides"
  - name: "policies"
    description: "Company policies (PTO, remote work, expenses, code of conduct)"
  - name: "benefits"
    description: "Health insurance, 401k, perks, enrollment guides"
```

---

## Step 3: Create Grimoire (Copy + Customize Template)

### Goal
Create the grimoire directory with customized files.

### AI Instructions

1. **Create the grimoire repository**:
   ```bash
   mkdir {{grimoire_directory}} && cd {{grimoire_directory}}
   git init
   cp ~/grimoire/arcana/formulae/grimoire/INDEX.md .
   cp ~/grimoire/arcana/formulae/grimoire/README.md .
   cp ~/grimoire/arcana/formulae/grimoire/grimoire.json .
   mkdir chapters skills
   ```

   The `grimoire.json` file is the grimoire's self-declared identity (name,
   namespace, description) — it's the canonical source for the skill namespace
   used by `/grm-skills-register`. The `skills/` directory is created empty;
   skills are added later as the grimoire grows.

2. **Customize INDEX.md**:
   Replace placeholders in `{{grimoire_directory}}/INDEX.md`:
   - `{{GRIMOIRE_NAME}}` → "Knowledge Domain"
   - `{{GRIMOIRE_TOKEN}}` → "Domain"
   - `{{GRIMOIRE_PURPOSE}}` → "domain-specific knowledge and resources"
   - `{{GRIMOIRE_DOMAIN}}` → "Domain"
   - `{{CHAPTER_ROUTES}}` → Generate from selected_chapters:
     ```markdown
     - New hire processes and checklists:
       - `chapters/onboarding/INDEX.md`
     - Company policies (PTO, remote work, expenses):
       - `chapters/policies/INDEX.md`
     - Employee benefits and enrollment:
       - `chapters/benefits/INDEX.md`
     ```

3. **Customize README.md**:
   Replace placeholders in `{{grimoire_directory}}/README.md`:
   - `{{GRIMOIRE_NAME}}` → "Knowledge Domain"
   - `{{CREATION_DATE}}` → "2026-03-22"
   - `{{OWNER_DOMAIN}}` → "Knowledge Domain"
   - `{{GRIMOIRE_DOMAIN}}` → "Domain"
   - `{{GRIMOIRE_PURPOSE}}` → "domain-specific knowledge and resources"
   - `{{GRIMOIRE_PURPOSE_DETAILED}}` → "employee onboarding, company policies, benefits information, and performance review processes"
   - `{{GRIMOIRE_DIRECTORY}}` → "grimoire_domain_a"
   - `{{SKILL_NAMESPACE}}` → "dom"
   - `{{EXAMPLE_DOMAIN}}` → "onboarding"
   - `{{DOMAIN_CHANNEL}}` → domain channel
   - `{{CHAPTER_LIST}}` → Generate from selected_chapters:
     ```markdown
     - **onboarding** - New hire processes, checklists, first day/week/month guides
     - **policies** - Company policies (PTO, remote work, expenses, code of conduct)
     - **benefits** - Health insurance, 401k, perks, enrollment guides
     ```
   - `{{CHAPTER_TREE}}` → Generate from selected_chapters:
     ```
     ├── onboarding/
     ├── policies/
     └── benefits/
     ```

3a. **Customize grimoire.json**:
   Replace placeholders in `{{grimoire_directory}}/grimoire.json`:
   - `{{GRIMOIRE_DIRECTORY}}` → "grimoire_domain_a"
   - `{{SKILL_NAMESPACE}}` → "dom" (short lowercase root, must match `^[a-z][a-z0-9]*$`)
   - `{{GRIMOIRE_PURPOSE}}` → "domain-specific knowledge and resources"

   The namespace becomes the prefix for all skills this grimoire ships
   (e.g. `dom-area-verb-object`). It must be unique across grimoires you
   plan to install side-by-side.

4. **Clean up template artifacts**:
   ```bash
   rm {{grimoire_directory}}/chapters/.gitkeep  # Will be replaced with real chapters
   ```

5. **Inform the user**:
   ```
   ✅ Created grimoire directory: {{grimoire_directory}}/
   ✅ Customized INDEX.md with your chapters
   ✅ Customized README.md with your details

   Next: Creating your selected chapters...
   ```

---

## Step 4: Create Chapters (Using create_chapter Invocation)

### Goal
Create each selected chapter using the existing create-chapter invocation.

### AI Instructions

For each chapter in `selected_chapters`:

1. **Invoke create-chapter invocation**:
   ```
   "Now creating chapter: {{domain_name}}"

   Following: GRIMOIRE_ARCANA/invocations/grimoire/create_chapter.md
   ```

2. **Auto-fill create_chapter inputs**:
   - **Chapter name**: Use from selected_chapters
   - **Purpose**: Use description from selected_chapters
   - **Starting pointers**: Ask user OR use generic placeholders ("Define during usage")
   - **Sub_topics**: Suggest 2-3 based on chapter name and description
     - For "onboarding": ["first_day", "first_week", "manager_guide"]
     - For "policies": ["pto", "remote_work", "expenses"]
     - For "benefits": ["health_insurance", "retirement", "perks"]

3. **Streamline sub_topics**:
   - Don't create full leaf docs yet (too time-consuming)
   - Create chapter INDEX.md with routing to planned sub_topics
   - Add placeholders for leaf docs:
     ```bash
     mkdir -p {{grimoire_directory}}/chapters/{{domain_name}}
     # Create INDEX.md
     # Create placeholder .md files or note TODOs in INDEX.md
     ```

4. **Update grimoire INDEX.md**:
   - Verify chapter routing is added (should already be from Step 3)

5. **Progress indicator**:
   ```
   ✅ Chapter 1/3: onboarding (created)
   ✅ Chapter 2/3: policies (created)
   ✅ Chapter 3/3: benefits (created)
   ```

---

## Step 5: Register the Grimoire

### Goal
Add the new grimoire to the user's local catalog so agents can resolve it.

### AI Instructions

1. **Check if `~/grimoire/catalog.json` exists**:
   - If it does not exist, create it with the full template below.
   - If it exists, add one entry to the `grimoires` object.

2. **Entry to add**:
   ```json
   "{{grimoire_directory}}": {
     "local_path": "$HOME/path/to/{{grimoire_directory}}",
     "online_path": null
   }
   ```
   Replace `$HOME/path/to/{{grimoire_directory}}` with the actual absolute path used in Step 3.

   **Note**: The catalog only records *where* grimoires live. The skill
   namespace is declared inside each grimoire's `grimoire.json` (set in Step 3a)
   and is read directly by the registration rite — it does not belong in the
   catalog.

3. **If creating from scratch**:
   ```json
   {
     "grimoires": {
       "{{grimoire_directory}}": {
         "local_path": "$HOME/path/to/{{grimoire_directory}}",
         "online_path": null
       }
     }
   }
   ```

4. **Check agent instruction files** — if `~/.claude/CLAUDE.md` or `~/.codex/AGENTS.md` does not already contain a `## Grimoire Knowledge Base` section, tell the user to add the canonical block from `GRIMOIRE_ARCANA/rites/templates/grimoire_block.md`. That block never changes as new grimoires are added; only the catalog does.

**Present to user**:
```
✅ Grimoire created successfully!

📋 Next Steps:

1. Catalog updated: ~/grimoire/catalog.json now includes {{grimoire_directory}} (namespace `{{skill_namespace}}` declared in {{grimoire_directory}}/grimoire.json)

2. If this is your first grimoire, add the Grimoire section to your agent instruction files
   (see GRIMOIRE_ARCANA/docs/agent_configuration.md for the block to paste)

3. Test your grimoire:
   - Ask me: "What domains exist in {{grimoire_name}}?"
   - Ask me: `/grm-domain-create-chapter [new topic]`

4. Populate your chapters:
   - Each chapter currently has an INDEX.md
   - Use `/grm-domain-create-chapter [specific topic]` to add more
   - Or manually add leaf docs using templates from GRIMOIRE_ARCANA/formulae/

Your grimoire is ready to use! 🚀
```

---

## Step 6: Validate and Test

### Goal
Verify the grimoire works correctly.

### AI Instructions

1. **Check file structure**:
   ```bash
   ls -la {{grimoire_directory}}/
   # Should show: INDEX.md, README.md, chapters/

   ls -la {{grimoire_directory}}/chapters/
   # Should show: selected chapter directories
   ```

2. **Test routing** (if the relevant agent instruction file is already updated):
   ```
   Testing: "What domains exist in {{grimoire_name}}?"
   Expected: AI reads {{grimoire_directory}}/INDEX.md and lists domains
   ```

3. **Validate placeholders replaced**:
   ```bash
   grep "{{" {{grimoire_directory}}/INDEX.md
   # Should return nothing (all placeholders replaced)

   grep "{{" {{grimoire_directory}}/README.md
   # Should return nothing (all placeholders replaced)
   ```

4. **Report results**:
   ```
   ✅ File structure valid
   ✅ All placeholders replaced
   ✅ Routing tested successfully

   Summary:
   - Grimoire: {{grimoire_directory}}/
   - Domains created: {{count}}
   - Status: Ready for use
   ```

---

## Error Handling

### If User is Unclear

**Don't give up** - probe deeper:
```
"I want to make sure I understand correctly. When you say 'policies',
do you mean Domain policies like PTO, or something else?"
```

### If User Wants Too Many Domains

**Guide them**:
```
"That's a lot of domains! I recommend starting with 3-5 and adding more later.
Which are the most urgent or frequently asked about?"
```

### If Grimoire Already Exists

**Check first**:
```bash
if [ -d "{{grimoire_directory}}" ]; then
  echo "Grimoire already exists. Use a different name or delete the existing one."
  exit 1
fi
```

### If Chapter Creation Fails

**Report and continue**:
```
⚠️ Failed to create chapter: {{domain_name}}
   Continuing with remaining domains...

   You can create it later with: /grm-domain-create-chapter {{domain_name}}
```

---

After all steps complete, run `/grm-domain-validate-structure` to confirm the grimoire passes structural checks.
