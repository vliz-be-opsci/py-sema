import logging
import random
import unittest
from itertools import product

from conftest import run_single_test

from sema.commons.log.loader import load_log_config
from sema.subyt.api import GeneratorSettings

load_log_config()
log = logging.getLogger(__name__)


class TestGeneratorSettings(unittest.TestCase):
    def test_statics(self):
        descr = GeneratorSettings.describe()
        self.assertTrue(descr, "generic description should not be empty")
        self.assertEqual(
            len(GeneratorSettings._scheme.keys()),
            descr.count("\n") + 1,
            "Each key in the description should be described",
        )

    def test_parse(self):
        mode: str = "no-ig,fl,it"
        generator_settings: GeneratorSettings = GeneratorSettings(mode)
        self.assertFalse(
            generator_settings.ignorecase, "IgnoreCase should be off"
        )
        self.assertTrue(generator_settings.flatten, "Flatten should be on")
        self.assertTrue(generator_settings.iteration, "Iteration should be on")

    def test_errors(self):
        pass

    def test_cases_roundtrip(self):
        minlen = 2  # minimal length of the part to still be unambiguous
        keys = GeneratorSettings._scheme.keys()
        for case in product([True, False], repeat=len(keys)):
            case_vals = {key: case[i] for (i, key) in enumerate(keys)}
            case_keys = list()
            case_parts = list()
            for key in keys:
                part = key[
                    : (minlen + random.randrange(len(key) - minlen))
                ]  # leading part of key
                val_pfx = "no-" if not case_vals[key] else ""
                case_parts.append(val_pfx + part)
                case_keys.append(val_pfx + key)
            case_mode = ",".join(case_parts)
            case_generator_settings = GeneratorSettings(case_mode)
            for key in keys:
                self.assertEqual(
                    case_vals[key],
                    case_generator_settings.__getattr__(key),
                    "wrong setting for key '%s' via modstr '%s' should be %s"
                    % (key, case_mode, case_vals[key]),
                )

            case_roundtrip = case_generator_settings.as_modifier_str()
            self.assertEqual(
                set(case_keys),
                set(case_roundtrip.split(",")),
                "Roundtrip settings does not match '%s' <> '%s'."
                % (case_mode, case_roundtrip),
            )


if __name__ == "__main__":
    run_single_test(__file__)
