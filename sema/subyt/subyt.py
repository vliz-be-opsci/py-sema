import logging
from pathlib import Path
from typing import Dict

from sema.commons.service import ServiceBase, ServiceResult, ServiceTrace

from .api import GeneratorSettings
from .j2.generator import JinjaBasedGenerator
from .sinks import SinkFactory
from .sources import SourceFactory

log = logging.getLogger(__name__)


class SubytResult(ServiceResult):
    """Result of the subyt service"""

    def __init__(self):
        self._success = False

    @property
    def success(self) -> bool:
        return self._success


class SubytTrace(ServiceTrace):
    """Trace of the subyt service"""

    def toProv(self):
        pass  # TODO - export essential traces into prov-o format // see #63


class Subyt(ServiceBase):
    """The main class for the subyt service."""

    def __init__(
        self,
        *,
        template_name: str,
        template_folder: str,
        source: str = None,
        extra_sources: Dict[str, str] = {},
        sink: str = None,
        overwrite_sink: bool | str = True,
        allow_repeated_sink_paths: bool | str = False,
        conditional: bool | str = False,
        variables: Dict[str, str] = {},
        mode: str = "it",
    ) -> None:
        """Initialize the Subyt Service object

        :param template_name: the name of the template to be used,
            this should match a filename in the template_folder
        :type template_name: str
        :param template_folder: the folder where the template is located
        :type template_folder: str
        :param source: the source file to be used
            Can be relative to the current working directory
        :type source: str
        :param extra_sources: other sources to be used
        :type extra_sources: Dict[str, str]
        :param sink: the sink file to be used
            Can be relative to the current working directory
        :type sink: str
        :param overwrite_sink: overwrites the sink file even if it exists
        :type overwrite_sink: bool | str
        :param allow_repeated_sink_paths: allows to repeat sink paths
            # TODO - what does this mean?
        :type allow_repeated_sink_paths: bool | str
        :param conditional: conditional processing only runs the generator
            if source or template fils are newer than the sink file
            Default is False (no conditional processing / always run)
        :type conditional: bool | str
        :param variables: variables to be injected into the templates
        :type variables: Dict[str, str]
        :param mode: the mode to be used
        :type mode: str
        :return: Subyt object
        :rtype: Subyt
        """
        # upfront checks
        assert template_name, "template_name is required"
        assert Path(template_folder).exists(), "template_folder does not exist"

        # actual task inputs
        self.template_name = template_name
        self._inputs = {}
        if source:
            self._inputs.update({"_": SourceFactory.make_source(source)})
        self._inputs.update(
            {
                nm: SourceFactory.make_source(src)
                for nm, src in extra_sources.items()
            }
        )
        self._conditional = bool(conditional)
        self._variables = variables
        self._generator_settings = GeneratorSettings(mode)

        # output options
        self._sink = SinkFactory.make_sink(
            sink, bool(overwrite_sink), bool(allow_repeated_sink_paths)
        )
        log.debug(f"Subyt initialized with {self.__dict__}")

        # internal statGraph()e
        self._generator = JinjaBasedGenerator(template_folder)
        self._result, self._trace = None, None

    def process(self) -> None:
        assert self._result is None, "Service already processed"
        self._result = SubytResult()
        self._trace = SubytTrace()

        self._generator.process(
            template_name=self.template_name,
            inputs=self._inputs,
            generator_settings=self._generator_settings,
            sink=self._sink,
            vars_dict=self._variables,
            conditional=self._conditional,
        )
        self._result._success = True

        return self._result, self._trace
