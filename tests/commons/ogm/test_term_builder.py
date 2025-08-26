from rdflib import Graph, Literal, Namespace, URIRef
from sema.commons.ogm import TermBuilder

def test_term_builder_parse():
    assert TermBuilder._parse("bar") == (None, None, "bar")  # literal
    assert TermBuilder._parse("<bar>") == ("@base", None, "bar")  # uriref w/ base
    assert TermBuilder._parse("\\<bar\\>") == (None, None, "<bar>")  # literal
    assert TermBuilder._parse(":bar") == (None, "", "bar")  # uriref w/ lookup
    assert TermBuilder._parse("\\:bar") == (None, None, ":bar")  # literal
    assert TermBuilder._parse("foo:bar") == (None, "foo", "bar")  # uriref w/ lookup
    assert TermBuilder._parse("foo\\:bar") == (None, None, "foo:bar")  # literal

def test_term_builder():
    # direct application of namespace
    assert TermBuilder(namespace="urn:nil:", suffix="bar").term == URIRef("urn:nil:bar")

    # literal
    assert TermBuilder(suffix="bar").term == Literal("bar")
    assert TermBuilder("bar").term == Literal("bar")
    assert TermBuilder("\\<bar\\>").term == Literal("<bar>")
    assert TermBuilder("\\:bar").term == Literal(":bar")
    assert TermBuilder("foo\\:bar").term == Literal("foo:bar")

    # uriref w/ base
    g = Graph(base="urn:base:")
    g.bind("", Namespace("urn::"))
    g.bind("foo", Namespace("urn:foo:"))

    assert TermBuilder(namespace="@base", suffix="bar", graph=g).term == URIRef("urn:base:bar")
    assert TermBuilder("<bar>", graph=g).term == URIRef("urn:base:bar")

    # uriref w/ lookup
    assert TermBuilder(prefix="", suffix="bar", graph=g).term == URIRef("urn::bar")
    assert TermBuilder(":bar", graph=g).term == URIRef("urn::bar")

    assert TermBuilder(prefix="foo", suffix="bar", graph=g).term == URIRef("urn:foo:bar")
    assert TermBuilder("foo:bar", graph=g).term == URIRef("urn:foo:bar")
