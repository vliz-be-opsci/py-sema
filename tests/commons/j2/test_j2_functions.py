from datetime import date, datetime
from typing import Callable

import pytest

from sema.commons.j2.j2_functions import Filters, Functions, ValueMapper

uritexpand_fmt = Functions.all()["uritexpand"]
regexreplace_fmt = Functions.all()["regexreplace"]
map_build_fmt = Functions.all()["map"]
xsd_fmt = Filters.all()["xsd"]
uri_fmt = Filters.all()["uri"]


def test_xsd_fmt() -> None:
    assert xsd_fmt is not None, "xsd_fmt function not found"
    assert isinstance(xsd_fmt, Callable), "xsd_fmt function not callable"


def assertFormat(
    content: any,
    type_name: str,
    expected: str,
    quote: str | None = "'",
) -> None:
    format = xsd_fmt(content, type_name, quote)
    assert format == expected, (
        f"unexpected {type_name} format for {content} using {quote}: "
        f"{format} != {expected}"
    )


def assertCase(
    short_name: str, case: tuple, pfx_variants: list[str] | None = None
) -> None:
    content, expected, *quote = case
    quote = quote[0] if quote else "'"
    if pfx_variants is None:
        pfx_variants = ["xsd:"]  # default is to apply xsd: prefix
    pfx_variants.append("")  # in all cases we should also test without prefix
    for pfx in pfx_variants:
        assertFormat(content, pfx + short_name, expected, quote)


@pytest.mark.parametrize(
    "case",
    [
        (("true", '"true"^^xsd:boolean', '"')),
        (("false", '"false"^^xsd:boolean', '"')),
        (("true", "'true'^^xsd:boolean")),
        (("false", "'false'^^xsd:boolean")),
        ((1, "'true'^^xsd:boolean")),
        (("anything", "'true'^^xsd:boolean")),
        ((True, "'true'^^xsd:boolean")),
        ((0, "'false'^^xsd:boolean")),
        ((False, "'false'^^xsd:boolean")),
    ],
)
def test_bool(case: tuple[str, str, str | None]) -> None:
    assertCase("boolean", case)


def test_rigid_bool() -> None:
    # None conversion required before formatting
    with pytest.raises(TypeError):
        xsd_fmt(None, "xsd:boolean")
        raise Exception("None should not be accepted as bool value")

    # [] conversion (empty or not) required before formatting
    with pytest.raises(TypeError):
        xsd_fmt([], "xsd:boolean")
        raise Exception("[] should not be accepted as bool value")

    # {} conversion (empty or not) required before formatting
    with pytest.raises(TypeError):
        xsd_fmt({}, "xsd:boolean")
        raise Exception("{} should not be accepted as bool value")


@pytest.mark.parametrize(
    "case",
    [
        ((1, '"1"^^xsd:integer', '"')),
        ((1, "'1'^^xsd:integer")),
        ((-10, '"-10"^^xsd:integer', '"')),
        ((0, '"0"^^xsd:integer', '"')),
        ((int(1.0), "'1'^^xsd:integer")),
        ((int("001"), "'1'^^xsd:integer")),
        (("1000", "'1000'^^xsd:integer")),
    ],
)
def test_int(case: tuple[str, str, str | None]) -> None:
    assertCase("integer", case)


def test_rigid_int() -> None:
    # leading zero's should be dealth with before formatting
    with pytest.raises(ValueError):
        xsd_fmt("001", "xsd:integer")
        raise Exception(
            "leading zero's should not be accepted in strings for int value"
        )

    # floats should not be accepted
    with pytest.raises(ValueError):
        xsd_fmt(1.0, "xsd:integer")
        raise Exception("floats should not be accepted as int value")

    # floats disguised as strings should not be accepted
    with pytest.raises(ValueError):
        xsd_fmt("1.0", "xsd:integer")
        raise Exception(
            "floats disguised as strings should not be accepted as int value"
        )


@pytest.mark.parametrize(
    "case",
    [
        ((1.0, "'1.0'^^xsd:double")),
        (("1", "'1.0'^^xsd:double")),
        ((1, "'1.0'^^xsd:double")),
        ((float(1), "'1.0'^^xsd:double")),
    ],
)
def test_double(case: tuple[str, str, str | None]) -> None:
    assertCase("double", case)


@pytest.mark.parametrize(
    "case",
    [
        (("1970-05-06", "'1970-05-06'^^xsd:date")),
        ((date.fromisoformat("1970-05-06"), "'1970-05-06'^^xsd:date")),
        ((date(1970, 5, 6), "'1970-05-06'^^xsd:date")),
        (("2021-09-30T16:25:50+02:00", "'2021-09-30'^^xsd:date")),
        (
            (
                datetime.fromisoformat("2021-09-30T16:25:50+02:00").date(),
                "'2021-09-30'^^xsd:date",
            )
        ),
    ],
)
def test_date(case: tuple[str, str, str | None]) -> None:
    assertCase("date", case)


def test_rigid_date() -> None:
    with pytest.raises(TypeError):
        xsd_fmt(datetime.fromisoformat("2021-09-30T16:25:50+02:00"), "date")
        raise Exception("datetime should not be accepted as date value")


@pytest.mark.parametrize(
    "case",
    [
        (
            (
                "2021-09-30T16:25:50+02:00",
                "'2021-09-30T16:25:50+02:00'^^xsd:dateTime",
            )
        ),
        (
            (
                datetime.fromisoformat("2021-09-30T16:25:50+02:00"),
                "'2021-09-30T16:25:50+02:00'^^xsd:dateTime",
            )
        ),
    ],
)
def test_datetime(case: tuple[str, str, str | None]) -> None:
    assertCase("dateTime", case)


@pytest.mark.parametrize(
    "case",
    [
        ((2021, "'2021'^^xsd:gYear")),
        (("2021", "'2021'^^xsd:gYear")),
        ((date(2021, 1, 1), "'2021'^^xsd:gYear")),
        ((12004, "'12004'^^xsd:gYear")),
        ((922, "'0922'^^xsd:gYear")),
        ((-45, "'-0045'^^xsd:gYear")),
    ],
)
def test_gyear(case: tuple[str, str, str | None]) -> None:
    assertCase("gYear", case)


@pytest.mark.parametrize(
    "case",
    [
        ("2021-09", "'2021-09'^^xsd:gYearMonth"),
        (date(2021, 9, 1), "'2021-09'^^xsd:gYearMonth"),
        ("2021-09-30", "'2021-09'^^xsd:gYearMonth"),
        ("922-09-17", "'0922-09'^^xsd:gYearMonth"),
        ("-45-05", "'-0045-05'^^xsd:gYearMonth"),
    ],
)
def test_gyearmonth(case: tuple[str, str, str | None]) -> None:
    assertCase("gYearMonth", case)


@pytest.mark.parametrize(
    "case",
    [
        (
            (
                "https://example.org/for/testing",
                "'https://example.org/for/testing'^^xsd:anyURI",
            )
        ),
        (
            (
                "https://example.org/for/[testing]",
                "'https://example.org/for/%5Btesting%5D'^^xsd:anyURI",
            )
        ),
    ],
)
def test_uri(case: tuple[str, str, str | None]) -> None:
    assertCase("anyURI", case)


@pytest.mark.parametrize(
    "case",
    [
        (("Hello!", '"Hello!"^^xsd:string', '"')),
        (("Hello!", "'Hello!'^^xsd:string")),
        (("'", "'\\''^^xsd:string")),
        (("'", '"\'"^^xsd:string', '"')),
        (('"', "'\"'^^xsd:string")),
        (('"', '"\\""^^xsd:string', '"')),
        ((">'<", "'>\\'<'^^xsd:string")),
        ((">\n<", "'''>\n<'''^^xsd:string")),
        ((">\n<", '""">\n<"""^^xsd:string', '"')),
        (
            (
                "ceci n'est pas une texte",
                "'ceci n\\'est pas une texte'^^xsd:string",
            )
        ),
        (("As \\ said before", "'As \\\\ said before'^^xsd:string")),
    ],
)
def test_string(case: tuple[str, str, str | None]) -> None:
    assertCase("string", case)


def test_lang_string() -> None:
    format = xsd_fmt("Hello!", "@en")
    expected = "'Hello!'@en"
    assert format == expected, "unexpected language-string format"

    format_fr = xsd_fmt("ceci n'est pas une texte", "@fr")
    expected_fr = "'ceci n\\'est pas une texte'@fr"
    assert format_fr == expected_fr, (
        "unexpected language-string format with quote-escapes",
    )

    format_en = xsd_fmt("As \\ said before", "@en")
    expected_en = "'As \\\\ said before'@en"
    assert format_en == expected_en, (
        "unexpected language-string format with backslash-escapes",
    )


def test_uri_fmt() -> None:
    assert uri_fmt is not None, "uri_fmt function not found"
    assert isinstance(uri_fmt, Callable), "uri_fmt function not callable"


def test_nobase() -> None:
    fmt = uri_fmt("https://example.org/[square-brackets]")
    exp = "<https://example.org/%5Bsquare-brackets%5D>"
    assert fmt == exp, "unexpected uri format for nobase"


@pytest.mark.parametrize(
    "case",
    [
        (
            (
                datetime(2024, 1, 13, 11, 48, 29),
                "'2024-01-13T11:48:29'^^xsd:dateTime",
                "'",
            )
        ),
        ((date(2024, 1, 13), "'2024-01-13'^^xsd:date", "'")),
        (("2024-01-13T11:48:29", "'2024-01-13T11:48:29'^^xsd:dateTime", "'")),
        (("2024-01-13", "'2024-01-13'^^xsd:date", "'")),
        (("2024-01", "'2024-01'^^xsd:gYearMonth", "'")),
        (("2024", "'2024'^^xsd:gYear", "'")),
        ((2024, "'2024'^^xsd:gYear", "'")),
    ],
)
def test_auto_date(case: tuple[str, str, str | None]) -> None:
    assertCase("auto-date", case, [])  # no prefix-variants to test


def test_fail_auto_date() -> None:
    with pytest.raises(ValueError):
        xsd_fmt("brol", "auto-date")
        raise Exception(
            "auto-date should not accept strings "
            "that have no meaningfull date format"
        )


@pytest.mark.parametrize(
    "case",
    [
        ((1, "'1'^^xsd:integer", "'")),
        ((1, "'1'^^xsd:integer")),
        (("1", "'1'^^xsd:integer")),
        ((1.0, "'1.0'^^xsd:double", "'")),
        ((1.0, "'1.0'^^xsd:double")),
        (("1.0", "'1.0'^^xsd:double")),
    ],
)
def test_auto_number(case: tuple[str, str, str | None]) -> None:
    assertCase("auto-number", case, [])  # no prefix-variants to test


def test_fail_auto_number() -> None:
    with pytest.raises(ValueError):
        xsd_fmt("3.14.15", "auto-number")
        raise Exception(
            "auto-number should not accept strings "
            "that have no meaningfull number format"
        )


@pytest.mark.parametrize(
    "case",
    [
        (
            (
                "https://example.org/basic",
                "'https://example.org/basic'^^xsd:anyURI",
                "'",
            )
        ),
        (
            (
                "https://example.org/[square-brackets]",
                "'https://example.org/%5Bsquare-brackets%5D'^^xsd:anyURI",
                "'",
            )
        ),
        (
            (
                "https://example.org/[square-brackets]",
                "'https://example.org/%5Bsquare-brackets%5D'^^xsd:anyURI",
            )
        ),
        ((1, "'1'^^xsd:integer", "'")),
        (("1", "'1'^^xsd:integer", "'")),
        ((True, "'true'^^xsd:boolean", "'")),
        (("true", "'true'^^xsd:boolean", "'")),
        (("false", "'false'^^xsd:boolean", "'")),
        ((1.0, "'1.0'^^xsd:double", "'")),
        (("1.0", "'1.0'^^xsd:double", "'")),
        ((date(2024, 1, 13), "'2024-01-13'^^xsd:date", "'")),
        (("2024-01-13T11:48:29", "'2024-01-13T11:48:29'^^xsd:dateTime", "'")),
        (("2024-01-13", "'2024-01-13'^^xsd:date", "'")),
        (("2024-01", "'2024-01'^^xsd:gYearMonth", "'")),
        # (("2024", "'2024'^^xsd:gYear", "'")), -- int inference is stronger
        (("brol", "'brol'^^xsd:string", "'")),
    ],
)
def test_auto_any(case: tuple[str, str, str | None]) -> None:
    assertCase("auto", case, [])  # no prefix-variants to test


def test_urit_fn() -> None:
    assert uritexpand_fmt is not None, "uritexpand_fmt function not found"
    assert isinstance(uritexpand_fmt, Callable), (
        "uritexpand_fmt function not callable",
    )


def test_urit() -> None:
    fmt = uritexpand_fmt(
        None,  # placeholder for context, ignored in test
        "https://vliz.be/code/pysubyt/test/item{#id}",
        {"id": "somepath"},
    )
    exp = "https://vliz.be/code/pysubyt/test/item#somepath"
    assert fmt == exp, "unexpected uri result for uritexpand test"


def test_regexreplace_fn() -> None:
    assert regexreplace_fmt is not None, "regexreplace_fmt function not found"
    assert isinstance(regexreplace_fmt, Callable), (
        "regexreplace_fmt function not callable",
    )


def test_regexreplace() -> None:
    fmt = regexreplace_fmt("^[^:]*:", "", "all-after-semicolon:is-kept")
    exp = "is-kept"
    assert fmt == exp, "unexpected regexreplace result"


def test_mapbuild_fn() -> None:
    assert map_build_fmt is not None, "map_build_fmt function not found"
    assert isinstance(map_build_fmt, Callable), (
        "map_build_fmt function not callable",
    )


def test_mapbuild() -> None:
    map_expects = {"a": 5, "b": 6, "c": 7}
    map_test: list[dict[str, str | int]] = [
        {"from": "a", "to": map_expects["a"]},
        {"from": "b", "to": map_expects["b"]},
    ]

    # check building the map
    map_fmt = map_build_fmt(map_test, "from", "to")
    assert map_fmt is not None, "map not built"
    assert isinstance(map_fmt, ValueMapper), "map not a ValueMapper instance"
    assert map_fmt._map["a"] == map_expects["a"], "map not built correctly"
    assert map_fmt._map["b"] == map_expects["b"], "map not built correctly"

    # check adding to the map
    map_fmt.add("c", map_expects["c"])
    assert "c" in map_fmt._map, "key not added to map"
    assert len(map_fmt._map) == len(map_expects), "key not added correctly"
    assert map_fmt._map["c"] == map_expects["c"], "value not added correctly"

    # check applying the map
    for origin in map_expects:
        record = {"from-field": origin}
        map_fmt.apply(record, "from-field", "to-field")
        assert "to-field" in record, "map not applied"
        assert record["to-field"] == map_expects[origin], (
            "map not applied correctly",
        )

