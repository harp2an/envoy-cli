"""Tests for envoy.compliance module."""

from __future__ import annotations

import pytest

from envoy.compliance import (
    ComplianceError,
    check_compliance,
    get_compliance,
    list_compliance,
    remove_compliance,
)
from envoy.storage import save_manifest


@pytest.fixture
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.compliance.get_store_dir", lambda: tmp_path)
    monkeypatch.setattr("envoy.storage.get_store_dir", lambda: tmp_path)
    save_manifest({"alpha": {"file": "alpha.enc"}, "beta": {"file": "beta.enc"}}, tmp_path)
    return tmp_path


def test_check_compliance_passes(isolated_store):
    result = check_compliance("alpha", "basic", 5, ["FOO"], isolated_store)
    assert result.passed is True
    assert result.violations == []


def test_check_compliance_too_many_keys(isolated_store):
    result = check_compliance("alpha", "minimal", 25, [], isolated_store)
    assert result.passed is False
    assert any("exceeds max" in v for v in result.violations)


def test_check_compliance_forbidden_key(isolated_store):
    result = check_compliance("alpha", "strict", 3, ["DEBUG"], isolated_store)
    assert result.passed is False
    assert any("DEBUG" in v for v in result.violations)


def test_check_compliance_missing_project_raises(isolated_store):
    with pytest.raises(ComplianceError, match="not found"):
        check_compliance("ghost", "basic", 1, [], isolated_store)


def test_check_compliance_unknown_standard_raises(isolated_store):
    with pytest.raises(ComplianceError, match="Unknown standard"):
        check_compliance("alpha", "nope", 1, [], isolated_store)


def test_check_compliance_persists(isolated_store):
    check_compliance("alpha", "basic", 2, ["A"], isolated_store)
    record = get_compliance("alpha", isolated_store)
    assert record is not None
    assert record["project"] == "alpha"
    assert record["standard"] == "basic"


def test_get_compliance_missing_returns_none(isolated_store):
    assert get_compliance("alpha", isolated_store) is None


def test_list_compliance_empty(isolated_store):
    assert list_compliance(isolated_store) == {}


def test_list_compliance_multiple(isolated_store):
    check_compliance("alpha", "basic", 1, [], isolated_store)
    check_compliance("beta", "minimal", 2, [], isolated_store)
    records = list_compliance(isolated_store)
    assert "alpha" in records
    assert "beta" in records


def test_remove_compliance_success(isolated_store):
    check_compliance("alpha", "basic", 1, [], isolated_store)
    remove_compliance("alpha", isolated_store)
    assert get_compliance("alpha", isolated_store) is None


def test_remove_compliance_missing_raises(isolated_store):
    with pytest.raises(ComplianceError, match="No compliance record"):
        remove_compliance("alpha", isolated_store)


def test_compliance_result_as_dict(isolated_store):
    result = check_compliance("alpha", "strict", 1, ["SECRET_KEY"], isolated_store)
    d = result.as_dict()
    assert d["project"] == "alpha"
    assert d["passed"] is False
    assert isinstance(d["violations"], list)
