from sema.bench.handler import (
    PyshaclHandler,
    PysubytHandler,
    PySyncFsTriplesHandler,
    PyTravHarvHandler,
)


class TaskDispatcher:
    func_to_handler = {
        "pysubyt": PysubytHandler,
        "pyshacl": PyshaclHandler,
        "py-sync-fs-triples": PySyncFsTriplesHandler,
        "py-trav-harv": PyTravHarvHandler,
    }

    def dispatch(self, task):
        handler = self.func_to_handler[task.func]
        handler().handle(task)
        return handler
