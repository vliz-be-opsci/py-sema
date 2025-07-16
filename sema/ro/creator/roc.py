from pathlib import Path
import re
import yaml
from types import SimpleNamespace
from sema.commons.rdf_ogm import ObjectGraphMapper

class Roc(ObjectGraphMapper):
    def __init__(self, rocrate_path: str = "./", blueprint_path = None, namespaces = {}, *args, **kwargs):
        self.blueprint = SimpleNamespace()
        self.context = SimpleNamespace(version="1.0")
        self.graph = SimpleNamespace(
            ignore = ["^.rocrateignore$"],
            include = []
        )
        self.metadata = {}
        self._parse_rocrate_ignore(rocrate_path)
        self._parse_blueprint(blueprint_path)
        self._generate_default_metadata()
        self._generate_blueprint_metadata()
        super().__init__(
            namespaces={**namespaces, "rocrate": f"https://w3id.org/ro/crate/{self.context.version}/context/"},
            *args, **kwargs
        )
        self._generate_graph()

    def serialize(
            self,
            *args,
            format: str = "application/ld+json",
            indent=4,
            auto_compact=True,
            **kwargs
        ):
        for l, p in self.metadata.items():
            if l.startswith(":"):
                continue
            if ":" in l:
                ...
            self.create_node(label=l, property=p)
        return super().serialize(
            *args,
            format=format,
            indent=indent,
            auto_compact=auto_compact,
            **kwargs
        )

    def _parse_blueprint(self, blueprint_path: str):
        self.bp = yaml.safe_load(open(blueprint_path, "r")) if blueprint_path else {}
        version = self.bp.get(":context", {}).get("version", "1.0")
        self.rocrate_ignore.extend(self.bp.get(":blueprint").get("ignore", []))
        self.rocrate_include.extend(self.bp.get(":blueprint").get("include", []))

    def _parse_rocrate_ignore(self):
        rocrate_ignore_file = self.rocrate_path / ".rocrateignore"
        if rocrate_ignore_file.exists():
            with open(rocrate_ignore_file, "r") as f:
                return [line.strip() for line in f if line.strip() and not line.startswith("#")]
        self.rocrate_ignore.extend(self._parse_rocrate_ignore())
        return []

    def _generate_default_metadata(self):
        for p in self.rocrate_path.glob("**/*"):
            p = p.relative_to(self.rocrate_path).as_posix()
            if not any(re.search(pattern, p) for pattern in self.rocrate_ignore):
                self.metadata[p] = None

    def _generate_blueprint_metadata(self):
        for k, v in self.bp.get(":blueprint", {}).items():
            self.metadata[k] = v

    def _generate_graph(self):
        ...
