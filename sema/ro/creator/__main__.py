import sys
from logging import getLogger
from pathlib import Path

from sema.commons.cli import Namespace, SemaArgsParser
from sema.commons.glob import getMatchingGlobPaths
from sema.ro.creator.rocreator import Roc

log = getLogger(__name__)


def get_arg_parser() -> SemaArgsParser:
    """
    Defines the arguments to this script by using Python's
    [argparse](https://docs.python.org/3/library/argparse.html)
    """
    parser = SemaArgsParser(
        "sema-roc",
        "Ro-Creator produces ro-crate-metadata.json from roc-me.yml files.",
    )

    parser.add_argument(
        "-L",
        "--list",
        action="store_true",
        required=False,
        help="List all the available strategies. Prevents actual build.",
    )

    parser.add_argument(
        "-m",
        "--make",
        metavar="strategy",  # meaning of the argument
        action="store",
        help="Generates a ro-*yml file for the given strategy.",
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
        "root",
        action="store",
        nargs="?",
        help=(
            "Path of the rocrate to work on. "
            "This where roc-*yml is found or (in case of -m) placed. "
            "This is where ro-crate-metadata.json is placed. "
            "Defaults to the current working directory."
        ),
    )

    parser.add_argument(
        "out",
        action="store",
        nargs="?",
        help=(
            "Name of output-file to produce. "
            "Defaults to ro-crate-metadata.json resp. "
            "roc-me.yml (for the -m case). "
            "Can be absolute or relative to the specified root."
        ),
    )
    return parser


def _find_rocyml(root: str) -> tuple[str, str]:
    """Find the roc yml file in the root folder"""
    root = Path(root)
    rocyml = Path("roc-me.yml")
    if not root.exists():
        raise FileNotFoundError(f"root path {root} does not exist")

    if root.is_dir():
        # find roc-*yml file -- warn if more then one, use if only one
        rocfiles: list[Path] = getMatchingGlobPaths(root, "roc-*.yml")
        if len(rocfiles) > 1:
            raise ValueError(
                f"multiple roc yml files found in {root}, cannot proceed"
            )
        # else
        if len(rocfiles) < 1:
            raise FileNotFoundError(f"no roc yml file found in {root}")
        # else exactly one is how we like it
        rocyml = rocfiles[0]

    elif root.is_file():
        rocyml = root
        root = root.parent
        rocyml = rocyml.relative_to(root)

    # make into str paths again before return
    return str(root), str(rocyml)


def make_service(args: Namespace) -> Roc:
    """Make the service with the passed args"""
    root = args.root or "."  # default to current folder
    out = args.out or ("roc-me.yml" if args.make else "ro-crate-metadata.json")
    root, rocyml = _find_rocyml(root)
    return Roc(
        root=root,
        rocyml=rocyml,
        out=out,
        force=args.force,
    )


def _main(*args_list) -> bool:
    """The main entry point to this module."""
    args = get_arg_parser().parse_args(args_list)
    toreturn = False
    try:
        if args.list:
            # list all the available strategies
            # prevent actual build
            log.debug("listing all the available strategies")
            ...
            return
        # else
        if args.make:
            # generate the yml file for this particular strategy
            # root and out are used to determine the location
            # of the yml file to produce
            strategy_name: str = args.make
            log.debug(
                f"generating the yml file for the given {strategy_name=}"
            )
            ...
            return
        # else
        roc = make_service(args)
        r = roc.process()
        log.debug("processing done")
        toreturn = r.success
    except Exception as e:
        log.exception("sema.ro.creator processing failed", exc_info=e)
    return toreturn


def main():
    success: bool = _main(*sys.argv[1:])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
