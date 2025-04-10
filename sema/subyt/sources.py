import glob
import logging
import mimetypes
import os
from pathlib import Path
from typing import Callable, Iterable

import requests
from typeguard import check_type
from uritemplate import URITemplate

from sema.commons.clean.clean import check_valid_url
from sema.commons.glob import getMatchingGlobPaths
from sema.commons.web import parse_header

from .api import Source

log = logging.getLogger(__name__)


def assert_readable(path_name: str | Path):
    in_path = Path(path_name)
    if not in_path.is_file():
        raise ValueError(f"File to read '{path_name}' does not exist")
    if not os.access(in_path, os.R_OK):
        raise ValueError(f"Can not read '{path_name}'")


def fname_from_cdisp(cdisp):
    main, params = parse_header(cdisp, "content-disposition")
    return params.get("filename", None)


class SourceFactory:
    """Helper class to create Source objects based on identifier for them."""

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
        identifier: str | Path | dict,
        *,
        unique_pattern: str | None = None,
        fake_empty: bool = False,
    ) -> Source:
        """Factory method to create a Source object based on identifier.
        @param identifier: specification of the source to build. This can be a
            string, a Path object or a dictionary. If a string, it can be a
            simple file path, a glob pattern, or a URL. The file path can be
            extended with extra [+key=value] pairs to mimic the dictionary.
            If a dictionary, it should have at least a key 'path' holding
            the file path. Additinally an `ext` or `mime` key can be used to
            specify the mime type of the source. Depending on that type extra
            keys can be meaningful. (e.g. for csv header, delimiter, etc.)
            If the identifier is a URL, the mime type is derived from the
            response header.
        @type identifier: str | Path | dict
        @param unique_pattern: a pattern to filter out unique records from the
            source. This pattern uses uripattern syntax and when expanded will
            yield a value for each record that is used to filter records:
            only the first record for each expanded value is processed as part
            of the source.
        @type unique_pattern: str | None
        @param fake_empty: if True, any error in the factory process will lead
            to returning a fake empty source. Else the error is raised.
        """
        log.debug(
            f"creating source from '{identifier}' "
            f"with {unique_pattern=}, {fake_empty=}"
        )
        try:
            source = SourceFactory._make_core_source(identifier)
        except ValueError as e:
            if not fake_empty:
                raise e
            # else
            log.warning(
                f"Failed to create source from '{identifier}'",
                exc_info=e,
            )
            source = EmptySource()

        # check for extra filtering need
        if unique_pattern is not None:
            source = FilteringSource(source, unique_pattern)
        return source

    @staticmethod
    def _parse_source_identifier(identifier: str | Path | dict) -> dict:
        if isinstance(identifier, dict):
            config = identifier
            if "identifier" not in config:
                config["identifier"] = str(config["path"])
                config["path"] = Path(config["path"])
            return config
        # else
        if isinstance(identifier, Path):
            return {"identifier": identifier, "path": identifier}
        # else
        config: dict = dict()
        if isinstance(identifier, str):
            # split on '+', take first as new identifer, group rest as parts
            first, *parts = identifier.split("+")
            config["identifier"] = first
            for part in parts:
                key, value = part.split("=")
                config[key] = value
        if len(config) == 0:
            raise ValueError(f"Invalid identifier '{identifier}'")
        # else
        return config

    @staticmethod
    def _make_core_source(identifier: str | Path | dict) -> Source:
        config = SourceFactory._parse_source_identifier(identifier)
        identifier = config["identifier"]
        # check for url
        if check_valid_url(str(identifier)):
            mime: str = SourceFactory.mime_from_remote(identifier)  # type: ignore # noqa
            raise NotImplementedError(
                "Remote Source support not implemented yet - see issues #8"
            )

        # else get input types nicely split str vs Path
        source_path: Path = config.get("path", Path(identifier))
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
        mime: str = None
        if "mime" in config:
            mime = config["mime"]
        elif "ext" in config:
            mime = SourceFactory.instance().ext_2_mime.get(config["ext"])
        else:
            mime = SourceFactory.mime_from_identifier(identifier)
        assert mime is not None, (
            f"no valid mime derived from identifier '{identifier}'",
        )
        sourceClass: Callable[[str], Source] = None
        sourceClass = SourceFactory.instance()._find(mime)
        source = sourceClass(source_path, config)
        return source


class CollectionSource(Source):
    """Base class for Source implementations that are collections of sources.
    Meaning they are based on a collection of files, like a folder or a glob
    pattern. The content they represent is a concatenation of the content of
    the files in the collection.
    """

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

    def _exitCurrent(self, *exc) -> None:
        if self._current_source is not None:
            self._current_source.__exit__(*exc)

    def _nextSource(self) -> None:
        self._exitCurrent(None, None, None)
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

    def __exit__(self, *exc) -> None:
        # exit the current open source
        self._exitCurrent(*exc)
        self._reset()


class FolderSource(CollectionSource):
    """Case of CollectionSource respresenting all the direct-child files
    inside the specified folder."""

    def __init__(self, folder_path: Path):
        super().__init__()
        self._collection_path = folder_path.absolute()
        self._init_sourcefiles(
            [f for f in self._collection_path.iterdir() if f.is_file()]
        )

    def __repr__(self):
        return f"FolderSource('{self._collection_path}')"


class GlobSource(CollectionSource):
    """Case of CollectionSource respresenting all the files matching the
    specified glob pattern."""

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
    """Decorating source implementation that filters out records based on
    a unique pattern. Only the first record for each expanded value is
    processed as part of the source.
    Being a decorator means this can be applied to any other Source
    implementation.
    """

    def __init__(self, core: Source, unique_pattern: str) -> None:
        super().__init__()
        self._core = core
        self._unique_pattern = unique_pattern
        self._unique_template = URITemplate(unique_pattern)
        if len(self._unique_template.variable_names) == 0:
            raise ValueError(
                f"unique_pattern for filtering '{unique_pattern}' "
                "must have at least one variable in use."
            )

    def __repr__(self) -> str:
        return f"FilteringSource({self._core}, '{self._unique_pattern}')"

    def __enter__(self) -> object:
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

    def __exit__(self, *exc) -> None:
        self._core.__exit__(*exc)


class EmptySource(Source):
    """
    Fake Empty Source producing iterator over nothing.
    """

    def __init__(self) -> None:
        super().__init__()

    def __enter__(self) -> object:
        return iter([])

    def __exit__(self, *exc: object) -> None:
        pass

    def __repr__(self) -> str:
        return "EmptySource()"


try:
    import csv

    def csv_filter(
        content: Iterable[str],
        *,
        comment: str = "#",
        skip_blank_lines: bool = True,
    ):
        if comment is None and skip_blank_lines:
            return content  # nothing to do, just pass original content
        # else

        # make filter
        def not_comment_or_blank(line) -> bool:
            if skip_blank_lines and not line.strip():
                return False
            if comment and line.startswith(comment):
                return False
            return True

        # apply filter
        return filter(not_comment_or_blank, content)

    class CSVFileSource(Source):
        """Accepted keys in the constructor config dict"""

        CFGKEYS: set = {
            "delimiter",
            "quotechar",
            "header",
            "comment",
            "skip_blank_lines",
        }

        """
        Source producing iterator over data-set coming from CSV on file.
        The identifier (str or dict) for this source can have the following
        extra keys:
        - delimiter: the delimiter character used in the CSV file
        - quotechar: the quote character used in the CSV file
        - header: the header line of the CSV file (using the same delimiter)
        - comment: the comment character used in the CSV file,
              this lead character indicates lines to be skipped
        - skip_blank_lines: if True, blank lines are skipped
        """

        def __init__(self, csv_file_path: Path, config: dict = {}) -> None:
            super().__init__()
            assert_readable(csv_file_path)
            self._csv: Path = csv_file_path.absolute()
            self._init_source(self._csv)
            self._csvconfig: dict = dict()
            for key in self.CFGKEYS:
                if key in config:
                    self._csvconfig[key] = config[key]

        def __enter__(self) -> object:
            self._csvfile = open(self._csv, mode="r", encoding="utf-8-sig")
            # use config settings -- for CSVLinesFilter
            comment: str = self._csvconfig.get("comment", None)
            skip_blank_lines: bool = self._csvconfig.get(
                "skip_blank_lines", False
            )
            # and -- for csv.DictReader
            delimiter: str = self._csvconfig.get("delimiter", ",")
            quotechar: str = self._csvconfig.get("quotechar", '"')
            header: str = self._csvconfig.get("header")
            fieldnames: list = header.split(delimiter) if header else None

            return csv.DictReader(
                csv_filter(
                    self._csvfile,
                    comment=comment,
                    skip_blank_lines=skip_blank_lines,
                ),
                delimiter=delimiter,
                quotechar=quotechar,
                fieldnames=fieldnames,
            )

        def __exit__(self, *exc) -> None:
            self._csvfile.close()

        def __repr__(self) -> str:
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

        def __init__(self, json_file_path: Path, config: dict = {}) -> None:
            super().__init__()
            assert_readable(json_file_path)
            self._json = json_file_path.absolute()
            self._init_source(self._json)

        def __enter__(self) -> object:
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

        def __exit__(self, *exc) -> None:
            pass

        def __repr__(self) -> str:
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

        def __init__(self, xml_file_path: Path, config: dict = {}) -> None:
            super().__init__()
            assert_readable(xml_file_path)
            self._xml: Path = xml_file_path.absolute()
            self._init_source(self._xml)

        def __enter__(self) -> object:
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

        def __exit__(self, *exc) -> None:
            pass

        def __repr__(self) -> str:
            return f"XMLFileSource('{self._xml}')"

    SourceFactory.map("eml", "text/xml")
    SourceFactory.register("text/xml", XMLFileSource)
    # wrong, yet useful mime for xml:
    SourceFactory.register("application/xml", XMLFileSource)
except ImportError:
    log.warning("Python XML module not available -- disabling XML support!")
