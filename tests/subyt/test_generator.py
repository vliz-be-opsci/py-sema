import logging
import os
import unittest

from sema.subyt.api import GeneratorSettings, Sink
from sema.subyt.j2.generator import JinjaBasedGenerator
from sema.subyt.sources import SourceFactory

log = logging.getLogger(__name__)


class AssertingSink(Sink):
    def __init__(self, test):
        super().__init__()
        self._test = test
        self._parts = []

    def load_parts(self, parts):
        self._parts = parts
        self._index = 0

    def _assert_count(self):
        self._test.assertEqual(self._index, len(self._parts))

    def add(self, part: str, item: dict = None, source_mtime: float = None):
        log.debug(f"part received no. {self._index}:\n--\n{part}\n--")
        expected = self._parts[self._index].strip()
        part = part.strip()
        log.debug(f"expected part == \n{expected}\n")
        log.debug(f"actual part == \n{part}\n")
        log.debug(f"expectations ok: {bool(part == expected)}")
        self._test.assertEqual(
            expected,
            part,
            f"unexpected rendering for part at index {self._index}",
        )
        self._index += 1

    def open(self):
        pass

    def close(self):
        pass

    def evaluate(self):
        self._assert_count()


def get_expected_parts(outfile):
    parts = [""]
    n = 0
    with open(outfile, "r") as content:
        for line in content:
            if not line.startswith("#"):
                parts[n] = parts[n] + line
            else:
                if len(parts[n]) > 0:
                    parts.append("")
                    n += 1
    return parts


def get_indicator_from_name(
    name: str, splitter: str = "_", fallback: str = None
):
    known_cases = {"data_glob/*.json": "glob"}
    if name in known_cases.keys():
        return known_cases[name]
    stem = os.path.splitext(name)[0]
    indicator = (
        stem[stem.index(splitter) + 1 :] if splitter in stem else fallback
    )
    return indicator


class TestJinjaGenerator(unittest.TestCase):
    def test_templates(self):
        log.debug("beginning test_templates")
        self.maxDiff = None
        base = os.path.abspath(os.path.dirname(__file__))
        tpl_path = os.path.join(base, "templates")
        out_path = os.path.join(base, "out")
        inp_path = os.path.join(base, "in")

        g = JinjaBasedGenerator(tpl_path)

        inputs = dict()
        inp_content = next(
            os.walk(inp_path), (None, None, [])
        )  # the stuff in the folder
        inp_names = list(inp_content[2])  # the files
        inp_names.extend(inp_content[1])  # the folders too
        inp_names = [
            i for i in inp_names if i != "data_glob"
        ]  # filter "data_glob" folder source out
        inp_names.extend(
            ["data_glob/*.json"]
        )  # insert "glob pattern" glob source
        for inp_name in inp_names:
            key = get_indicator_from_name(inp_name, fallback="_")
            assert key not in inputs, (
                f"duplicate key '{key}' for input '"
                f"{inp_name}' --> object[{inputs[key]}]"
            )
            inputs[key] = SourceFactory.make_source(
                os.path.join(inp_path, inp_name)
            )

        self.assertTrue("_" in inputs, "the base set should be available")
        sink = AssertingSink(self)

        # read all names (files) in the tpl_path
        names = next(os.walk(tpl_path), (None, None, []))[2]  # [] if no file

        for name in names:
            # load the expected parts from the matching output-file in the sink
            sink.load_parts(get_expected_parts(os.path.join(out_path, name)))
            generator_settings = GeneratorSettings(
                get_indicator_from_name(name)
            )

            # process
            log.debug(
                f"processing test-template: {os.path.join(tpl_path, name)}"
            )
            try:
                g.process(
                    name,
                    inputs,
                    generator_settings,
                    sink,
                    vars_dict={"my_domain": "realexample.org"},
                )
            except Exception as e:
                log.error(f"failed to process template: {e}")
                log.exception(e)
                raise e

            # assure all records were passed
            sink.evaluate()
        log.debug("ending test_templates")
