import logging
import time
from pathlib import Path

import pandas as pd

from sema.subyt import Subyt
from sema.subyt.api import GeneratorSettings
from sema.subyt.j2.generator import JinjaBasedGenerator
from sema.subyt.sources import SourceFactory
from tests.subyt.test_generator import (
    AssertingSink,
    get_expected_parts,
    get_indicator_from_name,
)

log = logging.getLogger(__name__)

SUBYT_TEST_FOLDER = Path(__file__).absolute().parent


def test_conditional():
    a_path = SUBYT_TEST_FOLDER / "tmp/data/A.ttl"
    # b_path = SUBYT_TEST_FOLDER / "tmp/data/B.ttl"
    # c_path = SUBYT_TEST_FOLDER / "tmp/data/C.ttl"
    d_path = SUBYT_TEST_FOLDER / "tmp/data/D.ttl"
    for p in [a_path, d_path]:
        if p.exists():
            p.unlink()

    # first run
    Subyt(
        source=str(SUBYT_TEST_FOLDER / "resources/data.csv"),
        sink=str(SUBYT_TEST_FOLDER / "tmp/data/{key}.ttl"),
        template_name="data.ttl.j2",
        template_folder=str(SUBYT_TEST_FOLDER / "resources"),
        conditional=True,
    ).process()
    A_mtime1 = a_path.stat().st_mtime

    # second run and no updates to input file
    time.sleep(1)
    Subyt(
        source=str(SUBYT_TEST_FOLDER / "resources/data.csv"),
        sink=str(SUBYT_TEST_FOLDER / "tmp/data/{key}.ttl"),
        template_name="data.ttl.j2",
        template_folder=str(SUBYT_TEST_FOLDER / "resources"),
        conditional=True,
    ).process()
    A_mtime2 = a_path.stat().st_mtime
    assert A_mtime1 == A_mtime2  # output file should not have been updated

    # third run and update to input file
    time.sleep(1)
    df = pd.read_csv(str(SUBYT_TEST_FOLDER / "resources/data.csv"))
    df.at[0, "value"] = 0
    df.to_csv(str(SUBYT_TEST_FOLDER / "resources/data.csv"), index=False)
    Subyt(
        source=str(SUBYT_TEST_FOLDER / "resources/data.csv"),
        sink=str(SUBYT_TEST_FOLDER / "tmp/data/{key}.ttl"),
        template_name="data.ttl.j2",
        template_folder=str(SUBYT_TEST_FOLDER / "resources"),
        conditional=True,
    ).process()
    A_mtime3 = a_path.stat().st_mtime
    assert A_mtime1 < A_mtime3  # output file should have been updated

    # fourth run and no updates to input fildef test_templates(self):
    log.debug("beginning test_templates")
    base: Path = Path(__file__).parent.relative_to(Path(".").absolute())
    tpl_path: Path = base / "templates"
    out_path: Path = base / "out"
    inp_path: Path = base / "in"

    g = JinjaBasedGenerator(tpl_path)

    inputs = dict()
    inp_names = [p.name for p in inp_path.iterdir()]  # the stuff in the folder
    inp_names = [
        i for i in inp_names if i != "data_glob"
    ]  # filter "data_glob" folder source out
    inp_names.extend(["data_glob/*.json"])  # insert "glob pattern" glob source
    for inp_name in inp_names:
        key = get_indicator_from_name(inp_name, fallback="_")
        assert key not in inputs, (
            f"duplicate key '{key}' for input '"
            f"{inp_name}' --> object[{inputs[key]}]"
        )
        inputs[key] = SourceFactory.make_source(str(inp_path / inp_name))

    assert "_" in inputs, "the base set should be available"
    sink = AssertingSink()

    # read all names (files) in the tpl_path
    tlp_names = [p.name for p in tpl_path.iterdir() if p.is_file()]

    for tlp_name in tlp_names:
        # load the expected parts from the matching output-file in the sink
        sink.load_parts(get_expected_parts(out_path / tlp_name))
        generator_settings = GeneratorSettings(
            get_indicator_from_name(tlp_name)
        )

        # process
        log.debug(f"processing test-template: {tpl_path / tlp_name}")
        try:
            g.process(
                tlp_name,
                inputs,
                generator_settings,
                sink,
                vars_dict={"my_domain": "realexample.org"},
            )
        except Exception as e:
            log.exception(e)
            log.exception("failed to process template")
            raise

        # assure all records were passed
        sink.evaluate()
    log.debug("ending test_templates")
    time.sleep(1)
    Subyt(
        source=str(SUBYT_TEST_FOLDER / "resources/data.csv"),
        sink=str(SUBYT_TEST_FOLDER / "tmp/data/{key}.ttl"),
        template_name="data.ttl.j2",
        template_folder=str(SUBYT_TEST_FOLDER / "resources"),
        conditional=True,
    ).process()
    A_mtime4 = a_path.stat().st_mtime
    D_mtime4 = d_path.stat().st_mtime
    assert A_mtime3 <= A_mtime4  # output file should not have been updated

    # fifth run and one of the output files is missing
    time.sleep(1)
    d_path.unlink()
    Subyt(
        source=str(SUBYT_TEST_FOLDER / "resources/data.csv"),
        sink=str(SUBYT_TEST_FOLDER / "tmp/data/{key}.ttl"),
        template_name="data.ttl.j2",
        template_folder=str(SUBYT_TEST_FOLDER / "resources"),
        conditional=True,
    ).process()
    A_mtime5 = a_path.stat().st_mtime
    D_mtime5 = d_path.stat().st_mtime
    assert A_mtime4 == A_mtime5  # output file should not have been updated
    assert D_mtime4 < D_mtime5  # output file should have been updated

    # reset input file
    df = pd.read_csv(str(SUBYT_TEST_FOLDER / "resources/data.csv"))
    df.at[0, "value"] = 1
    df.to_csv(str(SUBYT_TEST_FOLDER / "resources/data.csv"), index=False)
