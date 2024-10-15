# your_submodule/service.py

import logging
import os

import yaml

# from .testing.base import TestBase
from .testing.test_example import ExampleTest  # Import concrete test classes

log = logging.getLogger(__name__)


def load_yaml_files(input_folder):
    log.debug(f"Loading YAML files from {input_folder}")
    yaml_files = [
        f
        for f in os.listdir(input_folder)
        if f.endswith(".yaml") or f.endswith(".yml")
    ]
    rules = []
    for file in yaml_files:
        log.debug(f"Loading {file}")
        try:
            with open(os.path.join(str(input_folder), file), "r") as stream:
                try:
                    data = yaml.safe_load(stream)
                    if data:
                        rules.extend(data)
                except yaml.YAMLError as exc:
                    log.error(f"Error parsing {file}: {exc}")
        except Exception as e:
            log.exception(f"Error loading {file}: {e}")
    log.debug(f"Loaded {len(rules)} rules")
    return rules


def instantiate_test(rule):
    log.debug(f"Instantiating test from rule: {rule}")
    test_type = rule.get("type")
    log.debug(f"Test type: {test_type}")
    if test_type == "example":
        return ExampleTest(
            url=rule.get("url"),
            options=rule.get("options"),
            type_test=rule.get("type"),
        )
    # Add more test types here
    else:
        raise ValueError(f"Unknown test type: {test_type}")


def run_tests(input_folder):
    rules = load_yaml_files(input_folder)
    log.debug(f"Loaded rules: {rules}")
    test_objects = [instantiate_test(rule) for rule in rules]
    results = []
    for test in test_objects:
        result = test.run()
        results.append(result)
    return results
