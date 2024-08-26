import pytest

from sema.commons.web.download_to_file import extract_name_parts


@pytest.mark.parametrize(
    "url, id",
    (
        ("http://example.org", ""),
        ("http://example.org/", ""),
        ("http://example.org/1", "1"),
        ("http://example.org/1/a", "1-a"),
        ("http://example.org/1/a.txt", "1-a"),
        ("http://example.org/prior/1/a.txt", "1-a"),
        ("http://example.org/more/prior/1/a.txt", "1-a"),
        ("http://example.org/1/a.txt?args=some", "1-a"),
        ("http://example.org/1/a.txt?args=some#frgmnt", "1-a"),
    ),
)
def test_name_parts_extraction(url, id):
    res_id, res_suffix = extract_name_parts(url, "text/turtle")
    assert res_id == id, f"for {url=} got {res_id=} expected {id=}"
    assert res_suffix == ".ttl", f"expected .ttl got {res_suffix=}"
