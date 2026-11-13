import tempfile
from pathlib import Path
from unittest import TestCase

from rdflib import Graph, Namespace, URIRef

from sema.bench.core import Sembench
from sema.ro.creator import ROCreator


class TestExampleBenchRocReason(TestCase):
    def test_example_sembench_and_rocreator(self):
        with tempfile.TemporaryDirectory() as td:
            bench_dir = Path(td)
            input_dir = bench_dir / "input"
            input_dir.mkdir()
            output_dir = bench_dir / "output"
            output_dir.mkdir()
            queries_dir = bench_dir / "queries"
            queries_dir.mkdir()

            # Input RDF data with an observation that lacks a location
            source_ttl = input_dir / "data.ttl"
            source_ttl.write_text(
                """
                @prefix ex: <http://example.org/> .
                @prefix schema: <http://schema.org/> .

                ex:obs_20260821_01 a schema:Observation ;
                    schema:result 21.5 .

                ex:station_alpha a schema:Place ;
                    schema:name "Station Alpha" .
                """,
                encoding="utf-8",
            )

            # CONSTRUCT query that reasons the missing location triple
            query_file = queries_dir / "add_location.sparql"
            query_file.write_text(
                """
                PREFIX ex: <http://example.org/>
                PREFIX schema: <http://schema.org/>

                CONSTRUCT {
                    ex:obs_20260821_01 schema:location ex:station_alpha .
                }
                WHERE {
                    ex:obs_20260821_01 a schema:Observation .
                }
                """,
                encoding="utf-8",
            )

            out_file = output_dir / "reasoned_triples.ttl"

            # Sembench config: a single "reason" task
            sembench_yaml = bench_dir / "sembench.yaml"
            sembench_yaml.write_text(
                f"""
reason_task:
  func: reason
  args:
    sources:
      - "{source_ttl}"
    queries:
      - "{query_file}"
    output_path: "{out_file}"
    input_path: "{input_dir}"
""",
                encoding="utf-8",
            )

            # 1. Run Sembench
            sb = Sembench(locations={"home": str(bench_dir)}, fail_fast=True)
            sb.process()

            self.assertTrue(out_file.exists())
            g_bench = Graph().parse(out_file, format="turtle")
            self.assertGreater(len(g_bench), 0)

            schema = Namespace("http://schema.org/")
            ex = Namespace("http://example.org/")

            self.assertIn(
                (ex.obs_20260821_01, schema.location, ex.station_alpha),
                g_bench,
            )

            # 2. Run ROCreator with reasoning
            # Create a data file so the crate has content
            (bench_dir / "data.csv").write_text(
                "col1,col2\n1,2\n", encoding="utf-8"
            )

            # Extra external triples for ROCreator reasoning
            extra_ttl = bench_dir / "extra.ttl"
            extra_ttl.write_text(
                """
                @prefix ex: <http://example.org/> .
                @prefix schema: <http://schema.org/> .

                ex:station_alpha a schema:Place ;
                    schema:name "Station Alpha" .
                """,
                encoding="utf-8",
            )

            # CONSTRUCT query for ROCreator to add spatialCoverage
            roc_query_file = queries_dir / "add_spatial.sparql"
            roc_query_file.write_text(
                """
                PREFIX ex: <http://example.org/>
                PREFIX schema: <http://schema.org/>

                CONSTRUCT {
                    <./> schema:spatialCoverage ex:station_alpha .
                }
                WHERE {
                    ex:station_alpha a schema:Place .
                }
                """,
                encoding="utf-8",
            )

            roc_yaml = bench_dir / "roc-me.yml"
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
  name: "Test RO-Crate"
  description: "Crate enriched by SPARQL CONSTRUCT"

data.csv:
  $type: File
  name: "data.csv"
""",
                encoding="utf-8",
            )

            roc = ROCreator(
                blueprint_path=roc_yaml,
                rocrate_path=bench_dir,
                force=True,
            )
            roc.process()

            metadata_file = bench_dir / "ro-crate-metadata.json"
            self.assertTrue(metadata_file.exists())
            g_roc = Graph().parse(metadata_file, format="json-ld")

            # Locate the root dataset node
            root = next(
                g_roc.subjects(
                    URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                    schema.Dataset,
                )
            )

            # Verify reasoned spatialCoverage triple on the root dataset
            self.assertIn(
                (root, schema.spatialCoverage, ex.station_alpha), g_roc
            )
