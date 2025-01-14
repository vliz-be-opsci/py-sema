import pytest

from sema.commons.web import parse_header


@pytest.mark.parametrize(
    "mode, content, expected_main, expected_params",
    [
        ("content-type", "application/json", "application/json", {}),
        (
            "content-type",
            'text/plain; charset="utf8"',
            "text/plain",
            {"charset": "utf8"},
        ),
        (
            "content-type",
            'main/subtype; key="value"; other="info"',
            "main/subtype",
            {"key": "value", "other": "info"},
        ),
        (
            "content-disposition",
            'Attachment; filename="name.extension"',
            "attachment",
            {"filename": "name.extension"},
        ),
        ("content-type", "", None, None),
    ],
)
def test_parse_headers(
    mode: str,
    content: str,
    expected_main: str | None,
    expected_params: dict[str, str] | None,
) -> None:
    main, params = parse_header(content, mode)
    assert main == expected_main, f"Expected {expected_main}, but got {main}"
    assert (
        params == expected_params
    ), f"Expected {expected_params}, but got {params}"


@pytest.mark.parametrize(
    ("mode", "content", "expected_error", "expected_result"),
    [
        ("invalid-mode", "some-content", "mode should be one of", None),
        ("content-type", "invalidtype;extra", None, ("text/plain", {"extra": ""})),
    ],
)
def test_parse_headers_errors(
    mode: str,
    content: str,
    expected_error: str | None,
    expected_result: tuple[str, dict[str, str]] | None,
) -> None:
    if expected_error:
        with pytest.raises(ValueError, match=expected_error):
            parse_header(content, mode)
            raise AssertionError("There should have been an error")
    else:
        result = parse_header(content, mode)
        assert result == expected_result, f"Expected {expected_result}, but got {result}"
