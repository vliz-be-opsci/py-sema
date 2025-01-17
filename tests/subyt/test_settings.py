import logging
import random
from itertools import product

from sema.subyt.api import GeneratorSettings

log = logging.getLogger(__name__)


def test_statics():
    descr = GeneratorSettings.describe()
    assert descr, "generic description should not be empty"
    assert len(GeneratorSettings._scheme.keys()) == descr.count("\n") + 1, (
        "Each key in the description should be described",
    )


def test_parse():
    mode: str = "no-ig,fl,it"
    generator_settings: GeneratorSettings = GeneratorSettings(mode)
    assert not generator_settings.ignorecase, "IgnoreCase should be off"
    assert generator_settings.flatten, "Flatten should be on"
    assert generator_settings.iteration, "Iteration should be on"


def test_cases_roundtrip():
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
            assert case_vals[key] == case_generator_settings.__getattr__(key), (
                f"wrong setting for key '{key}' via modstr "
                f"'{case_mode}' should be {case_vals[key]}",
            )

        case_roundtrip = case_generator_settings.as_modifier_str()
        assert set(case_keys) == set(case_roundtrip.split(",")), (
            f"Roundtrip settings does not match "
            f"'{case_mode}' <> '{case_roundtrip}'.",
        )
