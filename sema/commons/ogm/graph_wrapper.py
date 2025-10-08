from rdflib import Graph, URIRef, BNode, Literal
from rdflib.plugins.parsers.jsonld import Context
from uuid import uuid4
from .term_builder import TermBuilder

class GraphWrapper:
    def __init__(self, graph=None, base=None):
        self.graph: Graph = graph or Graph(base=base, bind_namespaces="none")
        self._listify = lambda x: x if isinstance(x, list) else [x]

    def set_jsonld_context(self, context) -> None:
        self.graph._jsonld_context = Context(context)
        self.graph._jsonld_context_repr = context  # Context.to_dict() doesn't preserve original representation

    def bind(self, prefix, namespace) -> None:
        self.graph.bind(prefix, namespace)
    
    def update_node(
            self,
            identifier: URIRef,
            a: URIRef | str | list[URIRef | str] = None,
            label: str | list[str] = None,
            properties: dict[URIRef | str, URIRef | Literal | str | list] = None,
        ) -> None:
        if not (a or label or properties):
            return  # nothing to do

        subject = identifier

        if a:
            a_templates = self._listify(a)
            for a_template in a_templates:
                self.graph.add((
                    subject,
                    TermBuilder("rdf:type", graph=self.graph).build(),
                    TermBuilder(a_template, graph=self.graph).build()
                ))

        if label:
            label_templates = self._listify(label)
            for label_template in label_templates:
                self.graph.add((
                    subject,
                    TermBuilder("rdfs:label", graph=self.graph).build(),
                    TermBuilder(label_template, graph=self.graph).build()
                ))

        if properties:
            for predicate_template, object_tmp in properties.items():
                predicate = TermBuilder(predicate_template, graph=self.graph).build()
                object_templates = self._listify(object_tmp)
                for object_template in object_templates:
                    object = TermBuilder(object_template, graph=self.graph).build()
                    self.graph.add((subject, predicate, object))

    def create_node(
            self,
            identifier: URIRef | str | None = None,
            a: URIRef | str | list[URIRef | str] | None = None,
            label: str | list[str] | None = None,
            properties: dict[URIRef | str, URIRef | Literal | str | list | None] | None = None,
            kind: str = "blank",
            typed: bool = True,
    ) -> URIRef | BNode:
        """
        identifier: URIRef, str, or None. If None, a UUID will be generated.
        a: URIRef, str, list of these, or None. "a" is shorthand for "type" in RDF terminology.
        kind: If "blank", the identifier will be a BNode (blank node). If "iri" or "relative", the identifier will be a URIRef.
        typed: If True, a type declaration must be added to the node. Then, if a=None, the type declaration will be "rdfs:Resource".
        """
        if kind == "iri":
            subject_template = identifier or f"<{uuid4()}>"
            subject = TermBuilder(template=subject_template, graph=self.graph).build()
        elif kind == "relative":
            subject_template = identifier or str(uuid4())
            subject = URIRef(subject_template)
        elif kind == "blank":
            subject_template = identifier or str(uuid4())
            subject = BNode(subject_template)
        else:
            raise AssertionError(f"invalid kind of node: {kind}")

        if not a and typed:
            a = "rdfs:Resource"

        self.update_node(identifier=subject, a=a, label=label, properties=properties)

        return subject

    def create_iri_node(self, *args, **kwargs) -> URIRef:
        return self.create_node(kind="iri", *args, **kwargs)

    def create_relative_node(self, *args, **kwargs) -> URIRef:  # TODO where is this method used?
        """
        relative to the document uri (i.e. not relative to the base uri)
        """
        return self.create_node(kind="relative", *args, **kwargs)
    
    def create_blank_node(self, *args, **kwargs) -> BNode:
        return self.create_node(kind="blank", *args, **kwargs)

    def unwrap(self) -> Graph:
        return self.graph
