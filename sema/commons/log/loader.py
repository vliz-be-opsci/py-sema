import logging
from pathlib import Path

import yaml

DEFAULT_LOGGING_CONFIG_LOCATION = Path(__file__).parent / "debug_logconf.yml"


def load_log_config(logconf: str = None):
    """
    Load the logger configuration from a file.

    :param logconf: location of the log configuration file
    """
    if logconf is None:
        logconf = DEFAULT_LOGGING_CONFIG_LOCATION

    logconf_path = Path(logconf)
    if not logconf_path.exists():
        raise FileNotFoundError(f"Log configuration file not found: {logconf}")

    if str(logconf_path).endswith(".yml"):
        with open(logconf_path, "r") as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
        return

    logging.config.fileConfig(str(logconf_path))
