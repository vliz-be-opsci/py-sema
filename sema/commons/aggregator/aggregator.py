import logging
from pathlib import Path

from rdflib import Graph

logger = logging.getLogger(__name__)


class Aggregator:
    def __init__(
        self,
        input_path: str | Path,
        globs: str,
        output_path: str | Path | None = None,
        output_format: str | None = None,
    ) -> None:
        self.input_path = Path(input_path)
        self.output_path = Path(
            output_path or self.input_path / "graph.ttl"
        )  # output path should include the file name
        self.output_format = output_format or "text/turtle"
        self.globs = {
            k.strip(): v.strip()
            for k, v in (i.strip().split(":") for i in globs.split(","))
        }
        self.graph = Graph()

    def process(self) -> None:
        open(
            self.output_path, "w"
        ).close()  # required for RecursionError check
        for glb, fmt in self.globs.items():
            for p in self.input_path.rglob(glb):
                if p.is_file():
                    if p == self.output_path:
                        raise RecursionError(
                            "output file is in the input directory"
                        )
                    try:
                        self.graph.parse(p, format=fmt)
                    except Exception as e:
                        logger.error(f"failed to parse {p}: {e}")

        self.graph.serialize(self.output_path, format=self.output_format)
