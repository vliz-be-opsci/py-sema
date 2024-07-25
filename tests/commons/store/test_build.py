import logging

import pytest

from sema.commons.store import MemoryRDFStore, URIRDFStore, create_rdf_store

log = logging.getLogger(__name__)


def test_create_rdf_store():
    # Test case 1: No arguments
    store = create_rdf_store()
    assert isinstance(store, MemoryRDFStore)

    # Test case 2: One argument
    store = create_rdf_store("read_uri")
    assert isinstance(store, URIRDFStore)

    # Test case 3: Two arguments
    store = create_rdf_store("read_uri", "write_uri")
    assert isinstance(store, URIRDFStore)

    # Test case 4: More than two arguments
    with pytest.raises(AssertionError):
        create_rdf_store("read_uri", "write_uri", "extra_uri")
