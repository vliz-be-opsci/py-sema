# sema-subyt: Template-Based RDF Triple Generation

`sema-subyt` (Subject-Template) produces RDF triples by applying Jinja2 templates to input data sets.

## Overview

The subyt module provides:
- Template-based RDF generation from structured data
- Support for CSV, JSON, YAML, and other tabular formats
- Jinja2 templating with RDF-specific filters and functions
- Iteration over data sets with unique filtering
- Conditional execution based on file timestamps
- Integration with URI templates for dynamic outputs

## Installation

```bash
poetry install
# Or for development
poetry install --with dev --with tests
```

## Command-Line Usage

```bash
sema-subyt --name <template> [options]
```

### Required Arguments

- `-n, --name NAME`: Name of the template to use (without extension)

### Optional Arguments

**Input/Output:**
- `-i, --input FILE`: Base input set file (shorthand for `-s _ FILE`)
- `-s, --set KEY FILE`: Add named data set under `sets["KEY"]` for templating
- `-o, --output FILE|PATTERN`: Output file path (can use URI templates like `{name}.ttl`)
- `-t, --templates FOLDER`: Folder containing templates (default: current directory)

**Variables and Filtering:**
- `-v, --var NAME VALUE`: Add named variables to the templating context
- `-u, --unique PATTERN`: Filter unique records using URI template pattern
- `-f, --force`: Force writing output, overwrite existing files
- `-r, --allow-repeated-sink-paths`: Allow repeated sink paths for duplicated data

**Execution Control:**
- `-c, --conditional`: Execute only when input has been updated
- `-m, --mode MODE`: Iteration mode (see modes below)
- `-l, --logconf LOGCONF`: Path to logging configuration file

### Iteration Modes

- `it` (default): Iterate over each row in input set
- `no-it`: Apply template once to complete input set
- `ig`: Case-insensitive mode (to be implemented)
- `fl`: Flatten mode (to be implemented)

Combine modes: `-m it,fl` or `-m no-it`

## Usage Examples

### Basic Template Application

```bash
sema-subyt --name person_to_rdf --input persons.csv --output persons.ttl
```

### Using Multiple Data Sets

```bash
sema-subyt \
  --name combined_template \
  --set persons persons.csv \
  --set organizations orgs.csv \
  --output output.ttl
```

### With Variables

```bash
sema-subyt \
  --name dataset_template \
  --input data.csv \
  --var base_uri http://example.org/ \
  --var year 2024 \
  --output dataset.ttl
```

### Dynamic Output Files

```bash
# Create one file per person
sema-subyt \
  --name person_template \
  --input persons.csv \
  --output "output/{name}.ttl"
```

### Filter Unique Records

```bash
# Process only first occurrence of each unique ID
sema-subyt \
  --name template \
  --input data.csv \
  --unique "{id}" \
  --output output.ttl
```

### Conditional Execution

```bash
# Only run if input has been modified
sema-subyt \
  --name template \
  --input data.csv \
  --output output.ttl \
  --conditional
```

### Non-Iterative Mode

```bash
# Apply template once to entire dataset
sema-subyt \
  --name summary_template \
  --input data.csv \
  --mode no-it \
  --output summary.ttl
```

### Complete Example

```bash
sema-subyt \
  --templates /path/to/templates \
  --name person_to_foaf \
  --input persons.csv \
  --var namespace http://example.org/persons/ \
  --var created 2024-01-23 \
  --output "rdf/{id}.ttl" \
  --unique "{id}" \
  --force \
  --logconf logging.yml
```

## Template Format

Templates use Jinja2 syntax with RDF-specific features:

### Basic Template

```turtle
{# templates/person_to_rdf.ttl #}
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

{% for person in sets._ %}
<{{ namespace }}{{ person.id }}>
    a foaf:Person ;
    foaf:name "{{ person.name }}" ;
    foaf:mbox <mailto:{{ person.email }}> ;
    {% if person.age %}
    foaf:age {{ person.age | int }}^^xsd:integer ;
    {% endif %}
    .
{% endfor %}
```

### With Multiple Sets

```turtle
{# templates/combined.ttl #}
@prefix org: <http://www.w3.org/ns/org#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

{% for org in sets.organizations %}
<{{ base_uri }}org/{{ org.id }}>
    a org:Organization ;
    org:name "{{ org.name }}" .
{% endfor %}

{% for person in sets.persons %}
<{{ base_uri }}person/{{ person.id }}>
    a foaf:Person ;
    foaf:name "{{ person.name }}" ;
    org:memberOf <{{ base_uri }}org/{{ person.org_id }}> .
{% endfor %}
```

## Programmatic Usage

```python
from sema.subyt import SubytService

# Configure service
service = SubytService(
    template_name="person_to_rdf",
    template_folder="./templates",
    input_file="persons.csv",
    output_pattern="output/{id}.ttl",
    variables={"namespace": "http://example.org/"}
)

# Execute template
service.execute()
```

### With Multiple Data Sets

```python
from sema.subyt import SubytService

service = SubytService(
    template_name="combined",
    template_folder="./templates",
    sets={
        "persons": "persons.csv",
        "organizations": "orgs.csv"
    },
    output_pattern="output.ttl"
)

service.execute()
```

## Template Filters and Functions

sema-subyt provides Jinja2 filters for RDF generation:

### Type Conversion

```jinja2
{{ value | int }}           {# Convert to integer #}
{{ value | double }}        {# Convert to double #}
{{ value | bool }}          {# Convert to boolean #}
{{ value | date }}          {# Convert to date #}
{{ value | datetime }}      {# Convert to datetime #}
{{ value | gyear }}         {# Convert to gYear #}
```

### XSD Formatting

```jinja2
{{ value | xsd_fmt('integer') }}    {# Format as xsd:integer #}
{{ value | xsd_fmt('date') }}       {# Format as xsd:date #}
{{ value | xsd_fmt('string') }}     {# Format as xsd:string #}
```

### URI Cleaning

```jinja2
{{ uri | clean_uri }}       {# Normalize and clean URI #}
{{ text | uri_encode }}     {# URL-encode text #}
```

## Input Data Formats

Supported input formats:
- **CSV**: Comma-separated values
- **TSV**: Tab-separated values  
- **JSON**: JSON arrays or objects
- **YAML**: YAML lists or dictionaries
- **XML**: XML with xmlasdict conversion

## URI Template Patterns

Use URI templates in `--output` and `--unique`:

```bash
# Use fields from data
--output "output/{category}/{id}.ttl"
--unique "{person_id}"

# Use variables
--output "{base_path}/{year}/{name}.ttl"
```

## Best Practices

1. **Organize templates by domain** - Group related templates in folders
2. **Use meaningful variable names** - Make templates self-documenting
3. **Validate generated RDF** - Check syntax with `rapper` or similar tools
4. **Use unique filtering** to avoid processing duplicates
5. **Test templates on small datasets** before processing large files
6. **Use conditional execution** for incremental workflows
7. **Store templates in version control** for reproducibility

## Common Use Cases

### CSV to RDF Conversion

```bash
# Convert tabular data to RDF
sema-subyt \
  --name csv_to_rdf \
  --input data.csv \
  --output data.ttl
```

### Data Integration

```bash
# Combine multiple data sources
sema-subyt \
  --name integrate \
  --set people people.csv \
  --set places places.json \
  --set events events.yaml \
  --output integrated.ttl
```

### Incremental Processing

```bash
# Only process if input changed
sema-subyt \
  --name incremental \
  --input data.csv \
  --output output.ttl \
  --conditional
```

### Batch Generation

```bash
# Generate one file per record
sema-subyt \
  --name individual \
  --input records.csv \
  --output "records/{id}.ttl"
```

## Integration with Other Services

### With sema-query

```bash
# Generate RDF, then query it
sema-subyt --name gen --input data.csv --output data.ttl
sema-query --source data.ttl --template_name analysis.sparql
```

### With sema-bench

```yaml
# sembench.yaml
services:
  - name: generate_rdf
    command: sema-subyt
    args:
      - --name
      - template
      - --input
      - data.csv
      - --output
      - output.ttl
      
  - name: validate
    command: sema-bench
    depends_on: generate_rdf
```

## Troubleshooting

**Template not found:**
- Check template folder path with `--templates`
- Ensure template file has `.ttl` or `.rdf` extension
- Verify template name matches file name (without extension)

**Invalid output:**
- Validate Jinja2 syntax in template
- Check that all variables are defined
- Ensure RDF syntax is correct (use `rapper` to validate)

**No output generated:**
- Verify input file exists and has data
- Check that unique pattern doesn't filter all records
- Use `--force` to overwrite existing files

**Conditional execution skipped:**
- Input file must be newer than output file
- Use `--force` to override conditional check

## Related Modules

- [Jinja2 Utilities](../commons/j2/) - Template filters and functions
- [Template Management](../commons/j2-template/) - Template loading
- [Service Framework](../commons/service/) - Service base classes

## See Also

- Test files: `tests/subyt/` for usage examples
- [Jinja2 documentation](https://jinja.palletsprojects.com/)
- [URI Template spec (RFC 6570)](https://tools.ietf.org/html/rfc6570)