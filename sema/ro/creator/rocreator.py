import logging
import os
from pathlib import Path

from sema.commons.service import ServiceBase, ServiceResult, Trace
from .api import RocModel, RocStrategy, write_model, read_roccfg
from .strategies import RocStrategies

log = logging.getLogger(__name__)


class RocResult(ServiceResult):
    """Result of the Roc service"""

    def __init__(self):
        self._success = False

    @property
    def success(self) -> bool:
        return self._success


class Roc(ServiceBase):
    """The main class for the roc 'ro-creator' service."""

    def __init__(
        self,
        *,
        root: str,
        rocyml: str,
        out: str,
        force: bool = False,
    ) -> None:
        """Initialize the roc Service object

        :param root: the path to the ro-crate root folder to work on,
            if relative it is relative to the current working directory
        :type root: str
        :param rocyml: the path to the roc yml file to be used,
            if relative it is relative to the root
        :type rocyml: str
        :param out: the path to the output file to be used,
            if relative it is relative to the root
        :type out: str
        :param force: overwrites the output file even if it exists
        :type force: bool
        """
        self._result = RocResult()
        # path resolving, exists, read-write checks
        self._root: Path = Path(root)
        if (not self._root.exists()) or (not self._root.is_dir()):
            raise ValueError("root path does not exist or is not a folder")

        self._rocymla: Path = self._root / rocyml
        if (not self._rocyml.exists()) or (not self._rocyml.is_file()):
            raise ValueError("roc yml file does not exist or is not a file")
        if not os.access(self._rocyml, os.R_OK):
            raise ValueError("roc yml file is not readable")

        self._out: Path = self._root / out
        if self._out.exists() and (not force):
            raise ValueError("output file exists but is not a file")
        if not self._out.exists():
            self._out.parent.mkdir(parents=True, exist_ok=True)

    @Trace.init(Trace)
    def process(self) -> RocResult:
        roccfg: dict[str, any] = read_roccfg(self._rocyml)
        sg_name: str = roccfg.get("uses", "basic")
        sg = RocStrategies.get_strategy(sg_name)
        rocm: RocModel = sg.build_model(roccfg)
        write_model(rocm, self._out)
        self._result._success = True

        return self._result
