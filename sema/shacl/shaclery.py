import logging
from abc import ABC, abstractmethod
from pathlib import Path
from urllib.parse import urlsplit

import requests
from pyshacl import validate as pyshacl_validate
from rdflib import Graph

from sema.commons.glob.globbery import getMatchingGlobPaths
from sema.commons.service import ServiceBase, ServiceResult, Trace

log = logging.getLogger(__name__)


def _load_graph(source: str | Path | Graph) -> Graph:
    log.debug(f"loading graph content from {source=}")
    if isinstance(source, Graph):
        return source
    elif isinstance(source, (str, Path)):
        g = Graph()
        if isinstance(source, Path):
            source = str(source)
        # now source is str, but still one off url, glob, or single path
        sources: list[str] = []
        if source.startswith("http://") or source.startswith("https://"):
            sources = [source]
        else:  # handle file or glob source
            source = str(Path(source).absolute())
            sources = getMatchingGlobPaths(includes=source, makeRelative=False)
            if len(sources) == 0:
                raise ValueError(f"No content to be loaded from {source}")

        # now load it all
        for src in sources:
            log.debug(f"Loading graph from source: {src}")
            g.parse(src)
        return g
    else:
        raise ValueError(f"Unsupported graph source type: {type(source)}")


class ShaclResult(ServiceResult):
    """Result of the shacl service"""

    def __init__(self):
        self._success = False

    @property
    def success(self) -> bool:
        return self._success


class Validator(ABC):
    @abstractmethod
    def validate(
        self,
        graph: str | Path | Graph,
        shacl: str | Path | Graph,
    ) -> tuple[bool, Graph]:
        pass

    @staticmethod
    def conf_result_from_report(report: Graph) -> bool:
        ask_conformity: str = """
            PREFIX shacl: <http://www.w3.org/ns/shacl#>
            ASK {
                ?report a shacl:ValidationReport; shacl:conforms true .
            }
        """
        conf_result = report.query(ask_conformity)
        return bool(conf_result)


class PyShaclValidator(Validator):
    def validate(
        self,
        graph: str | Path | Graph,
        shacl: str | Path | Graph,
    ) -> tuple[bool, Graph]:
        log.debug(
            f"Validating graph {graph} against SHACL {shacl} using pySHACL"
        )
        data_graph = _load_graph(graph)
        shacl_graph = _load_graph(shacl)
        log.debug(f"Data graph has {len(data_graph)} triples")
        log.debug(f"SHACL graph has {len(shacl_graph)} triples")
        conf_result, conf_rpt, _ = pyshacl_validate(
            data_graph=data_graph,
            shacl_graph=shacl_graph,
            inference="rdfs",
            debug=True,
        )
        return conf_result, conf_rpt


class GraphDBValidator(Validator):
    def _gdb_validate_url(self, url: str) -> str:
        original = urlsplit(url)
        # wrap the path in /rest and /validate/text
        changed = original._replace(path=f"/rest{original.path}/validate/text")
        return changed.geturl()

    def _request_conf_rpt(self, url: str, shacl_ttl_text: str) -> Graph:
        log.debug(f"GraphDB {url=} for SHACL:\n{shacl_ttl_text}")
        response = requests.post(
            url,
            headers={  # both body sent and response expected in turtle
                "Accept": "text/turtle",
                "Content-Type": "text/turtle",
            },
            data=shacl_ttl_text,
        )
        if response.status_code != 200:
            raise ValueError(
                "GraphDB validation failed with status code "
                f"{response.status_code}: {response.text}"
            )
        conf_rpt: Graph = Graph().parse(data=response.text, format="turtle")
        return conf_rpt

    def validate(
        self,
        graph: str | Path | Graph,
        shacl: str | Path | Graph,
    ) -> tuple[bool, Graph]:
        # graph needs to be URI in this case
        # assert graph is str, and is a valid URI, otherwise raise error
        if not isinstance(graph, str):
            raise ValueError(
                "graph arg must be a URI string for GraphDBValidator, "
                f"got {type(graph)}"
            )
        store_url: str = graph
        validate_url: str = self._gdb_validate_url(store_url)
        shacl_ttl_text: str = _load_graph(shacl).serialize(format="turtle")
        conf_rpt: Graph = self._request_conf_rpt(validate_url, shacl_ttl_text)
        conf_result: bool = Validator.conf_result_from_report(conf_rpt)
        return conf_result, conf_rpt


def select_validator(method: str) -> Validator:
    if method == "pyshacl":
        return PyShaclValidator()
    elif method == "graphdb":
        return GraphDBValidator()
    else:
        raise ValueError(f"Unsupported validation method: {method}")


class Shacl(ServiceBase):
    """The main class for the shacl service."""

    def __init__(
        self,
        *,
        graph: str,
        shacl: str,
        output: str | None = None,
        method: str = "pyshacl",
    ) -> None:
        """Initialize the Shacl Service object

        :param graph: the graph source (file, glob or url) to be validated
        :type graph: str
        :param shacl: the SHACL constraints source (file or url)
        :type shacl: str
        :param output: the location where to write the validation report
        :type output: str | None
        :param method: the validation method to use
        :type method: str
        :return: Shacl object
        :rtype: Shacl
        """
        self.graph = graph
        self.shacl = shacl
        self.output = None if output == "-" else output
        self._result = ShaclResult()
        self._validator: Validator = select_validator(method)

    @Trace.init(Trace)
    def process(self) -> ShaclResult:
        success, report = self._validator.validate(self.graph, self.shacl)
        log.debug(
            f"Validation: {success=} saving report to "
            f"{self.output if self.output else 'stdout'}"
            f" report has {len(report)} triples"
        )

        if self.output is not None:
            report.serialize(destination=self.output, format="turtle")
        else:
            out = report.serialize(format="turtle")
            print(out)
        self._result._success = success
        return self._result
