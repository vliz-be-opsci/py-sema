# py-sema Examples

This directory contains practical examples demonstrating how to use py-sema for various RDF data manipulation tasks.

## Available Examples

### 1. Simple SPARQL Query (`simple_query.py`)

Learn how to:
- Load RDF data from files or SPARQL endpoints
- Execute SPARQL queries
- Use SPARQL templates with Jinja2

**Run:**
```bash
python examples/simple_query.py
```

### 2. RDF Data Harvesting (`harvest_example.py`)

Learn how to:
- Harvest RDF data from various sources
- Use the `sema-harvest` CLI tool
- Implement programmatic harvesting

**Run:**
```bash
python examples/harvest_example.py
```

### 3. SHACL Validation (`validation_example.py`)

Learn how to:
- Validate RDF data using SHACL shapes
- Use the `sema-bench` CLI tool
- Create SHACL shape definitions
- Fix validation errors

**Run:**
```bash
python examples/validation_example.py
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

## Example Data

Some examples reference RDF data files. You can:
- Use your own RDF data files (Turtle, RDF/XML, N-Triples)
- Find sample RDF data in the `tests/` directory
- Download RDF datasets from public sources

## CLI Tools Quick Reference

py-sema provides several CLI tools that are demonstrated in these examples:

| Command | Purpose | Example |
|---------|---------|---------|
| `sema-query` | Execute SPARQL queries | `sema-query --source data.ttl` |
| `sema-harvest` | Harvest RDF data | `sema-harvest --source url` |
| `sema-bench` | SHACL validation | `sema-bench --data data.ttl --shapes shapes.ttl` |
| `sema-syncfs` | File synchronization | `sema-syncfs --help` |
| `sema-get` | Discovery operations | `sema-get --help` |

Run any command with `--help` to see all available options.

## Learning Path

Recommended order for beginners:

1. **Start with `simple_query.py`** - Understand basic RDF querying
2. **Try `validation_example.py`** - Learn about data quality with SHACL
3. **Explore `harvest_example.py`** - Collect RDF data from sources
4. **Check the module READMEs** - Deep dive into specific modules
5. **Review test files** - See real-world usage in `tests/` directory

## Need Help?

- **Documentation:** See the main [README.md](../README.md)
- **Contributing:** See [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Issues:** Report problems at https://github.com/vliz-be-opsci/py-sema/issues
- **Module docs:** Each module has its own README in `sema/*/README.md`

## Contributing Examples

Have a useful example to share? Please contribute!

1. Create a well-commented Python script
2. Add a description to this README
3. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.
