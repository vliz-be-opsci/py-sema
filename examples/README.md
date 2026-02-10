# py-sema Examples

This directory contains practical examples demonstrating how to use py-sema for various RDF data manipulation tasks.

## Available Examples

### Core Modules

#### 1. SPARQL Query (`simple_query.py`)

Learn how to:
- Query RDF data using sema-query CLI
- Use SPARQL templates with Jinja2
- Execute queries programmatically

**Run:**
```bash
python examples/simple_query.py
```

#### 2. Task Orchestration (`bench_orchestration.py`)

Learn how to:
- Orchestrate multiple services with sema-bench
- Configure SHACL validation workflows
- Use task scheduling and file watching

**Run:**
```bash
python examples/bench_orchestration.py
```

#### 3. RDF Harvesting (`harvest_example.py`)

Learn how to:
- Harvest RDF data from various sources
- Configure harvesting workflows
- Use the sema-harvest CLI tool

**Run:**
```bash
python examples/harvest_example.py
```

#### 4. RDF Discovery (`discovery_example.py`)

Learn how to:
- Discover RDF data from URIs using sema-get
- Use content negotiation
- Enable discovery tracing

**Run:**
```bash
python examples/discovery_example.py
```

#### 5. Template-Based Generation (`subyt_templating.py`)

Learn how to:
- Generate RDF from CSV/JSON using templates
- Use Jinja2 filters for RDF generation
- Apply templates to multiple data sets

**Run:**
```bash
python examples/subyt_templating.py
```

#### 6. Filesystem Synchronization (`syncfs_example.py`)

Learn how to:
- Sync RDF files to triple stores
- Manage named graphs
- Organize RDF file structures

**Run:**
```bash
python examples/syncfs_example.py
```

#### 7. SHACL Validation (`validation_example.py`)

Learn how to:
- Validate RDF data using SHACL shapes
- Use the sema-bench CLI tool
- Create SHACL shape definitions

**Run:**
```bash
python examples/validation_example.py
```

#### 8. RO-Crate Creation (`rocrate_example.py`)

Learn how to:
- Create RO-Crate metadata from YAML
- Package research objects
- Use environment variables in configurations

**Run:**
```bash
python examples/rocrate_example.py
```

#### 9. RO-Crate Assets (`examples/ro/`)

Learn how to:
- Run RO-Crate creation on ready-made sample crates
- Use explicit entries vs glob-driven crates
- Resolve environment variables in `roc-me.yml`

**Run:**
```bash
python -m sema.ro.creator ./examples/ro/basic --force
python -m sema.ro.creator ./examples/ro/globbed --force --load-os-env
```

## Prerequisites

Before running the examples, ensure you have:

1. **Installed py-sema:**
   ```bash
   poetry install
   # or
   pip install -e .
   ```

2. **Activated the virtual environment:**
   ```bash
   poetry shell
   # or activate your venv
   ```

## Example Categories

### Data Input & Generation
- `subyt_templating.py` - Convert structured data to RDF
- `discovery_example.py` - Discover and retrieve RDF from URIs

### Data Processing
- `simple_query.py` - Query RDF data with SPARQL
- `validation_example.py` - Validate RDF with SHACL

### Data Management
- `harvest_example.py` - Harvest RDF from sources
- `syncfs_example.py` - Synchronize files to triple stores

### Orchestration & Packaging
- `bench_orchestration.py` - Orchestrate multiple services
- `rocrate_example.py` - Package research objects
- `examples/ro/` - RO-Crate assets and blueprints

## CLI Tools Quick Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `sema-query` | Execute SPARQL queries | `sema-query --source data.ttl` |
| `sema-harvest` | Harvest RDF data | `sema-harvest --config config.yaml` |
| `sema-bench` | Task orchestration & SHACL | `sema-bench --config-path config/` |
| `sema-get` | Discover RDF from URIs | `sema-get https://example.org/resource` |
| `sema-subyt` | Generate RDF from templates | `sema-subyt --name template --input data.csv` |
| `sema-syncfs` | Sync files to triple store | `sema-syncfs --root rdf/ --store <endpoint>` |
| `sema-roc` | Create RO-Crate metadata | `sema-roc /path/to/rocrate` |

Run any command with `--help` to see all available options.

## Learning Path

Recommended order for beginners:

1. **Start with `simple_query.py`** - Understand basic RDF querying
2. **Try `validation_example.py`** - Learn about data quality with SHACL
3. **Explore `subyt_templating.py`** - Generate RDF from structured data
4. **Review `discovery_example.py`** - Discover RDF from web resources
5. **Try `harvest_example.py`** - Collect RDF data from sources
6. **Experiment with `syncfs_example.py`** - Manage RDF in triple stores
7. **Learn `bench_orchestration.py`** - Orchestrate complex workflows
8. **Explore `rocrate_example.py`** - Package research outputs
9. **Check the module READMEs** - Deep dive into specific modules
10. **Review test files** - See real-world usage in `tests/` directory

## Example Data

Some examples reference RDF data files. You can:
- Use your own RDF data files (Turtle, RDF/XML, N-Triples, JSON-LD)
- Find sample RDF data in the `tests/` directory
- Download RDF datasets from public sources like DBpedia, Wikidata, etc.

## Complete Workflow Example

Here's how the tools work together in a typical workflow:

```bash
# 1. Discover external RDF data
sema-get https://example.org/dataset --output external.ttl

# 2. Generate local RDF from CSV
sema-subyt --name people --input people.csv --output local.ttl

# 3. Combine and sync to triple store
mkdir rdf && mv *.ttl rdf/
sema-syncfs --root rdf/ --base http://example.org/ --store <endpoint>

# 4. Validate with SHACL
sema-bench --config-path validation/ --config-name shapes.yaml

# 5. Query and extract results
sema-query --source <endpoint> --template_name report.sparql --output results.csv

# 6. Package as RO-Crate for publication
sema-roc --force
```

## Integration Examples

### Data Pipeline

```bash
# Harvest → Validate → Query → Export
sema-harvest --config harvest.yaml --dump data.ttl
sema-bench --config-path validation/
sema-query --source data.ttl --template_name analysis.sparql
```

### Incremental Updates

```bash
# Generate only if source changed
sema-subyt --name template --input data.csv --output rdf.ttl --conditional

# Sync to store
sema-syncfs --root . --store <endpoint>
```

### Continuous Monitoring

```bash
# Watch and re-run on changes
sema-bench --config-path monitoring/ --watch --interval 60
```

## Need Help?

- **Documentation:** See the main [README.md](../README.md)
- **Contributing:** See [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Issues:** Report problems at https://github.com/vliz-be-opsci/py-sema/issues
- **Module docs:** Each module has its own README in `sema/*/README.md`:
  - [sema-bench](../sema/bench/README.md) - Task orchestration
  - [sema-query](../sema/query/README.md) - SPARQL queries
  - [sema-harvest](../sema/harvest/README.md) - Data harvesting
  - [sema-get](../sema/discovery/README.md) - RDF discovery
  - [sema-subyt](../sema/subyt/README.md) - Template-based generation
  - [sema-syncfs](../sema/syncfs/README.md) - Filesystem sync
  - [sema-roc](../sema/ro/README.md) - RO-Crate creation

## Contributing Examples

Have a useful example to share? Please contribute!

1. Create a well-commented Python script showing a specific use case
2. Add a description to this README under the appropriate category
3. Test your example to ensure it runs correctly
4. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.
