from yaml import SafeLoader, Loader
from yaml.nodes import ScalarNode
from logging import getLogger, Logger


log: Logger = getLogger(__name__)


class LoaderBuilder():
    def __init__(self):
        # this to guarantee that no add_constuctor() chain are shared
        class ClonedLoader(SafeLoader):
            def __new__(cls, *args, **kwargs):
                return super().__new__(cls)

        self._loader: Loader = ClonedLoader

    def to_resolve(self, context):

        def resolver(loader: SafeLoader, node: ScalarNode) -> str:
            txt = loader.construct_scalar(node)
            try:
                txt = txt.format(**context)
            except KeyError as ke:
                log.error(
                    f"yml config contains '{txt}' "
                    f"with unknown key reference to --> {ke}"
                )
            return txt

        self._loader.add_constructor("!resolve", resolver)
        return self

    def ignore_unknown(self):
        def ignore(loader: SafeLoader, node: ScalarNode) -> str:
            return loader.construct_scalar(node)

        self._loader.add_constructor(None, ignore)
        return self

    def build(self) -> Loader:
        return self._loader
