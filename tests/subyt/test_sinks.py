import logging
import random
import string
import tempfile

import pytest

from pathlib import Path

from sema.subyt.sinks import (
    PatternedFileSink,
    SingleFileSink,
    SinkFactory,
    StdOutSink,
)

log = logging.getLogger(__name__)


def rand_alfanum_str(k: int):
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=k))


@pytest.mark.parametrize(
    "identifier, expected_type",
    [
        ("-", StdOutSink),
        ("test", SingleFileSink),
        ("{key}", PatternedFileSink),
        ("{key}-{id}", PatternedFileSink),
    ],
)
def test_factory(identifier, expected_type):
    sink = SinkFactory.make_sink(identifier)
    assert isinstance(sink, expected_type), (
        f"expected sink type {expected_type} for identifier {identifier}"
        f"got {type(sink)}",
    )


@pytest.mark.parametrize(
    "items",
    [
        [
            {
                "id": i,
                "key": f"{i:04d}",
                "data": f"data-{i:d}-{rand_alfanum_str(20)}",
            }
            for i in range(4)
        ]
    ],
)
def test_sink_outputs(items):
    base = Path(__file__).absolute().parent
    temp = base / "tmp"
    temp.mkdir(exist_ok=True, parents=True)

    count = len(items)

    with tempfile.TemporaryDirectory(dir=temp) as temp_folder:
        temp_path: Path = Path(temp_folder)
        all_file = temp_path / "all.out"
        all_in_one_sink = SinkFactory.make_sink(str(all_file))

        separate_files_sink = SinkFactory.make_sink(str(temp_path / "item-{key}.out"))

        for sink in [all_in_one_sink, separate_files_sink]:
            sink.open()
            for item in items:
                sink.add(item["data"], item)
            sink.close()

        # assert there are now count +1 files
        # +1 for the all-out and one for each item
        foundfiles = len(list(temp_path.iterdir()))
        assert count + 1 == foundfiles, (
            "expecting exactly one more files than the number of items "
            f"in the folder {temp_folder} "
            f"found {foundfiles} files - but expected {count + 1}",
        )

        # assert content of the item files
        all_data = ""
        for item in items:
            item_file: Path = temp_path / f"item-{item['key']}.out"
            with open(item_file, "r") as f:
                content = f.read()
                assert item["data"] == content, (
                    f"content for item {item['id']} should match",
                )
                all_data += item["data"]
        # assert the content of the overview file
        with open(all_file, "r") as f:
            all_content = f.read()
            assert all_data == all_content, (
                "aggregated content for all items should match",
            )

        # test the leniency of pattern production
        # by removing one {key} in the available items
        items[1]["key"] = ""
        log.debug(f"updated items is now: {items}")

        separate_files_sink = SinkFactory.make_sink(str(temp_path / "{key}"))
        separate_files_sink.open()
        for item in items:
            separate_files_sink.add(item["data"], item)
        separate_files_sink.close()

        # this should have worked without errors
        # and created one less extra file then the number of items
        newfoundfiles = len(list(temp_path.iterdir())) - foundfiles
        assert count - 1 == newfoundfiles, (
            "unexpectd amount of newly generated files when one key was empty "
            f"in the folder {temp_folder} "
            f"found {newfoundfiles} new files - but expected {count - 1}",
        )
