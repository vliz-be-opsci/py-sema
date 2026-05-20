import requests
import shutil
import zipfile
import logging
import tempfile
import glob
from sema.commons.service import ServiceBase, ServiceResult, Trace
from pathlib import Path
from rdflib import Graph


logger = logging.getLogger(__name__)

class ROGetterResult(ServiceResult):
    """Result of the ROGetter service"""

    def __init__(self):
        self._success = False

    @property
    def success(self) -> bool:
        return self._success


class ROGetter(ServiceBase):
    def __init__(self, *, uri, output_path = None, force = False):
        # uri = "https://data.emobon.embrc.eu/observatory-profile/latest"
        assert uri, "URI is required"
        if not uri.endswith("/"):
            uri = uri + "/"
        self._uri = uri
        self._output_path = Path(output_path or ".")
        self._result = ROGetterResult()
        self._force = force

    @Trace.init(Trace)
    def process(self) -> ROGetterResult:
        query_result = (
            Graph()
            .parse(data=requests.get(f"{self._uri}ro-crate-metadata.json").text, format="json-ld", base=self._uri)
            .query(f"""
            PREFIX schema: <http://schema.org/>

            SELECT ?d ?e 
            WHERE {{
                <{self._uri}ro-crate-metadata.json> schema:about ?o .
                ?o schema:distribution ?d .
                ?d schema:encodingFormat ?e .
            }}
            """)
        )  # TODO: consider moving this query to sema/query/sparql_templates

        assert len(query_result) <= 1, "Expected exactly one distribution"

        distribution, encoding_format = next(iter(query_result))
        assert encoding_format.strip() == "application/zip", f"Expected zip distribution, got {encoding_format}"

        if self._force and self._output_path.exists():
            shutil.rmtree(self._output_path)

        if self._output_path != "." and not self._output_path.exists():
            self._output_path.mkdir(parents=True, exist_ok=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            zipball = requests.get(distribution)
            temp_dir = Path(temp_dir)
            with open(temp_dir / "zipball.zip", "wb") as f:
                f.write(zipball.content)
            with zipfile.ZipFile(temp_dir / "zipball.zip", 'r') as f:
                f.extractall(temp_dir / "zipball")
            for path in glob.glob(str(temp_dir / "zipball" / "*" / "*")):
                shutil.move(path, self._output_path)

        self._result._success = True
        return self._result
