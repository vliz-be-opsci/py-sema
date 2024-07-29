from logging import getLogger
import os
import re
import shutil
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from typing import Callable, Dict, Iterable, Optional
from uuid import uuid4

import pytest
import requests
from dotenv import load_dotenv
from rdflib import BNode, Graph, Namespace, URIRef

from sema.commons.log import load_log_config
from sema.commons.store import (
    GraphNameMapper,
    MemoryRDFStore,
    RDFStore,
    URIRDFStore,
)
from sema.harvest.store import RDFStoreAccess

TEST_FOLDER = Path(__file__).parent
TEST_INPUT_FOLDER = TEST_FOLDER / "input"
TEST_OUTPUT_FOLDER = TEST_FOLDER / "output"
TEST_SYNC_FOLDER = TEST_FOLDER / "__sync__"

DCT: Namespace = Namespace("http://purl.org/dc/terms/#")
DCT_ABSTRACT: URIRef = DCT.abstract
SELECT_ALL_SPO = "SELECT ?s ?p ?o WHERE { ?s ?p ?o . }"

# TODO choose better name + apply all-caps for constants
TEST_Path: Path = TEST_FOLDER / "harvest" / "scenarios"

# TODO httpd usage should not be confined to harvest issues maybe?
# so maybe move to TEST_FOLDER / "httpd"  and have specific harvest-input under there?
HTTPD_ROOT: Path = TEST_Path / "input"
HTTPD_HOST: str = (
    # TODO test with localhost.localdomain
    "localhost"  # can be '' - maybe also try '0.0.0.0' to bind all
)
HTTPD_PORT: int = 8080
HTTPD_EXTENSION_MAP: Dict[str, str] = {
    ".txt": "text/plain",
    ".jsonld": "application/ld+json",
    ".ttl": "text/turtle",
}

log = getLogger("tests")


def enable_test_logging():
    load_dotenv()
    load_log_config(os.environ.get("PYTEST_LOGCONF", None))


enable_test_logging()  # note that this includes loading .env into os.getenv


# TODO maybe tests that use this should use sema.commons.fileformats in stead?
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


@pytest.fixture()
def outpath() -> Path:
    # note we clean the folder at the start
    # and keeping it at the end -- so the folder can be expected after test
    shutil.rmtree(str(TEST_OUTPUT_FOLDER), ignore_errors=True)  # always clean
    TEST_OUTPUT_FOLDER.mkdir(exist_ok=True, parents=True)  # and recreate
    return TEST_OUTPUT_FOLDER


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
        syncpathname: str = f"sync-{n + 1:02d}-{rdf_store_type}"
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


@pytest.fixture()
def decorated_rdf_stores(rdf_stores):
    return (RDFStoreAccess(rdf_store) for rdf_store in rdf_stores)


class TestRequestHandler(SimpleHTTPRequestHandler):
    def __init__(
        self, request, client_address, server, *args, **kwargs
    ) -> None:
        super().__init__(
            request,
            client_address,
            server,
            directory=str(HTTPD_ROOT.absolute()),
        )


TestRequestHandler.extensions_map = HTTPD_EXTENSION_MAP


@pytest.fixture(scope="session")
def _mem_store_info():
    return ()


@pytest.fixture(scope="session")
def _uri_store_info():
    read_uri: str = os.getenv("TEST_SPARQL_READ_URI", None)
    write_uri: str = os.getenv("TEST_SPARQL_WRITE_URI", read_uri)
    if read_uri is None or write_uri is None:
        return None
    # else
    return (read_uri, write_uri)


@pytest.fixture(scope="session")
def store_info_sets(_mem_store_info, _uri_store_info):
    return tuple(
        storeinfo
        for storeinfo in (_mem_store_info, _uri_store_info)
        if storeinfo is not None
    )


@pytest.fixture(scope="session")
def httpd_server():
    with HTTPServer((HTTPD_HOST, HTTPD_PORT), TestRequestHandler) as httpd:

        def httpd_serve():
            httpd.serve_forever()

        t = Thread(target=httpd_serve)
        t.daemon = True
        t.start()

        yield httpd
        httpd.shutdown()


@pytest.fixture(scope="session")
def httpd_server_base(httpd_server: HTTPServer) -> str:
    return f"http://{httpd_server.server_name}:{httpd_server.server_port}/"


@pytest.fixture(scope="session")
def all_extensions_testset():
    return {
        mime: f"{re.sub(r'[^0-9a-zA-Z]+', '-', mime)}.{ext}"
        for ext, mime in HTTPD_EXTENSION_MAP.items()
    }


# test if all objects can be retrieved
@pytest.mark.usefixtures("httpd_server_base", "all_extensions_testset")
def test_conf_fixturtes(httpd_server_base: str, all_extensions_testset):
    assert httpd_server_base

    INPUT = TEST_Path / "input"

    for input in Path(INPUT).glob("*"):
        log.debug(f"{input=}")
        # get name of file
        name_file = input.name
        url = f"{httpd_server_base}{name_file}"
        log.debug(f"{url=}")
        req = requests.get(url)
        assert req.ok
        ctype = req.headers.get("content-type")
        clen = int(req.headers.get("content-length"))
        assert clen > 0
        log.debug(f"{clen=}")
        log.debug(f"{ctype=}")

        g = Graph().parse(url)
        # ttl = g.serialize(format="turtle").strip()
        # log.debug(f"{ttl=}")
        log.debug(f"{len(g)=}")
