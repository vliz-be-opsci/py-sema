# your_submodule/sinks/__init__.py

from .csv_sink import write_csv
from .html_sink import write_html
from .yml_sink import write_yml

__all__ = [
    "write_csv",
    "write_html",
    "write_yml",
]
