from pathlib import Path

import pytest

from sema.subyt.api import Source
from sema.subyt.sources import CSVFileSource, SourceFactory
from tests.conftest import log

MY_FOLDER = Path(__file__).parent
DATA_FOLDER = MY_FOLDER / "resources"
INPUT_FILE = DATA_FOLDER / "data_ages_tabs_comments.tsv"
HEADER = "name\tage"
DELIMITER = "\t"
MIME_TYPE = "text/csv"
CONFIG_DICT = {
    "path": str(INPUT_FILE),
    "header": HEADER,
    "delimiter": DELIMITER,
    "comment": "#",
    "skip_blank_lines": True,
    "mime": MIME_TYPE,
}


@pytest.mark.parametrize("source_param", [CONFIG_DICT])
def test_source_factory_config_handling(source_param: str | dict) -> None:
    source: Source = SourceFactory.make_source(source_param)
    assert source is not None
    assert isinstance(source, CSVFileSource)
    log.debug("checking that comments are blank lines are skipped...")
    with source as items:
        data = list(items)
        assert len(data) == 3
        assert data[0] == {"name": "Bram", "age": "40"}
        assert data[1] == {"name": "Steve", "age": "48"}
        assert data[2] == {"name": "Marc", "age": "54"}
