import pytest
from rdflib import Graph

from sema.discovery.__main__ import (
    SemaArgsParser,
    get_arg_parser,
    main,
    normalise_mime_type_requests,
)


@pytest.mark.parametrize(
    "args_line, expected",
    [
        ("-m text/turtle", {"request_mimes": "text/turtle"}),
        (
            "-m text/turtle,application/ld+json -o -",
            {
                "request_mimes": "text/turtle,application/ld+json",
                "output": "-",
            },
        ),
        (
            (
                "http://example.org/ "
                "-m text/turtle,application/ld+json -m application/json"
            ),
            {
                "request_mimes": (
                    "text/turtle,application/ld+json,application/json"
                ),
                "url": "http://example.org/",
            },
        ),
    ],
)
def test_args(args_line, expected):
    parser = get_arg_parser()
    assert parser is not None
    ns = parser.parse_args(args_line.split(" "))
    args = vars(ns)
    args["request_mimes"] = SemaArgsParser.args_joined(args["request_mimes"])
    assert set(expected.items()).issubset(set(args.items()))


@pytest.mark.parametrize(
    "args_line, expected",
    [
        ("-m turtle", {"text/turtle"}),
        ("-m ttl", {"text/turtle"}),
        ("-m file.ttl", {"text/turtle"}),
        ("-m text/turtle,ttl,turtle", {"text/turtle"}),
        ("-m json-ld", {"application/ld+json"}),
        ("-m json", {"application/json"}),
        ("-m xml", {"application/rdf+xml"}),
        ("-m html", {"text/html"}),
        ("-m html,xml", {"text/html", "application/rdf+xml"}),
        ("-m json,html", {"application/json", "text/html"}),
        (
            "-m xml,html -m json",
            {"application/json", "text/html", "application/rdf+xml"},
        ),
        ("-m json-ld -m json", {"application/ld+json", "application/json"}),
    ],
)
def test_normalise_mime_type_requests(args_line, expected):
    parser = get_arg_parser()
    ns = parser.parse_args(args_line.split(" "))
    result = normalise_mime_type_requests(ns.request_mimes)
    assert set(result.split(",")) == expected


def test_help(capfd):
    help_line: str = "--help"
    with pytest.raises(SystemExit) as caught:
        success: bool = main(*help_line.split())
        assert not success
        assert caught.value.code == 0
        assert caught.type == SystemExit
    out, err = capfd.readouterr()
    assert len(out) > 0
    assert out.startswith("usage: ")


def test_cli(capfd):
    subject_uri = "http://data.emobon.embrc.eu/"
    output_format = "json-ld"
    cli_line = f"{subject_uri} -o - -f {output_format}"
    success: bool = main(*cli_line.split())
    assert success
    out, err = capfd.readouterr()
    assert len(out) > 0
    g = Graph().parse(data=out, format=output_format)
    assert len(g) > 0


@pytest.mark.parametrize(
    "switch, expected_success", [("-z", True), ("", False)]
)
def test_cli_no_triples(capfd, switch, expected_success):
    subject_uri = "http://www.vliz.be"  # there are no triples here
    cli_line = f"{subject_uri} {switch}"
    success: bool = main(*cli_line.split())
    assert success == expected_success
    out, err = capfd.readouterr()
    assert len(out) == 0
