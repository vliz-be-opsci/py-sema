import logging
import os
from pathlib import Path

from uritemplate import URITemplate, variables

from .api import Sink

log = logging.getLogger(__name__)


def assert_writable(path_name: str | Path, force_output: bool = False):
    out_path = Path(path_name)
    if not force_output:
        assert not out_path.exists(), (
            f"File to write '{path_name}' already exists"
        )
    # ensure parent folder exists
    parent_path = out_path.parent.absolute()
    parent_path.mkdir(parents=True, exist_ok=True)
    assert os.access(parent_path, os.W_OK), (
        f"Can not write to folder '{parent_path}' for creating new files",
    )


class SinkFactory:
    @staticmethod
    def make_sink(
        identifier: str,
        force_output: bool = False,
        allow_repeated_sink_paths: bool = False,
    ) -> Sink:
        identifier = identifier or "-"
        if identifier == "-":
            if allow_repeated_sink_paths:
                log.warning(
                    "repeated sink paths do not apply to StdOutSink, "
                    "ignoring..."
                )
            return StdOutSink()
        # else:
        if len(variables(identifier)) == 0:  # identifier is not a pattern
            if allow_repeated_sink_paths:
                log.warning(
                    "repeated sink paths do not apply to SingleFileSink, "
                    "ignoring..."
                )
            return SingleFileSink(identifier, force_output)
        # else:                                        #identifier is a pattern
        return PatternedFileSink(
            identifier, force_output, allow_repeated_sink_paths
        )


class StdOutSink(Sink):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return "StdOutSink"

    def open(self):
        pass

    def close(self):
        pass

    def add(
        self,
        part: str,
        item: dict | None = None,
        source_mtime: float | None = None,
    ):
        print(part)


class SingleFileSink(Sink):
    def __init__(self, path_name: str, force_output: bool = False):
        super().__init__()
        assert_writable(path_name, force_output)
        self._file_path: Path = Path(path_name)
        self._force_output = force_output
        if self._file_path.exists():
            self.mtimes = {path_name: self._file_pathpath_name.stats().st_mtime}

    def __repr__(self):
        return (
            f"SingleFileSink('{str(self._file_path.resolve())}', "
            f"{self._force_output})"
        )

    def open(self):
        self._fopen = open(self._file_path, "w", encoding="utf-8")

    def close(self):
        if self._fopen:
            self._fopen.close()
        self._fopen = None

    def add(
        self,
        part: str,
        item: dict | None = None,
        source_mtime: float | None = None,
    ):
        assert self._fopen is not None, "File to Sink to already closed"
        log.info(f"Creating {self._file_path}")
        self._fopen.write(part)


class PatternedFileSink(Sink):
    def __init__(
        self,
        name_pattern: str,
        force_output: bool = False,
        allow_repeated_sink_paths: bool = False,
    ):
        super().__init__()
        self._name_template = URITemplate(name_pattern)
        self._force_output = force_output
        self._allow_repeated_sink_paths = allow_repeated_sink_paths
        self._file_paths = []
        self.mtimes = None

    def __repr__(self):
        return (
            f"PatternedFileSink("
            f"'{self._name_template.uri}', {self._force_output})"
        )

    def open(self):
        pass

    def close(self):
        pass

    def _add(
        self, file_path: str, part: str, source_mtime: float | None = None
    ):
        out_path: Path = Path(file_path)
        if out_path.exists() and out_path.is_dir():
            log.warning(
                f"Skipping creation of {file_path} as it is a directory. "
            )
            return
        # else
        sink_mtime = out_path.stat().st_mtime if out_path.exists() else 0
        if source_mtime and (source_mtime < sink_mtime):
            log.info(
                f"Aborting creation of {file_path} "
                f"(source_mtime = {source_mtime}; sink_mtime = {sink_mtime})"
            )
            return
        # else
        assert_writable(file_path, self._force_output)
        log.info(f"Creating {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(part)

    def add(
        self,
        part: str,
        item: dict | None = None,
        source_mtime: float | None = None,
    ):
        assert item is not None, "No data context available to expand template"
        for template_var in self._name_template.variables:
            for var_name in template_var.variable_names:
                if (
                    var_name not in item
                    or item[var_name] is None
                    or item[var_name] == ""
                ):
                    log.warning(
                        f"{self} expansion requires field '{var_name}'. "
                        "It is however not present in the current item."
                    )
        file_path = self._name_template.expand(item)
        if self._allow_repeated_sink_paths:
            extended_file_path = file_path[:]
            if file_path in self._file_paths:
                extended_file_path = (
                    f"{file_path}_{self._file_paths.count(file_path) - 1}"
                )
            self._add(extended_file_path, part, source_mtime)
        else:
            if file_path in self._file_paths:
                raise RuntimeError(
                    f"{file_path} was already created in this process, "
                    "make sure data items are not duplicated or "
                    "set allow_repeated_sink_paths to True"
                )
            self._add(file_path, part, source_mtime)
        self._file_paths.append(file_path)
