#!/usr/bin/env python
import logging
from pathlib import Path

import pytest
from conftest import run_single_test

from sema.harvest.config_build import TravHarvConfigBuilder
from sema.harvest.executor import TravHarvExecutor

log = logging.getLogger(__name__)

TEST_CONFIG_FOLDER = Path(__file__).parent / "config"


@pytest.mark.usefixtures("decorated_rdf_stores")
def test_executor(decorated_rdf_stores):
    for rdf_store in decorated_rdf_stores:
        # first make travharv_config_builder
        travharvconfigbuilder = TravHarvConfigBuilder(
            rdf_store,
            str(TEST_CONFIG_FOLDER / "good_folder"),
        )

        travharvobject = travharvconfigbuilder.build_from_config(
            "base_test.yml"
        )

        # extract values from travharvobject and pass them to travharvexecutor
        TravHarvExecutor(
            travharvobject.configname,
            travharvobject.NSM,
            travharvobject.tasks,
            rdf_store,
        ).assert_all_paths()


if __name__ == "__main__":
    run_single_test(__file__)
