from sema.commons.aggregator import Aggregator


def test_aggregator():
    Aggregator(
        input_path="./tests/commons/aggregator/data",
        globs="**/*.ttl: ttl, **/*.json: json-ld",
    ).process()

    with open("./tests/commons/aggregator/data/graph.ttl") as f:
        lines = [_ for _ in f.readlines() if _.strip()]  # exclude empty lines
        assert len(lines) == 12
