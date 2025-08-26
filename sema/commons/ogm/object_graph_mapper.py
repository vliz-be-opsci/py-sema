import yaml
from copy import deepcopy
from .graph_builder import GraphBuilder
from .graph_blueprint import GraphBlueprint

class ObjectGraphMapper:
    def __init__(
            self,
            *args,
            blueprint_data: dict | None = None,
            blueprint_path: str | None = None,
            blueprint_uri: str | None = None,
            **kwargs
        ):
        """
        TODO update docstring
        blueprintparsing priority: blueprint_data > blueprint_path > blueprint_uri
        """
        self.blueprint_data = blueprint_data
        self.blueprint_path = blueprint_path
        self.blueprint_uri = blueprint_uri
        self.graph_builder = GraphBuilder(*args, **kwargs)
        self.blueprint = None
        self._blueprint_parsed = False
        self._mapped = False
    
    @staticmethod
    def _split_blueprint(data: dict | None):
        if data:
            body = deepcopy(data)
            head = body.get("$") or {}  # data["$"] may exist, but can still be None
            if "$" in body: body.pop("$")
            return head, body
        else:
            return {}, {}

    def _parse_blueprint(self):
        if self.blueprint_data:
            head, body = self._split_blueprint(self.blueprint_data)
            self.blueprint = GraphBlueprint(body=body, **head)
        elif self.blueprint_path:
            with open(self.blueprint_path, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)
            head, body = self._split_blueprint(data)
            self.blueprint =  GraphBlueprint(body=body, **head)
        elif self.blueprint_uri:
            raise NotImplementedError # TODO implement blueprint_uri
        else:
            self.blueprint = GraphBlueprint()

        self._blueprint_parsed = True

    def _map(self):
        if not self._blueprint_parsed: self._parse_blueprint()

        for prefix, namespace in self.blueprint.prefix.items():
            self.graph_builder.bind(prefix, namespace)

        for identifier, property in self.blueprint.body.items():
            type = property.get("$type")
            if type: property.pop("$type")

            label = property.get("$label")
            if label: property.pop("$label")

            self.create_inode(
                identifier=identifier,
                a=type,
                label=label,
                property=property
            )

        self._mapped = True

    def serialize(self, destination, *args, **kwargs):
        if not self._mapped: self._map()
        return self.graph_builder.serialize(*args, destination=destination, **kwargs)

    def __str__(self, *args, format="text/turtle", **kwargs):
        if not self._mapped: self._map()
        return self.graph_builder.__str__(*args, format=format, **kwargs)

    def create_inode(self, *args, **kwargs):  # TODO rename function
        return self.graph_builder.create_node(*args, **kwargs, kind="iri")

    def create_rnode(self, *args, **kwargs):  # TODO rename function
        return self.graph_builder.create_node(*args, **kwargs, kind="relative")

    def create_bnode(self, *args, **kwargs):  # TODO rename function
        return self.graph_builder.create_node(*args, **kwargs, kind="blank")
    
    def create_node(self, *args, **kwargs):
        return self.graph_builder.create_node(*args, **kwargs)

    def update_node(self, *args, **kwargs):
        return self.graph_builder.update_node(*args, **kwargs)
