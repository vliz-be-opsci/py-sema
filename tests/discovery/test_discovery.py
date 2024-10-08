import logging
import os
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
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
        "http://localhost:8000/card.ttl",
        "text/turtle",
        86,
    ),
    (
        "http://localhost:8000/mrgid.jsonld",
        "application/ld+json",
        99,
    ),
    (
        "http://localhost:8000/homepage.html",
        "text/turtle",
        83,
    ),
    (
        "http://localhost:8000/rocrate.html",
        "application/json",
        532,
    ),
]

REMOTE_CASES: List[Tuple[str, str, int]] = [
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
        115,
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


# Wrap direct cases into signposted cases
SIGNPOSTED_CASES = list()
for uri, mime, length in DIRECT_CASES:
    link = wrap_signpost_uri(uri)
    SIGNPOSTED_CASES.append((link, mime, length))

ALL_CASES = REMOTE_CASES + SIGNPOSTED_CASES


class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def guess_type(self, path):
        ext = os.path.splitext(path)[1]
        return HTTPD_EXTENSION_MAP.get(ext, super().guess_type(path))


@pytest.fixture(scope="module", autouse=True)
def http_server():
    # Change working directory to the test files directory
    os.chdir(TEST_FILES_DIR)

    # Set up and start the HTTP server
    handler = CustomHTTPRequestHandler
    httpd = HTTPServer(("0.0.0.0", 8000), handler)

    thread = threading.Thread(target=httpd.serve_forever)
    thread.start()

    yield

    httpd.shutdown()
    thread.join()


@pytest.mark.parametrize("uri, mime, length", ALL_CASES)
def test_discovery_case(uri, mime, length):
    graph = discover_subject(uri, mimetypes=[mime])
    assert isinstance(graph, Graph)
    assert len(graph) > 0
