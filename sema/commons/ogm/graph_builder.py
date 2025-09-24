import yaml
from pathlib import Path
from rdflib import Graph, Namespace
from .graph_blueprint import GraphBlueprint
from .graph_wrapper import GraphWrapper

class GraphBuilder:
    def __init__(
            self,
            namespaces: dict[str, str] = {},
            blueprint: GraphBlueprint | dict | Path | str | None = None
        ):
        base = namespaces.get("@base", "urn:nil:")

        namespaces = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            **{k: v for k, v in namespaces.items() if k != "@base"}
        }

        self._blueprint: GraphBlueprint = self._parse_blueprint(blueprint)
        self.graph: Graph | None = None
        self._graph_wrapper: GraphWrapper = GraphWrapper(base=base)

        for prefix, namespace in namespaces.items():
            assert namespace[-1] in ("#", "/", ":")
            self._graph_wrapper.bind(prefix, Namespace(namespace))
    
    @staticmethod
    def _split_blueprint(data: dict) -> tuple[dict, dict]:
        head = data.get("$") or {}  # data["$"] may exist, but can still be None
        body = {k: v for k, v in data.items() if k != "$"}
        return head, body

    @staticmethod
    def _parse_blueprint(blueprint) -> GraphBlueprint:
        if isinstance(blueprint, GraphBlueprint):
            return blueprint
        elif isinstance(blueprint, dict):
            head, body = GraphBuilder._split_blueprint(blueprint)
            return GraphBlueprint(body=body, **head)
        elif isinstance(blueprint, Path):
            with open(blueprint, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
            head, body = GraphBuilder._split_blueprint(data)
            return GraphBlueprint(body=body, **head)
        elif isinstance(blueprint, str):
            raise NotImplementedError # TODO implement blueprint_uri (str should contain "://")
        else:
            return GraphBlueprint()

    def _build(self) -> None:
        for prefix, namespace in self._blueprint.prefix.items():
            self._graph_wrapper.bind(prefix, namespace)

        for identifier, properties in self._blueprint.body.items():
            self._graph_wrapper.create_iri_node(
                identifier=identifier,
                a=properties.get("$type"),
                label=properties.get("$label"),
                properties={k: v for k, v in properties.items() if not k.startswith("$")}
            )
        
        self.graph = self._graph_wrapper.unwrap()

    def build(self) -> Graph:
        self._build()
        assert self.graph is not None
        return self.graph
