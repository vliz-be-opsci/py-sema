from rdflib import Graph, Namespace, URIRef, Literal, BNode

class TermBuilder:
    def __init__(
        self,
        template: str = None,
        namespace: str = None,
        prefix: str = None,
        suffix: str = None,
        graph: Graph = None
    ):
        self._namespace, self._prefix, self._suffix = None, None, None

        if template:
            assert not (namespace or prefix or suffix), "{template} is mutually exclusive with {namespace, prefix, suffix}"
            self._namespace, self._prefix, self._suffix = self._parse(template)
            
        if (namespace or prefix or suffix):
            assert not template, "{template} is mutually exclusive with {namespace, prefix, suffix}"
            self._suffix = suffix
            if namespace:
                assert not prefix, "namespace is mutually exclusive with prefix"
                self._namespace = namespace
            if prefix:
                ...

        assert self._suffix, "suffix is undefined"
        self._graph = graph or Graph()
        self._graph_namespaces = {
            k: Namespace(v) for k, v in self._graph.namespaces()
        }
        self.term = self._build()

    @staticmethod
    def _parse(t):
        if "\\" in t:
            t = t.replace("\\", "")
            return None, None, t
        elif t.startswith("<") and t.endswith(">"):
            t = t[1:-1]
            return "@base", None, t
        elif ":" in t:
            segments = t.split(":")
            assert len(segments) == 2, "Template can only have one colon"
            return None, segments[0], segments[1]
        else:
            return None, None, t

    def _build(self):
        # namespace
        if self._namespace and (not self._namespace == "@base"):
            return getattr(Namespace(self._namespace), self._suffix)

        # literal
        if self._prefix is None and (not self._namespace == "@base"):
            return Literal(self._suffix)
        
        # uriref w/ base
        if self._namespace == "@base":
            if not self._graph.base:
                raise AssertionError("Graph needs base attribute when using base namespace to expand term")
            base = Namespace(graph.base)
            return getattr(base, self._suffix)
        
        # uriref w/ lookup
        assert self._prefix is not None # TODO check if this can happen
        return getattr(Namespace(self._lookup(self._prefix)), self._suffix)

    def _lookup(self, prefix):
        try:
            return self._graph_namespaces[prefix]
        except KeyError as e:
            raise RuntimeError("prefix is undefined in the graph") from e
