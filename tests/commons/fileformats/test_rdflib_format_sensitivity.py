"""
Not really a test, but a demonstration of how rdflib's format parameter is to be used.
Making sure we understand the sensitivity (or lack thereof) inside rdflib about 
using mimetypes (like 'text/turtle') 
in stead of format names (like 'turtle').
"""
import pytest
from conftest import TEST_INPUT_FOLDER, make_sample_graph
from rdflib import Graph
from pathlib import Path
from sema.commons.fileformats import mime_from_filename, format_from_filename


@pytest.mark.parametrize("test_path, format, mimetype", [
    (TEST_INPUT_FOLDER / "issue-bnodes.ttl", "turtle", "text/turtle"),
    (TEST_INPUT_FOLDER / "issue-bnodes.jsonld", "json-ld", "application/ld+json"),
])
def test_rdflib_parse_format_sensitivity(test_path: Path, format: str, mimetype: str):
    assert format_from_filename(test_path) == format
    assert mime_from_filename(test_path) == mimetype

    # parse by format
    gf: Graph = Graph().parse(str(test_path), format=format)
    assert len(gf) > 0

    # parse by mimetype
    gm: Graph = Graph().parse(str(test_path), format=mimetype)
    assert len(gm) > 0

    # it all is the same!
    assert len(gf) == len(gm)


@pytest.mark.parametrize("suffix", [
    ".ttl",
    ".jsonld",
])
@pytest.mark.usefixtures("outpath")
def test_rdfib_serialize_format_insenstivity(suffix, outpath):
    g: Graph = make_sample_graph([1, "a", True])

    # write by format
    outbyfmt = outpath / f"test_ser_byfmt{suffix}"
    format = format_from_filename(outbyfmt)
    g.serialize(str(outbyfmt), format=format)

    # write by mime
    outbymt = outpath / f"test_ser_bymt{suffix}"
    mimetype = mime_from_filename(outbymt)
    g.serialize(str(outbymt), format=mimetype)

    # no difference!
    assert outbyfmt.read_text() == outbymt.read_text()
