import logging
# import sys
from pathlib import Path

from sema.check import service

log = logging.getLogger(__name__)


def test_load_yaml_file():
    input_folder = Path(__file__).parent / "test_files"

    rules = [
        {
            "options": {"param1": "value1", "param2": "value2"},
            "type": "example",
            "url": "http://example.com",
        },
        {
            "options": {"paramA": "valueA"},
            "type": "example",
            "url": "http://another.com/another",
        },
    ]
    loaded_rules = service.load_yaml_files(input_folder)
    assert len(loaded_rules) == 2
    assert rules == loaded_rules


def test_instantiate_tests():
    rule = {
        "options": {"param1": "value1", "param2": "value2"},
        "type": "example",
        "url": "http://example.com",
    }
    test = service.instantiate_test(rule)
    assert test.url == "http://example.com"
    assert test.options == {"param1": "value1", "param2": "value2"}
    assert test.type == "example"


def test_instantiate_unknown_type():
    rule = {
        "options": {"param1": "value1", "param2": "value2"},
        "type": "unknown",
        "url": "http://example.com",
    }
    try:
        service.instantiate_test(rule)
        assert False, "Should have raised a ValueError"
    except ValueError as e:
        assert str(e) == "Unknown test type: unknown"


def test_run_tests():
    input_folder = Path(__file__).parent / "test_files"
    results = service.run_tests(input_folder)
    assert len(results) == 2
    assert results[0].success
    assert results[1].success
    assert not results[0].error
    assert not results[1].error
