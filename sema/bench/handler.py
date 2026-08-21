import os
import re
from pathlib import Path

"""
This module defines various task handlers for different types of tasks.
Each handler inherits from the `TaskHandler` base class and
implements the `handle` method to process specific tasks.
Classes:
    TaskHandler: Abstract base class for task handlers.
    CSVWHandler: Handler for CSVW tasks.
    EyereasonerHandler: Handler for Eyereasoner tasks.
    QueryHandler: Handler for Query tasks.
    ShaclHandler: Handler for SHACL validation tasks.
    SubytHandler: Handler for Subyt tasks.
    SyncFsTriplesHandler: Handler for SyncFsTriples tasks.
    HarvestHandler: Handler for Harvest tasks.
    RMLHandler: Handler for RML tasks.
The `TaskHandler` class provides a common interface for handling tasks,
allowing for a consistent way to process different types of tasks.
Each specific handler class implements the `handle` method
to perform the necessary actions for its respective task type.
"""
from logging import getLogger

from pyshacl import validate

from sema.commons.aggregator import Aggregator
from sema.commons.reason import Reasoner
from sema.harvest import Harvest
from sema.ro.getter import ROGetter
from sema.subyt import Subyt
from sema.syncfs import SyncFsTriples

logger = getLogger(__name__)

# TODO - for subyt and syncfs, import service from sema
# from sema.query import service as Query


class TaskHandler:
    def handle(self, task):
        raise NotImplementedError


class CSVWHandler(TaskHandler):
    def handle(self, task):
        # TODO: implement
        raise NotImplementedError


class EyereasonerHandler(TaskHandler):
    def handle(self, task):
        # TODO: implement
        raise NotImplementedError


class QueryHandler(TaskHandler):
    def handle(self, task):
        # TODO: implement
        # Query(**task.args).process()
        raise NotImplementedError


class ShaclHandler(TaskHandler):
    def handle(self, task):
        conforms, _, _ = validate(
            data_graph=os.path.join(
                task.input_data_location, task.args["data_graph"]
            ),
            shacl_graph=os.path.join(
                task.sembench_data_location, task.args["shacl_graph"]
            ),
            data_graph_format="ttl",
            shacl_graph_format="ttl",
            inference="rdfs",
            debug=True,
        )
        assert conforms, (
            "pyshacl validation failed for "
            f"data graph \"{task.args['data_graph']}\" "
            "with "
            f"shape graph \"{task.args['shacl_graph']}\""
        )
        return conforms


class SubytHandler(TaskHandler):
    def handle(self, task):
        Subyt(**task.args).process()


class SyncFsTriplesHandler(TaskHandler):
    def handle(self, task):
        SyncFsTriples(**task.args).process()


class HarvestHandler(TaskHandler):
    def handle(self, task):
        Harvest(**task.args).process()


class RMLHandler(TaskHandler):
    def handle(self, task):
        # TODO: implement
        raise NotImplementedError


class AggregateHandler(TaskHandler):
    def handle(self, task):
        Aggregator(**task.args).process()


class RoGetHandler(TaskHandler):
    def handle(self, task):
        ROGetter(**task.args).process()


SPARQL_KW_PATTERN = re.compile(
    r"^\s*(PREFIX|BASE|CONSTRUCT|SELECT|ASK|DESCRIBE)\s+",
    re.IGNORECASE,
)


def _is_inline_sparql(val: str) -> bool:
    """Check if string is an inline SPARQL query text."""
    if not isinstance(val, str):
        return False
    if "\n" in val:
        return True
    return bool(SPARQL_KW_PATTERN.match(val.strip()))


def _resolve_bench_path(val, base_dir):
    """Resolve relative path or glob pattern against base_dir."""
    if isinstance(val, (str, Path)):
        if isinstance(val, str) and _is_inline_sparql(val):
            return val
        p = Path(val)
        if not p.is_absolute():
            if (Path(base_dir) / p).exists():
                return str(Path(base_dir) / p)
            val_str = str(val)
            if "*" in val_str or "?" in val_str:
                return str(Path(base_dir) / p)
    return val


def _resolve_bench_paths(item, base_dir):
    """Resolve scalar or list of relative paths against base_dir."""
    if isinstance(item, list):
        return [_resolve_bench_path(x, base_dir) for x in item]
    elif isinstance(item, (str, Path)):
        return _resolve_bench_path(item, base_dir)
    return item


class ReasonHandler(TaskHandler):
    """Handler for SemBench SPARQL reasoning tasks."""

    def handle(self, task):
        """Execute the reasoning task with resolved sources and queries."""
        args = dict(task.args)
        if "sources" in args:
            args["sources"] = _resolve_bench_paths(
                args["sources"], task.input_data_location
            )
        if "queries" in args:
            args["queries"] = _resolve_bench_paths(
                args["queries"], task.sembench_data_location
            )
        if "input_path" not in args:
            args["input_path"] = task.sembench_data_location
        Reasoner(**args).process()
