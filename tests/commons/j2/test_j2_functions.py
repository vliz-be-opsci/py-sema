import unittest
from datetime import date, datetime
from typing import Callable

from sema.commons.j2.j2_functions import Filters, Functions, ValueMapper

uritexpand_fmt = Functions.all()["uritexpand"]
regexreplace_fmt = Functions.all()["regexreplace"]
map_build_fmt = Functions.all()["map"]
xsd_fmt = Filters.all()["xsd"]
uri_fmt = Filters.all()["uri"]


class TestXSDFormatting(unittest.TestCase):
    def test_fn(self):
        self.assertIsNotNone(xsd_fmt, "function not found")
        self.assertTrue(isinstance(xsd_fmt, Callable), "function not callable")

    def test_bool(self):
        short_name = "boolean"
        for pfx in ("", "xsd:"):
            type_name = pfx + short_name
            self.assertEqual(
                xsd_fmt(True, type_name),
                "'true'^^xsd:boolean",
                "bad %s format" % type_name,
            )
            self.assertEqual(
                xsd_fmt("anything", type_name, '"'),
                '"true"^^xsd:boolean',
                "bad %s format" % type_name,
            )
            self.assertEqual(
                xsd_fmt(False, type_name, '"'),
                '"false"^^xsd:boolean',
                "bad %s format" % type_name,
            )
            self.assertEqual(
                xsd_fmt(0, type_name),
                "'false'^^xsd:boolean",
                "bad %s format" % type_name,
            )
            self.assertEqual(
                xsd_fmt(None, type_name),
                "'false'^^xsd:boolean",
                "bad %s format" % type_name,
            )

    def test_int(self):
        short_name = "integer"
        for pfx in ("", "xsd:"):
            type_name = pfx + short_name
            self.assertEqual(
                xsd_fmt(1, type_name),
                "'1'^^xsd:integer",
                "bad %s format" % type_name,
            )
            self.assertEqual(
                xsd_fmt(-10, type_name, '"'),
                '"-10"^^xsd:integer',
                "bad %s format" % type_name,
            )
            self.assertEqual(
                xsd_fmt(0, type_name, '"'),
                '"0"^^xsd:integer',
                "bad %s format" % type_name,
            )

            with self.assertRaises(
                AssertionError,
                msg="leading zero's should be dealth with before formatting",
            ):
                xsd_fmt(
                    "001", type_name
                )  # you should not simply assume this to become 1
            # in stead -- force int casting:
            self.assertEqual(
                xsd_fmt(int("001"), type_name),
                "'1'^^xsd:integer",
                "bad %s format" % type_name,
            )

    def test_double(self):
        short_name = "double"
        for pfx in ("", "xsd:"):
            type_name = pfx + short_name
            self.assertEqual(
                xsd_fmt(1.0, type_name),
                "'1.0'^^xsd:double",
                "bad %s format" % type_name,
            )
            self.assertEqual(
                xsd_fmt("1", type_name),
                "'1.0'^^xsd:double",
                "bad %s format" % type_name,
            )  # automatic to float
            self.assertEqual(
                xsd_fmt(1, type_name),
                "'1.0'^^xsd:double",
                "bad %s format" % type_name,
            )  # automatic to float
            self.assertEqual(
                xsd_fmt(1.00, type_name),
                "'1.0'^^xsd:double",
                "bad %s format" % type_name,
            )  # reformatting sideeffect
            # so actual forced float casting is not needed any more (but works)
            self.assertEqual(
                xsd_fmt(float(1), type_name),
                "'1.0'^^xsd:double",
                "bad %s format" % type_name,
            )

    def test_date(self):
        long_name = "xsd:date"
        short_name = long_name[4:]
        for pfx in ("", "xsd:"):
            type_name = pfx + short_name
            val = "1970-05-06"
            values = [val, date.fromisoformat(val)]
            for v in values:
                fmt = "'" + str(v) + "'^^" + long_name

                self.assertEqual(
                    xsd_fmt(v, type_name), fmt, "bad %s format" % type_name
                )

    def test_datetime(self):
        long_name = "xsd:dateTime"
        short_name = long_name[4:]
        for pfx in ("", "xsd:"):
            type_name = pfx + short_name
            val = "2021-09-30T16:25:50+02:00"
            values = [val, datetime.fromisoformat(val)]

            for v in values:
                fmt = "'" + val + "'^^" + long_name
                self.assertEqual(
                    xsd_fmt(v, type_name), fmt, "bad %s format" % type_name
                )

    def test_uri(self):
        long_name = "xsd:anyURI"
        short_name = long_name[4:]
        for pfx in ("", "xsd:"):
            type_name = pfx + short_name
            val = "https://example.org/for/testing"
            fmt = "'" + val + "'^^" + long_name
            self.assertEqual(
                xsd_fmt(val, type_name), fmt, "bad %s format" % type_name
            )

    def test_uri_cleaning(self):
        long_name = "xsd:anyURI"
        short_name = long_name[4:]
        for pfx in ("", "xsd:"):
            type_name = pfx + short_name
            val = "https://example.org/for/[testing]"
            clean_val = "https://example.org/for/%5Btesting%5D"
            fmt = "'" + clean_val + "'^^" + long_name
            self.assertEqual(
                xsd_fmt(val, type_name), fmt, "bad %s format" % type_name
            )

    def test_string(self):
        long_name = "xsd:string"
        short_name = long_name[4:]
        for pfx in ("", "xsd:"):
            type_name = pfx + short_name
            self.assertEqual(
                xsd_fmt("Hello!", type_name),
                "'Hello!'^^xsd:string",
                f"bad {type_name} format",
            )
            self.assertEqual(
                xsd_fmt("'", type_name, quote='"'),
                '"\'"^^xsd:string',
                f"bad {type_name} format",
            )
            self.assertEqual(
                xsd_fmt('"', type_name, quote="'"),
                "'\"'^^xsd:string",
                f"bad {type_name} format",
            )
            self.assertEqual(
                xsd_fmt("'", type_name, quote="'"),
                "'\\''^^xsd:string",
                f"bad {type_name} format",
            )
            self.assertEqual(
                xsd_fmt('"', type_name, quote='"'),
                '"\\""^^xsd:string',
                f"bad {type_name} format",
            )
            self.assertEqual(
                xsd_fmt(">'<", type_name, quote="'"),
                "'>\\'<'^^xsd:string",
                f"bad {type_name} format",
            )
            self.assertEqual(
                xsd_fmt(">\n<", type_name, quote="'"),
                "'''>\n<'''^^xsd:string",
                f"bad {type_name} format",
            )
            self.assertEqual(
                xsd_fmt(">\n<", type_name, quote='"'),
                '""">\n<"""^^xsd:string',
                f"bad {type_name} format",
            )

        def test_lang_string(self):
            self.assertEqual(
                xsd_fmt("Hello!", "@en"),
                "'Hello!'@en",
                "bad language-string format",
            )
            self.assertEqual(
                xsd_fmt("ceci n'est pas une texte", "@fr"),
                "'ceci n\\'est pas une texte'@fr",
                "bad language-string formatting with quote-escapes",
            )
            self.assertEqual(
                xsd_fmt("As \\ said before", "@en"),
                "'As \\\\ said before'@en",
                "bad language-string formatting with backslash-escapes",
            )


class TestURIFormatting(unittest.TestCase):
    def test_fn(self):
        self.assertIsNotNone(uri_fmt, "function not found")
        self.assertTrue(isinstance(uri_fmt, Callable), "function not callable")

    def test_nobase(self):
        uri = "<https://example.org/%5Bsquare-brackets%5D>"
        fmt = uri_fmt("https://example.org/[square-brackets]")
        self.assertEqual(fmt, uri)


class TestURITemplateExpansion(unittest.TestCase):
    def test_fn(self):
        self.assertIsNotNone(uritexpand_fmt, "function not found")
        self.assertTrue(
            isinstance(uritexpand_fmt, Callable), "function not callable"
        )

    def test_all(self):
        uri = "https://vliz.be/code/pysubyt/test/item#somepath"
        fmt = uritexpand_fmt(
            "https://vliz.be/code/pysubyt/test/item{#id}", {"id": "somepath"}
        )
        self.assertEqual(fmt, uri)


class TestRegexFormatting(unittest.TestCase):
    def test_fn(self):
        self.assertIsNotNone(regexreplace_fmt, "function not found")
        self.assertTrue(
            isinstance(regexreplace_fmt, Callable), "function not callable"
        )

    def test_all(self):
        text = "is-kept"
        fmt = regexreplace_fmt("^[^:]*:", "", "all-after-semicolon:is-kept")
        self.assertEqual(fmt, text)


class TestMapFormatting(unittest.TestCase):
    key_name = "Alpha-2 code"
    val_name = "Alpha-3 code"
    key_val = str(3)
    val_val = str(4)
    map_test = [
        {key_name: key_val, val_name: val_val},
    ]
    fmt = map_build_fmt(map_test, key_name, val_name)

    # TODO: Redo this tests.
    def test_fn(self):
        self.assertIsNotNone(map_build_fmt, "function not found")
        self.assertTrue(
            isinstance(map_build_fmt, Callable), "function not callable"
        )

    def test_all(self):
        self.assertIsInstance(self.fmt, ValueMapper)
        self.assertEqual(self.fmt._map[self.key_val], self.val_val)

    def test_add(self):
        key_name = "Alpha-5 code"
        key_val = 9
        self.fmt.add(key_name, key_val)
        self.assertDictEqual(
            self.fmt._map, self.fmt._map | {key_name: key_val}
        )

    def test_apply(self):
        key_name = "Alpha-8 code"
        self.fmt.apply(self.map_test[0], self.key_name, key_name)
        assert key_name in self.map_test[0]
