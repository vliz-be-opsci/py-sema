from email.message import EmailMessage


def parse_header(content: str, mode: str = "content-type") -> tuple[str, dict[str, str]]:
    # deal with empty content
    if content is None:
        return None, None
    content = content.strip()
    if not content:
        return None, None
    # deal with actual content
    msg = EmailMessage()
    mode = mode.lower()
    msg[mode] = content
    if mode == "content-type":
        main = msg.get_content_type()
    elif mode == "content-disposition":
        main = msg.get_content_disposition()
    else:
        raise ValueError(
            "mode should be one of 'content-type' (default) "
            "or 'content-disposition'")
    params = msg[mode].params
    return main, params


def get_parsed_header(headers, key) -> tuple[str, dict[str, str]]:
    return parse_header(headers.get(key, None), key)
