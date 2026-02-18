from rdflib import Graph
from rdflib.compare import to_isomorphic

from sema.commons.aggregator import Aggregator


def test_aggregator():
    Aggregator(
        input_path="./tests/commons/aggregator/data",
        globs="**/*.ttl: ttl, **/*.json: json-ld",
    ).process()
    g0 = Graph().parse("./tests/commons/aggregator/data/graph_expected.ttl")
    g1 = Graph().parse("./tests/commons/aggregator/data/graph.ttl")
    assert to_isomorphic(g0) == to_isomorphic(g1)
