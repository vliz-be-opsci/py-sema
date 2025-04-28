from contextlib import contextmanager
from typing import Generator
from singleton_decorator import singleton
from sema.ro.creator.api import RocStrategy, RocStrategyContext
from .roc_basic import BasicStrategy

# load registry of available and known strategies
# run over embedded ones
# consider some env to yml listing more strategies to load
# expose a singleton strategy registry
# with api for more strategies to be added


@singleton
class RocStrategies:
    """The registry of all known RocStrategies.
    In fact it is a registry of RoCrateStrategyContexts
    but this is largely opaque to the user."""

    def __init__(self):
        self._strategies = {}
        self._load_embedded_strategies()

    @property
    def names(self):
        return self._strategies.keys()

    def get_context(self, name: str):
        return self._strategies.get(name)

    def register(self, strategy: RocStrategyContext):
        self._strategies[strategy.name] = strategy

    def _load_embedded_strategies(self):
        # for now hard-coded references, can look into dynamic stuff later
        self.register(BasicStrategy())

    @contextmanager
    def get_strategy(
        self,
        roccfg: dict[str, any] | str,
    ) -> Generator[RocStrategy, None, None]:
        # convert str arg to expected dict
        if isinstance(roccfg, str):
            roccfg = {"uses": {"strategy": roccfg}}

        uses: str | dict = roccfg.get("uses", {"strategy": "basic"})
        # convert str cfg to expected dict
        if isinstance(uses, str):
            uses = {"strategy": uses}

        name: str = uses.get("strategy", "basic")
        context = self.get_context(name)
        with context(uses) as strategy:
            yield strategy
