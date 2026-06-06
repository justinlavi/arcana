"""The reference.md placeholder table must match the scaffolding system's tokens.

reference.md is the canonical home for placeholder meanings (formulae/README.md),
so a placeholder used in a formula must be documented, and a documented
placeholder must actually be consumed somewhere - no phantoms.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOKEN_RE = re.compile(r"\{\{([A-Z0-9_]+)\}\}")


def _documented_tokens():
    ref = (REPO_ROOT / "docs" / "reference.md").read_text(encoding="utf-8")
    return set(re.findall(r"`\{\{([A-Z0-9_]+)\}\}`", ref))


def _template_files():
    formulae = REPO_ROOT / "formulae"
    # formulae/README.md documents the {{TOKEN}} convention; it is not a template.
    return [
        p
        for p in sorted(formulae.rglob("*"))
        if p.is_file() and p.suffix in (".md", ".json") and p != formulae / "README.md"
    ]


def _consumer_files():
    return _template_files() + [
        REPO_ROOT / "invocations" / "grimoire" / "create_grimoire.md",
        REPO_ROOT / "invocations" / "grimoire" / "add.md",
    ]


def test_every_formula_placeholder_is_documented():
    used = set()
    for path in _template_files():
        used |= set(TOKEN_RE.findall(path.read_text(encoding="utf-8")))
    missing = sorted(used - _documented_tokens())
    assert not missing, f"placeholders used in formulae but absent from reference.md: {missing}"


def test_no_phantom_placeholders_in_reference():
    consumer_text = "".join(p.read_text(encoding="utf-8") for p in _consumer_files())
    phantom = sorted(t for t in _documented_tokens() if ("{{" + t + "}}") not in consumer_text)
    assert not phantom, f"placeholders documented in reference.md but used nowhere: {phantom}"
