# sema-query: SPARQL Query Execution and Table Extraction

`sema-query` extracts tabular data from RDF knowledge graphs using SPARQL queries and Jinja2 templates.

## Overview

The query module provides:
- SPARQL query execution against RDF files and endpoints
- Template-based queries using Jinja2 for reusability
- Output to CSV or TSV formats
- Support for multiple data sources (files, URLs, SPARQL endpoints)
- Variable substitution in query templates

## Installation

```bash
poetry install
# Or for development
poetry install --with dev --with tests
```

## Command-Line Usage

```bash
sema-query --source <file-or-url> [options]
```

### Required Arguments

- `-s, --source FILE [URL ...]`: Input RDF file(s), URL(s), or SPARQL endpoint(s)
  - Can be local files (`.ttl`, `.rdf`, `.nt`, `.jsonld`)
  - Can be URLs to download RDF data
  - Can be SPARQL endpoint URLs
- `-t, --template_name TEMPLATE_NAME`: Name of the SPARQL template to use
- `-o, --output_location FILE`: Output file path (relative to current directory)

### Optional Arguments

- `-tf, --template_folder PATH`: Folder containing SPARQL templates (default: built-in templates)
- `-f, --output_format {csv,tsv}`: Output format (default: csv)
- `-v, --variables [VARIABLES ...]`: Template variables in format `name=value`
- `-l, --logconf LOGCONF`: Path to logging configuration file (YAML)

## Usage Examples

### Query a Local RDF File

```bash
# Basic query with built-in template
sema-query --source data.ttl --template_name all.sparql --output_location results.csv
```

### Query a SPARQL Endpoint

```bash
sema-query \
  --source http://localhost:7200/repositories/myrepo \
  --template_name all.sparql \
  --output_format csv \
  --output_location results.csv
```

### Using SPARQL Templates

```bash
# Use a specific template with variables
sema-query \
  --source data.ttl \
  --template_folder ./templates \
  --template_name persons.sparql \
  --variables limit=100 type=Person \
  --output_format csv
```

### Query Multiple Sources

```bash
# Merge multiple RDF files into a single graph
sema-query \
  --source file1.ttl file2.ttl file3.ttl \
  --template_name all.sparql \
  --output_location merged_results.csv
```

### Complete Example with All Options

```bash
sema-query \
  --source data.ttl \
  --template_folder /path/to/templates \
  --template_name extract_data.sparql \
  --variables year=2024 status=active \
  --output_format tsv \
  --output_location results.tsv \
  --logconf logging.yml
```

## Extensive Examples

These examples are designed to mirror the style of the scripts in [examples/simple_query.py](examples/simple_query.py), but with more concrete command lines and template variables to copy and adapt.

### 1) Quick start with embedded templates

The query module ships with embedded templates, so you can run useful queries without creating your own.

```bash
# List all triples (optionally limit with -v N=10)
sema-query \
  --source data.ttl \
  --template_name all.sparql \
  --variables N=10 \
  --output_location triples.csv
```

What you can do:
- Extract a quick preview of any RDF file.
- Use the same command against a SPARQL endpoint (replace `data.ttl` with a URL).

### 2) Inspect the types available in a graph

Use the built-in `rdf-types.sparql` template to learn what kinds of entities are in a dataset.

```bash
sema-query \
  --source data.ttl \
  --template_name rdf-types.sparql \
  --variables regex=Person \
  --output_location types.csv
```

What you can do:
- Scan for classes (types) in a dataset.
- Filter the results with `regex` when working with large graphs.

### 3) Query a SKOS collection list

The `skos-collection.sparql` template lists SKOS collections, optionally filtered by language.

```bash
sema-query \
  --source http://vocab.nerc.ac.uk/sparql/sparql \
  --template_name skos-collection.sparql \
  --variables language="en" \
  --output_location collections.csv
```

What you can do:
- Identify collections on a SKOS endpoint before exploring members.
- Capture collection titles for reporting or QA.

### 4) List members of a BODC collection

The `bodc-listing.sparql` template is optimized for the NERC BODC vocabularies.

```bash
sema-query \
  --source http://vocab.nerc.ac.uk/sparql/sparql \
  --template_name bodc-listing.sparql \
  --variables cc=P06 lang=en N=50 \
  --output_location p06-members.csv
```

What you can do:
- Fetch a known collection and limit results for quick inspection.
- Use the same template on local dumps (see next example).

### 5) Run the same template on a local dump

```bash
sema-query \
  --source tests/query/sources/bodc/20230605-P06-dump.ttl \
  --template_name bodc-listing.sparql \
  --variables cc=P06 lang=en \
  --output_location p06-dump.csv
```

What you can do:
- Compare online endpoint results with local RDF dumps.
- Generate stable, reproducible CSVs for downstream workflows.

### 6) Search within a set of collections

The `bodc-find.sparql` template uses a list of collection codes and a regex.

```bash
sema-query \
  --source http://vocab.nerc.ac.uk/sparql/sparql \
  --template_name bodc-find.sparql \
  --variables collections[]=P01,P06 regex=.*orca.* language=en \
  --output_location bodc-find.csv
```

What you can do:
- Search across multiple collections with a single query.
- Use regex to locate term labels or identifiers.

### 7) Use a custom template folder

```bash
sema-query \
  --source data.ttl \
  --template_folder ./my-templates \
  --template_name my-query.sparql \
  --variables dataset=stations limit=25 \
  --output_location custom.csv
```

What you can do:
- Build a reusable library of domain-specific queries.
- Keep templates in version control alongside your project.

### 8) Mix multiple RDF files into one queryable graph

```bash
sema-query \
  --source data/part1.ttl data/part2.ttl data/part3.ttl \
  --template_name all.sparql \
  --variables N=100 \
  --output_location merged.csv
```

What you can do:
- Treat multiple RDF files as one combined graph.
- Run a single query over merged data sources.

## SPARQL Template Format

Templates use Jinja2 syntax for variable substitution:

```sparql
# templates/persons.sparql
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?name ?email ?age
WHERE {
    ?person rdf:type foaf:{{ type | default('Person') }} .
    ?person foaf:name ?name .
    OPTIONAL { ?person foaf:mbox ?email }
    OPTIONAL { ?person foaf:age ?age }
}
ORDER BY ?name
LIMIT {{ limit | default(100) }}
```

Use this template:

```bash
sema-query \
  --source persons.ttl \
  --template_folder templates \
  --template_name persons.sparql \
  --variables type=Person limit=50
```

## Programmatic Usage

```python
from sema.query import GraphSource

# Build a graph source from a file
source = GraphSource.build("data.ttl")

# Or from a SPARQL endpoint
source = GraphSource.build("http://localhost:7200/repositories/myrepo")

# Or from multiple sources
source = GraphSource.build("file1.ttl", "file2.ttl")

# Execute a SPARQL query
query = """
SELECT ?subject ?predicate ?object
WHERE {
    ?subject ?predicate ?object .
}
LIMIT 10
"""
result = source.query(query)

# Process results
for row in result:
    print(row)
```

### Using the Query Builder

```python
from sema.query import DefaultSparqlBuilder

# Create a query builder with templates
builder = DefaultSparqlBuilder(
    template_folder="./templates"
)

# Build a query from a template
query = builder.build_query(
    template_name="persons.sparql",
    variables={"limit": 50, "type": "Person"}
)

# Execute the query
source = GraphSource.build("data.ttl")
result = source.query(query)
```

### Working with Query Results

Every query returns a `QueryResult` implementation that can be converted into common formats.

```python
from sema.query import GraphSource

source = GraphSource.build("data.ttl")
result = source.query("SELECT * WHERE { ?s ?p ?o } LIMIT 5")

rows = result.to_list()        # List[dict]
as_dict = result.to_dict()     # Dict[str, List]
df = result.to_dataframe()     # pandas.DataFrame
result.as_csv("out.csv")       # Write CSV (or use sep="\t" for TSV)
```

## Template Management

### Install Default Templates

```bash
sema-query-templates
```

This installs default SPARQL templates to your user directory.

### Custom Template Organization

Organize templates by domain or purpose:

```
templates/
├── persons/
│   ├── list_all.sparql
│   └── by_name.sparql
├── organizations/
│   └── by_location.sparql
└── common/
    └── all.sparql
```

## Supported Input Formats

- **Turtle** (`.ttl`)
- **RDF/XML** (`.rdf`, `.xml`)
- **N-Triples** (`.nt`)
- **JSON-LD** (`.jsonld`)
- **SPARQL endpoints** (HTTP URLs)

## Output Formats

- **CSV**: Comma-separated values (default)
- **TSV**: Tab-separated values

## Best Practices

1. **Use templates for reusable queries** - Create a template library for common query patterns
2. **Parameterize with variables** - Make templates flexible with Jinja2 variables
3. **Test queries on small datasets first** - Verify query logic before running on large graphs
4. **Use LIMIT clauses** - Prevent accidentally retrieving huge result sets
5. **Organize templates by domain** - Group related queries in folders
6. **Handle optional patterns carefully** - Use `OPTIONAL` for properties that may not exist

## Common Use Cases

### Extract All Triples

```bash
sema-query --source data.ttl --template_name all.sparql --output_location all.csv
```

### Filter by Type

```bash
sema-query \
  --source data.ttl \
  --template_name by_type.sparql \
  --variables type=Person \
  --output_location types.csv
```

### Join Multiple Graphs

```bash
sema-query \
  --source graph1.ttl graph2.ttl graph3.ttl \
  --template_name join_query.sparql
```

## Template Variables: CLI Formats

The CLI parser supports three variable styles:

- `key=value` for single values
- `list_key[]=a,b,c` for lists
- `dict_key.one=1` for single-level dicts

Examples:

```bash
# Single value
sema-query -s data.ttl -t all.sparql -v N=10 -o out.csv

# List values
sema-query -s endpoint -t bodc-find.sparql -v collections[]=P01,P06 -o out.csv

# Dict-like values
sema-query -s data.ttl -t my-template.sparql -v filters.one=foo filters.two=bar -o out.csv
```

Note: you cannot mix files and endpoints in a single `--source` list. Use either files/URLs or a SPARQL endpoint, but not both.

## Troubleshooting

**Query returns no results:**
- Check that the prefixes in your query match the namespaces in your data
- Verify that the patterns in your WHERE clause match your data structure
- Use OPTIONAL for properties that may not exist

**Template not found:**
- Verify the template folder path with `--template_folder`
- Ensure the template file exists with the exact name specified
- Check file permissions

**Invalid SPARQL syntax:**
- Validate your SPARQL query syntax
- Check for proper prefix declarations
- Ensure Jinja2 variables are correctly substituted

## Related Modules

- [GraphSource](./query.py) - RDF source abstraction
- [SPARQL Builder](./query.py) - Query construction
- [Template Management](./copytpl.py) - Template installation

## See Also

- Test files: `tests/query/` for usage examples
- Example queries: Default templates installed by `sema-query-templates`
- [SPARQL 1.1 Query Language](https://www.w3.org/TR/sparql11-query/) specification