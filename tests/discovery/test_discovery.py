import logging

import pytest
from rdflib import Graph

from sema.discovery import discover_subject

log = logging.getLogger(__name__)


@pytest.mark.parametrize(
    "uri, mime, length",
    [
        ("https://www.w3.org/People/Berners-Lee/card.ttl", "text/turtle", 86),
        (
            "https://marineregions.org/mrgid/3293.jsonld",
            "application/ld+json",
            99,
        ),
        ("https://data.arms-mbon.org/", "text/turtle", 112),
        (
            "https://data.arms-mbon.org/data_release_001/latest/#",
            "application/json",
            532,
        ),
    ],
)
def test_discovery_case(uri, mime, length):
    graph = discover_subject(uri, mimetypes=[mime])
    assert isinstance(graph, Graph)
    assert len(graph) > 0
    assert len(graph) == length
    # Add more assertions as needed
