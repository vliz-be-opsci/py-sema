from pathlib import Path

from rdflib import Graph
from rdflib.namespace import RDF, Namespace

from sema.shacl.shaclery import _load_graph

SCHEMA = Namespace("https://schema.org/")
SHACL = Namespace("http://www.w3.org/ns/shacl#")

DATA_FOLDER = Path(__file__).parent.absolute() / "data"


def test_load_graph_file():
    g: Graph = _load_graph(DATA_FOLDER / "graph-ok.ttl")
    assert len(g) >= 3  # at least 3 triples in the graph

    persons = list(g.subjects(predicate=RDF.type, object=SCHEMA.Person))
    assert len(persons) == 1  # exact one person in the graph


def test_load_graph_glob():
    g = _load_graph(DATA_FOLDER / "*.*")
    assert len(g) > 30  # more then 30 triples in the graph

    persons = list(g.subjects(predicate=RDF.type, object=SCHEMA.Person))
    assert len(persons) == 3  # exact 3 person in the graph

    shapes = list(g.subjects(predicate=RDF.type, object=SHACL.NodeShape))
    assert len(shapes) > 10


def test_load_graph_url():
    g = _load_graph("https://marineinfo.org/id/person/38476")
    assert len(g) > 30  # more then 30 triples in the graph

    persons = list(g.subjects(predicate=RDF.type, object=SCHEMA.Person))
    assert len(persons) == 1  # exact 1 person in the graph

    this_person = persons[0]
    assert str(this_person) == "https://marineinfo.org/id/person/38476"
    assert (
        str(g.value(subject=this_person, predicate=SCHEMA.name))
        == "Mr Marc Portier"
    )
    assert (
        str(g.value(subject=this_person, predicate=SCHEMA.identifier))
        == "https://orcid.org/0000-0002-9648-6484"
    )
