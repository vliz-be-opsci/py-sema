import logging

from conftest import run_single_test

from sema.commons.log.loader import load_log_config
from sema.discovery.lod_html_parser import LODAwareHTMLParser

load_log_config()
log = logging.getLogger(__name__)


def test_init():
    parser = LODAwareHTMLParser()
    assert parser.links == []
    assert parser.scripts == []
    assert parser.in_script is False
    assert parser.type is None


def test_handle_starttag():
    parser = LODAwareHTMLParser()
    parser.handle_starttag(
        "link", [("rel", "describedby"), ("href", "example.com")]
    )
    assert parser.links == ["example.com"]
    assert parser.scripts == []
    assert parser.in_script is False
    assert parser.type is None

    parser.handle_starttag("script", [("type", "application/ld+json")])
    assert parser.links == ["example.com"]
    assert parser.scripts == []
    assert parser.in_script is True
    assert parser.type == "application/ld+json"

    parser.handle_starttag("script", [("type", "text/turtle")])
    assert parser.links == ["example.com"]
    assert parser.scripts == []
    assert parser.in_script is True
    assert parser.type == "text/turtle"

    parser.handle_starttag("div", [])
    assert parser.links == ["example.com"]
    assert parser.scripts == []
    assert parser.in_script is True
    assert parser.type == "text/turtle"


def test_handle_endtag():
    parser = LODAwareHTMLParser()
    parser.in_script = True
    parser.type = "application/ld+json"
    parser.handle_endtag("script")
    assert parser.in_script is False

    parser.in_script = True
    parser.type = "text/turtle"
    parser.handle_endtag("script")
    assert parser.in_script is False

    parser.in_script = False
    parser.type = None
    parser.handle_endtag("script")
    assert parser.in_script is False


def test_handle_data():
    parser = LODAwareHTMLParser()
    parser.in_script = True
    parser.type = "application/ld+json"
    parser.handle_data('{"name": "John Doe"}')
    assert parser.scripts == [{"application/ld+json": '{"name": "John Doe"}'}]

    parser.in_script = True
    parser.type = "text/turtle"
    parser.handle_data(
        "<http://example.org/subject> "
        "<http://example.org/predicate> "
        '"Object" .'
    )
    assert parser.scripts == [
        {"application/ld+json": '{"name": "John Doe"}'},
        {
            "text/turtle": "<http://example.org/subject> "
            "<http://example.org/predicate> "
            '"Object" .'
        },
    ]

    parser.in_script = False
    parser.type = None
    parser.handle_data("Some random data")
    assert parser.scripts == [
        {"application/ld+json": '{"name": "John Doe"}'},
        {
            "text/turtle": "<http://example.org/subject> "
            "<http://example.org/predicate> "
            '"Object" .'
        },
    ]


if __name__ == "__main__":
    run_single_test(__file__)
