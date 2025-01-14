from logging import getLogger
from pathlib import Path
from typing import Iterable, List
from urllib.parse import urljoin

from rdflib import Graph
from requests.exceptions import RetryError
from requests.models import Response
from urllib3.exceptions import ResponseError

from sema.commons.clean import check_valid_url
from sema.commons.fileformats import format_from_filepath, mime_to_format
from sema.commons.service import (
    ServiceBase,
    ServiceResult,
    StatusMonitor,
    Trace,
)
from sema.commons.store import create_rdf_store
from sema.commons.web import (
    get_parsed_header,
    make_http_session,
    save_web_content,
)

from .linkheaders import extract_link_headers
from .lod_html_parser import LODAwareHTMLParser

log = getLogger(__name__)


class DiscoveryResult(ServiceResult, StatusMonitor):
    """Result of the discovery service"""

    def __init__(self):
        self._graph = Graph()
        self._success = False

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
        request_mimes: str | None = None,
        read_uri: str | None = None,
        write_uri: str | None = None,
        named_graph: str | None = None,
        output_file: str | None = None,
        output_format: str | None = None,
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

    def _make_response(
        self, url: str, req_mime_type: str | None = None
    ) -> Response | None:
        """Make a request to the url and return the response"""
        headers = dict(Accept=req_mime_type) if req_mime_type else dict()
        log.debug(f"requesting {url} with {headers=}")
        try:
            resp = self.session.get(url, headers=headers)
        except (ResponseError, RetryError) as e:  # if retry strategy gives up
            log.exception(f"FAILED request {url} with {headers=} ", exc_info=e)
            return None
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
        resp_mime_type, options = get_parsed_header(
            resp.headers, "Content-Type",
        )
        if not resp_mime_type:
            log.debug(f"no content-type header in {resp.url=}")
            return

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

    @Trace.by(Trace.Event, name="StructuredContentEvent")
    def _get_structured_content(
        self, url: str, req_mime_type: str | None = None
    ) -> Response | None:
        resp: Response | None = self._make_response(url, req_mime_type)
        if resp is None:
            return  # nothing to extract
        # else
        self._extract_triples_from_response(resp)
        return resp  # note the return will be reigstered in the event-trace

    def _discover_subject(
        self,
        target_url: str | None = None,  # type: ignore
        force_types: Iterable[str] = [],  # type: ignore
    ):
        """Discover triples describing the subject (assumed at subject_url)
        and add them to the result graph, using various strategies
        """
        # we start off at the core subject_uri and try to discover that
        target_url: str | None = target_url or self.subject_uri
        force_types: Iterable[str] = force_types or self.request_mimes

        # TODO consider rewrite more elegantly/clearly
        #   essentially this is chain of strategies to fallback

        # -- strategy #01 do as your a told, pass forced mimes in conneg
        # i.e. go explcitely over the mime-types that are requested (if any)
        log.debug(f"discovery #01 trying {force_types=} for " f"{target_url=}")
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
            self._store.add_graph(g, self._named_graph)  # type: ignore

        if self._output_file:
            if self._output_file == "-":
                content = g.serialize(format=self._output_format)
                print(content)
            else:
                g.serialize(self._output_file, format=self._output_format)

    @Trace.init(Trace, monitor_attr="_result")
    def process(self) -> DiscoveryResult:
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

    def export_trace(self, dump_path_str: str) -> None:
        trace: Trace = Trace.extract(self)
        assert trace is not None
        log.debug(f"dumping {len(trace.events)=} to {dump_path_str=}")
        # make dump_path folder
        dump_path = Path(dump_path_str)
        dump_path.mkdir(parents=True, exist_ok=True)

        # run over traced content and save the content + assemble outcsv
        outcsv = (
            "ts,discovery_status,url,resp_url,"
            "mime_type,response_status,content_length,dumpfile\n"
        )
        for evt_reg in trace.events:
            ts = evt_reg["ts"]
            status = evt_reg["status"]
            evt = evt_reg["event"]
            if evt.name == "StructuredContentEvent":
                # arg expansion trick: pad with [None]* minimal size,
                # and ignore any excess in *_
                url, mime_type, *_ = evt.listargs + (None,) * 2
                resp: Response = evt.returns
                resp_url = resp.url if resp else url
                resp_content = resp.text if resp else ""
                resp_status = resp.status_code if resp else None
                resp_mime = (
                    get_parsed_header(resp.headers, "Content-Type")[0]
                    if resp
                    else None
                )
                outpath = (
                    save_web_content(
                        dump_path,
                        None,
                        resp_url,
                        resp_mime or mime_type,
                        None,
                        resp_content,
                    )
                    if resp_content
                    else None
                )

                log.debug(f"saved {len(resp_content)} chars to {outpath=}")
                outcsv += (
                    f"{ts},{status},{url},{resp_url},{mime_type},"
                    f"{resp_status},{len(resp_content)},{outpath}\n"
                )

        # make csv file with the trace
        csvfile = dump_path / "trace.csv"
        with open(csvfile, "w") as f:
            f.write(outcsv)


def discover_subject(subject_url: str, mimetypes: List[str] = []):
    service = Discovery(
        subject_uri=subject_url,
        request_mimes=",".join(mimetypes),
    )

    r = service.process()
    return r.graph if r else None
