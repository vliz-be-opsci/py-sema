from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef

from sema.ro.creator import ROCreator


def test_rocreator_with_reasoning(tmp_path: Path):
    crate_dir = tmp_path / "test_crate"
    crate_dir.mkdir()
    (crate_dir / "data.csv").write_text("col1,col2\n1,2\n", encoding="utf-8")

    # Extra external triples
    extra_ttl = crate_dir / "extra.ttl"
    extra_ttl.write_text(
        """
        @prefix schema: <http://schema.org/> .
        @prefix ex: <http://example.org/> .

        ex:observatory_station a schema:Place ;
            schema:name "Station Alpha" ;
            schema:latitude 51.2 ;
            schema:longitude 2.9 .
        """,
        encoding="utf-8",
    )

    # CONSTRUCT query to enrich root dataset ./ with spatial coverage
    queries_dir = crate_dir / "queries"
    queries_dir.mkdir()
    (queries_dir / "add_spatial.sparql").write_text(
        """
        PREFIX schema: <http://schema.org/>
        PREFIX ex: <http://example.org/>

        CONSTRUCT {
            <./> schema:spatialCoverage ex:observatory_station ;
                 schema:keywords "Biota" .
        }
        WHERE {
            ex:observatory_station a schema:Place .
        }
        """,
        encoding="utf-8",
    )

    roc_yaml = crate_dir / "roc-me.yml"
    roc_yaml.write_text(
        """
$:
  prefix:
    schema: "http://schema.org/"
    ex: "http://example.org/"
  reason:
    sources:
      - "extra.ttl"
    queries:
      - "queries/add_spatial.sparql"

ro-crate-metadata.json:
  $type: CreativeWork
  conformsTo: https://w3id.org/ro/crate/1.2
  about: ./

./:
  $type: Dataset
  name: "My Reasoned RO-Crate"
  description: "Crate enriched by SPARQL CONSTRUCT"

data.csv:
  $type: File
  name: "data.csv"
        """,
        encoding="utf-8",
    )

    roc = ROCreator(
        blueprint_path=roc_yaml,
        rocrate_path=crate_dir,
    )
    roc.process()

    metadata_file = crate_dir / "ro-crate-metadata.json"
    assert metadata_file.exists()

    g = Graph().parse(metadata_file, format="json-ld")
    schema = Namespace("http://schema.org/")
    ex = Namespace("http://example.org/")

    # Locate the root dataset node
    root = next(
        g.subjects(
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
            schema.Dataset,
        )
    )

    # Verify reasoned triples exist on the root dataset
    assert (root, schema.spatialCoverage, ex.observatory_station) in g
    assert (root, schema.keywords, Literal("Biota")) in g
    assert (root, schema.name, Literal("My Reasoned RO-Crate")) in g
