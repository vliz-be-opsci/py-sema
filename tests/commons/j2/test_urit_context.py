from logging import Logger, getLogger
from pathlib import Path

from sema.commons.j2.syntax_builder import J2RDFSyntaxBuilder

MY_FLDR = Path(__file__).parent
TEST_TMPLS_FLDR = MY_FLDR / "templates"
log: Logger = getLogger("tests")


def test_urit_context():
    j2sb: J2RDFSyntaxBuilder = J2RDFSyntaxBuilder(TEST_TMPLS_FLDR)
    vars: dict = {
        "name": "global.name",
        "record": {
            "name": "record.name",
        },
    }
    expected: list[str] = [
        "global.name",
        "record.name",
        "<http://ex.org/global.name>",
        "<http://ex.org/record.name>",
    ]
    output: str = j2sb.build_syntax("uritexpand_context.j2", **vars)
    lines: list[str] = output.split("\n")
    assert len(lines) == len(expected)
    for index, line in enumerate(lines):
        expanded, predicted = line.split("=")
        assert expanded == predicted
        assert expanded == expected[index]
