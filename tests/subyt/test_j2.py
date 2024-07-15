import logging
import os

from conftest import run_single_test

from sema.subyt.j2.generator import JinjaBasedGenerator

log = logging.getLogger(__name__)


def test_JinjaBasedGenerator():
    jb_generator = JinjaBasedGenerator()
    abs_folder = os.path.abspath(".")
    assert jb_generator._templates_folder == "."
    assert str(jb_generator) == f"JinjaBasedGenerator('{abs_folder}')"


if __name__ == "__main__":
    run_single_test(__file__)
