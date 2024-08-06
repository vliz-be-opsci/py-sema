from typing import Dict, List

import requests
from conftest import log
from requests.models import Response
from uritemplate import URITemplate

from sema.discovery.linkheaders import extract_link_headers


def test_link_headers():
    some_headers: List = list(
        (
            list(
                (
                    dict(
                        link="http://example.org",
                        rel="describedby",
                    ),
                    dict(
                        link="/relative-other/",
                        rel="other",
                    ),
                )
            ),
            list(
                (
                    dict(
                        link="/rel-describedby/",
                        rel="describedby",
                    ),
                )
            ),
        )
    )
    httpbin_params: Dict = dict(
        Link=", ".join(
            [
                "; ".join(
                    [f"<{ldef['link']}>; rel={ldef['rel']}" for ldef in llist]
                )
                for llist in some_headers
            ]
        )
    )
    log.debug(f"using {httpbin_params=}")
    httpbin_header_template = URITemplate(
        "https://httpbin.org/response-headers{?Link*}"
    )
    httpbin_url = httpbin_header_template.expand(httpbin_params)
    log.debug(f"requesting {httpbin_url=}")

    response: Response = requests.get(httpbin_url)
    assert isinstance(response, Response)
    assert response.ok, f"httpbin response not ok: {response.status_code=}"
    log.debug(f"{response.url=}")

    received_headers = extract_link_headers(response, rel="describedby")
    log.debug(f"{received_headers=}")

    assert received_headers == {
        "http://example.org",
        "https://httpbin.org/rel-describedby/",
    }
