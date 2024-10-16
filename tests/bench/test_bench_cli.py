from logging import getLogger

import pytest

from sema.bench.__main__ import _main, get_arg_parser

log = getLogger(__name__)


@pytest.mark.parametrize(
    "args_line, expected",
    [
        (
            "--config-path /path/to/config --config-name custom.yaml"
            " --interval 500 --watch --fail-fast",
            {
                "config_path": "/path/to/config",
                "config_name": "custom.yaml",
                "interval": 500,
                "watch": True,
                "fail_fast": True,
            },
        ),
        (
            "--config-path /another/path",
            {
                "config_path": "/another/path",
                "config_name": "sembench.yaml",
                "interval": 1000,
                "watch": False,
                "fail_fast": False,
            },
        ),
        (
            "--config-path /default/path",
            {
                "config_path": "/default/path",
                "config_name": "sembench.yaml",
                "interval": 1000,
                "watch": False,
                "fail_fast": False,
            },
        ),
    ],
)
def test_args(args_line, expected) -> None:
    parser = get_arg_parser()
    assert parser is not None
    log.info("args_line: %s", args_line)
    ns = parser.parse_args(args_line.split(" "))
    args = vars(ns)
    expected_set = set(expected.items())
    args_set = set(args.items())
    assert expected_set.issubset(args_set), (
        f"{expected_set=} " f"not in {args_set=}"
    )


def test_help(capfd: pytest.CaptureFixture) -> None:
    help_line: str = "--help"
    with pytest.raises(SystemExit) as caught:
        success: bool = _main(*help_line.split())
        assert not success
        assert caught.value.code == 0
        assert caught.type == SystemExit
    out, err = capfd.readouterr()
    assert len(out) > 0
    assert out.startswith("usage: ")
