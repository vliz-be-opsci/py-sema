import argparse
import logging
import logging.config
import sys

from sema.commons.cli import SemaArgsParser
from sema.shacl import Shacl

log = logging.getLogger(__name__)


def get_arg_parser() -> SemaArgsParser:
    """
    Get the argument parser for the module
    """

    parser = SemaArgsParser(
        "sema-shacl",
        "Py Script to execute SHACL validation.",
    )

    parser.add_argument(
        "-g",
        "--graph",
        type=str,
        required=True,
        metavar=("FILE | GLOB | URL"),
        action="store",
        help=(
            "graph source to be validated. Can be single input file, "
            "a glob pattern of multiple matching files to be validated, "
            "or sparql endpoint url (assuming graphdb with shacl support)"
        ),
    )

    parser.add_argument(
        "-s",
        "--shacl",
        type=str,
        required=True,
        metavar=("FILE | URL"),
        action="store",
        help=(
            "Shacl constraints source to validate against. "
            "Can be single input file, or a url to the content"
        ),
    )

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        metavar="FILE",
        action="store",
        help="SHACL report file location relative to current directory path",
    )

    parser.add_argument(
        "-m",
        "--method",
        type=str,
        metavar="METHOD",
        default="pyshacl",
        action="store",
        help="name of SHACL validation method: pyshacl | graphdb",
    )

    return parser


def enable_logging(args: argparse.Namespace):
    if args.logconf is None:
        return
    # conditional dependency -- we only need this (for now) when logconf needs
    #   to be read
    import yaml

    with open(args.logconf, "r") as yml_logconf:
        logging.config.dictConfig(
            yaml.load(yml_logconf, Loader=yaml.SafeLoader)
        )
    log.info(f"Logging enabled according to config in {args.logconf}")


def _main(*cli_args):
    """
    The main entry point to this module.

    """
    args: argparse.Namespace = get_arg_parser().parse_args(cli_args)

    enable_logging(args)
    log.info("The args passed to %s are: %s." % (sys.argv[0], args))
    log.debug("Performing service")
    Shacl(
        graph=args.graph,
        shacl=args.shacl,
        output=args.output,
        method=args.method,
    ).process()


def main() -> None:
    _main(*sys.argv[1:])


if __name__ == "__main__":
    main()
