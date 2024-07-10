import logging
import os
import random
import string
import tempfile
import unittest

from conftest import run_single_test

from sema.commons.log.loader import load_log_config
from sema.subyt.sinks import PatternedFileSink, SingleFileSink, SinkFactory

load_log_config()
log = logging.getLogger(__name__)


class TestSinks(unittest.TestCase):
    def test_sinks(self):
        base = os.path.abspath(os.path.dirname(__file__))
        temp = os.path.join(base, "tmp")
        if not os.path.isdir(temp):
            os.makedirs(temp)

        count = 3
        items = [
            {
                "id": i,
                "key": "%04d" % i,
                "data": "data-%d-%s"
                % (
                    i,
                    "".join(
                        random.choices(
                            string.ascii_uppercase + string.digits, k=20
                        )
                    ),
                ),
            }
            for i in range(count)
        ]

        with tempfile.TemporaryDirectory(dir=temp) as temp_folder:
            sfs = SinkFactory.make_sink(os.path.join(temp_folder, "all.out"))
            self.assertTrue(
                isinstance(sfs, SingleFileSink), "expected single file sink"
            )

            pfs = SinkFactory.make_sink(
                os.path.join(temp_folder, "item-{key}.out")
            )
            self.assertTrue(
                isinstance(pfs, PatternedFileSink),
                "expected Patterned file sink",
            )

            for sink in [sfs, pfs]:
                sink.open()
                for item in items:
                    sink.add(item["data"], item)
                sink.close()

            # assert there are now count +1 files
            self.assertEqual(
                count + 1,
                len(os.listdir(temp_folder)),
                "expecting exactly one more file then number of items",
            )

            # assert content of the item files
            all_data = ""
            for item in items:
                item_file = os.path.join(
                    temp_folder, "item-%04d.out" % item["id"]
                )
                with open(item_file, "r") as f:
                    content = f.read()
                    self.assertEqual(
                        item["data"],
                        content,
                        "content for item %d should match" % item["id"],
                    )
                    all_data += item["data"]
            # assert the content of the overview file
            all_file = os.path.join(temp_folder, "all.out")
            with open(all_file, "r") as f:
                all_content = f.read()
                self.assertEqual(
                    all_data,
                    all_content,
                    "aggregated content for all items should match",
                )


if __name__ == "__main__":
    run_single_test(__file__)
