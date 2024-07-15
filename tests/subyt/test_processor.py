import logging
import unittest
from collections.abc import Iterable
from typing import Callable

from conftest import run_single_test

from sema.subyt.api import Generator, GeneratorSettings, Sink, Source

log = logging.getLogger(__name__)


class DebugIterator(Iterable):
    """Just wraps an iterator to follow and debug progress"""

    def __init__(self, a_range):
        self._wrapped_iter = iter(a_range)
        self._count = 0

    def __iter__(self):
        return self

    def __next__(self):
        val = next(self._wrapped_iter)
        log.debug(f"next() [{self._count}] yields {val}")
        assert self._count == val, "unexpected order of basic iteration"
        self._count += 1
        return val


class SimpleRangeSource(Source):
    """Just generates int items from zero to size-1"""

    def __init__(self, size):
        super().__init__()
        self._size = size

    def __enter__(self) -> Iterable:
        return DebugIterator(range(self._size))

    def __exit__(self, *exc):
        pass  # just nothing to do


class CountingSink(Sink):
    """Just verifies that added parts are incrementing up to
    the expected size"""

    def __init__(self, size):
        super().__init__()
        self._size = size
        self._count = 0

    def add(self, part: str, item, source_mtime: float = None):
        assert int(part) == item, "pass-through behaviour failed"
        assert item == self._count, "item not arriving at expected count"
        self._count += 1

    def open(self):
        pass

    def close(self):
        pass

    def evaluate(self):
        assert (
            self._count == self._size
        ), "sink did not receive expected number of added parts"


class SimplePassGenerator(Generator):
    """Just lets items pass through unchanged"""

    def __init__(self, testname, size):
        assert (
            size > 2
        ), "test only makes sense to check beyond first/last cases"
        self._name = testname
        self._size = size
        self._count = 0

    def make_render_fn(self, template_name: str) -> Callable:
        def render(**params):
            item = params["_"]
            sets = params["sets"]
            ctrl = params["ctrl"]
            log.debug("render call..")
            log.debug(f".. self._count = {self._count}")
            log.debug(f".. item = {item}")
            log.debug(f".. sets = {sets}")
            log.debug(f".. ctrl = {ctrl}")
            # assertions on the progress / count
            assert item == self._count, "unexpected item for current count"
            assert item == ctrl["index"], "unexpected item for current index"
            # more assertions on the ctrl object
            if item == 0:
                assert ctrl["isFirst"]
                assert not (ctrl["isLast"])
            elif item == self._size - 1:
                assert not (ctrl["isFirst"])
                assert ctrl["isLast"]
            else:
                assert not (ctrl["isFirst"])
                assert not (ctrl["isLast"])
            self._count += 1
            return str(item)

        assert template_name == self._name
        return render


class TestAPIProcessor(unittest.TestCase):
    """Core purpose of this test is checking up on the processor behaviour
    More precisely - checking if all items are correctly processed and
        the ctrl variables are set correctly
    """

    def test_processor(self):
        TESTSIZE = 5
        TESTNAME = "something to be actually ignored but just tested"
        fg = SimplePassGenerator(TESTNAME, TESTSIZE)
        inputs = dict(_=SimpleRangeSource(TESTSIZE))
        generator_settings = GeneratorSettings()
        sink = CountingSink(TESTSIZE)
        fg.process(TESTNAME, inputs, generator_settings, sink)
        sink.evaluate()


if __name__ == "__main__":
    run_single_test(__file__)
