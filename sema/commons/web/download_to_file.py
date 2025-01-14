import base64
import os
from hashlib import sha256
from pathlib import Path
from typing import Tuple
from urllib.parse import urlparse

from sema.commons.fileformats import suffix_for_mime

from .httpsession import make_http_session
from .parse_headers import get_parsed_header


def download_to_file(
    dump_path: str, filename: str, url: str, headers: dict = {}
) -> str:
    session = make_http_session()
    response = session.get(url, headers=headers)
    response.raise_for_status()
    content = response.text
    save_web_content(
        dump_path=Path(dump_path),
        filename=filename,
        url=url,
        mime_type=get_parsed_header(response.headers, "Content-Type")[0],
        profile=headers.get("Accept-profile", None),
        content=content,
    )
    return filename


def save_web_content(
    dump_path: Path,
    filename: str | None,
    url: str,
    mime_type: str,
    profile: str | None,
    content: str,
) -> str:
    assert url is not None
    mime_type = mime_type or "application/octet-stream"
    profile = profile or ""
    filename = filename or make_unique_filename(url, mime_type, profile)

    filepath = dump_path / filename
    with open(filepath, "w") as out:
        out.write(content)
    # remember what this file is for
    os.setxattr(filepath, "user.web.url", url.encode("utf-8"))  # type: ignore
    os.setxattr(filepath, "user.web.mime_type", mime_type.encode("utf-8"))  # type: ignore # noqa
    os.setxattr(filepath, "user.web.profile", profile.encode("utf-8"))  # type: ignore # noqa
    return str(filepath.absolute())


def make_unique_filename(url: str, mime_type: str, *args) -> str:
    base = args_to_unique(url, mime_type, *args)
    id, suffix = extract_name_parts(url, mime_type)
    return f"{base}-{id}{suffix}"


def extract_name_parts(url: str, mime_type: str) -> Tuple[str, str]:
    suffix = suffix_for_mime(mime_type)
    # urlparse - drop .ext - split - remove empty - keep max two - rejoin
    id = "-".join(
        [p for p in urlparse(url).path.split(".")[0].split("/") if p][-2:]
    )
    return id, suffix


def args_to_unique(*args) -> str:
    N: int = 13  # number of bytes of hash to keep
    # aggregate any input as bytes, hash them
    b = "".join(str(a) for a in args).encode("utf-8")
    # hash - b64 safe encode - truncate - byte to string decode - return
    return base64.urlsafe_b64encode(sha256(b).digest())[:N].decode()
