"""Unit tests for rites/_lib.py - the shared validator/utility library."""

from pathlib import Path

import _lib


# ---------------------------------------------------------------------------
# parse_frontmatter
# ---------------------------------------------------------------------------


def test_parse_frontmatter_returns_empty_dict_when_no_frontmatter():
    assert _lib.parse_frontmatter("# heading only\n\nbody") == {}


def test_parse_frontmatter_extracts_simple_scalars():
    text = '---\ntype: hub\ntitle: "Hello"\n---\n\nbody'
    fm = _lib.parse_frontmatter(text)
    assert fm["type"] == "hub"
    assert fm["title"] == "Hello"


def test_parse_frontmatter_inline_list():
    text = "---\ntype: hub\ntags: [a, b, c]\n---\n\nbody"
    fm = _lib.parse_frontmatter(text)
    assert fm["tags"] == ["a", "b", "c"]


def test_parse_frontmatter_multiline_list():
    text = "---\ntype: hub\naliases:\n  - one\n  - two\n  - three\n---\n\nbody"
    fm = _lib.parse_frontmatter(text)
    assert fm["aliases"] == ["one", "two", "three"]


def test_parse_frontmatter_handles_empty_inline_list():
    text = "---\ntype: hub\naliases: []\n---\n\nbody"
    assert _lib.parse_frontmatter(text)["aliases"] == []


def test_parse_frontmatter_strips_quotes():
    text = "---\ntype: 'hub'\ntitle: \"quoted\"\n---\n\nbody"
    fm = _lib.parse_frontmatter(text)
    assert fm["type"] == "hub"
    assert fm["title"] == "quoted"


# ---------------------------------------------------------------------------
# strip_code_blocks
# ---------------------------------------------------------------------------


def test_strip_code_blocks_removes_fenced_content():
    text = "before\n```\n[fake](link.md)\n```\nafter"
    cleaned = _lib.strip_code_blocks(text)
    assert "[fake]" not in cleaned
    assert "before" in cleaned and "after" in cleaned


def test_strip_code_blocks_removes_inline_backticks():
    text = "live link [real](real.md) and `[fake](fake.md)` end"
    cleaned = _lib.strip_code_blocks(text)
    assert "[real]" in cleaned
    assert "[fake]" not in cleaned


def test_strip_code_blocks_preserves_line_count():
    text = "a\n```\nb\nc\n```\nd"
    assert len(_lib.strip_code_blocks(text).splitlines()) == len(text.splitlines())


# ---------------------------------------------------------------------------
# load_manifest
# ---------------------------------------------------------------------------


GOOD = Path(__file__).parent / "fixtures" / "good_grimoire"
BAD_FRONT = Path(__file__).parent / "fixtures" / "bad_frontmatter"
BAD_LINKS = Path(__file__).parent / "fixtures" / "bad_links"


def test_load_manifest_reads_good_fixture():
    metadata, errors = _lib.load_manifest(GOOD)
    assert errors == []
    assert metadata["name"] == "good_grimoire"
    assert metadata["skill_prefix"] == "good"


def test_load_manifest_returns_none_when_missing(tmp_path):
    metadata, errors = _lib.load_manifest(tmp_path)
    assert metadata is None
    assert errors == ["missing grimoire.json"]


def test_load_manifest_flags_invalid_skill_prefix(tmp_path):
    (tmp_path / "grimoire.json").write_text(
        '{"name": "x", "skill_prefix": "BAD-NS"}'
    )
    metadata, errors = _lib.load_manifest(tmp_path)
    assert metadata is not None
    assert any("invalid skill_prefix" in e for e in errors)


def test_load_manifest_handles_permission_error(tmp_path, monkeypatch):
    # An unstattable grimoire.json must degrade to an error, not raise, so a
    # restricted directory under the grimoire home cannot crash a scan.
    restricted = tmp_path / "restricted"
    restricted.mkdir()
    real_is_file = Path.is_file

    def fake_is_file(self):
        if self.name == "grimoire.json":
            raise PermissionError("[Errno 13] Permission denied")
        return real_is_file(self)

    monkeypatch.setattr(Path, "is_file", fake_is_file)
    metadata, errors = _lib.load_manifest(restricted)
    assert metadata is None
    assert errors and "could not access" in errors[0]


# ---------------------------------------------------------------------------
# load_library
# ---------------------------------------------------------------------------


def test_load_library_returns_empty_when_missing(tmp_path):
    assert _lib.load_library(tmp_path / "missing.json") == {"grimoires": {}}


def test_load_library_normalizes_missing_grimoires_key(tmp_path):
    p = tmp_path / "library.json"
    p.write_text("{}")
    assert _lib.load_library(p) == {"grimoires": {}}


# ---------------------------------------------------------------------------
# iter_pages
# ---------------------------------------------------------------------------


def test_iter_pages_finds_chapter_and_root_hub():
    pages = list(_lib.iter_pages(GOOD, ["chapters"], exempt_filenames={"README.md", "log.md"}))
    names = {p.name for p in pages}
    assert "good_grimoire.md" in names      # root hub yielded via include_root_md
    assert "sourdough.md" in names           # leaf in chapters/recipes/
    assert "recipes.md" in names             # chapter hub
    assert "README.md" not in names          # exempted
    assert "log.md" not in names             # exempted


def test_iter_pages_respects_skip_dirs():
    # Construct a tree with a skip target and ensure it's filtered.
    pages = list(_lib.iter_pages(GOOD, ["chapters"], skip_dirs={"recipes"}))
    assert all("recipes" not in p.parts for p in pages)


# ---------------------------------------------------------------------------
# Regex sanity (constants are part of the public surface)
# ---------------------------------------------------------------------------


def test_skill_prefix_regex_accepts_valid_slugs():
    assert _lib.SKILL_PREFIX_RE.fullmatch("arc")
    assert _lib.SKILL_PREFIX_RE.fullmatch("oly2")


def test_skill_prefix_regex_rejects_invalid_slugs():
    assert not _lib.SKILL_PREFIX_RE.fullmatch("arc-bad")
    assert not _lib.SKILL_PREFIX_RE.fullmatch("Arc")
    assert not _lib.SKILL_PREFIX_RE.fullmatch("2arc")


def test_skill_slug_regex_accepts_kebab_case():
    assert _lib.SKILL_SLUG_RE.fullmatch("validate-all")
    assert _lib.SKILL_SLUG_RE.fullmatch("a")


def test_skill_slug_regex_rejects_mixed_case():
    assert not _lib.SKILL_SLUG_RE.fullmatch("Arcana-Bad")
    assert not _lib.SKILL_SLUG_RE.fullmatch("arcana_underscore")


def test_date_regex_basic():
    assert _lib.DATE_RE.match("2026-05-15")
    assert not _lib.DATE_RE.match("2026-5-15")


# ---------------------------------------------------------------------------
# is_skipped
# ---------------------------------------------------------------------------


def test_is_skipped_matches_single_segment_dir():
    assert _lib.is_skipped("sources/article.md", {"sources"})
    assert _lib.is_skipped(Path("inbox/note.md"), {"inbox", "tests"})


def test_is_skipped_does_not_match_sibling_prefix():
    # The bug this guards: a sibling sharing a name prefix must not be skipped.
    assert not _lib.is_skipped("sources_extra/page.md", {"sources"})
    assert not _lib.is_skipped("inbox_archive/page.md", {"inbox"})


def test_is_skipped_matches_multi_segment_prefix():
    skip = {"invocations/arcana/validators"}
    assert _lib.is_skipped("invocations/arcana/validators/x.md", skip)
    assert not _lib.is_skipped("invocations/arcana/validators_extra/x.md", skip)


def test_is_skipped_is_anchored_at_path_start():
    assert not _lib.is_skipped("chapters/sources/x.md", {"sources"})


def test_is_skipped_normalizes_backslashes():
    assert _lib.is_skipped("sources\\article.md", {"sources"})


# ---------------------------------------------------------------------------
# public_document
# ---------------------------------------------------------------------------


def test_public_document_top_level_filenames(tmp_path):
    assert _lib.public_document(tmp_path / "README.md", tmp_path)
    assert _lib.public_document(tmp_path / "CHANGELOG.md", tmp_path)


def test_public_document_docs_tree(tmp_path):
    assert _lib.public_document(tmp_path / "docs" / "installation.md", tmp_path)


def test_public_document_vault_surface_is_not_public(tmp_path):
    assert not _lib.public_document(tmp_path / "chapters" / "recipes" / "sourdough.md", tmp_path)
    assert not _lib.DATE_RE.match("not-a-date")
