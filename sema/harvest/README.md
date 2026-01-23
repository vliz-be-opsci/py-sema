# sema-harvest: RDF Data Harvesting Service

`sema-harvest` is a service for traversing, discovering, and harvesting RDF data from various sources into a triple store.

## Overview

The harvest module provides:
- Automated RDF data collection from configured sources
- Loading and initialization of RDF data into triple stores
- Configuration-based harvesting workflows
- Support for local files and SPARQL endpoints
- Graph dumping and export capabilities

## Installation

```bash
poetry install
# Or for development
poetry install --with dev --with tests
```

## Command-Line Usage

```bash
sema-harvest [options]
```

### Optional Arguments

- `-c, --config CONFIG`: Path to folder containing configuration files or to a single configuration file (default: `./config`)
- `-d, --dump DUMP`: Path to dump the harvested resulting graph (use `-` for stdout)
- `-i, --init INIT [INIT ...]`: List of paths to files or folders to load into the store at start
- `-s, --store STORE STORE`: Pair of read_uri and write_uri for the SPARQL endpoint store
- `-l, --logconf LOGCONF`: Path to logging configuration file (YAML)

## Configuration File Format

Create YAML configuration files in your config directory:

```yaml
# config/harvest_config.yaml
sources:
  - type: file
    path: /path/to/data.ttl
    
  - type: url
    url: https://example.org/data.rdf
    
  - type: sparql
    endpoint: http://localhost:7200/repositories/source

harvesting:
  output_graph: http://example.org/harvested
  interval: 3600  # Re-harvest every hour
```

## Usage Examples

### Basic Harvesting from Configuration

```bash
sema-harvest --config ./config
```

### Harvest and Dump to File

```bash
sema-harvest \
  --config ./config/harvest.yaml \
  --dump output/harvested_data.ttl
```

### Dump to stdout

```bash
sema-harvest \
  --config ./config \
  --dump - > harvested_data.ttl
```

### Initialize Store with Existing Data

```bash
sema-harvest \
  --config ./config \
  --init data/initial1.ttl data/initial2.ttl
```

### Use External SPARQL Endpoint

```bash
sema-harvest \
  --config ./config \
  --store http://localhost:7200/repositories/myrepo/statements \
          http://localhost:7200/repositories/myrepo/statements
```

### Complete Example

```bash
sema-harvest \
  --config /path/to/config \
  --init initial_data/ \
  --store http://localhost:7200/repositories/harvest \
          http://localhost:7200/repositories/harvest/statements \
  --dump results/harvested.ttl \
  --logconf logging.yml
```

## Programmatic Usage

```python
from sema.harvest import HarvestService, HarvestConfig

# Create configuration
config = HarvestConfig(
    config_path="./config",
    init_files=["data1.ttl", "data2.ttl"]
)

# Initialize harvesting service
service = HarvestService(config)

# Run harvesting
service.execute()

# Dump results
service.dump_graph("output.ttl")
```

## Harvesting Workflows

### 1. File-based Harvesting

Harvest from local RDF files:

```yaml
# config/file_harvest.yaml
sources:
  - type: file
    path: /data/rdf/*.ttl
    format: turtle
```

```bash
sema-harvest --config config/file_harvest.yaml
```

### 2. URL-based Harvesting

Harvest from web resources:

```yaml
# config/web_harvest.yaml
sources:
  - type: url
    url: https://example.org/data.ttl
    headers:
      Accept: text/turtle
```

### 3. SPARQL Endpoint Harvesting

Harvest from remote triple stores:

```yaml
# config/sparql_harvest.yaml
sources:
  - type: sparql
    endpoint: http://dbpedia.org/sparql
    query: |
      CONSTRUCT {
        ?s ?p ?o
      } WHERE {
        ?s a <http://dbpedia.org/ontology/Person> .
        ?s ?p ?o .
      }
      LIMIT 1000
```

### 4. Scheduled Harvesting

Use with `sema-bench` for scheduled harvesting:

```yaml
# sembench.yaml
services:
  - name: harvest_daily
    type: harvest
    config: /path/to/harvest_config.yaml
    interval: 86400  # Daily
```

## Initialization Data

Load existing RDF data before harvesting:

```bash
# Load from files
sema-harvest --init data/schema.ttl data/initial.ttl

# Load from directory
sema-harvest --init data/
```

## Output Options

### Save to File

```bash
sema-harvest --config ./config --dump output.ttl
```

### Output to stdout

```bash
sema-harvest --config ./config --dump -
```

### Store in SPARQL Endpoint

```bash
sema-harvest \
  --config ./config \
  --store http://localhost:7200/repositories/myrepo \
          http://localhost:7200/repositories/myrepo/statements
```

## Best Practices

1. **Validate sources first** - Test source availability before large harvesting jobs
2. **Use initialization data** for schemas and reference data that won't change
3. **Configure appropriate intervals** for scheduled harvesting to avoid overloading sources
4. **Handle failures gracefully** - Configure retry logic in your harvest configurations
5. **Monitor harvesting** - Use logging to track progress and identify issues
6. **Organize configurations** by source or domain for maintainability

## Configuration Organization

Organize harvest configurations by purpose:

```
config/
├── schemas/
│   └── schema_harvest.yaml
├── external/
│   ├── dbpedia_harvest.yaml
│   └── wikidata_harvest.yaml
└── local/
    └── file_harvest.yaml
```

Run specific configurations:

```bash
sema-harvest --config config/external/dbpedia_harvest.yaml
```

## Integration with Other Services

### With sema-bench

Orchestrate harvesting with other tasks:

```yaml
# sembench.yaml
services:
  - name: harvest
    command: sema-harvest
    args:
      - --config
      - config/harvest.yaml
      
  - name: validate
    command: sema-bench
    depends_on: harvest
```

### With sema-query

Query harvested data:

```bash
# Harvest data
sema-harvest --config harvest.yaml --dump harvested.ttl

# Query the harvested data
sema-query --source harvested.ttl --template_name analysis.sparql
```

## Troubleshooting

**Configuration not found:**
- Verify the config path with `--config`
- Ensure configuration files have `.yaml` or `.yml` extension
- Check file permissions

**Store connection failed:**
- Verify SPARQL endpoint URLs are correct
- Check that endpoint is accessible (try with curl)
- Ensure read and write URIs are properly specified

**Initialization files not loading:**
- Check file paths are absolute or relative to working directory
- Verify RDF file format is supported
- Check for syntax errors in RDF files

## Related Modules

- [Harvest Executor](./executor.py) - Harvesting execution engine
- [Harvest Service](./service.py) - Service implementation
- [Store Integration](../commons/store/) - Triple store interface

## See Also

- Test files: `tests/harvest/` for usage examples
- Service framework: `sema/commons/service/` for service patterns
- Configuration examples in test resources