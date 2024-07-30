from sema.bench.handler import (
    ShaclHandler,
    SubytHandler,
    SyncFsTriplesHandler,
    HarvestHandler,
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
