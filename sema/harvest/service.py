import logging
import logging.config
from pathlib import Path
from typing import List, Optional

from sema.commons.store import RDFStore, create_rdf_store
from sema.harvest.store import RDFStoreAccess

from .config_build import Config, ConfigBuilder
from .executor import Executor

log = logging.getLogger(__name__)


class service:
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

        log.debug(f"config for harvest service set to {config=}")
        self.config = config

        log.debug(f"creating core store with {target_store_info=}")
        core_store: RDFStore = create_rdf_store(*target_store_info)
        self.target_store = RDFStoreAccess(core_store)
        log.debug(f"created core store with {self.target_store=}")

        if Path(self.config).is_dir():
            self.config_builder = ConfigBuilder(self.target_store, self.config)
        else:
            # take the parent of the config file as the config folder
            self.config_folder = self.config.parent
            self.config_builder = ConfigBuilder(
                self.target_store, self.config_folder
            )
        self.executor = None
        self.error_occurred = False

    def process(self):
        try:
            log.debug("running dereference tasks")
            trav_harv_config: Optional[Config] = None
            # if self.config is a path to a folder then
            # we will run all configurations in the folder
            if Path(self.config).is_dir():
                log.debug("running all configurations")
                self.ConfigList = self.config_builder.build_from_folder()
                log.debug(f"""self.ConfigList: {self.ConfigList}""")
                for trav_harv_config in self.ConfigList:
                    if trav_harv_config is None:
                        continue

                    self.executor = Executor(
                        trav_harv_config.configname,
                        trav_harv_config.NSM,
                        trav_harv_config.tasks,
                        self.target_store,
                    )
                    self.executor.assert_all_paths()
            else:
                trav_harv_config = self.config_builder.build_from_config(
                    self.config
                )

                if trav_harv_config is None:
                    log.error(
                        f"No configuration found with name: {self.config}"
                    )
                    return
                self.executor = Executor(
                    trav_harv_config.configname,
                    trav_harv_config.NSM,
                    trav_harv_config.tasks,
                    self.target_store,
                )
                self.executor.assert_all_paths()
        except Exception as e:
            log.error(e)
            log.exception(e)
            log.error("Error running dereference tasks")
            self.error_occurred = True
