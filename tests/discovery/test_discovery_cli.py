import pytest
from sema.discovery.__main__ import main


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
    subject_uri = "http://todo.next/good/subject"
    cli_line = f"{subject_uri} -o - -f turtle"
    success: bool = main(*cli_line.split())
    assert success
