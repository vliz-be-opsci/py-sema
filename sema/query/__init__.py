"""query

.. module:: query
    :synopsis: Extracting table data from knowwledge-graphs
        using sparql templates

.. moduleauthor:: "Open Science Team VLIZ vzw" <opsci@vliz.be>
"""

import logging
from pathlib import Path

from sema.commons.j2 import J2RDFSyntaxBuilder as DefaultSparqlBuilder

from .query import GraphSource, QueryResult

log = logging.getLogger(__name__)
DEFAULT_TEMPLATES_FOLDER = (
    Path(__file__).parent.absolute() / "sparql_templates"
)


def copy_embedded_templates_to(
    destination: Path, excludes: list[str] = []
) -> None:
    """Copy the embedded sparql templates to a destination folder.

    Args:
        destination (Path): The destination folder.
    """
    import shutil

    shutil.copytree(
        DEFAULT_TEMPLATES_FOLDER,
        destination,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns(*excludes),
    )


template_path: str = DEFAULT_TEMPLATES_FOLDER.absolute().as_posix()
install_templates = copy_embedded_templates_to

__all__ = [
    "DefaultSparqlBuilder",
    "GraphSource",
    "QueryResult",
    "template_path",
    "install_templates",
]
