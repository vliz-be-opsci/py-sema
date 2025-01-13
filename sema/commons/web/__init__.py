from .conneg import ConnegEvaluation, FoundVariants
from .download_to_file import download_to_file, save_web_content
from .httpsession import make_http_session
from .parse_headers import get_parsed_header, parse_header

__all__ = [
    "make_http_session",
    "ConnegEvaluation",
    "FoundVariants",
    "download_to_file",
    "save_web_content",
    "get_parsed_header",
    "parse_header",
]
