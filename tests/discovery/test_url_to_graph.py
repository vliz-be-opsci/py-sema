import logging

from rdflib import Graph

from sema.commons.fileformats import mime_to_format
from sema.discovery.url_to_graph import get_graph_for_format

log = logging.getLogger(__name__)


def test_ctype_to_rdf_format():
    assert mime_to_format("application/ld+json") == "json-ld"
    assert mime_to_format("text/turtle") == "turtle"
    assert mime_to_format("application/json") is None
    assert mime_to_format("application/octet-stream") is None
    assert mime_to_format("text/html") == "html"
    assert mime_to_format("application/rdf+xml") == "xml"
    assert mime_to_format("text/n3") == "n3"
    assert mime_to_format("application/n-triples") == "nt"


# ttl file
# jsonld file
# html file with ttl file in head as full script
# html file with jsonld file in head as script link
# TODO use @pytest.mark.parametrize()

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
        "length": 532,
        "format": "application/json",
    },
    # add more test cases as needed
]


def test_download_uri_cases():
    for case in test_cases:
        uri = case["uri"]
        format = case["format"]
        log.debug(f"{format}")
        # TODO use the new service in stead
        # and/or rewrite the previous get_graph_ method to do so as a migration path
        graph = get_graph_for_format(uri, formats=[format])
        assert isinstance(graph, Graph)
        assert len(graph) > 0
        assert len(graph) == case["length"]
        # Add more assertions as needed
