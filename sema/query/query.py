import logging
from abc import ABC, abstractmethod
from typing import Callable, Generator, Iterable, List, Tuple, Union

import pandas as pd
from rdflib import Graph
from rdflib.query import Result
from rdflib.plugins.sparql.processor import SPARQLResult

from sema.commons.store import RDFStore, URIRDFStore

from .exceptions import (
    CompatibilityCheckerNotCallable,
    MultipleSourceTypes,
    NoCompatibilityChecker,
    NoGraphSource,
    NotASubClass,
    WrongInputFormat,
)

log = logging.getLogger(__name__)


# Create abstract class for making a contract by design for devs ##
class QueryResult(ABC):
    """
    Class that encompasses the result from a performed query

    :param list data: query result data
    :param str query: query

    """

    @abstractmethod
    def as_csv(self, fileoutputlocation: str, sep: str = ","):
        """
        From the query result build a standard list of dicts,
            where each key is the relation in the triplet.

        :param reslist: list with the query.
        """
        pass  # pragma: no cover

    @abstractmethod
    def to_list(self) -> List:
        """
        Returns the list of query responses

        :return: List of query responses
        :rtype: list
        """
        pass  # pragma: no cover

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Converts the result query to a dictionary.
            Each key having a list with every query row.

        :return: Query as a dictionary.
        :rtype: dict
        """
        pass  # pragma: no cover

    @abstractmethod
    def to_dataframe(self) -> pd.DataFrame:
        """
        Converts the result query to a pandas dataframe.

        :return: Query as a dataframe.
        :rtype: pd.Dataframe
        """
        pass  # pragma: no cover

    @abstractmethod
    def __len__(self) -> int:
        """
        Returns the length of the query result.

        :return: Length of the query result.
        :rtype: int
        """
        pass  # pragma: no cover

    @property
    @abstractmethod
    def columns() -> Iterable:
        """
        Returns the columns of the query result.
        :return: Columns of the query result.
        :rtype: Iterable
        """
        pass  # pragma: no cover

    registry = set()

    @staticmethod
    def register(constructor):
        if not issubclass(constructor, QueryResult):
            raise NotASubClass
        if not getattr(constructor, "check_compatibility", False):
            raise NoCompatibilityChecker
        QueryResult.registry.add(constructor)

    @staticmethod
    def build(data: list, query: str = ""):
        """
        QueryResult main builder
            Accepts a query response and a query.

        :param list data: query response.
        :param str query: query made.
        :return: QueryResult class apropriate for the query response.
        :rtype: QueryResult
        """

        for constructor in QueryResult.registry:
            if constructor.check_compatibility(data, query) is True:
                return constructor(data, query)

        raise WrongInputFormat


class DFBasedQueryResult(QueryResult):
    """
    Class that encompasses the result from a performed query.
        When the result is iformatted as a pandas dataframe
    """
    def __init__(self, df: pd.DataFrame, query: str = ""):
        """
        :param df: the result of the query as a pandas dataframe
        :type df: pd.DataFrame
        :param query: the sparql query leading to this result
        :type query: str
        """
        self.query = query
        self.df = df

    def as_csv(self, file_output_path: str, sep: str = ","):
        self.df.to_csv(file_output_path, sep=sep, index=False)

    def to_list(self) -> List:
        return self.df.to_dict(orient="records")

    def to_dict(self) -> dict:
        return self.df.to_dict(orient="list")

    def to_dataframe(self) -> pd.DataFrame:
        return self.df.copy()

    def __len__(self) -> int:
        return len(self.df)

    @property
    def columns(self) -> Iterable:
        return self.df.columns

    @staticmethod
    def check_compatibility(df: pd.DataFrame, query: str) -> bool:
        return isinstance(df, pd.DataFrame) and isinstance(query, str)


class SPARQLQueryResult(DFBasedQueryResult):
    """
    Class that encompasses the result from a performed query.
        When the result is return as a rdflib.query.Result
    """

    @staticmethod
    def sparql_results_to_df(result: SPARQLResult) -> pd.DataFrame:
        """
        Export results from an rdflib SPARQL query into a `pandas.DataFrame`,
        using Python types. See https://github.com/RDFLib/rdflib/issues/1179
        and https://github.com/RDFLib/sparqlwrapper/issues/205.
        """
        return pd.DataFrame(
            data=([None if x is None else x.toPython() for x in row] for row in result),
            columns=[str(x) for x in result.vars],
        )

    def __init__(self, result: Result, query: str = ""):
        """
        :param df: the result of the query as a pandas dataframe
        :type df: pd.DataFrame
        :param query: the sparql query leading to this result
        :type query: str
        """
        super().__init__(self.sparql_results_to_df(result), query)

    @staticmethod
    def check_compatibility(data, query) -> bool:
        return isinstance(data, Result) and isinstance(query, str)


QueryResult.register(DFBasedQueryResult)
QueryResult.register(SPARQLQueryResult)


class GraphSource(ABC):
    @abstractmethod
    def query(self, sparql: str) -> QueryResult:
        """
        Function that queries data with the given sparql

        :param sparql: sparql statement logic for querying data.
        """
        pass  # pragma: no cover

    registry = set()

    @staticmethod
    def register(constructor):
        # assert that constructor is for a subclass of QueryResult
        # e.g. check if method check_compatibility is present
        if not issubclass(constructor, GraphSource):
            raise NotASubClass(parent_class="GraphSource")
        check_compatibility_function = getattr(
            constructor, "check_compatibility", False
        )
        if not check_compatibility_function:
            raise NoCompatibilityChecker
        if not isinstance(check_compatibility_function, Callable):
            raise CompatibilityCheckerNotCallable
        GraphSource.registry.add(constructor)

    @staticmethod
    def build(*sources):
        """
        GrasphSource main builder
            export a tabular data file based on the users preferences.
        :param sources: source of graph

        :return: GraphSource class appropriate files.
        :rtype: GraphSource
        """

        for constructor in GraphSource.registry:
            if constructor.check_compatibility(*sources) is True:
                return constructor(*sources)

        raise WrongInputFormat(
            input_format="str, str, ...", class_failed="GraphSource"
        )

    @staticmethod
    def detect_source_type(*sources: Union[str, Iterable]) -> str:
        """
        From the input sources it will get a list/generator with the types,
            It will check if there is only one type, and return it.
            Otherwise raise error for Multiple Sources.

        :param sources: files or endpoints
        :return: The source type of the given inputs.
        :rtype: str
        """
        source_type = generator_of_source_types(*sources)
        if isinstance(source_type, Iterable):
            # In case the source type is a generator
            source_type = [f for f in source_type]
            source_type = set(source_type)
            # For multiple inputs they need to have the same source_type
            if len(source_type) > 1:
                raise MultipleSourceTypes
            source_type = list(source_type)[-1]
        return source_type


class MemoryGraphSource(GraphSource):
    """
    Class that makes a GraphSource from instatiated graphs.

    :param graph: rdf knowledge graph.
    """

    def __init__(self, graph: Graph) -> None:
        super().__init__()
        assert graph is not None, NoGraphSource
        self.graph = graph

    def parse(self, *sources):
        for f in sources:
            log.debug(f"loading graph from file {f}")
            try:
                self.graph.parse(f)
            except Exception as e:
                log.exception(e)
                file_extension = f.split(".")[-1]
                log.debug(f"parsing {f} and applying format {file_extension=}")
                self.graph.parse(f, format=file_extension)

    def query(self, sparql: str) -> QueryResult:
        log.debug(f"executing sparql {sparql}")
        result = self.graph.query(sparql)
        return QueryResult.build(result, query=sparql)

    @staticmethod
    def check_compatibility(*graph):
        return isinstance(graph[-1], Graph)


class FileGraphSource(MemoryGraphSource):
    """
    Class that makes a GraphSource from given turtle file(s)

    :param *sources: turtle files that should be converted into a single
        knowledge graph.
    """

    def __init__(self, *sources):
        graph = Graph()
        super().__init__(graph)
        self.parse(*sources)

    @staticmethod
    def check_compatibility(*sources: Tuple):
        source_type = GraphSource.detect_source_type(*sources)
        return source_type == "file"


class SPARQLGraphSource(GraphSource):
    """
    Class that makes a GraphSource from given url endpoint

    :param url: url of the endpoint to make the GraphSource from.
    """

    def __init__(self, url):
        super().__init__()
        self.endpoint = url

    def query(self, sparql: str) -> QueryResult:
        store: RDFStore = URIRDFStore(self.endpoint)
        result: Result = store.select(sparql)
        return QueryResult.build(result, query=sparql)

    @staticmethod
    def check_compatibility(*sources):
        source_type = GraphSource.detect_source_type(*sources)
        return source_type == "sparql-endpoint"


GraphSource.register(MemoryGraphSource)
GraphSource.register(FileGraphSource)
GraphSource.register(SPARQLGraphSource)


def detect_single_source_type(source: str) -> str:
    """
    Check the source type. Restrain only to files, or endpoints

    :param source: files or endpoints
    :return: The source type of the given input.
        Endpoint or File
    :rtype: str

    """
    source_type = "file"
    if source.startswith("http"):
        query_ask = "ask where {?s ?p [].}"
        store = URIRDFStore(source)
        try:
            store.select(query_ask)
            source_type = "sparql-endpoint"
        except Exception:
            log.debug(f"tested {source} not a sparql endpoint")
    return source_type


def generator_of_source_types(*source: Union[str, Iterable]) -> Generator:
    """
    Check the source type. Restrain only to files, or endpoints.
        It will return a generator where each item is a source_type.

    :param source: files or endpoints
    """
    for src in source:
        if src and isinstance(src, str):
            yield detect_single_source_type(src)
        else:
            yield None
