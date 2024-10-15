# your_submodule/sinks/html_sink.py

from typing import List

from ..testing.base import TestResult


def write_html(results: List[TestResult], output_file: str) -> None:
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Test Results</title>
    <style>
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .success { color: green; }
        .error { color: red; }
    </style>
</head>
<body>
    <h1>Test Results</h1>
    <table>
        <thead>
            <tr>
                <th>Success</th>
                <th>Error</th>
                <th>Message</th>
            </tr>
        </thead>
        <tbody>
    """

    for result in results:
        success_class = "success" if result.success else "error"
        html_content += f"""
            <tr>
                <td class="{success_class}">{result.success}</td>
                <td>{result.error}</td>
                <td>{result.message}</td>
            </tr>
        """

    html_content += """
        </tbody>
    </table>
</body>
</html>
    """

    try:
        with open(output_file, "w") as f:
            f.write(html_content)
    except IOError as e:
        print(f"Error writing to file {output_file}: {e}")
        # Consider raising an exception or returning a status code

    for result in results:
        success_class = "success" if result.success else "error"
        html_content += f"""
            <tr>
                <td class="{success_class}">{result.success}</td>
                <td>{result.error}</td>
                <td>{result.message}</td>
            </tr>
        """

    html_content += """
        </tbody>
    </table>
</body>
</html>
    """

    with open(output_file, "w") as f:
        f.write(html_content)


# In the future add some way to visualise this with graphs or something
# For now this is good enough
