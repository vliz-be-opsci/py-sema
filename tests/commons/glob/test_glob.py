from pathlib import Path
from typing import Any

import pytest
from conftest import TEST_FOLDER, log

from sema.commons.glob import (
    GlobMatchVisitor,
    getMatchingGlobPaths,
    pathMatchesGlob,
    visitGlobPaths,
)


def test_getMatchingGlobPaths() -> None:
    assert getMatchingGlobPaths
    root = TEST_FOLDER / "data/glob"
    assert root.exists() and root.is_dir()

    # basic full listing
    log.debug("globtest - all paths")
    all_paths = getMatchingGlobPaths(root)
    assert all_paths
    assert len(all_paths) == 10

    # basic full listing with only files
    log.debug("globtest - all files")
    all_files = getMatchingGlobPaths(root, onlyFiles=True)
    assert all_files
    assert len(all_files) == 8

    # all txt files
    log.debug("globtest - all txt files")
    txt_files = getMatchingGlobPaths(root, includes="**/*.txt")
    assert txt_files
    assert len(txt_files) == 5

    # only text files not dirtectly under the 050/ folder
    log.debug("globtest - some txt files")
    some_files = getMatchingGlobPaths(
        root, includes=["**/*.txt"], excludes=["050/*.txt"]
    )
    assert some_files
    assert len(some_files) == 3


@pytest.mark.parametrize(
    "path, glob, expected",
    [
        ("./sub/file.txt", "**/*.txt", True),
        ("./sub/file.txt", "**/f*.txt", True),
        ("./sub/file.txt", "**/1*.txt", False),
        ("./sub/file.txt", "*.txt", True),
        ("./sub/file.txt", "*.xml", False),
    ],
)
def test_pathMatchesGlob(path, glob, expected) -> None:
    assert pathMatchesGlob(TEST_FOLDER / "data/glob" / path, glob) == expected


def test_visitGlobPaths() -> None:
    assert visitGlobPaths
    assert GlobMatchVisitor

    class TestVisitor(GlobMatchVisitor):
        def __init__(self) -> None:
            self.visited = []

        def visitExcluded(self, path: Path) -> None:
            raise RuntimeError(
                f"in this test we should not exclude path {path}"
            )

        def _apply_visited(
            self, path: Path, result: dict[str, bool], applying: list[Any]
        ) -> dict[str, bool]:
            self.visited.append(path)
            for apply in applying:
                result.update(apply(path))
            return result

        def visitFile(self, path: Path, applying: list[Any]) -> Any:
            return self._apply_visited(
                path, {"is_file": True, "in_sub": False}, applying
            )

        def visitDirectory(self, path: Path, applying: list[Any]) -> Any:
            return self._apply_visited(
                path, {"is_dir": True, "in_sub": False}, applying
            )

    root = TEST_FOLDER / "data/glob"
    visitor = TestVisitor()
    applying: dict[str, any] = {
        "*.xml": lambda p: {"is_xml": True},
        "*.txt": lambda p: {"is_txt": True},
        "*.csv": lambda p: {"is_csv": True},
        "*.json": lambda p: {"is_json": True},
        "*/*": lambda p: {"in_sub": True},
    }

    results = visitGlobPaths(
        visitor,
        root,
        includes="**/*",
        applying=applying,
    )
    assert results
    assert len(results) == 10

    assert results[Path("010.txt")] == {
        "is_file": True,
        "is_txt": True,
        "in_sub": False,
    }
    assert results[Path("020.txt")] == {
        "is_file": True,
        "is_txt": True,
        "in_sub": False,
    }
    assert results[Path("030.csv")] == {
        "is_file": True,
        "is_csv": True,
        "in_sub": False,
    }
    assert results[Path("040.xml")] == {
        "is_file": True,
        "is_xml": True,
        "in_sub": False,
    }
    assert results[Path("050")] == {"is_dir": True, "in_sub": False}
    assert results[Path("050/060.txt")] == {
        "is_file": True,
        "is_txt": True,
        "in_sub": True,
    }
    assert results[Path("050/070.json")] == {
        "is_file": True,
        "is_json": True,
        "in_sub": True,
    }
    assert results[Path("050/080")] == {"is_dir": True, "in_sub": True}
    assert results[Path("050/080/090.txt")] == {
        "is_file": True,
        "is_txt": True,
        "in_sub": True,
    }
    assert results[Path("050/100.txt")] == {
        "is_file": True,
        "is_txt": True,
        "in_sub": True,
    }

    # provoke the exception in the visitor for exclusions
    with pytest.raises(RuntimeError):
        visitGlobPaths(
            visitor,
            root,
            includes=["**/*"],
            applying=applying,
            excludes=["*.txt"],
        )
