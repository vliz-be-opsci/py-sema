import pytest
from conftest import log

from sema.commons.web.conneg_cli import SemaArgsParser, get_arg_parser, main


@pytest.mark.parametrize(
    "args_line, expected",
    [
        ("-v text/turtle", {"request_variants": "text/turtle"}),
        (
            (
                "-v text/turtle;"
                "http://example.org#prof-ttl,application/ld+json "
                "-o -"
            ),
            {
                "request_variants": (
                    "text/turtle;"
                    "http://example.org#prof-ttl,application/ld+json"
                ),
                "output": "-",
            },
        ),
        (
            (
                "http://example.org/ "
                "-v text/turtle,application/ld+json;"
                "http://example.org#prof-jsonld "
                "-v application/json;http://example.org#prof-json"
            ),
            {
                "request_variants": (
                    "text/turtle,application/ld+json;"
                    "http://example.org#prof-jsonld,"
                    "application/json;http://example.org#prof-json"
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
    args["request_variants"] = SemaArgsParser.args_joined(
        args["request_variants"]
    )
    assert set(expected.items()).issubset(set(args.items()))


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
    url = "https://marineinfo.org/id/person/38476"
    output_format = "csv"
    cli_line = f"{url} -o - -f {output_format}"
    success: bool = main(*cli_line.split())
    assert success
    out, err = capfd.readouterr()
    assert len(out) > 0
    # TODO parse the csv output and check some of the expected outcome
    log.debug(out)
