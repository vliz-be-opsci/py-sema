import logging

from sema.commons.service import ServiceBase, ServiceResult, Trace

from .service import run_tests
from .sinks import write_csv, write_html, write_yml

log = logging.getLogger(__name__)


class CheckResult(ServiceResult):
    """Result of the check service"""

    def __init__(self):
        self._success = False

    @property
    def success(self) -> bool:
        return self._success


class Check(ServiceBase):
    """The main class for the check service."""

    def __init__(self, *, input_folder: str, output: str) -> None:
        """Initialize the Check Service object

        :param input_folder: the folder where the files
        to be checked are located
        :type input_folder: str
        :param output: the output format to be used
        :type output: str
        """
        self.input_folder = input_folder
        self.output = output

        log.debug(
            "Check service initialized with input_folder: %s, output: %s",
            self.input_folder,
            self.output,
        )

        assert self.input_folder, "input_folder not provided"
        assert self.output, "output not provided"

        self._result = CheckResult()

    @Trace.init(Trace)
    def process(self) -> None:
        """Process the check service"""
        try:
            results = run_tests(self.input_folder)
            log.debug(f"Test results: {results}")
            if self.output == "csv":
                write_csv(results, "results.csv")
            elif self.output == "html":
                write_html(results, "results.html")
            elif self.output == "yml":
                write_yml(results, "results.yml")
            log.debug(f"Test results written to results.{self.output}")
            self._result._success = True
        except Exception as e:
            log.error(f"An error occurred: {e}")
            return self._result._success
        finally:
            return self._result._success
