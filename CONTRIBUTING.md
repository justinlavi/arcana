# Contributing to Arcana

Thank you for your interest. Arcana is an opinionated framework with a small surface, so contributions land best when they fit the existing patterns. This guide is the fastest way to get from idea to a mergeable PR.

---

## Quick orientation

Arcana has four working layers. Almost every PR touches exactly one of them:

| Layer | What lives there | Read first |
|---|---|---|
| `docs/` | Framework documentation for humans | [docs/operating_model.md](docs/operating_model.md) |
| `formulae/` | Templates copied when scaffolding new content | [formulae/page.formula.md](formulae/page.formula.md) |
| `invocations/` | AI-guided workflow definitions referenced by skills | [invocations/meta/base_invocation.md](invocations/meta/base_invocation.md) |
| `rites/` | Python automation - validators, library sync, installer | [rites/_lib.py](rites/_lib.py) |
| `skills/` | Pointer files registered into agent skill directories | any `skills/*/SKILL.md` |

If you're unsure where a change belongs, [docs/script_vs_ai.md](docs/script_vs_ai.md) explains the rite-vs-invocation split that drives most placement decisions.

---

## Setting up a development environment

```bash
git clone https://github.com/justinlavi/arcana
cd arcana
python3 -m pip install -e '.[dev]'
```

Arcana's runtime is pure Python stdlib - no install-time dependencies. The `[dev]` extra pulls in `pytest` for the test suite. The `[gui]` and `[build]` extras are only needed for the summoning rite's GUI launcher and PyInstaller release builds respectively.

---

## Running checks before you submit

Two suites guard every PR:

```bash
# 1. Validators - structure, naming, frontmatter, links, security, etc.
python3 rites/validate.py

# 2. Test suite - unit tests covering the rites/ layer
pytest
```

Both must pass. The validators are the same ones the `/arc-validate-all` skill runs.

For faster feedback during iteration, run a single validator directly:

```bash
python3 rites/validate_frontmatter.py
python3 rites/validate_links.py
# ...etc
```

---

## Adding a new validator

Every validator should:

1. Import shared helpers from [rites/_lib.py](rites/_lib.py) - never reimplement frontmatter parsing, logging, manifest loading, or root resolution.
2. Accept `--grimoire <path>` via `add_grimoire_arg(parser)`. Default to Arcana itself; allow grimoires too.
3. Exit `0` on clean, `1` on violations. Use `info` / `ok` / `warn` / `err` from `_lib` for output.
4. Ship as a `validate_<aspect>.py` file under `rites/`.
5. Get a corresponding command-family skill folder such as `skills/arcana/validate-<aspect>/SKILL.md` or `skills/grimoire/validate-<aspect>/SKILL.md` (see [docs/skill_schema.md](docs/skill_schema.md)).
6. Be added to the orchestrator [rites/validate.py](rites/validate.py) if it is part of the Arcana validator suite so `/arc-validate-all` picks it up.
7. Get a covering test under `tests/test_validate_<aspect>.py` using the fixture grimoires under `tests/fixtures/`.

The minimal skeleton:

```python
import argparse
from _lib import add_grimoire_arg, resolve_grimoire_arg, iter_pages, warn

def main():
    parser = argparse.ArgumentParser(description="...")
    add_grimoire_arg(parser)
    args = parser.parse_args()
    root = resolve_grimoire_arg(args.grimoire)
    # ...
```

---

## Adding a new skill

Skills are pointer files. The skill itself contains no logic - it dispatches to an invocation or rite.

1. Choose the command family first: `arcana`, `grimoire`, `library`, `agent`, `workspace`, or `help`. See [docs/skill_schema.md](docs/skill_schema.md).
2. Create `skills/<family>/<slug>/SKILL.md`. The folder name is the command suffix after that family's prefix.
3. Use the `{{SKILL_PREFIX}}-<registered-slug>` template in the `name:` frontmatter - registration substitutes the command family's prefix from `arcana.json`.
4. Mirror the frontmatter fields the surrounding skills use: `description`, `when_to_use`, `user-invocable`, `allowed-tools`. Add `disable-model-invocation: true` for destructive skills.
5. Include the corresponding invocation under `invocations/` if the skill needs more than 5-10 lines of guidance.
6. Run [rites/sync_docs.py](rites/sync_docs.py) to regenerate [docs/skills.md](docs/skills.md).

---

## Documentation changes

- Each concept has one canonical home. Storage layers live in [docs/operating_model.md](docs/operating_model.md), the page schema lives in [docs/page_schema.md](docs/page_schema.md), and so on. Other docs link rather than duplicate.
- Knowledge-routing markdown carries YAML frontmatter - see [docs/page_schema.md](docs/page_schema.md). [rites/validate_frontmatter.py](rites/validate_frontmatter.py) enforces it for `docs/`, `invocations/`, `formulae/`, `chapters/`, and grimoire root hubs. GitHub-facing root files such as `README.md`, `CONTRIBUTING.md`, and `CHANGELOG.md` are exempt unless Arcana explicitly adopts frontmatter for them.
- Every folder has a hub file named after the folder. New folders need a new hub.
- Internal links use markdown for cross-doc references and full-path `[[wikilinks]]` for hub-internal navigation. [rites/validate_links.py](rites/validate_links.py) checks both.

---

## Code style

- Pure Python stdlib. Don't reach for third-party libraries; if you find yourself wanting one, open an issue first.
- Snake_case for `.py` and `.md` paths (validator-enforced). Kebab-case for skill folder names and slash-command identifiers.
- No comments restating what the code does - only the *why* when non-obvious.
- Keep new files small. If you find yourself writing a 500-line validator, look for what belongs in [rites/_lib.py](rites/_lib.py) instead.

---

## Pull request expectations

- One concern per PR. Mixing a doc rewrite with a validator change makes review hard.
- Update [CHANGELOG.md](CHANGELOG.md). Before the current version is tagged as final, edit that version's entry in place; after a final tag, collect new changes under `## [Unreleased]`.
- Bump [VERSION](VERSION) only as part of an explicit release PR.
- If you touched user-facing behavior, mention what a downstream grimoire owner has to do to adopt the change.

---

## Reporting issues

- For bugs: include the validator output, your Arcana version (`cat VERSION`), and Python version.
- For terminology or design questions: link the existing doc that confused you so it can be improved.
- For new features: describe the use case before proposing an implementation. Arcana intentionally has a small surface and bias-to-shrink - additions need a clear earned-its-keep story.

---

## Maintainer notes

The `/arc-improve` and `/arc-validate-all` skills are the canonical maintenance entry points. Run them before tagging a release. Release workflow lives in [docs/release.md](docs/release.md).
