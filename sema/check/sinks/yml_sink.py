# your_submodule/sinks/yml_sink.py

from typing import List

import yaml

from ..testing.base import TestResult


def write_yml(results: List[TestResult], output_file: str):
    with open(output_file, "w") as f:
        yaml.dump([result.__dict__ for result in results], f)
