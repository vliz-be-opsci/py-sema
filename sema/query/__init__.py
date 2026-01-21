"""query

.. module:: query
    :synopsis: Extracting table data from knowwledge-graphs
        using sparql templates

.. moduleauthor:: "Open Science Team VLIZ vzw" <opsci@vliz.be>
"""

import logging

from sema.commons.j2 import J2RDFSyntaxBuilder as DefaultSparqlBuilder

from .copytpl import (
    DEFAULT_TEMPLATES_FOLDER,
    copy_embedded_templates_to,
    template_path,
)
from .query import GraphSource, QueryResult

log = logging.getLogger(__name__)
install_templates = copy_embedded_templates_to

__all__ = [
    "DefaultSparqlBuilder",
    "GraphSource",
    "QueryResult",
    "template_path",
    "install_templates",
    "DEFAULT_TEMPLATES_FOLDER",
]
