"""discovery

.. submodule:: discovery
:platform: Unix, Windows
:synopsis: A library for discovering triples from a given URL

.. moduleauthor:: "Open Science Team VLIZ vzw" <opsci@vliz.be>
"""

from .discovery import discover_subject, DiscoveryService, DiscoveryResult, DiscoveryTrace

__all__ = [
    "discover_subject",
    "DiscoveryService",
    "DiscoveryResult",
    "DiscoveryTrace",
]
