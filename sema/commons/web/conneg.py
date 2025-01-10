import cgi
from logging import getLogger
from pathlib import Path
from typing import Any, Dict, List, Tuple

from rdflib import Graph
from requests.exceptions import RetryError
from requests.models import Response
from urllib3.exceptions import ResponseError

from sema.commons.clean import check_valid_url
from sema.commons.fileformats import mime_to_format
from sema.commons.service import (
    ServiceBase,
    ServiceResult,
    StatusMonitor,
    Trace,
)

from .download_to_file import save_web_content
from .httpsession import make_http_session

log = getLogger(__name__)


class FoundVariants(ServiceResult, StatusMonitor):
    """Result of the conneg evaluation service"""

    def __init__(self, requested: List[Tuple[str, str]]) -> None:
        self.requested = requested or []
        self.detected = []
        self.variants: Dict[Tuple[str, str], Dict[str, Any]] = {}

    def set_detected(self, detected: List[Tuple[str, str]]):
        self.detected = detected or []

    def add_variant(
        self, *, mime_type: str, profile: str, response: Response | None = None
    ) -> None:
        key = (mime_type or "", profile or "")
        assert key not in self.variants, f"Variant {key} already added"
        response_mime = (
            cgi.parse_header(response.headers["Content-Type"])[0]
            if response
            else None
        )
        cdispval, cdispparams = cgi.parse_header(
            response.headers.get("Content-Disposition", "")  # type: ignore
        )
        cdispfile = (
            cdispparams.get("filename") if cdispval == "attachment" else None
        )

        self.variants[key] = dict(
            mime_type=mime_type,
            profile=profile,
            inRequested=bool(key in self.requested),
            inDetected=bool(key in self.detected),
            response=response,
            content=response.text if response else None,
            status=response.status_code if response else None,
            match_mime=bool(mime_type == response_mime) if response else None,
            filename=cdispfile if response else None,
        )

    @property
    def success(self) -> bool:
        expected_unique_variants = set(self.requested + self.detected)
        # success requires
        return expected_unique_variants == self.variants.keys() and all(
            v["status"] == 200 for v in self.variants.values()
        )

    @property
    def status(self) -> int:
        return len(self)

    def __len__(self) -> int:
        return len(self.variants)

    def __str__(self) -> str:
        out = "#FoundVariants:\n"
        out += f"#  requested: #{len(self.requested)}\n"
        out += f"#  detected : #{len(self.detected)}\n"
        out += f"#  variants : #{len(self.variants)}\n"
        out += f"#-----\n{self.as_csv()}"
        return out

    def as_csv(self: "FoundVariants", url: str | None = None) -> str:
        out = ""
        outfields = [
            "mime_type",
            "profile",
            "inRequested",
            "inDetected",
            "status",
            "match_mime",
            "filename",
        ]
        out += "url," if url else ""
        out += ",".join(outfields) + "\n"
        for v in self.variants.values():
            out += f"{url}," if url else ""
            out += ",".join(str(v[fld]) for fld in outfields) + "\n"
        return out


class ConnegEvaluation(ServiceBase):
    def __init__(
        self,
        *,
        url: str,
        request_variants: List[Tuple[str, str]] | None = None,
    ) -> None:
        """Initialize the conneg evaluation service.
        @param url: URL of the resource to evaulate
        @param request_variants: comma separated list of semicol separated
           "mime_type;profile" tuples describing the requested variants
        """
        # upfront checks
        assert url, f"{url=} required"
        assert check_valid_url(url), f"{url=} not valid"

        # actual task inputs
        self.url = url
        # split string to list of tuples
        request_variants = (
            [
                (mt.strip(), pf.strip())
                for mt, pf in (  # since profile is optional, we:
                    (v + ";").split(";")[:2]  # force semicolon and keep only 2
                    for v in request_variants.split(",")  # type: ignore
                )
            ]
            if request_variants
            else []
        )

        # internal state
        self._found = FoundVariants(request_variants)

    @property
    def session(self):
        """Access to reusable http session for executing requests"""
        if not hasattr(self, "_session"):
            self._session = make_http_session()
        return self._session

    def _get_variant_response(
        self, mime_type: str | None = None, profile: str | None = None
    ) -> Response | None:
        """Get the content of the resource with the requested variant"""
        headers = dict()
        if mime_type:
            headers["Accept"] = mime_type
        if profile:
            headers["Accept-profile"] = profile
        log.debug(f"requesting {self.url} with {headers=}")
        try:
            resp = self.session.get(self.url, headers=headers)
        except (ResponseError, RetryError) as e:
            log.exception(
                f"FAILED request {self.url} with {headers=} ", exc_info=e
            )
            return None

        log.debug(f"request for {self.url} ended at {resp.url}")
        if not resp.ok:
            log.debug(
                f"FAILED request {self.url} with {headers=} "
                f"> {resp.status_code}"
            )
            return None
        # else
        return resp

    @staticmethod
    def variants_query(url: str) -> str:
        return f"""
prefix altr: <http://www.w3.org/ns/dx/conneg/altr#>
prefix dct: <http://purl.org/dc/terms/>
SELECT ?mime ?profile WHERE {{
  bind(<{url}> as ?url)
  ?url altr:hasRepresentation ?repr.
  ?repr a altr:Representation.
  OPTIONAL{{ ?repr dct:format ?mime .}}
  OPTIONAL{{ ?repr dct:conformsTo ?profile .}}
}}
"""

    def _detect_variants(self) -> None:
        """Detect the available variants for the resource"""
        resp = self._get_variant_response(
            "text/turtle", "http://www.w3.org/ns/dx/conneg/altr"
        )
        if resp is None:
            log.debug(f"no variants detected for {self.url}")
            return
        # else
        mime_type, options = cgi.parse_header(resp.headers["Content-Type"])
        fmt = mime_to_format(mime_type)
        if fmt not in ["turtle", "n3", "json-ld"]:
            log.debug(f"unsupported format {fmt=} for {self.url}")
            return
        # else
        g = Graph().parse(data=resp.text, format=fmt, publicID=resp.url)
        log.debug(
            f"for {self.url} found variants >>\n{g.serialize(format='turtle')}"
        )
        sparql = self.variants_query(self.url)
        matches: List[Tuple[str]] = [
            tuple(str(u) for u in r) for r in g.query(sparql)  # type: ignore
        ]
        log.debug(f"for {self.url} parsed variants >>\n{matches} ")
        self._found.set_detected(matches)  # type: ignore

    def _check_variants(self):
        """Check the available variants against the requested variants"""
        already_done = set()
        # go over the requested variants, then the remaining detected variants
        for mime_type, profile in self._found.requested + self._found.detected:
            if (mime_type, profile) in already_done:
                continue
            already_done.add((mime_type, profile))
            resp = self._get_variant_response(mime_type, profile)
            self._found.add_variant(
                mime_type=mime_type, profile=profile, response=resp
            )

    @Trace.init(Trace)
    def process(self) -> FoundVariants:
        self._detect_variants()
        self._check_variants()
        return self._found

    def export_result(
        self, output_ref: str, format: str | None = None
    ) -> None:
        """Export the result to the output"""
        output_ref = output_ref or "-"
        format = format or "csv"
        assert format == "csv", "currently only csv output is supported"

        csv = self._found.as_csv(self.url)
        if output_ref == "-":
            return print(csv)
        # else
        output_path = Path(output_ref)
        log.debug(f"appending csv result for {self.url} to {output_path}")
        with open(output_path, "a") as out:
            out.write(csv)

    def dump_variants(self, dump_path: str) -> None:
        """Dump the obtained variants to the path"""
        dump_path_path = Path(dump_path)
        dump_path_path.mkdir(parents=True, exist_ok=True)
        variant_filenames = [
            v["filename"]
            for v in self._found.variants.values()
            if v["filename"]
        ]
        all_unique_filenames = bool(
            len(set(variant_filenames)) == len(variant_filenames)
        )
        for v in self._found.variants.values():
            content = v["content"]
            if not v["content"]:
                continue
            # else
            save_web_content(
                dump_path_path,
                v["filename"] if all_unique_filenames else None,
                self.url,
                v["mime_type"],
                v["profile"],
                content,
            )
