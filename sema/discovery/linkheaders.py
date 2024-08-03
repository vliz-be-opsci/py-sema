from typing import Set
from requests.models import Response
from urllib.parse import urljoin
from logging import getLogger


log = getLogger(__name__)


def extract_link_headers(resp: Response, rel=None) -> Set[str]:
    """Extract the links from the HTTP headers of the response."""
    link_header = resp.headers.get("Link", None)
    if link_header is None:
        return None
    # else
    baseurl: str = resp.url
    log.debug(f"extracting links from {link_header=}")
    links = set()
    for link_str in link_header.split(","):
        link, *remainder = link_str.split(";")
        link = link.strip("<> ")
        remainder = '|'.join([part.strip() for part in remainder])
        if rel is None or f"rel={rel}" in remainder:
            log.debug(f"adding matching link {link=} relative to {baseurl=}")
            links.add(urljoin(baseurl, link))

    return links
