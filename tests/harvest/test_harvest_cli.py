import logging
from pathlib import Path

import pytest

from sema.harvest.__main__ import _main

log = logging.getLogger(__name__)

TEST_CONFIG_FOLDER = Path(__file__).parent / "config"
TEST_INPUT_FOLDER = Path(__file__).parent / "inputs"


@pytest.mark.usefixtures("outpath", "store_info_sets")
def test_main(outpath: Path, store_info_sets: tuple):
    conf_path = TEST_CONFIG_FOLDER / "good_folder"
    init_path = TEST_INPUT_FOLDER / "3293.jsonld"

    for n, store_info in enumerate(store_info_sets):
        dump_path = outpath / f"test_main_out_{n:02d}.ttl"
        assert not dump_path.exists(), "no output before run..."

        argsline: str = (
            f"--config {conf_path} --init {init_path} --dump {dump_path}"
        )
        store_part = " ".join(store_info)
        if (len(store_part)) > 0:
            argsline += f" --store {store_part}"

        log.debug(f"testing equivlnt of python -m harvest {argsline}")
        _main(*argsline.split(" "))  # pass as individual arguments
        assert dump_path.exists(), "run did not create expected output"

        # TODO consider some extra assertions on the result
