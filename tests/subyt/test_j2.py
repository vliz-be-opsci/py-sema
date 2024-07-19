import logging
import os

from sema.subyt.j2.generator import JinjaBasedGenerator

log = logging.getLogger(__name__)


def test_JinjaBasedGenerator():
    jb_generator = JinjaBasedGenerator()
    abs_folder = os.path.abspath(".")
    assert jb_generator._templates_folder == "."
    assert str(jb_generator) == f"JinjaBasedGenerator('{abs_folder}')"
