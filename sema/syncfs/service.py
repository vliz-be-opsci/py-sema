from datetime import datetime, timezone
from logging import getLogger
from pathlib import Path
from typing import Dict

from rdflib import Graph

from sema.commons.fileformats import (
    format_from_filepath,
    is_supported_rdffilepath,
)
from sema.commons.glob import getMatchingGlobPaths
from sema.commons.service import ServiceBase, ServiceResult
from sema.commons.store import (
    GraphNameMapper,
    MemoryRDFStore,
    RDFStore,
    URIRDFStore,
)

log = getLogger(__name__)
UTC_tz = timezone.utc
DEFAULT_URN_BASE = "urn:sync:"


class SyncFsResult(ServiceResult):
    """Result of the syncfs service"""

    def __init__(self) -> None:
        super().__init__()
        self._success = False

    @property
    def success(self) -> bool:
        return self._success

    @success.setter
    def success(self, value: bool) -> None:
        self._success = value


def get_lastmod_by_fname(from_path: Path) -> Dict[str, datetime]:
    """lists all files in path with their lastmod timestamp

    :param from_path: root to list contents from
    :type from_path: Path
    :returns: dict of fnames + their lastmod on disk
    :rtype: Dict[ str, datetime ]
    """
    return {
        str(p): datetime.fromtimestamp(p.stat().st_mtime, UTC_tz)
        for p in getMatchingGlobPaths(
            from_path, onlyFiles=True, makeRelative=False
        )
        if is_supported_rdffilepath(p)
    }


def load_graph_fpath(fpath: Path, format: str | None = None) -> Graph:
    """loads content of file at fpath into a graph
    :param fpath: path of file to load
    :type fpath: Path
    :param format: rdflib format to apply when parsing the file
        optional - if left None, autodetected base on file-extension
    :type format: str
    :returns: the graph containing the triples from the file
    :rtype: Graph
    """
    format = format or format_from_filepath(fpath)
    graph: Graph = Graph().parse(location=str(fpath), format=format)
    return graph


def relative_pathname(subpath: Path, ancestorpath: Path) -> str:
    """gives the relative part pointing to the subpath from the ancestorpath"""
    return str(subpath.absolute().relative_to(ancestorpath.absolute()))


def sync_removal(store: RDFStore, fpath: Path, rootpath: Path) -> None:
    """Handles removal event triggered when file on disk got removed.
    (i.e. has a matching graph in store, but no longer exists).
    Resolution should ensure removal of the matching graph in the store

    :param store: target store where removal should happen
    :type store: RDFStore
    :param fpath: file-path of file that no longer exists
    :type fpath: Path
    :param rootpath: root containing the sub fpath
    :type rootpath: Path
    :param nmapper: convertor between fnames and graphnames to be used
    :type nmapper: GraphFileNameMapper
    :rtype: None
    """
    key: str = relative_pathname(fpath, rootpath)
    store.drop_graph_for_key(key)
    store.forget_graph_for_key(key)


def sync_addition(store: RDFStore, fpath: Path, rootpath: Path) -> None:
    """Handles addition event triggered when a new file on disk appeared.
    (i.e. has not yet a matching graph in store).
    Resolution should ensure addition of the matching graph in the store

    :param store: target store where addition should happen
    :type store: RDFStore
    :param fpath: file-path of file that was added
    :type fpath: Path
    :param rootpath: root containing the sub fpath
    :type rootpath: Path
    :param nmapper: convertor between fnames and graphnames to be used
    :type nmapper: GraphFileNameMapper
    :rtype: None
    """
    key: str = relative_pathname(fpath, rootpath)
    g: Graph = load_graph_fpath(fpath)
    store.insert_for_key(g, key)


def sync_update(store: RDFStore, fpath: Path, rootpath: Path) -> None:
    """Handles update event triggered when a file on disk was changed
    (i.e. has a more recent lastmod then matching graph in store).
    Resolution should ensure addition of the matching graph in the store

    :param store: target store where update should happen
    :type store: RDFStore
    :param fpath: file-pathname of file that was updated
    :type fpath: Path
    :param rootpath: root containing the sub fpath
    :type rootpath: Path
    :param nmapper: convertor between fnames and graphnames to be used
    :type nmapper: GraphFileNameMapper
    :rtype: None
    """
    key: str = relative_pathname(fpath, rootpath)
    store.drop_graph_for_key(key)
    g: Graph = load_graph_fpath(fpath)
    store.insert_for_key(g, key)


def perform_sync(from_path: Path, to_store: RDFStore) -> None:
    """synchronizes found rdf-dump files
    in the from_path to the RDFStore specified

    :param from_path: folder path to sync from
    :type from_path: Path
    :param to_store: rdf store target for the sync operation
    :type to_store: RDFStore
    :param nmapper: convertor between fnames and graphnames to be used
    :type nmapper: GraphFileNameMapper
    :rtype: None
    """
    known_relnames_in_store = to_store.keys
    current_lastmod_by_fname = get_lastmod_by_fname(from_path)
    log.debug(f"current_lastmod_by_fname: {current_lastmod_by_fname}")
    for relname in known_relnames_in_store:
        fname = str(from_path / relname)
        if fname not in current_lastmod_by_fname:
            log.debug(f"old file {fname} no longer exists")
            sync_removal(to_store, Path(fname), from_path)
    for fname, lastmod in current_lastmod_by_fname.items():
        relname = relative_pathname(Path(fname), from_path)
        if relname not in known_relnames_in_store:
            log.debug(f"new file {fname} with lastmod {lastmod}")
            sync_addition(to_store, Path(fname), from_path)
        elif not to_store.verify_max_age_of_key(
            relname, reference_time=lastmod
        ):
            log.debug(f"updated file {fname} with lastmod {lastmod}")
            sync_update(to_store, Path(fname), from_path)
        else:
            log.debug(f"skip file {fname} with lastmod {lastmod} - unchanged")


class SyncFsTriples(ServiceBase):
    """Process-wrapper-pattern for easy inclusion in other contexts."""

    def __init__(
        self,
        root: str,
        named_graph_base: str = DEFAULT_URN_BASE,
        read_uri: str | None = None,
        write_uri: str | None = None,
    ) -> None:
        """Creates the process-wrapper instance

        :param root: path to te folder to check for
        nested rdf dump files to be synced up.
        :type root: str
        :param named_graph_base: the base to be used
        for building named_graphs in the conversion
            optional - defaults to DEFAULT_URN_BASE = "urn:sync:"
        :type named_graph_base: str
        :param read_uri: uri to the triple-store to sync to
            optional - defaults to None - leading to using an in-MemoryStore
        :type read_uri: str
        :param write_uri: uri for write operations to the triple store
            optional - defaults to None - leading
            to a store that can only be read from
        :type write_uri: str
        """
        super().__init__()
        self.source_path: Path = Path(root)
        assert self.source_path.exists(), (
            "cannot sync a source-path " + str(root) + " that does not exist."
        )
        assert self.source_path.is_dir(), (
            "source-path " + str(root) + " should be a folder."
        )
        nmapper: GraphNameMapper = GraphNameMapper(base=named_graph_base)
        self.rdfstore: RDFStore | None = None
        if not read_uri:
            self.rdfstore = MemoryRDFStore(mapper=nmapper)
        else:
            self.rdfstore = URIRDFStore(read_uri, write_uri, mapper=nmapper)

        self._result = SyncFsResult()

    def process(self) -> None:
        """executes the SyncFs command"""
        try:
            if self.rdfstore:
                perform_sync(
                    from_path=self.source_path,
                    to_store=self.rdfstore,
                )
                self._result.success = True
        except FileNotFoundError as e:
            log.error("Source file not found during sync", exc_info=e)
            self._result.success = False
        except PermissionError as e:
            log.error("Permission denied during sync", exc_info=e)
            self._result.success = False
        except Exception as e:
            log.exception("Unexpected error during sync", exc_info=e)
            self._result.success = False
            raise  # Re-raise unexpected exceptions
