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

### Optional Arguments

- `-t, --template_name TEMPLATE_NAME`: Name of the SPARQL template to use
- `-tf, --template_folder PATH`: Folder containing SPARQL templates (default: built-in templates)
- `-f, --output_format {csv,tsv}`: Output format (default: csv)
- `-o, --output_location FILE`: Output file path (default: stdout)
- `-v, --variables [VARIABLES ...]`: Template variables in format `name=value`
- `-l, --logconf LOGCONF`: Path to logging configuration file (YAML)

## Usage Examples

### Query a Local RDF File

```bash
# Basic query with default template
sema-query --source data.ttl --output_format csv
```

### Query a SPARQL Endpoint

```bash
sema-query \
  --source http://localhost:7200/repositories/myrepo \
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
sema-query --source data.ttl --template_name all.sparql
```

### Filter by Type

```bash
sema-query \
  --source data.ttl \
  --template_name by_type.sparql \
  --variables type=Person
```

### Join Multiple Graphs

```bash
sema-query \
  --source graph1.ttl graph2.ttl graph3.ttl \
  --template_name join_query.sparql
```

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