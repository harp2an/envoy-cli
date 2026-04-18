"""Tests for envoy.cmd_snapshot CLI layer."""

import argparse
import pytest
from unittest.mock import patch, MagicMock

from envoy.cmd_snapshot import (
    cmd_snapshot_create,
    cmd_snapshot_list,
    cmd_snapshot_restore,
    cmd_snapshot_delete,
    register_snapshot_parser,
)


def _args(**kwargs):
    ns = argparse.Namespace(project="proj", tag=None, label=None)
    ns.__dict__.update(kwargs)
    return ns


def test_register_snapshot_parser():
    p = argparse.ArgumentParser()
    sp = p.add_subparsers(dest="cmd")
    register_snapshot_parser(sp)
    args = p.parse_args(["snapshot", "list", "myproject"])
    assert args.project == "myproject"


def test_cmd_snapshot_create_prints_tag(capsys):
    with patch("envoy.cmd_snapshot.getpass.getpass", return_value="pw"), \
         patch("envoy.cmd_snapshot.create_snapshot", return_value="20240101T000000Z") as m:
        cmd_snapshot_create(_args(project="proj", label=None))
    out = capsys.readouterr().out
    assert "20240101T000000Z" in out


def test_cmd_snapshot_create_error_exits(capsys):
    from envoy.snapshot import SnapshotError
    with patch("envoy.cmd_snapshot.getpass.getpass", return_value="pw"), \
         patch("envoy.cmd_snapshot.create_snapshot", side_effect=SnapshotError("boom")):
        with pytest.raises(SystemExit):
            cmd_snapshot_create(_args(project="proj"))


def test_cmd_snapshot_list_no_snapshots(capsys):
    with patch("envoy.cmd_snapshot.list_snapshots", return_value=[]):
        cmd_snapshot_list(_args(project="proj"))
    assert "No snapshots" in capsys.readouterr().out


def test_cmd_snapshot_list_with_snapshots(capsys):
    with patch("envoy.cmd_snapshot.list_snapshots", return_value=["a", "b"]):
        cmd_snapshot_list(_args(project="proj"))
    out = capsys.readouterr().out
    assert "a" in out and "b" in out


def test_cmd_snapshot_restore_success(capsys):
    with patch("envoy.cmd_snapshot.getpass.getpass", return_value="pw"), \
         patch("envoy.cmd_snapshot.restore_snapshot") as m:
        cmd_snapshot_restore(_args(project="proj", tag="v1"))
    assert m.called


def test_cmd_snapshot_delete_success(capsys):
    with patch("envoy.cmd_snapshot.delete_snapshot") as m:
        cmd_snapshot_delete(_args(project="proj", tag="v1"))
    assert m.called
