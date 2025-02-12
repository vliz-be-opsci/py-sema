from sema.subyt.api import Source
from sema.subyt.sources import CSVFileSource, FilteringSource, SourceFactory
from tests.conftest import TEST_FOLDER


class FixedDataListSource(Source):
    def __init__(self):
        self._data: list[dict[str, any]] = [
            {"name": "theo", "parent": "stef"},
            {"name": "fien", "parent": "marc"},
            {"name": "tuur", "parent": "marc"},
            {"name": "jef", "parent": "stef"},
        ]

    def __enter__(self):
        return iter(self._data)

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def test_verify_base_source():
    fdls = FixedDataListSource()
    with fdls as items:
        data = [item for item in items]
        assert len(data) == 4
        assert data[0]["name"] == "theo"
        assert data[2]["parent"] == "marc"


def test_filtered_source() -> None:
    fdls = FixedDataListSource()
    upfs = FilteringSource(fdls, "the unique parent = {parent}")
    with upfs as items:
        data = [item for item in items]
        assert len(data) == 2
        assert data[0]["parent"] == "stef"
        assert data[1]["parent"] == "marc"
        assert data[0]["name"] == "theo"
        assert data[1]["name"] == "fien"


def test_filtered_csv_source() -> None:
    csv_source = SourceFactory.make_source(
        str(TEST_FOLDER / "subyt/in/data_countries.csv")
    )
    assert csv_source is not None
    assert isinstance(csv_source, CSVFileSource)
    with csv_source as items:
        assert len([item for item in items]) == 246

    upfs = SourceFactory.make_source(
        str(TEST_FOLDER / "subyt/in/data_countries.csv"),
        unique_pattern="{English short name lower case:1}",
    )
    assert upfs is not None
    assert isinstance(upfs, FilteringSource)
    with upfs as items:
        uniq_leadchar_countries = [item for item in items]

        expected_leadchars = "AÅBCDEFGHIJKLMNOPQRSTUVWYZ"
        assert len(uniq_leadchar_countries) == len(expected_leadchars)

        for i, elc in enumerate(expected_leadchars):
            assert uniq_leadchar_countries[i][
                "English short name lower case"
            ].startswith(elc)


def test_filtered_json_source() -> None:
    json_source = SourceFactory.make_source(
        str(TEST_FOLDER / "subyt/in/data_team.json")
    )
    assert json_source is not None
    with json_source as items:
        assert len([item for item in items]) == 5

    upfs = SourceFactory.make_source(
        str(TEST_FOLDER / "subyt/in/data_team.json"),
        unique_pattern="{orcid:9}",
    )
    assert upfs is not None
    with upfs as items:
        uniq_lead9_orcids = [item for item in items]
        assert len(uniq_lead9_orcids) == 3
        print(f"{uniq_lead9_orcids=}")
        for i in range(0, 3):
            assert uniq_lead9_orcids[i]["orcid"].startswith(f"0000-000{i + 1}")


def test_unique_processing() -> None:
    # TODO run a full Subyt process
    # with output to some tempdir --> files to be checked and verified

    # take team json
    # use the cli with the -u # option
    # check the output files
    ...
