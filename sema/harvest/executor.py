import logging

from sema.harvest.store import RDFStoreAccess

from .config_build import TravHarvConfig
from .execution_report import ExecutionReport, TaskExecutionReport
from .path_assertion import SubjPropPathAssertion

log = logging.getLogger(__name__)


class TravHarvExecutor:
    """
    A class to represent a TravHarvExecutor.
    This class will assert all paths
    for all subjects given for each task per config.
    """

    def __init__(
        self,
        config_filename: str,
        NSM: TravHarvConfig.NSM,
        tasks: list,
        rdf_store_access: RDFStoreAccess,
    ):
        """constructor

        :param config_filename: str
        :param NSM: dict
        :param tasks: list
        :param rdf_store_access: RDFStoreAccess
        """
        self.config_filename = config_filename
        self.NSM = NSM
        self.tasks = tasks
        self.rdf_store_access = rdf_store_access
        self.execution_report = ExecutionReport(config_filename)
        log.debug("TravHarvExecutor initialized")
        log.debug(f"Config filename: {self.config_filename}")
        log.debug(f"NSM set: {self.NSM}")
        log.debug(f"Tasks: {self.tasks}")

    def assert_all_paths(self):
        """
        Assert all paths for all subjects given for each task per config.
        """
        log.debug(
            """Asserting all paths for all
               subjects given for each task per config"""
        )
        for task in self.tasks:
            task_execution_report = TaskExecutionReport()
            log.debug(f"Task: {task}")
            # check if subject is a URI or a SPARQL query
            log.debug(f"Info task: {task}")
            subject_definition = task.subject_definition
            assertion_path_set = task.assert_path_set
            log.debug(f"Subject definition: {subject_definition}")
            log.debug(f"Assertion path set: {assertion_path_set}")
            for subject in subject_definition.list_subjects():
                log.debug(f"Subject: {subject}")
                for (
                    assertion_path
                ) in assertion_path_set.list_assertion_paths():
                    log.debug(f"Assertion path: {str(assertion_path)}")
                    try:
                        SubjPropPathAssertion(
                            subject,
                            assertion_path,
                            self.rdf_store_access,
                            self.NSM,
                            self.config_filename,
                            task_execution_report,
                        )
                    except Exception as e:
                        log.error(
                            f"""
                            {subject} has an error: {e}
                            for assertion path: {assertion_path}
                            """
                        )
                        log.exception(e)
                    finally:
                        log.debug(
                            f"Assertion path: {str(assertion_path)} asserted"
                        )

            # TODO figure out if the task_execution_report object
            # is a pointer or a copy of the object
            # so add_task_report can be done earlier
            # and the report can happen per assertion basis
            # and not per task basis
            self.execution_report.add_task_report(task_execution_report)
            self.execution_report.report_to_store(self.rdf_store_access)
            log.debug(f"All paths asserted for task: {task}")

        log.debug("All paths asserted for all tasks")
