import pytest

from sema.commons.fileformats import suffix_for_mime


@pytest.mark.parametrize(
    "mime, suffix",
    (
        ("text/turtle", ".ttl"),
        ("text/plain", ".txt"),
        ("application/ld+json", ".jsonld"),
        ("application/json", ".json"),
        ("application/rdf+xml", ".rdf"),
        ("text/html", ".html"),
        ("text/xml", ".xml"),
        ("text/n3", ".n3"),
        ("text/anything", ".txt"),
        ("unknown/whatever", ".bin"),
    ),
)
def test_sfx_from_mime(mime, suffix):
    result = suffix_for_mime(mime)
    assert result == suffix, f"expected {suffix=} for {mime=} got {result=}"
