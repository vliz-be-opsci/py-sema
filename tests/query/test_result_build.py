import pytest

from sema.query import GraphSource, QueryResult
from sema.query.exceptions import (
    NoCompatibilityChecker,
    NotASubClass,
    WrongInputFormat,
)
from sema.query.query import QueryResultFromListDict
from const import TTL_FILES_QUERY_RESULT


@pytest.mark.parametrize(
    "query_response, QueryType",
    [
        (TTL_FILES_QUERY_RESULT, QueryResultFromListDict),
    ],
)
def test_factory_choice(query_response, QueryType):
    query_result = QueryResult.build(query_response)
    assert type(query_result) is QueryType


class DummyQueryResult(QueryResult):
    pass  # pragma: no cover


@pytest.mark.parametrize(
    "constructor, CustomException",
    [(GraphSource, NotASubClass), (DummyQueryResult, NoCompatibilityChecker)],
)
def test_class_register_raises(constructor, CustomException):
    with pytest.raises(CustomException) as exc:
        QueryResult.register(constructor)
    assert exc.type == CustomException


@pytest.mark.parametrize(
    "query_response, CustomException",
    [(["test"], WrongInputFormat), ("test", WrongInputFormat)],
)
def test_class_build_raises(query_response, CustomException):
    with pytest.raises(CustomException) as exc:
        QueryResult.build(query_response)
    assert exc.type == CustomException
