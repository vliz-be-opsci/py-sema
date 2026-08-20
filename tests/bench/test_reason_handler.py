from pathlib import Path
from unittest import TestCase
from rdflib import Graph, Literal, Namespace

from sema.bench.dispatcher import TaskDispatcher
from sema.bench.handler import ReasonHandler
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
