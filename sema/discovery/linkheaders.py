from logging import getLogger
from typing import Set
from urllib.parse import urljoin

from requests.models import Response

log = getLogger(__name__)


def extract_link_headers(resp: Response, rel=None) -> Set[str]:
    """Extract the links from the HTTP headers of the response."""
    baseurl: str = resp.url
    link_header = resp.headers.get("Link", None)
    if link_header is None:
        log.debug(f"no link header at {baseurl=}")
        return None
    # else
    log.debug(f"extracting links from {link_header=}")
    links = set()
    for link_str in link_header.split(","):
        link, *remainder = link_str.split(";")
        link = link.strip("<> ")
        remainder = "|".join([part.strip() for part in remainder])
        if rel is None or f"rel={rel}" in remainder:
            log.debug(f"adding matching link {link=} relative to {baseurl=}")
            links.add(urljoin(baseurl, link))
    log.debug(f"extracted {links=} from {baseurl=}")
    return links
