import pandas as pd
import pytest

from sema.query import (
    DEFAULT_TEMPLATES_FOLDER,
    DefaultSparqlBuilder,
    GraphSource,
    QueryResult,
)
from sema.query.exceptions import (
    CompatibilityCheckerNotCallable,
    MultipleSourceTypes,
    NoCompatibilityChecker,
    NotASubClass,
    WrongInputFormat,
)
from sema.query.query import SPARQLGraphSource, FileGraphSource, MemoryGraphSource
from const import (
    ALL_TRIPLES_SPARQL,
    BODC_ENDPOINT,
    TTL_FILE_IN_URI,
    TTL_FILES_TO_TEST,
    graph,
)
from conftest import log


@pytest.mark.parametrize(
    "source_args, source_type",
    [
        (TTL_FILES_TO_TEST, FileGraphSource),
        ([BODC_ENDPOINT], SPARQLGraphSource),
        ([TTL_FILE_IN_URI], FileGraphSource),
        ([graph], MemoryGraphSource),
    ],
)
def test_factory_choice(source_args, source_type):
    source = GraphSource.build(*source_args)
    assert type(source) is source_type


@pytest.mark.parametrize(
    "source_args, query, query_response_length",
    [
        (TTL_FILES_TO_TEST, ALL_TRIPLES_SPARQL, 20),
        (BODC_ENDPOINT, ALL_TRIPLES_SPARQL, 25),
        (TTL_FILE_IN_URI, ALL_TRIPLES_SPARQL, 25),
        ([graph], ALL_TRIPLES_SPARQL, 20),
    ],
)
def test_query(source_args, query, query_response_length):
    if isinstance(source_args, str):
        source_args = [source_args]
    source = GraphSource.build(*source_args)
    result = source.query(query)
    assert result._data is not None
    assert set(result._data[0].keys()) == set(["s", "o", "p"])
    assert len(result._data) == query_response_length
    assert len(result) == query_response_length


def test_query_functions():
    source = GraphSource.build(*TTL_FILES_TO_TEST)
    result = source.query(ALL_TRIPLES_SPARQL)

    assert type(result.to_list()) == list
    assert type(result.to_dict()) == dict
    assert type(result.to_dataframe()) == pd.DataFrame


class DummyGraphSource(GraphSource):
    pass  # pragma: no cover


class Dummy2GraphSource(GraphSource):
    @property
    def check_compatibility():
        return None


@pytest.mark.parametrize(
    "constructor, CustomException",
    [
        (QueryResult, NotASubClass),
        (DummyGraphSource, NoCompatibilityChecker),
        (Dummy2GraphSource, CompatibilityCheckerNotCallable),
    ],
)
def test_class_register_raises(constructor, CustomException):
    with pytest.raises(CustomException) as exc:
        GraphSource.register(constructor)
    assert exc.type == CustomException


@pytest.mark.parametrize(
    "files, CustomException",
    [
        ([{"test"}], WrongInputFormat),
        ([BODC_ENDPOINT, *TTL_FILES_TO_TEST], MultipleSourceTypes),
    ],
)
def test_class_build_raises(files, CustomException):
    with pytest.raises(CustomException) as exc:
        GraphSource.build(*files)
    assert exc.type == CustomException


def test_full_search():
    # make full search on the endpoint of BODC to see what it returns test on
    #   the BODC server itself first
    test_source = SPARQLGraphSource(BODC_ENDPOINT)
    # make test qry using template from BODC
    log.info("full test")
    j2sqb = DefaultSparqlBuilder(DEFAULT_TEMPLATES_FOLDER)

    qry = j2sqb.build_syntax(
        "bodc-find.sparql", collections=["P01"], regex=".*orca.*"
    )
    log.debug(f"query = {qry}")
    result = test_source.query(qry)
    log.debug(f"result = {result}")
    assert result._data is not None
    assert set(result._data[0].keys()) == set(
        ["uri", "identifier", "prefLabel"]
    )
    assert len(result._data) == 2


def test_xml_response_cabt():
    endpoint: str = "https://id.cabi.org/PoolParty/sparql/cabt"
    query: str = "SELECT * WHERE { ?s ?p ?i. } LIMIT 3"
    source = SPARQLGraphSource(endpoint)
    result = source.query(query)
    df = result.to_dataframe()
    assert len(df) == 3