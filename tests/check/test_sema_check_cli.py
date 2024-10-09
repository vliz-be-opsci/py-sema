import sys
import logging
from pathlib import Path
from sema.check.__main__ import main as query_main

log = logging.getLogger(__name__)


def test_main():
    log.info(f"test_main_check")

    input_folder = Path(__file__).parent / "test_files"
    output_formats = ["csv", "html", "yml"]
    for output in output_formats:
        cli_line = f"--input_folder {input_folder} --output {output}"
        # Backup the original sys.argv
        original_argv = sys.argv
        try:
            # Set sys.argv to simulate command-line arguments
            sys.argv = ["sema-check"] + cli_line.split()
            success: bool = query_main(sys.argv)
            # assert success, f"sema-check failed for output format: {output}"
        finally:
            # Restore the original sys.argv
            sys.argv = original_argv
