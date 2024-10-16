import logging
import logging.config
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace

from sema.commons.log.loader import load_log_config

from .service import DEFAULT_URN_BASE, SyncFsTriples

log = logging.getLogger(__name__)


def get_arg_parser():
    """Defines the arguments to this module's __main__ cli script
    by using Python's
    [argparse](https://docs.python.org/3/library/argparse.html)
    """
    ap = ArgumentParser(
        prog="syncfs",
        description="CLI for main action in pysyncfstriples",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    ap.add_argument(
        "-l",
        "--logconf",
        metavar="LOGCONF_FILE.yml",
        type=str,
        action="store",
        help="The config file for the Logging in yml format",
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


def main(*cli_args):
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


if __name__ == "__main__":
    # getting the cli_args here and passing them to main
    # this make the main() testable without shell subprocess
    main(*sys.argv[1:])
