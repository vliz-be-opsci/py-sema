import re
from collections.abc import Iterable
from datetime import date, datetime
from logging import getLogger
from typing import Any

import jinja2
from dateutil import parser
from jinja2 import pass_context
from jinja2.runtime import Context
from uritemplate import URITemplate

from sema.commons.clean import clean_uri_str
from sema.commons.clean.clean import check_valid_uri

log = getLogger(__name__)


class Functions:
    _cache = dict()

    @staticmethod
    def all():
        return {
            "uritexpand": uritexpand,
            "regexreplace": regexreplace,
            "map": map_build,
            # TODO: Check for duplication in filters and the meaning.
            "xsd": xsd_format,
            "unite": unite,
        }


class Filters:
    @staticmethod
    def all() -> dict:
        return {
            "xsd": xsd_format,
            "uri": uri_format,
        }


def xsd_value(
    content: any,
    quote: str,
    type_name: str,
    suffix: str | None = None,
) -> str:
    if suffix is None:
        suffix = "^^" + type_name
    return quote + str(content) + quote + suffix


def xsd_format_boolean(content: Any, quote: str, *_: Any) -> str:
    if isinstance(content, (list, dict, type(None), jinja2.runtime.Undefined)):
        raise TypeError(
            f"unsuported input type {type(content)} for boolean formatting - "
            "conversion required before format call"
        )

    # make rigid bool
    if not isinstance(content, bool):
        asbool = str(content).lower() not in ["", "0", "no", "false", "off"]
        content = asbool
    # serialize to string again
    return xsd_value(str(content).lower(), quote, "xsd:boolean")


def xsd_format_integer(content: Any, quote: str, *_: Any) -> str:
    # make rigid int
    if not isinstance(content, int):
        asint = int(str(content))
        if str(content) != str(asint):
            raise ValueError(
                "int format does not round-trip "
                f"[ {content!s} <> {asint!s} ]"
            )
        content = asint
    # serialize to string again
    return xsd_value(str(content), quote, "xsd:integer")


def _xsd_format_realnum(
    xsd_type_name: str, content: Any, quote: str, *_: Any
) -> str:
    # make rigid real number
    if not isinstance(content, float):
        asreal = float(str(content))
        content = asreal
    # serialize to string again
    return xsd_value(str(content), quote, xsd_type_name)


def xsd_format_float(content: Any, quote: str, *_: Any) -> str:
    return _xsd_format_realnum("xsd:float", content, quote, _)


def xsd_format_double(content: Any, quote: str, *_: Any) -> str:
    return _xsd_format_realnum("xsd:double", content, quote, _)


def xsd_format_date(content: Any, quote: str, *_: Any) -> str:
    # make rigid date
    if isinstance(content, datetime):
        raise TypeError(
            "use datetime format for datetime values, or past .date() result"
        )

    if not isinstance(content, date):
        asdt = parser.isoparse(content).date()
    else:
        asdt = content
    return xsd_value(asdt.isoformat(), quote, "xsd:date")


def xsd_format_gyear(content: Any, quote: str, *_: Any) -> str:
    # make rigid gYear
    if isinstance(content, date):
        year = content.year  # extract year from date
    else:  # other input types handled
        content = str(content).strip()  # via trimmed string
        year = int(content)  # converted to int
    # we should be sure of int now
    # see https://www.datypic.com/sc/xsd11/t-xsd_gYear.html
    # for examples of correct value formatting
    content = f"{'-' if year < 0 else ''}{abs(year):04d}"
    return xsd_value(content, quote, "xsd:gYear")


def xsd_format_gyearmonth(content: Any, quote: str, *_: Any) -> str:
    # make rigid gMonthYear
    if isinstance(content, (date, datetime)):
        year, month = content.year, content.month  # extract parts from date
    else:  # other types of input handled
        content = str(content).strip()  # via trimmed string
        sign = 1
        if content[0] == "-":  # extract sign if present
            sign = -1
            content = content[1:]
        # split into parts
        [year, month, *ignored_rest] = content.split("-")
        # and ensure they are int with carried sign
        year, month = int(year) * sign, int(month)
    # https://www.datypic.com/sc/xsd11/t-xsd_gYearMonth.html
    # for examples of correct value formatting
    content = f"{'-' if year < 0 else ''}{abs(year):04d}-{month:02d}"
    return xsd_value(content, quote, "xsd:gYearMonth")


def xsd_format_datetime(content: Any, quote: str, *_: Any) -> str:
    # make rigid datetime
    if not isinstance(content, datetime):
        asdtm = parser.isoparse(content)
    else:
        asdtm = content
    return xsd_value(asdtm.isoformat(), quote, "xsd:dateTime")


def xsd_format_uri(content: str, quote: str, *_: Any) -> str:
    # assume content is valid uri for now
    uri = clean_uri_str(content)
    return xsd_value(uri, quote, "xsd:anyURI")


def xsd_format_string(content: str, quote: str, suffix: str) -> str:
    if isinstance(content, (list, dict, type(None), jinja2.runtime.Undefined)):
        raise TypeError(
            f"unsuported input type {type(content)} for boolean formatting - "
            "conversion required before format call"
        )
    # apply escape sequences: \ to \\ and quote to \quote
    escqt = f"\\{quote}"
    content = str(content).replace("\\", "\\\\").replace(quote, escqt)

    if "\n" in content:
        quote = quote * 3  # make long quote variant to allow for newlines
        assert quote not in content, (
            "ttl format error: still having "
            f"quote {quote} in text content {content}"
            f"applied quote format {quote} in text content"
        )
    return xsd_value(content, quote, "xsd:string", suffix)


def _auto_str_to_formatted_date(content: str, quote: str) -> str | None:
    for regex, formatter in [
        (r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}", xsd_format_datetime),
        (r"\d{4}-\d{2}-\d{2}", xsd_format_date),
        (r"\d{4}-\d{2}", xsd_format_gyearmonth),
        (r"\d{4}", xsd_format_gyear),
    ]:
        if re.match(regex, content):
            try:
                parser.isoparse(content)
                return formatter(content, quote)
            except ValueError:
                pass
    return None


def _auto_str_to_formatted_number(content: str, quote: str) -> str | None:
    testcontent = content.strip().lower()
    if testcontent[0] in ["-", "+"]:
        testcontent = testcontent[1:]
    if testcontent.isdigit():
        return xsd_format_integer(content, quote)
    if testcontent.replace(".", "", 1).isdigit():
        return xsd_format_double(content, quote)
    return None


def xsd_auto_format_date(content: Any, quote: str, *_: Any) -> str:
    # infer type from input + apply formatting according to fallback-scenario
    # 1. type datetime
    if isinstance(content, datetime):
        return xsd_format_datetime(content, quote)
    # 2. type date
    if isinstance(content, date):
        return xsd_format_date(content, quote)
    # 3. string parseable to datetime
    # 4. string parseable to date
    # 5. string matching [-]?YYYY-MM for gyearmonth
    # 6. string matching [-]?YYYY for gyear
    formatted_date = _auto_str_to_formatted_date(str(content), quote)
    if formatted_date is not None:
        return formatted_date
    # 7. int for gyear
    if isinstance(content, int):
        return xsd_format_gyear(content, quote)
    # 8. anything else should raise an error
    raise ValueError("auto-date format failed to infer date type")


def xsd_auto_format_number(content: Any, quote: str, *_: Any) -> str:
    # infer type from input + apply formatting according to fallback-scenario
    # 1. type int
    if isinstance(content, int):
        return xsd_format_integer(content, quote)
    # 2. type float
    if isinstance(content, float):
        return xsd_format_double(content, quote)
    # 3. string parseable to int
    # 4. string parseable to float
    formatted_number = _auto_str_to_formatted_number(str(content), quote)
    if formatted_number is not None:
        return formatted_number
    # 5. anything else should raise an error
    raise ValueError("auto-number format failed to infer number type")


def xsd_auto_format_any(content: Any, quote: str, *_: Any) -> str:
    # infer type from input + apply formatting according to fallback-scenario
    # 1. type bool
    if isinstance(content, bool):
        return xsd_format_boolean(content, quote)
    # 2. type int
    if isinstance(content, int):
        return xsd_format_integer(content, quote)
    # 3. type float
    if isinstance(content, float):
        return xsd_format_double(content, quote)
    # 4. type datetime
    if isinstance(content, datetime):
        return xsd_format_datetime(content, quote)
    # 5. type date
    if isinstance(content, date):
        return xsd_format_date(content, quote)
    # -- special case for empty and whitespace-only strings
    if isinstance(content, str) and len(content.strip()) == 0:
        return xsd_format_string(content, quote, None)
    # 6. string parseable to exact bool true or false (ignoring case)
    if str(content).strip().lower() in ["true", "false"]:
        return xsd_format_boolean(content, quote)
    # 7. string parseable to int
    # 8. string parseable to float
    formatted_number = _auto_str_to_formatted_number(str(content), quote)
    if formatted_number is not None:
        return formatted_number
    # 9. string parseable to datetime
    # 10. string parseable to date
    # 11. string matching [-]?YYYY-MM for gyearmonth
    # 12. string matching [-]?YYYY for gyear
    formatted_date = _auto_str_to_formatted_date(str(content), quote)
    if formatted_date is not None:
        return formatted_date
    # 13. string is valid uri
    if check_valid_uri(clean_uri_str(str(content))):
        return xsd_format_uri(content, quote)
    # 14. remaining string content
    return xsd_format_string(content, quote, None)


XSD_FMT_TYPE_FN = {
    "xsd:boolean": xsd_format_boolean,
    "xsd:integer": xsd_format_integer,
    "xsd:float": xsd_format_float,
    "xsd:double": xsd_format_double,
    "xsd:date": xsd_format_date,
    "xsd:datetime": xsd_format_datetime,
    "xsd:anyuri": xsd_format_uri,
    "xsd:string": xsd_format_string,
    "xsd:gyear": xsd_format_gyear,
    "xsd:year": xsd_format_gyear,
    "xsd:yyyy": xsd_format_gyear,
    "xsd:gyearmonth": xsd_format_gyearmonth,
    "xsd:year-month": xsd_format_gyearmonth,
    "xsd:yyyy-mm": xsd_format_gyearmonth,
    "auto-date": xsd_auto_format_date,
    "auto-number": xsd_auto_format_number,
    "auto-any": xsd_auto_format_any,
    "auto": xsd_auto_format_any,
}


def xsd_format(
    content: Any, type_name: str, quote: str = "'", *, fb: str = None
) -> str:
    assert quote in "'\"", "ttl format only accepts ' or \" as valid quotes."

    suffix = None
    type_name = type_name.lower()
    if type_name.startswith("@"):
        suffix = type_name
        # assuming string content for further quoting rules
        type_name = "xsd:string"

    # first try
    type_format_fn = XSD_FMT_TYPE_FN.get(type_name, None)
    if not type_name.startswith("auto"):
        if not type_name.startswith("xsd:"):
            type_name = "xsd:" + type_name

        # second try
        type_format_fn = XSD_FMT_TYPE_FN.get(type_name.lower(), None)
        assert type_format_fn is not None, (
            "type_name '%s' not supported." % type_name
        )

    val = fb
    try:
        val = type_format_fn(content, quote, suffix)
    except Exception as e:
        if fb is None:
            raise e
        log.warning(
            f"formatting of content '{content}' "
            f"with type '{type_name}' failed: {e}, "
            f"using fallback value '{fb}'"
        )
    return val


def uri_format(uri: str) -> str:
    uri = clean_uri_str(uri)
    return f"<{uri}>"


@pass_context
def uritexpand(
    j2ctx: Context,
    template: str,
    context: dict | None = None,
) -> str:
    context = context or {
        k: v for k, v in j2ctx.get_all().items() if not callable(v)
    }
    return URITemplate(template).expand(context)


def regexreplace(find: str, replace: str, text: str) -> str:
    return re.sub(find, replace, text)


class ValueMapper:
    def __init__(self):
        self._map = dict()

    def add(self, key: Any, val: Any) -> None:
        if key in self._map:
            assert val == self._map[key], (
                f"duplicate key {key} with distinct"
                " values not allowed to build map"
            )
        self._map[key] = val

    def apply(
        self, record: dict, origin_name: str, target_name: str, fallback=None
    ) -> None:
        assert (
            target_name not in record
        ), "applying map refuses to overwrite content already in record"
        key = record[origin_name]
        val = self._map.get(key, fallback)
        record[target_name] = val


def map_build(
    it: Iterable,
    key_name: str,
    val_name: str | None = None,
    cached_as: str | None = None,
) -> ValueMapper:
    assert key_name, "cannot build map without valid key-name"
    # note: id val_name is None, we just map to the whole record
    if cached_as is not None and cached_as in Functions._cache:
        return Functions._cache[cached_as]
    # else - make map
    vmap = ValueMapper()
    # - populate it
    for item in it:
        target = item[val_name] if val_name is not None else item
        vmap.add(item[key_name], target)
    # add it to the cache
    if cached_as is not None:
        Functions._cache[cached_as] = vmap
    return vmap


def unite(*args: Any, **kwargs: Any) -> str:
    # unite multiple values into one string, separated by separator
    # but only if all values evaluate to a boolean True, and
    # if at most n resulting string values are non-empty
    # when conditions are not met, return fallback value fb (default "")
    # Usage:
    #   {{ unite( val1, val2, val3, ..., separator=" ", n=3, fb="") }}
    # Motivation:
    # This is to guarantee that only complete sets of values are united in the template output
    # The practical use is for guaranteeing complete triples in turtle output
    # Note that values None, '', 0, [], {} evaluate to boolean False
    # while any non-empty string, even '0', 'False', 'No' evaluate to boolean True
    sep: str = kwargs.get("sep", " ")
    n: int = kwargs.get("n", 3)
    fb: str = kwargs.get("fb", "")

    boolvals: list[bool] = [bool(a) for a in args]
    if not all(boolvals):
        return fb
    # else - make the string from the strings only
    strvals: list[str] = [a for a in args if isinstance(a, str)]
    if len(strvals) == 0 or len(strvals) > n:
        return fb
    return sep.join(strvals)
