import tempfile
from pathlib import Path

import pytest
from rdflib import Graph, URIRef

from sema.subyt.__main__ import _main
from sema.subyt.api import Source
from sema.subyt.sources import CSVFileSource, SourceFactory
from sema.subyt.subyt import Subyt
from tests.conftest import log

MY_FOLDER = Path(__file__).parent
TEMPLATES_FOLDER = MY_FOLDER / "templates"
TEMPLATE_NAME = "extra/peep-ages.ttl"
DATA_FOLDER = MY_FOLDER / "resources"
INPUT_FILE = DATA_FOLDER / "data_ages.psv"
HEADER = "name|age"
DELIMITER = "|"
EXT = "csv"
MIME_TYPE = "text/csv"
CONFIG_DICT = {
    "path": str(INPUT_FILE),
    "header": HEADER,
    "delimiter": DELIMITER,
    # "ext": EXT,
    "mime": MIME_TYPE,
}
CONFIG_STRING = (
    f"{INPUT_FILE !s}+mime={MIME_TYPE}+header={HEADER}+delimiter={DELIMITER}"
)


def test_parsing() -> None:
    expected = CONFIG_DICT.copy()
    path: str = expected.pop("path")

    config = SourceFactory._parse_source_identifier(CONFIG_STRING)
    assert isinstance(config, dict)
    identifier: str = config.pop("identifier")
    assert identifier == path
    assert identifier == str(INPUT_FILE)

    log.debug(f"{config=} <> {expected=}")
    assert config == expected


@pytest.mark.parametrize("source_param", [CONFIG_DICT, CONFIG_STRING])
def test_source_factory_config_handling(source_param: dict) -> None:
    source: Source = SourceFactory.make_source(source_param)
    assert source is not None
    assert isinstance(source, CSVFileSource)
    with source as items:
        data = list(items)
        assert len(data) == 3
        assert data[0] == {"name": "Bram", "age": "40"}
        assert data[1] == {"name": "Steve", "age": "48"}
        assert data[2] == {"name": "Marc", "age": "54"}


def verify_output(outfile: Path) -> None:
    with open(outfile, "r") as f:
        content = f.read()
        assert len(content) > 0
        log.debug(f"{content=}")
        g = Graph().parse(data=content, format="turtle")
        found_names = list(
            g.objects(predicate=URIRef("http://xmlns.com/foaf/0.1/name"))
        )
        assert len(found_names) == 3
        assert found_names[0].value == "Bram"
        assert found_names[1].value == "Steve"
        assert found_names[2].value == "Marc"
        found_ages = list(
            g.objects(predicate=URIRef("https://example.org/peeps/age"))
        )
        assert len(found_ages) == 3
        assert found_ages[0].value == 40
        assert found_ages[1].value == 48
        assert found_ages[2].value == 54


@pytest.mark.parametrize("source_param", [CONFIG_DICT, CONFIG_STRING])
def test_api_with_string(source_param) -> None:
    with tempfile.TemporaryDirectory() as tmpdirname:
        outfile = Path(tmpdirname) / "output.ttl"
        subyt: Subyt = Subyt(
            source=source_param,
            template_folder=TEMPLATES_FOLDER,
            template_name=TEMPLATE_NAME,
            sink=str(outfile),
        )
        subyt.process()
        assert outfile.exists()
        verify_output(outfile)


def test_source_config_cli() -> None:
    with tempfile.TemporaryDirectory() as tmpdirname:
        outfile = Path(tmpdirname) / "output.ttl"
        # use the cli with the expanded source config string
        cli_line = (
            f" --templates {TEMPLATES_FOLDER}"
            f" --input {CONFIG_STRING}"
            f" --name {TEMPLATE_NAME}"
            f" --output {outfile}"
        )
        log.debug(f"{cli_line.split()=}")
        success: bool = _main(*cli_line.split())
        assert success
        verify_output(outfile)
