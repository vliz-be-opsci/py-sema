# your_submodule/__main__.py

# your_submodule/cli.py
import sys
from logging import getLogger

from sema.commons.cli import Namespace, SemaArgsParser
from sema.check import Check

log = getLogger(__name__)


def get_arg_parser() -> SemaArgsParser:
    """
    Defines the arguments to this script by using Python's
    [argparse](https://docs.python.org/3/library/argparse.html)
    """
    parser = SemaArgsParser(
        "sema-check",
        "Run tests based on YAML configurations.",
    )

    parser.add_argument(
        "-i",
        "--input_folder",
        action="store",
        required=True,
        help="Path to the folder containing YAML files.",
    )

    parser.add_argument(
        "-o",
        "--output",
        choices=["csv", "html", "yml"],
        default="csv",
        help="Output format for the test results.",
    )

    return parser


def make_service(args: Namespace) -> Check:
    return Check(
        input_folder=args.input_folder,
        output=args.output,
    )


def _main(*args_list) -> bool:
    log.info(f"Running sema-check with args: {args_list}")
    args = get_arg_parser().parse_args(args_list)

    try:
        check = make_service(args)
        r = check.process()
        print(f"Finished running tests: {r}")
        return bool(r)
    except Exception as e:
        log.error(f"An error occurred: {e}")
        return False


def main(args=None):
    log.debug(f"Running sema-check with args: {args[1:]}")
    success: bool = _main(*args[1:])
    log.debug(f"Finished running sema-check")
    log.info(f"Success: {success}")
    # sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
