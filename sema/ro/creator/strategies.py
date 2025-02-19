from singleton_decorator import singleton

from sema.ro.creator.api import RocStrategy

# load registry of available and known strategies
# run over embedde ones
# consider some env to yml listing more strategies to load
# expose a singleton strategy registry
# with api for more strategies to be added


@singleton
class RocStrategies():
    def __init__(self):
        self._strategies = {}
        self._load_embedded_strategies()

    def get(self, name: str):
        return self._strategies.get(name)

    def register(self, name: str, strategy: RocStrategy):
        self._strategies[name] = strategy
