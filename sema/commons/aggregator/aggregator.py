import logging
from pathlib import Path

from rdflib import Graph

from sema.commons.glob import getMatchingGlobPaths
from sema.commons.service import ServiceBase, ServiceResult, Trace

logger = logging.getLogger(__name__)


class AggregatorResult(ServiceResult):
    """Result of the aggregator service"""

    def __init__(self):
        self._success = False

    @property
    def success(self) -> bool:
        return self._success


class Aggregator(ServiceBase):
    def __init__(
        self,
        *,
        input_path: str | Path,
        globs: list[str, dict[str, str]],
        output_path: str | Path | None = None,
        output_format: str | None = None,
    ) -> None:
        self._input_path = Path(input_path)
        self._globs = globs
        self._output_path = Path(
            output_path or self._input_path / "graph.ttl"
        )  # output path should include the file name
        self._output_format = output_format or "text/turtle"
        self._graph = Graph()
        self._result = AggregatorResult()

    @Trace.init(Trace)
    def process(self) -> AggregatorResult:
        for glob in self._globs:
            if isinstance(glob, str):
                g = glob
                fmt = None
            elif isinstance(glob, dict):
                assert (
                    len(glob) == 1
                ), "each glob dict should have exactly one key-value pair"
                g, fmt = next(iter(glob.items()))
            else:
                raise TypeError("globs should be a list of strings or dicts")

            for p in getMatchingGlobPaths(
                self._input_path, g, makeRelative=False
            ):
                if p.is_file():
                    if p.resolve() == self._output_path.resolve():
                        continue
                    try:
                        self._graph.parse(p, format=fmt)
                    except Exception as e:
                        logger.error(f"failed to parse {p}: {e}")

        self._output_path.parent.mkdir(parents=True, exist_ok=True)
        self._graph.serialize(self._output_path, format=self._output_format)
        self._result._success = True
        return self._result
