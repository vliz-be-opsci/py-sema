from rdflib import Graph
from rdflib.compare import to_isomorphic
from sema.ro.creator import ROCreator

def test_ro_creator():
    roc = ROCreator(
        blueprint_path="./tests/ro/creator/data/sema_roc.yml",
        blueprint_env={"DOI": "https://doi.org/10.3233/DS-210053"},
        rocrate_path="./tests/ro/creator/data/katoomba-rainfall",
    )
    roc.process()

    g0 = Graph().parse(
        "./tests/ro/creator/data/ro-crate-metadata-expected.json",
        format="json-ld",
        base="urn:nil:"
    )

    g1 = Graph().parse(
        "./tests/ro/creator/data/katoomba-rainfall/ro-crate-metadata.json",
        format="json-ld",
        base="urn:nil:"
    )

    assert to_isomorphic(g0) == to_isomorphic(g1)
