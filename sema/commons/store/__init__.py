"""store

.. module:: store
:platform: Unix, Windows
:synopsis: A library for creating and interacting with RDF stores

.. moduleauthor:: "Open Science Team VLIZ vzw" <opsci@vliz.be>
"""

from .build import create_rdf_store
from .store import (
    GraphNameMapper,
    MemoryRDFStore,
    RDFStore,
    URIRDFStore,
    timestamp,
)

__all__ = [
    "RDFStore",
    "MemoryRDFStore",
    "URIRDFStore",
    "timestamp",
    "create_rdf_store",
    "GraphNameMapper",
]
