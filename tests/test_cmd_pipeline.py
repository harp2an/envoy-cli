"""Tests for envoy.cmd_pipeline CLI commands."""
import argparse
import sys
import pytest

from envoy.cmd_pipeline import (
    cmd_pipeline_create,
    cmd_pipeline_delete,
    cmd_pipeline_list,
    cmd_pipeline_show,
    register_pipeline_parser,
)
from envoy.pipeline import create_pipeline


@pytest.fixture()
def isolated_store(tmp_path, monkeypatch):
    monkeypatch.setattr("envoy.pipeline.get_store_dir", lambda: tmp_path)
    return tmp_path


def _args(**kwargs):
    ns = argparse.Namespace(**kwargs)
    return ns


def test_register_pipeline_parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_pipeline_parser(sub)
    parsed = p.parse_args(["pipeline", "list"])
    assert parsed.pipeline_cmd == "list"


def test_register_pipeline_parser_create():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_pipeline_parser(sub)
    parsed = p.parse_args(["pipeline", "create", "myflow", "lint", "push"])
    assert parsed.name == "myflow"
    assert parsed.steps == ["lint", "push"]


def test_cmd_pipeline_create_success(isolated_store, capsys):
    args = _args(name="deploy", steps=["lint", "push"])
    cmd_pipeline_create(args)
    out = capsys.readouterr().out
    assert "deploy" in out
    assert "lint" in out


def test_cmd_pipeline_create_error_exits(isolated_store):
    args = _args(name="bad", steps=["nonexistent"])
    with pytest.raises(SystemExit):
        cmd_pipeline_create(args)


def test_cmd_pipeline_show_success(isolated_store, capsys):
    create_pipeline("ci", ["lint", "validate"], store_dir=isolated_store)
    args = _args(name="ci")
    cmd_pipeline_show(args)
    out = capsys.readouterr().out
    assert "lint" in out
    assert "validate" in out


def test_cmd_pipeline_show_missing_exits(isolated_store):
    args = _args(name="ghost")
    with pytest.raises(SystemExit):
        cmd_pipeline_show(args)


def test_cmd_pipeline_list_empty(isolated_store, capsys):
    cmd_pipeline_list(_args())
    out = capsys.readouterr().out
    assert "No pipelines" in out


def test_cmd_pipeline_list_with_entries(isolated_store, capsys):
    create_pipeline("nightly", ["snapshot", "rotate"], store_dir=isolated_store)
    cmd_pipeline_list(_args())
    out = capsys.readouterr().out
    assert "nightly" in out
    assert "snapshot" in out


def test_cmd_pipeline_delete_success(isolated_store, capsys):
    create_pipeline("tmp", ["pull"], store_dir=isolated_store)
    cmd_pipeline_delete(_args(name="tmp"))
    out = capsys.readouterr().out
    assert "deleted" in out


def test_cmd_pipeline_delete_missing_exits(isolated_store):
    with pytest.raises(SystemExit):
        cmd_pipeline_delete(_args(name="nope"))
