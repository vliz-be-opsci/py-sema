from sema.bench.handler import (
    AggregateHandler,
    HarvestHandler,
    RoGetHandler,
    ShaclHandler,
    SubytHandler,
    SyncFsTriplesHandler,
)


class TaskDispatcher:
    func_to_handler = {
        "subyt": SubytHandler,
        "shacl": ShaclHandler,
        "sync-fs-triples": SyncFsTriplesHandler,
        "harvest": HarvestHandler,
        "aggregate": AggregateHandler,
        "ro-get": RoGetHandler,
    }

    def dispatch(self, task):
        handler = self.func_to_handler[task.func]
        handler().handle(task)
        return handler
