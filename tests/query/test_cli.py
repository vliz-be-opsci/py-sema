from sema.query.__main__ import main as query_main


def test_basic():
    arg1 = "tests/query/sources/01-persons-shape.ttl"
    arg2 = "tests/query/sources/02-person.ttl"
    output = "/tmp/test-sema-query-vliz.csv"

    query_main(f"-s {arg1} {arg2} -o {output} -t all.sparql".split(" "))
