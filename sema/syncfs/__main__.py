import logging
import logging.config
import sys
from argparse import Namespace

from sema.commons.cli import SemaArgsParser
from sema.commons.log.loader import load_log_config

from .service import DEFAULT_URN_BASE, SyncFsTriples

log = logging.getLogger(__name__)


def get_arg_parser() -> SemaArgsParser:
    """
    Get the argument parser for the sema-syncfs module.

    This parser includes arguments for the root folder, the base uri,
    and the store endpoints.
    """

    ap = SemaArgsParser(
        "sema-sync",
        "CLI for main action in pysyncfstriples."
        "SyncFsTriples is a service to synchronize"
        "a filesystem with a triplestore.",
    )

    ap.add_argument(
        "-r",
        "--root",
        metavar="ROOT_FOLDER/",
        type=str,
        action="store",
        required=True,
        help=(
            "The path to the root folder "
            "containing the files to be synchronized."
        ),
    )
    ap.add_argument(
        "-b",
        "--base",
        metavar="BASE",
        type=str,
        action="store",
        required=False,
        default=DEFAULT_URN_BASE,
        help=(
            "The uri baseref (prefix) for the associated named-graphs "
            "of synced files."
        ),
    )
    ap.add_argument(
        "-s",
        "--store",
        metavar="ENDPOINT",
        nargs="+",
        action="store",
        required=False,
        help=(
            "Pair of read_uri and write_uri describing the "
            "SPARQL endpoint to use as store. "
        ),
    )
    return ap


def make_service(args) -> SyncFsTriples:
    store_info: list = args.store or []
    root = args.root
    base = args.base
    log.debug(f"make service with {root=}, {base=}, {store_info=}")
    service: SyncFsTriples = SyncFsTriples(root, base, *store_info)
    log.debug(f"target store type {type(service.rdfstore).__name__}")
    return service


def _main(*cli_args: str) -> None:
    # parse cli args
    print(f"cli_args = {cli_args}")
    args: Namespace = get_arg_parser().parse_args(cli_args)
    # enable logging
    load_log_config(args.logconf)
    log.debug(f"cli called with {args=}")
    # build the core service
    service: SyncFsTriples = make_service(args)
    # do what needs to be done
    service.process()


def main() -> None:
    _main(*sys.argv[1:])


if __name__ == "__main__":
    # getting the cli_args here and passing them to main
    # this make the main() testable without shell subprocess
    main()
