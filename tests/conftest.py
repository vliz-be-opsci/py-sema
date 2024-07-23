import logging
import logging.config
import os
import sys
from pathlib import Path
import shutil
from typing import Iterable, Optional, Callable
from uuid import uuid4

import pytest
import yaml
from dotenv import load_dotenv
from rdflib import BNode, Graph, Namespace, URIRef

from sema.commons.store import (
    RDFStore,
    create_rdf_store,
    GraphNameMapper,
    URIRDFStore,
    MemoryRDFStore,
)

TEST_INPUT_FOLDER = Path(__file__).parent / "./input"
TEST_FOLDER = Path(__file__).parent
TEST_SYNC_FOLDER = Path(__file__).parent / "__sync__"
DCT: Namespace = Namespace("http://purl.org/dc/terms/#")
DCT_ABSTRACT: URIRef = DCT.abstract
SELECT_ALL_SPO = "SELECT ?s ?p ?o WHERE { ?s ?p ?o . }"


log = logging.getLogger("tests")


def enable_test_logging():
    load_dotenv()
    if "PYTEST_LOGCONF" in os.environ:
        logconf = os.environ["PYTEST_LOGCONF"]
        try:
            with open(logconf, "r") as yml_logconf:
                logging.config.dictConfig(
                    yaml.load(yml_logconf, Loader=yaml.SafeLoader)
                )
            log.info(f"Logging enabled according to config in {logconf}")
        except Exception:
            print(f"error while tryring to load {logconf=}")
            # and then silently ignore..


def run_single_test(testfile):
    enable_test_logging()
    log.info(
        f"Running tests in {testfile} "
        + "with -v(erbose) and -s(no stdout capturing) "
        + "and logging to stdout, "
        + "level controlled by env var ${PYTEST_LOGCONF}"
    )
    sys.exit(pytest.main(["-v", "-s", testfile]))


enable_test_logging()  # note that this includes loading .env into os.getenv


def format_from_extension(fpath: Path):
    sfx = fpath.suffix
    sfmap = {".ttl": "turtle", ".jsonld": "json-ld"}
    return sfmap[sfx]


def assert_file_ingest(
    rdf_store: RDFStore,
    fpath: Path,
    sparql_test: str = None,
    expected_count: int = None,
):
    assert fpath.exists(), (
        "can not test insertion of " f"non-existent file {fpath=}"
    )

    ns = f"urn:test:{fpath.stem}"

    rdf_store_type = type(rdf_store).__name__
    log.debug(f"{rdf_store_type} :: testing ingest of {fpath=} into {ns=}")

    # clear it to avoid effects from previous tests
    log.debug(f"{rdf_store_type} :: dropping {ns=} to set clear base")
    rdf_store.drop_graph(ns)

    # read file into graph
    fg = Graph().parse(str(fpath), format=format_from_extension(fpath))
    num_triples = len(fg)
    log.debug(f"{rdf_store_type} :: inserting {num_triples=} into {ns=}")
    rdf_store.insert(fg, ns)

    # then verify
    if sparql_test is None:
        # default test is to just retrieve all triples we inserted
        sparql_test = SELECT_ALL_SPO
        expected_count = num_triples

    result = rdf_store.select(sparql_test, ns)
    assert len(result) == expected_count, (
        f"{rdf_store_type} :: "
        f"test after insert of {fpath=} into {ns=} "
        f"did not yield {expected_count=}"
    )

    return fg, ns, result


@pytest.fixture(scope="session")
def quicktest() -> bool:
    """bool setting indicating to skip lengthy tests
    setting driven by setting env variable "QUICKTEST" to anything but 0 or ""
    """
    return bool(os.getenv("QUICKTEST", 0))


@pytest.fixture()
def base() -> str:
    return f"urn:test-sync:{uuid4()}:"


@pytest.fixture()
def nmapper(base: str) -> GraphNameMapper:
    return GraphNameMapper(base=base)


@pytest.fixture(scope="function")  # a fresh folder per store for each test
def syncfolders(store_builds) -> Iterable[Path]:
    mainpath = TEST_SYNC_FOLDER
    syncpathperstore = list()
    for n, store_build in enumerate(store_builds):
        rdf_store_type: str = store_build.store_type.__name__
        syncpathname: str = f"sync-{n+1:02d}-{rdf_store_type}"
        syncpath: Path = mainpath / syncpathname
        shutil.rmtree(str(syncpath), ignore_errors=True)  # force remove it
        syncpath.mkdir(parents=True, exist_ok=True)  # create it afresh
        syncpathperstore.append(syncpath)
    return syncpathperstore


@pytest.fixture(scope="session")
def _mem_store_build():
    def fn(*, cleaner: Callable = None, mapper: GraphNameMapper = None):
        return MemoryRDFStore(cleaner=cleaner, mapper=mapper)

    fn.store_type = MemoryRDFStore
    fn.store_info = ()
    return fn


@pytest.fixture(scope="session")
def _uri_store_build():
    read_uri: str = os.getenv("TEST_SPARQL_READ_URI", None)
    write_uri: str = os.getenv("TEST_SPARQL_WRITE_URI", read_uri)
    if read_uri is None or write_uri is None:
        return None
    # else

    def fn(*, cleaner: Callable = None, mapper: GraphNameMapper = None):
        return URIRDFStore(read_uri, write_uri, cleaner=cleaner, mapper=mapper)

    fn.store_type = URIRDFStore
    fn.store_info = tuple((read_uri, write_uri))
    return fn


@pytest.fixture(scope="session")
def store_builds(_mem_store_build, _uri_store_build):
    return tuple(
        storeinfo
        for storeinfo in (_mem_store_build, _uri_store_build)
        if storeinfo is not None
    )


@pytest.fixture()
def rdf_stores(store_builds, nmapper):
    return [storebuild(mapper=nmapper) for storebuild in store_builds]


@pytest.fixture()
def _mem_rdf_store(_mem_store_build, nmapper: GraphNameMapper) -> RDFStore:
    """in memory store
    uses simple dict of Graph
    """
    log.debug("creating in memory rdf store")
    return _mem_store_build(mapper=nmapper)


@pytest.fixture()
def _uri_rdf_store(_uri_store_build, nmapper: GraphNameMapper) -> RDFStore:
    """proxy to available graphdb store
    But only if environment variables are set and service is available
    else None (which will result in trimming it from rdf_stores fixture)
    """
    if _uri_store_build is None:
        return None
    # else
    return _uri_store_build(mapper=nmapper)


def loadfilegraph(fname, format="json-ld"):
    graph = Graph()
    graph.parse(fname, format=format)
    return graph


@pytest.fixture()
def sample_file_graph():
    """graph loaded from specific input file
    in casu: tests/input/3293.jsonld
    """
    return loadfilegraph(str(TEST_INPUT_FOLDER / "3293.jsonld"))


def make_sample_graph(
    items: Iterable,
    base: Optional[str] = "https://example.org/",
    bnode_subjects: Optional[bool] = False,
) -> Graph:
    """makes a small graph for testing purposes
    the graph is build up of triples that follow the
    pattern {base}{part}-{item}
    where:
     - base is optionally provided as argument
     - item is iterated from the required items argument
     - part is built in iterated over ("subject", "predicate", "object")

    :param items: list of 'items' to be inserted in the uri
    :type items: Iterable, note that all members of it will simply be
      str()-ified into the uri building
    :param base: (optional) baseuri to apply into the pattern
    :type base: str
    :param bnode_subjects: indicating that the subject
    :type bnode_subjects: bool
    :return: the graph
    :rtype
    """

    def replace_with_bnode(part):
        return bool(bnode_subjects and part == "subject")

    g = Graph()
    for item in items:
        triple = tuple(
            (
                URIRef(f"{base}{part}-{item}")
                if not replace_with_bnode(part)
                else BNode()
            )
            for part in ["subject", "predicate", "object"]
        )
        g.add(triple)
    return g


@pytest.fixture()
def example_graphs():
    return [make_sample_graph([i]) for i in range(10)]
