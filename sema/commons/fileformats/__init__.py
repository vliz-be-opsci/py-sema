"""fileformats

.. module:: store
:platform: Unix, Windows
:synopsis: A set of simple helper functions to determine the format
    of typical RDF files

.. moduleauthor:: "Open Science Team VLIZ vzw" <opsci@vliz.be>
"""

from .rdffiles import (
    format_from_filepath,
    is_supported_rdffile_suffix,
    is_supported_rdffilepath,
    mime_from_filepath,
    mime_to_format,
)

__all__ = [
    "format_from_filepath",
    "mime_from_filepath",
    "mime_to_format",
    "is_supported_rdffilepath",
    "is_supported_rdffile_suffix",
]
