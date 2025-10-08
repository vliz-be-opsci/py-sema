class GraphBlueprint:
    def __init__(
            self,
            body: dict | None = None,
            context: str | list | None = None,
            prefix: dict | None = None,
            extends: str = None,
        ):
        self.body = body or {}
        self.context = context
        self.prefix = prefix or {}
        self.extends = extends
        if extends:
            self.lineage = None
            raise NotImplementedError # TODO implement extends
