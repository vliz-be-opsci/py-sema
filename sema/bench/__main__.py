import sys
from logging import getLogger

from sema.bench.core import Sembench
from sema.commons.cli import Namespace, SemaArgsParser

log = getLogger(__name__)


def get_arg_parser() -> SemaArgsParser:
    """
    Defines the arguments to this script using Python's argparse module.

    See the argparse docs: https://docs.python.org/3/library/argparse.html
    """
    parser = SemaArgsParser(
        "sema-bench",
        "Bench is a tool to orchestrate the execution of multiple services "
        "from py-sema.",
    )

    # locations , dict of key value pairs of locations in filesystem
    parser.add_argument(
        "-loc",
        "--locations",
        action="store",
        default=None,
        help=(
            "Dict of keyed paths to various filesystem locations with specific"
            "roles, such as 'home', 'input', 'output', ..."
        ),
    )

    # config path
    parser.add_argument(
        "-c",
        "--config-path",
        action="store",
        required=True,
        help="Path to the sembench configuration parent folder.",
    )

    # sembench config name (default: sembench.yaml)
    parser.add_argument(
        "-n",
        "--config-name",
        action="store",
        default="sembench.yaml",
        help="Name of the sembench config file. (default: sembench.yaml)",
    )

    # scheduler interval
    parser.add_argument(
        "--interval",
        action="store",
        default=1000,
        type=int,
        help="Interval in seconds to run the scheduler. (default: 1000)",
    )

    # boolean to watch config file for changes default False
    parser.add_argument(
        "-w",
        "--watch",
        action="store_true",
        help="Watch the config file for changes.",
    )

    # fail fast boolean
    parser.add_argument(
        "-ff",
        "--fail-fast",
        action="store_true",
        help="Fail fast if any service fails.",
    )

    return parser


def make_service(args: Namespace) -> Sembench:
    return Sembench(
        locations=args.locations,
        sembench_config_file_name=args.config_name,
        scheduler_interval_seconds=args.interval,
        watch_config_file=args.watch,
        fail_fast=args.fail_fast,
    )


def _main(*args_list: str) -> bool:
    args = get_arg_parser().parse_args(args_list)

    try:
        sembench = make_service(args)
        sembench.run()
    except Exception:
        log.exception("sema.bench processing failed")
        return False
    return True


def main() -> None:
    success: bool = _main(*sys.argv[1:])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
