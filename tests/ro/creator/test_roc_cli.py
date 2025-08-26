import os
from pathlib import Path

import pytest

from sema.ro.creator.__main__ import _main

MY_FOLDER = Path(__file__).parent
ROCRATEROOT_FOLDER = MY_FOLDER / "data"


def test_help(capfd):
    help_line: str = "--help"
    with pytest.raises(SystemExit) as caught:
        success: bool = _main(*help_line.split())
        assert not success
        assert caught.value.code == 0
        assert caught.type == SystemExit
    out, err = capfd.readouterr()
    assert len(out) > 0
    assert out.startswith("usage: ")


def test_cli_toomany_yml(capfd):
    rocfile = ROCRATEROOT_FOLDER
    # not a file but a folder that contains multiplre roc-*.yml files

    cli_line = f" {rocfile !s}"
    success: bool = _main(*cli_line.split())
    assert not success


def test_cli_01(capfd):
    rocfile = ROCRATEROOT_FOLDER / "roc-01-basic.yml"

    cli_line = f" {rocfile !s}"
    os.environ["domain"] = "https://ex.org/"
    os.environ["repo"] = "myrepo"
    success: bool = _main(*cli_line.split())
    assert success
    # todo assert the output file exists and conforms...
