import re
from collections.abc import Iterable
from datetime import date, datetime

from dateutil import parser
from uritemplate import URITemplate

from sema.commons.clean import clean_uri_str


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
        }


class Filters:
    @staticmethod
    def all():
        return {
            "xsd": xsd_format,
            "uri": uri_format,
        }


def xsd_value(content, quote, type_name, suffix=None):
    if suffix is None:
        suffix = "^^" + type_name
    return quote + str(content) + quote + suffix


def xsd_format_boolean(content, quote, suffix):
    # make rigid bool
    if not isinstance(content, bool):
        asbool = str(content).lower() not in ["", "0", "no", "false", "off"]
        content = asbool
    # serialize to string again
    return xsd_value(str(content).lower(), quote, "xsd:boolean")


def xsd_format_integer(content, quote, suffix):
    # make rigid int
    if not isinstance(content, int):
        asint = int(str(content))
        assert str(content) == str(
            asint
        ), "int format does not round-trip [ %s <> %s ]" % (
            str(content),
            str(asint),
        )
        content = asint
    # serialize to string again
    return xsd_value(str(content), quote, "xsd:integer")


def xsd_format_double(content, quote, suffix):
    # make rigid double
    if not isinstance(content, float):
        assert (
            str(float) and float is not None
        ), "double format requires actual input"
        asdbl = float(str(content))
        content = asdbl
    # serialize to string again
    return xsd_value(str(content), quote, "xsd:double")


def xsd_format_date(content, quote, suffix):
    # make rigid date
    if not isinstance(content, date):
        asdt = parser.isoparse(content).date()
    else:
        asdt = content
    return xsd_value(asdt.isoformat(), quote, "xsd:date")


def xsd_format_datetime(content, quote, suffix):
    # make rigid datetime
    if not isinstance(content, datetime):
        asdtm = parser.isoparse(content)
    else:
        asdtm = content
    return xsd_value(asdtm.isoformat(), quote, "xsd:dateTime")


def xsd_format_uri(content, quote, suffix):
    # assume content is valid uri for now
    uri = clean_uri_str(content)
    return xsd_value(uri, quote, "xsd:anyURI")


def xsd_format_string(content, quote, suffix):
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


XSD_FMT_TYPE_FN = {
    "xsd:boolean": xsd_format_boolean,
    "xsd:integer": xsd_format_integer,
    "xsd:double": xsd_format_double,
    "xsd:date": xsd_format_date,
    "xsd:datetime": xsd_format_datetime,
    "xsd:anyuri": xsd_format_uri,
    "xsd:string": xsd_format_string,
}


def xsd_format(content, type_name: str, quote: str = "'"):
    assert quote in "'\"", "ttl format only accepts ' or \" as valid quotes."
    if content is None:
        content = ""

    suffix = None
    if type_name.startswith("@"):
        suffix = type_name
        # assuming string content for further quoting rules
        type_name = "xsd:string"

    if not type_name.startswith("xsd:"):
        type_name = "xsd:" + type_name

    type_format_fn = XSD_FMT_TYPE_FN.get(type_name.lower(), None)
    assert type_format_fn is not None, (
        "type_name '%s' not supported." % type_name
    )

    return type_format_fn(content, quote, suffix)


def uri_format(uri: str):
    uri = clean_uri_str(uri)
    return f"<{uri}>"


def uritexpand(template: str, context):
    return URITemplate(template).expand(context)


def regexreplace(find: str, replace: str, text: str):
    return re.sub(find, replace, text)


class ValueMapper:
    def __init__(self):
        self._map = dict()

    def add(self, key, val):
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
