"""stage_publish.py flattens a grimoire into a generator content tree; audit_publish.py guards the boundary."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RITES = REPO_ROOT / "rites"
GOOD = Path(__file__).parent / "fixtures" / "good_grimoire"


def _run(script: str, root: Path, *extra: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(RITES / script), "--grimoire", str(root), "--format", "json", *extra],
        capture_output=True, text=True, timeout=120,
    )
    return {"returncode": result.returncode, "report": json.loads(result.stdout), "stderr": result.stderr}


def _grimoire(tmp_path: Path) -> Path:
    root = tmp_path / "good_grimoire"
    shutil.copytree(GOOD, root)
    recipes = root / "chapters" / "recipes"
    (recipes / "sources").mkdir(exist_ok=True)
    (recipes / "sources" / "card.pdf").write_bytes(b"%PDF-1.4 fixture")
    (recipes / "templates").mkdir(exist_ok=True)
    (recipes / "templates" / "card_template.md").write_text("# template\n", encoding="utf-8")
    (recipes / "sourdough.md").write_text(
        "---\ntype: concept\ntitle: \"Sourdough\"\naliases: [\"sourdough\", \"levain\"]\ntags: [chapter/recipes, type/concept]\n"
        "authority: hybrid\nsources:\n  - chapters/recipes/sources/card.pdf\nlast_verified: 2026-11-12\n---\n\n# Sourdough\n\n"
        "Back to [[chapters/recipes/recipes|recipes]] and the [[good_grimoire|hub]]. The card is [here](sources/card.pdf).\n",
        encoding="utf-8", newline="\n",
    )
    return root


def test_stage_plan_writes_nothing_and_apply_flattens(tmp_path):
    root = _grimoire(tmp_path)
    plan = _run("stage_publish.py", root)
    assert plan["returncode"] == 0 and plan["report"]["status"] == "noop"
    assert not (root / "publish" / "content").exists()

    out = _run("stage_publish.py", root, "--apply")
    assert out["returncode"] == 0, out
    content = root / "publish" / "content"
    assert (content / "index.md").is_file()
    assert (content / "recipes" / "sourdough.md").is_file()
    assert (content / "recipes" / "sources" / "card.pdf").is_file()
    assert not (content / "chapters").exists()
    assert not (content / "recipes" / "templates").exists()  # asset folders are authoring scaffolding
    assert not list(content.rglob(".gitkeep"))

    page = (content / "recipes" / "sourdough.md").read_text(encoding="utf-8")
    assert "[[recipes/recipes|recipes]]" in page
    assert "[[index|hub]]" in page
    assert "- recipes/sources/card.pdf" in page
    assert "(/recipes/sources/card.pdf)" in page
    assert 'aliases: ["levain"]' in page  # the self-alias is dropped
    assert out["report"]["mutations"][0]["action"] == "stage"


def test_stage_honours_exclusions_and_refuses_content_outside_publish(tmp_path):
    root = _grimoire(tmp_path)
    (root / "publish" / "publish.json").write_text(json.dumps({"exclude": ["chapters/recipes/sources"]}), encoding="utf-8")
    out = _run("stage_publish.py", root, "--apply")
    assert out["returncode"] == 0
    assert not (root / "publish" / "content" / "recipes" / "sources").exists()

    (root / "publish" / "publish.json").write_text(json.dumps({"content_dir": "chapters/staged"}), encoding="utf-8")
    refused = _run("stage_publish.py", root, "--apply")
    assert refused["returncode"] == 1 and refused["report"]["status"] == "blocked"


def test_audit_passes_a_clean_stage_and_blocks_secrets(tmp_path):
    root = _grimoire(tmp_path)
    _run("stage_publish.py", root, "--apply")
    clean = _run("audit_publish.py", root)
    assert clean["returncode"] == 0, clean
    codes = [d["code"] for d in clean["report"]["diagnostics"]]
    assert "PUBLISH_BLOCKER" not in codes
    assert "PUBLISH_WARNING" in codes  # the published PDF is a warning behind access control

    content = root / "publish" / "content"
    (content / "recipes" / "leak.md").write_text(
        "# leak\n\npassword: hunter2\n\nCard 4111 1111 1111 1111 on file.\n", encoding="utf-8"
    )
    dirty = _run("audit_publish.py", root)
    assert dirty["returncode"] == 1
    blockers = [d["message"] for d in dirty["report"]["diagnostics"] if d["code"] == "PUBLISH_BLOCKER"]
    assert any("password-or-credential" in m for m in blockers)
    assert any("payment card" in m for m in blockers)


def test_audit_known_identifier_patterns_and_custom_warnings(tmp_path):
    root = _grimoire(tmp_path)
    (root / "publish" / "publish.json").write_text(json.dumps({
        "audit": {
            "warning_patterns": {"booking-reference": r"\brecord locator\b"},
            "known_identifier_patterns": [r"rooms/{digits}\b"],
        }
    }), encoding="utf-8")
    _run("stage_publish.py", root, "--apply")
    content = root / "publish" / "content"
    (content / "recipes" / "stay.md").write_text(
        "# stay\n\nListing https://example.com/rooms/4111111111111111 and the record locator ABC123.\n", encoding="utf-8"
    )
    out = _run("audit_publish.py", root)
    assert out["returncode"] == 0, out
    messages = [d["message"] for d in out["report"]["diagnostics"]]
    assert any("booking-reference" in m for m in messages)
    assert not any("payment card" in m for m in messages)


def test_audit_blocks_authoring_roots_and_unresolved_sources(tmp_path):
    root = _grimoire(tmp_path)
    _run("stage_publish.py", root, "--apply")
    content = root / "publish" / "content"
    (content / "inbox").mkdir()
    (content / "inbox" / "note.md").write_text("# x\n", encoding="utf-8")
    (content / "recipes" / "sourdough.md").write_text(
        "---\ntype: concept\ntitle: \"Sourdough\"\nsources:\n  - recipes/sources/missing.pdf\n---\n\n# Sourdough\n", encoding="utf-8"
    )
    out = _run("audit_publish.py", root)
    assert out["returncode"] == 1
    blockers = [d["message"] for d in out["report"]["diagnostics"] if d["code"] == "PUBLISH_BLOCKER"]
    assert any("authoring root staged" in m for m in blockers)
    assert any("unresolved-frontmatter-source" in m for m in blockers)


def test_audit_missing_target_exits_two(tmp_path):
    root = _grimoire(tmp_path)
    out = _run("audit_publish.py", root, "--target", str(tmp_path / "nowhere"))
    assert out["returncode"] == 2


def test_stage_resolves_the_root_hub_from_the_manifest_in_a_ci_checkout(tmp_path):
    root = tmp_path / "repo"  # a CI runner's checkout name, not the grimoire's
    shutil.copytree(GOOD, root)
    out = _run("stage_publish.py", root, "--apply")
    assert out["returncode"] == 0, out
    index = (root / "publish" / "content" / "index.md").read_text(encoding="utf-8")
    assert index.startswith("---")
