from logging import getLogger
from sema.discovery import discover_subject

log = getLogger(__name__)


def get_graph_for_format(subject_url: str, formats: str):
    return discover_subject(subject_url, formats) if subject_url else None
