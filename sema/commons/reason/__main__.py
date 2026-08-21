# -*- coding: utf-8 -*-
import sys
from logging import getLogger

from sema.commons.cli import Namespace, SemaArgsParser
from sema.commons.reason import Reasoner

log = getLogger(__name__)


def get_arg_parser() -> SemaArgsParser:
    """Create and configure the argument parser for sema-reason."""
    parser = SemaArgsParser(
        "sema-reason",
        "Execute SPARQL CONSTRUCT queries against RDF sources "
        "and output the reasoned graph.",
    )

    parser.add_argument(
        "-i",
        "--input-path",
        default=".",
        help=(
            "Input working directory for resolving relative file "
            "and query paths"
        ),
    )

    parser.add_argument(
        "-s",
        "--source",
        action="append",
        help=(
            "Source RDF file, folder, or glob pattern "
            "(can be specified multiple times)"
        ),
    )

    parser.add_argument(
        "-q",
        "--query",
        action="append",
        help=(
            "SPARQL CONSTRUCT query string, query file (.sparql/.rq), "
            "or folder/glob (can be specified multiple times)"
        ),
    )

    parser.add_argument(
        "-o",
        "--output-path",
        help="Output file path",
    )

    parser.add_argument(
        "-fmt",
        "--output-format",
        default="text/turtle",
        help="Output RDF format (default: text/turtle)",
    )

    return parser


def make_service(args: Namespace) -> Reasoner:
    """Make the service with the passed args"""
    return Reasoner(
        input_path=args.input_path,
        sources=args.source,
        queries=args.query,
        output_path=args.output_path,
        output_format=args.output_format,
    )


def _main(*args_list) -> bool:
    """The main entry point to this module."""
    args = get_arg_parser().parse_args(args_list)
    toreturn = False
    try:
        reasoner = make_service(args)
        r = reasoner.process()
        log.debug("processing done")
        toreturn = r.success
    except Exception as e:
        log.exception("sema.commons.reason processing failed", exc_info=e)
    return toreturn


def main():
    """Main CLI entry point for sema-reason."""
    success: bool = _main(*sys.argv[1:])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
