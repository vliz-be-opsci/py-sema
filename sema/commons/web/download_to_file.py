import base64
import cgi
import os
from hashlib import sha256
from pathlib import Path

from .httpsession import make_http_session


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
        mime_type=cgi.parse(response.headers.get("Content-Type"))[0],
        profile=headers.get("Accept-profile", None),
        content=content,
    )
    return filename


def save_web_content(
    dump_path: Path,
    filename: str,
    url: str,
    mime_type: str,
    profile: str,
    content: str,
) -> None:
    assert url is not None
    mime_type = mime_type or "application/octet-stream"
    profile = profile or ""
    filename = filename or make_unique_filename(url, mime_type, profile)

    filepath = dump_path / filename
    with open(filepath, "w") as out:
        out.write(content)
    # remember what this file is for
    os.setxattr(filepath, "user.web.url", url.encode("utf-8"))
    os.setxattr(filepath, "user.web.mime_type", mime_type.encode("utf-8"))
    os.setxattr(filepath, "user.web.profile", profile.encode("utf-8"))


def make_unique_filename(*args) -> str:
    # aggregate any input as bytes, hash them
    b = "".join(str(a) for a in args).encode("utf-8")
    # hash - b64 safe encode - truncate - byte to string decode - return
    return base64.urlsafe_b64encode(sha256(b).digest())[:13].decode()
