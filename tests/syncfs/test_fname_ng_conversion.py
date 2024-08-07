""" test_fname_ng_conversion
tests our expectations on translating filenames to named_graphs and back
"""

import logging
from pathlib import Path
from typing import Iterable

import pytest
from conftest import TEST_FOLDER

from sema.commons.store import RDFStore
from sema.syncfs.service import GraphNameMapper, sync_addition

log = logging.getLogger(__name__)


def test_key_to_ng():
    log.info("test_key_to_ng")
    base: str = "urn:sync:"
    nmapper: GraphNameMapper = GraphNameMapper(base=base)

    # Test case 1: Valid filename
    fname = "example.txt"
    expected_ng = "urn:sync:example.txt"
    assert nmapper.key_to_ng(fname) == expected_ng

    # Test case 2: Filename with special characters
    fname = "file name with spaces.txt"
    expected_ng = "urn:sync:file%20name%20with%20spaces.txt"
    assert nmapper.key_to_ng(fname) == expected_ng

    # Test case 3: Empty filename
    fname = ""
    expected_ng = "urn:sync:"
    assert nmapper.key_to_ng(fname) == expected_ng

    # Add more test cases as needed


def test_ng_to_key():
    log.info("test_ng_to_key")
    base: str = "urn:sync:"
    nmapper: GraphNameMapper = GraphNameMapper(base=base)

    # Test case 1: Valid named graph URN
    ng = "urn:sync:example.txt"
    expected_fname = "example.txt"
    assert nmapper.ng_to_key(ng) == expected_fname

    # Test case 2: Named graph URN with special characters
    ng = "urn:sync:file%20name%20with%20spaces.txt"
    expected_fname = "file name with spaces.txt"
    assert nmapper.ng_to_key(ng) == expected_fname

    # Add more test cases as needed


@pytest.mark.usefixtures("rdf_stores")
def test_get_keys_in_store(rdf_stores: Iterable[RDFStore]):
    log.info(f"test_get_keys_in_store ({len(list(rdf_stores))})")
    for rdf_store in rdf_stores:
        rdf_store_type: str = type(rdf_store).__name__
        # Test case 1: Empty store
        for key in rdf_store.keys:
            rdf_store.forget_graph_for_key(key)
        assert rdf_store.keys == []

        # TODO: discuss with @mpo to see if this is a valid approach
        # before the addition of Path this test would fail with
        # 'input\\marine_region_63523.ttl' != 'input/marine_region_63523.ttl'

        # Test case 2: Store with one named graph
        relative = Path("input/marine_region_63523.ttl")
        sync_addition(rdf_store, TEST_FOLDER / relative, TEST_FOLDER)
        keys_in_store: Iterable[str] = rdf_store.keys
        assert keys_in_store == [str(relative)]
        log.debug(f"{rdf_store_type} :: {keys_in_store=}")

        # Add more test cases as needed
