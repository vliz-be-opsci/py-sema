import pytest
from conftest import log
from rdflib import Graph

from sema.commons.web import ConnegEvaluation, FoundVariants


@pytest.mark.parametrize(
    "variant_str, expected",
    (
        (None, []),
        ("", []),
        ("mt", [("mt", "")]),
        ("mt;pr", [("mt", "pr")]),
        ("m1;p1,m2,m3;p3", [("m1", "p1"), ("m2", ""), ("m3", "p3")]),
        ("m1,m2,m3", [("m1", ""), ("m2", ""), ("m3", "")]),
        ("mt", [("mt", "")]),
        ("mt;pr", [("mt", "pr")]),
        ("m1;p1,m2,m3;p3", [("m1", "p1"), ("m2", ""), ("m3", "p3")]),
        ("m1,m2;p2,m3", [("m1", ""), ("m2", "p2"), ("m3", "")]),
        ("m1,m2,m3", [("m1", ""), ("m2", ""), ("m3", "")]),
    ),
)
def test_variant_parsing(variant_str, expected):
    ce = ConnegEvaluation(
        url="http://example.com", request_variants=variant_str
    )
    assert ce._found.requested == expected


def expected_marine_info_variants(type_id: str):
    return {
        ("text/html", "https://marineinfo.org/ns/profile#default", None),
        (
            "text/xml",
            "https://marineinfo.org/ns/profile#default",
            f"-{type_id}.xml",
        ),
        (
            "text/turtle",
            "https://marineinfo.org/ns/profile#default",
            f"-{type_id}.ttl",
        ),
        (
            "application/json",
            "https://marineinfo.org/ns/profile#default",
            f"-{type_id}.json",
        ),
        (
            "application/ld+json",
            "https://marineinfo.org/ns/profile#default",
            f"-{type_id}.jsonld",
        ),
        (
            "text/html",
            "http://www.w3.org/ns/dx/conneg/altr",
            None,
        ),
        (
            "text/turtle",
            "http://www.w3.org/ns/dx/conneg/altr",
            f"-{type_id}-alt.ttl",
        ),
    }


@pytest.mark.parametrize(
    "url, expected",
    (
        (
            "https://marineinfo.org/id/person/38476",
            expected_marine_info_variants("person-38476"),
        ),
        (
            "https://marineinfo.org/id/collection/619",
            expected_marine_info_variants("collection-619"),
        ),
        (
            "https://marineinfo.org/id/institute/36",
            expected_marine_info_variants("institute-36"),
        ),
        (
            "https://marineinfo.org/id/project/5315",
            expected_marine_info_variants("project-5315"),
        ),
        # inclusion of test blocked by ttl formatting issue in marineinfo
        # - see https://vliz.atlassian.net/browse/IMIS-1805
        # (
        #     "https://marineinfo.org/id/publication/307837",
        #     expected_marine_info_variants("publication-307837"),
        # ),
        # inclusion of test is blocked by conneg issue in marineinfo
        # - see https://vliz.atlassian.net/browse/IMIS-1806
        # (
        #     "https://marineinfo.org/id/dataset/90",
        #     expected_marine_info_variants("dataset-90")
        #     | {
        #         (
        #             "text/xml",
        #             "https://marineinfo.org/ns/profile#gcmd",
        #             "-dataset-90-gcmd.xml",
        #         ),
        #         (
        #             "text/xml",
        #             "https://marineinfo.org/ns/profile#inspire",
        #             "-dataset-90-inspire.xml",
        #         ),
        #         (
        #             "text/xml",
        #             "https://marineinfo.org/ns/profile#eml-2.1.1",
        #             "-dataset-90-eml2.1.1.xml",
        #         ),
        #         (
        #             "text/xml",
        #             "https://marineinfo.org/ns/profile#eml-2.2.0",
        #             "-dataset-90-eml2.2.0.xml",
        #         ),
        #     },
        # ),
        (
            "http://vocab.nerc.ac.uk/collection/S25/current/BE006521/",
            {
                ("application/ld+json", "https://schema.org", None),
                ("application/n-triples", "https://schema.org", None),
                ("application/rdf+xml", "https://schema.org", None),
                ("text/turtle", "https://schema.org", None),
                (
                    "application/ld+json",
                    "https://w3id.org/profile/vocpub",
                    None,
                ),
                (
                    "application/n-triples",
                    "https://w3id.org/profile/vocpub",
                    None,
                ),
                (
                    "application/rdf+xml",
                    "https://w3id.org/profile/vocpub",
                    None,
                ),
                ("text/turtle", "https://w3id.org/profile/vocpub", None),
                (
                    "application/ld+json",
                    "https://w3id.org/profile/nvs-col",
                    None,
                ),
                (
                    "application/n-triples",
                    "https://w3id.org/profile/nvs-col",
                    None,
                ),
                (
                    "application/rdf+xml",
                    "https://w3id.org/profile/nvs-col",
                    None,
                ),
                ("text/turtle", "https://w3id.org/profile/nvs-col", None),
                ("text/html", "https://w3id.org/profile/nvs-col", None),
                (
                    "application/ld+json",
                    "https://www.w3.org/TR/skos-reference/",
                    None,
                ),
                (
                    "application/n-triples",
                    "https://www.w3.org/TR/skos-reference/",
                    None,
                ),
                (
                    "application/rdf+xml",
                    "https://www.w3.org/TR/skos-reference/",
                    None,
                ),
                ("text/turtle", "https://www.w3.org/TR/skos-reference/", None),
                (
                    "application/json",
                    "http://www.w3.org/ns/dx/conneg/altr",
                    None,
                ),
                (
                    "application/ld+json",
                    "http://www.w3.org/ns/dx/conneg/altr",
                    None,
                ),
                (
                    "application/n-triples",
                    "http://www.w3.org/ns/dx/conneg/altr",
                    None,
                ),
                (
                    "application/rdf+xml",
                    "http://www.w3.org/ns/dx/conneg/altr",
                    None,
                ),
                ("text/html", "http://www.w3.org/ns/dx/conneg/altr", None),
                ("text/turtle", "http://www.w3.org/ns/dx/conneg/altr", None),
            },
        ),
    ),
)
def test_conneg_eval(url, expected):
    # repeating the test without any and with all ...
    # ... expected variants in the request_variants
    for use_request_variants in (False, True):

        request_variants = (
            ",".join(f"{mt};{pf}" for mt, pf, _ in expected)
            if use_request_variants
            else None
        )
        ce: ConnegEvaluation = ConnegEvaluation(
            url=url, request_variants=request_variants
        )

        result: FoundVariants = ce.process()
        log.debug(f"RESULT: {bool(result)=} {len(result)=} {str(result)=}")

        assert result, f"For {url} :: Expected a positive result, got {result}"

        assert len(result) > 0, (
            f"For {url} :: Expected at least one variant, "
            "probably detection is broken."
        )
        assert len(result) == len(expected), (
            f"For {url} :: Expected {len(expected)} variants, "
            f"got {len(result)} in stead."
        )

        for exp_mime, exp_profile, exp_suffix in expected:
            variant_key = (exp_mime, exp_profile)
            assert variant_key in result.variants
            variant = result.variants[variant_key]
            assert variant["status"] == 200  # already part of bool(result)
            assert (
                variant["profile"] == exp_profile
            ), f"Expected {exp_profile=}, got {variant['profile']=}"
            assert (
                variant["mime_type"] == exp_mime
            ), f"Expected {exp_mime=}, got {variant['mime_type']=}"
            assert variant["match_mime"] is True, "MIME type mismatch"
            assert variant["inRequested"] is use_request_variants, (
                f"the {variant_key} "
                f"should {'' if use_request_variants else 'not'} "
                "be inRequested"
            )
            assert (
                variant["inDetected"] is True
            ), f"the {variant_key} should always be inDetected"

            filename = variant["filename"]
            if exp_suffix is None:
                assert (
                    filename is None
                ), f"Not expected to have {filename=} for {url} {exp_suffix=}"
            else:
                assert (
                    filename is not None
                ), f"Missing filename for {url},{exp_mime},{exp_profile} {exp_suffix=}"
                assert filename.endswith(
                    exp_suffix
                ), f"{filename=} for {url},{exp_mime},{exp_profile} not ending with {exp_suffix=}"

            if exp_mime in {"text/turtle", "application/ld+json"}:
                try:
                    g = Graph().parse(
                        data=variant["content"],
                        format=exp_mime,
                        publicID=variant["response"].url,
                    )
                    assert len(g) > 0, (
                        f"Empty graph for {(exp_mime, exp_profile)} "
                        f"variant for {url}"
                    )
                except Exception as e:
                    log.exception(
                        f"FAILED to parse {exp_mime} variant for {url}",
                        exc_info=e,
                    )
                    log.debug(
                        f"FAILING CONTENT:\n--\n{variant['content']}\n--"
                    )
                    assert (
                        False
                    ), f"FAILED to parse {exp_mime} variant for {url}"
