from pathlib import Path

import pytest

from sema.shacl.shaclery import PyShaclValidator

DATA_FOLDER = Path(__file__).parent.absolute() / "data"


def test_pyshacl_exists():
    assert PyShaclValidator is not None


@pytest.mark.parametrize(
    ["filename", "expected_result"],
    (
        ("graph-ok.ttl", True),
        ("graph-nok.ttl", False),
    ),
)
def test_pyshacl(filename: str, expected_result: bool):
    validator = PyShaclValidator()
    assert validator is not None

    graph_path = DATA_FOLDER / filename
    shacl_path = DATA_FOLDER / "shacl.ttl"

    succes, res_graph = validator.validate(
        graph=graph_path,
        shacl=shacl_path,
    )

    assert succes is expected_result
    assert res_graph is not None
    assert len(res_graph) > 0  # the report has at least one triple
