# -*- coding: utf-8 -*-
import sys
from logging import getLogger

from sema.commons.cli import Namespace, SemaArgsParser
from sema.subyt import Subyt

log = getLogger(__name__)


def get_arg_parser() -> SemaArgsParser:
    """
    Defines the arguments to this script by using Python's
    [argparse](https://docs.python.org/3/library/argparse.html)
    """
    parser = SemaArgsParser(
        "sema-subyt",
        "SuByT produces triples by applying a template",
    )

    parser.add_argument(
        "-n",
        "--name",
        action="store",
        required=True,
        help="Speficies the name of the template to use",
    )

    parser.add_argument(
        "-s",
        "--set",
        nargs=2,  # each -s should have 2 arguments
        metavar=("KEY", "FILE"),  # meaning/purpose of those arguments
        action="append",  # multiple -s can be combined
        help=(
            "Multiple entries will add different sets "
            'under sets["KEY"] to the templating process'
        ),
    )

    parser.add_argument(
        "-v",
        "--var",
        nargs=2,  # each -v should have 2 arguments
        metavar=("NAME", "VALUE"),  # meaning/purpose of those arguments
        action="append",  # multiple -v can be combined
        help=(
            "Multiple entries will add different named "
            "variables to the templating process"
        ),
    )

    parser.add_argument(
        "-t",
        "--templates",
        metavar="FOLDER",  # meaning of the argument
        action="store",
        default=".",  # local working directory
        help="Passes the context folder holding all the templates",
    )

    parser.add_argument(
        "-i",
        "--input",
        metavar="FILE",  # meaning of the argument
        action="store",
        help=(
            "Specifies the base input set to run over. "
            "Shorthand for -s _ FILE"
        ),
    )

    parser.add_argument(
        "-o",
        "--output",
        metavar="FILE|PATTERN",  # meaning of the argument
        action="store",
        help="Specifies where to write the output, can use {uritemplate}.",
    )

    parser.add_argument(
        "-f",
        "--force",
        default=False,
        action="store_true",
        help=(
            "Force writing output, do not check "
            "if output files already exist."
        ),
    )

    parser.add_argument(
        "-m",
        "--mode",
        metavar=" (no-)it(eration), (no-)ig(norecase), (no-)fl(atten) ",
        action="store",
        help="""Modifies the mode of iteration:
                1. it (default) vs. no-it: apply template for each
                                                iterated row in the input set
                                           vs. apply it only once once for
                                                the complete input set;
                2. ig vs. no-ig: to be implemented;
                3. fl vs. no-fl: to be implemented.""",
    )

    parser.add_argument(
        "-r",
        "--allow-repeated-sink-paths",
        default=False,
        action="store_true",
        help=("Allow repeated sink paths in case of duplicated data items."),
    )

    parser.add_argument(
        "-c",
        "--conditional",
        default=False,
        action="store_true",
        help=("Execute only when input has been updated. Abort otherwise."),
    )

    return parser


def make_service(args: Namespace) -> Subyt:
    """Make the service with the passed args"""
    return Subyt(
        template_name=args.name,
        template_folder=args.templates,
        source=args.input,
        extra_sources=SemaArgsParser.args_to_dict(args.set),
        sink=args.output,
        overwrite_sink=args.force,
        allow_repeated_sink_paths=args.allow_repeated_sink_paths,
        conditional=args.conditional,
        variables=SemaArgsParser.args_to_dict(args.var),
        mode=args.mode,
    )


def _main(*args_list) -> bool:
    """The main entry point to this module."""
    args = get_arg_parser().parse_args(args_list)
    toreturn = False
    try:
        subyt = make_service(args)
        r = subyt.process()
        log.debug("processing done")
        toreturn = r.success
    except Exception as e:
        log.exception("sema.subyt processing failed", exc_info=e)
    finally:
        if subyt:
            subyt._sink.close()  # TODO investigate suspicious location for this
    return toreturn


def main():
    success: bool = _main(*sys.argv[1:])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
