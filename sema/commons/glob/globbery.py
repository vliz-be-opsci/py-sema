from abc import ABC, abstractmethod
from logging import getLogger
from pathlib import Path
from typing import Any

log = getLogger(__name__)


def getMatchingGlobPaths(
    root: Path,
    includes: list[str] | str = ["**/*"],
    excludes: list[str] | str = [],
    *,
    onlyFiles: bool = False,
    makeRelative: bool = True,
) -> list[Path]:
    """
    Get all paths under `root` that match any of the globs in `includes`
    and none of the globs in `excludes`.
    @param root: The root path to search under.
    @param includes: A list of globs to include.
        For convenience, a single string is also accepted.
    @param excludes: A list of globs to exclude.
        For convenience, a single string is also accepted.
    @param onlyFiles: If True, only return files, not directories.
    @param makeRelative: If True, return paths relative to `root`.
    @return: A list of paths that match the globs.
    """
    found: set[Path] = set()
    if isinstance(includes, str):
        includes = [includes]
    if isinstance(excludes, str):
        excludes = [excludes]
    for include in includes:
        for path in root.glob(include):
            if any(path.match(exclude) for exclude in excludes):
                log.debug(f"excluding {path} by {excludes}")
                continue
            if onlyFiles and path.is_dir():
                log.debug(f"excluding {path} is folder")
                continue
            if makeRelative:
                path = path.relative_to(root)
            log.debug(f"including {path}")
            found.add(path)
    return list(found)


def pathMatchesGlob(path: Path, glob: str) -> bool:
    """
    Check if a path matches a glob.
    @param path: The path to check.
    @param glob: The glob to match against.
    @return: True if the path matches the glob.
    """
    return path.match(glob)


class GlobMatchVisitor(ABC):
    """Abstract interface for visiting paths matched by a glob."""

    @abstractmethod
    def visitExcluded(self, path: Path) -> None:
        """
        Called when a path is excluded by a glob.
        @param path: The path that was excluded.
        """
        pass

    @abstractmethod
    def visitFile(self, path: Path, applying: list[Any]) -> Any:
        """
        Called when a file is visited.
        @param path: The file path.
        @param applying: A list of apply objects with matching globs.
        @return: custom result of the visit to be aggregated by the caller.
        """
        pass

    @abstractmethod
    def visitDirectory(self, path: Path, applying: list[Any]) -> Any:
        """
        Called when a directory is visited.
        @param path: The directory path.
        @param applying: A list of apply objects with matching globs.
        @return: custom result of the visit to be aggregated by the caller.
        """
        pass


def visitGlobPaths(
    visitor: GlobMatchVisitor,
    root: Path,
    includes: list[str] | str = ["**/*"],
    excludes: list[str] | str = [],
    applying: dict[str, Any] = {},
    *,
    onlyFiles: bool = False,
    makeRelative: bool = True,
) -> dict[Path, Any]:
    """
    Visit all paths under `root` that match any of the globs in `includes`
    and none of the globs in `excludes`.
    @param visitor: The visitor to call for each path.
    @param root: The root path to search under.
    @param includes: A list of globs to include.
        For convenience, a single string is also accepted.
    @param excludes: A list of globs to exclude.
        For convenience, a single string is also accepted.
    @param applying: A dictionary of apply objects to pass to the visitor.
        Keys are globs.
    @param onlyFiles: If True, only visit files, not directories.
    @param makeRelative: If True, return paths relative to `root`.
        Alsso makes them relative before visit.
    @return: A dictionary of paths to visitor results.
        Keys are paths being visited.
    """
    results: dict[Path, Any] = dict()
    if isinstance(includes, str):
        includes = [includes]
    if isinstance(excludes, str):
        excludes = [excludes]
    for include in includes:
        for path in root.glob(include):
            relpath = path.relative_to(root) if makeRelative else path
            if any(path.match(exclude) for exclude in excludes):
                log.debug(f"excluding {path} by {excludes}")
                visitor.visitExcluded(relpath)
                continue
            if onlyFiles and path.is_dir():
                log.debug(f"excluding {path} is folder")
                visitor.visitExcluded(relpath)
                continue
            # find all applying objects for this path
            apps = [a for p, a in applying.items() if relpath.match(p)]
            if path.is_dir():
                log.debug(f"applying {apps} to dir {path}")
                results[relpath] = visitor.visitDirectory(path, apps)
            else:
                log.debug(f"applying {apps} to file {path}")
                results[relpath] = visitor.visitFile(path, apps)
    return results
