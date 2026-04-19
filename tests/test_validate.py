import pytest
from envoy.validate import validate_env, ValidationResult


SIMPLE = "DB_HOST=localhost\nDB_PORT=5432\nSECRET=abc\n"
EMPTY_VAL = "DB_HOST=\nDB_PORT=5432\n"
MISSING = "DB_PORT=5432\n"


def test_validate_all_required_present():
    result = validate_env(SIMPLE, required=["DB_HOST", "DB_PORT"])
    assert result.ok


def test_validate_missing_required_key():
    result = validate_env(MISSING, required=["DB_HOST", "DB_PORT"])
    assert not result.ok
    assert "DB_HOST" in result.missing


def test_validate_empty_value_flagged_when_disallowed():
    result = validate_env(EMPTY_VAL, required=["DB_HOST", "DB_PORT"], allow_empty=False)
    assert "DB_HOST" in result.empty
    assert result.missing == []


def test_validate_empty_value_ok_by_default():
    result = validate_env(EMPTY_VAL, required=["DB_HOST", "DB_PORT"])
    assert result.ok


def test_validate_unknown_keys_flagged():
    result = validate_env(
        SIMPLE,
        required=["DB_HOST", "DB_PORT"],
        optional=[],
        allow_unknown=False,
    )
    assert "SECRET" in result.unknown


def test_validate_unknown_keys_allowed_by_default():
    result = validate_env(SIMPLE, required=["DB_HOST", "DB_PORT"])
    assert result.unknown == []


def test_validate_ignores_comments_and_blanks():
    content = "# comment\n\nDB_HOST=localhost\n"
    result = validate_env(content, required=["DB_HOST"])
    assert result.ok


def test_result_str_ok():
    r = ValidationResult()
    assert str(r) == "OK"


def test_result_str_shows_issues():
    r = ValidationResult(missing=["FOO"], empty=["BAR"], unknown=["BAZ"])
    s = str(r)
    assert "MISSING" in s and "FOO" in s
    assert "EMPTY" in s and "BAR" in s
    assert "UNKNOWN" in s and "BAZ" in s


def test_validate_empty_content_all_required_missing():
    result = validate_env("", required=["A", "B"])
    assert set(result.missing) == {"A", "B"}
