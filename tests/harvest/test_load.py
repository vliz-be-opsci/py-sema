#!/usr/bin/env python
import logging
from pathlib import Path

import pytest
from conftest import run_single_test
from rdflib import Graph

from sema.harvest.__main__ import load_resource_into_graph

log = logging.getLogger(__name__)

TEST_INPUT_FOLDER = Path(__file__).parent / "inputs"


def test_insert_resource_into_graph_uri():
    uri = "https://www.w3.org/People/Berners-Lee/card.ttl"
    graph = load_resource_into_graph(Graph(), uri, format="text/turtle")
    assert isinstance(graph, Graph)
    assert len(graph) > 0


def test_insert_resource_into_graph_file_jsonld():
    file_path = str(TEST_INPUT_FOLDER / "3293.jsonld")
    graph = load_resource_into_graph(
        Graph(), file_path, format="application/ld+json"
    )
    assert isinstance(graph, Graph)
    assert len(graph) > 0


def test_insert_resource_into_graph_file_ttl():
    file_path = str(TEST_INPUT_FOLDER / "63523.ttl")
    graph = load_resource_into_graph(Graph(), file_path, format="text/turtle")
    assert isinstance(graph, Graph)
    assert len(graph) > 0


def test_insert_resource_into_graph_invalid_resource():
    resource = "invalid_resource"
    with pytest.raises(ValueError):
        load_resource_into_graph(Graph(), resource, format="text/turtle")


if __name__ == "__main__":
    run_single_test(__file__)
