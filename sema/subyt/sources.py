import glob
import logging
import mimetypes
import os
import re
from pathlib import Path
from typing import Callable

import requests
from typeguard import check_type
from uritemplate import URITemplate

from sema.commons.clean.clean import check_valid_url
from sema.commons.glob import getMatchingGlobPaths

from .api import Source

log = logging.getLogger(__name__)


def assert_readable(path_name: str | Path):
    in_path = Path(path_name)
    assert in_path.is_file(), f"File to read '{path_name}' does not exist"
    assert os.access(in_path, os.R_OK), f"Can not read '{path_name}'"


def fname_from_cdisp(cdisp):
    return re.split(r"; ?filename=", cdisp, flags=re.IGNORECASE)


class SourceFactory:
    _instance = None

    def __init__(self):
        self._register = dict()
        self._ext_mime_map = {"csv": "text/csv"}

    @property
    def ext_2_mime(self):
        return self._ext_mime_map

    def _add(self, mime: str, sourceClass: Callable[[str], Source]) -> None:
        assert mime is not False, "mime cannot be empty to register "
        assert sourceClass is not None, "sourceClass must be provided"
        check_type(sourceClass, Callable[[str], Source])

        self._register[mime] = sourceClass

    def _find(self, mime: str):
        assert mime in self._register, (
            f"no Source class available for mime '{mime}'",
        )
        return self._register[mime]

    @staticmethod
    def instance():
        if SourceFactory._instance is None:
            SourceFactory._instance = SourceFactory()
        return SourceFactory._instance

    @staticmethod
    def register(mime: str, sourceClass: Callable[[str], Source]) -> None:
        SourceFactory.instance()._add(mime, sourceClass)

    @staticmethod
    def map(ext: str, mime: str) -> None:
        SourceFactory.instance().ext_2_mime[ext] = mime

    @staticmethod
    def mime_from_url(url: str) -> str:
        # just get the header, no content yet
        response = requests.head(url, allow_redirects=True)
        if response.status_code == 200:
            mime: str = response.info().get_content_type()  # type: ignore
            cdhead = response.headers.get("Content-Disposition")
            if mime == "application/octet-stream" and cdhead is not None:
                cd = fname_from_cdisp(cdhead)
                mime = SourceFactory.mime_from_identifier(cd)  # type: ignore
        return mime

    @staticmethod
    def mime_from_identifier(identifier: str) -> str:
        ext = identifier.split(".")[-1]
        mime = SourceFactory.instance().ext_2_mime.get(ext)
        log.debug(f"mapping ext '{ext}' to mime '{mime}'")
        if mime is not None:
            return mime
        # else
        return mimetypes.guess_type(identifier)[0]  # type: ignore

    @staticmethod
    def make_source(
        identifier: str | Path, *, unique_pattern: str | None = None
    ) -> Source:
        source = SourceFactory._make_core_source(identifier)
        if unique_pattern is not None:
            source = FilteringSource(source, unique_pattern)
        return source

    @staticmethod
    def _make_core_source(identifier: str | Path) -> Source:
        # check for url
        if check_valid_url(str(identifier)):
            mime: str = SourceFactory.mime_from_remote(identifier)  # type: ignore # noqa
            raise NotImplementedError(
                "Remote Source support not implemented yet - see issues #8"
            )

        # else get input types nicely split str vs Path
        source_path: Path = Path(identifier)
        identifier = str(identifier)
        # check for folder source
        source: Source = None
        if source_path.is_dir():
            source = FolderSource(source_path)
            return source

        # else check for glob
        if glob.has_magic(identifier):
            source = GlobSource(identifier)
            return source

        # else should be single file with source tuned to mime
        mime: str = SourceFactory.mime_from_identifier(identifier)
        assert mime is not None, (
            f"no valid mime derived from identifier '{identifier}'",
        )
        sourceClass: Callable[[str], Source] = None
        sourceClass = SourceFactory.instance()._find(mime)
        source = sourceClass(source_path)
        return source


class CollectionSource(Source):
    def __init__(self) -> None:
        super().__init__()
        self._collection_path: Path = Path(".")
        self._sourcefiles: list[Path] = []

    def __repr__(self):
        return f"{type(self).__name__}('{self._collection_path}')"

    def _init_sourcefiles(self, source_paths: list[Path]):
        self._sourcefiles = sorted(source_paths)
        assert len(self._sourcefiles) > 0, (
            f"{self} should have content files.",
        )
        self._init_mtimes(self._sourcefiles)
        self._reset()

    def _reset(self):
        self._current_source = None
        self._current_iter = None
        self._ix = -1

    def _exitCurrent(self, exc_type, exc_val, exc_tb):
        if self._current_source is not None:
            self._current_source.__exit__(exc_type, exc_val, exc_tb)

    def _nextSource(self):
        self._exitCurrent()
        self._ix += 1
        if self._ix < len(self._sourcefiles):
            self._current_source = SourceFactory.make_source(
                self._sourcefiles[self._ix]
            )
            self._current_iter = self._current_source.__enter__()
        else:
            self._current_source = None
            self._current_iter = None
            raise StopIteration

    def _nextItem(self):
        # proceed to next element, if needed, proceed to next source
        if self._current_source is None:
            self._nextSource()
        try:
            return next(self._current_iter)  # type: ignore
        except StopIteration:
            self._nextSource()
            return next(self._current_iter)  # type: ignore

    def __enter__(self):
        class IterProxy:
            def __init__(self, me):
                self._me = me

            def __iter__(self):
                self._me._reset()
                return self

            def __next__(self):
                return self._me._nextItem()

        return IterProxy(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # exit the current open source
        self._exitCurrent(exc_type, exc_val, exc_tb)
        self._reset()


class FolderSource(CollectionSource):
    def __init__(self, folder_path: Path):
        super().__init__()
        self._collection_path = folder_path.absolute()
        self._init_sourcefiles(
            [f for f in self._collection_path.iterdir() if f.is_file()]
        )

    def __repr__(self):
        return f"FolderSource('{self._collection_path}')"


class GlobSource(CollectionSource):
    def __init__(self, pattern: str, pattern_root_dir: str = "."):
        super().__init__()
        self._collection_path = Path(pattern_root_dir).absolute()
        self._pattern: str = pattern
        self._init_sourcefiles(
            [
                f
                for f in getMatchingGlobPaths(
                    self._collection_path,
                    includes=[pattern],
                    onlyFiles=True,
                    makeRelative=False,
                )
            ]
        )

    def __repr__(self):
        return f"GlobSource('{self._pattern}', '{self._collection_path}')"


class FilteringSource(Source):
    def __init__(self, core: Source, unique_pattern: str):
        super().__init__()
        self._core = core
        self._unique_pattern = unique_pattern
        self._unique_template = URITemplate(unique_pattern)

    def __repr__(self):
        return f"FilteringSource({self._core}, '{self._unique_pattern}')"

    def __enter__(self):
        class FilterIterProxy:
            def __init__(self, me):
                self._me = me
                self._core_iter = me._core.__enter__()
                self._seen = set()

            def __iter__(self):
                return FilterIterProxy(self._me)

            def __next__(self):
                item = next(self._core_iter)
                unique = self._me._unique_template.expand(item)
                if unique not in self._seen:
                    self._seen.add(unique)
                    return item
                # else
                log.debug(f"skipping record {item=} matching {unique=}")
                return next(self)

        return FilterIterProxy(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._core.__exit__(exc_type, exc_val, exc_tb)


try:
    import csv

    class CSVFileSource(Source):
        """
        Source producing iterator over data-set coming from CSV on file
        """

        def __init__(self, csv_file_path: Path):
            super().__init__()
            assert_readable(csv_file_path)
            self._csv: Path = csv_file_path.absolute()
            self._init_source(self._csv)

        def __enter__(self):
            self._csvfile = open(self._csv, mode="r", encoding="utf-8-sig")
            return csv.DictReader(self._csvfile, delimiter=",")

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._csvfile.close()

        def __repr__(self):
            return f"CSVFileSource('{self._csv!s}')"

    SourceFactory.register("text/csv", CSVFileSource)
    # wrong, yet useful mime for csv:
    SourceFactory.register("application/csv", CSVFileSource)
except ImportError:
    log.warning("Python CSV module not available -- disabling CSV support!")


try:
    import json

    class JsonFileSource(Source):
        """
        Source producing iterator over data-set coming from json on file
        """

        def __init__(self, json_file_path: Path):
            super().__init__()
            assert_readable(json_file_path)
            self._json = json_file_path.absolute()
            self._init_source(self._json)

        def __enter__(self):
            # note this is loading everything in memory
            #   -- will not work for large sets
            #   in the future we might need to consider:
            #   (json-stream)[https://pypi.org/project/json-stream/]
            with open(self._json, mode="r", encoding="utf-8-sig") as jsonfile:
                data = json.load(jsonfile)
                # unwrap nested structures
                while isinstance(data, dict) and len(data.keys()) == 1:
                    child = list(data.values())[0]
                    if isinstance(child, dict) and len(child.keys()) == 0:
                        data = [data]
                    else:
                        data = child
                if not isinstance(data, list):
                    data = [data]
            return iter(data)

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def __repr__(self):
            return f"JsonFileSource('{self._json!s}')"

    SourceFactory.register("application/json", JsonFileSource)
except ImportError:
    log.warning("Python JSON module not available -- disabling JSON support!")


try:
    import xmlasdict

    class XMLFileSource(Source):
        """
        Source producing iterator over data-set coming from XML on file
        """

        def __init__(self, xml_file_path: Path):
            super().__init__()
            assert_readable(xml_file_path)
            self._xml: Path = xml_file_path.absolute()
            self._init_source(self._xml)

        def __enter__(self):
            with open(self._xml, mode="r", encoding="utf-8-sig") as xmlfile:
                xml_str = xmlfile.read()
                xdict = xmlasdict.parse(xml_str)
                # unpack root wrappers
                try:
                    xdict = xmlasdict.parse(xml_str)
                    # unpack root wrappers
                    data = xdict.unpack()  # type: ignore
                except Exception:
                    log.exception(f"Failed to parse XML file {self._xml}")
                    raise

            return iter(data)

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

        def __repr__(self):
            return f"XMLFileSource('{self._xml}')"

    SourceFactory.map("eml", "text/xml")
    SourceFactory.register("text/xml", XMLFileSource)
    # wrong, yet useful mime for xml:
    SourceFactory.register("application/xml", XMLFileSource)
except ImportError:
    log.warning("Python XML module not available -- disabling XML support!")
