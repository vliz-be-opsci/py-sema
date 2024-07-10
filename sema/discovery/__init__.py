"""discovery

.. submodule:: discovery
:platform: Unix, Windows
:synopsis: A library for discovering triples from a given URL

.. moduleauthor:: "Open Science Team VLIZ vzw" <opsci@vliz.be>
"""

from .url_to_graph import get_graph_for_format

__all__ = ["get_graph_for_format"]
