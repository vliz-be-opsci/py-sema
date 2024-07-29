"""discovery

.. submodule:: discovery
:platform: Unix, Windows
:synopsis: A library for discovering triples from a given URL

.. moduleauthor:: "Open Science Team VLIZ vzw" <opsci@vliz.be>
"""

from .discovery import (
    DiscoveryResult,
    DiscoveryService,
    DiscoveryTrace,
    discover_subject,
)

__all__ = [
    "discover_subject",
    "DiscoveryService",
    "DiscoveryResult",
    "DiscoveryTrace",
]
