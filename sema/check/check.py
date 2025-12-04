import logging
import os
from typing import Any, Dict, List

import yaml

from sema.commons.service import ServiceBase, ServiceResult

from .implementations.test_example import (  # Import concrete test classes
    ExampleTest,
)
from .sinks import write_csv, write_html, write_yml

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
                        if isinstance(data, list):
                            rules.extend(data)
                        else:
                            rules.append(data)
                except Exception:
                    log.error(f"Error parsing {file}")
        except Exception:
            log.exception(f"Error loading {file}")
    log.debug(f"Loaded {len(rules)} rules")
    return rules


def instantiatie_impl_checks(rule):
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


def run_tests(input_folder: str) -> List[Dict[str, Any]]:
    rules = load_yaml_files(input_folder)
    log.info(f"Loaded {len(rules)} rules from {input_folder}")
    results = []
    for i, rule in enumerate(rules, 1):
        try:
            test = instantiatie_impl_checks(rule)
            log.debug(
                f"Running test {i}/{len(rules)}: {test.__class__.__name__}"
            )
            result = test.run()
            results.append(result)
        except Exception as e:
            log.exception(f"Error running test {i}/{len(rules)}: {e}")
            results.append({"status": "error", "message": str(e)})
    log.info(f"Completed {len(results)} tests")
    return results


class CheckResult(ServiceResult):
    """Result of the check service"""

    def __init__(self) -> None:
        self._success = False

    @property
    def success(self) -> bool:
        return self._success


class Check(ServiceBase):
    """The main class for the check service."""

    def __init__(self, *, input_folder: str, output: str) -> None:
        """Initialize the Check Service object

        :param input_folder: the folder where the files
        to be checked are located
        :type input_folder: str
        :param output: the output format to be used
        :type output: str
        """
        self.input_folder = input_folder
        self.output = output

        log.debug(
            "Check service initialized with input_folder: %s, output: %s",
            self.input_folder,
            self.output,
        )

        if not self.input_folder:
            raise ValueError("input_folder not provided")
        if not self.output:
            raise ValueError("output not provided")

        self._result = CheckResult()

    def process(self) -> bool:
        """Process the check service"""
        try:
            results = run_tests(self.input_folder)
            log.debug(f"Test results: {results}")
            if self.output == "csv":
                write_csv(results, "results.csv")
            elif self.output == "html":
                write_html(results, "results.html")
            elif self.output == "yml":
                write_yml(results, "results.yml")
            log.debug("Test results written to results.%s", self.output)
            self._result._success = True
        except Exception as e:
            log.error(f"An error occurred: {e}")
        finally:
            return self._result._success
