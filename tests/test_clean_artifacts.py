"""Temp-target tests for the artifact-cleanup rite."""

import clean_artifacts


def _artifacts(base):
    arts = base / "rites" / ".artifacts"
    arts.mkdir(parents=True)
    (arts / "x.log").write_text("data", encoding="utf-8")
    return arts


def test_clean_location_dry_run_keeps_files(tmp_path):
    arts = _artifacts(tmp_path)
    assert clean_artifacts.clean_location(tmp_path, "x", dry_run=True) == 1
    assert arts.exists()


def test_clean_location_apply_removes(tmp_path):
    arts = _artifacts(tmp_path)
    assert clean_artifacts.clean_location(tmp_path, "x", dry_run=False) == 1
    assert not arts.exists()


def test_clean_location_missing_artifacts_is_noop(tmp_path):
    assert clean_artifacts.clean_location(tmp_path, "x", dry_run=False) == 0


def test_clean_location_survives_rmtree_error(tmp_path, monkeypatch):
    _artifacts(tmp_path)

    def boom(_path):
        raise OSError("locked")

    monkeypatch.setattr(clean_artifacts.shutil, "rmtree", boom)
    # One failure must not propagate; it would otherwise abort a multi-location run.
    assert clean_artifacts.clean_location(tmp_path, "x", dry_run=False) == 0
