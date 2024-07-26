from sema.discovery.__main__ import main


def test_main():
    subject_uri = "http://todo.next/good/subject"
    cli_line = f"{subject_uri} -o - -f turtle"
    success: bool = main(*cli_line.split())
    assert success
