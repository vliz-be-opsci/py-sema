# your_submodule/sinks/html_sink.py

from typing import List
from ..testing.base import TestResult


def write_html(results: List[TestResult], output_file: str):
    html_content = "<html><head><title>Test Results</title></head><body>"
    html_content += "<table border='1'><tr><th>Success</th><th>Error</th><th>Message</th></tr>"
    for result in results:
        html_content += f"<tr><td>{result.success}</td><td>{result.error}</td><td>{result.message}</td></tr>"
    html_content += "</table></body></html>"

    with open(output_file, "w") as f:
        f.write(html_content)


# In the future add some way to visualise this with graphs or something
# For now this is good enough
