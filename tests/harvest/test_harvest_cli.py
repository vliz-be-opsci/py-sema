import pytest

from sema.harvest.__main__ import _main, get_arg_parser


@pytest.mark.parametrize(
    "args_line, expected",
    [
        (
            "-c /path/to/config -d /path/to/dump",
            {
                "config": ("/path/to/config",),
                "dump": ("/path/to/dump",),
            },
        ),
    ],
)
def test_args(args_line: str, expected: dict[str, tuple[str, ...]]) -> None:
    parser = get_arg_parser()
    assert parser is not None
    ns = parser.parse_args(args_line.split(" "))
    args = vars(ns)
    expected_set = set(expected.items())
    args_set = {
        (k, tuple(v) if isinstance(v, list) else v) for k, v in args.items()
    }
    assert expected_set.issubset(args_set), (
        f"{expected_set=} not in {args_set=}"
    )


def test_help(capfd: pytest.CaptureFixture) -> None:
    help_line: str = "--help"
    with pytest.raises(SystemExit) as caught:
        _main(*help_line.split())
    assert caught.value.code == 0
    assert caught.type is SystemExit
    out, err = capfd.readouterr()
    assert len(out) > 0
    assert out.startswith("usage: ")
