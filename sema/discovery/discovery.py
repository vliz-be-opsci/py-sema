import cgi
from logging import getLogger
from typing import Iterable, List, Tuple
from urllib.parse import urljoin

from rdflib import Graph
from requests import Session
from requests.adapters import HTTPAdapter
from requests.models import Response
from urllib3.util.retry import Retry

from sema.commons.clean import check_valid_url
from sema.commons.fileformats import format_from_filepath, mime_to_format
from sema.commons.service import ServiceBase, ServiceResult, ServiceTrace
from sema.commons.store import create_rdf_store

from .lod_html_parser import LODAwareHTMLParser

log = getLogger(__name__)


class DiscoveryResult(ServiceResult):
    """Result of the discovery service"""

    def __init__(self):
        self._graph = Graph()

    @property
    def graph(self) -> Graph:
        return self._graph

    def __len__(self) -> int:
        return len(self._graph)

    @property
    def success(self) -> bool:
        return len(self) > 0


class DiscoveryTrace(ServiceTrace):
    """Trace of the discovery service"""

    def toProv(self):
        pass  # TODO - exportessential traces into prov-o format // see #63


class DiscoveryService(ServiceBase):
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
            self._output_format = output_format or format_from_filepath(
                output_file
            )

        # state intialization
        self._result, self._trace = None, None

    SUPPORTED_MIMETYPES = {
        "application/ld+json",
        "text/turtle",
        "application/json",
    }

    @staticmethod
    def make_http_session():
        """Create a requests session with retry logic"""
        total_retry = 8
        session = Session()
        retry = Retry(
            total=total_retry,
            backoff_factor=0.4,
            status_forcelist=[500, 502, 503, 504, 429],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    @property
    def session(self):
        """Access to reusable http session fro executing requests"""
        if not hasattr(self, "_session"):
            self._session = self.make_http_session()
        return self._session

    @property
    def triples_found(self):
        return self._result.success

    def _make_response(self, url: str, req_mime_type: str = None) -> Response:
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
            self._result._graph.parse(
                data=content, format=format, publicID=source_url
            )
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
        log.debug(f"got {resp.status_code=} {resp_mime_type=}")
        # add triples from the response content
        if self._add_triples_from_text(resp.text, resp_mime_type, resp.url):
            return  # we are done
        # else
        # TODO retrieve FAIR-Signpost link from Header
        # else
        if resp_mime_type == "text/html":
            parser = LODAwareHTMLParser()
            parser.feed(resp.text)
            log.info(f"found {len(parser.links)} links in the html file")
            # TODO this does not seem to consider links from the http headers?
            for alt_url in parser.links:
                # check first if the link is absolute or relative
                if alt_url.startswith("http"):
                    alt_abs_url = alt_url
                else:
                    # Resolve the relative URL to an absolute URL
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

    def _get_structured_content(
        self, url: str, req_mime_type: str = None
    ) -> None:
        resp: Response = self._make_response(url, req_mime_type)
        # TODO trace and deal with non-triple content
        if resp is None:
            return  # nothing to extract
        # else
        self._extract_triples_from_response(resp)

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
        for mt in force_types:
            self._get_structured_content(target_url, mt)
        if self.triples_found:
            return  # we are done
        # else

        # -- strategy #02 do the basic thing
        # i.e. do the plan - no conneg request
        self._get_structured_content(target_url)
        if self.triples_found:
            return  # we are done
        # else

        # -- strategy #03 do what we can
        # i.e. go on and conneg over remaining known RDF mime-types
        # in this case we stop as soon as we find some triples
        for mt in set(self.SUPPORTED_MIMETYPES) - set(self.request_mimes):
            self._get_structured_content(target_url, mt)
            if self.triples_found:
                return  # we are done

        # -- strategy #04 do final attempt like humans
        # i.e. just grab what we can get from a text/html request
        self._get_structured_content(target_url, "text/html")

    def _output_result(self):
        g = self._result.graph
        if self._store:
            self._store.add_graph(g, self._named_graph)

        if self._output_file:
            # TODO cover export to stdout requested as output_file == "-"
            g.serialize(self._output_file, format=self._output_format)

    def process(self) -> Tuple[ServiceResult, ServiceTrace]:
        assert self._result is None, "Service has already been executed"

        self._result = DiscoveryResult()
        self._trace = DiscoveryTrace()

        try:
            self._discover_subject()
            self._output_result()
            self._result._success = True
        except Exception as e:
            log.exception(
                f"Error during discovery of {self.subject_uri}", exc_info=e
            )

        return self._result, self._trace


def discover_subject(subject_url: str, mimetypes: List[str] = []):
    service = DiscoveryService(
        subject_uri=subject_url,
        request_mimes=",".join(mimetypes),
    )

    r, t = service.process()
    return r.graph if r else None