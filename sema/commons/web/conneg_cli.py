import sys
from logging import getLogger
from typing import Iterable

from sema.commons.cli import Namespace, SemaArgsParser
from sema.commons.web import ConnegEvaluation

log = getLogger(__name__)


def get_arg_parser():
    """
    Defines the arguments to this script by using Python's
    [argparse](https://docs.python.org/3/library/argparse.html)
    """
    parser = SemaArgsParser(
        "sema-conneg",
        "Conneg Evaluator checks the conneg features available on the passed url",
    )

    # args.url
    # is either first positional argument or -u/--url,
    parser.add_argument(
        "url",
        nargs="?",
        action="store",
        metavar="URL",
        help="The URL to evaluate",
    )
    parser.add_argument(
        "-u",
        "--url",
        metavar="URL",
        action="store",
        help="The URL to evaluate",
    )

    # args.request_variants
    # -v/--request-variants can appear multiple times and use ',' to separate
    parser.add_argument(
        "-v",
        "--request-variants",
        metavar="[MIME[;PROFILE]?,]+",
        action="append",
        help="Comma-separated list of acceptable MIME;PROFILE variants. Can be repeated.",
    )

    # args.output
    # -o/--output
    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE",
        action="store",
        help="Specifies where to write the output, '-' for stdout",
    )

    # args.format
    # -f/--format
    parser.add_argument(
        "-f",
        "--format",
        metavar="FORMAT",
        default="csv",
        action="store",
        help="Specifies the output format (csv default)",
    )

    # args.dump
    # -d/--dump
    parser.add_argument(
        "-d",
        "--dump",
        metavar="PATH",
        action="store",
        help="Location to dump all the obtained variants",
    )

    return parser


def make_service(args: Namespace) -> ConnegEvaluation:
    """Make the service with the passed args"""
    return ConnegEvaluation(
        url=args.url,
        request_variants=SemaArgsParser.args_joined(args.request_variants),
    )


def main(*args_list) -> bool:
    args = get_arg_parser().parse_args(args_list)

    connegeval = make_service(args)
    result = connegeval.process()
    # export the result
    if args.output:
        connegeval.export_result(args.output, args.format)
    # export the trace if flag is set
    if args.dump:
        connegeval.dump_variants(args.dump)
    return bool(result)


if __name__ == "__main__":
    success: bool = main(*sys.argv[1:])
    sys.exit(0 if success else 1)
