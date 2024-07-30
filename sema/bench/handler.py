import os
from logging import getLogger

from pyshacl import validate

from sema.harvest import service as TravHarv
from sema.subyt import Subyt
from sema.syncfs import SyncFsTriples

logger = getLogger(__name__)

# TODO - for subyt and syncfs, import service from sema


class TaskHandler:
    def handle(self):
        raise NotImplementedError


class CSVWHandler(TaskHandler):
    def handle(self, task):
        # TODO: implement
        raise NotImplementedError


class EyereasonerHandler(TaskHandler):
    def handle(self, task):
        # TODO: implement
        raise NotImplementedError


class Pykg2tblHandler(TaskHandler):
    def handle(self, task):
        # TODO: implement
        raise NotImplementedError


class PyshaclHandler(TaskHandler):
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


class PysubytHandler(TaskHandler):
    def handle(self, task):
        Subyt(**task.args).process()


class PySyncFsTriplesHandler(TaskHandler):
    def handle(self, task):
        SyncFsTriples(**task.args).process()


class PyTravHarvHandler(TaskHandler):
    def handle(self, task):
        TravHarv(**task.args).process()


class RMLHandler(TaskHandler):
    def handle(self, task):
        # TODO: implement
        raise NotImplementedError
