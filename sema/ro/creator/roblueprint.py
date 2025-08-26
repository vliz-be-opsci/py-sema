from copy import deepcopy
from sema.commons.ogm import GraphBlueprint
from sema.commons.glob import getMatchingGlobPaths

class ROBlueprint(GraphBlueprint):
    def __init__(
            self,
            *args,
            body: dict = None,
            nested_datasets=False,
            glob_root=None,
            glob_rnode=False,
            glob_walk=False,
            glob_ignore: list[str] | str = [],
            version="latest",
            context=None,
            **kwargs
        ):
        super().__init__(*args, **kwargs)

        context_uris = {
            "latest": "https://w3id.org/ro/crate/1.2/context",
            "1.2": "https://w3id.org/ro/crate/1.2/context",
        }

        self.version = version
        if not context:
            self.context = context_uris[version]
        else:
            self.context = context
        
        self.body = body or {}
        self.nested_datasets = nested_datasets
        self.implicit_body = {k: v for k, v in self.body.items() if "*" in k}
        self.explicit_body = {k: v for k, v in self.body.items() if not ("*" in k)}
        self.glob_root = glob_root
        self.glob_ignore = glob_ignore
        if glob_walk: self.implicit_body["**/*"] = {}
        if glob_walk or glob_rnode: self._expand_glob()
    
    def _expand_glob(self):
        assert self.glob_root, "glob_root must be set to expand glob patterns"
        self.body = {}
        for glob_pattern, property in self.implicit_body.items():
            paths = getMatchingGlobPaths(
                root=self.glob_root,
                includes=glob_pattern,
                excludes=self.glob_ignore,
            )
            for path in paths:
                if (self.glob_root / path).is_file():
                    if not property.get("$type"):
                        property["$type"] = "File"
                    self.body[str(path)] = deepcopy(property)
                else:
                    if not property.get("$type"):
                        property["$type"] = "Dataset"

        for identifier, property in self.explicit_body.items():
            if identifier in self.body:
                self.body[identifier].update(property)
            else:
                self.body[identifier] = property
