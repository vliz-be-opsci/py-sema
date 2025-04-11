import os
import yaml
from abc import ABC, abstractmethod
from pathlib import Path
from sema.commons.yml import LoaderBuilder

# main elements of the roc API

# strategy interface and strategies registry
# serializer interface / function ?
# yml processing input & conversion to model


class RocModel:
    """The internal model structuring all content expected inside a RO-Crate.
    The various RocStrategy implementations allow for how to popiulate up this
    from reading any specific yml file.
    Serialising these models to jsonld completes the work of the RoCreator.
    """

    ...


class RocStrategy(ABC):
    """Abstract interface for a ROC strategy."""
    @abstractmethod
    def describe(self) -> str:
        """Produce a short (< 255 chars) description of what
        this strategy is about.
        """
        pass

    @property
    def rocyml_template_path(self) -> Path:
        """The path to the template roc yml file for this strategy."""
        raise NotImplementedError

    def make_rocyml(self, rocyml: Path) -> None:
        """Make the roc yml file for this strategy.
        Standard implementation uses self.rocyml_template_path to copy content.
        Either override this method or use that property to provide such path.
        @param rocyml: The path to the roc yml file to be created.
        """
        if not self.rocyml_template_path.exists():
            raise FileNotFoundError(f"roc yml template not found at {self.rocyml_template_path}")
        # else
        rocyml.parent.mkdir(parents=True, exist_ok=True)
        with self.rocyml_template_path.open() as src, rocyml.open("w") as dst:
            dst.write(src.read())

    @abstractmethod
    def build_model(self, roccfg: dict[str, any]) -> RocModel:
        """Build the model for this strategy."""
        pass


class RocStrategyContext:
    """Base class for a context manager for a RocStrategy."""
    def __init__(self, name: str):
        super().__init__()
        self._name = name

    @property
    def name(self) -> str:
        """The name of this strategy. Used as key in the registry."""
        return self._name

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        pass

    def __call__(self, uses: dict[str, any]) -> RocStrategy:
        """Extra call allows for configuration of the strategy."""
        return self


def read_roccfg(rocyml: Path) -> RocModel:
    context: dict = os.environ.copy()
    loader = LoaderBuilder().to_resolve(context).build()
    with rocyml.open() as f:
        roccfg = yaml.load(f, Loader=loader)
        return roccfg


def write_model(rocmodel: RocModel, rocrate_path: Path):
    # TODO create the jsonld file based on the internal model
    ...
