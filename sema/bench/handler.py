import os

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

from sema.harvest import Harvest
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
        # TODO wrap this direct call in a process class
        # one that can be called elsewhere
        # and adds more features (like including graphdb)
        conforms, _, _ = validate(
            data_graph=os.path.join(  # TODO avoid os.path and use pathlib
                task.input_data_location, task.args["data_graph"]
            ),
            shacl_graph=os.path.join(
                task.sembench_data_location, task.args["shacl_graph"]
            ),
            # TODO: expand options to
            #  - "graphdb" (to valildate graphdb),
            #  - "url" (to get online content and use its mimetype)
            data_graph_format="ttl",
            # TODO: expand options to include "url"
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
        # TODO this return is never used - so should be removed
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
