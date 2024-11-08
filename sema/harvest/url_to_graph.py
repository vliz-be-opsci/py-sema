from logging import getLogger
from rdflib import Graph
from sema.discovery import discover_subject

log = getLogger(__name__)


def get_graph_for_format(subject_url: str, formats: list[str]) -> Graph | None:
    return discover_subject(subject_url, formats) if subject_url else None
