from rdflib import Graph
from abc import ABC, abstractmethod


class ObjectGraphMapper(ABC):
    def __init__(self):
        self._graph: Graph | None = None
    
    @abstractmethod
    def _map(self) -> Graph:
        ...

    def serialize(self, *args, destination=None, **kwargs):
        if not self._graph: self._graph = self._map()
        assert self._graph is not None
        return self._graph.serialize(
            *args,
            destination=(destination or "./object_graph_mapping.ttl"),
            **kwargs
        )

    def __str__(self, *args, format="text/turtle", **kwargs):
        if not self._graph: self._graph = self._map()
        assert self._graph is not None
        return self._graph.serialize(*args, format=format, **kwargs)
