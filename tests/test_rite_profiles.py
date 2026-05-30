"""Contract tests for Arcana's mutating-rite profiles."""

import ast
from pathlib import Path

from rite_profiles import (
    _WriteVisitor,
    discover_write_capable_rites,
    profile_entries,
    validate_rite_profiles,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def _detects_write(src: str) -> bool:
    visitor = _WriteVisitor()
    visitor.visit(ast.parse(src))
    return visitor.mutates


def test_write_detector_flags_atomic_and_move_idioms():
    assert _detects_write("tmp.replace(dest)")      # Path.replace(target) - atomic rename
    assert _detects_write("p.rename(dest)")         # Path.rename(target)
    assert _detects_write("os.replace(a, b)")
    assert _detects_write("os.rename(a, b)")
    assert _detects_write("os.write(fd, blob)")
    assert _detects_write("shutil.move(a, b)")
    assert _detects_write("path.write_text('x')")


def test_write_detector_ignores_string_and_container_ops():
    assert not _detects_write("s.replace('a', 'b')")                 # str.replace (2 args)
    assert not _detects_write("s.replace('a', 'b').replace('c','d')")
    assert not _detects_write("d.copy()")                           # dict/list copy
    assert not _detects_write("f.write('x')")                       # file write, not os.write
    assert not _detects_write("x = 1 + 2")


def test_rite_profile_contract_covers_write_capable_rites():
    contract, errors = validate_rite_profiles(REPO_ROOT)

    assert not errors
    assert contract is not None
    profiled = {entry["path"] for entry in profile_entries(contract)}
    assert profiled == discover_write_capable_rites(REPO_ROOT)


def test_rite_profile_docs_list_every_profiled_rite():
    contract, errors = validate_rite_profiles(REPO_ROOT)
    assert not errors

    docs = (REPO_ROOT / "docs" / "rite_profiles.md").read_text(encoding="utf-8")
    for entry in profile_entries(contract):
        assert entry["path"] in docs
        assert entry["profile"] in docs
