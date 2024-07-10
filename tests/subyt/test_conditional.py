import logging
import os
import time
import unittest
from pathlib import Path

import pandas as pd
from conftest import run_single_test

from sema.commons.log.loader import load_log_config
from sema.subyt import Subyt

load_log_config()
log = logging.getLogger(__name__)

SUBYT_TEST_FOLDER = Path(os.path.dirname(os.path.abspath(__file__)))


class TestConditional(unittest.TestCase):
    """
    Test case based on examples/subyt_conditional.py
    """

    def test_conditional(self):
        if (SUBYT_TEST_FOLDER / "tmp/data/A.ttl").exists():
            os.remove(SUBYT_TEST_FOLDER / "tmp/data/A.ttl")

        if (SUBYT_TEST_FOLDER / "tmp/data/D.ttl").exists():
            os.remove(SUBYT_TEST_FOLDER / "tmp/data/D.ttl")

        # first run
        Subyt(
            source=str(SUBYT_TEST_FOLDER / "resources/data.csv"),
            sink=str(SUBYT_TEST_FOLDER / "tmp/data/{key}.ttl"),
            template_name="data.ttl.j2",
            template_folder=str(SUBYT_TEST_FOLDER / "resources"),
            conditional=True,
        ).process()
        A_mtime1 = os.stat(str(SUBYT_TEST_FOLDER / "tmp/data/A.ttl")).st_mtime

        # second run and no updates to input file
        time.sleep(1)
        Subyt(
            source=str(SUBYT_TEST_FOLDER / "resources/data.csv"),
            sink=str(SUBYT_TEST_FOLDER / "tmp/data/{key}.ttl"),
            template_name="data.ttl.j2",
            template_folder=str(SUBYT_TEST_FOLDER / "resources"),
            conditional=True,
        ).process()
        A_mtime2 = os.stat(str(SUBYT_TEST_FOLDER / "tmp/data/A.ttl")).st_mtime
        assert A_mtime1 == A_mtime2  # output file should not have been updated

        # third run and update to input file
        time.sleep(1)
        df = pd.read_csv(str(SUBYT_TEST_FOLDER / "resources/data.csv"))
        df.at[0, "value"] = 0
        df.to_csv(str(SUBYT_TEST_FOLDER / "resources/data.csv"), index=False)
        Subyt(
            source=str(SUBYT_TEST_FOLDER / "resources/data.csv"),
            sink=str(SUBYT_TEST_FOLDER / "tmp/data/{key}.ttl"),
            template_name="data.ttl.j2",
            template_folder=str(SUBYT_TEST_FOLDER / "resources"),
            conditional=True,
        ).process()
        A_mtime3 = os.stat(str(SUBYT_TEST_FOLDER / "tmp/data/A.ttl")).st_mtime
        assert A_mtime1 < A_mtime3  # output file should have been updated

        # fourth run and no updates to input file
        time.sleep(1)
        Subyt(
            source=str(SUBYT_TEST_FOLDER / "resources/data.csv"),
            sink=str(SUBYT_TEST_FOLDER / "tmp/data/{key}.ttl"),
            template_name="data.ttl.j2",
            template_folder=str(SUBYT_TEST_FOLDER / "resources"),
            conditional=True,
        ).process()
        A_mtime4 = os.stat(str(SUBYT_TEST_FOLDER / "tmp/data/A.ttl")).st_mtime
        D_mtime4 = os.stat(str(SUBYT_TEST_FOLDER / "tmp/data/D.ttl")).st_mtime
        assert A_mtime3 == A_mtime4  # output file should not have been updated

        # fifth run and one of the output files is missing
        time.sleep(1)
        os.remove(str(SUBYT_TEST_FOLDER / "tmp/data/D.ttl"))
        Subyt(
            source=str(SUBYT_TEST_FOLDER / "resources/data.csv"),
            sink=str(SUBYT_TEST_FOLDER / "tmp/data/{key}.ttl"),
            template_name="data.ttl.j2",
            template_folder=str(SUBYT_TEST_FOLDER / "resources"),
            conditional=True,
        ).process()
        A_mtime5 = os.stat(str(SUBYT_TEST_FOLDER / "tmp/data/A.ttl")).st_mtime
        D_mtime5 = os.stat(str(SUBYT_TEST_FOLDER / "tmp/data/D.ttl")).st_mtime
        assert A_mtime4 == A_mtime5  # output file should not have been updated
        assert D_mtime4 < D_mtime5  # output file should have been updated

        # reset input file
        df = pd.read_csv(str(SUBYT_TEST_FOLDER / "resources/data.csv"))
        df.at[0, "value"] = 1
        df.to_csv(str(SUBYT_TEST_FOLDER / "resources/data.csv"), index=False)


if __name__ == "__main__":
    run_single_test(__file__)
