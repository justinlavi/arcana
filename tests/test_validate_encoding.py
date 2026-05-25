from pathlib import Path

from validate_encoding import check_file


def test_numeric_range_repair_artifacts_are_caught(tmp_path: Path):
    path = tmp_path / "broken.md"
    path.write_text("Use 2" + "?5 examples.\n", encoding="utf-8", newline="\n")

    violations = check_file(path, tmp_path)

    assert violations
    assert violations[0].code == "ENCODING_REPAIR_ARTIFACT"
    assert "numeric range repair artifact" in violations[0].message
