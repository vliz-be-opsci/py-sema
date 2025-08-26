import re
from rdflib import Graph, Namespace, Literal, URIRef

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
            assert not (namespace or (prefix is not None) or suffix), "{template} is mutually exclusive with {namespace, prefix, suffix}"
            self._namespace, self._prefix, self._suffix = self._parse(template)
            
        if (namespace or (prefix is not None) or suffix):
            assert not template, "{template} is mutually exclusive with {namespace, prefix, suffix}"
            self._suffix = suffix
            if namespace:
                assert prefix is None, "namespace is mutually exclusive with prefix"
                self._namespace = namespace
            if prefix is not None:
                assert not namespace, "prefix is mutually exclusive with namespace"
                self._prefix = prefix

        assert self._suffix, "suffix is undefined"

        if graph is not None:
            self._graph = graph
        else:
            self._graph = Graph()

        self._graph_namespaces = {
            k: Namespace(v) for k, v in self._graph.namespaces()
        }
        self.term = self._build()

    @staticmethod
    def _parse(t):
        if "://" in t:
            return None, None, t
        elif "\\" in t:
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

        # literal (or url)
        if self._prefix is None and (not self._namespace == "@base"):
            if re.match(r"[\"\'].*[\"\']\^\^xsd:string", self._suffix):
                return Literal(self._suffix[1:-13])
            elif "://" in self._suffix:
                return URIRef(self._suffix)
            else:
                return Literal(self._suffix)
        
        # uriref w/ base
        if self._namespace == "@base":
            if not self._graph.base:
                raise AssertionError("Graph needs base attribute when using base namespace to expand term")
            base = Namespace(self._graph.base)
            return getattr(base, self._suffix)
        
        # uriref w/ lookup
        assert self._prefix is not None, "_prefix must be defined in order to perform namespace lookup"
        return getattr(Namespace(self._lookup(self._prefix)), self._suffix)

    def _lookup(self, prefix):
        try:
            return self._graph_namespaces[prefix]
        except KeyError as e:
            raise RuntimeError(f"prefix `{prefix}` is undefined in the graph") from e
