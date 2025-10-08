import json
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
            return self.__application_ld_json__(destination=destination, *args, **kwargs)
        
        return self.__text_turtle__(destination=destination, *args, **kwargs)

    
    def __text_turtle__(self, destination=None, *args, **kwargs) -> str:
        return self.graph.serialize(
            destination=destination,
            format="text/turtle",
            *args,
            **kwargs
        )

    def __application_ld_json__(self, destination=None, *args, **kwargs) -> str:
        indent = kwargs.get("indent", 4)
        data = json.loads(self.graph.serialize(
            format="application/ld+json",
            context=self.graph._jsonld_context_repr if hasattr(self.graph, "_jsonld_context_repr") else None,
            auto_compact=True,
            indent=indent,
            *args,
            **kwargs
        ))

        data["@graph"] = sorted(data["@graph"], key=lambda node: node.get("@id"))

        if destination:
            json.dump(data, open(destination, "w", encoding="utf-8"), indent=indent)

        return json.dumps(data, indent=indent)

    @abstractmethod
    def _map(self) -> Graph:
        raise NotImplementedError
