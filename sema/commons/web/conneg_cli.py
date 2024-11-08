import sys
from logging import getLogger

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
        "Conneg Evaluator checks the url for available conneg features",
    )

    # args.url
    # first positional argument (optional)
    parser.add_argument(
        "url",
        nargs="?",
        action="store",
        metavar="URL",
        help="The URL to evaluate",
    )
    # args.url_option
    # -u/--url
    parser.add_argument(
        "-u",
        "--url",
        dest="url_option",
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
        help=(
            "Comma-separated list of acceptable MIME;PROFILE variants. "
            "Can be repeated."
        ),
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
        url=args.url or args.url_option,
        request_variants=SemaArgsParser.args_joined(args.request_variants),  # type: ignore
    )


def _main(*args_list) -> bool:
    args = get_arg_parser().parse_args(args_list)

    connegeval = make_service(args)
    result = connegeval.process()
    # export the result
    if len(result) == 0:
        log.warning(
            f"No variants obtained for {args.url}. " "No result to output."
        )
    else:
        if args.output:
            connegeval.export_result(args.output, args.format)
    # export the trace if flag is set
    if args.dump:
        connegeval.dump_variants(args.dump)
    return bool(result)


def main():
    success: bool = _main(*sys.argv[1:])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
