from pathlib import Path
from rdflib import Graph
from rdflib.compare import to_isomorphic
from sema.commons.ogm import ObjectGraphMapper, GraphBuilder

def test_object_graph_mapper():
    class OGMLike(ObjectGraphMapper):
        def __init__(self, blueprint):
            super().__init__()
            self.blueprint = Path(blueprint)

        def _map(self):
            return GraphBuilder(
                namespaces={"@base": "http://example.org/"}, # overriding default value to circumvent rdflib bug (https://github.com/RDFLib/rdflib/issues/1216)
                blueprint=self.blueprint
            ).build()

    ogml = OGMLike("./tests/commons/ogm/data/object_graph_mapping.yml")
    ogml.serialize("./tests/commons/ogm/data/object_graph_mapping.ttl")

    g0 = Graph().parse("./tests/commons/ogm/data/object_graph_mapping_expected.ttl")
    g1 = Graph().parse("./tests/commons/ogm/data/object_graph_mapping.ttl")

    assert to_isomorphic(g0) == to_isomorphic(g1)
