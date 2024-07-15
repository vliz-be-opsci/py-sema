import logging

from .api import GeneratorSettings
from .j2.generator import JinjaBasedGenerator
from .sinks import SinkFactory
from .sources import SourceFactory

log = logging.getLogger(__name__)


class Subyt:
    def __init__(
        self,
        template_name: str,
        template_folder: str,
        source: str = None,
        extra_sources: dict = {},
        sink: str = None,
        overwrite_sink: bool = True,
        allow_repeated_sink_paths: bool = False,
        conditional: bool = False,
        variables: dict = {},
        mode: str = "it",
    ) -> None:
        self.template_name = template_name
        self.service = JinjaBasedGenerator(template_folder)
        self.sources = {}
        if source:
            self.sources.update({"_": SourceFactory.make_source(source)})
        self.sources.update(
            {k: SourceFactory.make_source(v) for k, v in extra_sources.items()}
        )
        self.sink = SinkFactory.make_sink(
            sink, overwrite_sink, allow_repeated_sink_paths
        )
        self.conditional = conditional
        self.variables = variables
        self.generator_settings = GeneratorSettings(mode)
        log.debug(f"Subyt initialized with {self.__dict__}")

    def process(self) -> None:
        self.service.process(
            template_name=self.template_name,
            inputs=self.sources,
            generator_settings=self.generator_settings,
            sink=self.sink,
            vars_dict=self.variables,
            conditional=self.conditional,
        )
