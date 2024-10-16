import csv
from pathlib import Path

import yaml

from sema.check.base import CheckResult
from sema.check.sinks import write_csv, write_html, write_yml


def test_write_csv() -> None:
    # Arrange
    results = [
        CheckResult(
            success=True,
            error=None,
            message="Test passed",
            url="http://example.com",
            type_test="example",
        ),
        CheckResult(
            success=False,
            error="Some error",
            message="Test failed",
            url="http://example.com/2",
            type_test="example",
        ),
    ]
    tmp_path = Path(__file__).parent / "out"
    tmp_path.mkdir(parents=True, exist_ok=True)
    output_file = tmp_path / "output.csv"

    # Act
    write_csv(results, str(output_file))

    # Assert
    assert output_file.exists()
    with open(output_file, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["success"] == "True"
        assert rows[0]["error"] == ""
        assert rows[0]["message"] == "Test passed"
        assert rows[0]["url"] == "http://example.com"
        assert rows[0]["type"] == "example"
        assert rows[1]["success"] == "False"
        assert rows[1]["error"] == "Some error"
        assert rows[1]["message"] == "Test failed"
        assert rows[1]["url"] == "http://example.com/2"
        assert rows[1]["type"] == "example"


def test_write_html() -> None:
    results = [
        CheckResult(
            success=True,
            error=False,
            message="Test 1 passed",
            url="http://example.com",
            type_test="example",
        ),
        CheckResult(
            success=False,
            error=True,
            message="Test 2 failed",
            url="http://example.com/2",
            type_test="example",
        ),
    ]
    tmp_path = Path(__file__).parent / "out"
    output_file = tmp_path / "test_results.html"

    write_html(results, str(output_file))

    assert output_file.exists()
    with open(output_file) as f:
        content = f.read()
        assert '<html lang="en">' in content
        assert "<title>Test Results</title>" in content
        assert "Test 1 passed" in content
        assert "Test 2 failed" in content


def test_write_yml():
    results = [
        CheckResult(
            success=True,
            error=None,
            message="Test passed",
            url="http://example.com",
            type_test="example",
        ),
        CheckResult(
            success=False,
            error="Some error",
            message="Test failed",
            url="http://example.com/2",
            type_test="example",
        ),
    ]
    tmp_path = Path(__file__).parent / "out"
    tmp_path.mkdir(parents=True, exist_ok=True)
    output_file = tmp_path / "output.yml"
    write_yml(results, str(output_file))
    with open(output_file) as f:
        loaded_results = yaml.safe_load(f)

    assert output_file.exists()
    assert len(loaded_results) == 2
    assert loaded_results[0]["success"] is True
    assert loaded_results[0]["error"] is None
    assert loaded_results[0]["message"] == "Test passed"
    assert loaded_results[0]["url"] == "http://example.com"
    assert loaded_results[0]["type_test"] == "example"
    assert loaded_results[1]["success"] is False
    assert loaded_results[1]["error"] == "Some error"
    assert loaded_results[1]["message"] == "Test failed"
    assert loaded_results[1]["url"] == "http://example.com/2"
    assert loaded_results[1]["type_test"] == "example"
