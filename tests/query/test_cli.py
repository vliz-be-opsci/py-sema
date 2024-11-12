from sema.query.__main__ import _main as query_main


def test_basic() -> None:
    arg1 = "tests/query/sources/01-persons-shape.ttl"
    arg2 = "tests/query/sources/02-person.ttl"
    output = "tests/output/test-sema-query-vliz.csv"

    cli_line = f" -t all.sparql" f" -s {arg1} {arg2}" f" -o {output}"

    query_main(*cli_line.split())
