"""Tests for envoy.export module."""

import pytest
from envoy.export import parse_dotenv, render_dotenv, export_shell, ExportError


def test_parse_simple_pairs():
    text = "FOO=bar\nBAZ=qux\n"
    result = parse_dotenv(text)
    assert result == {"FOO": "bar", "BAZ": "qux"}


def test_parse_ignores_comments_and_blanks():
    text = "# comment\n\nFOO=bar\n"
    result = parse_dotenv(text)
    assert result == {"FOO": "bar"}


def test_parse_strips_double_quotes():
    result = parse_dotenv('KEY="hello world"')
    assert result["KEY"] == "hello world"


def test_parse_strips_single_quotes():
    result = parse_dotenv("KEY='hello'")
    assert result["KEY"] == "hello"


def test_parse_invalid_line_raises():
    with pytest.raises(ExportError, match="Invalid line"):
        parse_dotenv("NOTAVALIDLINE")


def test_parse_invalid_key_raises():
    with pytest.raises(ExportError, match="Invalid key"):
        parse_dotenv("123BAD=value")


def test_render_dotenv_sorted():
    env = {"Z_KEY": "last", "A_KEY": "first"}
    text = render_dotenv(env)
    lines = text.strip().splitlines()
    assert lines[0].startswith("A_KEY")
    assert lines[1].startswith("Z_KEY")


def test_render_quotes_values_with_spaces():
    text = render_dotenv({"MSG": "hello world"})
    assert 'MSG="hello world"' in text


def test_render_plain_values_unquoted():
    text = render_dotenv({"TOKEN": "abc123"})
    assert "TOKEN=abc123" in text


def test_roundtrip():
    original = {"FOO": "bar", "GREETING": "hello world", "NUM": "42"}
    text = render_dotenv(original)
    parsed = parse_dotenv(text)
    assert parsed == original


def test_export_shell_format():
    result = export_shell({"FOO": "bar"})
    assert result.strip() == 'export FOO="bar"'


def test_export_shell_escapes_quotes():
    result = export_shell({"VAL": 'say "hi"'})
    assert 'say \\"hi\\"' in result


def test_render_empty_dict():
    assert render_dotenv({}) == ""
