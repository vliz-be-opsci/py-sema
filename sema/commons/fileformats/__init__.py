"""fileformats

.. module:: store
:platform: Unix, Windows
:synopsis: A set of simple helper functions to determine the format of typical RDF files

.. moduleauthor:: "Open Science Team VLIZ vzw" <opsci@vliz.be>
"""
from .rdffiles import format_from_filename, mime_from_filename, mime_to_format, is_supported_rdffilename, is_supported_rdffile_suffix


__ALL__ = ["format_from_filename", "mime_from_filename", "mime_to_format", "is_supported_rdffilename", "is_supported_rdffile_suffix"]
