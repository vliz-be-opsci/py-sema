from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from rdflib import Graph

from sema.shacl.__main__ import _main
from sema.shacl.shaclery import Validator

DATA_FOLDER: Path = Path(__file__).parent.absolute() / "data"


@pytest.mark.parametrize(
    ["filename", "expected_result"],
    (
        ("graph-ok.ttl", True),
        ("graph-nok.ttl", False),
    ),
)
def test_main(filename: str, expected_result: bool):
    graph_path = (DATA_FOLDER / filename).absolute()
    shacl_path = (DATA_FOLDER / "shacl.ttl").absolute()
    with NamedTemporaryFile(suffix=".ttl") as tmp:
        out_path = Path(tmp.name).absolute()
        argsline: str = (
            f"--graph {graph_path} --shacl {shacl_path} --output {out_path}"
        )
        _main(*argsline.split(" "))  # pass as individual arguments
        assert out_path.exists(), "run did not create expected output"
        conf_rpt = Graph().parse(out_path, format="turtle")
        conf_result = Validator.conf_result_from_report(conf_rpt)
        assert conf_result is expected_result
