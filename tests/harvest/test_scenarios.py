#!/usr/bin/env python
import logging
from pathlib import Path

import pytest
from conftest import run_single_test

from sema.commons.j2 import J2RDFSyntaxBuilder
from sema.harvest import TravHarv
from sema.harvest.store import RDFStoreAccess

log = logging.getLogger(__name__)

QUERY_BUILDER: J2RDFSyntaxBuilder = J2RDFSyntaxBuilder(
    templates_folder=str(Path(__file__).parent / "scenarios" / "templates")
)
TEST_FOLDER = Path(__file__).parent
TEST_Path: Path = TEST_FOLDER / "scenarios"
BASE = "http://localhost:8080/"
OUTPUTS = TEST_Path / "output"
INPUT = TEST_Path / "input"
CONFIGS = TEST_Path / "travharv_config"
RDF_MIMES = {
    "text/turtle",
    "application/ld+json",
}

# TODO write out all the assertions for the tests
# this being the number of triples
# the documents that ware asserted
SCENARIOS_OUTCOMES = {
    "dereference_test1_sparql.yml": [
        {"expected_len_triples": "19", "mode": "stop"},
        {"expected_len_triples": "19", "mode": "nostop"},
    ],
    "dereference_test2_sparql.yml": [
        {"expected_len_triples": "28", "mode": "stop"},
        {"expected_len_triples": "TBD", "mode": "nostop"},
    ],
    "dereference_test3_sparql.yml": [
        {"expected_len_triples": "19", "mode": "stop"},
        {"expected_len_triples": "TBD", "mode": "nostop"},
    ],
    "dereference_test4_sparql.yml": [
        {"expected_len_triples": "19", "mode": "stop"},
        {"expected_len_triples": "TBD", "mode": "nostop"},
    ],
    "dereference_test5_sparql.yml": [
        {"expected_len_triples": "19", "mode": "stop"},
        {"expected_len_triples": "TBD", "mode": "nostop"},
    ],
}


def netto_triples_for_store_info_set(
    store_info_set: tuple, store: RDFStoreAccess, context_name_graph: str
):
    if store_info_set == ():
        sparql_all = "SELECT ?s ?p ?o WHERE { ?s ?p ?o }"
        context_name_graph = ""
        sparql = QUERY_BUILDER.build_syntax(
            "execution_report_data.sparql",
        )
    else:
        context_name_graph = store._nmapper.key_to_ng(context_name_graph)
        sparql_all = (
            f"SELECT ?s ?p ?o FROM <{context_name_graph}> "
            f"WHERE {{ ?s ?p ?o }}"
        )
        sparql = QUERY_BUILDER.build_syntax(
            "execution_report_data.sparql",
            context_name_graph=context_name_graph,
        )
    all_triples = store.select(sparql_all)
    execution_report_data_result = store.select(sparql)
    netto_triples = len(all_triples) - len(execution_report_data_result)
    return netto_triples


def graphs_in_execution_report(rdfstore: RDFStoreAccess):
    sparql = """
    PREFIX schema: <https://schema.org/>
    PREFIX void: <http://rdfs.org/ns/void#>
    SELECT ?s ?contentUrl ?triples
    WHERE {
        ?s a schema:DataDownload ;
        schema:contentUrl ?contentUrl ;
        void:triples ?triples .
    }
    """
    results = rdfstore.select(sparql)
    # convert results into list of dicts with just the value
    # convert uriref term or literal to str
    results = [
        {
            "contentUrl": str(result["contentUrl"]),
            "triples": str(result["triples"]),
        }
        for result in results
    ]
    # get the unique results
    results = list(
        {result["contentUrl"]: result for result in results}.values()
    )
    return results


def len_store(store: RDFStoreAccess):
    log.debug("Getting the length of the store")
    triples = store.all_triples()
    return len(triples)


@pytest.mark.usefixtures("httpd_server_base", "store_info_sets")
def test_scenario_one(
    httpd_server_base: str,
    store_info_sets,
):
    assert httpd_server_base
    for store in store_info_sets:

        log.debug(f"testing scenario one for {store}")
        config = CONFIGS / "dereference_test1_sparql.yml"
        travharv = TravHarv(
            config,
            store,
        )
        length_store = len_store(travharv.target_store)

        travharv.process()

        # get all the travharv:downloadedresources from the store
        results = graphs_in_execution_report(travharv.target_store)

        # docs that should be present at all times are
        # DOC1
        docs = ["DOC1"]
        for doc in docs:
            assert any(doc in result["contentUrl"] for result in results)

        # len expected triples is the triplecount of the docs
        # that should be present at all times
        # count all the triples in the results
        expected_len_triples = sum(
            int(result["triples"]) for result in results
        )
        log.debug(f"{expected_len_triples=}")
        log.debug(f"{store=}")
        netto_triples = netto_triples_for_store_info_set(
            store,
            travharv.target_store,
            "dereference_test1_sparql.yml",
        )
        log.debug(f"{netto_triples=}")
        assert netto_triples + length_store >= expected_len_triples

        # delete the context from the store so
        # it doesn't interfere with the next test
        travharv.target_store.drop_graph_for_config(
            "dereference_test1_sparql.yml"
        )


@pytest.mark.usefixtures("httpd_server_base", "store_info_sets")
def test_scenario_two(
    httpd_server_base: str,
    store_info_sets,
):
    assert httpd_server_base
    for store in store_info_sets:
        log.debug(f"testing scenario one for {store}")
        config = CONFIGS / "dereference_test2_sparql.yml"
        travharv = TravHarv(
            config,
            store,
        )
        length_store = len_store(travharv.target_store)
        travharv.process()
        # assertions here

        results = graphs_in_execution_report(travharv.target_store)

        # docs that should be present at all times are
        # DOC1, DOC2, DOC3, DOC4, DOC5, DOC6
        docs = ["DOC1", "DOC2", "DOC3", "DOC4", "DOC5", "DOC6"]
        for doc in docs:
            assert any(doc in result["contentUrl"] for result in results)

        # len expected triples is the triplecount of the docs
        # that should be present at all times
        # count all the triples in the results
        expected_len_triples = sum(
            int(result["triples"]) for result in results
        )
        log.debug(f"{expected_len_triples=}")
        log.debug(f"{store=}")
        netto_triples = netto_triples_for_store_info_set(
            store,
            travharv.target_store,
            "dereference_test2_sparql.yml",
        )
        log.debug(f"{netto_triples=}")
        assert netto_triples + length_store >= expected_len_triples

        # delete the context from the store so
        # it doesn't interfere with the next test
        travharv.target_store.drop_graph_for_config(
            "dereference_test2_sparql.yml"
        )


@pytest.mark.usefixtures("httpd_server_base", "store_info_sets")
def test_scenario_three(
    httpd_server_base: str,
    store_info_sets,
):
    assert httpd_server_base
    for store in store_info_sets:
        log.debug(f"testing scenario one for {store}")
        config = CONFIGS / "dereference_test3_sparql.yml"
        travharv = TravHarv(
            config,
            store,
        )
        length_store = len_store(travharv.target_store)
        travharv.process()
        # assertions here

        # get all the travharv:downloadedresources from the store
        results = graphs_in_execution_report(travharv.target_store)

        # docs that should be present at all times are
        # DOC1
        docs = ["DOC1"]
        for doc in docs:
            assert any(doc in result["contentUrl"] for result in results)

        # scenarios that could happen are
        # DOC1, DOC2, DOC4
        # DOC1, DOC5, DOC6
        # DOC1, DPC3
        # DOC1, DOC8
        # DOC1, DOC7

        possible_docs = [
            ["DOC1", "DOC2", "DOC4"],
            ["DOC1", "DOC5", "DOC6"],
            ["DOC1", "DOC3"],
            ["DOC1", "DOC8"],
            ["DOC1", "DOC7"],
        ]

        # check if any of the possible docs are the same as the results
        scenario_found = False
        for possible_doc in possible_docs:
            log.debug(f"{possible_doc=}")

            # check if all the docs are present in the results
            # if they are then break the loop
            if all(
                any(doc in result["contentUrl"] for result in results)
                for doc in possible_doc
            ):
                scenario_found = True
                break
        assert scenario_found

        # len expected triples is the triplecount of the docs
        # that should be present at all times
        # count all the triples in the results
        expected_len_triples = sum(
            int(result["triples"]) for result in results
        )
        log.debug(f"{expected_len_triples=}")
        log.debug(f"{store=}")

        netto_triples = netto_triples_for_store_info_set(
            store,
            travharv.target_store,
            "dereference_test3_sparql.yml",
        )

        log.debug(f"{netto_triples=}")
        assert netto_triples + length_store >= expected_len_triples
        # delete the context from the store so
        # it doesn't interfere with the next test
        travharv.target_store.drop_graph_for_config(
            "dereference_test3_sparql.yml"
        )


@pytest.mark.usefixtures("httpd_server_base", "store_info_sets")
def test_scenario_four(
    httpd_server_base: str,
    store_info_sets,
):
    assert httpd_server_base
    for store in store_info_sets:
        log.debug(f"testing scenario one for {store}")
        config = CONFIGS / "dereference_test4_sparql.yml"
        travharv = TravHarv(
            config,
            store,
        )
        length_store = len_store(travharv.target_store)
        travharv.process()
        # assertions here

        # get all the travharv:downloadedresources from the store
        results = graphs_in_execution_report(travharv.target_store)

        # docs that should be present at all times are
        # DOC1
        docs = ["DOC1"]
        for doc in docs:
            assert any(doc in result["contentUrl"] for result in results)

        # scenarios that could happen are
        # DOC1, DOC2, DOC4
        # DOC1, DOC5, DOC6
        # DOC1, DPC3
        # DOC1, DOC8
        # DOC1, DOC7

        possible_docs = [
            ["DOC1", "DOC2", "DOC4"],
            ["DOC1", "DOC5", "DOC6"],
            ["DOC1", "DOC3"],
            ["DOC1", "DOC8"],
            ["DOC1", "DOC7"],
        ]

        # check if any of the possible docs are the same as the results
        scenario_found = False
        for possible_doc in possible_docs:
            log.debug(f"{possible_doc=}")

            # check if all the docs are present in the results
            # if they are then break the loop
            if all(
                any(doc in result["contentUrl"] for result in results)
                for doc in possible_doc
            ):
                scenario_found = True
                break
        assert scenario_found

        # len expected triples is the triplecount of the docs
        # that should be present at all times
        # count all the triples in the results
        expected_len_triples = sum(
            int(result["triples"]) for result in results
        )
        log.debug(f"{expected_len_triples=}")
        log.debug(f"{store=}")

        netto_triples = netto_triples_for_store_info_set(
            store,
            travharv.target_store,
            "dereference_test4_sparql.yml",
        )

        log.debug(f"{netto_triples=}")
        assert netto_triples + length_store >= expected_len_triples

        # delete the context from the store so
        # it doesn't interfere with the next test
        travharv.target_store.drop_graph_for_config(
            "dereference_test4_sparql.yml"
        )


@pytest.mark.usefixtures("httpd_server_base", "store_info_sets")
def test_scenario_five(
    httpd_server_base: str,
    store_info_sets,
):
    assert httpd_server_base
    for store in store_info_sets:
        log.debug(f"testing scenario one for {store}")
        config = CONFIGS / "dereference_test5_sparql.yml"
        travharv = TravHarv(
            config,
            store,
        )
        length_store = len_store(travharv.target_store)
        travharv.process()
        # assertions here

        # get all the travharv:downloadedresources from the store
        results = graphs_in_execution_report(travharv.target_store)

        # docs that should be present at all times are
        # DOC1
        docs = ["DOC1"]
        for doc in docs:
            assert any(doc in result["contentUrl"] for result in results)

        # scenarios that could happen are
        # DOC1, DOC2, DOC4
        # DOC1, DOC5, DOC6
        # DOC1, DPC3
        # DOC1, DOC8
        # DOC1, DOC7

        possible_docs = [
            ["DOC1", "DOC2", "DOC4"],
            ["DOC1", "DOC5", "DOC6"],
            ["DOC1", "DOC3"],
            ["DOC1", "DOC8"],
            ["DOC1", "DOC7"],
        ]

        # check if any of the possible docs are the same as the results
        scenario_found = False
        for possible_doc in possible_docs:
            log.debug(f"{possible_doc=}")

            # check if all the docs are present in the results
            # if they are then break the loop
            if all(
                any(doc in result["contentUrl"] for result in results)
                for doc in possible_doc
            ):
                scenario_found = True
                break
        assert scenario_found

        # len expected triples is the triplecount of the docs
        # that should be present at all times
        # count all the triples in the results
        expected_len_triples = sum(
            int(result["triples"]) for result in results
        )
        log.debug(f"{expected_len_triples=}")
        log.debug(f"{store=}")

        netto_triples = netto_triples_for_store_info_set(
            store,
            travharv.target_store,
            "dereference_test5_sparql.yml",
        )

        log.debug(f"{netto_triples=}")
        assert netto_triples + length_store >= expected_len_triples

        # delete the context from the store so
        # it doesn't interfere with the next test
        travharv.target_store.drop_graph_for_config(
            "dereference_test5_sparql.yml"
        )


if __name__ == "__main__":
    run_single_test(__file__)
