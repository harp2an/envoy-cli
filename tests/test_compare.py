"""Tests for envoy.compare."""
import pytest
from unittest.mock import patch
from envoy.compare import compare_projects, format_compare, CompareResult, CompareError
from envoy.crypto import encrypt


ENV_A = "KEY1=hello\nKEY2=world\nSHARED=same\n"
ENV_B = "KEY3=foo\nSHARED=same\nDIFF=other\n"
ENV_A_DIFF = "KEY1=hello\nSHARED=changed\n"


def _enc(text, pw="pass"):
    return encrypt(text, pw)


def test_compare_identical_projects():
    cipher = _enc(ENV_A)
    with patch("envoy.compare.load_env", return_value=cipher):
        result = compare_projects("p1", "pass", "p2", "pass")
    assert result.is_equal
    assert result.only_in_a == []
    assert result.only_in_b == []
    assert result.different == []


def test_compare_different_projects():
    cipher_a = _enc(ENV_A)
    cipher_b = _enc(ENV_B)
    call_count = {"n": 0}

    def fake_load(project):
        call_count["n"] += 1
        return cipher_a if call_count["n"] == 1 else cipher_b

    with patch("envoy.compare.load_env", side_effect=fake_load):
        result = compare_projects("p1", "pass", "p2", "pass")

    assert "KEY1" in result.only_in_a
    assert "KEY2" in result.only_in_a
    assert "KEY3" in result.only_in_b
    assert "DIFF" in result.only_in_b
    assert "SHARED" in result.same
    assert not result.is_equal


def test_compare_value_difference():
    cipher_a = _enc(ENV_A)
    cipher_b = _enc(ENV_A_DIFF)
    call_count = {"n": 0}

    def fake_load(project):
        call_count["n"] += 1
        return cipher_a if call_count["n"] == 1 else cipher_b

    with patch("envoy.compare.load_env", side_effect=fake_load):
        result = compare_projects("p1", "pass", "p2", "pass")

    keys_diff = [d[0] for d in result.different]
    assert "SHARED" in keys_diff


def test_compare_missing_project_raises():
    with patch("envoy.compare.load_env", side_effect=FileNotFoundError):
        with pytest.raises(CompareError, match="not found"):
            compare_projects("missing", "pass", "other", "pass")


def test_compare_wrong_password_raises():
    cipher_a = _enc(ENV_A, "correct")
    cipher_b = _enc(ENV_B, "correct")
    call_count = {"n": 0}

    def fake_load(project):
        call_count["n"] += 1
        return cipher_a if call_count["n"] == 1 else cipher_b

    with patch("envoy.compare.load_env", side_effect=fake_load):
        with pytest.raises(CompareError, match="wrong password"):
            compare_projects("p1", "wrong", "p2", "correct")


def test_format_compare_equal():
    result = CompareResult(same=["A", "B"])
    out = format_compare(result, "p1", "p2")
    assert "identical" in out


def test_format_compare_differences():
    result = CompareResult(
        only_in_a=["X"],
        only_in_b=["Y"],
        different=[("Z", "v1", "v2")],
    )
    out = format_compare(result, "p1", "p2")
    assert "< X" in out
    assert "> Y" in out
    assert "~ Z" in out
