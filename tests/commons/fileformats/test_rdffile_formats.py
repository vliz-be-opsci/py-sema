import pytest

from sema.commons.fileformats import mime_from_filepath


@pytest.mark.parametrize(
    "suffix, mime",
    [
        (".ttl", "text/turtle"),
        (".rdf", "application/rdf+xml"),
        (".jsonld", "application/ld+json"),
    ],
)
def test_factory_choice(suffix, mime):
    fname = f"whatever-file-name{suffix}"
    assert mime_from_filepath(fname) == mime
