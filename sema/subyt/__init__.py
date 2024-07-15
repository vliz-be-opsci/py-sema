""" subyt

.. submodule:: subyt
    :synopsis: python implementation for Semantic Uplifting by Templates.
        Helps to produces triples out of various datasources
    :noindex:

.. moduleauthor:: "Open Science Team VLIZ vzw" <opsci@vliz.be>

"""

from .api import Generator, GeneratorSettings, Sink, Source
from .j2.generator import JinjaBasedGenerator
from .sinks import SinkFactory
from .sources import SourceFactory
from .subyt import Subyt

__all__ = [
    "Sink",
    "Source",
    "GeneratorSettings",
    "Generator",
    "SourceFactory",
    "SinkFactory",
    "JinjaBasedGenerator",
    "Subyt",
]
