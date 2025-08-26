from typing import Union, Iterable
from uuid import uuid4
from rdflib import Graph, Namespace, URIRef, BNode, Literal
from .term_builder import TermBuilder

class GraphBuilder:
    def __init__(
            self,
            base_namespace: str = "urn:nil:",
            defined_namespaces: dict[str, str] = {},
            *args,
            **kwargs
        ):

        self.graph = Graph(
            *args,
            **kwargs,
            base=base_namespace,  # pyrefly: ignore
            bind_namespaces="none"  # pyrefly: ignore
        )

        redefined_namespaces: dict[str, str] = {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        }
        redefined_namespaces.update(defined_namespaces)

        for prefix, namespace in redefined_namespaces.items():
            assert namespace[-1] in ("#", "/", ":")
            self.graph.bind(prefix, Namespace(namespace))
    
    def create_node(
            self,
            identifier: URIRef | str | None = None,
            a: Union[URIRef, str, list[Union[URIRef, str]]] = None,
            label: Union[str, list[str]] = None,
            property: dict[Union[URIRef, str], Union[URIRef, Literal, str, list]] = None,
            kind: bool = "blank",
            typed: bool = True,
        ) -> Union[URIRef, None]:
        """
        # TODO update docstring
        identifier: URIRef, str, or None. If None, a UUID will be generated.
        label: str, list of str, or None.
        property: dict ...
        a: URIRef, str, list of these, or None. "a" is shorthand for "type" in RDF terminology.
        kind: If "blank", the identifier will be a BNode (blank node). If "iri", the identifier will be a URIRef.
        typed: If True, a type declaration must be added to the node. Then, if a=None, the type declaration will be "rdfs:Resource".
        """
        if not (a or label or property) and not typed:
            return None  # can't give you anything if you give me nothing

        if not identifier:
            if kind == "iri":
                identifier = f":{uuid4()}"
            else:
                identifier = str(uuid4())

        if kind == "iri":
            identifier = TermBuilder(template=identifier, graph=self.graph).term
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
                self.graph.add((
                    subject,
                    TermBuilder("rdf:type", graph=self.graph).term,
                    TermBuilder(_a, graph=self.graph).term
                ))

        if label:
            label = self._listify(label)
            for _label in label:
                self.graph.add((
                    subject,
                    TermBuilder("rdfs:label", graph=self.graph).term,
                    TermBuilder(_label, graph=self.graph).term
                ))

        if property:
            for predicate, object in property.items():
                if not object:
                    continue

                # make sure predicate (k) is expanded (TODO update comment)
                predicate = TermBuilder(predicate, graph=self.graph).term

                # make sure object (v) is expanded (TODO update comment)
                Array = (list, tuple)
                if not isinstance(object, Array):
                    object = TermBuilder(object, graph=self.graph).term
                    self.graph.add((subject, predicate, object))

                # if v is an Array (list or tuple), make sure objects (i) within are expanded (TODO update comment)
                if isinstance(object, Array):
                    objects = object
                    for object in objects:
                        object = TermBuilder(object, graph=self.graph).term
                        self.graph.add((identifier, predicate, object))

    @staticmethod
    def _listify(x) -> Union[list, Iterable]:
        if isinstance(x, Iterable) and not isinstance(x, str):
            return x
        else:
            return [x]

    def serialize(self, *args, **kwargs):
        return self.graph.serialize(*args, **kwargs)

    def __str__(self, *args, format="text/turtle", **kwargs):
        return self.graph.serialize(*args, format=format, **kwargs)

    def bind(self, prefix: str, namespace: str):
        self.graph.bind(prefix, Namespace(namespace))
