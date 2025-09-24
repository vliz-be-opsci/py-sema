from rdflib import Graph, Literal, Namespace, URIRef
from sema.commons.ogm import TermBuilder

def test_term_builder_parse():
    assert TermBuilder._parse("<bar>") == {"namespace": "@base", "prefix": None, "suffix": "bar", "nop": None}
    assert TermBuilder._parse(":bar") == {"namespace": None, "prefix": "", "suffix": "bar", "nop": None}
    assert TermBuilder._parse("foo:bar") == {"namespace": None, "prefix": "foo", "suffix": "bar", "nop": None}
    assert TermBuilder._parse("bar") == {"namespace": None, "prefix": None, "suffix": None, "nop": "bar"}
    assert TermBuilder._parse("\\<bar\\>") == {"namespace": None, "prefix": None, "suffix": None, "nop": "<bar>"}
    assert TermBuilder._parse("\\:bar") == {"namespace": None, "prefix": None, "suffix": None, "nop": ":bar"}
    assert TermBuilder._parse("foo\\:bar") == {"namespace": None, "prefix": None, "suffix": None, "nop": "foo:bar"}
    assert TermBuilder._parse("http://foo.net/bar") == {"namespace": None, "prefix": None, "suffix": None, "nop": "http://foo.net/bar"}
    assert TermBuilder._parse('"http://foo.net/bar"^^xsd:string') == {"namespace": None, "prefix": None, "suffix": None, "nop": '"http://foo.net/bar"^^xsd:string'}

def test_term_builder():
    g = Graph(base="urn:base:")
    g.bind("", Namespace("urn:void:"))
    g.bind("foo", Namespace("urn:foo:"))

    # namespace + suffix
    assert TermBuilder(namespace="urn:nil:", suffix="bar").build() == URIRef("urn:nil:bar")
    assert TermBuilder(namespace="@base", suffix="bar", graph=g).build() == URIRef("urn:base:bar")
    assert TermBuilder("<bar>", graph=g).build() == URIRef("urn:base:bar")

    # prefix + suffix
    assert TermBuilder(prefix="", suffix="bar", graph=g).build() == URIRef("urn:void:bar")
    assert TermBuilder(":bar", graph=g).build() == URIRef("urn:void:bar")
    assert TermBuilder(prefix="foo", suffix="bar", graph=g).build() == URIRef("urn:foo:bar")
    assert TermBuilder("foo:bar", graph=g).build() == URIRef("urn:foo:bar")

    # nop
    assert TermBuilder(nop="bar").build() == Literal("bar")
    assert TermBuilder("bar").build() == Literal("bar")
    assert TermBuilder("\\<bar\\>").build() == Literal("<bar>")
    assert TermBuilder("\\:bar").build() == Literal(":bar")
    assert TermBuilder("foo\\:bar").build() == Literal("foo:bar")
    assert TermBuilder("http://foo.net/bar").build() == URIRef("http://foo.net/bar")
    assert TermBuilder('"http://foo.net/bar"^^xsd:string').build() == Literal("http://foo.net/bar")
