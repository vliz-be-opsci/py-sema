# -*- coding: utf-8 -*-
import sys
from logging import getLogger

from sema.commons.cli import Namespace, SemaArgsParser
from sema.ro.getter import ROGetter

log = getLogger(__name__)


def get_arg_parser() -> SemaArgsParser:
    parser = SemaArgsParser(
        "sema-ro-get",
        "Download ROCrate from URI.",
    )

    parser.add_argument(
        "-u",
        "--uri",
        required=True,
        help="Input folder containing one or more RDF files",
    )

    parser.add_argument(
        "-o",
        "--output-path",
        default=".",
        help="Output file path",
    )

    parser.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help=("Overwrite output path if it already exists."),
    )

    return parser


def make_service(args: Namespace) -> ROGetter:
    """Make the service with the passed args"""
    return ROGetter(
        uri=args.uri,
        output_path=args.output_path,
        force=args.force,
    )


def _main(*args_list) -> bool:
    """The main entry point to this module."""
    args = get_arg_parser().parse_args(args_list)
    toreturn = False
    try:
        rog = make_service(args)
        r = rog.process()
        log.debug("processing done")
        toreturn = r.success
    except Exception as e:
        log.exception("sema.commons.aggregator processing failed", exc_info=e)
    return toreturn


def main():
    success: bool = _main(*sys.argv[1:])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
