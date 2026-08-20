from pathlib import Path

from rdflib import Graph, Literal, Namespace

from sema.commons.reason.__main__ import _main


def test_reason_cli(tmp_path: Path):
    source_ttl = tmp_path / "source.ttl"
    source_ttl.write_text(
        """
        @prefix ex: <http://example.org/> .
        ex:sample1 ex:measured 42 .
        """,
        encoding="utf-8",
    )

    query_file = tmp_path / "query.sparql"
    query_file.write_text(
        """
        PREFIX ex: <http://example.org/>
        CONSTRUCT {
            ex:sample1 ex:status "valid" .
        }
        WHERE {
            ex:sample1 ex:measured ?m .
        }
        """,
        encoding="utf-8",
    )

    out_file = tmp_path / "output.ttl"

    success = _main(
        "-i",
        str(tmp_path),
        "-s",
        "source.ttl",
        "-q",
        "query.sparql",
        "-o",
        str(out_file),
    )

    assert success is True
    assert out_file.exists()

    g = Graph().parse(out_file)
    ex = Namespace("http://example.org/")
    assert (ex.sample1, ex.status, Literal("valid")) in g
