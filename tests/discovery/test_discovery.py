import logging
import os
from typing import Dict, List, Tuple

import pytest
from rdflib import Graph
from uritemplate import URITemplate

from sema.discovery import discover_subject

log = logging.getLogger(__name__)

# Directory where test files are stored
TEST_FILES_DIR = os.path.join(os.path.dirname(__file__), "test_files")

# MIME type map
HTTPD_EXTENSION_MAP: Dict[str, str] = {
    ".txt": "text/plain",
    ".jsonld": "application/ld+json",
    ".ttl": "text/turtle",
    ".html": "text/html",
}

# Update DIRECT_CASES to use local URIs with a domain
DIRECT_CASES: List[Tuple[str, str, int]] = [
    (
        "card.ttl",
        "text/turtle",
        86,
    ),
    (
        "mrgid.jsonld",
        "application/ld+json",
        99,
    ),
    (
        "homepage.html",
        "text/turtle",
        83,
    ),
    (
        "rocrate.html",
        "application/json",
        532,
    ),
]


def wrap_signpost_uri(uri: str) -> str:
    urit = URITemplate("https://httpbin.org/response-headers{?Link*}")
    link = urit.expand(dict(Link=f"<{uri}>; rel=describedby"))
    return link


@pytest.mark.fixture("httpd_server_base")
def test_discovery_cases(httpd_server_base: str):
    assert httpd_server_base

    for to_search, mime, length in DIRECT_CASES:
        full_uri = f"{httpd_server_base}{to_search}"
        wrapped_uri = wrap_signpost_uri(full_uri)
        graph = discover_subject(full_uri, mimetypes=[mime])
        assert isinstance(graph, Graph)
        assert len(graph) == length

        graph = discover_subject(wrapped_uri, mimetypes=[mime])
        assert isinstance(graph, Graph)
        assert len(graph) == length
