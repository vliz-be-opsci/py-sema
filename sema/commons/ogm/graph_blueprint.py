class GraphBlueprint:
    def __init__(
            self,
            body: dict | None = None,
            prefix: dict | None = None,
            extends: str = None,
        ):
        self.body = body or {}
        self.prefix = prefix or {}
        self.extends = extends
        if extends:
            self.lineage = []
            raise NotImplementedError # TODO implement extends
