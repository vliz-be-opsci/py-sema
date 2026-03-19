import tempfile
from pathlib import Path

import pytest
from rdflib import Graph
from rdflib.compare import isomorphic as graph_compare

from sema.shacl import Shacl
from sema.shacl.shaclery import Validator

DATA_FOLDER: Path = Path(__file__).parent.absolute() / "data"


@pytest.mark.parametrize(
    ["filename", "expected_result"],
    (
        ("graph-ok.ttl", True),
        ("graph-nok.ttl", False),
    ),
)
def test_shacl_service_no_rpt(filename: str, expected_result: bool):
    service = Shacl(
        graph=str(DATA_FOLDER / filename),
        shacl=str(DATA_FOLDER / "shacl.ttl"),
        output="-",
    )
    assert service is not None

    result = service.process()
    assert result is not None
    assert result.success is expected_result


@pytest.mark.parametrize(
    ["filename", "expected_result"],
    (
        ("graph-ok.ttl", True),
        ("graph-nok.ttl", False),
    ),
)
def test_shacl_service_capturerpt(filename: str, expected_result: bool):
    # make temp file for report_graph
    report_graph = Graph()

    with tempfile.NamedTemporaryFile(suffix=".ttl") as tmp:
        service = Shacl(
            graph=str(DATA_FOLDER / filename),
            shacl=str(DATA_FOLDER / "shacl.ttl"),
            output=tmp.name,
        )
        result = service.process()

        assert result is not None
        assert result.success is expected_result

        # check that report file is created and has content
        with open(tmp.name, "r") as f:
            content = f.read()
            assert len(content) > 0  # report file should not be empty

        report_graph.parse(tmp.name, format="turtle")
        assert len(report_graph) > 1  # report has at least 2 triples
        conf_result: bool = Validator.conf_result_from_report(report_graph)
        assert conf_result is expected_result

        if expected_result is True:
            assert len(report_graph) == 2  # report has exactly least 2 triples
            success_graph = Graph()
            success_graph.parse(
                format="turtle",
                data="""
                    @prefix sh: <http://www.w3.org/ns/shacl#> .
                    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

                [] a sh:ValidationReport ;
                    sh:conforms true .
            """,
            )
            assert graph_compare(report_graph, success_graph) is True
