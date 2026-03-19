import os
from pathlib import Path
from typing import Callable, Optional

import pytest
from rdflib import Graph

from sema.commons.store import RDFStore
from sema.shacl.shaclery import GraphDBValidator

DATA_FOLDER: Path = Path(__file__).parent.absolute() / "data"
URN_TEST_GRAPH = "urn:shacl:gdb:test"


@pytest.mark.usefixtures("quicktest", "_uri_store_build")
@pytest.mark.parametrize(
    ["filename", "expected_result"],
    (
        ("graph-ok.ttl", True),
        ("graph-nok.ttl", False),
    ),
)
def test_gdb_shacl(
    quicktest: bool,
    _uri_store_build: Optional[Callable[[], RDFStore]],
    filename: str,
    expected_result: bool,
):
    if quicktest:
        pytest.skip("gdb shacl test skipped in quicktest mode")
    if _uri_store_build is None:
        pytest.skip("gdb shacl test skipped: gdb store config missing")
    assert GraphDBValidator is not None
    validator = GraphDBValidator()
    assert validator is not None

    graph_path: Path = DATA_FOLDER / filename
    shacl_path: Path = DATA_FOLDER / "shacl.ttl"

    # create uri store for testing
    store: RDFStore = _uri_store_build()
    store.drop_graph(URN_TEST_GRAPH)  # ensure store is empty before testing
    # upload data into the store
    g = Graph().parse(graph_path, format="turtle")
    store.insert(g, URN_TEST_GRAPH)
    # call the shacl validator on the store

    store_uri = os.getenv("TEST_SPARQL_READ_URI")
    succes, res_graph = validator.validate(
        graph=store_uri,
        shacl=shacl_path,
    )

    # cleanup the store after testing
    store.drop_graph(URN_TEST_GRAPH)

    assert succes is expected_result
    assert res_graph is not None
    assert len(res_graph) > 0  # the report has at least one triple
