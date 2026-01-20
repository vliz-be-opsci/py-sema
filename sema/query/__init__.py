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

__all__ = ["DefaultSparqlBuilder", "GraphSource", "QueryResult"]
