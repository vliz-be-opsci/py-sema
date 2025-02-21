import tempfile
from pathlib import Path

import pytest
from rdflib import Graph, URIRef

from sema.commons.glob import getMatchingGlobPaths
from sema.subyt.__main__ import _main
from sema.subyt.api import Source
from sema.subyt.sources import CSVFileSource, FilteringSource, SourceFactory
from tests.conftest import log

MY_FOLDER = Path(__file__).parent
TEMPLATES_FOLDER = MY_FOLDER / "templates"
DATA_FOLDER = MY_FOLDER / "in"


class FixedDataListSource(Source):
    def __init__(self) -> None:
        self._data: list[dict[str, any]] = [
            {"name": "theo", "parent": "stef"},
            {"name": "fien", "parent": "marc"},
            {"name": "tuur", "parent": "marc"},
            {"name": "jef", "parent": "stef"},
        ]

    def __enter__(self) -> object:
        return iter(self._data)

    def __exit__(self, *exc) -> None:
        pass


def test_verify_base_source():
    fdls = FixedDataListSource()
    with fdls as items:
        data = list(items)
        assert len(data) == 4
        assert data[0]["name"] == "theo"
        assert data[2]["parent"] == "marc"


def test_filtered_source() -> None:
    fdls = FixedDataListSource()
    upfs = FilteringSource(fdls, "the unique parent = {parent}")
    with upfs as items:
        data = list(items)
        assert len(data) == 2
        assert data[0]["parent"] == "stef"
        assert data[1]["parent"] == "marc"
        assert data[0]["name"] == "theo"
        assert data[1]["name"] == "fien"


def test_filtered_csv_source() -> None:
    csv_source_path = str(DATA_FOLDER / "data_countries.csv")
    csv_source = SourceFactory.make_source(csv_source_path)
    assert csv_source is not None
    assert isinstance(csv_source, CSVFileSource)
    with csv_source as items:
        assert len([item for item in items]) == 246

    upfs = SourceFactory.make_source(
        csv_source_path,
        unique_pattern="{English short name lower case:1}",
    )
    assert upfs is not None
    assert isinstance(upfs, FilteringSource)
    with upfs as items:
        uniq_leadchar_countries = list(items)

        expected_leadchars = "AÅBCDEFGHIJKLMNOPQRSTUVWYZ"
        assert len(uniq_leadchar_countries) == len(expected_leadchars)

        for i, elc in enumerate(expected_leadchars):
            assert uniq_leadchar_countries[i][
                "English short name lower case"
            ].startswith(elc)


expected_names: list = [
    "Cedric Decruw",
    "Katrina Exter",
    "Laurian Van Maldeghem",
]


def test_filtered_json_source() -> None:
    json_source_path = str(DATA_FOLDER / "data_team.json")
    json_source = SourceFactory.make_source(json_source_path)
    assert json_source is not None
    with json_source as items:
        assert len([item for item in items]) == 5

    upfs = SourceFactory.make_source(
        json_source_path,
        unique_pattern="{orcid:9}",
    )
    assert upfs is not None
    with upfs as items:
        uniq_lead9_orcids = list(items)
        assert len(uniq_lead9_orcids) == 3
        print(f"{uniq_lead9_orcids=}")
        for i in range(0, 3):
            assert uniq_lead9_orcids[i]["orcid"].startswith(f"0000-000{i + 1}")
            assert uniq_lead9_orcids[i]["name"] == expected_names[i]


def test_valid_unique_pattern() -> None:
    fdls = FixedDataListSource()
    with pytest.raises(ValueError):
        # this fails when the unique_pattern has no {variable} magic in it?
        FilteringSource(fdls, "no magic here")


def test_unique_processing() -> None:
    json_source_path = str(DATA_FOLDER / "data_team.json").strip()
    name = "filter/unique-team-orcid.ttl"
    with tempfile.TemporaryDirectory() as tmpdirname:
        out_pattern = tmpdirname + "/orcid-{orcid:9}.ttl"
        # use the cli with the -u # option
        cli_line = (
            f" --templates {TEMPLATES_FOLDER}"
            f" --input {json_source_path}"
            f" --name {name}"
            f" --output {out_pattern}"
            " --unique #"  # reuses out_pattern as the pattern for uniqueness
        )
        log.debug(f"{cli_line.split()=}")
        success: bool = _main(*cli_line.split())
        assert success
        # check the output files
        outfiles = getMatchingGlobPaths(Path(tmpdirname), ["**/*"])
        assert len(outfiles) == 3

        for i in range(0, 3):
            tmpfile = Path(tmpdirname) / f"orcid-0000-000{i + 1}.ttl"
            with open(tmpfile, "r") as f:
                content = f.read()
                assert len(content) > 0
                g = Graph().parse(data=content, format="turtle")
                found_names = list(
                    g.objects(
                        predicate=URIRef("http://xmlns.com/foaf/0.1/name")
                    )
                )
                assert len(found_names) == 1
                assert found_names[0].value == expected_names[i]
