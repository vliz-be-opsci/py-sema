import os
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


class ReasonHandler(TaskHandler):
    def handle(self, task):
        args = dict(task.args)
        if "sources" in args and isinstance(args["sources"], list):
            args["sources"] = [
                str(Path(task.input_data_location) / s)
                if isinstance(s, (str, Path))
                and not Path(s).is_absolute()
                and (Path(task.input_data_location) / s).exists()
                else s
                for s in args["sources"]
            ]
        if "queries" in args and isinstance(args["queries"], list):
            args["queries"] = [
                str(Path(task.sembench_data_location) / q)
                if isinstance(q, (str, Path))
                and not Path(q).is_absolute()
                and (Path(task.sembench_data_location) / q).exists()
                else q
                for q in args["queries"]
            ]
        if "input_path" not in args:
            args["input_path"] = task.sembench_data_location
        Reasoner(**args).process()
