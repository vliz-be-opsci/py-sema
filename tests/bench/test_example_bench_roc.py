from pathlib import Path
from unittest import TestCase

from rdflib import Graph, Namespace

from sema.bench.core import Sembench
from sema.ro.creator import ROCreator


class TestExampleBenchRocReason(TestCase):
    def test_example_sembench_and_rocreator(self):
        bench_dir = Path("examples/temp_bench_roc_reason")
        self.assertTrue(bench_dir.exists())

        # 1. Run Sembench
        sb = Sembench(locations={"home": str(bench_dir)}, fail_fast=True)
        sb.process()

        out_file = bench_dir / "output/reasoned_triples.ttl"
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
        roc = ROCreator(
            blueprint_path=bench_dir / "roc-me.yml",
            rocrate_path=bench_dir,
            force=True,
        )
        roc.process()

        metadata_file = bench_dir / "ro-crate-metadata.json"
        self.assertTrue(metadata_file.exists())
        g_roc = Graph().parse(metadata_file, format="json-ld")

        # Verify reasoned spatialCoverage triple on the root dataset
        self.assertIn((None, schema.spatialCoverage, ex.station_alpha), g_roc)
