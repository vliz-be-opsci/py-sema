import logging
import os
import unittest
from pathlib import Path

from sema.subyt import Subyt

log = logging.getLogger(__name__)

SUBYT_TEST_FOLDER = Path(os.path.dirname(os.path.abspath(__file__)))


class TestRepeatedSinkPaths(unittest.TestCase):
    """
    Test case based on examples/subyt_duplicated_data_items.py
    """

    def test_allow_repeated_sink_paths(self):
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
        ).process()
        assert (SUBYT_TEST_FOLDER / "tmp/data/D.ttl").exists()
        assert (SUBYT_TEST_FOLDER / "tmp/data/D.ttl_0").exists()
        assert (SUBYT_TEST_FOLDER / "tmp/data/D.ttl_1").exists()

    def test_disallow_repeated_sink_paths(self):
        subyt = Subyt(
            source=str(
                SUBYT_TEST_FOLDER
                / "resources/data_with_repeated_identifiers.csv"
            ),
            sink=str(SUBYT_TEST_FOLDER / "tmp/data/{key}.ttl"),
            template_name="data.ttl.j2",
            template_folder=str(SUBYT_TEST_FOLDER / "resources"),
            conditional=True,
        )
        self.assertRaises(RuntimeError, subyt.process)
