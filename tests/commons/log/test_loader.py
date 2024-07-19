# loader tests here

import os
import tempfile
from pathlib import Path

import pytest
from conftest import TEST_INPUT_FOLDER

from sema.commons.log.loader import load_log_config


# Test loading default log configuration
def test_load_default_log_config():
    # Assuming a default log configuration file exists for the test
    default_config_path = Path(TEST_INPUT_FOLDER) / "debug_logconf.yml"
    with open(default_config_path, "w") as f:
        f.write("version: 1\n")
    load_log_config()
    # Add assertions to verify the logging configuration is loaded


# Test handling of non-existent log configuration file
def test_nonexistent_log_config():
    with pytest.raises(FileNotFoundError):
        load_log_config("nonexistent_file.yml")


# Test loading YAML log configuration
def test_load_yaml_log_config():
    with tempfile.NamedTemporaryFile(
        "w", suffix=".yml", delete=False
    ) as tmpfile:
        tmpfile.write("version: 1\n")
    load_log_config(tmpfile.name)
    os.unlink(tmpfile.name)
    # Add assertions to verify the YAML configuration is loaded


# Test loading non-YAML log configuration (if applicable)
# This test is dependent on the support for
# non-YAML configurations in your application