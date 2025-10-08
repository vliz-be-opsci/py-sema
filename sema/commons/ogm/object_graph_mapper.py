from rdflib import Graph
from abc import ABC, abstractmethod


class ObjectGraphMapper(ABC):
    def __init__(self):
        self._graph: Graph | None = None

    @property
    def graph(self) -> Graph:
        if not isinstance(self._graph, Graph): self._graph = self._map()
        assert isinstance(self._graph, Graph), "self._map() must return a Graph"
        return self._graph

    def serialize(self, destination=None, format=None, *args, **kwargs) -> None:
        self.__str__(
            destination=destination or "./object_graph_mapping.ttl",
            format=format,
            *args,
            **kwargs
        )

    def __str__(self, destination=None, format=None, *args, **kwargs) -> str:
        if format == "application/ld+json":
            return self.graph.serialize(
                destination=destination,
                format=format,
                context=self.graph._jsonld_context_repr if hasattr(self.graph, "_jsonld_context_repr") else None,
                auto_compact=True,
                indent=4,
                *args,
                **kwargs
            )

        return self.graph.serialize(
            destination=destination,
            format=format or "text/turtle",
            *args,
            **kwargs
        )

    @abstractmethod
    def _map(self) -> Graph:
        raise NotImplementedError
