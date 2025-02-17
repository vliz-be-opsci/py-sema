import logging
from pathlib import Path

import pytest

from sema.harvest import Harvest
from sema.harvest.config_build import ConfigBuilder

log = logging.getLogger(__name__)

TEST_FOLDER = Path(__file__).parent
TEST_Path: Path = TEST_FOLDER / "scenarios"
CONFIGS = TEST_Path / "config"


@pytest.mark.usefixtures("store_info_sets")
def test_files_folder(store_info_sets: tuple) -> None:
    for store in store_info_sets:
        harvest = Harvest(str(CONFIGS), store)
        # get the rdf store access
        rdf_store_access = harvest.target_store
        config_builder = ConfigBuilder(rdf_store_access, str(CONFIGS))
        files = config_builder._files_folder()
        assert isinstance(files, list)
        assert len(files) > 0


@pytest.mark.usefixtures("store_info_sets")
def test_files_folder_invalid_path(store_info_sets: tuple) -> None:
    for store in store_info_sets:
        harvest = Harvest(str(CONFIGS), store)
        # get the rdf store access
        rdf_store_access = harvest.target_store
        config_builder = ConfigBuilder(rdf_store_access, "invalid_path")
        files = config_builder._files_folder()
        assert isinstance(files, list)
        assert len(files) == 0
