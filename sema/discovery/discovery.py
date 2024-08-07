import cgi
from logging import getLogger
from typing import Iterable, List
from urllib.parse import urljoin

from rdflib import Graph
from requests.models import Response

from sema.commons.clean import check_valid_url
from sema.commons.fileformats import format_from_filepath, mime_to_format
from sema.commons.service import (
    ServiceBase,
    ServiceResult,
    StatusMonitor,
    Trace,
)
from sema.commons.store import create_rdf_store
from sema.commons.web import make_http_session

from .linkheaders import extract_link_headers
from .lod_html_parser import LODAwareHTMLParser

log = getLogger(__name__)


class DiscoveryResult(ServiceResult, StatusMonitor):
    """Result of the discovery service"""

    def __init__(self):
        self._graph = Graph()

    @property
    def graph(self) -> Graph:
        return self._graph

    def __len__(self) -> int:
        return len(self.graph)

    @property
    def status(self) -> int:
        return len(self)

    @property
    def success(self) -> bool:
        return self.status > 0


class Discovery(ServiceBase):
    def __init__(
        self,
        *,
        subject_uri: str,
        request_mimes: str = None,
        read_uri: str = None,
        write_uri: str = None,
        named_graph: str = None,
        output_file: str = None,
        output_format: str = None,
    ):
        # upfront checks
        assert subject_uri, f"{subject_uri=} required"
        assert check_valid_url(subject_uri), f"{subject_uri=} not valid"

        # actual task inputs
        self.subject_uri = subject_uri
        self.request_mimes = (
            [mt.strip() for mt in request_mimes.split(",")]
            if request_mimes
            else []
        )

        # output options
        self._store, self._output_file = None, None
        if read_uri:
            self._store = (
                create_rdf_store(read_uri, write_uri) if read_uri else None
            )
            self._named_graph = named_graph
        if output_file:
            self._output_file = output_file
            self._output_format = (
                output_format or format_from_filepath(output_file) or "turtle"
            )

        # state intialization
        self._result = DiscoveryResult()

    SUPPORTED_MIMETYPES = {
        "application/ld+json",
        "text/turtle",
        "application/json",
    }

    @staticmethod
    def _make_http_session():
        return make_http_session()

    @property
    def session(self):
        """Access to reusable http session for executing requests"""
        if not hasattr(self, "_session"):
            self._session = self._make_http_session()
        return self._session

    @property
    def triples_found(self):
        return self._result.success

    def _make_response(self, url: str, req_mime_type: str = None) -> Response:
        """Make a request to the url and return the response"""
        headers = dict(Accept=req_mime_type) if req_mime_type else dict()
        log.debug(f"requesting {url} with {headers=}")
        resp = self.session.get(url, headers=headers)
        return resp if resp.ok else None

    def _add_triples_from_text(self, content, mimetype, source_url):
        if mimetype not in self.SUPPORTED_MIMETYPES:
            return False
        # else
        EXTRA_FORMATS = {
            "application/octet-stream": "turtle",
            "application/json": "json-ld",
        }
        format = mime_to_format(mimetype) or EXTRA_FORMATS.get(mimetype, None)
        try:
            g: Graph = Graph().parse(
                data=content, format=format, publicID=source_url
            )
            log.debug(
                f"parsed {len(g)} triples from {source_url} in {format=}"
            )
            # Note: pure application/json parsing will not fail,
            # but simply return an empty graph
            # still we attempt that case because e.g. github pages
            # will serve jsonld as json
            if len(g) == 0:
                return False
            # else
            self._result._graph += g
            return True
        except Exception as e:
            log.exception(
                f"failed to parse content from {source_url} in {format=}",
                exc_info=e,
            )
        return False

    def _extract_triples_from_response(self, resp: Response):
        # note we can be sure the response is ok, as we checked that before
        ctype_header = resp.headers.get("Content-Type", None)
        resp_mime_type, options = cgi.parse_header(ctype_header)
        log.debug(f"extract from {resp.url=} in format {resp_mime_type=}")
        # add triples from the response content
        if self._add_triples_from_text(resp.text, resp_mime_type, resp.url):
            log.debug(f"added {len(self._result)} triples from {resp.url}")
            return  # we are done
        # else
        # check for FAIR-SIGNPOST links in the headers
        links = extract_link_headers(resp, rel="describedby")
        if links is not None:
            log.debug(f"found {len(links)} signposted links in the headers")
            for alt_abs_url in links:
                self._discover_subject(alt_abs_url)
        # else
        if resp_mime_type == "text/html":
            parser = LODAwareHTMLParser()
            parser.feed(resp.text)
            log.info(f"found {len(parser.links)} links in the html file")
            for alt_url in parser.links:
                alt_abs_url = urljoin(resp.url, alt_url)
                self._discover_subject(alt_abs_url)

            for script in parser.scripts:
                # parse the script and check if it is json-ld or turtle
                # if so then add it to the triplestore
                for script_type, script_content in script.items():
                    if script_type in self.SUPPORTED_MIMETYPES:
                        self._add_triples_from_text(
                            script_content, script_type, resp.url
                        )
            parser.close()

    @Trace.by(Trace.Event)
    def _get_structured_content(
        self, url: str, req_mime_type: str = None
    ) -> Response:
        resp: Response = self._make_response(url, req_mime_type)
        if resp is None:
            return  # nothing to extract
        # else
        self._extract_triples_from_response(resp)
        return resp  # note the return will be reigstered in the event-trace

    def _discover_subject(
        self, target_url: str = None, force_types: Iterable[str] = []
    ):
        """Discover triples describing the subject (assumed at subject_url)
        and add them to the result graph, using various strategies
        """
        # we start off at the core subject_uri and try to discover that
        target_url: str = target_url or self.subject_uri
        force_types: Iterable[str] = force_types or self.request_mimes

        # TODO consider rewrite more elegantly/clearly
        #   essentially this is chain of strategies to fallback

        # -- strategy #01 do as your a told, pass forced mimes in conneg
        # i.e. go explcitely over the mime-types that are requested (if any)
        log.debug(f"discovery #01 trying {force_types=} for {target_url=}")
        for mt in force_types:
            self._get_structured_content(target_url, mt)
        if self.triples_found:
            return  # we are done
        # else

        # -- strategy #02 do the basic thing
        # i.e. do the plan - no conneg request
        log.debug(f"discovery #02 plain request for {target_url=}")
        self._get_structured_content(target_url)
        if self.triples_found:
            return  # we are done
        # else

        # -- strategy #03 do what we can
        # i.e. go on and conneg over remaining known RDF mime-types
        # in this case we stop as soon as we find some triples
        remain_types = set(self.SUPPORTED_MIMETYPES) - set(force_types)
        log.debug(f"discovery #03 trying {remain_types=} for {target_url=}")
        for mt in remain_types:
            self._get_structured_content(target_url, mt)
            if self.triples_found:
                return  # we are done

        # -- strategy #04 do final attempt like humans
        # i.e. just grab what we can get from a text/html request
        log.debug(f"discovery #04 trying text/html for {target_url=}")
        self._get_structured_content(target_url, "text/html")

    def _output_result(self):
        g = self._result.graph
        if self._store:
            self._store.add_graph(g, self._named_graph)

        if self._output_file:
            if self._output_file == "-":
                content = g.serialize(format=self._output_format)
                print(content)
            else:
                g.serialize(self._output_file, format=self._output_format)

    @Trace.init(Trace, monitor_attr="_result")
    def process(self) -> ServiceResult:
        try:
            self._discover_subject()
            log.debug(
                f"done with {self.subject_uri=} "
                f"discovered {len(self._result)} triples"
            )
            self._output_result()
            self._result._success = True
        except Exception as e:
            log.exception(
                f"Error during discovery of {self.subject_uri}", exc_info=e
            )
        return self._result

    def export_trace(self, output_path: str) -> None:
        trace: Trace = Trace.extract(self)
        log.debug(f"TODO dump {trace=} to {output_path=}")


def discover_subject(subject_url: str, mimetypes: List[str] = []):
    service = Discovery(
        subject_uri=subject_url,
        request_mimes=",".join(mimetypes),
    )

    r = service.process()
    return r.graph if r else None
