import logging
import re
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

import yaml
from rdflib.namespace import NamespaceManager
from rdflib.plugins.sparql.parser import parseQuery

from sema.harvest.store import RDFStoreAccess

from .helper import makeNSM, resolve_ppaths, resolve_sparql

log = logging.getLogger(__name__)


def relative_pathname(subpath: Path, ancestorpath: Path) -> str:
    """gives the relative part pointing to the subpath from the ancestorpath"""
    return str(subpath.absolute().relative_to(ancestorpath.absolute()))


class Task:
    """
    A task to harvest
    This task contains the following:
    - SubjectDefinition class: a class that defines the subjects
    - AssertPathSet class: a class that contains a list of AssertPath objects
    """

    def __init__(self, task):
        """
        Initialise the task

        :param task: The task.
        :type task: dict
        """
        self.task = task

    @property
    def subject_definition(self):
        return self.task["subject_definition"]

    @property
    def assert_path_set(self):
        return self.task["assert_path_set"]


class SubjectDefinition(ABC):
    @abstractmethod
    def list_subjects(self) -> list[str]:
        pass


class LiteralSubjectDefinition(SubjectDefinition):
    """
    A subject definition that is a list of strings
    """

    def __init__(self, subjects):
        """
        Initialise the literal subject definition

        :param subjects: The subjects.
        :type subjects: list[str]
        """
        self.subjects = subjects

    def list_subjects(self) -> list[str]:
        """
        Get the subjects

        :return: list[str]
        :rtype: list[str]
        """
        return self.subjects


class SPARQLSubjectDefinition(SubjectDefinition):
    """
    A subject definition that is a SPARQL query
    """

    def __init__(
        self,
        NSM: NamespaceManager,
        SPARQL=str,
        rdf_store_access=RDFStoreAccess,
    ):
        """
        Initialise the SPARQL subject definition

        :param SPARQL: The SPARQL query.
        :type SPARQL: str
        :param targetstore: The target store.
        :type targetstore: TargetStore
        """
        log.debug("init SPARQL subjects")
        log.debug(f"{NSM=}")
        self.NSM = NSM
        self.sparql = resolve_sparql(SPARQL, self.NSM)
        self.rdf_store_access = rdf_store_access

    def list_subjects(self) -> list[str]:
        """
        Get the subjects

        :return: list[str]
        :rtype: list[str]
        """
        return self._get_subjects(self.sparql, self.rdf_store_access)

    def _get_subjects(self, SPARQL=str, rdf_store_access=RDFStoreAccess):
        log.debug("getting subjects")
        return rdf_store_access.select_subjects(SPARQL)


class AssertPathSet:
    """
    A set/list of assert paths
    """

    def __init__(self, NSM: NamespaceManager, assert_paths: List[str]):
        """
        Initialise the assert path set

        :param assert_path_set: The set of assert paths.
        :type assert_path_set: list[AssertPath]
        """
        self.NSM = NSM
        self.pre_assert_paths = resolve_ppaths(assert_paths, self.NSM)
        self.assert_paths = [AssertPath(p) for p in self.pre_assert_paths]

    def list_assertion_paths(self) -> List:
        """
        Get the assertion paths

        :return: list[AssertPath]
        :rtype: list[AssertPath]
        """
        return self.assert_paths


class AssertPath:
    """
    A path to assert.
    This class contains the following:
    - Path_parts: a list of strings
    - max_size: a function to return the len of the list of path_parts
    - get_path_for_depth(): a function that returns a path at a given depth
    """

    def __init__(self, assert_path=str):
        """
        Initialise the assert path

        :param assert_path: The path to assert.
        :type assert_path: str
        """
        self.path_parts = self._make_path_parts(assert_path)

    def get_path_parts(self):
        """
        Get the path parts

        return: list[str]
        rtype: list[str]
        """
        return self.path_parts

    def get_max_size(self):
        """
        Get the max size

        return: int
        rtype: int
        """
        return len(self.path_parts)

    def get_path_for_depth(self, depth):
        """
        Get a concatination of the path parts up to a given depth

        return: str
        rtype: str
        """
        return "/".join(self.path_parts[:depth])

    def _make_path_parts(self, assert_path):
        """
        Make the path parts by splitting the path string on regex expression
        """
        REGEXP = r"\s*/\s*(?![^<]*>)"

        # split the path on the regex expression
        return re.split(REGEXP, assert_path)


class Config:
    """
    Configuration for the harvest
    This class contains the following:
        - NSM: NamespaceManager object from rdflib
        - tasks: a list of tasks
        - configname: a string
    """

    def __init__(self, config):
        """
        Initialise the  config.

        :param config: The configuration for the config.
        :type config: dict
        :return: A Config object.
        :rtype: Config
        """
        self.config = config

    def get_config(self):
        return self.config

    @property
    def NSM(self):
        return self.config["NSM"]

    @property
    def tasks(self):
        return self.config["tasks"]

    @property
    def configname(self):
        return self.config["configname"]


class ConfigBuilder:
    def __init__(
        self, rdf_store_access: RDFStoreAccess, config_folder: str = ""
    ):
        """
        Initialize the ConfigBuilder.

        :param rdf_store_access: The RDF store access.
        :type rdf_store_access: RDFStoreAccess
        :param config_folder: The folder containing the config files.
        :type config_folder: str
        :return: A ConfigBuilder object.
        :rtype: ConfigBuilder
        """
        if config_folder is None:
            config_folder = Path("config")
            log.warning(
                """Config folder is None,
                using current working directory as config folder"""
            )
        self.config_files_folder = Path(config_folder)
        self._rdf_store_access = rdf_store_access
        log.debug("ConfigBuilder initialized")

    def build_from_config(self, config_name=str):
        """
        Build a Config from a given config file.

        :param config_name: The name of the config file.
        :type config_name: str
        :return: A Config object.
        :rtype: Config
        """
        config_file = str(Path.cwd() / self.config_files_folder / config_name)
        dict_object = self._load_yml_to_dict(config_file)

        relative_name_config = relative_pathname(
            Path(config_file), Path.cwd() / self.config_files_folder
        )

        log.debug(f"{config_file=}")

        return self._makeConfigPartFromDict(dict_object, relative_name_config)

    def build_from_folder(self):
        """
        Build a list of Config objects from a given folder.

        :return: A list of Config objects.
        :rtype: list[Config]
        """
        config_files = self._files_folder()
        configs = []
        for config_file in config_files:
            path_config_file = (
                Path.cwd() / self.config_files_folder / config_file
            )
            log.debug(f"{path_config_file=}")
            dict_object = self._load_yml_to_dict(path_config_file)
            configs.append(
                self._makeConfigPartFromDict(dict_object, config_file)
            )
        return configs

    def _assert_subjects(self, subjects):
        assert isinstance(subjects, dict), "Subjects must be a dictionary"
        assert (
            "literal" in subjects or "SPARQL" in subjects
        ), "Subjects must contain 'literal' or 'SPARQL'"
        for key, value in subjects.items():
            if key == "literal":
                assert isinstance(
                    value, list
                ), "Subjects of type literal must be a list of strings"
                for subject in value:
                    assert isinstance(
                        subject, str
                    ), "Subjects of type literal must be a list of strings"
            if key == "SPARQL":
                assert isinstance(
                    value, str
                ), "Subjects of type SPARQL must be a string"
                self._assert_valid_sparql_syntax(value)
        # Add more assertions as needed...

    def _assert_valid_sparql_syntax(self, sparql_query):
        parseQuery(sparql_query)
        assert isinstance(sparql_query, str), "SPARQL query must be a string"
        # Add more assertions as needed...

    def _files_folder(self):
        return [
            f.name
            for f in Path(self.config_files_folder).rglob("*")
            if f.is_file() and f.name.endswith((".yml", ".yaml"))
        ]

    def _load_yml_to_dict(self, file):
        with open(file, "r") as stream:
            try:
                return yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                log.exception(exc)

    def _makeConfigPartFromDict(
        self,
        dict_object,
        name_config: str = "default",
        # TODO reconsider this "default" for name_config - not self-explaining
    ):
        log.debug(f"Making Config from dict for {name_config}")
        # make it so that the assertions are always checked for lowercase
        # TODO - apply this as a general rule on the level of the yml load
        #  thus ensuring that it applies across the board
        #  and that users know the yml keys are in fact ignoring case
        dict_object = {k.lower(): v for k, v in dict_object.items()}
        assert (
            "snooze-till-graph-age-minutes" in dict_object
        ), "snooze-till-graph-age-minutes must be defined"
        assert "assert" in dict_object, "assert must be defined"
        for assert_task in dict_object["assert"]:
            self._assert_subjects(assert_task["subjects"])
        # Add more assertions as needed...
        try:
            # function here to check if the snooze-till-graph-age-minutes
            # if older then the last modified date of the admin graph
            # if it is older then the last modified date
            # of the admin graph then we can continue
            # if it is not older then the last modified date
            # of the admin graph then we can snooze the config
            if not self._check_snooze(
                dict_object["snooze-till-graph-age-minutes"],
                name_config,
            ):
                log.info(
                    f"""{name_config=} snoozed for
                    {dict_object['snooze-till-graph-age-minutes']} minutes
                    """
                )
                return
        except Exception as e:
            log.exception(e)
            log.warning(f"{e}")

        self.NSM = makeNSM(dict_object["prefix"])

        config = {
            "configname": name_config,
            "NSM": self.NSM,
            "tasks": [
                Task(
                    {
                        "subject_definition": (
                            LiteralSubjectDefinition(
                                assert_task["subjects"]["literal"]
                            )
                            if "literal" in assert_task["subjects"]
                            else SPARQLSubjectDefinition(
                                self.NSM,
                                assert_task["subjects"]["SPARQL"],
                                self._rdf_store_access,
                            )
                        ),
                        "assert_path_set": AssertPathSet(
                            self.NSM, assert_task["paths"]
                        ),
                    }
                )
                for assert_task in dict_object["assert"]
            ],
        }

        return Config(config)

    def _check_snooze(self, snooze_time, name_config):
        try:
            # First get the lastmod_ts of the named graph
            # if there is one and check if that one is older
            # then the lastmod of the config file
            config_lastmod_file = Path(self.config_files_folder) / name_config
            lastmod_file = config_lastmod_file.stat().st_mtime

            log.debug(
                f"""Last modified date of config file:
                    {name_config}: {lastmod_file}
                """
            )

            lastmod_config = self._rdf_store_access.lastmod_ts_for_config(
                name_config
            )
            if lastmod_config is not None:
                if lastmod_file > lastmod_config.timestamp():
                    log.debug(
                        """Config file is newer then the last modified
                        of the config in the admin graph. Bypassing snooze."""
                    )
                    # if the config file is newer then the last modified
                    # of the config in the admin graph then we can bypass
                    # the snooze and continue
                    return True

            log.debug(
                f"""Last modified of config in admin graph:
                {name_config}: {lastmod_config}"""
            )
            log.debug(
                f"Checking if config {name_config}"
                f"is older then {snooze_time} minutes"
            )
            return not self._rdf_store_access.verify_max_age_of_config(
                name_config, snooze_time
            )
        except Exception as e:
            log.exception(e)
            return True
