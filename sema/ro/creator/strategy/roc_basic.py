from pathlib import Path
from sema.ro.creator.api import RocModel, RocStrategy, RocStrategyContext


class BasicStrategy(RocStrategyContext, RocStrategy):
    def __init__(self):
        super().__init__("basic")

    @property
    def roc_template_path(self) -> Path:
        # my own name but with.yml extension
        return Path(__file__).with_suffix(".yml")

    def describe(self) -> str:
        return (
            "A basic strategy to build RO-Crates from yml instructions. "
            "For general use."
        )

    def build_model(self, roccfg: dict[str, any]) -> RocModel:
        # todo implement this
        ...
