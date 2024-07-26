from sema.commons.service import ServiceBase, ServiceResult, ServiceTrace
from typing import Tuple
from sema.commons.store import create_rdf_store
from sema.commons.fileformats import format_from_filepath
from .url_to_graph import get_graph_for_format
from rdflib import Graph
from logging import getLogger
from typing import Iterable, List


log = getLogger(__name__)


class DiscoveryResult(ServiceResult):
    def __init__(self):
        self._success = False
        self._graph = Graph()

    @property
    def success(self) -> bool:
        return self._success

    @property
    def graph(self) -> Graph:
        return self._graph


class DiscoveryTrace(ServiceTrace):
    def toProv(self):
        ...


class DiscoveryService(ServiceBase):
    def __init__(self, *, subject_uri: str, request_mimes: str = None, read_uri: str = None, write_uri: str = None, named_graph: str = None, output_file: str = None, output_format: str = None):
        # actual task inputs
        self.subject_uri = subject_uri
        self.request_mimes = [mt.strip() for mt in request_mimes.split(',')] if request_mimes else []

        # output options
        self._store, self._output_file = None, None
        if read_uri:
            self._store = create_rdf_store(read_uri, write_uri) if read_uri else None
            self._named_graph = named_graph
        if output_file:
            self._output_file = output_file
            self._output_format = output_format or format_from_filepath(output_file)

        # state intialization
        self._result, self._trace = None, None

    def _discover_subject(self):
        """Discover triples describing the subject (assumed at subject_url)
           and add them to the result graph
        """
        find_triples_for_subject(self.subject_uri, self.request_mimes, self._result.graph, self._trace)

    def _output_result(self):
        g = self._result.graph
        if self._store:
            self._store.add_graph(g, self._named_graph)

        if self._output_file:
            # TODO cover export to stdout requested as output_file == "-"
            g.serialize(self._output_file, format=self._output_format)

    def process(self) -> Tuple[ServiceResult, ServiceTrace]:
        assert self._result is None, "Service has already been executed"

        self._result = DiscoveryResult()
        self._trace = DiscoveryTrace()

        try:
            self._discover_subject()
            self._output_result()
            self._result._success = True
        except Exception as e:
            log.exception(f"Error during discovery of {self.subject_uri}", exc_info=e)

        return self._result, self._trace


def find_triples_for_subject(subject_uri: str, request_mimes: Iterable[str] = [], result_graph: Graph = None, tracer: DiscoveryTrace = None):
    """Discover triples describing the subject (assumed at subject_url)
       and add them to the result graph
    """
    result_graph = result_graph or Graph()
    tracer = tracer or DiscoveryTrace()

    # TODO get tracing and semantic straight by rewriting the following
    get_graph_for_format(subject_uri, request_mimes, result_graph)

    return result_graph