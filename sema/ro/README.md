# sema-roc: RO-Crate Creator

`sema-roc` (Research Object Creator) generates RO-Crate metadata files from YAML configuration files.

## Overview

The RO Creator module provides:
- Generation of `ro-crate-metadata.json` from YAML configurations
- Support for RO-Crate specification compliance
- Environment variable resolution in configurations
- Flexible output file naming
- Force overwrite mode for updates

## Installation

```bash
poetry install
# Or for development
poetry install --with dev --with tests
```

## Command-Line Usage

```bash
sema-roc [root] [out] [options]
```

### Positional Arguments

- `root`: Path of the RO-Crate to work on (where `roc-*.yml` is found, and where `ro-crate-metadata.json` is placed). Defaults to current working directory.
- `out`: Name of output file to produce. Defaults to `ro-crate-metadata.json`. Can be absolute or relative to the specified root.

### Optional Arguments

- `-f, --force`: Force writing output, overwrite existing files
- `-e, --load-os-env`: Load OS environment variables for use in `!resolve` tags
- `-l, --logconf LOGCONF`: Path to logging configuration file

## Usage Examples

### Basic RO-Crate Creation

```bash
# Create ro-crate-metadata.json in current directory
sema-roc
```

### Specify RO-Crate Root

```bash
# Create in specific directory
sema-roc /path/to/rocrate
```

### Custom Output File

```bash
# Use custom output filename
sema-roc . my-ro-crate.json
```

### Force Overwrite

```bash
# Overwrite existing metadata file
sema-roc --force
```

### With Environment Variables

```bash
# Enable environment variable resolution
export PROJECT_NAME="My Research Project"
export VERSION="1.0.0"
sema-roc --load-os-env
```

### Complete Example

```bash
sema-roc \
  /path/to/my-rocrate \
  custom-metadata.json \
  --force \
  --load-os-env \
  --logconf logging.yml
```

## Configuration File Format

Create a `roc-me.yml` (or similar `roc-*.yml` pattern) file:

```yaml
# roc-me.yml
"@context": "https://w3id.org/ro/crate/1.1/context"
"@graph":
  - "@id": "ro-crate-metadata.json"
    "@type": "CreativeWork"
    conformsTo:
      "@id": "https://w3id.org/ro/crate/1.1"
    about:
      "@id": "./"
      
  - "@id": "./"
    "@type": "Dataset"
    name: "My Research Dataset"
    description: "Description of my research dataset"
    datePublished: "2024-01-23"
    license:
      "@id": "https://creativecommons.org/licenses/by/4.0/"
    author:
      - "@id": "#author1"
        
  - "@id": "#author1"
    "@type": "Person"
    name: "Jane Researcher"
    email: "jane@example.org"
```

### Using Environment Variables

```yaml
# roc-me.yml with environment variable resolution
"@graph":
  - "@id": "./"
    "@type": "Dataset"
    name: !resolve "${PROJECT_NAME}"
    version: !resolve "${VERSION}"
    author:
      name: !resolve "${AUTHOR_NAME}"
```

Enable with:

```bash
export PROJECT_NAME="My Project"
export VERSION="1.0.0"
export AUTHOR_NAME="Jane Doe"
sema-roc --load-os-env
```

## Programmatic Usage

```python
from sema.ro.creator import ROCreator

# Create RO-Crate metadata
creator = ROCreator(
    root_path="/path/to/rocrate",
    output_name="ro-crate-metadata.json",
    force=False,
    load_env=False
)

# Generate metadata file
creator.create()
```

### With Environment Variables

```python
import os
from sema.ro.creator import ROCreator

# Set environment variables
os.environ['PROJECT_NAME'] = 'My Project'
os.environ['VERSION'] = '1.0.0'

# Create with env variable resolution
creator = ROCreator(
    root_path="./rocrate",
    load_env=True
)

creator.create()
```

## RO-Crate Structure

A typical RO-Crate directory structure:

```
my-rocrate/
├── roc-me.yml                  # Configuration file
├── ro-crate-metadata.json      # Generated metadata
├── data/                       # Research data
│   ├── dataset.csv
│   └── results.json
├── workflows/                  # Computational workflows
│   └── analysis.cwl
└── README.md                   # Documentation
```

## RO-Crate Entities

### Root Dataset

```yaml
- "@id": "./"
  "@type": "Dataset"
  name: "My Dataset"
  description: "Dataset description"
  datePublished: "2024-01-23"
```

### Data Files

```yaml
- "@id": "data/dataset.csv"
  "@type": "File"
  name: "Research Data"
  encodingFormat: "text/csv"
  contentSize: "1024000"
```

### People

```yaml
- "@id": "#alice"
  "@type": "Person"
  name: "Alice Researcher"
  email: "alice@example.org"
  affiliation:
    "@id": "https://ror.org/example"
```

### Organizations

```yaml
- "@id": "https://ror.org/example"
  "@type": "Organization"
  name: "Example University"
  url: "https://example.edu"
```

### Computational Workflows

```yaml
- "@id": "workflows/analysis.cwl"
  "@type": ["File", "ComputationalWorkflow"]
  name: "Analysis Workflow"
  programmingLanguage:
    "@id": "https://w3id.org/workflowhub/workflow-ro-crate#cwl"
```

## Best Practices

1. **Use semantic identifiers** - Use URIs for entities when possible (e.g., ORCIDs, ROR IDs)
2. **Include all relevant metadata** - Document authors, license, dates, etc.
3. **Reference external resources** - Link to related publications, datasets, etc.
4. **Validate generated metadata** - Use RO-Crate validation tools
5. **Version your configurations** - Keep `roc-me.yml` in version control
6. **Use environment variables** for deployment-specific values
7. **Document your data** - Include README and detailed descriptions

## Common Use Cases

### Research Dataset Publication

```yaml
"@graph":
  - "@id": "./"
    "@type": "Dataset"
    name: "Climate Model Output 2024"
    description: "High-resolution climate model results"
    license: "https://creativecommons.org/licenses/by/4.0/"
    datePublished: "2024-01-23"
    author:
      - "@id": "https://orcid.org/0000-0000-0000-0001"
```

### Workflow Package

```yaml
"@graph":
  - "@id": "./"
    "@type": "Dataset"
    name: "Bioinformatics Pipeline"
    mainEntity:
      "@id": "workflow.cwl"
      
  - "@id": "workflow.cwl"
    "@type": ["File", "ComputationalWorkflow"]
    programmingLanguage: "CWL"
```

### Software Package

```yaml
"@graph":
  - "@id": "./"
    "@type": "SoftwareSourceCode"
    name: "Analysis Tool"
    version: "1.0.0"
    license: "MIT"
    codeRepository: "https://github.com/example/tool"
```

## Integration with Other Services

### With sema-harvest

Package harvested data as RO-Crate:

```bash
# Harvest data
sema-harvest --config harvest.yaml --dump data/harvested.ttl

# Create RO-Crate metadata
sema-roc /path/to/rocrate
```

### With sema-bench

Orchestrate RO-Crate creation:

```yaml
# sembench.yaml
services:
  - name: generate_data
    command: sema-query
    args: [--source, data.ttl, --output, results.csv]
    
  - name: create_rocrate
    command: sema-roc
    args: [., ro-crate-metadata.json, --force]
    depends_on: generate_data
```

## Validation

Validate generated RO-Crate metadata:

```bash
# Using online validator
# Upload ro-crate-metadata.json to https://www.researchobject.org/ro-crate/tools/

# Using ro-crate-py (if installed)
rocrate validate ro-crate-metadata.json
```

## Troubleshooting

**Configuration file not found:**
- Ensure `roc-*.yml` file exists in root directory
- Check file naming pattern matches `roc-*.yml`
- Verify file permissions

**Output file exists:**
- Use `--force` to overwrite existing files
- Or remove existing file manually

**Environment variables not resolved:**
- Enable with `--load-os-env` flag
- Verify environment variables are set (`echo $VAR_NAME`)
- Check YAML syntax for `!resolve` tags

**Invalid JSON output:**
- Validate YAML configuration syntax
- Ensure proper nesting and indentation
- Check for special characters requiring escaping

## RO-Crate Resources

- [RO-Crate Specification](https://www.researchobject.org/ro-crate/)
- [RO-Crate Tools](https://www.researchobject.org/ro-crate/tools/)
- [Workflow RO-Crate Profile](https://w3id.org/workflowhub/workflow-ro-crate)
- [Schema.org](https://schema.org/) - Vocabulary reference

## Related Modules

- [RO Blueprint](./creator/roblueprint.py) - RO-Crate blueprint definitions
- [RO Builder](./creator/robuilder.py) - RO-Crate construction logic
- [RO Creator](./creator/rocreator.py) - Main creation implementation

## See Also

- Test files: `tests/ro/` for usage examples (if available)
- RO-Crate examples: [GitHub repository](https://github.com/ResearchObject/ro-crate/)
- FAIR data principles: [GO FAIR](https://www.go-fair.org/)