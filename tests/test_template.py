"""Tests for envoy/template.py"""

import pytest
from envoy.template import (
    TemplateError,
    apply_template_to_project,
    load_template_file,
    parse_template,
    render_template,
)


SIMPLE = "DB_HOST={{ HOST }}\nDB_PORT={{ PORT }}\n"


def test_parse_template_finds_vars():
    assert parse_template(SIMPLE) == ["HOST", "PORT"]


def test_parse_template_deduplicates():
    assert parse_template("{{ X }}={{ X }}") == ["X"]


def test_parse_template_empty():
    assert parse_template("NO_VARS=1\n") == []


def test_render_template_substitutes():
    result = render_template(SIMPLE, {"HOST": "localhost", "PORT": "5432"})
    assert result == "DB_HOST=localhost\nDB_PORT=5432\n"


def test_render_template_missing_strict_raises():
    with pytest.raises(TemplateError, match="Missing template variables"):
        render_template(SIMPLE, {"HOST": "localhost"})


def test_render_template_missing_loose_keeps_placeholder():
    result = render_template(SIMPLE, {"HOST": "localhost"}, strict=False)
    assert "{{ PORT }}" in result
    assert "DB_HOST=localhost" in result


def test_render_template_no_vars():
    text = "KEY=value\n"
    assert render_template(text, {}) == text


def test_apply_template_to_project():
    result = apply_template_to_project(SIMPLE, {"HOST": "db", "PORT": "3306"})
    assert "DB_HOST=db" in result


def test_load_template_file(tmp_path):
    f = tmp_path / "env.tpl"
    f.write_text("X={{ X }}\n")
    assert load_template_file(str(f)) == "X={{ X }}\n"


def test_load_template_file_missing_raises():
    with pytest.raises(TemplateError, match="not found"):
        load_template_file("/nonexistent/path/env.tpl")
