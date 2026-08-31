from copy import deepcopy
from functools import cache
from itertools import product

import networkx as nx

from sema.commons.glob import getMatchingGlobPaths
from sema.commons.ogm import GraphBlueprint


class ROBlueprint(GraphBlueprint):
    def __init__(
        self,
        body: dict = None,
        context=None,
        prefix=None,
        version="latest",
        nested_datasets=False,
        glob_root=None,
        glob_walk=False,
        glob_ignore: list[str] | str | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(
            body=body,
            context=context
            or {
                "latest": "https://w3id.org/ro/crate/1.2/context",
                "1.2": "https://w3id.org/ro/crate/1.2/context",
            }[version],
            prefix=prefix
            or {
                "schema": "http://schema.org/",
                "dc": "http://purl.org/dc/terms/",
            },
            *args,
            **kwargs,
        )

        self.nested_datasets = nested_datasets
        self.glob_root = glob_root
        self.glob_ignore = glob_ignore or []
        if glob_walk and (not "**/*" in self.body):
            self.body["**/*"] = {}
        self._expand_body()
        assert (
            not self.nested_datasets
        ), "nested datasets are not yet supported"  # TODO support nested datasets # noqa: E501

    @cache
    def _expand_glob(self, glob):
        fs = frozenset(
            getMatchingGlobPaths(
                root=self.glob_root,
                includes=glob,
                excludes=self.glob_ignore,
            )
        )

        if len(fs) == 0:
            raise ValueError(f"glob pattern {glob} did not match any files")

        return fs

    def _expand_body(self):
        assert self.glob_root, "glob_root must be set to expand glob patterns"
        globs = [
            k
            for k in self.body.keys()
            if not (k == "ro-crate-metadata.json" or k == "./" or "://" in k)
        ]

        # create a DAG of globs, pointing from more general to more specific
        dg = nx.DiGraph()
        dg.add_nodes_from(globs)
        dg.add_edges_from(
            [
                (x, y)
                for x, y in product(globs, globs)
                if x != y
                and self._expand_glob(y).issubset(self._expand_glob(x))
            ]
        )

        # flatten the DAG into a list of file paths,
        # sorted from more general to more specific
        expanded_body = {}
        for glob in nx.topological_sort(dg):
            paths = self._expand_glob(glob)
            for path in paths:
                p = path.as_posix()
                if not p in expanded_body:
                    expanded_body[path.as_posix()] = deepcopy(self.body[glob])
                else:
                    expanded_body[path.as_posix()].update(self.body[glob])

        # handle rocrate root and URIs
        for k, v in self.body.items():
            if k == "ro-crate-metadata.json" or k == "./" or "://" in k:
                expanded_body[k] = v

        self.body = dict(
            sorted(expanded_body.items())
        )  # sort keys to make output deterministic
