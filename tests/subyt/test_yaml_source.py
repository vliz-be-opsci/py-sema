import tempfile
from pathlib import Path

import pytest

from sema.subyt.api import Source
from sema.subyt.sources import SourceFactory, YamlFileSource

YAML_LIST_CONTENT = """
- name: Alice
  age: 30
- name: Bob
  age: 25
"""

YAML_MULTI_DOC_CONTENT = """
---
name: Alice
age: 30
---
name: Bob
age: 25
"""

YAML_WRAPPED_CONTENT = """
people:
  - name: Alice
    age: 30
  - name: Bob
    age: 25
"""

YAML_SINGLE_RECORD = """
name: Alice
age: 30
"""


@pytest.mark.parametrize(
    "content,expected_len",
    [
        (YAML_LIST_CONTENT, 2),
        (YAML_MULTI_DOC_CONTENT, 2),
        (YAML_WRAPPED_CONTENT, 2),
        (YAML_SINGLE_RECORD, 1),
    ],
)
def test_yaml_file_source_contents(content: str, expected_len: int) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        source: Source = SourceFactory.make_source(str(temp_path))
        assert isinstance(source, YamlFileSource)
        with source as items:
            data = list(items)
            assert len(data) == expected_len
            assert data[0]["name"] == "Alice"
            assert data[0]["age"] == 30
    finally:
        temp_path.unlink()


def test_yaml_yml_extension_and_mime() -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".yml", delete=False) as f:
        f.write(YAML_LIST_CONTENT)
        temp_yml = Path(f.name)

    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        f.write(YAML_LIST_CONTENT)
        temp_yaml = Path(f.name)

    try:
        # Check .yml detection via mimetypes
        source_yml = SourceFactory.make_source(str(temp_yml))
        assert isinstance(source_yml, YamlFileSource)

        # Check .yaml detection via mimetypes
        source_yaml = SourceFactory.make_source(str(temp_yaml))
        assert isinstance(source_yaml, YamlFileSource)

        # Check explicit config with official IANA mime type (application/yaml)
        source_mime = SourceFactory.make_source(
            {"path": str(temp_yaml), "mime": "application/yaml"}
        )
        assert isinstance(source_mime, YamlFileSource)
    finally:
        temp_yml.unlink()
        temp_yaml.unlink()


def test_yaml_unique_filter() -> None:
    content = """
- id: 1
  name: Alice
- id: 1
  name: Alice Duplicate
- id: 2
  name: Bob
"""
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        source = SourceFactory.make_source(
            str(temp_path), unique_pattern="{id}"
        )
        with source as items:
            records = list(items)
            assert len(records) == 2
            assert records[0]["name"] == "Alice"
            assert records[1]["name"] == "Bob"
    finally:
        temp_path.unlink()

