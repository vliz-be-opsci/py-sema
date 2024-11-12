import logging
from abc import ABC, abstractmethod
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional
from urllib.parse import unquote

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.plugins.stores.sparqlstore import SPARQLStore, SPARQLUpdateStore
from rdflib.query import Result

from sema.commons.clean import clean_uri_str, default_cleaner

log = logging.getLogger(__name__)

UTC_tz = timezone.utc
NIL_NS = "urn:_:nil"
ADMIN_NAMED_GRAPH = "urn:py-rdf-store:admin"
SCHEMA = Namespace("https://schema.org/")
SCHEMA_DATEMODIFIED = SCHEMA.dateModified
g_cfg_kwargs = dict(bind_namespaces="none")


def timestamp():
    return datetime.now(UTC_tz)


class GraphNameMapper:
    """Helper class to convert external keys objects into graph-names."""

    def __init__(self, base: str = "urn:none:"):
        """constructor

        :param base: (optional) base_uri to apply,
        - defaults to 'urn:none'
        :type base: str
        """
        self._base = str(base)

    def key_to_ng(self, key: Any) -> str:
        """converts identifier key object to a named_graph (uri-string)

        :param key: string version of this is used in the named_graph
        :type key: str
        :returns: uri representing the key, to be used as named-graph
        :rtype: str
        """
        return f"{self._base}{clean_uri_str(str(key))}"

    def ng_to_key(self, ng: str) -> str:
        """converts named_graph uri back into the string representation
        of the identifier-key-object

        :param ng: uri of the named-graph
        :type ng: str
        :returns: the str representation of the matching identifier key-object
        :rtype: str
        """
        assert ng.startswith(self._base), (
            f"Unknown {ng=}. " f"It should start with {self._base=}"
        )
        lead: int = len(self._base)
        return unquote(ng[lead:])

    def get_keys_in_store(self, store) -> Iterable[str]:
        """selects those named graphs in the store.named_graphs under our base
        and converts them into config names

        :param store: the store to grab & filter the named_graphs from
        :type store: RDFStore
        :returns: list of str representation sof identifier key objects found
        :rtype: List[str]
        """
        return [
            self.ng_to_key(ng)
            for ng in store.named_graphs
            if ng.startswith(self._base)
        ]  # filter and convert the named_graphs to config names we handle


class RDFStore(ABC):
    """This interface describes the basic contract for having read,
    write operations versus a managed set of named-graphs so that
    the lastmod timestamp on each of these is being tracked properly
    so the 'age' of these can be compared easily to decide on required
    or opportune updates
    """

    def __init__(
        self,
        *,
        cleaner: Callable | None = None,
        mapper: GraphNameMapper | None = None,
    ):
        """Constructor
        :param cleaner: function to clean graphs before insert
        :param mapper: helper class to convert custom key types of any type
        to/from valid named_graph uri-strings
        """
        # TODO reconsider the default below as soon as upper layers start
        # dealing with cleaning config themselves
        # for now we ensure cleaning to fix rdflib-jsonld parsing issue
        cleaner = cleaner or default_cleaner()
        # always ensure a no-op callable
        self._cleaner: Callable = cleaner or (lambda graph: graph)
        self._nmapper: GraphNameMapper = mapper or GraphNameMapper()

    def clean(self, graph: Graph) -> Graph:
        """Cleans the graph as suggested by the constructor setting"""
        return self._cleaner(graph)

    def named_graph_for_key(self, key: Any) -> str:
        """Converts the identifier key into a valid uri useable as named_graph
        :param key: identifier key
        :return: uri of matching named_graph
        """
        return self._nmapper.key_to_ng(key)

    def insert_for_key(self, graph: Graph, key: str) -> None:
        """inserts the triples from the passed graph
        into a graph tied to the key

        :param graph: the graph of triples to insert
        :type graph: Graph
        :param key: the identifier key
        :type key: str
        :rtype: None
        """
        ng: str = self.named_graph_for_key(key)
        return self.insert(graph, ng)

    def verify_max_age_of_key(
        self,
        key: Any,
        age_minutes: int = 0,
        reference_time: datetime | None = None,
    ) -> bool:
        """verifies that a certain graph is "sufficiently young"
        i.e. not aged older than a certain amount of minutes
        or not aged older then a certain reference_time
        (potentially plus some minutes)

        :param key: the name of the config to check
        :type key: str
        :param age_minutes: the max acceptable age in minutes
         - optional, defaults to 0
        :type age_minutes: int
        :param reference_time: the basis for the comparison
         - optional, defaults to now()
        :type reference_time: datetime
        :return: True if the contents of the store associated
        to the config has aged less than the passed number of
        minutes in the argument versus the reference_time, else False
        :rtype: bool
        """
        ng: str = self.named_graph_for_key(key)
        return self.verify_max_age(
            ng, age_minutes=age_minutes, reference_time=reference_time
        )

    @property
    def keys(self) -> Iterable[str]:
        """returns the known & managed identifier keys in the store

        :return: the list of identifier keys, known and managed
        (Note: possibly already deleted, but not forgotten) in this store
        :rtype: List[str]
        """
        return self._nmapper.get_keys_in_store(self)

    def drop_graph_for_key(self, key: Any) -> None:
        """drops the content in graph associated to specified identifier key
        (and all its contents)

        :param key: the uri describing the named_graph to drop
        :type key: str
        :rtype: None
        """
        ng: str = self.named_graph_for_key(key)
        return self.drop_graph(ng)

    def forget_graph_for_key(self, key: Any) -> None:
        """forgets about the identifier key being under control
        This functions independent of the drop_graph method.
        So any client of this service is expected to decide when
        (or not) to combine both

        :param key: the identifier key to which associated graph to forget
        :type key: Any
        :rtype: None
        """
        ng: str = self.named_graph_for_key(key)
        return self.forget_graph(ng)

    @abstractmethod
    def select(self, sparql: str, named_graph: Optional[str]) -> Result:
        """executes a sparql select query, possibly narrowed to
        the named_grap it represents

        :param sparql: the query-statement to execute
        :type sparql: str
        :param named_graph: the uri describing the named_graph into which
          the select should be narrowed
        :type named_graph: str
        :return: the result of the query
        :rtype: Result
        """
        pass  # pragma: no cover

    @abstractmethod
    def insert(self, graph: Graph, named_graph: Optional[str] = None) -> None:
        """inserts the triples from the passed graph into
        the suggested named_graph

        :param graph: the graph of triples to insert
        :type graph: Graph
        :param named_graph: the uri describing the named_graph into which
          the graph should be inserted
        :type named_graph: str
        :rtype: None
        """
        pass  # pragma: no cover

    def verify_max_age(
        self,
        named_graph: str,
        age_minutes: int = 0,
        reference_time: datetime | None = None,
    ) -> bool:
        """verifies that a certain graph is "sufficiently young"
        i.e. not aged older than a certain amount of minutes
        or not aged older then a certain reference_time
        (potentially plus some minutes)

        :param named_graph: the uri describing the named_graph to check
          the age of
        :type named_graph: str
        :param age_minutes: the max acceptable age in minutes
         - optional, defaults to 0
        :type age_minutes: int
        :param reference_time: the basis for the comparison
         - optional, defaults to now()
        :type reference_time: datetime
        :return: True if the contents of the store associated
        to the config has aged less than the passed number of
        minutes in the argument versus the reference_time, else False
        :rtype: bool
        """
        named_graph_lastmod = self.lastmod_ts(named_graph)
        if named_graph_lastmod is None:
            return False
        named_graph_lastmod = named_graph_lastmod.astimezone(UTC_tz)
        reference_time = reference_time or timestamp()
        timelapsed: timedelta = reference_time - named_graph_lastmod
        return bool(timelapsed.total_seconds() <= age_minutes * 60)

    @abstractmethod
    def lastmod_ts(self, named_graph: str) -> datetime:
        """returns the update timestamp of the specified graph
        Note: the implementations should make the stored and returned
        datetime object are
          1. timezone - aware and
          2. placed in the UTC_tz

        :param named_graph: the uri describing the named_graph to get
          the lastmod timestamp of
        :type named_graph: str
        :return: the time of last modification (insert or drop)
        :rtype: datetime
        """
        pass  # pragma: no cover

    @property
    @abstractmethod
    def named_graphs(self) -> Iterable[str]:
        """returns the known & managed named-graphs in the store

        :return: the list of named-graphs, known and managed
          (possibly already deleted) in this store
        :rtype: List[str]
        """
        pass  # pragma: no cover

    @abstractmethod
    def drop_graph(self, named_graph: str) -> None:
        """drops the specifed named_graph (and all its contents)
        Note: dropping any unknown graph should just work without complaints
        Note: dropping a graph still leaves a trail of its 'update'
              in the admin-graph (meaning its age can be verified)
              Consider forget_graph to remove that trail of 'update'

        :param named_graph: the uri describing the named_graph to drop
        :type named_graph: str
        :rtype: None
        """
        pass  # pragma: no cover

    @abstractmethod
    def forget_graph(self, named_graph: str) -> None:
        """forgets about the names_graph being under control
        This functions independent of the drop_graph method.
        So any client of this service is expected to decide when (or not)
        to combine both

        Note: dropping any unknown graph should just work without complaints
        Note: forgetting a graph removes any trail of its 'update'
              in the admin-graph.
              It does nothing to also actually removed the content in the graph

        :param named_graph: the uri describing the named_graph to drop
        :type named_graph: str
        :rtype: None
        """
        pass  # pragma: no cover


class URIRDFStore(RDFStore):
    """This class is used to connect to a SPARQL endpoint and execute
    SPARQL queries

    :param read_uri: The URI of the SPARQL endpoint to read from
    :type read_uri: str
    :param write_uri: The URI of the SPARQL endpoint to write to.
      If not provided, the store can only be read from, not updated.
    :type write_uri: Optional[str]
    """

    def __init__(
        self,
        read_uri: str,
        write_uri: Optional[str] = None,
        *,
        cleaner: Callable | None = None,
        mapper: GraphNameMapper | None = None,
    ):
        super().__init__(cleaner=cleaner, mapper=mapper)
        self.allows_update = False
        self._store_constr = None  # we will delay creating independent stores
        if write_uri is None:

            def store_constr_ro():
                return SPARQLStore(
                    query_endpoint=read_uri, returnFormat="json"
                )

            self._store_constr = store_constr_ro
        else:

            def store_constr_rw():
                return SPARQLUpdateStore(
                    query_endpoint=read_uri,
                    update_endpoint=write_uri,
                    method="POST",
                    autocommit=True,
                )

            self.allows_update = True
            self._store_constr = store_constr_rw

    @property
    def sparql_store(self):  # dynamically (delayed) build of the instance
        if self._store_constr is None:
            raise RuntimeError(
                "SPARQL store is not available. Ensure the store"
                "constructor was properly initialized with valid URIs."
            )
        return self._store_constr()

    def select(self, sparql: str, named_graph: Optional[str] = None) -> Result:
        log.debug(f"exec select {sparql=} into {named_graph=}")
        if named_graph is not None:
            select_graph = Graph(
                store=self.sparql_store, identifier=named_graph, **g_cfg_kwargs  # type: ignore # noqa
            )
        else:
            select_graph = Graph(store=self.sparql_store, **g_cfg_kwargs)  # type: ignore # noqa
        result: Result = select_graph.query(sparql)
        assert isinstance(result, Result), (
            "Failed getting proper result for:" f"{sparql=}, got {result=}"
        )
        log.debug(f"Result from SPARQLStore :: {type(result)=} -> {result=}")
        return result

    def insert(self, graph: Graph, named_graph: Optional[str] = NIL_NS):
        graph = self.clean(graph)
        assert (
            self.allows_update
        ), "data can not be inserted into a store if no write_uri is provided"
        log.debug(f"insertion of {len(graph)=} into ({named_graph=})")
        store_graph = Graph(
            store=self.sparql_store, identifier=named_graph, **g_cfg_kwargs  # type: ignore # noqa
        )
        store_graph += graph.skolemize()
        if named_graph is not None:
            self._update_registry_lastmod(named_graph, timestamp())

    def _update_registry_lastmod(
        self, named_graph: str | None, lastmod: datetime | None = None
    ) -> Iterable[str]:
        """Consults and changes the admin-graph of lastmod entries
        per named_graph.

        :param named_graph: the named_graph to be handled, required,
          can be None to return the list of all available names
        :type named_graph: str (or None)
        :param lastmod: the new lastmod timestamp for this named_graph,
          if None (or not provided) this will 'forget' the named_graph
        :type lastmod: datetime
        :return: the list of named_graphs in management
        :rtype: Iterable[str]
        """
        graph_subject = (
            URIRef(named_graph) if named_graph is not None else None
        )
        response = [named_graph] if named_graph is not None else None

        adm_graph = Graph(
            store=self.sparql_store,
            identifier=ADMIN_NAMED_GRAPH,
            **g_cfg_kwargs,  # type: ignore
        )

        # construct what we are matching for
        pattern = tuple(
            (graph_subject, SCHEMA_DATEMODIFIED, None)
        )  # missing subject or object functions as pattern
        # remove any previous triple for this graph if it is specified
        if graph_subject is not None:
            adm_graph.remove(pattern)  # type: ignore
        else:
            response = [
                str(sub) for (sub, pred, obj) in adm_graph.triples(pattern)  # type: ignore # noqa
            ]

        # insert the new data if provided
        if graph_subject is not None and lastmod is not None:
            triple = (graph_subject, SCHEMA_DATEMODIFIED, Literal(lastmod))
            adm_graph.add(triple)  # type: ignore

        return response or []

    def lastmod_ts(self, named_graph: str) -> datetime:
        adm_graph = Graph(
            store=self.sparql_store,
            identifier=ADMIN_NAMED_GRAPH,
            **g_cfg_kwargs,  # type: ignore
        )
        lastmod: Literal = adm_graph.value(
            URIRef(named_graph), SCHEMA_DATEMODIFIED
        )  # type: ignore
        # above is None if nothing found,
        # else convert the literal to actual .value (datetime)
        return lastmod.value if lastmod is not None else None  # type: ignore

    def drop_graph(self, named_graph: str) -> None:
        store_graph = Graph(
            store=self.sparql_store, identifier=named_graph, **g_cfg_kwargs  # type: ignore # noqa
        )
        self.sparql_store.remove_graph(store_graph)
        self._update_registry_lastmod(named_graph, timestamp())

    def forget_graph(self, named_graph: str) -> None:
        self._update_registry_lastmod(named_graph, None)

    @property
    def named_graphs(self) -> Iterable[str]:
        return self._update_registry_lastmod(None)


class MemoryRDFStore(RDFStore):
    # check if rdflib.Dataset could not help out here,
    # such would allign more logically and elegantly?
    def __init__(
        self,
        *,
        cleaner: Callable | None = None,
        mapper: GraphNameMapper | None = None,
    ):
        super().__init__(cleaner=cleaner, mapper=mapper)
        self._all: Graph = Graph(**g_cfg_kwargs)  # type: ignore
        self._named_graphs = dict()
        self._admin_registry = dict()

    def select(self, sparql: str, named_graph: Optional[str] = None) -> Result:
        target = (
            self._named_graphs[named_graph]
            if named_graph is not None
            else self._all
        )
        return target.query(sparql)

    def insert(
        self, graph: Graph, named_graph: Optional[str] | None = None
    ) -> None:
        graph = self.clean(graph)
        if named_graph is not None:
            if named_graph not in self._named_graphs:
                self._named_graphs[named_graph] = Graph(**g_cfg_kwargs)  # type: ignore # noqa
            named_graph_graph: Graph = self._named_graphs[named_graph]
            named_graph_graph += graph
            self._admin_registry[named_graph] = timestamp()
        self._all += graph

    def lastmod_ts(self, named_graph: str) -> datetime:
        return self._admin_registry.get(named_graph, None)

    def drop_graph(self, named_graph: str) -> None:
        if named_graph is not None and named_graph in self._named_graphs:
            self._all -= self._named_graphs.pop(named_graph)
            self._named_graphs[named_graph] = Graph()
        self._admin_registry[named_graph] = timestamp()

    def forget_graph(self, named_graph: str) -> None:
        self._admin_registry.pop(named_graph)

    @property
    def named_graphs(self) -> Iterable[str]:
        return self._admin_registry.keys()


class RDFStoreDecorator(RDFStore):
    """
    Base-class for «Decorator» implementations that behave like a store,
    by adding features and just wrapping them.
    """

    def __init__(self, store: RDFStore):
        """
        :param store: the actual store to wrap and decorate
        :type store: RDFStore
        """
        # for now decorators do not support stepping inbetween
        # the mapper and cleaner of the core
        self._core = store

    def select(self, sparql: str, named_graph: Optional[str] = None) -> Result:
        return self._core.select(sparql, named_graph)

    def all_triples(self, named_graph: Optional[str] = None) -> Result:
        return self._core.select(
            "SELECT ?s ?p ?o WHERE { ?s ?p ?o }", named_graph
        )

    def insert(self, graph: Graph, named_graph: Optional[str] = None):
        return self._core.insert(graph, named_graph)

    def lastmod_ts(self, named_graph: str) -> datetime:
        return self._core.lastmod_ts(named_graph)

    def drop_graph(self, named_graph: str) -> None:
        return self._core.drop_graph(named_graph)

    def forget_graph(self, named_graph: str) -> None:
        return self._core.forget_graph(named_graph)

    @property
    def named_graphs(self) -> Iterable[str]:
        return self._core.named_graphs
