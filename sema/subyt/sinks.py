import logging
import os
from pathlib import Path

from uritemplate import URITemplate, variables

from .api import Sink

log = logging.getLogger(__name__)


def assert_writable(file_path: str, force_output: bool = False):
    if not force_output:
        assert not os.path.isfile(
            file_path
        ), f"File to write '{file_path}' already exists"
    parent_path = Path(file_path).parent.absolute()
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)
    assert os.access(
        parent_path, os.W_OK
    ), f"Can not write to folder '{parent_path}' for creating new files"


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
    def __init__(self, file_path: str, force_output: bool = False):
        super().__init__()
        assert_writable(file_path, force_output)
        self._file_path = file_path
        self._force_output = force_output
        if Path(file_path).exists():
            self.mtimes = {file_path: os.stat(file_path).st_mtime}

    def __repr__(self):
        return (
            f"SingleFileSink('{str(Path(self._file_path).resolve())}', "
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
        sink_mtime = (
            Path(file_path).stat().st_mtime if Path(file_path).exists() else 0
        )
        if source_mtime and (source_mtime < sink_mtime):
            log.info(
                f"Aborting creation of {file_path} "
                f"(source_mtime = {source_mtime}; sink_mtime = {sink_mtime})"
            )
            return
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
