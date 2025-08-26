import yaml
from pathlib import Path
from sema.commons.ogm import ObjectGraphMapper
from sema.commons.yml import LoaderBuilder
from .roblueprint import ROBlueprint
from typing import override

# log = logging.getLogger(__name__) # TODO implement logging

class ROCreator(ObjectGraphMapper):
    @override
    def __init__(self,
            blueprint_path,
            *args,
            blueprint_env={},
            rocrate_path=None,
            force=True,
            **kwargs
        ):
        super().__init__(*args, blueprint_path=blueprint_path, **kwargs)
        self.blueprint_env = blueprint_env
        self.rocrate_path = Path(rocrate_path) if rocrate_path else None
        self.force = force
    
    @override
    def _parse_blueprint(self):
        loader = LoaderBuilder().to_resolve(self.blueprint_env).build()
        with open(self.blueprint_path, "r", encoding="utf-8") as file:
            data = yaml.load(file, Loader=loader)
        head, body = self._split_blueprint(data)
        self.blueprint = ROBlueprint(body=body, glob_root=self.rocrate_path, **head)
        self._blueprint_parsed = True


    def _map(self):
        if not self._blueprint_parsed: self._parse_blueprint()
        root_dataset = self.create_rnode(identifier="./", a="Dataset")
        self.create_rnode(
            identifier="ro-crate-metadata.json",
            a="CreativeWork",
            property={
                "about": root_dataset,
            }
        )
        for identifier, property in self.blueprint.body.items():
            type = property.get("$type")
            if type: property.pop("$type")

            label = property.get("$label")
            if label: property.pop("$label")

            if "://" in identifier:
                self.create_inode(
                    identifier=identifier,
                    a=type,
                    label=label,
                    property=property
                )
            else:
                self.create_rnode(
                    identifier=identifier,
                    a=type,
                    label=label,
                    property=property
                )
                assert not self.blueprint.nested_datasets, "nested datasets are not yet supported" # TODO support nested datasets
                if type == "File":
                    self.update_node(
                        identifier=root_dataset,
                        property={"hasPart": identifier}
                    )

        self._mapped = True

    @override
    def __str__(self):
        if not self._mapped: self._map()
        return self.graph_builder.__str__(
            format="application/ld+json",
            auto_compact=True,
            indent=4,
            context=self.blueprint.context,
        )

    @override
    def serialize(self, *args, rocrate_file_name = None, contextless=False, **kwargs):
        assert self.rocrate_path, "rocrate_path must be defined in order to serialize"

        destination = self.rocrate_path / (rocrate_file_name or "ro-crate-metadata.json")
        if destination.exists() and not self.force:
            # print(f"File {destination} already exists. Use --force or force=True to overwrite.") # TODO implement via logging
            return
        
        if contextless:

            raise NotImplementedError
            
            # TODO implement contextless serialization (look into GraphBuilder.graph.__init__)
            # return super().serialize(
            #     *args,
            #     destination=destination,
            #     **kwargs
            # )

        else:
            # TODO check for usage of out-of-context terms

            if not self._mapped: self._map()
            
            return super().serialize(
                *args,
                destination=destination,
                format="application/ld+json",
                auto_compact=True,
                indent=4,
                context=self.blueprint.context,
                **kwargs
            )

    def process(self, *args, **kwargs):
        self.serialize(*args, **kwargs)
