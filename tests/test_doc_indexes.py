"""Doc-index coverage: routing surfaces must reference every docs/ page.

Locks the invariant that a new docs/ page is added to both the arcana.md routing
hub and the README documentation table, instead of silently drifting out of one.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def _doc_names():
    return sorted(p.name for p in (REPO_ROOT / "docs").glob("*.md"))


def test_arcana_hub_routes_to_every_doc():
    arcana = (REPO_ROOT / "arcana.md").read_text(encoding="utf-8")
    # arcana.md is a vault surface: it links docs via [[docs/<stem>|...]] wikilinks.
    missing = [name for name in _doc_names() if f"docs/{name[:-3]}" not in arcana]
    assert not missing, f"arcana.md does not route to: {missing}"


def test_readme_links_every_doc():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    # README is a public doc: it links docs via standard (docs/<name>) Markdown links.
    missing = [name for name in _doc_names() if f"docs/{name}" not in readme]
    assert not missing, f"README.md does not link: {missing}"


def test_contributing_is_reachable_from_routing_surfaces():
    arcana = (REPO_ROOT / "arcana.md").read_text(encoding="utf-8")
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "CONTRIBUTING" in arcana, "CONTRIBUTING.md not referenced from arcana.md"
    assert "CONTRIBUTING" in readme, "CONTRIBUTING.md not referenced from README.md"
