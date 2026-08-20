from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef

from sema.commons.reason import Reasoner, ReasonResult


def test_reason_single_construct_query(tmp_path: Path):
    source_ttl = tmp_path / "source.ttl"
    source_ttl.write_text(
        """
        @prefix ex: <http://example.org/> .
        @prefix foaf: <http://xmlns.com/foaf/0.1/> .

        ex:alice a foaf:Person ;
                 foaf:name "Alice" .
        """,
        encoding="utf-8",
    )

    query_sparql = tmp_path / "query.sparql"
    query_sparql.write_text(
        """
        PREFIX ex: <http://example.org/>
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX schema: <http://schema.org/>

        CONSTRUCT {
            ?person schema:name ?name ;
                    schema:jobTitle "Scientist" .
        }
        WHERE {
            ?person a foaf:Person ;
                    foaf:name ?name .
        }
        """,
        encoding="utf-8",
    )

    out_file = tmp_path / "reasoned.ttl"
    reasoner = Reasoner(
        sources=source_ttl,
        queries=query_sparql,
        output_path=out_file,
    )
    result = reasoner.process()

    assert isinstance(result, ReasonResult)
    assert result.success is True
    assert out_file.exists()

    res_graph = Graph().parse(out_file)
    schema = Namespace("http://schema.org/")
    alice = URIRef("http://example.org/alice")
    assert (alice, schema.name, Literal("Alice")) in res_graph
    assert (alice, schema.jobTitle, Literal("Scientist")) in res_graph


def test_reason_in_memory_graph():
    g = Graph()
    ex = Namespace("http://example.org/")
    g.add((ex.station1, ex.temperature, Literal(23.5)))

    query = """
    PREFIX ex: <http://example.org/>
    PREFIX sosa: <http://www.w3.org/ns/sosa/>
    CONSTRUCT {
        ?station a sosa:Platform .
    }
    WHERE {
        ?station ex:temperature ?temp .
    }
    """
    reasoner = Reasoner(sources=g, queries=query)
    res_g = reasoner.reason()
    sosa = Namespace("http://www.w3.org/ns/sosa/")
    rdf_type = URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
    assert (ex.station1, rdf_type, sosa.Platform) in res_g


def test_reason_prefix_and_base_injection(tmp_path: Path):
    source_ttl = tmp_path / "data.ttl"
    source_ttl.write_text(
        """
        @base <http://example.org/base/> .
        <item> <http://schema.org/name> "Test Dataset" .
        """,
        encoding="utf-8",
    )

    # Query without explicit PREFIX or BASE
    query = """
    CONSTRUCT {
        <item> schema:description "Auto-injected description" .
    }
    WHERE {
        <item> schema:name ?name .
    }
    """
    reasoner = Reasoner(
        sources=source_ttl,
        queries=query,
        prefixes={"schema": "http://schema.org/"},
        base="http://example.org/base/",
    )
    res_g = reasoner.reason()
    schema = Namespace("http://schema.org/")
    assert (
        URIRef("http://example.org/base/item"),
        schema.description,
        Literal("Auto-injected description"),
    ) in res_g


def test_reason_glob_queries(tmp_path: Path):
    source = tmp_path / "obs.ttl"
    source.write_text(
        """
        @prefix ex: <http://example.org/> .
        ex:obs1 ex:val 10 .
        ex:obs2 ex:val 20 .
        """,
        encoding="utf-8",
    )

    qdir = tmp_path / "queries"
    qdir.mkdir()
    (qdir / "q1.sparql").write_text(
        "PREFIX ex: <http://example.org/> "
        "CONSTRUCT { ?s ex:hasVal true } "
        "WHERE { ?s ex:val ?v }",
        encoding="utf-8",
    )
    (qdir / "q2.sparql").write_text(
        "PREFIX ex: <http://example.org/> "
        "CONSTRUCT { ?s ex:isObs true } "
        "WHERE { ?s ex:val ?v }",
        encoding="utf-8",
    )

    reasoner = Reasoner(
        input_path=tmp_path,
        sources="obs.ttl",
        queries="queries/*.sparql",
    )
    res_g = reasoner.reason()
    ex = Namespace("http://example.org/")
    assert (ex.obs1, ex.hasVal, Literal(True)) in res_g
    assert (ex.obs1, ex.isObs, Literal(True)) in res_g
    assert (ex.obs2, ex.hasVal, Literal(True)) in res_g
