import sys
from logging import getLogger

from .discovery import DiscoveryService

log = getLogger(__name__)


def main(*args_list):
    log.debug(f"discovery::main({args_list=})")
    # TODO actually use args_list and argsparser to replace hardcoding below
    service = DiscoveryService(subject_uri="https://data.emobon.embrc.eu/")
    result, trace = service.process()
    return bool(result)


if __name__ == "__main__":
    success: bool = main(*sys.argv[1:])
    sys.exit(0 if success else 1)
