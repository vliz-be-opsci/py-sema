import logging
from pathlib import Path

from sema.commons.service import ServiceBase, ServiceResult, Trace


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
        # upfront checks
        # path resolving
        # existance and writeability checks
        self._result = RocResult()
        ...

    @Trace.init(Trace)
    def process(self) -> RocResult:
        ...

        self._result._success = True

        return self._result
