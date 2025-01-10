""" test_main_cli
tests concerning the cli call functioning
"""

import logging
import shutil
from uuid import uuid4

import pytest
from conftest import TEST_INPUT_FOLDER

from sema.syncfs.__main__ import _main

log = logging.getLogger(__name__)


@pytest.mark.usefixtures("store_builds", "syncfolders")
def test_main(store_builds: tuple, syncfolders: tuple):
    log.info(f"test_main ({len(store_builds)})")
    base: str = f"urn:sync:test-main:{uuid4()}:"
    for store_build, syncpath in zip(store_builds, syncfolders):
        root_path = syncpath / "input"
        shutil.copytree(TEST_INPUT_FOLDER, root_path, dirs_exist_ok=True)
        argsline: str = f"--root {str(root_path)} --base {base}"
        store_info: tuple = store_build.store_info
        store_part = " ".join(store_info)
        if (len(store_part)) > 0:
            argsline += f" --store {store_part}"

        log.debug(f"testing equivalent of python -msyncfstriples {argsline}")
        args_list: list = argsline.split(" ")
        _main(*args_list)  # pass as individual arguments

        # TODO consider some extra assertions on the result


def test_main_logconf():
    log.info("test_main_logconf")
    with pytest.raises(FileNotFoundError):
        argsline: str = "--root /tmp --logconf unexisting.yml"
        args_list: list = argsline.split(" ")
        _main(*args_list)  # pass as individual arguments


def test_help(capfd: pytest.CaptureFixture) -> None:
    help_line: str = "--help"
    with pytest.raises(SystemExit) as caught:
        _main(*help_line.split())
    assert caught.value.code == 0
    assert caught.type is SystemExit
    out, err = capfd.readouterr()
    assert len(out) > 0
    assert "usage: " in out
    assert "-r" in out
    assert "--root" in out
    assert "-b" in out
    assert "--base" in out
    assert "--store" in out
    assert "-s" in out
