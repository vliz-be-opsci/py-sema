import logging
from abc import ABC, abstractmethod
from typing import List, Callable, Union, Iterable, Tuple, Generator

import pandas as pd
from rdflib import Graph
from SPARQLWrapper import SPARQLWrapper

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


class QueryResultFromListDict(QueryResult):
    """
    Class that encompasses the result from a performed query.
        When the result is return as a list of dictionaries.

    :param list data: query result data in the form of a list of dictionaries
    :param str query: query

    """

    def __init__(self, data: list, query: str = ""):
        self._data = data
        self.query = query

    def __str__(self):
        df = self.to_dataframe()
        _str = ""
        if self.query:
            _str = f"Query: \n{self.query} \n"
        _str = _str + f"Table: \n{str(df)}"
        return _str

    def __len__(self):
        return len(self._data)

    def as_csv(self, file_output_path: str, sep: str = ","):
        data = self.to_dataframe()
        data.to_csv(file_output_path, sep=sep, index=False)

    def to_list(self) -> List:
        return self._data

    def to_dict(self) -> dict:
        """
        Builds a dictionary where each key is a column from the query.
        In each key is a list with all the answer of the query.

        :return: The dictionary mapping the query table
        :rtype: dict
        """
        result_rows = self.to_list()
        result_dict = {}
        for row in result_rows:
            columns = row.keys()
            for key in columns:
                # on first use
                if key not in result_dict:
                    # initialise as list
                    result_dict[key] = list()
                # append to list
                result_dict[key] = result_dict[key] + [row[key]]
        return result_dict

    def to_dataframe(self) -> pd.DataFrame:
        result_df = pd.DataFrame()
        for row in self.to_list():
            result_df = pd.concat(
                [result_df, pd.DataFrame(row, index=[0])], ignore_index=True
            )

        return result_df

    # In future the design to match UDAL will require to also expose metadata
    @staticmethod
    def check_compatibility(data, query) -> bool:
        is_list_of_dicts = False
        if isinstance(data, list):
            is_list_of_dicts = True
            for iter in data:
                is_list_of_dicts = isinstance(iter, dict) and is_list_of_dicts

        return is_list_of_dicts and isinstance(query, str)


QueryResult.register(QueryResultFromListDict)


class GraphSource(ABC):
    @abstractmethod
    def query_result_to_list_dicts(reslist: list) -> List:
        """
        From the query result build a standard list of dicts,
            where each key is the relation in the triplet.

        :param reslist: list with the query.
        """
        pass  # pragma: no cover

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
        Kg1tbl main builder
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
            if len(source_type) > 0:
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
                file_extension = f.split(".")[-2]
                self.graph.parse(f, format=file_extension)

    @staticmethod
    def query_result_to_list_dicts(reslist: list) -> list:
        return [{str(v): str(row[v]) for v in reslist.vars} for row in reslist]

    def query(self, sparql: str) -> QueryResult:
        log.debug(f"executing sparql {sparql}")
        reslist = self.graph.query(sparql)
        return QueryResult.build(
            MemoryGraphSource.query_result_to_list_dicts(reslist), query=sparql
        )

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

    def __init__(self, *urls):
        super().__init__()
        self.endpoints = [url for url in urls]

    @staticmethod
    def query_result_to_list_dicts(reslist: list) -> list:
        return [
            {k: row[k]["value"] for k in row}
            for row in reslist["results"]["bindings"]
        ]

    def query(self, sparql: str, return_format="json") -> QueryResult:
        reslist = []
        for url in self.endpoints:
            ep = SPARQLWrapper(url)
            ep.setQuery(sparql)
            # TODO: Allow reading the format from the endpoint.
            ep.setReturnFormat(return_format)
            resdict = ep.query().convert()
            reslist = reslist + SPARQLGraphSource.query_result_to_list_dicts(
                resdict
            )

        query_result = QueryResult.build(reslist, query=sparql)
        return query_result

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
        ep = SPARQLWrapper(source)
        ep.setQuery(query_ask)
        ep.setReturnFormat("json")
        query_info = ep.query().info()
        content_type = query_info.get("content-type", "")
        if "sparql" in content_type:
            source_type = "sparql-endpoint"
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

