# Grimoire Quickstart Guide

Get started with Grimoire in 10 minutes.

---

## Prerequisites

- Access to Arcana
- Access to your domain's grimoire
- AI agent (Claude, ChatGPT, etc.)
- Basic markdown knowledge

---

## Step 1: Verify Access

### Local Filesystem

Navigate to your domain's grimoire root:
```bash
cd /path/to/{your-domain-grimoire}
ls -la
# Should see: INDEX.md, README.md, chapters/
```

Verify Arcana is installed:
```bash
ls -la ~/grimoire/arcana/
# Should see: INDEX.md, invocations/, formulae/, rites/, docs/
```

---

## Step 2: Configure AI Agent

Add the Grimoire configuration to your AI agent. See [docs/agent_configuration.md](agent_configuration.md) for:
- Configuration template
- Examples for Claude, ChatGPT, GitHub Copilot
- Cloud storage vs. local filesystem setup

---

## Step 3: Test Setup

Ask your AI agent:

> "Read the Grimoire README and summarize it"

**Expected**:
1. AI reads `README.md` from your domain grimoire
2. AI provides summary

---

## Step 4: Create Test Chapter (Optional)

Create a test chapter to verify routing:

```bash
mkdir -p chapters/test
cp ~/grimoire/arcana/formulae/chapter_index.formula.md chapters/test/INDEX.md
```

Edit `chapters/test/INDEX.md`:
- Replace placeholders with "Test Chapter"
- Add route: `- Hello world → hello.md`

Create `chapters/test/hello.md`:
```markdown
# Hello World

Test knowledge document.

**Test**: Ask AI "What's in the test chapter?"
```

Update root `INDEX.md` to add:
```markdown
- Test chapter: `chapters/test/INDEX.md`
```

Test:
> "What's in the Grimoire test chapter?"

AI should route: INDEX.md → chapters/test/INDEX.md → chapters/test/hello.md

---

## Troubleshooting

**AI can't read INDEX.md**
- **Cloud**: Check read permissions
- **Local**: Verify file path in configuration

**AI reads INDEX.md but doesn't route to chapter**
- Verify INDEX.md has explicit pointer (e.g., `chapters/test/INDEX.md`)
- Check chapter folder exists with INDEX.md
- Check for typos in paths

**AI reads files but doesn't find answer**
- Knowledge may not exist yet - create it
- Knowledge exists elsewhere - add pointer to Grimoire

**Slow routing (>5 seconds)**
- **Cloud**: Network latency, acceptable
- **Local**: Should be <1 second; check disk performance

**Still stuck?**
- Domain communication: #grimoire_users
- Include: Error message, file paths, expected vs actual behavior

---

## Next Steps

**Create chapters** for frequently asked topics:
- Use `/grm-create-chapter [topic]`
- See [invocations/grimoire/create_chapter.md](../invocations/grimoire/create_chapter.md)

**Learn routing model**:
- Read [docs/operating_model.md](operating_model.md)

**Browse templates**:
- Chapter template: `formulae/chapter_index.formula.md`
- Page template: `formulae/page.formula.md`

---
