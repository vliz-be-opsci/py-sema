from logging import getLogger

from .rdffiles import (
    FORMAT_TO_MIME,
    SUFFIX_TO_FORMAT,
    mime_from_filepath,
    mime_from_format,
)

log = getLogger(__name__)


EXTRA_MIME_KEYS = {
    "application/json": ["json"],
    "text/html": ["html", "htm"],
}

EXTRA_KEY_TO_MIME_MAP = {}
for sfx, fmt in SUFFIX_TO_FORMAT.items():
    EXTRA_KEY_TO_MIME_MAP[sfx[1:]] = FORMAT_TO_MIME[fmt]
for mime, keys in EXTRA_MIME_KEYS.items():
    for key in keys:
        EXTRA_KEY_TO_MIME_MAP[key] = mime


def to_mimetype(key: str) -> str:
    if len(key.split("/")) == 2:
        return key  # already a mime type
    log.debug(f"finding mime for {key=}")
    mt: str = None
    mt = mime_from_format(key)
    if mt:
        log.debug(f"found from format {mt=}")
        return mt
    # else
    mt = mime_from_filepath(key)
    if mt:
        log.debug(f"found from filepath {mt=}")
        return mt
    # else
    mt = EXTRA_KEY_TO_MIME_MAP.get(key, None)
    log.debug(f"found at last {mt=}")
    return mt