"""Doc-index coverage: routing surfaces must reference every docs/ page.

Locks the invariant that a new docs/ page is added to both the arcana.md routing
hub and the README documentation table, instead of silently drifting out of one.

The check itself lives in `validate_structure.doc_index_violations` so the
runtime validator (`/arc-validate-structure`, `/arc-validate-all`) and these
tests share one implementation; these tests assert it stays clean on the live
Arcana tree.
"""

import validate_structure

ROOT = validate_structure.ARCANA_ROOT


def _paths(code=None, path=None):
    return [
        viol_path
        for viol_code, viol_path, _ in validate_structure.doc_index_violations(ROOT)
        if (code is None or viol_code == code) and (path is None or viol_path == path)
    ]


def test_arcana_hub_routes_to_every_doc():
    missing = _paths(code="STRUCTURE_DOC_NOT_IN_HUB")
    assert not missing, f"arcana.md does not route to: {missing}"


def test_readme_links_every_doc():
    missing = _paths(code="STRUCTURE_DOC_NOT_IN_README")
    assert not missing, f"README.md does not link: {missing}"


def test_contributing_is_reachable_from_routing_surfaces():
    missing = _paths(path="CONTRIBUTING.md")
    assert not missing, f"CONTRIBUTING.md is not referenced from: {missing}"
