from sema.commons.ogm import ObjectGraphMapper

def test_object_graph_mapper():
    ogm = ObjectGraphMapper(
        blueprint_path="./tests/commons/ogm/data/blueprint.yml"
    )
    ogm.serialize("./tests/commons/ogm/data/graph.ttl")
