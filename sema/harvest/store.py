import logging
from pathlib import Path
from typing import Iterable, List

from rdflib import Graph
from rdflib.plugins.sparql.processor import Result

from sema.commons.j2 import J2RDFSyntaxBuilder
from sema.commons.store import GraphNameMapper, RDFStore, RDFStoreDecorator

from .helper import resolve_sparql

log = logging.getLogger(__name__)


# The syntax-builder for travharv
QUERY_BUILDER: J2RDFSyntaxBuilder = J2RDFSyntaxBuilder(
    templates_folder=str(Path(__file__).parent / "templates")
)

# The default URN BASE fopr travharv
DEFAULT_URN_BASE = "urn:traversal-harvesting:"


class RDFStoreAccess(RDFStoreDecorator):
    """Decorator class adding some trav-harv specific features"""

    def __init__(
        self,
        core: RDFStore,
        name_mapper: GraphNameMapper = GraphNameMapper(base=DEFAULT_URN_BASE),
    ):
        super().__init__(core)
        self._qryBuilder = QUERY_BUILDER
        self._nmapper = name_mapper

    def select_subjects(self, sparql) -> List[str]:
        result: Result = self.select(sparql)

        # todo convert response into list of subjects
        list_of_subjects = [row[0] for row in result]
        log.debug(f"length list_of_subjects: {len(list_of_subjects)}")
        log.debug(f"list_of_subjects: {list_of_subjects}")
        return list_of_subjects

    def select_subjects_for_ppath(self, subject, property_path, NSM):
        pre_sparql = self._qryBuilder.build_syntax(
            "trajectory.sparql",
            subject=subject,
            property_trajectory=property_path,
        )
        sparql = resolve_sparql(pre_sparql, NSM)
        log.debug(f"{sparql=}")
        return self.select_subjects(sparql)

    def verify_path(self, subject, property_path, NSM):
        pre_sparql = self._qryBuilder.build_syntax(
            "trajectory.sparql",
            subject=subject,
            property_trajectory=property_path,
        )
        sparql = resolve_sparql(pre_sparql, NSM)
        result: Result = self.select(sparql)

        list_of_bindings = [row for row in result]
        return bool(len(list_of_bindings) > 0)

    def all_triples(self):
        return self.select("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")

    def insert_for_config(self, graph: Graph, name_config: str) -> None:
        """inserts the triples from the passed graph
        into a graph tied to this name_config

        :param graph: the graph of triples to insert
        :type graph: Graph
        :param name_config: the name of the config
        :type name_config: str
        :rtype: None
        """
        ng: str = self._nmapper.key_to_ng(name_config)
        # chekc if graph is not Nonetype or empty
        if graph is None or len(graph) == 0:
            log.warning(
                f"Graph for {name_config} is empty. Nothing to insert."
            )
            return
        return self.insert(graph, ng)

    def lastmod_ts_for_config(self, name_config: str):
        ng: str = self._nmapper.key_to_ng(name_config)
        return self.lastmod_ts(ng)

    def verify_max_age_of_config(
        self, name_config: str, age_minutes: int
    ) -> bool:
        """verifies that a certain graph is not aged older
        than a certain amount of minutes

        :param name_config: the name of the config to check
        :type name_config: str
        :param age_minutes: the max acceptable age in minutes
        :type age_minutes: int
        :return: True if the contents of the store associated
        to the config has aged less than the passed number of
        minutes in the argument, else False
        :rtype: bool
        """
        ng: str = self._nmapper.key_to_ng(name_config)
        return self.verify_max_age(ng, age_minutes)

    @property
    def name_configs(self) -> Iterable[str]:
        """returns the known & managed name-configs in the store

        :return: the list of name-configs, known and managed
        (but possibly already deleted, but not forgotten) in this store
        :rtype: List[str]
        """
        return self._nmapper.get_kets_in_store(self)

    def drop_graph_for_config(self, name_config: str) -> None:
        """drops the content in rdf_store associated to specified name_config
        (and all its contents)

        :param name_config: the uri describing the named_graph to drop
        :type name_config: str
        :rtype: None
        """
        ng: str = self._nmapper.key_to_ng(name_config)
        return self.drop_graph(ng)

    def forget_graph_for_config(self, name_config: str) -> None:
        """forgets about the name_config being under control
        This functions independent of the drop_graph method.
        So any client of this service is expected to decide when
        (or not) to combine both

        :param name_config: the uri describing the named_graph to drop
        :type name_config: str
        :rtype: None
        """
        ng: str = self._nmapper.key_to_ng(name_config)
        return self.forget_graph(ng)
