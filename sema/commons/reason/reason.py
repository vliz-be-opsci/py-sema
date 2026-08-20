import logging
import re
from pathlib import Path
from typing import Any, Iterable

from rdflib import Graph, Namespace
from rdflib.query import Result

from sema.commons.glob import getMatchingGlobPaths
from sema.commons.service import ServiceBase, ServiceResult, Trace
from sema.commons.store import RDFStore

logger = logging.getLogger(__name__)


class ReasonResult(ServiceResult):
    """Result of the reasoner service"""

    def __init__(self, graph: Graph | None = None) -> None:
        self._success: bool = False
        self._graph: Graph | None = graph

    @property
    def success(self) -> bool:
        return self._success

    @property
    def graph(self) -> Graph | None:
        return self._graph


class Reasoner(ServiceBase):
    """
    Reasoner service that executes SPARQL CONSTRUCT queries against RDF sources
    (in-memory graphs, triple files, RDFStores, or endpoints) and outputs
    the reasoned triples.
    """

    def __init__(
        self,
        *,
        sources: Any | None = None,
        queries: str | Path | list[str | Path] | None = None,
        output_path: str | Path | None = None,
        output_format: str | None = None,
        prefixes: dict[str, str] | None = None,
        base: str | None = None,
        input_path: str | Path | None = None,
    ) -> None:
        self._input_path = Path(input_path) if input_path else Path.cwd()
        self._sources = sources if sources is not None else []
        if isinstance(self._sources, (str, Path, Graph, RDFStore)):
            self._sources = [self._sources]
        elif not isinstance(self._sources, (list, tuple, set)):
            self._sources = [self._sources]

        self._queries = queries if queries is not None else []
        if isinstance(self._queries, (str, Path)):
            self._queries = [self._queries]

        self._output_path = Path(output_path) if output_path else None
        self._output_format = output_format or "text/turtle"
        self._prefixes = prefixes or {}
        self._base = base
        self._result = ReasonResult()

    def _resolve_path(self, path_str_or_path: str | Path) -> Path:
        p = Path(path_str_or_path)
        if not p.is_absolute():
            p = (self._input_path / p).resolve()
        return p

    def _collect_query_texts(self) -> list[str]:
        query_texts: list[str] = []
        for q in self._queries:
            is_file_like = isinstance(q, Path) or (
                isinstance(q, str)
                and (
                    q.endswith(".sparql")
                    or q.endswith(".rq")
                    or (
                        "\n" not in q
                        and (
                            "*" in q
                            or "?" in q
                            or "/" in q
                            or "\\" in q
                            or Path(q).suffix in [".sparql", ".rq"]
                        )
                    )
                )
            )
            if is_file_like:
                if isinstance(q, str) and ("*" in q or "?" in q):
                    # glob
                    matches = getMatchingGlobPaths(
                        self._input_path, q, makeRelative=False
                    )
                    for match in sorted(matches):
                        if match.is_file():
                            query_texts.append(
                                match.read_text(encoding="utf-8")
                            )
                else:
                    candidate = (
                        self._resolve_path(q)
                        if isinstance(q, (str, Path))
                        else q
                    )
                    if candidate.is_dir():
                        for match in sorted(
                            candidate.rglob("*.sparql")
                        ) + sorted(candidate.rglob("*.rq")):
                            if match.is_file():
                                query_texts.append(
                                    match.read_text(encoding="utf-8")
                                )
                    elif candidate.is_file():
                        query_texts.append(
                            candidate.read_text(encoding="utf-8")
                        )
                    elif Path(q).is_file():
                        query_texts.append(
                            Path(q).read_text(encoding="utf-8")
                        )
                    else:
                        raise FileNotFoundError(
                            f"SPARQL query file or folder '{q}' not "
                            f"found at '{candidate}'."
                        )
            else:
                # Raw query string
                query_texts.append(str(q))
        return query_texts

    def _inject_prefixes_and_base(self, query_str: str) -> str:
        injected = []
        if self._base and not re.search(
            r"^\s*BASE\s+<", query_str, re.IGNORECASE | re.MULTILINE
        ):
            injected.append(f"BASE <{self._base}>")

        for prefix, uri in self._prefixes.items():
            pattern = rf"^\s*PREFIX\s+{re.escape(prefix)}:\s*<"
            if not re.search(pattern, query_str, re.IGNORECASE | re.MULTILINE):
                injected.append(f"PREFIX {prefix}: <{uri}>")

        if injected:
            return "\n".join(injected) + "\n" + query_str
        return query_str

    def _build_source_graph(self, base_graph: Graph | None = None) -> Graph:
        source_graph = Graph()
        if base_graph is not None:
            source_graph += base_graph

        for prefix, uri in self._prefixes.items():
            source_graph.bind(prefix, Namespace(uri))

        for src in self._sources:
            if isinstance(src, Graph):
                source_graph += src
            elif isinstance(src, RDFStore):
                # Export all triples from store into source_graph
                store_res = src.select(
                    "SELECT ?s ?p ?o WHERE { ?s ?p ?o }", None
                )
                for row in store_res:
                    source_graph.add((row[0], row[1], row[2]))
            elif isinstance(src, (str, Path)):
                src_str = str(src)
                if "*" in src_str or "?" in src_str:
                    matches = getMatchingGlobPaths(
                        self._input_path, src_str, makeRelative=False
                    )
                    for match in sorted(matches):
                        if match.is_file():
                            self._parse_file_into_graph(source_graph, match)
                else:
                    resolved = self._resolve_path(src)
                    if resolved.is_file():
                        self._parse_file_into_graph(source_graph, resolved)
                    elif resolved.is_dir():
                        for match in sorted(resolved.rglob("*")):
                            if match.is_file():
                                try:
                                    self._parse_file_into_graph(
                                        source_graph, match
                                    )
                                except Exception:
                                    pass

        return source_graph

    @staticmethod
    def _parse_file_into_graph(graph: Graph, path: Path) -> None:
        suffix = path.suffix.lower()
        format_map = {
            ".ttl": "turtle",
            ".turtle": "turtle",
            ".jsonld": "json-ld",
            ".json": "json-ld",
            ".nt": "nt",
            ".n3": "n3",
            ".xml": "xml",
            ".rdf": "xml",
        }
        fmt = format_map.get(suffix)
        try:
            if fmt:
                graph.parse(path, format=fmt)
            else:
                graph.parse(path)
        except Exception as e:
            logger.error(f"Failed to parse RDF file {path}: {e}")
            raise e

    def reason(self, base_graph: Graph | None = None) -> Graph:
        """
        Executes configured CONSTRUCT queries against the accumulated
        source graph and returns the resulting Graph of constructed triples.
        """
        source_graph = self._build_source_graph(base_graph=base_graph)
        reasoned_graph = Graph()

        for prefix, uri in self._prefixes.items():
            reasoned_graph.bind(prefix, Namespace(uri))

        query_texts = self._collect_query_texts()
        for raw_query in query_texts:
            query = self._inject_prefixes_and_base(raw_query)
            logger.debug(f"Executing SPARQL CONSTRUCT query:\n{query}")
            res = source_graph.query(query)
            if (
                isinstance(res, Result)
                and getattr(res, "graph", None) is not None
            ):
                reasoned_graph += res.graph
            elif isinstance(res, Iterable):
                for triple in res:
                    reasoned_graph.add(triple)

        return reasoned_graph

    @Trace.init(Trace)
    def process(self) -> ReasonResult:
        reasoned_graph = self.reason()
        if self._output_path:
            self._output_path.parent.mkdir(parents=True, exist_ok=True)
            reasoned_graph.serialize(
                destination=self._output_path, format=self._output_format
            )

        self._result._graph = reasoned_graph
        self._result._success = True
        return self._result


# Convenience alias
Reason = Reasoner
