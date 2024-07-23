import logging
from pathlib import Path
from typing import List, Optional

from sema.commons.store import RDFStore, create_rdf_store
from sema.harvest.store import RDFStoreAccess

from .config_build import TravHarvConfig, TravHarvConfigBuilder
from .executor import TravHarvExecutor

log = logging.getLogger(__name__)


class TravHarv:
    """Assert all paths for given subjects.
    Given a configuration file, assert all paths
    for all subjects in the configuration file.
    """

    def __init__(
        self,
        config: str,
        target_store_info: Optional[List[str]] = None,
    ):
        """Assert all paths for given subjects.
        Given a configuration file, assert all paths
        for all subjects in the configuration file.
        :param config: The path/name to the configuration file.
        this can be a path to a folder containing multiple configuration files.
        or a path to a single configuration file.
        :type config: str
        :param target_store_info: (optional) The target store information.
         - If None, a memory store will be used.
        :type target_store_info: List[str]
        """

        log.debug(f"config for travharv service set to {config=}")
        self.config = config

        log.debug(f"creating core store with {target_store_info=}")
        core_store: RDFStore = create_rdf_store(*target_store_info)
        self.target_store = RDFStoreAccess(core_store)

        if Path(self.config).is_dir():
            self.travharv_config_builder = TravHarvConfigBuilder(
                self.target_store, self.config
            )
        else:
            # take the parent of the config file as the config folder
            self.config_folder = self.config.parent
            self.travharv_config_builder = TravHarvConfigBuilder(
                self.target_store, self.config_folder
            )
        self.travharvexecutor = None
        self.error_occurred = False

    def process(self):
        try:
            log.debug("running dereference tasks")
            trav_harv_config: Optional[TravHarvConfig] = None
            # if self.config is a path to a folder then
            # we will run all configurations in the folder
            if Path(self.config).is_dir():
                log.debug("running all configurations")
                self.travHarvConfigList = (
                    self.travharv_config_builder.build_from_folder()
                )
                log.debug(
                    f"""self.travHarvConfigList: {self.travHarvConfigList}"""
                )
                for trav_harv_config in self.travHarvConfigList:
                    if trav_harv_config is None:
                        continue

                    self.travharvexecutor = TravHarvExecutor(
                        trav_harv_config.configname,
                        trav_harv_config.NSM,
                        trav_harv_config.tasks,
                        self.target_store,
                    )
                    self.travharvexecutor.assert_all_paths()
            else:
                trav_harv_config = (
                    self.travharv_config_builder.build_from_config(self.config)
                )

                if trav_harv_config is None:
                    log.error(
                        f"No configuration found with name: {self.config}"
                    )
                    return
                self.travharvexecutor = TravHarvExecutor(
                    trav_harv_config.configname,
                    trav_harv_config.NSM,
                    trav_harv_config.tasks,
                    self.target_store,
                )
                self.travharvexecutor.assert_all_paths()
        except Exception as e:
            log.error(e)
            log.exception(e)
            log.error("Error running dereference tasks")
            self.error_occurred = True
