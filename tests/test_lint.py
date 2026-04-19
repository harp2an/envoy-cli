"""Tests for envoy.lint."""

import pytest
from envoy.lint import lint_content, lint_project, LintError


def test_lint_clean_content():
    result = lint_content("KEY=value\nOTHER=123\n")
    assert result.ok


def test_lint_ignores_comments_and_blanks():
    result = lint_content("# comment\n\nKEY=value\n")
    assert result.ok


def test_lint_invalid_line_no_equals():
    result = lint_content("BADLINE\n")
    assert not result.ok
    assert any(i.code == "E001" for i in result.issues)


def test_lint_empty_key():
    result = lint_content("=value\n")
    assert not result.ok
    assert any(i.code == "E002" for i in result.issues)


def test_lint_duplicate_key():
    result = lint_content("KEY=a\nKEY=b\n")
    assert not result.ok
    assert any(i.code == "W002" for i in result.issues)


def test_lint_empty_value_warns():
    result = lint_content("KEY=\n")
    assert not result.ok
    assert any(i.code == "W003" for i in result.issues)


def test_lint_unconventional_key_warns():
    result = lint_content("my-key=value\n")
    issues_codes = [i.code for i in result.issues]
    assert "W001" in issues_codes


def test_lint_issue_str():
    result = lint_content("KEY=\n")
    issue = result.issues[0]
    assert "W003" in str(issue)
    assert "L1" in str(issue)


def test_lint_multiple_issues():
    content = "KEY=\nKEY=again\nBADLINE\n"
    result = lint_content(content)
    codes = [i.code for i in result.issues]
    assert "W003" in codes
    assert "W002" in codes
    assert "E001" in codes


def test_lint_project_missing_raises(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    with pytest.raises(LintError):
        lint_project("no_such_project", "pass")


def test_lint_project_success(tmp_path, monkeypatch):
    monkeypatch.setenv("ENVOY_STORE_DIR", str(tmp_path))
    from envoy.storage import store_env
    store_env("myproject", "KEY=value\n", "secret")
    result = lint_project("myproject", "secret")
    assert result.ok
