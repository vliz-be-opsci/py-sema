import logging
from pathlib import Path
from rdflib import Graph
from sema.commons.ogm import ObjectGraphMapper
from sema.ro.creator.robuilder import ROBuilder

logger = logging.getLogger(__name__)

class ROCreator(ObjectGraphMapper):
    def __init__(self,
            blueprint_path: Path | str,
            blueprint_env: dict | None = None,
            rocrate_path: Path | None = None,
            rocrate_metadata_name: str | None = None,
            force: bool = True,
        ):
        super().__init__()
        self.blueprint_path = Path(blueprint_path)
        self.blueprint_env = blueprint_env or {}
        self.rocrate_path = Path(rocrate_path) if rocrate_path else None
        self.rocrate_metadata_name = rocrate_metadata_name or "ro-crate-metadata.json"
        self.force = force

    def _map(self) -> Graph:
        return ROBuilder(
            blueprint=self.blueprint_path,
            blueprint_env=self.blueprint_env,
            rocrate_path=self.rocrate_path,
        ).build()

    def process(self, *args, **kwargs) -> None:
        destination = self.rocrate_path / self.rocrate_metadata_name
        if destination.exists() and not self.force:
            logger.warning(f"File {destination} already exists. Use --force or force=True to overwrite.")
            return
        self.serialize(
            destination,
            format="application/ld+json",
            *args,
            **kwargs
        )
