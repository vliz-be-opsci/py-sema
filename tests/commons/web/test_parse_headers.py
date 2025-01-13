import pytest
from sema.commons.web import parse_header


@pytest.mark.parametrize("mode, content, expected_main, expected_params", [
    ("content-type", "application/json", "application/json", {}),
    ("content-type", 'text/plain; charset="utf8"', "text/plain", {"charset": "utf8"}),
    ("content-type", 'main/subtype; key="value"; other="info"', "main/subtype", {"key": "value", "other": "info"}),
    ("content-disposition", 'Attachment; filename="name.extension"', "attachment", {"filename": "name.extension"}),
    ("content-type", "", None, None),
],)
def test_parse_headers(mode, content, expected_main, expected_params):
    main, params = parse_header(content, mode)
    assert main == expected_main, f"Expected {expected_main}, but got {main}"
    assert params == expected_params, f"Expected {expected_params}, but got {params}"
