import logging
from pathlib import Path

import pytest

from sema.harvest.config_build import ConfigBuilder
from sema.harvest.executor import Executor

log = logging.getLogger(__name__)

TEST_CONFIG_FOLDER = Path(__file__).parent / "config"


@pytest.mark.usefixtures("decorated_rdf_stores")
def test_executor(decorated_rdf_stores):
    for rdf_store in decorated_rdf_stores:
        # first make config_builder
        configbuilder = ConfigBuilder(
            rdf_store,
            str(TEST_CONFIG_FOLDER / "good_folder"),
        )

        t_object = configbuilder.build_from_config("base_test.yml")

        # extract values from t_object and pass them to executor
        Executor(
            t_object.configname,
            t_object.NSM,
            t_object.tasks,
            rdf_store,
        ).assert_all_paths()


@pytest.mark.usefixtures("decorated_rdf_stores")
def test_executor_star_config(decorated_rdf_stores):
    for rdf_store in decorated_rdf_stores:
        # first make config_builder
        configbuilder = ConfigBuilder(
            rdf_store,
            str(TEST_CONFIG_FOLDER),
        )

        t_object = configbuilder.build_from_config("star_config.yml")

        # extract values from t_object and pass them to executor
        Executor(
            t_object.configname,
            t_object.NSM,
            t_object.tasks,
            rdf_store,
        ).assert_all_paths()
