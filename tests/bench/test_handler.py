#! /usr/bin/env python
from pathlib import Path
from unittest import TestCase

from sema.bench.handler import ShaclHandler
from sema.bench.task import Task


class TestPyshaclHandler(TestCase):
    def test_handle(self):
        task = Task(
            Path("./tests/bench/resources/input_data"),
            Path("."),
            Path("./tests/bench/resources/sembench_data"),
            "my_pyshacl_task1",
            "shacl",
            {
                "data_graph": "example_data_conform.ttl",
                "shacl_graph": "example_shape.ttl",
            },
        )
        self.assertTrue(ShaclHandler().handle(task))

        task = Task(
            Path("./tests/bench/resources/input_data"),
            Path("."),
            Path("./tests/bench/resources/sembench_data"),
            "my_pyshacl_task2",
            "shacl",
            {
                "data_graph": "example_data_nonconform.ttl",
                "shacl_graph": "example_shape.ttl",
            },
        )
        with self.assertRaises(AssertionError):
            ShaclHandler().handle(task)
