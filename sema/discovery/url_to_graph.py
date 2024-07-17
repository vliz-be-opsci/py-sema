import cgi
import logging
from urllib.parse import urljoin

import requests
from rdflib import Graph
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .lod_html_parser import LODAwareHTMLParser

log = logging.getLogger(__name__)

RDF_MIME_TO_FORMAT = {
    "application/ld+json": "json-ld",
    "text/turtle": "turtle",
}


def ctype_to_rdf_format(ctype: str) -> str:
    return RDF_MIME_TO_FORMAT.get(ctype, None)


def get_graph_for_format(subject_url: str, formats: str, graph: Graph = None):
    """
    Discover triples describing the subject (assumed at subject_url)
    and add them to the graph

    :param subject_url: url (originally assumed from <uri>)
    pointing to the subject to be discovered
    :type subject_url: str
    :param g: graph to be filled
    :type g: rdflib.Graph
    :param format: indicating what format should be retrieved json-ld, turtle
    :type form: str
    :returns: the graph whith added discovered triples
    :rtype: rdflib.Graph
    """

    if subject_url is None:
        return None

    if graph is None:
        graph = Graph()  # create a fresh graph if you don't have it yet

    total_retry = 8
    session = requests.Session()
    retry = Retry(
        total=total_retry,
        backoff_factor=0.4,
        status_forcelist=[500, 502, 503, 504, 429],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    triples_found = False

    ACCEPTABLE_MIMETYPES = {
        "application/ld+json",
        "text/turtle",
        "application/json",
    }

    for format in formats:
        headers = {"Accept": format}
        log.debug(f"requesting {subject_url} with {headers=}")
        r = session.get(subject_url, headers=headers)
        mime_type, options = cgi.parse_header(r.headers.get("Content-Type", None))
        log.debug(f"got {r.status_code=} {mime_type=}")

        if r.status_code == 200 and bool(mime_type in ACCEPTABLE_MIMETYPES):
            triples_found = True
            try:
                # if mimetype is application/json assume application/ld+json
                # to satisfy the known formats of rdflib.parser
                if mime_type == "application/json":
                    mime_type = "application/ld+json"
                if mime_type == "application/octet-stream":
                    mime_type = "text/turtle"
                graph.parse(
                    data=r.text, format=mime_type, publicID=subject_url
                )

            except Exception as e:
                log.warning(
                    f"failed to parse {subject_url} in {format=} error: {e}"
                )

            finally:
                return graph

    if not triples_found:
        # perform a check in the html to
        # see if there is any link to fair signposting
        # perform request to uri with accept header text/html
        headers = {"Accept": "text/html"}
        r = session.get(subject_url, headers=headers)
        if r.status_code == 200 and "text/html" in r.headers["Content-Type"]:
            # parse the html and check if there is any link to fair signposting
            # if there is then download it to the triplestore
            log.info(f"content of {subject_url} is html")
            # go over the html file and find all the links in the head section
            # and check if there is any links with rel="describedby" anf if so
            # then follow it and download it to the triplestore

            parser = LODAwareHTMLParser()
            parser.feed(r.text)
            log.info(f"found {len(parser.links)} links in the html file")
            graph = Graph()
            for alt_url in parser.links:
                # check first if the link is absolute or relative
                if alt_url.startswith("http"):
                    alt_abs_url = alt_url
                else:
                    # Resolve the relative URL to an absolute URL
                    alt_abs_url = urljoin(subject_url, alt_url)
                # use this linked uri as the alternative for this subect
                # determine the format of the file and use the correct parser
                try:
                    graph = graph + get_graph_for_format(
                        alt_abs_url, formats=ACCEPTABLE_MIMETYPES
                    )

                except Exception as e:
                    log.warning(
                        f"failed to get {alt_abs_url} in {format=} error: {e}"
                    )

            for script in parser.scripts:
                # parse the script and check if it is json-ld or turtle
                # if so then add it to the triplestore
                log.info(f"script: {script}")
                # { 'application/ld+json': '...'} | {'text/turtle': '...'}
                for ctype, content in script.items():
                    cformat: str = ctype_to_rdf_format(ctype)
                    if format is None:  # ctype is not known as rdf-format
                        continue  # skip
                    log.info(f"found script with rdf {ctype=}, {cformat=}")
                    graph.parse(
                        data=content, format=cformat, publicID=subject_url
                    )

            parser.close()
            return graph
        log.warning(
            f"request for {subject_url} failed "
            f"with status code {r.status_code} "
            f"and content type {r.headers['Content-Type']}"
        )

    return None
