"""Tests for restructure_grimoire (move/rename + remove).

Each test builds a small grimoire in a temp dir and drives the operation
helpers directly, so nothing touches a real grimoire.
"""

from pathlib import Path

from diagnostics import ResultReporter

import restructure_grimoire as R


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _grimoire(tmp_path: Path) -> Path:
    """A grimoire with a `guide` chapter (hub + leaf + sub-chapter) and a cross-link."""
    root = tmp_path / "g"
    _write(root / "chapters/guide/guide.md",
           "links: [[chapters/guide/intro|Intro]] and [[chapters/guide/setup/setup|Setup]]\n")
    _write(root / "chapters/guide/intro.md",
           "see [[chapters/guide/setup/setup|Setup]] and `[[chapters/guide/intro|self]]`\n")
    _write(root / "chapters/guide/setup/setup.md",
           "back to [[chapters/guide/intro#Start|Intro]]\n")
    _write(root / "chapters/other/other.md",
           "cross to [[chapters/guide/intro|Intro]]\n")
    return root


def _reporter(root: Path, apply: bool) -> ResultReporter:
    return ResultReporter("restructure_grimoire", root=root, mode="apply" if apply else "plan")


# ---------------------------------------------------------------------------
# move
# ---------------------------------------------------------------------------


def test_move_page_rename_rewrites_links(tmp_path):
    root = _grimoire(tmp_path)
    rc = R.do_move(root, "chapters/guide/intro.md", "chapters/guide/overview.md",
                   apply=True, reporter=_reporter(root, True), human=False, fmt="json")
    assert rc == 0
    assert not (root / "chapters/guide/intro.md").exists()
    assert (root / "chapters/guide/overview.md").is_file()
    # Inbound links retargeted, labels and #sections preserved.
    assert "[[chapters/guide/overview|Intro]]" in (root / "chapters/guide/guide.md").read_text()
    assert "[[chapters/guide/overview#Start|Intro]]" in (root / "chapters/guide/setup/setup.md").read_text()
    assert "[[chapters/guide/overview|Intro]]" in (root / "chapters/other/other.md").read_text()


def test_move_does_not_touch_links_in_code(tmp_path):
    root = _grimoire(tmp_path)
    R.do_move(root, "chapters/guide/intro.md", "chapters/guide/overview.md",
              apply=True, reporter=_reporter(root, True), human=False, fmt="json")
    # The backticked self-link in the moved file is left as-is (it is code).
    assert "`[[chapters/guide/intro|self]]`" in (root / "chapters/guide/overview.md").read_text()


def test_move_page_to_another_chapter(tmp_path):
    root = _grimoire(tmp_path)
    R.do_move(root, "chapters/guide/intro.md", "chapters/other/intro.md",
              apply=True, reporter=_reporter(root, True), human=False, fmt="json")
    assert (root / "chapters/other/intro.md").is_file()
    assert "[[chapters/other/intro|Intro]]" in (root / "chapters/guide/guide.md").read_text()


def test_move_chapter_folder_renames_hub_and_all_links(tmp_path):
    root = _grimoire(tmp_path)
    rc = R.do_move(root, "chapters/guide", "chapters/manual",
                   apply=True, reporter=_reporter(root, True), human=False, fmt="json")
    assert rc == 0
    assert not (root / "chapters/guide").exists()
    # Hub renamed to match the new folder name; sub-chapter kept its name.
    assert (root / "chapters/manual/manual.md").is_file()
    assert (root / "chapters/manual/setup/setup.md").is_file()
    assert not (root / "chapters/manual/guide.md").exists()
    # Cross-chapter link retargeted to the new path.
    assert "[[chapters/manual/intro|Intro]]" in (root / "chapters/other/other.md").read_text()
    # Internal links inside the moved chapter retargeted before the move.
    assert "[[chapters/manual/setup/setup|Setup]]" in (root / "chapters/manual/manual.md").read_text()


def test_move_plan_writes_nothing(tmp_path):
    root = _grimoire(tmp_path)
    R.do_move(root, "chapters/guide/intro.md", "chapters/guide/overview.md",
              apply=False, reporter=_reporter(root, False), human=False, fmt="json")
    assert (root / "chapters/guide/intro.md").is_file()
    assert not (root / "chapters/guide/overview.md").exists()
    assert "[[chapters/guide/intro|Intro]]" in (root / "chapters/guide/guide.md").read_text()


def test_move_refuses_existing_destination(tmp_path):
    root = _grimoire(tmp_path)
    rc = R.do_move(root, "chapters/guide/intro.md", "chapters/guide/setup",
                   apply=True, reporter=_reporter(root, True), human=False, fmt="json")
    assert rc == 1
    assert (root / "chapters/guide/intro.md").is_file()  # untouched


def test_move_refuses_outside_chapters(tmp_path):
    root = _grimoire(tmp_path)
    _write(root / "README.md", "# readme\n")
    rc = R.do_move(root, "README.md", "chapters/guide/readme.md",
                   apply=True, reporter=_reporter(root, True), human=False, fmt="json")
    assert rc == 1


def test_move_refuses_lone_hub(tmp_path):
    root = _grimoire(tmp_path)
    rc = R.do_move(root, "chapters/guide/guide.md", "chapters/guide/renamed.md",
                   apply=True, reporter=_reporter(root, True), human=False, fmt="json")
    assert rc == 1
    assert (root / "chapters/guide/guide.md").is_file()


def test_move_refuses_into_own_subpath_without_writing(tmp_path):
    root = _grimoire(tmp_path)
    before = (root / "chapters/guide/guide.md").read_text()
    rc = R.do_move(root, "chapters/guide", "chapters/guide/sub",
                   apply=True, reporter=_reporter(root, True), human=False, fmt="json")
    assert rc == 1
    assert (root / "chapters/guide").is_dir()
    # No links rewritten and no half-move: content is byte-identical.
    assert (root / "chapters/guide/guide.md").read_text() == before


def test_move_refuses_when_destination_parent_is_a_file(tmp_path):
    root = _grimoire(tmp_path)
    before = (root / "chapters/guide/guide.md").read_text()
    rc = R.do_move(root, "chapters/other/other.md", "chapters/guide/intro.md/x.md",
                   apply=True, reporter=_reporter(root, True), human=False, fmt="json")
    assert rc == 1
    assert (root / "chapters/other/other.md").is_file()
    assert (root / "chapters/guide/guide.md").read_text() == before


def test_move_plan_and_apply_agree_on_refusal(tmp_path):
    root = _grimoire(tmp_path)
    plan_rc = R.do_move(root, "chapters/guide", "chapters/guide/sub",
                        apply=False, reporter=_reporter(root, False), human=False, fmt="json")
    apply_rc = R.do_move(root, "chapters/guide", "chapters/guide/sub",
                         apply=True, reporter=_reporter(root, True), human=False, fmt="json")
    assert plan_rc == 1 and apply_rc == 1


# ---------------------------------------------------------------------------
# remove
# ---------------------------------------------------------------------------


def test_remove_page_reports_inbound(tmp_path):
    root = _grimoire(tmp_path)
    reporter = _reporter(root, True)
    rc = R.do_remove(root, "chapters/guide/intro.md", apply=True,
                     reporter=reporter, human=False, fmt="json")
    assert rc == 0
    assert not (root / "chapters/guide/intro.md").exists()
    warnings = [m for m in reporter.messages if m["severity"] == "warning"]
    # guide.md, setup/setup.md, and other/other.md all linked to intro.
    assert len(warnings) == 3


def test_remove_chapter_folder(tmp_path):
    root = _grimoire(tmp_path)
    reporter = _reporter(root, True)
    rc = R.do_remove(root, "chapters/guide", apply=True,
                     reporter=reporter, human=False, fmt="json")
    assert rc == 0
    assert not (root / "chapters/guide").exists()
    # only other/other.md remains pointing in (its link to guide/intro).
    warnings = [m for m in reporter.messages if m["severity"] == "warning"]
    assert any("other/other.md" in (w.get("path") or "") for w in warnings)


def test_remove_plan_writes_nothing(tmp_path):
    root = _grimoire(tmp_path)
    R.do_remove(root, "chapters/guide/intro.md", apply=False,
                reporter=_reporter(root, False), human=False, fmt="json")
    assert (root / "chapters/guide/intro.md").is_file()


def test_remove_refuses_lone_hub(tmp_path):
    root = _grimoire(tmp_path)
    rc = R.do_remove(root, "chapters/guide/guide.md", apply=True,
                     reporter=_reporter(root, True), human=False, fmt="json")
    assert rc == 1
    assert (root / "chapters/guide/guide.md").is_file()
