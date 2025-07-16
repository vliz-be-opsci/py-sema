
from typing import Union, Iterable
from uuid import uuid4
from rdflib import Graph, Namespace, URIRef, BNode, Literal
from rdflib.namespace import NamespaceManager
from .graph_builder import GraphBuilder

class ObjectGraphMapper(GraphBuilder):
    def __init__(
            self,
            base_namespace: dict = {"nil": "urn:nil:"},
            defined_namespaces: dict = {},
            *args,
            **kwargs
        ):
        self.graph = Graph(*args, **kwargs, bind_namespaces="none")
        # self.namespace_manager = NamespaceManager(Graph(), bind_namespaces="none")
        self.base_namespace = base_namespace
        self.defined_namespaces = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#", # TODO check if overwritten
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#"
            **defined_namespaces
        }

        for namespace_prefix, namespace in self.defined_namespaces.items():
            assert namespace_prefix != "rdf", "rdf is a reserved namespace"
            assert namespace_prefix != "rdfs", "rdfs is a reserved namespace"
            assert str(namespace)[-1] in ("#", "/", ":")
            namespace = Namespace(namespace)
            if not self.ns:
                self.ns_prefix = namespace_prefix
                self.ns = namespace
                continue

            self._add_namespace(namespace_prefix, namespace)

        assert self.ns
    
    def create_inode(self, *args, **kwargs):
        return self.create_node(*args, **kwargs, kind="iri")

    def create_rnode(self, *args, **kwargs):
        return self.create_node(*args, **kwargs, kind="relative")

    def create_bnode(self, *args, **kwargs):
        return self.create_node(*args, **kwargs)
    
    def create_node(
            self,
            identifier: Union[URIRef, str] = None,
            a: Union[URIRef, str, list[Union[URIRef, str]]] = None,
            label: Union[str, list[str]] = None,
            property: dict[Union[URIRef, str], Union[URIRef, Literal, str, list]] = None,
            kind: bool = "blank",
            typed: bool = True,
        ) -> Union[URIRef, None]:
        """
        identifier: URIRef, str, or None. If None, a UUID will be generated.
        label: str, list of str, or None.
        property: dict ...
        a: URIRef, str, list of these, or None. "a" is shorthand for "type" in RDF terminology.
        kind: If "blank", the identifier will be a BNode (blank node). If "iri", the identifier will be a URIRef.
        typed: If True, a type declaration must be added to the node. Then, if a=None, the type declaration will be "urn:nil:Resource".
        """
        if not (a or label or property) and not typed:
            return None  # can't give you anything if you give me nothing

        if not identifier:
            if kind == "iri":
                identifier = f":{uuid4()}"
            else:
                identifier = str(uuid4())

        if kind == "iri":
            identifier = IRITemplate(identifier).expand(self)
        elif kind == "relative":
            identifier = URIRef(identifier)
        elif kind == "blank":
            identifier = BNode(identifier)
        else:
            raise AssertionError

        if not a and typed:
            a = "rdfs:Resource"

        self.update_node(identifier, a=a, label=label, property=property)

        return identifier

    def update_node(self, identifier, a=None, label=None, property=None):
        subject = identifier

        if a:
            a = self._listify(a)
            for _a in a:
                self.add((
                    subject,
                    IRITemplate("rdf:type").expand(self),
                    IRITemplate(_a).expand(self)
                ))

        if label:
            label = self._listify(label)
            for _label in label:
                self.add((
                    subject,
                    IRITemplate("rdfs:label").expand(self),
                    IRITemplate(_label).expand(self)
                ))

        if property:
            for predicate, object in property.items():
                if not object:
                    continue

                # make sure predicate (k) is expanded
                predicate = IRITemplate(predicate).expand(self)

                # make sure object (v) is expanded
                Array = (list, tuple)
                if not isinstance(v, Array):
                    object = IRITemplate(object).expand(self)
                    self.add((subject, predicate, object))

                # if v is an Array (list or tuple), make sure objects (i) within are expanded
                if isinstance(v, Array):
                    objects = object
                    for object in objects:
                        object = IRITemplate(object).expand(self)
                        self.add((identifier, predicate, object))


    # def serialize(self, *args, **kwargs, break_on_unused=False):
    #     unused = self._check_for_unused_namespaces()
    #     if break_on_unused and unused:
    #         raise AssertionError

    #     return super().serialize(*args, **kwargs)

    def _listify(self, x) -> Union[list, Iterable]:
        if isinstance(x, Iterable) and not isinstance(x, str):
            return x
        else:
            return [x]

    def __str__(self, format="text/turtle"):
        return self.serialize(format=format)

