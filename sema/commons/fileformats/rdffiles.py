from pathlib import Path

SUFFIX_TO_FORMAT: dict = {
    ".ttl": "turtle",
    ".turtle": "turtle",
    ".jsonld": "json-ld",
    ".json-ld": "json-ld",
    ".json": "json-ld",
    ".rdf": "xml",
    ".n3": "n3",
}
SUPPORTED_RDFFILE_SUFFIXES: set = set(SUFFIX_TO_FORMAT.keys())
MIME_TO_FORMAT: dict = {
    "application/ld+json": "json-ld",
    "application/rdf+xml": "xml",
    "application/n-triples": "nt",
    "text/turtle": "turtle",
    "text/n3": "n3",
    "text/html": "html",
}
FORMAT_TO_MIME: dict = {v: k for k, v in MIME_TO_FORMAT.items()}


def mime_to_format(mime: str, fallback: str | None = None) -> str:
    return MIME_TO_FORMAT.get(mime, fallback)


def mime_from_format(format: str, fallback: str | None = None) -> str:
    return FORMAT_TO_MIME.get(format, fallback)


def format_from_filepath(
    filename: str | Path, fallback: str | None = None
) -> str:
    suffix: str = Path(filename).suffix
    return SUFFIX_TO_FORMAT.get(suffix, fallback)


def mime_from_filepath(
    filename: str | Path, fallback: str | None = None
) -> str | None:
    format = format_from_filepath(filename, None)
    if format is None:
        return fallback
    # else
    return FORMAT_TO_MIME.get(format, fallback)


def is_supported_rdffilepath(filename: str) -> bool:
    sfx: str = Path(filename).suffix
    return is_supported_rdffile_suffix(sfx)


def is_supported_rdffile_suffix(sfx: str) -> bool:
    return sfx in SUPPORTED_RDFFILE_SUFFIXES
