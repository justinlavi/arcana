# Script vs AI Intelligence: Architectural Principle

**The fundamental distinction between what scripts do vs what AI does**

---

## Core Principle

**Rites (Scripts) = Simple, Deterministic Tasks**
**Invocations (AI) = Contextual, Intelligent Analysis**

As AI capabilities expand exponentially (more intelligence, parallelism, context, reasoning), the balance shifts toward AI handling increasingly complex tasks. Scripts should remain focused on what they do best: simple, fast, deterministic operations.

---

## When to Use Scripts (Rites)

### ✅ Scripts Are Perfect For:

**Data Extraction**:
- Finding files matching patterns
- Counting occurrences
- Extracting structured data from files
- Checking file/directory existence
- Measuring file sizes, line counts

**Basic Validation**:
- File format compliance (does it have required sections?)
- Naming convention enforcement (snake_case vs camelCase)
- Structural integrity (required directories exist?)
- Link syntax validation (is it a valid path format?)

**Simple Operations**:
- Running deterministic checks (shellcheck, linters)
- Executing commands and capturing output
- File system operations (create, delete, move)
- Parallel execution of independent tasks

### Examples:
```bash
# ✅ GOOD: Script finds files
find . -name "*.md" -type f

# ✅ GOOD: Script counts lines
wc -l *.sh

# ✅ GOOD: Script checks existence
[[ -f "$file" ]] || echo "Missing: $file"

# ✅ GOOD: Script validates format
grep -q "^## Purpose" "$invocation_file"
```

---

## When to Use AI (Invocations)

### ✅ AI Is Perfect For:

**Contextual Analysis**:
- Understanding semantic meaning
- Determining if terminology is used correctly
- Identifying when content is outdated or inconsistent
- Detecting subtle quality issues

**Pattern Recognition**:
- Finding duplication that isn't exact matches
- Identifying anti-patterns in documentation
- Recognizing when explanations are unclear
- Detecting organizational issues

**Judgment Calls**:
- Should this be simplified?
- Is this the right level of abstraction?
- Does this follow best practices?
- Is this explanation sufficient?

**Evolution & Improvement**:
- Suggesting better names
- Recommending structural changes
- Proposing consolidations
- Identifying missing content

### Examples:
```
❌ BAD: Script tries to validate semantics
if grep -q "Grimoire Grimoire" "$file"; then
    echo "Redundant phrasing"
fi

✅ GOOD: AI analyzes semantics
"I've reviewed all files against reference.md. The term 'Scribe'
appears in chapters/onboarding.md where 'domain lead' would be more appropriate
given the context of describing the grimoire owner role."

---

❌ BAD: Script tries to detect duplication
if diff file1.md file2.md > /dev/null; then
    echo "Duplicate files"
fi

✅ GOOD: AI detects semantic duplication
"Both README.md and INDEX.md explain 'What is a Grimoire' but with different
wording. The README version is more user-friendly, while INDEX's is more technical.
Suggest keeping README's version and having INDEX reference it."
```

---

## The Evolution Factor

**2024**: AI can analyze a few files, suggest improvements
**2025**: AI can analyze entire codebases, understand complex patterns
**2026**: AI can reason about architecture, propose refactorings
**2027+**: AI context windows and reasoning capabilities continue expanding

**Implication**: Tasks that seem too complex for AI today will be trivial tomorrow. Don't prematurely encode "intelligence" into scripts that will become obsolete.

---

## Anti-Patterns to Avoid

### ❌ Scripts Trying to Be Smart

**Problem**: Hard-coding semantic rules into bash scripts
```bash
# ❌ BAD: Script tries to understand meaning
DEPRECATED_TERMS=("Scribe" "The Keepers" "Apprentice")
for term in "${DEPRECATED_TERMS[@]}"; do
    if grep -q "$term" "$file"; then
        echo "Found deprecated term: $term"
    fi
done
```

**Why Bad**:
- Terms get removed → script becomes useless
- Doesn't understand context (term might be in historical docs, examples of what NOT to do)
- Doesn't suggest what to use instead based on context
- Doesn't learn or evolve

**Better Approach**:
```bash
# ✅ GOOD: Script extracts data
# Extract all terminology from reference
sed -n '/^## Core Concepts/,/^---$/p' docs/reference.md > /tmp/terminology.txt

# ✅ GOOD: AI analyzes using that data
/grm-domain-analyze-semantics
# AI reads reference, understands context, suggests improvements intelligently
```

### ❌ AI Doing Simple Counting

**Problem**: Using AI to count files or check existence
```
User: "How many invocation files do we have?"
AI: *reads every file, analyzes content* "You have 18 invocations..."

# ❌ BAD: AI doing what a script should do
```

**Better Approach**:
```bash
# ✅ GOOD: Script does the counting
find invocations/ -name "*.md" ! -name "INDEX.md" | wc -l
```

---

## Practical Guidelines

### For Rites (Scripts):

**DO**:
- Keep them under 150 lines (except comprehensive validators)
- Focus on one clear, simple task
- Use them for speed and consistency
- Make them idempotent and safe
- Exit codes: 0 = success, 1 = failure

**DON'T**:
- Try to understand meaning or context
- Make judgment calls about quality
- Suggest improvements (just report facts)
- Try to be intelligent or adaptive

### For Invocations (AI):

**DO**:
- Use scripts to gather data first
- Analyze the data with contextual understanding
- Make recommendations based on judgment
- Explain the reasoning behind suggestions
- Adapt to edge cases and special circumstances

**DON'T**:
- Manually count or search (use scripts for that)
- Reinvent what scripts already do
- Ignore data that scripts provide

---

## The Arcana Pattern

### Current Architecture (Correct):

```
┌─────────────────────────────────────────────┐
│  RITE: validate_structure.py                │
│  ────────────────────────────────────────   │
│  • Find required directories                │
│  • Check file existence                     │
│  • Report: ✅ or ❌                          │
│  • Exit code: 0 or 1                        │
└─────────────────────────────────────────────┘
                    │
                    │ Provides data to
                    ▼
┌─────────────────────────────────────────────┐
│  INVOCATION: improve_arcana.md            │
│  ────────────────────────────────────────   │
│  • Runs rites to gather data              │
│  • AI analyzes the results                  │
│  • AI determines if issues are real         │
│  • AI suggests specific fixes               │
│  • AI applies improvements                  │
└─────────────────────────────────────────────┘
```

### What We Avoid:

```
❌ RITE trying to be smart:
validate_semantics.py analyzing context and suggesting improvements

❌ INVOCATION doing grunt work:
AI manually checking every file instead of using find/grep
```

---

## Migration Strategy

When you find a rite trying to be intelligent:

1. **Extract the simple parts** → Keep in rite (find, count, check)
2. **Extract the smart parts** → Move to invocation (analyze, judge, suggest)
3. **Create data pipeline** → Rite provides data, invocation analyzes it

**Example**:

```bash
# BEFORE: validate_semantics.py (trying to be smart)
DEPRECATED_TERMS=("Scribe" "The Keepers")
for term in "${DEPRECATED_TERMS[@]}"; do
    # ... complex logic trying to understand context
done

# AFTER: validate_semantics.py (simple data extractor)
# Just report raw facts about what terminology exists
grep -rh -o '\b[A-Z][a-z]* [A-Z][a-z]*\b' . | sort -u > /tmp/found_terms.txt

# AFTER: analyze_semantics.md (AI analyzes intelligently)
# AI reads found_terms.txt AND reference.md
# AI understands context and suggests appropriate changes
```

---

## Future-Proofing Grimoire

**As AI evolves, tasks shift from scripts → AI:**

**2024 State**:
- Scripts: Structure validation, file finding, format checking
- AI: Semantic analysis, improvement suggestions, pattern detection

**2027+ State** (predicted):
- Scripts: Still just finding and counting
- AI: Everything requiring understanding (expanded dramatically)

**Key**: Scripts stay simple forever. AI capabilities expand indefinitely.

---

## Decision Framework

When creating new validation:

```
Ask: "Does this require understanding context and meaning?"
├─ YES → Create/enhance an INVOCATION (AI does it)
│   Examples:
│   • Is this terminology used correctly?
│   • Is this explanation clear enough?
│   • Should these be consolidated?
│   • What would be a better structure?
│
└─ NO → Create/enhance a RITE (script does it)
    Examples:
    • Does this file exist?
    • How many files match this pattern?
    • Does this follow snake_case?
    • Are these required sections present?
```

---

## Summary

| Aspect | Rites (Scripts) | Invocations (AI) |
|--------|------------------|-------------|
| **Purpose** | Simple, fast, deterministic | Contextual, intelligent, adaptive |
| **Tasks** | Find, count, check, extract | Analyze, judge, suggest, improve |
| **Context** | None needed | Essential |
| **Evolution** | Stays simple forever | Expands with AI capabilities |
| **Speed** | <1 second | Seconds to minutes |
| **Output** | Facts (✅/❌, counts, lists) | Insights (suggestions, analysis) |

**The Golden Rule**: If a human would need to think about it, AI should do it. If a computer can mechanically check it, a script should do it.

---

## Applying this to skills

Every Arcana skill delegates to one of two backing implementations:

- **Rite-backed**: `SKILL.md` body says `python3 {{ARCANA_PATH}}/rites/<name>.py`. The AI reads the skill, runs the rite, reports the rite's output. No judgment in between.
- **Invocation-backed**: `SKILL.md` body says `` `!cat {{ARCANA_PATH}}/invocations/<area>/<name>.md` ``. The AI loads the invocation guide and follows its workflow, applying judgment.

Pick by the same rule that applies to rites vs invocations themselves:

| If the skill's job is… | Pick this backing | Examples |
|---|---|---|
| Mechanical, deterministic, no judgment required | Rite-backed | `/grm-skills-register`, `/grm-catalog-sync`, `/grm-arcana-clean`, every `/grm-arcana-validate-*` |
| Conversational, judgment-driven, or multi-step exploratory | Invocation-backed | `/grm-domain-create-grimoire`, `/grm-domain-improve`, `/grm-arcana-improve`, `/grm-meta-help` |
| Both — the rite gathers data, the AI interprets | **Both, in that order**: skill body runs the rite first, then loads an invocation that reads the rite's output | `/grm-arcana-validate-semantics` could evolve into this if/when the analysis judgment grows beyond the rite's pattern check |

Two anti-patterns to avoid:

- A rite-backed skill whose body has prose instructions for the AI to interpret. If you find yourself writing "and then decide whether…" in a SKILL.md, the skill is judgment work — make it invocation-backed.
- An invocation-backed skill whose invocation just `!cat`s a script's help output. If the work is "run a thing and report the result," skip the invocation and have the skill call the rite directly.

When a skill grows beyond a thin pointer, the right response is almost always to push the new logic *down* into a rite or invocation, not *up* into the SKILL.md body. The skill stays portable across agent platforms; the invocation/rite is where complexity lives.

---


**This principle is foundational to Grimoire's architecture and should guide all future development.**
