# your_submodule/sinks/csv_sink.py

import csv
from typing import List

from ..testing.base import TestBase


def write_csv(results: List[TestBase], output_file: str):
    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["url", "type", "success", "error", "message"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "url": result.url,
                    "type": result.type_test,
                    "success": result.success,
                    "error": result.error,
                    "message": result.message,
                }
            )
