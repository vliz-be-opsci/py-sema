"""
LabeledPropertyGraph extends rdflib.Graph



```
from labeled_property_graph import LabeledPropertyGraph

lpg = LabeledPropertyGraph()
```



# Creating nodes
```
lpg.create_node()
```

```
lpg.create_node(blank=False)
```

# Updating nodes
```
node_ref = lpg.create_node()
```

```
lpg.update_node(node_ref)
```

# Configuring namespaces

:xyz -> uri(mew2:xyz)
abc:xyz -> uri(abc:xyz)
xyz -> lit(xyz)
abc\:xyz -> lit(abc:xyz)

None -> bnode(_:uuid) IF kind=blank
None -> uri(:uuid) IF kind=iri
None -> uri(uuid) IF kind=relative

inode -> identifier is an IRI
rnode -> identifier is a relative IRI
bnode -> identifier is a blank node
"""
from rdflib import Graph, Literal, Namespace, URIRef
from sema.commons.rdf_ogm import GraphBuilder, TermBuilder

def test_term_builder_parse():
    assert TermBuilder._parse("bar") == (None, None, "bar") # literal
    assert TermBuilder._parse("<bar>") == ("@base", None, "bar") # uriref w/ base
    assert TermBuilder._parse(":bar") == (None, "", "bar") # uriref w/ lookup
    assert TermBuilder._parse("foo:bar") == (None, "foo", "bar") # uriref w/ lookup
    assert TermBuilder._parse("foo\:bar") == (None, None, "foo:bar") # literal

def test_term_builder():
    assert TermBuilder(namespace="urn:foo:", prefix="", suffix="bar").term == URIRef("urn:foo:bar")
    assert TermBuilder("bar").term == Literal("bar")
    assert TermBuilder(suffix="bar").term == Literal("bar")
    assert TermBuilder("\<bar\>").term == Literal("<bar>")
    assert TermBuilder("\:bar").term == Literal(":bar")
    assert TermBuilder("foo\:bar").term == Literal("foo:bar")
    # assert TermBuilder("foo:bar").term == URIRef("urn:foo:bar")
    # assert TermBuilder(prefix="foo", suffix="bar").term == URIRef("urn:foo:bar")







    # g = Graph(base="urn:base:")
    # g.bind("", Namespace("urn::"))
    # g.bind("foo", Namespace("urn:foo:"))

    # assert TermBuilder("<bar>", graph=g).term == URIRef("urn:base:bar")
    # assert TermBuilder(namespace="@base", suffix="bar", graph=g).term == URIRef("urn:base:bar")

    # assert TermBuilder(":bar", graph=g).term == URIRef("urn::bar")
    # assert TermBuilder(prefix="", suffix="bar", graph=g).term == URIRef("urn::bar")

    # assert TermBuilder("foo:bar", graph=g).term == URIRef("urn:foo:bar")
    # assert TermBuilder(prefix="foo", suffix="bar", graph=g).term == URIRef("urn:foo:bar")



def test_graph_builder():
    # lpg = LabeledPropertyGraph()
    # lpg.create_inode()
    # lpg.create_inode("bar")
    # lpg.create_rnode()
    # lpg.create_rnode("bar")
    # lpg.create_bnode()
    # lpg.create_bnode("bar")
    # lpg.serialize("./test/data-output/lpg.json", format="application/ld+json", indent=4, auto_compact=True) # compacted and flattened json-ld



    # lpg.create_node(property={"foaf:nick": "hello"}, typed=False)

    # lpg.create_node(label="my_label0")
    # lpg.create_node(label="my_label1")
    # lpg.create_node()
    # lpg.create_unode()


    # print(lpg)
    # print("---")

    # identifier = lpg.create_node(force_type_declaration=False)
    # assert not identifier

    # lpg.create_node(label="my_label", force_type_declaration=False)
    # print(lpg)
    # print("---")

    # lpg.create_node(property={"my_key": "my_value"}, force_type_declaration=False)
    # print(lpg)
    # print("---")

    # lpg.create_node(a="MyType", force_type_declaration=False)
    # print(lpg)
    # print("---")

    # lpg.create_node()
    # print(lpg)
    # print("---")

    # lpg.create_node(label="my_label2")
    # print(lpg)
    # print("---")

    # lpg.create_node(property={"my_key2": "my_value2"})
    # print(lpg)
    # print("---")

    # lpg.create_node(a="MyType2")
    # print(lpg)
    # print("---")

    # node_uri = lpg.create_node(label="my_incomplete_node")
    # print(lpg)
    # print("---")

    # lpg.update_node(
    #     identifier=node_uri,
    #     a=["MoreTypes1", "MoreTypes2", "MoreTypes3"],
    #     label=["more_labels1", "more_labels2", "more_labels3"],
    #     property={
    #         "my_example": "my_value",
    #         "my_other_example": ["my_other_value", "my_other_value2"],
    #     },
    # )
    # print(lpg)
    # print("---")

    # node_uri2 = lpg.create_node(label="my_other_incomplete_node", force_type_declaration=False)
    # print(lpg)
    # print("---")

    # lpg.update_node(
    #     identifier=node_uri2,
    #     a=["MoreTypes1", "MoreTypes2", "MoreTypes3"],
    #     label=["more_labels1", "more_labels2", "more_labels3"],
    #     property={
    #         "my_example": "my_value",
    #         "my_other_example": ["my_other_value", "my_other_value2"],
    #     },
    # )
    # print(lpg)

    # lpg.update_node(
    #     identifier=node_uri2,
    #     a="foaf:Person",
    # )

    # lpg.update_node(
    #     identifier=node_uri2,
    #     a="example:Entity",
    # )


    # bnode0 = lpg.create_node(blank=True)

    # print(bnode0)
    # print(type(bnode0))

    # lpg.create_node(
    #     property={
    #         "foaf:nick": bnode0
    #     },
    # )
    ...

if __name__ == "__main__":
    test_term_builder_parse()
    test_term_builder()
    test_graph_builder()