from sema.bench.handler import (
    HarvestHandler,
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
    }

    def dispatch(self, task):
        handler = self.func_to_handler[task.func]
        handler().handle(task)
        return handler
