from logging.config import dictConfig, fileConfig
from pathlib import Path

import yaml

DEFAULT_LOGGING_CONFIG_LOCATION = Path(__file__).parent / "debug_logconf.yml"


def load_log_config(logconf: str | None | Path = None):
    """
    Load the logger configuration from a file.

    :param logconf: location of the log configuration file
    """
    if logconf is None and DEFAULT_LOGGING_CONFIG_LOCATION.exists():
        logconf = DEFAULT_LOGGING_CONFIG_LOCATION

    if logconf is None:
        return

    logconf_path = Path()

    if isinstance(logconf, Path):
        logconf_path = logconf

    if isinstance(logconf, str):
        logconf_path = Path(logconf)

    if not logconf_path.exists():
        raise FileNotFoundError(f"Log configuration file not found: {logconf}")

    if logconf_path.suffix == ".yml":
        with open(logconf_path, "r") as f:
            dictConfig(yaml.load(f, Loader=yaml.SafeLoader))
        return
    # else
    fileConfig(str(logconf_path))
