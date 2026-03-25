# -*- coding: utf-8 -*-
import sys
from logging import getLogger

from sema.commons.aggregator import Aggregator
from sema.commons.cli import Namespace, SemaArgsParser

log = getLogger(__name__)


def get_arg_parser() -> SemaArgsParser:
    parser = SemaArgsParser(
        "sema-aggregate",
        "Aggregate one or more RDF files into a single RDF file.",
    )

    parser.add_argument(
        "-ip",
        "--input-path",
        default=".",
        help="Input folder containing one or more RDF files",
    )

    parser.add_argument(
        "-ig",
        "--input-glob",
        default="**/*",
        help="Glob pattern for selecting input files relative to input path",
    )

    parser.add_argument(
        "-if",
        "--input-format",
        default="text/turtle",
        help="Input RDF format",
    )

    parser.add_argument(
        "-op",
        "--output-path",
        help="Output file path",
    )

    parser.add_argument(
        "-of",
        "--output-format",
        help="Output RDF format",
    )

    return parser


def make_service(args: Namespace) -> Aggregator:
    """Make the service with the passed args"""
    return Aggregator(
        input_path=args.input_path,
        globs={args.input_glob: args.input_fmt},
        output_path=args.output_path,
        output_format=args.output_fmt,
    )


def _main(*args_list) -> bool:
    """The main entry point to this module."""
    args = get_arg_parser().parse_args(args_list)
    toreturn = False
    try:
        aggregator = make_service(args)
        r = aggregator.process()
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
