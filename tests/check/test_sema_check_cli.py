import logging
import sys
from pathlib import Path

from sema.check.__main__ import main as query_main

log = logging.getLogger(__name__)


def test_main() -> None:
    input_folder = Path(__file__).parent / "test_files"
    output_formats = ["csv", "html", "yml"]
    for output in output_formats:
        cli_line = f"--input_folder {input_folder} --output {output}"
        # Backup the original sys.argv
        original_argv = sys.argv
        output_file = None
        try:
            # Set sys.argv to simulate command-line arguments
            sys.argv = ["sema-check", *cli_line.split()]
            success: bool = query_main(sys.argv)
            assert (
                not success
            ), f"sema-check failed for output format: {output}"

            # Check if output file is created
            output_file = Path(f"results.{output}")
            assert (
                output_file.exists()
            ), f"Output file for {output} format not created"

        finally:
            # Restore the original sys.argv
            sys.argv = original_argv
            # Clean up the output file
            if output_file and output_file.exists():
                output_file.unlink()
