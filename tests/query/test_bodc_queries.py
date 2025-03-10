from const import BODC_ENDPOINT, FAKE_DUMP_FILE, P06_DUMP_FILE

from sema.query import (
    DEFAULT_TEMPLATES_FOLDER,
    DefaultSparqlBuilder,
    GraphSource,
    QueryResult,
)

j2sqb = DefaultSparqlBuilder(DEFAULT_TEMPLATES_FOLDER)


def test_bodc_listing_published_P06():
    nerc_server: GraphSource = GraphSource.build(BODC_ENDPOINT)
    qry: str = j2sqb.build_syntax("bodc-listing.sparql", cc="P06")

    result: QueryResult = nerc_server.query(sparql=qry)
    assert result is not None, "there should be a result"
    assert len(result) > 0, "the result should not be empty"


def test_bodc_listing_knowndump_P06():
    ttl_dump = P06_DUMP_FILE
    assert (
        ttl_dump.exists()
    ), f"need input file {str(ttl_dump)} for test to work"
    in_memory: GraphSource = GraphSource.build(str(ttl_dump))
    qry: str = j2sqb.build_syntax("bodc-listing.sparql", cc="P06")

    result: QueryResult = in_memory.query(sparql=qry)
    assert result is not None, "there should be a result"
    assert len(result) == 395, "the known dated dump had exactly 395 members"


def test_bodc_listing_fakedump():
    ttl_dump = FAKE_DUMP_FILE
    assert (
        ttl_dump.exists()
    ), f"need input file {str(ttl_dump)} for test to work"
    in_memory: GraphSource = GraphSource.build(str(ttl_dump))
    qry: str = j2sqb.build_syntax("bodc-listing.sparql", cc="fake")

    result: QueryResult = in_memory.query(sparql=qry)
    assert result is not None, "there should be a result"
    assert len(result) == 3, "the known fake dump has exactly 3 members"
