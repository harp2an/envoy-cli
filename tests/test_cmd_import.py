"""Tests for envoy.cmd_import."""

import argparse
import pytest
from unittest.mock import patch, MagicMock

from envoy.cmd_import import cmd_import, register_import_parser


@pytest.fixture()
def args():
    ns = argparse.Namespace(project="myproject", file=".env")
    return ns


def test_register_import_parser():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register_import_parser(sub)
    parsed = parser.parse_args(["import", "proj", ".env"])
    assert parsed.project == "proj"
    assert parsed.file == ".env"


def test_cmd_import_success(args, capsys):
    with patch("envoy.cmd_import.getpass.getpass", return_value="pw"), \
         patch("envoy.cmd_import.import_dotenv_file", return_value=3) as mock_imp:
        cmd_import(args)
    out = capsys.readouterr().out
    assert "3" in out
    assert "myproject" in out
    mock_imp.assert_called_once_with("myproject", ".env", "pw")


def test_cmd_import_failure_exits(args):
    from envoy.import_env import ImportError as EnvImportError
    with patch("envoy.cmd_import.getpass.getpass", return_value="pw"), \
         patch("envoy.cmd_import.import_dotenv_file", side_effect=EnvImportError("bad")):
        with pytest.raises(SystemExit) as exc:
            cmd_import(args)
    assert exc.value.code == 1
