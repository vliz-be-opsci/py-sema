import logging
import logging.config
import os
import re
import shutil
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread
from typing import Dict, Iterable, Optional

import pytest
import requests
import yaml
from dotenv import load_dotenv
from rdflib import BNode, Graph, Namespace, URIRef

from sema.commons.store import RDFStore, create_rdf_store
from sema.harvest.store import RDFStoreAccess

TEST_INPUT_FOLDER = Path(__file__).parent / "./input"
DCT: Namespace = Namespace("http://purl.org/dc/terms/#")
DCT_ABSTRACT: URIRef = DCT.abstract
SELECT_ALL_SPO = "SELECT ?s ?p ?o WHERE { ?s ?p ?o . }"
TEST_FOLDER = Path(__file__).parent
TEST_OUTPUT_FOLDER = TEST_FOLDER / "output"
TEST_Path: Path = TEST_FOLDER / "harvest" / "scenarios"
HTTPD_ROOT: Path = TEST_Path / "input"
HTTPD_HOST: str = (
    "localhost"  # can be '' - maybe also try '0.0.0.0' to bind all
)
HTTPD_PORT: int = 8080
HTTPD_EXTENSION_MAP: Dict[str, str] = {
    ".txt": "text/plain",
    ".jsonld": "application/ld+json",
    ".ttl": "text/turtle",
}

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


@pytest.fixture(scope="session")
def _mem_rdf_store() -> RDFStore:
    """in memory store
    uses simple dict of Graph
    """
    log.debug("creating in memory rdf store")
    return create_rdf_store()


@pytest.fixture(scope="session")
def _uri_rdf_store() -> RDFStore:
    """proxy to available graphdb store
    But only if environment variables are set and service is available
    else None (which will result in trimming it from rdf_stores fixture)
    """
    read_uri = os.getenv("TEST_SPARQL_READ_URI", None)
    write_uri = os.getenv("TEST_SPARQL_WRITE_URI", read_uri)
    # if no URI provided - skip this by returning None
    if read_uri is None or write_uri is None:
        log.debug("not creating uri rdf store in test - no uri provided")
        return None
    # else -- all is well
    log.debug(f"creating uri rdf store proxy to ({read_uri=}, {write_uri=})")
    return create_rdf_store(read_uri, write_uri)


@pytest.fixture()
def rdf_stores(_mem_rdf_store, _uri_rdf_store) -> Iterable[RDFStore]:
    """trimmed list of available stores to be tested
    result should contain at least memory_rdf_store, and (if available)
    also include uri_rdf_store
    """
    stores = tuple(
        store
        for store in (_mem_rdf_store, _uri_rdf_store)
        if store is not None
    )
    return stores


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
