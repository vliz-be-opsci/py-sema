import logging

from conftest import run_single_test
from rdflib import Graph

from sema.discovery.url_to_graph import (
    ctype_to_rdf_format,
    get_graph_for_format,
)

log = logging.getLogger(__name__)


def test_ctype_to_rdf_format():
    assert ctype_to_rdf_format("application/ld+json") == "json-ld"
    assert ctype_to_rdf_format("text/turtle") == "turtle"
    assert ctype_to_rdf_format("application/json") is None
    assert ctype_to_rdf_format("application/octet-stream") is None
    assert ctype_to_rdf_format("text/html") is None


# ttl file
# jsonld file
# html file with ttl file in head as full script
# html file with jsonld file in head as script link
test_cases = [
    {
        "uri": "https://www.w3.org/People/Berners-Lee/card.ttl",
        "length": 86,
        "format": "text/turtle",
    },
    {
        "uri": "https://marineregions.org/mrgid/3293.jsonld",
        "length": 99,
        "format": "application/ld+json",
    },
    {
        "uri": "https://data.arms-mbon.org/",
        "length": 112,
        "format": "text/turtle",
    },
    {
        "uri": "https://data.arms-mbon.org/data_release_001/latest/#",
        "length": 514,
        "format": "application/json",
    },  # add more test cases as needed
]


def test_download_uri_cases():
    for case in test_cases:
        uri = case["uri"]
        format = case["format"]
        log.debug(f"{format}")
        graph = get_graph_for_format(uri, formats=[format])
        assert isinstance(graph, Graph)
        assert len(graph) > 0
        assert len(graph) >= case["length"]
        # Add more assertions as needed


if __name__ == "__main__":
    run_single_test(__file__)
