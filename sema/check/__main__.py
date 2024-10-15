from logging import getLogger

from sema.check import Check
from sema.commons.cli import Namespace, SemaArgsParser

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
    log.info("Running sema-check with args: %s", args_list)
    args = get_arg_parser().parse_args(args_list)

    try:
        check = make_service(args)
        r = check.process()
        print(f"Finished running tests: {r}")
        return bool(r)
    except (ValueError, IOError) as e:
        log.exception("An error occurred: %s", e)
        return False


def main(args: list[str] | None = None) -> None:
    log.debug("Running sema-check with args: %s", args[1:] if args else [])
    success: bool = _main(*args[1:])
    log.debug("Finished running sema-check")
    log.info("Success: %s", success)
    # sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
