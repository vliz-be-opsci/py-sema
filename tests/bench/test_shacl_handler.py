#! /usr/bin/env python
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from rdflib import Graph

from sema.bench.handler import ShaclHandler
from sema.bench.task import Task
from sema.shacl.shaclery import Validator

RESOURCES_FOLDER: Path = Path(__file__).parent / "resources"
GRAPH_INPUT_PATH: Path = RESOURCES_FOLDER / "input_data"
SHACL_INPUT_PATH: Path = RESOURCES_FOLDER / "sembench_data"


@pytest.mark.parametrize(
    ["filename", "expected_result"],
    (
        ("example_data_conform.ttl", True),
        ("example_data_nonconform.ttl", False),
    ),
)
def test_shacl_handler(filename: str, expected_result: bool):
    graph_path = str((GRAPH_INPUT_PATH / filename).absolute())
    shacl_path = str((SHACL_INPUT_PATH / "example_shape.ttl").absolute())

    with NamedTemporaryFile() as tmp:
        out_path = str(Path(tmp.name).absolute())

        task = Task(
            None,
            None,
            None,  # No need for Paths ...
            "my_pyshacl_task_conformity",
            "shacl",
            {
                "graph": graph_path,
                "shacl": shacl_path,
                "output": out_path,
            },
        )
        ShaclHandler().handle(task)
        # check that the output file is created and has content
        assert Path(out_path).exists()
        g = Graph().parse(out_path, format="turtle")

        assert len(g) > 0  # the report has at least one triple
        conf_result = Validator.conf_result_from_report(g)
        assert conf_result is expected_result
