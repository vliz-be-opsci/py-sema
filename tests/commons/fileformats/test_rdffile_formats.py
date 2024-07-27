import pytest

from sema.commons.fileformats import mime_from_filepath, mime_to_format


@pytest.mark.parametrize(
    "suffix, mime",
    [
        (".ttl", "text/turtle"),
        (".rdf", "application/rdf+xml"),
        (".jsonld", "application/ld+json"),
    ],
)
def test_filepath_mime_detection(suffix, mime):
    fname = f"whatever-file-name{suffix}"
    assert mime_from_filepath(fname) == mime


def test_mime_to_format():
    assert mime_to_format("application/ld+json") == "json-ld"
    assert mime_to_format("text/turtle") == "turtle"
    assert mime_to_format("application/json") is None
    assert mime_to_format("application/octet-stream") is None
    assert mime_to_format("text/html") == "html"
    assert mime_to_format("application/rdf+xml") == "xml"
    assert mime_to_format("text/n3") == "n3"
    assert mime_to_format("application/n-triples") == "nt"
