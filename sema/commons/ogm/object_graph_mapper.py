from rdflib import Graph
from .graph_builder import GraphBuilder

class ObjectGraphMapper:
    def __init__(self):
        self._graph: Graph | None = None
    
    def _map(self):
        self._graph = GraphBuilder().build()

    def serialize(self, *args, destination=None, **kwargs):
        if not self._graph: self._map()
        assert self._graph is not None
        return self._graph.serialize(
            *args,
            destination=(destination or "./object_graph_mapping.ttl"),
            **kwargs
        )

    def __str__(self, *args, format="text/turtle", **kwargs):
        if not self._graph: self._map()
        assert self._graph is not None
        return self._graph.serialize(*args, format=format, **kwargs)
