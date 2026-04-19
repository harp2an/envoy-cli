import zipfile
import json
import pytest
from pathlib import Path
from unittest.mock import patch

from envoy.archive import archive_project, archive_all, unarchive_project, ArchiveError
from envoy.storage import get_store_dir, store_env


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    return tmp_path


def _seed(store_dir, project, password, content):
    store_env(store_dir, project, password, content)


def test_archive_project_creates_zip(isolated_store):
    store_dir = get_store_dir()
    _seed(store_dir, "alpha", "pass", "KEY=val")
    dest = isolated_store / "alpha.zip"
    result = archive_project("alpha", "pass", dest)
    assert result == dest
    assert dest.exists()
    with zipfile.ZipFile(dest) as zf:
        assert "env.enc" in zf.namelist()
        assert "meta.json" in zf.namelist()


def test_archive_project_missing_raises(isolated_store):
    dest = isolated_store / "nope.zip"
    with pytest.raises(ArchiveError, match="not found"):
        archive_project("ghost", "pass", dest)


def test_archive_all_creates_multi_project_zip(isolated_store):
    store_dir = get_store_dir()
    _seed(store_dir, "proj1", "pw", "A=1")
    _seed(store_dir, "proj2", "pw", "B=2")
    dest = isolated_store / "all.zip"
    names = archive_all("pw", dest)
    assert set(names) == {"proj1", "proj2"}
    with zipfile.ZipFile(dest) as zf:
        nl = zf.namelist()
        assert "proj1/env.enc" in nl
        assert "proj2/meta.json" in nl


def test_archive_all_empty_raises(isolated_store):
    with pytest.raises(ArchiveError, match="No projects"):
        archive_all("pw", isolated_store / "out.zip")


def test_unarchive_project_roundtrip(isolated_store):
    store_dir = get_store_dir()
    _seed(store_dir, "beta", "secret", "X=42")
    dest = isolated_store / "beta.zip"
    archive_project("beta", "secret", dest)

    # remove original so we restore fresh
    (store_dir / "beta.enc").unlink()

    project = unarchive_project(dest, "secret", overwrite=True)
    assert project == "beta"


def test_unarchive_existing_no_overwrite_raises(isolated_store):
    store_dir = get_store_dir()
    _seed(store_dir, "gamma", "pw", "Z=9")
    dest = isolated_store / "gamma.zip"
    archive_project("gamma", "pw", dest)
    with pytest.raises(ArchiveError, match="already exists"):
        unarchive_project(dest, "pw", overwrite=False)


def test_unarchive_missing_file_raises(isolated_store):
    with pytest.raises(ArchiveError, match="not found"):
        unarchive_project(isolated_store / "missing.zip", "pw")
