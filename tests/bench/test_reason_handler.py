from pathlib import Path
from unittest import TestCase

from rdflib import Graph, Literal, Namespace

from sema.bench.dispatcher import TaskDispatcher
from sema.bench.handler import (
    ReasonHandler,
    _resolve_bench_path,
    _resolve_bench_paths,
)
from sema.bench.task import Task


class TestReasonHandler(TestCase):
    def test_dispatcher(self):
        task = Task(".", ".", ".", "test_reason_task", "reason", {})
        self.assertEqual(TaskDispatcher().dispatch(task), ReasonHandler)

    def test_handle(self, tmp_path=None):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            base_dir = Path(td)
            input_dir = base_dir / "input"
            input_dir.mkdir()
            output_dir = base_dir / "output"
            output_dir.mkdir()

            source_ttl = input_dir / "data.ttl"
            source_ttl.write_text(
                """
                @prefix ex: <http://example.org/> .
                ex:item1 ex:value 100 .
                """,
                encoding="utf-8",
            )

            query_file = base_dir / "construct.sparql"
            query_file.write_text(
                """
                PREFIX ex: <http://example.org/>
                CONSTRUCT {
                    ex:item1 ex:processed true .
                }
                WHERE {
                    ex:item1 ex:value ?v .
                }
                """,
                encoding="utf-8",
            )

            out_file = output_dir / "reasoned.ttl"

            task = Task(
                input_data_location=input_dir,
                output_data_location=output_dir,
                sembench_data_location=base_dir,
                task_id="test_reason_bench",
                func="reason",
                args={
                    "sources": ["data.ttl"],
                    "queries": ["construct.sparql"],
                    "output_path": str(out_file),
                    "input_path": str(input_dir),
                },
            )

            ReasonHandler().handle(task)

            self.assertTrue(out_file.exists())
            g = Graph().parse(out_file)
            ex = Namespace("http://example.org/")
            self.assertIn((ex.item1, ex.processed, Literal(True)), g)

    def test_handle_scalar_args(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            base_dir = Path(td)
            input_dir = base_dir / "input"
            input_dir.mkdir()
            output_dir = base_dir / "output"
            output_dir.mkdir()

            source_ttl = input_dir / "single.ttl"
            source_ttl.write_text(
                "@prefix ex: <http://example.org/> . ex:item2 ex:val 50 .",
                encoding="utf-8",
            )

            query_file = base_dir / "single_query.sparql"
            query_file.write_text(
                "PREFIX ex: <http://example.org/> "
                "CONSTRUCT { ex:item2 ex:done true } "
                "WHERE { ex:item2 ex:val ?v }",
                encoding="utf-8",
            )

            out_file = output_dir / "scalar_out.ttl"

            # Pass scalar strings instead of lists
            task = Task(
                input_data_location=input_dir,
                output_data_location=output_dir,
                sembench_data_location=base_dir,
                task_id="test_scalar_reason_bench",
                func="reason",
                args={
                    "sources": "single.ttl",
                    "queries": "single_query.sparql",
                    "output_path": str(out_file),
                },
            )

            ReasonHandler().handle(task)

            self.assertTrue(out_file.exists())
            g = Graph().parse(out_file)
            ex = Namespace("http://example.org/")
            self.assertIn((ex.item2, ex.done, Literal(True)), g)

    def test_resolve_bench_path(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            base_dir = Path(td)
            existing_file = base_dir / "existing.ttl"
            existing_file.write_text(
                "@prefix ex: <http://example.org/> .", encoding="utf-8"
            )

            # 1. Concrete relative path that exists -> resolved
            resolved = _resolve_bench_path("existing.ttl", base_dir)
            self.assertEqual(resolved, str(existing_file))

            # 2. Concrete relative path that does not exist -> unchanged
            resolved_missing = _resolve_bench_path("missing.ttl", base_dir)
            self.assertEqual(resolved_missing, "missing.ttl")

            # 3. Relative glob pattern -> rooted at base_dir
            resolved_glob = _resolve_bench_path("*.ttl", base_dir)
            self.assertEqual(resolved_glob, str(base_dir / "*.ttl"))

            resolved_nested = _resolve_bench_path("nested/*.ttl", base_dir)
            expected_nested = str(base_dir / "nested" / "*.ttl")
            self.assertEqual(resolved_nested, expected_nested)

            # Glob pattern with '?' and whitespace
            resolved_ws_q = _resolve_bench_path(
                "data sample ?.ttl", base_dir
            )
            self.assertEqual(
                resolved_ws_q, str(base_dir / "data sample ?.ttl")
            )

            # 4. Absolute glob pattern -> preserved as-is
            abs_glob = str(base_dir / "*.ttl")
            self.assertEqual(_resolve_bench_path(abs_glob, base_dir), abs_glob)

            # 5. Inline SPARQL query -> preserved as-is
            sparql = "CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }"
            self.assertEqual(_resolve_bench_path(sparql, base_dir), sparql)

            # 6. Non-string / non-Path -> unchanged
            self.assertIsNone(_resolve_bench_path(None, base_dir))
            g = Graph()
            self.assertIs(_resolve_bench_path(g, base_dir), g)

            # 7. Test _resolve_bench_paths on list
            resolved_list = _resolve_bench_paths(
                ["existing.ttl", "*.ttl", "data sample ?.ttl"], base_dir
            )
            self.assertEqual(
                resolved_list,
                [
                    str(existing_file),
                    str(base_dir / "*.ttl"),
                    str(base_dir / "data sample ?.ttl"),
                ],
            )

    def test_handle_source_glob(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            base_dir = Path(td)
            input_dir = base_dir / "input"
            input_dir.mkdir()
            output_dir = base_dir / "output"
            output_dir.mkdir()

            (input_dir / "data1.ttl").write_text(
                "@prefix ex: <http://example.org/> . ex:itemA ex:val 10 .",
                encoding="utf-8",
            )
            (input_dir / "data2.ttl").write_text(
                "@prefix ex: <http://example.org/> . ex:itemB ex:val 20 .",
                encoding="utf-8",
            )

            query_file = base_dir / "construct.sparql"
            query_file.write_text(
                "PREFIX ex: <http://example.org/> "
                "CONSTRUCT { ?s ex:processed true } "
                "WHERE { ?s ex:val ?v }",
                encoding="utf-8",
            )

            out_file = output_dir / "glob_out.ttl"

            # Pass relative glob pattern as sources
            task = Task(
                input_data_location=input_dir,
                output_data_location=output_dir,
                sembench_data_location=base_dir,
                task_id="test_glob_reason_bench",
                func="reason",
                args={
                    "sources": "*.ttl",
                    "queries": ["construct.sparql"],
                    "output_path": str(out_file),
                },
            )

            ReasonHandler().handle(task)

            self.assertTrue(out_file.exists())
            g = Graph().parse(out_file)
            ex = Namespace("http://example.org/")
            self.assertIn((ex.itemA, ex.processed, Literal(True)), g)
            self.assertIn((ex.itemB, ex.processed, Literal(True)), g)

    def test_handle_source_glob_whitespace_question_mark(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            base_dir = Path(td)
            input_dir = base_dir / "input"
            input_dir.mkdir()
            output_dir = base_dir / "output"
            output_dir.mkdir()

            (input_dir / "sample 1.ttl").write_text(
                "@prefix ex: <http://example.org/> . ex:item1 ex:val 10 .",
                encoding="utf-8",
            )
            (input_dir / "sample 2.ttl").write_text(
                "@prefix ex: <http://example.org/> . ex:item2 ex:val 20 .",
                encoding="utf-8",
            )

            query_file = base_dir / "construct.sparql"
            query_file.write_text(
                "PREFIX ex: <http://example.org/> "
                "CONSTRUCT { ?s ex:processed true } "
                "WHERE { ?s ex:val ?v }",
                encoding="utf-8",
            )

            out_file = output_dir / "ws_glob_out.ttl"

            # Pass relative ? glob pattern containing whitespace
            task = Task(
                input_data_location=input_dir,
                output_data_location=output_dir,
                sembench_data_location=base_dir,
                task_id="test_ws_glob_reason_bench",
                func="reason",
                args={
                    "sources": "sample ?.ttl",
                    "queries": "construct.sparql",
                    "output_path": str(out_file),
                },
            )

            ReasonHandler().handle(task)

            self.assertTrue(out_file.exists())
            g = Graph().parse(out_file)
            ex = Namespace("http://example.org/")
            self.assertIn((ex.item1, ex.processed, Literal(True)), g)
            self.assertIn((ex.item2, ex.processed, Literal(True)), g)

    def test_handle_source_glob_absolute(self):
        import tempfile

        with tempfile.TemporaryDirectory() as td:
            base_dir = Path(td)
            input_dir = base_dir / "input"
            input_dir.mkdir()
            output_dir = base_dir / "output"
            output_dir.mkdir()

            (input_dir / "data1.ttl").write_text(
                "@prefix ex: <http://example.org/> . ex:itemX ex:val 100 .",
                encoding="utf-8",
            )

            query_file = base_dir / "construct.sparql"
            query_file.write_text(
                "PREFIX ex: <http://example.org/> "
                "CONSTRUCT { ?s ex:active true } "
                "WHERE { ?s ex:val ?v }",
                encoding="utf-8",
            )

            out_file = output_dir / "abs_glob_out.ttl"

            # Pass absolute glob pattern as sources
            abs_glob = str(input_dir / "*.ttl")
            task = Task(
                input_data_location=input_dir,
                output_data_location=output_dir,
                sembench_data_location=base_dir,
                task_id="test_abs_glob_reason_bench",
                func="reason",
                args={
                    "sources": [abs_glob],
                    "queries": "construct.sparql",
                    "output_path": str(out_file),
                },
            )

            ReasonHandler().handle(task)

            self.assertTrue(out_file.exists())
            g = Graph().parse(out_file)
            ex = Namespace("http://example.org/")
            self.assertIn((ex.itemX, ex.active, Literal(True)), g)
