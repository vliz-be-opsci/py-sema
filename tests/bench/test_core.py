#! /usr/bin/env python
from pathlib import Path
from unittest import TestCase

from sema.bench.core import Sembench


class TestSembench(TestCase):
    """Assert whether a Sembench object is properly initialized, depending on
    which keyword arguments are provided.
    """

    def test_init_input_data(self):
        kwargs = dict(
            locations=dict(
                home="./tests/bench/resources/input_data",
            ),
        )
        sb = Sembench(**kwargs)
        self.assertEqual(sb.output_data_location, sb.input_data_location)
        self.assertEqual(sb.sembench_data_location, sb.input_data_location)
        self.assertEqual(
            Path(sb.sembench_config_path),
            Path(sb.sembench_data_location) / sb.sembench_config_file_name,
        )
        self.assertEqual(sb.sembench_config_file_name, "sembench.yaml")
        self.assertEqual(sb.task_configs["my_only_task"]["func"], "A")

    def test_init_input_data_output_data(self):
        kwargs = dict(
            locations=dict(
                home="./tests/bench/resources/input_data",
                output="./tests/bench/resources/output_data",
            )
        )
        sb = Sembench(**kwargs)
        self.assertEqual(
            Path(sb.output_data_location),
            Path("./tests/bench/resources/output_data"),
        )
        self.assertEqual(sb.sembench_data_location, sb.input_data_location)
        self.assertEqual(
            Path(sb.sembench_config_path),
            Path(sb.sembench_data_location) / sb.sembench_config_file_name,
        )
        self.assertEqual(sb.sembench_config_file_name, "sembench.yaml")
        self.assertEqual(sb.task_configs["my_only_task"]["func"], "A")

    def test_init_input_data_sembench_data(self):
        kwargs = dict(
            locations=dict(
                home="./tests/bench/resources/sembench_data",
                input="./tests/bench/resources/input_data",
            ),
        )
        sb = Sembench(**kwargs)
        self.assertEqual(sb.output_data_location, sb.input_data_location)
        self.assertEqual(
            Path(sb.sembench_data_location),
            Path("./tests/bench/resources/sembench_data"),
        )
        self.assertEqual(
            Path(sb.sembench_config_path),
            Path(sb.sembench_data_location) / sb.sembench_config_file_name,
        )
        self.assertEqual(sb.sembench_config_file_name, "sembench.yaml")
        self.assertEqual(sb.task_configs["my_only_task"]["func"], "B")

    def test_init_input_data_sembench_config_path(self):
        kwargs = dict(
            locations=dict(
                home="./tests/bench/resources/input_data",
            ),
            sembench_config_path="./tests/bench/resources/weirdly_named_sembench.yaml",  # noqa
        )
        sb = Sembench(**kwargs)
        self.assertEqual(sb.output_data_location, sb.input_data_location)
        self.assertEqual(sb.sembench_data_location, sb.input_data_location)
        self.assertEqual(
            Path(sb.sembench_config_path),
            Path("./tests/bench/resources/weirdly_named_sembench.yaml"),
        )
        self.assertEqual(
            sb.sembench_config_file_name, "weirdly_named_sembench.yaml"
        )
        self.assertEqual(sb.task_configs["my_only_task"]["func"], "C")

    def test_init_input_data_sembench_config_file_name(self):
        kwargs = dict(
            locations=dict(
                home="./tests/bench/resources/input_data",
            ),
            sembench_config_file_name="another_weirdly_named_sembench.yaml",
        )
        sb = Sembench(**kwargs)
        self.assertEqual(sb.output_data_location, sb.input_data_location)
        self.assertEqual(sb.sembench_data_location, sb.input_data_location)
        self.assertEqual(
            Path(sb.sembench_config_path),
            Path(sb.sembench_data_location) / sb.sembench_config_file_name,
        )
        self.assertEqual(
            sb.sembench_config_file_name, "another_weirdly_named_sembench.yaml"
        )
        self.assertEqual(sb.task_configs["my_only_task"]["func"], "D")

    def test_init_sembench_config_path_sembench_config_file_name(self):
        kwargs = dict(
            locations=dict(
                home="./tests/bench/resources/input_data",
            ),
            sembench_config_path="./tests/bench/resources/weirdly_named_sembench.yaml",  # noqa
            sembench_config_file_name="another_weirdly_named_sembench.yaml",
        )
        self.assertRaises(AssertionError, lambda: Sembench(**kwargs))

    def test_init_resolve_config_path(self):
        kwargs = dict(
            locations=dict(
                one="1",
                two="2",
            ),
            sembench_config_path="./tests/bench/resources/resolving-sembench.yml",  # noqa
        )
        sb = Sembench(**kwargs)
        self.assertEqual(
            sb.sembench_config_file_name, "resolving-sembench.yml"
        )
        self.assertEqual(
            Path(sb.sembench_config_path),
            Path("./tests/bench/resources/resolving-sembench.yml"),
        )
        self.assertEqual(
            Path(sb.sembench_data_location), Path("./tests/bench/resources")
        )
        self.assertTrue("my_resolved_task" in sb.task_configs)
        rt = sb.task_configs["my_resolved_task"]
        self.assertEqual(rt["func"], "R")
        expected_args = dict(
            plain="no resolve going on",
            skip="keep {one} unresolved",
            noop="nothing to resolve",
            one="unquoted 1/1",
            two="quoted 2/2",
            twelve="12/12",
        )
        self.assertDictEqual(rt["args"], expected_args)

    # TODO doesn't work anymore
    """
    def test_locations_environ(self):
        # note : the relevant environment variables are set in the pytest.ini
        # and are loaded into the env through plugin pytest-env
        locations = locations_from_environ()
        print(locations)
        self.assertTrue({"one", "two"} == locations.keys())
        self.assertTrue(locations["one"] == "1")
        self.assertTrue(locations["two"] == "2")
    """


if __name__ == "__main__":
    from util4tests import run_single_test

    run_single_test(__file__)
