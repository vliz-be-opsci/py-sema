import requests
from sema.ro.getter import ROGetter
from pathlib import Path


class MockResponse:
    def __init__(self):
        with open("./tests/ro/getter/input-data/ro-crate-metadata.json", "r") as f:
            self.text = f.read()
        
        with open("./tests/ro/getter/input-data/zipball.zip", "rb") as f:
            self.content = f.read()


def mock_get(*args, **kwargs):
    return MockResponse()


def test_ro_getter(monkeypatch):
    monkeypatch.setattr(requests, "get", mock_get)

    roc = ROGetter(
        uri="http://example.com/",
        output_path="./tests/ro/getter/output-data",
        force=True,
    )
    roc.process()


    assert Path("./tests/ro/getter/output-data/ro-crate-metadata.json").exists()
