from sema.commons.ogm import ObjectGraphMapper, GraphBuilder

def test_object_graph_mapper():
    class OGMLike(ObjectGraphMapper):
        def _map(self):
            return GraphBuilder().build()

    OGMLike().serialize()
