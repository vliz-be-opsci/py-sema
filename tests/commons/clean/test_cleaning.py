import json
from typing import Callable

from conftest import (
    TEST_INPUT_FOLDER,
    format_from_extension,
    loadfilegraph,
    log,
)
from rdflib import BNode, Graph, Literal, Namespace, URIRef

from sema.commons.clean import (  # the public __init__ parts
    Level,
    check_valid_uri,
    check_valid_url,
    check_valid_urn,
    clean_graph,
    clean_uri_str,
)
from sema.commons.clean.clean import (  # the non public parts under tested too
    NAMED_CLEAN_FUNCTIONS,
    build_clean_chain,
    clean_uri_node,
    normalise_scheme_node,
    normalise_scheme_str,
    reparse,
)

SCHEMA: Namespace = Namespace("https://schema.org/")
RDF: Namespace = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
EX: Namespace = Namespace("http://example.org/")


def test_compare_bnodes_ttl_jsonld():
    log.info("test_compare_bnodes_ttl_jsonld()")
    localnames = ["b0", "b1", "x9"]
    tst_content = dict()

    ttl = "\n".join(f"_:{ln} a <{EX}MyType> ." for ln in localnames)
    tst_content["turtle"] = ttl

    js = ",\n  ".join(
        f'{{"@id": "_:{ln}", "@type": "{EX.MyType}" }}' for ln in localnames
    )
    tst_content["json-ld"] = f"[\n  {js} ]"

    for fmt, cntnt in tst_content.items():
        log.debug(f"{fmt=}, cntnt ->\n{cntnt}\n<-")
        g = reparse(Graph().parse(data=cntnt, format=fmt))

        items = list(g.subjects(predicate=RDF.type, object=EX.MyType))
        assert len(items) == 3
        for i, item in enumerate(items):
            log.debug(f". found {i} -> {type(item).__name__} {item.n3()=} ")
            assert isinstance(item, BNode)
            assert (
                item.n3()[2:] not in localnames
            ), f"problem with format {fmt}"


def test_compare_bnodes_ttl_jsonld_files():
    """testing how rdlib jsonld parser is handling the "@id": "_:n1" in json
    see bug in rdflib: https://github.com/RDFLib/rdflib/issues/2760
    """
    log.info("test_compare_bnodes_ttl_jsonld_files()")
    for fname in ("issue-bnodes.jsonld", "issue-bnodes.ttl"):
        localnames = [
            "b0",
            "b1",
            "x9",
        ]  # known local id to be used in these files
        log.debug(f"testing ${fname=}")
        fpath = TEST_INPUT_FOLDER / fname

        g: Graph = reparse(
            loadfilegraph(fpath, format=format_from_extension(fpath))
        )
        persons = g.subjects(predicate=RDF.type, object=SCHEMA.Person)
        for i, p in enumerate(persons):
            log.debug(f". found {i} -> {type(p).__name__} {p.n3()=} ")
            assert isinstance(p, BNode)
            assert (
                p.n3()[2:] not in localnames
            ), "local id {p.n3()} used in file should have been replaced"


def test_clean_uri_str():
    log.info("test_clean_uri_str()")
    bad_uri: str = "https://example.org/with-[square]-brackets"
    assert not check_valid_uri(bad_uri)

    force_safe = clean_uri_str(bad_uri)
    force_safe_again = clean_uri_str(force_safe)

    smart_safe = clean_uri_str(bad_uri, smart=True)
    smart_safe_again = clean_uri_str(smart_safe, smart=True)

    assert force_safe == smart_safe
    assert (
        force_safe != force_safe_again
    ), "forced cleaning should not be idempotent"
    assert (
        smart_safe == smart_safe_again
    ), "smart cleaning should be idempotent"


def test_check_ur_inl_str():
    badany = (
        "",
        "urn",
        "urn:",
        "urn:x:abc",
        "urn:xy:",
        "http://localhost:1234/something",  # valid url need domain
    )
    goodurn = (
        "urn:xy:ab",
        "urn:urn:urn",
    )
    goodurl = (
        "https://example.org/path.ext?pk=v#fragment",
        "http://localhost.localdomain:8080/DOC1.ttl",
    )

    for ba in badany:
        assert not check_valid_urn(ba)
        assert not check_valid_url(ba)
        assert not check_valid_uri(ba)

    for gn in goodurn:
        assert check_valid_urn(gn)
        assert not check_valid_url(gn)
        assert check_valid_uri(gn)

    for gl in goodurl:
        assert not check_valid_urn(gl)
        assert check_valid_url(gl)
        assert check_valid_uri(gl)


def test_clean_uri_node():
    log.info("test_clean_uri_node()")
    bad_uri: str = "https://example.org/with-[square]-brackets"
    bad_ref_node: URIRef = URIRef(bad_uri)
    blank_node: BNode = BNode()
    literal_node: Literal = Literal(bad_uri, datatype="xsd:string")

    good_ref_node = clean_uri_node(bad_ref_node)
    assert bad_ref_node != good_ref_node
    assert not check_valid_uri(str(bad_ref_node))
    assert check_valid_uri(str(good_ref_node))

    assert blank_node == clean_uri_node(blank_node)
    assert literal_node == clean_uri_node(literal_node)


def test_normalise_scheme_node():
    log.info("test_normalise_scheme_node()")
    http_uri = "http://schema.org/test"
    https_uri = "https://schema.org/test"

    assert https_uri == normalise_scheme_str(http_uri)
    assert https_uri == normalise_scheme_str(https_uri)
    assert https_uri == str(normalise_scheme_node(URIRef(http_uri)))
    assert https_uri == str(normalise_scheme_node(URIRef(https_uri)))

    domain = "example.org"
    http_domain = f"http://{domain}/tester"
    https_domain = f"https://{domain}/tester"

    # in this domain we want to force http scheme
    assert http_domain == normalise_scheme_str(
        http_domain, domain=domain, to_scheme="http"
    )
    assert http_domain == normalise_scheme_str(
        https_domain, domain=domain, to_scheme="http"
    )
    assert http_domain == str(
        normalise_scheme_node(
            URIRef(http_domain), domain=domain, to_scheme="http"
        )
    )
    assert http_domain == str(
        normalise_scheme_node(
            URIRef(https_domain), domain=domain, to_scheme="http"
        )
    )

    no_domain = "none.ext"
    http_no_domain = f"http://{no_domain}/ignored"
    https_no_domain = f"https://{no_domain}/ignored"

    # and that should ignore uri from other domains
    assert http_no_domain == normalise_scheme_str(
        http_no_domain, domain=domain, to_scheme="http"
    )
    assert https_no_domain == normalise_scheme_str(
        https_no_domain, domain=domain, to_scheme="http"
    )
    assert http_no_domain == str(
        normalise_scheme_node(
            URIRef(http_no_domain), domain=domain, to_scheme="http"
        )
    )
    assert https_no_domain == str(
        normalise_scheme_node(
            URIRef(https_no_domain), domain=domain, to_scheme="http"
        )
    )


def test_clean_noop():
    log.info("test_clean_noop()")
    g: Graph = Graph().add(tuple((BNode(), RDF.type, SCHEMA.DataSet)))
    cg = clean_graph(g)  # when there is no cleaner-spec
    assert cg == g


def test_clean_custom_chain():
    log.info("test_clean_custom_chain()")
    count_triples: int = 0
    count_datasets: int = 0
    ds_uri: str = "http://schema.org/Dataset"

    def triple_count(trpl: tuple) -> tuple:
        nonlocal count_triples
        count_triples += 1  # testable side-effect
        return trpl  # do no real filtering

    triple_count.level = Level.Triple

    def dset_node_count(
        node: URIRef | BNode | Literal,
    ) -> URIRef | BNode | Literal:
        nonlocal count_datasets
        if str(node) == ds_uri:
            count_datasets += 1
        return node  # no real filtering

    dset_node_count.level = Level.Node

    def broken_filter(*args, **kwargs):
        raise RuntimeError("this will never happen")

    broken_filter.level = None  # not a valid level, so this will get skipped

    g: Graph = Graph()
    g.add(tuple((BNode(), RDF.type, URIRef(ds_uri))))
    g.add(tuple((URIRef(ds_uri), EX.test, Literal("just something here"))))
    cleaned = clean_graph(g, triple_count, dset_node_count, broken_filter)
    assert count_triples == len(g) == 2
    assert count_datasets == 2

    schema_uri_count = 0
    for t in cleaned.triples(tuple((None, None, None))):
        for n in t:
            if isinstance(n, URIRef):
                uri = str(n)
                if "schema.org" in uri:
                    schema_uri_count += 1
                    assert uri == ds_uri  # the only schema.org-uri used
    assert schema_uri_count == 2


def test_clean_chain():
    log.info("test_clean_chain()")
    count_triples: int = 0

    def custom_triple_filter(t: tuple) -> tuple:
        nonlocal count_triples
        count_triples += 1  # testable side-effect
        return t  # do no real filtering

    custom_triple_filter.level = Level.Triple

    specs = list(NAMED_CLEAN_FUNCTIONS.keys())  # apply all filters
    specs.append(custom_triple_filter)  # and our own

    cleaner: Callable = build_clean_chain(*specs)
    graph: Graph = Graph()  # the testgraph to clean

    bnode_name: str = "problematic_blanknode"
    json_data: str = json.dumps(
        {"@id": f"_:{bnode_name}", "@type": EX.TestType}
    )
    log.debug(f"parsing {json_data=}")
    graph.parse(data=json_data, format="json-ld")

    bad_schema_org_triple: tuple = tuple(
        (
            BNode(),
            URIRef("http://schema.org/one"),
            Literal("schema.org-clean-test"),
        )
    )
    graph.add(bad_schema_org_triple)

    bad_uri_triple = tuple(
        (
            BNode(),
            SCHEMA.downloadUrl,
            URIRef("http://example.org/here+comes/[badness]"),
        )
    )
    graph.add(bad_uri_triple)

    log.debug(f"cleaning:\n{graph.serialize(format='nt')}")
    cleaned = clean_graph(graph, cleaner)
    log.debug(f"cleaned to:\n{cleaned.serialize(format='nt')}")

    # assert all issues vanished
    count_bnodes: int = 0
    count_literals: int = 0
    count_uriref: int = 0
    count_other: int = 0
    for t in cleaned.triples(tuple((None, None, None))):
        for n in t:
            if isinstance(n, Literal):
                count_literals += 1
                continue
            # else
            if isinstance(n, BNode):
                count_bnodes += 1
                assert str(n) != bnode_name
                continue
            # else
            if isinstance(n, URIRef):
                count_uriref += 1
                uri = str(n)
                assert check_valid_uri(uri)
                if ("schema.org") in uri:
                    assert uri.startswith("https://")
                continue
            # else
            count_other += 1

    # assert all triples where visited
    expected_bnodes: int = 3
    expected_literals: int = 1
    expected_uriref = len(graph) * 3 - expected_bnodes - expected_literals
    expected_other: int = 0

    assert count_triples == len(graph)
    assert expected_bnodes == count_bnodes
    assert expected_literals == count_literals
    assert expected_uriref == count_uriref
    assert expected_other == count_other
