import logging
from pathlib import Path

import pytest

from sema.subyt import Subyt

log = logging.getLogger(__name__)

SUBYT_TEST_FOLDER = Path(__file__).absolute().parent


def test_allow_repeated_sink_paths():
    Subyt(
        source=str(
            SUBYT_TEST_FOLDER
            / "resources/data_with_repeated_identifiers.csv"
        ),
        sink=str(SUBYT_TEST_FOLDER / "tmp/data/{key}.ttl"),
        template_name="data.ttl.j2",
        template_folder=str(SUBYT_TEST_FOLDER / "resources"),
        conditional=True,
        allow_repeated_sink_paths=True,
        break_on_error=True,  # be sure to break on error
    ).process()
    assert (SUBYT_TEST_FOLDER / "tmp/data/D.ttl").exists()
    assert (SUBYT_TEST_FOLDER / "tmp/data/D.ttl_0").exists()
    assert (SUBYT_TEST_FOLDER / "tmp/data/D.ttl_1").exists()


def test_disallow_repeated_sink_paths():
    subyt = Subyt(
        source=str(
            SUBYT_TEST_FOLDER
            / "resources/data_with_repeated_identifiers.csv"
        ),
        sink=str(SUBYT_TEST_FOLDER / "tmp/data/{key}.ttl"),
        template_name="data.ttl.j2",
        template_folder=str(SUBYT_TEST_FOLDER / "resources"),
        conditional=True,
        break_on_error=True,  # be sure to break on error 
    )
    with pytest.raises(RuntimeError):
        subyt.process()
