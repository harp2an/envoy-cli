"""Tests for envoy/cmd_template.py"""

import argparse
import sys
from unittest.mock import patch, MagicMock

import pytest

from envoy.cmd_template import (
    cmd_template_render,
    cmd_template_vars,
    register_template_parser,
    _parse_vars,
)


def _args(**kwargs):
    defaults = dict(template="env.tpl", var=None, project=None, password=None, loose=False)
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_parse_vars_simple():
    assert _parse_vars(["HOST=localhost", "PORT=5432"]) == {"HOST": "localhost", "PORT": "5432"}


def test_parse_vars_invalid_exits(capsys):
    with pytest.raises(SystemExit):
        _parse_vars(["BADVAR"])


def test_register_template_parser():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd")
    register_template_parser(sub)
    args = p.parse_args(["template", "vars", "myfile.tpl"])
    assert args.template == "myfile.tpl"


def test_cmd_template_vars_prints(tmp_path, capsys):
    f = tmp_path / "t.tpl"
    f.write_text("A={{ FOO }}\nB={{ BAR }}\n")
    cmd_template_vars(_args(template=str(f)))
    out = capsys.readouterr().out
    assert "FOO" in out
    assert "BAR" in out


def test_cmd_template_render_to_stdout(tmp_path, capsys):
    f = tmp_path / "t.tpl"
    f.write_text("HOST={{ HOST }}\n")
    cmd_template_render(_args(template=str(f), var=["HOST=myhost"]))
    out = capsys.readouterr().out
    assert "HOST=myhost" in out


def test_cmd_template_render_missing_var_exits(tmp_path):
    f = tmp_path / "t.tpl"
    f.write_text("HOST={{ HOST }}\n")
    with pytest.raises(SystemExit):
        cmd_template_render(_args(template=str(f), var=[]))


def test_cmd_template_render_missing_file_exits():
    with pytest.raises(SystemExit):
        cmd_template_render(_args(template="/no/such/file.tpl"))
