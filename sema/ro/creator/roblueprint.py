from copy import deepcopy
from sema.commons.ogm import GraphBlueprint
from sema.commons.glob import getMatchingGlobPaths

class ROBlueprint(GraphBlueprint):
    def __init__(
            self,
            body: dict = None,
            context=None,
            prefix=None,
            version="latest",
            nested_datasets=False,
            glob_root=None,
            glob_rnode=True,
            glob_walk=False,
            glob_ignore: list[str] | str = [],
            *args,
            **kwargs,
        ):
        super().__init__(
            body=body,
            context=context or {
                "latest": "https://w3id.org/ro/crate/1.2/context",
                "1.2": "https://w3id.org/ro/crate/1.2/context",
            }[version],
            prefix=prefix or {
                "schema": "http://schema.org/",
                "dc": "http://purl.org/dc/terms/",
            },
            *args,
            **kwargs
        )
        
        self.nested_datasets = nested_datasets
        self.implicit_body = {k: v for k, v in self.body.items() if "*" in k}
        self.explicit_body = {k: v for k, v in self.body.items() if not ("*" in k)}
        self.glob_root = glob_root
        self.glob_ignore = glob_ignore
        if glob_walk: self.implicit_body["**/*"] = {}
        if glob_walk or glob_rnode: self._expand_glob()

        assert not self.nested_datasets, "nested datasets are not yet supported" # TODO support nested datasets
    
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
        
        self.body = dict(sorted(self.body.items()))  # sort keys to make output deterministic
