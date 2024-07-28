from logging import getLogger

from .discovery import DiscoveryService

log = getLogger(__name__)


def get_graph_for_format(subject_url: str, formats: str):
    if not subject_url:
        # note: harvest will call this even for blanknodes
        return None

    service = DiscoveryService(
        subject_uri=subject_url,
        request_mimes=",".join(formats),
    )

    r, t = service.process()
    return r.graph if r else None
