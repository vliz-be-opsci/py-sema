import sys
import os
from logging import getLogger
from pathlib import Path

from sema.commons.cli import Namespace, SemaArgsParser
from sema.commons.glob import getMatchingGlobPaths
from sema.ro.creator import ROCreator

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
        "-e",
        "--load-os-env",
        default=False,
        action="store_true",
        help=(
            "Load OS environment variables for use in !resolve."
        ),
    )

    parser.add_argument(
        "root",
        action="store",
        nargs="?",
        help=(
            "Path of the rocrate to work on. "
            "This where roc-*yml is found. "
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
            "Defaults to ro-crate-metadata.json."
            "Can be absolute or relative to the specified root."
        ),
    )
    return parser


def _find_rocyml(root: str) -> tuple[str, str]: # TODO update signature
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

    return root, rocyml


def make_service(args: Namespace) -> ROCreator:
    """Make the service with the passed args"""
    root = args.root or "."  # default to current folder
    root, rocyml = _find_rocyml(root)
    return ROCreator(
        blueprint_path=root / rocyml,
        blueprint_env=os.environ.copy() if args.load_os_env else {},
        rocrate_path=root,
        force=args.force,
    )


def _main(*args_list) -> bool:
    """The main entry point to this module."""
    args = get_arg_parser().parse_args(args_list)
    try:
        roc = make_service(args)
        roc.process(rocrate_file_name=args.out)
        log.debug("processing done")
        return True
    except Exception as e:
        log.exception("sema.ro.creator processing failed", exc_info=e)
        return False

def main():
    success: bool = _main(*sys.argv[1:])
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
