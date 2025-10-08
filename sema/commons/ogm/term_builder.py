import re
from rdflib import Graph, Namespace, Literal, URIRef

class TermBuilder:
    def __init__(
        self,
        template: str = None,
        namespace: str = None,
        prefix: str = None,
        suffix: str = None,
        nop: str = None,  # no operation
        graph: Graph = None,
    ):
        self._namespace = namespace
        self._prefix = prefix
        self._suffix = suffix
        self._nop = nop

        if template:
            self._template = self._parse(template)
            self._namespace = self._template["namespace"]
            self._prefix = self._template["prefix"]
            self._suffix = self._template["suffix"]
            self._nop = self._template["nop"]

        if self._namespace:  # namespace + suffix is a valid scenario
            assert self._suffix
            assert self._prefix is None
            assert self._nop is None

        if self._prefix is not None: # prefix + suffix is a valid scenario
            assert self._namespace is None
            assert self._suffix
            assert self._nop is None

        if self._nop: # nop is a valid scenario
            assert self._namespace is None
            assert self._prefix is None
            assert self._suffix is None

        if graph is not None:
            self._graph = graph
        else:
            self._graph = Graph() # TODO why not set bind_namespaces="none"?

        self._graph_namespaces = {k: v for k, v in self._graph.namespaces()} # TODO dict(self._graph.namespaces())?

        self.term = None

    @staticmethod
    def _parse(template: str):
        # nop
        if "://" in template:
            return {"namespace": None, "prefix": None, "suffix": None, "nop": template}
        if "\\" in template:
            template = template.replace("\\", "")
            return {"namespace": None, "prefix": None, "suffix": None, "nop": template}

        # namespace (@base) + suffix
        if template.startswith("<") and template.endswith(">"):
            template = template[1:-1]
            return {"namespace": "@base", "prefix": None, "suffix": template, "nop": None}

        # prefix + suffix
        if ":" in template:
            segments = template.split(":")
            assert len(segments) == 2, "Template can only have one colon"
            return {"namespace": None, "prefix": segments[0], "suffix": segments[1], "nop": None}

        # nop fallback
        return {"namespace": None, "prefix": None, "suffix": None, "nop": template}

    def _lookup(self, prefix):
        try:
            return self._graph_namespaces[prefix]
        except KeyError:
            raise AssertionError(f"prefix `{prefix}` is undefined in the graph")

    def _build(self):
        # namespace (@base) + suffix
        if self._namespace == "@base":
            assert self._graph.base, "Graph needs base attribute when using base namespace to expand term"
            return getattr(Namespace(self._graph.base), self._suffix)

        # namespace + suffix
        if self._namespace:
            return getattr(Namespace(self._namespace), self._suffix)

        # prefix + suffix
        if self._prefix is not None:
            return getattr(Namespace(self._lookup(self._prefix)), self._suffix)

        # nop
        if re.match(r"[\"\'].*[\"\']\^\^xsd:string", self._nop):
            return Literal(self._nop[1:-13])
        if "://" in self._nop:
            return URIRef(self._nop)
        if hasattr(self._graph, "_jsonld_context"):
            term = self._graph._jsonld_context.terms.get(self._nop, None)
            if term: return URIRef(getattr(term, 'id'))

        return Literal(self._nop)

    def build(self):
        self.term = self._build()
        assert self.term
        return self.term
