# -*- coding: utf-8 -*-
import sys
from logging import getLogger
from typing import Iterable

from sema.commons.cli import Namespace, SemaArgsParser
from sema.commons.fileformats import to_mimetype
from sema.discovery import Discovery

log = getLogger(__name__)


def get_arg_parser():
    """
    Defines the arguments to this script by using Python's
    [argparse](https://docs.python.org/3/library/argparse.html)
    """
    parser = SemaArgsParser(
        "sema-get",
        "Discovery gets structured content associated to the subject-uri",
    )

    # args.url
    # is either first positional argument or -u/--url,
    parser.add_argument(
        "url",
        nargs="?",
        action="store",
        metavar="URL",
        help="The subject URI to discover",
    )
    parser.add_argument(
        "-u",
        "--url",
        metavar="URL",
        action="store",
        help="The subject URI to discover",
    )

    # args.request_mimes
    # -m/--request-mimes can appear multiple times and use ',' to separate
    parser.add_argument(
        "-m",
        "--request-mimes",
        metavar="MIME",
        action="append",
        help="Comma-separated list of acceptable MIME types. Can be repeated.",
    )

    # args.read_uri
    # -r/--read-uri
    parser.add_argument(
        "-r",
        "--read-uri",
        metavar="URI",
        action="store",
        help="read-URI to triple store to use",
    )

    # args.write_uri
    # -w/--write-uri
    parser.add_argument(
        "-w",
        "--write-uri",
        metavar="URI",
        action="store",
        help="write-URI to triple store to use",
    )

    # args.graph
    # -g/--graph
    parser.add_argument(
        "-g",
        "--graph",
        metavar="URI",
        action="store",
        help="Named graph to use in the triple store",
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
        action="store",
        help="Specifies the output format",
    )

    return parser


def normalise_mime_type_requests(request_mimes: Iterable | str) -> str:
    if not request_mimes:
        return None
    # else
    if isinstance(request_mimes, str):
        if "," not in request_mimes:
            return to_mimetype(request_mimes)
        # else
        request_mimes = [request_mimes]
    # treat as sequence, possibly some of them in single string format
    request_mimes = SemaArgsParser.args_joined(request_mimes)
    request_mimes = request_mimes.split(",") if request_mimes else []
    return ",".join({normalise_mime_type_requests(mt) for mt in request_mimes})


def make_service(args: Namespace) -> Discovery:
    """Make the service with the passed args"""
    return Discovery(
        subject_uri=args.url,
        request_mimes=normalise_mime_type_requests(args.request_mimes),
        read_uri=args.read_uri,
        write_uri=args.write_uri,
        named_graph=args.graph,
        output_file=args.output,
        output_format=args.format,
    )


def main(*args_list) -> bool:
    args = get_arg_parser().parse_args(args_list)

    discovery = make_service(args)
    result, trace = discovery.process()
    return bool(result)


if __name__ == "__main__":
    success: bool = main(*sys.argv[1:])
    sys.exit(0 if success else 1)
