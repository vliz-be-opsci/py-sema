from pathlib import Path

import yaml

from sema.commons.ogm import GraphBuilder
from sema.commons.reason import Reasoner
from sema.commons.yml import LoaderBuilder

from .roblueprint import ROBlueprint


class ROBuilder(GraphBuilder):
    def __init__(
        self,
        blueprint: Path,
        blueprint_env: dict,
        rocrate_path: Path | None = None,
    ):
        self.blueprint_env = blueprint_env
        self.rocrate_path = rocrate_path
        super().__init__(
            namespaces={"@base": "urn:rocreator:"}, blueprint=blueprint
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

        root_dataset = self._graph_wrapper.create_relative_node(
            identifier="./", a="schema:Dataset"
        )

        self._graph_wrapper.create_relative_node(
            identifier="ro-crate-metadata.json",
            a="schema:CreativeWork",
            properties={
                "about": root_dataset,
            },
        )

        for identifier, properties in self._blueprint.body.items():
            a = properties.get("$type")
            label = properties.get("$label")
            properties = {
                k: v for k, v in properties.items() if not k.startswith("$")
            }

            if "://" in identifier:
                self._graph_wrapper.create_iri_node(
                    identifier=identifier,
                    a=a,
                    label=label,
                    properties=properties,
                )
            else:  # TODO identifiers like "<my_relative_id>" will give an error when created as a relative node # noqa: E501
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

        if getattr(self._blueprint, "reason", None):
            self._apply_reasoning()

        self.graph = self._graph_wrapper.unwrap()

    def _apply_reasoning(self):
        reason_cfg = self._blueprint.reason
        if not reason_cfg:
            return

        if isinstance(reason_cfg, dict):
            sources = (
                reason_cfg.get("source")
                or reason_cfg.get("sources")
                or []
            )
            queries = (
                reason_cfg.get("query")
                or reason_cfg.get("queries")
                or []
            )
        elif isinstance(reason_cfg, (list, tuple)):
            sources = []
            queries = list(reason_cfg)
        else:
            sources = []
            queries = [reason_cfg]

        prefixes = {
            str(k): str(v)
            for k, v in getattr(self._blueprint, "prefix", {}).items()
        }

        input_path = self.rocrate_path or Path.cwd()
        reasoner = Reasoner(
            sources=sources,
            queries=queries,
            prefixes=prefixes,
            base="urn:rocreator:",
            input_path=input_path,
        )

        current_graph = self._graph_wrapper.unwrap()
        reasoned_graph = reasoner.reason(base_graph=current_graph)
        current_graph += reasoned_graph
