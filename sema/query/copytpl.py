import shutil
from argparse import ArgumentParser
from pathlib import Path

DEFAULT_TEMPLATES_FOLDER = (
    Path(__file__).parent.absolute() / "sparql_templates"
)
template_path: str = DEFAULT_TEMPLATES_FOLDER.absolute().as_posix()


def copy_embedded_templates_to(
    destination: Path, excludes: list[str] = []
) -> None:
    """Copy the embedded sparql templates to a destination folder.

    Args:
        destination (Path): The destination folder.
    """
    shutil.copytree(
        DEFAULT_TEMPLATES_FOLDER,
        destination,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(*excludes),
    )


def main_cli_install_templates() -> None:
    """CLI entry point to install the embedded templates to a folder."""

    parser = ArgumentParser(
        description="Install embedded SPARQL templates to a folder."
    )
    parser.add_argument(
        "destination",
        metavar="PATH",
        type=Path,
        help="The destination folder to copy the templates to.",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        type=str,
        metavar="PATTERN",
        nargs="*",
        default=[],
        help="List of glob patterns to exclude from copying.",
    )
    args = parser.parse_args()
    print(
        f"Copying Embedded Templates to {args.destination} "
        f"- excluding: {args.exclude}"
    )
    copy_embedded_templates_to(args.destination, args.exclude)
    print("done")


if __name__ == "__main__":
    main_cli_install_templates()
