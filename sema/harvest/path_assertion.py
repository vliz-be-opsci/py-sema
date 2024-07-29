import logging
from uuid import uuid4

import rdflib
import validators
from rdflib.namespace import NamespaceManager

from sema.harvest.store import RDFStoreAccess
from sema.harvest.url_to_graph import get_graph_for_format

from .config_build import AssertPath
from .execution_report import (
    GraphAdditionReport,
    PathAssertionReport,
    TaskExecutionReport,
)
from .helper import timestamp

log = logging.getLogger(__name__)


class SubjPropPathAssertion:
    """
    A class to represent the assertion of
    all given property traversal paths for a given subject.
    """

    def __init__(
        self,
        subject: str,
        assertion_path: AssertPath,
        rdf_store_access: RDFStoreAccess,
        NSM: NamespaceManager,
        config_name: str,
        task_execution_report: TaskExecutionReport,
    ):
        """
        Construct a SubjPropPathAssertion object.
        Automatically asserts a property path for a given subject.
        Puts the results in a RDFStoreAccess.

        :param subject: str
        :param assertion_path: AssertPath
        :param rdf_store_access: RDFStoreAccess
        :param NSM: dict
        :param config_name: str

        """
        log.debug(subject)
        self.subject = self._subject_str_check(subject)
        if not self.subject:
            log.warning(f"Subject is not a valid URIRef or str: {subject}")
            return
        self.assertion_path = assertion_path
        self.depth = 0
        self.rdf_store_access = rdf_store_access
        self.previous_bounce_depth = 0
        self.max_depth = self.assertion_path.get_max_size()
        self.NSM = NSM
        self.config_name = config_name
        self.succesful_assertion_depth = 0
        self.task_execution_report = task_execution_report
        self.assertion_report_info = {
            "subject_uri": self.subject,
            "id": uuid4(),
        }
        self.bounced = False
        self.graph_reports = []
        # TODO: test if it is needed to really assert the path
        # During testing it came out that sometimes this is needed
        # since sometimes the subject is the beginning one for the path
        # and sometimes it is not
        # self._harvest_uri(self.subject)
        self.assert_path()

        # based on the self.successfull assertion depth determine
        # the property path that was successfull asserted
        pp_for_report = self.assertion_path.get_path_for_depth(
            self.succesful_assertion_depth
        )
        assertion_result = False
        message = f"Assertion failed, last path: {pp_for_report}"
        if self.succesful_assertion_depth == self.max_depth:
            assertion_result = True
            message = "Assertion successful"

        self.task_execution_report.add_path_assertion_report(
            PathAssertionReport(
                subject_uri=self.subject,
                assertion_path=pp_for_report,
                assertion_result=assertion_result,
                assertion_time=timestamp(),
                id=self.assertion_report_info["id"],
                message=message,
                graph_reports=self.graph_reports,
            )
        )

    def _subject_str_check(self, subject):
        """
        Check if subject is a strict str
        , if subject is rdflib.term.URIRef , convert to str
        """
        if type(subject) is str and validators.url(subject):
            log.debug(f"Subject is a valid URIRef: {subject}")
            return subject
        if "localhost" in subject:
            log.debug(f"Subject is a valid localhost URIRef: {subject}")
            return str(subject)
        if (
            type(subject) is rdflib.query.ResultRow
            or type(subject) is rdflib.term.URIRef
        ):
            # extract URIRef from ResultRow
            if type(subject) is rdflib.query.ResultRow:
                subject_row = subject[0]
                if type(subject_row) is dict:
                    subject_row = subject_row[
                        "value"
                    ]  # janky way of getting the URIRef from the ResultRow
                log.debug(f"Subject row: {subject_row}")
                if validators.url(subject_row):
                    return str(subject_row)
                if "localhost" in subject_row:
                    return str(subject_row)
                log.warning(f"Subject row is not a URIRef: {subject_row}")
            if validators.url(str(subject)):
                return str(subject)
            if "localhost" in str(subject):
                return str(subject)
            log.warning(f"Subject is not a URIRef: {subject}")
        log.debug(f"Subject is of type {type(subject)}")
        if not validators.url(str(subject)):
            log.warning(f"Subject is not a URIRef or a str: {subject}")
            return None

    def assert_path(self):
        """
        Assert a property path for a given subject.
        Put the results in a RDFStoreAccess.
        """
        log.debug("Asserting a property path for a given subject")
        log.debug(f"Subject: {self.subject}")
        # Implement method to assert a property path for a given subject
        while self.depth <= self.max_depth:
            # first check if last_succesful_depth is not
            # the same as the current depth
            # if it is not the same, then we have to assert the path
            if self.depth == self.max_depth and self.bounced is False:
                self._harvest_uri(self.subject)
                self._surface()

            if self.depth == self.max_depth and self.bounced is True:
                return
            self._assert_at_depth()
            self._increase_depth()

    def _assert_at_depth(self):
        """
        Assert a property path for a given subject at a given depth.
        """
        log.debug(
            "Asserting a property path for a given subject at a given depth"
        )
        log.debug(f"Subject: {self.subject}")
        log.debug(f"Depth: {self.path_length}")
        log.debug(f"""ppath: {self.path_for_depth}""")
        if self.rdf_store_access.verify_path(
            self.subject,
            self.path_for_depth,
            self.NSM,
        ):
            if self.depth != self.max_depth:
                log.debug("Subjects for property path assertion found")
                self._harvest()
                self.succesful_assertion_depth = self.depth
                return
            log.debug("Path assertion successful")
            self.succesful_assertion_depth = self.depth
            self._increase_depth()
            return

    def _harvest_uri(self, uri):
        """
        Harvest a given uri

        :param uri: str
        """
        # TODO in a next update this will be config driven
        MIMETYPES_TO_GET = {
            "text/turtle",
        }
        # doubting if this is really needed
        # here as a mimetype to get

        log.debug(f"Beginning harvesting of URI: {uri}")

        for mimetype in MIMETYPES_TO_GET:
            # do a get of the uri with the mimetype
            graph = get_graph_for_format(uri, [mimetype])
            log.debug(f"Graph: {graph}")
            if graph is not None:
                self.rdf_store_access.insert_for_config(
                    graph, self.config_name
                )

                self.graph_reports.append(
                    GraphAdditionReport(
                        download_url=uri,
                        mime_type=mimetype,
                        triple_count=len(graph),
                    )
                )

            else:
                log.debug(f"{uri=}, {mimetype=} did not return graph")
                return
        return

    @property
    def path_length(self):
        return self.max_depth - self.depth

    @property
    def path_for_depth(self):
        return self.assertion_path.get_path_for_depth(self.path_length)

    def _increase_depth(self):
        """
        Increase the depth of the property path assertion.
        """
        log.debug("Increasing the depth of the property path assertion")
        self.depth += 1

    def _surface(self):
        """
        Surface back to depth 0.
        """
        log.debug("Surfacing back to depth 0")
        self.previous_bounce_depth = self.depth
        self.depth = 0
        self.bounced = True

    def _harvest(self):
        """
        Harvest the property path.
        """
        log.debug("Harvesting the property path")
        # get the uri to harvest by getting
        # the first element of the path trajectory
        uri = self.rdf_store_access.select_subjects_for_ppath(
            self.subject,
            self.path_for_depth,
            self.NSM,
        )[0]

        log.debug(f"uri: {self._subject_str_check(uri)}")
        self._harvest_uri(self._subject_str_check(uri))
