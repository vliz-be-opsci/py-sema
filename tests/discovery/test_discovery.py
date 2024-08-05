import logging

import pytest
from rdflib import Graph
from uritemplate import URITemplate
from typing import List, Tuple

from sema.discovery import discover_subject

log = logging.getLogger(__name__)


DIRECT_CASES: List[Tuple[str, str, int]] = [
    (
        "https://www.w3.org/People/Berners-Lee/card.ttl",
        "text/turtle",
        86,
    ),
    (
        "https://marineregions.org/mrgid/3293.jsonld",
        "application/ld+json",
        99,
    ),
    (
        "https://data.arms-mbon.org/",
        "text/turtle",
        112,
    ),
    (
        "https://data.arms-mbon.org/data_release_001/latest/#",
        "application/json",
        532,
    ),
]


def wrap_signpost_uri(uri: str) -> str:
    urit = URITemplate("https://httpbin.org/response-headers{?Link*}")
    link = urit.expand(dict(Link=f"<{uri}>; rel=describedby"))
    return link


# wrap direct cases into signposted cases
SIGNPOSTED_CASES = list()
for uri, mime, length in DIRECT_CASES:
    link = wrap_signpost_uri(uri)
    SIGNPOSTED_CASES.append((link, mime, length))

ALL_CASES = DIRECT_CASES + SIGNPOSTED_CASES


@pytest.mark.parametrize("uri, mime, length", ALL_CASES)
def test_discovery_case(uri, mime, length):
    graph = discover_subject(uri, mimetypes=[mime])
    assert isinstance(graph, Graph)
    assert len(graph) > 0
    assert len(graph) == length
    # Add more assertions as needed
