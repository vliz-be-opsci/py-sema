from pathlib import Path
from typing import Any, Dict

import pytest
from rdflib import Graph

from sema.commons.log import logconf_path
from sema.subyt.__main__ import main

MY_FOLDER = Path(__file__).parent
TEMPLATES_FOLDER = MY_FOLDER / "templates"
DATA_FOLDER = MY_FOLDER / "in"


def test_help(capfd):
    help_line: str = "--help"
    with pytest.raises(SystemExit) as caught:
        success: bool = main(*help_line.split())
        assert not success
        assert caught.value.code == 0
        assert caught.type == SystemExit
    out, err = capfd.readouterr()
    assert len(out) > 0
    assert out.startswith("usage: ")


def test_cli(capfd):
    name: str = "01-basic.ttl"
    assert (TEMPLATES_FOLDER / name).exists(), (
        f"template {name=} does not exist in {TEMPLATES_FOLDER=}" ""
    )

    def make_multipart(argname: str, valdict: Dict[str, Any]):
        return " ".join(f"--{argname} {k} {v}" for k, v in valdict.items())

    setnames: Dict[str, str] = dict(
        _="data.csv", cities="data_cities/", movies="data_movies.xml"
    )
    setpaths: Dict[str, Path] = {
        k: (DATA_FOLDER / v) for k, v in setnames.items()
    }
    for n, p in setpaths.items():
        assert p.exists(), f"path {p} for set {n} does not exist"
    setpart = make_multipart("set", setpaths)
    varpart = make_multipart("var", dict(ME="notyou", one=1, two=2))

    cli_line = (
        f" --logconf {logconf_path}"
        f" --templates {TEMPLATES_FOLDER}"
        f" --name {name}"
        f" {setpart} {varpart}"
        f" --output -"
    )
    success: bool = main(*cli_line.split())
    assert success
    out, err = capfd.readouterr()
    assert len(out) > 0
    g = Graph().parse(data=out, format="turtle")
    assert len(g) > 0
