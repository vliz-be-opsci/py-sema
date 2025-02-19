# main elements of the roc API

# strategy interface
# serializer interface / function ?
# yml processing input & conversion to model


from abc import ABC, abstractmethod
from pathlib import Path

import yaml
from sema.commons.yml import LoaderBuilder


class RocModel():
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
        """Produce a short (< 255) description of what this strategy is about."""
        pass

    @abstractmethod
    def make_rocyml(self, rocyml: Path) -> str:
        """Make the roc yml file for this strategy."""
        pass

    @abstractmethod
    def build_model(self, roccfg: dict[str, any]) -> RocModel:
        """Build the model for this strategy."""
        pass


def read_roccfg(self, rocyml: Path) -> RocModel:
    loader = LoaderBuilder().build()  # for now, no resolving context
    with rocyml.open() as f:
        roccfg = yaml.load(f, Loader=loader)
        return roccfg


def write_model(rocmodel: RocModel, rocrate_path: Path):
    # TODO create the jsonld file based on the internal model
    ...
