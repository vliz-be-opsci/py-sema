import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Tuple

import pytest
from conftest import log

from sema.commons.web.conneg_cli import SemaArgsParser, _main, get_arg_parser


@pytest.mark.parametrize(
    "args_line, expected",
    [
        ("http://example.org/1", {"url": "http://example.org/1"}),
        ("-u http://example.org/2", {"url_option": "http://example.org/2"}),
        ("--url http://example.org/3", {"url_option": "http://example.org/3"}),
        (
            "http://example.org/pos --url http://example.org/opt",
            {
                "url": "http://example.org/pos",
                "url_option": "http://example.org/opt",
            },
        ),
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
    expected_set = set(expected.items())
    args_set = set(args.items())
    assert expected_set.issubset(args_set), (
        f"{expected_set=} " f"not in {args_set=}"
    )


def test_help(capfd):
    help_line: str = "--help"
    with pytest.raises(SystemExit) as caught:
        success: bool = _main(*help_line.split())
        assert not success
        assert caught.value.code == 0
        assert caught.type == SystemExit
    out, err = capfd.readouterr()
    assert len(out) > 0
    assert out.startswith("usage: ")


def test_cli(capfd):
    url = "https://marineinfo.org/id/person/38476"
    output_format = "csv"
    with tempfile.TemporaryDirectory() as tmpdirname:
        cli_line = f"{url} -o - -f {output_format} -d {tmpdirname}"
        success: bool = _main(*cli_line.split())
        assert success
        out, err = capfd.readouterr()
        assert len(out) > 0
        header, *variants = [
            line.split(",") for line in out.split("\n") if line.strip() != ""
        ]
        variants = [dict(zip(header, v)) for v in variants]
        variants_by_key: Dict[Tuple[str, str], Dict[str, Any]] = {
            (v["mime_type"], v["profile"]): v for v in variants
        }
        log.debug(f"found {variants=}")
        log.debug(f"{len(variants)=}")
        # run over files in tmpdirname
        dump_path: Path = Path(tmpdirname)
        for f in [f for f in dump_path.glob("**/*") if f.is_file()]:
            # get the metadata stored on the files
            fattrs = {
                k: os.getxattr(f, f"user.web.{k}").decode("utf-8")
                for k in ("url", "mime_type", "profile")
            }
            assert fattrs["url"] == url
            # find the matching csv output
            v = variants_by_key.pop((fattrs["mime_type"], fattrs["profile"]))
            assert v is not None
            assert v["url"] == url
            assert v["inRequested"] == "False"  # since we requested none

        assert len(variants_by_key) == 0, "remaining variants exist"
