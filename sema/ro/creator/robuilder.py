import yaml
from pathlib import Path
from sema.commons.ogm import GraphBuilder
from sema.commons.yml import LoaderBuilder
from .roblueprint import ROBlueprint

class ROBuilder(GraphBuilder):
    def __init__(self, blueprint: Path, blueprint_env: dict, rocrate_path: Path | None = None):
        self.blueprint_env = blueprint_env
        self.rocrate_path = rocrate_path
        super().__init__(
            namespaces={"@base": "urn:rocreator:"},
            blueprint=blueprint
        )

    def _parse_blueprint(self, blueprint) -> ROBlueprint:
        loader = LoaderBuilder().to_resolve(self.blueprint_env).build()
        with open(blueprint, "r", encoding="utf-8") as file:
            data = yaml.load(file, Loader=loader)
        head, body = self._split_blueprint(data)
        return ROBlueprint(body=body, glob_root=self.rocrate_path, **head)

    def _build(self):
        if self._blueprint.context:
            self._graph_wrapper.set_jsonld_context(self._blueprint.context)

        for prefix, namespace in self._blueprint.prefix.items():
            self._graph_wrapper.bind(prefix, namespace)

        root_dataset = self._graph_wrapper.create_relative_node(identifier="./", a="schema:Dataset")

        self._graph_wrapper.create_relative_node(
            identifier="ro-crate-metadata.json",
            a="schema:CreativeWork",
            properties={
                "about": root_dataset,
            }
        )

        for identifier, properties in self._blueprint.body.items():
            a = properties.get("$type")
            label = properties.get("$label")
            properties = {k: v for k, v in properties.items() if not k.startswith("$")}

            if "://" in identifier:
                self._graph_wrapper.create_iri_node(
                    identifier=identifier,
                    a=a,
                    label=label,
                    properties=properties,
                )
            else:  # TODO identifiers like "<my_relative_id>" will give an error when created as a relative node
                self._graph_wrapper.create_relative_node(
                    identifier=identifier,
                    a=a,
                    label=label,
                    properties=properties,
                )

            if a == "File":
                self._graph_wrapper.update_node(
                    identifier=root_dataset,
                    properties={"hasPart": identifier},
                )

            self.graph = self._graph_wrapper.unwrap()
