# sema-syncfs: Filesystem to Triple Store Synchronization

`sema-syncfs` synchronizes a filesystem with a triple store, automatically loading RDF files into named graphs based on their location.

## Overview

The syncfs module provides:
- Automatic synchronization of RDF files to triple stores
- File watching for real-time updates
- Named graph management based on file paths
- Support for multiple RDF formats
- Configurable base URIs for named graphs

## Installation

```bash
poetry install
# Or for development
poetry install --with dev --with tests
```

## Command-Line Usage

```bash
sema-syncfs --root <folder> --store <read_uri> <write_uri> [options]
```

### Required Arguments

- `-r, --root ROOT_FOLDER/`: Path to the root folder containing RDF files to synchronize
- `-s, --store ENDPOINT [ENDPOINT ...]`: Pair of read_uri and write_uri for the SPARQL endpoint

### Optional Arguments

- `-b, --base BASE`: URI baseref (prefix) for associated named graphs (default: `urn:sync:`)
- `-l, --logconf LOGCONF`: Path to logging configuration file

## Usage Examples

### Basic Synchronization

```bash
sema-syncfs \
  --root /path/to/rdf/files \
  --store http://localhost:7200/repositories/myrepo \
          http://localhost:7200/repositories/myrepo/statements
```

### With Custom Base URI

```bash
sema-syncfs \
  --root /data/rdf \
  --base http://example.org/graphs/ \
  --store http://localhost:7200/repositories/myrepo \
          http://localhost:7200/repositories/myrepo/statements
```

### Complete Example

```bash
sema-syncfs \
  --root /project/rdf/data \
  --base http://example.org/sync/ \
  --store http://localhost:7200/repositories/knowledge \
          http://localhost:7200/repositories/knowledge/statements \
  --logconf logging.yml
```

## How It Works

### File to Named Graph Mapping

Files in the root folder are automatically mapped to named graphs:

```
/root/data/persons.ttl     → <base>data/persons.ttl
/root/data/orgs/main.ttl   → <base>data/orgs/main.ttl
/root/schema.ttl           → <base>schema.ttl
```

With `--base http://example.org/sync/`:
- `/root/data/persons.ttl` → `http://example.org/sync/data/persons.ttl`

### Synchronization Behavior

1. **Initial Sync**: All RDF files in root folder are loaded into corresponding named graphs
2. **Watch Mode**: Changes to files trigger automatic re-synchronization
3. **Deletions**: Removed files result in deleted named graphs
4. **Updates**: Modified files update their corresponding named graphs

## Programmatic Usage

```python
from sema.syncfs import SyncFsTriples

# Configure synchronization
sync = SyncFsTriples(
    root_folder="/path/to/rdf/files",
    base_uri="http://example.org/sync/",
    read_uri="http://localhost:7200/repositories/myrepo",
    write_uri="http://localhost:7200/repositories/myrepo/statements"
)

# Run initial synchronization
sync.sync_all()

# Watch for changes (blocking)
sync.watch()
```

### One-Time Sync

```python
from sema.syncfs import SyncFsTriples

sync = SyncFsTriples(
    root_folder="/data/rdf",
    base_uri="http://example.org/graphs/",
    read_uri="http://localhost:7200/repositories/myrepo",
    write_uri="http://localhost:7200/repositories/myrepo/statements"
)

# Sync once without watching
sync.sync_all()
```

## Supported File Formats

- Turtle (`.ttl`)
- RDF/XML (`.rdf`, `.xml`)
- N-Triples (`.nt`)
- JSON-LD (`.jsonld`)
- Notation3 (`.n3`)

## Filesystem Organization

Organize RDF files by domain or type:

```
root/
├── schemas/
│   ├── person.ttl
│   └── organization.ttl
├── data/
│   ├── persons/
│   │   ├── alice.ttl
│   │   └── bob.ttl
│   └── orgs/
│       └── acme.ttl
└── metadata/
    └── provenance.ttl
```

Each file syncs to its own named graph, preserving the directory structure.

## Use Cases

### 1. Development Environment

Automatically sync local RDF files to a development triple store:

```bash
sema-syncfs \
  --root ./rdf \
  --base http://dev.example.org/ \
  --store http://localhost:7200/repositories/dev \
          http://localhost:7200/repositories/dev/statements
```

### 2. Data Pipeline

Sync generated RDF files to production store:

```bash
# Generate RDF files
sema-subyt --name gen --input data.csv --output rdf/output.ttl

# Sync to store
sema-syncfs \
  --root rdf/ \
  --base http://example.org/data/ \
  --store http://triplestore:7200/repositories/prod \
          http://triplestore:7200/repositories/prod/statements
```

### 3. Multi-Domain Knowledge Graph

Organize different domains in subdirectories:

```bash
sema-syncfs \
  --root /knowledge-base \
  --base http://example.org/kb/ \
  --store http://localhost:7200/repositories/kb \
          http://localhost:7200/repositories/kb/statements
```

## Best Practices

1. **Organize files by domain** - Use subdirectories to group related RDF files
2. **Use consistent naming** - Follow a naming convention for files and graphs
3. **Set meaningful base URIs** - Use URIs that reflect your data organization
4. **Monitor sync logs** - Configure logging to track sync operations
5. **Test in development first** - Verify sync behavior before production use
6. **Use named graphs wisely** - Consider query performance with many small graphs

## Named Graph Queries

Query synchronized data using named graphs:

```sparql
# Query specific graph
SELECT ?s ?p ?o
FROM <http://example.org/sync/data/persons.ttl>
WHERE {
    ?s ?p ?o .
}

# Query across multiple graphs
SELECT ?s ?p ?o
FROM <http://example.org/sync/data/persons.ttl>
FROM <http://example.org/sync/data/orgs/main.ttl>
WHERE {
    ?s ?p ?o .
}

# Query all synced graphs
SELECT ?g ?s ?p ?o
WHERE {
    GRAPH ?g {
        ?s ?p ?o .
        FILTER(STRSTARTS(STR(?g), "http://example.org/sync/"))
    }
}
```

## Integration with Other Services

### With sema-subyt

Generate and sync RDF files:

```bash
# Generate RDF from templates
sema-subyt --name template --input data.csv --output rdf/{id}.ttl

# Sync generated files
sema-syncfs --root rdf/ --store <read> <write>
```

### With sema-bench

Orchestrate sync as part of a pipeline:

```yaml
# sembench.yaml
services:
  - name: sync_rdf
    command: sema-syncfs
    args:
      - --root
      - /data/rdf
      - --base
      - http://example.org/sync/
      - --store
      - http://localhost:7200/repositories/myrepo
      - http://localhost:7200/repositories/myrepo/statements
```

## Troubleshooting

**Files not syncing:**
- Verify root folder path exists
- Check file extensions match supported formats
- Ensure files contain valid RDF syntax
- Check SPARQL endpoint connectivity

**Named graph conflicts:**
- Verify base URI is appropriate
- Check for duplicate file paths
- Ensure write permissions on triple store

**Performance issues:**
- Consider batch size for large directories
- Monitor triple store memory usage
- Use appropriate query patterns for named graphs

**Connection errors:**
- Verify SPARQL endpoint URLs
- Check network connectivity
- Ensure read and write URIs are correct
- Verify triple store authentication if required

## Advanced Configuration

### Custom File Patterns

Filter which files to sync by organizing them:

```
root/
├── active/      # Sync these
│   └── data.ttl
└── archive/     # Don't sync these
    └── old.ttl
```

### Logging Configuration

Create `logging.yml`:

```yaml
version: 1
loggers:
  sema.syncfs:
    level: DEBUG
    handlers: [console, file]
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
  file:
    class: logging.FileHandler
    filename: syncfs.log
    level: DEBUG
```

Use with:

```bash
sema-syncfs --root /data --store <read> <write> --logconf logging.yml
```

## Related Modules

- [SyncFsTriples](./syncfs.py) - Core synchronization implementation
- [File System Utils](../commons/path/) - Path manipulation
- [Store Interface](../commons/store/) - Triple store integration

## See Also

- Test files: `tests/syncfs/` for usage examples
- SPARQL endpoint documentation for your triple store
- Named graphs in SPARQL: [SPARQL 1.1 spec](https://www.w3.org/TR/sparql11-query/#namedGraphs)