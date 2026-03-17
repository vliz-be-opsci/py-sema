# sema-get: RDF Discovery Service

`sema-get` (also known as `sema-discovery`) discovers and retrieves structured RDF content associated with a subject URI.

## Overview

The discovery module provides:
- Automatic RDF content discovery from subject URIs
- Content negotiation with configurable MIME types
- Integration with triple stores for discovered data
- Trace logging for provenance and debugging
- Support for multiple discovery techniques

## Installation

```bash
poetry install
# Or for development
poetry install --with dev --with tests
```

## Command-Line Usage

```bash
sema-get <url> [options]
# or
sema-get --url <url> [options]
```

### Positional Arguments

- `URL`: The subject URI to discover (can also use `--url`)

### Optional Arguments

- `-u, --url URL`: The subject URI to discover (alternative to positional)
- `-m, --request-mimes MIME`: Comma-separated list of acceptable MIME types (can be repeated)
- `-r, --read-uri URI`: Read URI to triple store
- `-w, --write-uri URI`: Write URI to triple store
- `-g, --graph URI`: Named graph to use in the triple store
- `-o, --output FILE`: Output file path (use `-` for stdout)
- `-f, --format FORMAT`: Output RDF format (turtle, xml, json-ld, etc.)
- `-z, --accept-zero`: Accept zero triples as success (don't fail on empty results)
- `-t, --trace PATH`: Location to store discovery trace/provenance
- `-l, --logconf LOGCONF`: Path to logging configuration file

## Usage Examples

### Basic Discovery

Discover RDF data for a URI:

```bash
sema-get https://example.org/resource/123
```

### Save to File

```bash
sema-get https://example.org/resource/123 --output discovered.ttl
```

### Output to stdout

```bash
sema-get https://example.org/resource/123 --output -
```

### Specify Output Format

```bash
sema-get https://example.org/resource/123 \
  --output discovered.jsonld \
  --format json-ld
```

### Request Specific MIME Types

```bash
sema-get https://example.org/resource/123 \
  --request-mimes text/turtle,application/rdf+xml \
  --output discovered.ttl
```

### Store in Triple Store

```bash
sema-get https://example.org/resource/123 \
  --read-uri http://localhost:7200/repositories/myrepo \
  --write-uri http://localhost:7200/repositories/myrepo/statements \
  --graph http://example.org/discovered
```

### Enable Discovery Tracing

```bash
sema-get https://example.org/resource/123 \
  --output discovered.ttl \
  --trace trace/discovery_log.txt
```

### Accept Zero Results

```bash
# Don't fail if no RDF data is found
sema-get https://example.org/unknown \
  --accept-zero \
  --output result.ttl
```

### Complete Example

```bash
sema-get https://example.org/person/alice \
  --request-mimes text/turtle,application/ld+json \
  --output discovered/alice.ttl \
  --format turtle \
  --trace logs/alice_discovery.txt \
  --logconf logging.yml
```

## Programmatic Usage

```python
from sema.discovery import DiscoveryService

# Create discovery service
service = DiscoveryService(
    subject_uri="https://example.org/resource/123",
    accept_mimes=["text/turtle", "application/rdf+xml"]
)

# Discover RDF data
graph = service.discover()

# Save discovered data
graph.serialize("discovered.ttl", format="turtle")
```

### With Triple Store

```python
from sema.discovery import DiscoveryService

# Configure with triple store
service = DiscoveryService(
    subject_uri="https://example.org/resource/123",
    read_uri="http://localhost:7200/repositories/myrepo",
    write_uri="http://localhost:7200/repositories/myrepo/statements",
    graph_uri="http://example.org/discovered"
)

# Discover and store
service.discover_and_store()
```

## Discovery Techniques

sema-get employs multiple discovery techniques:

1. **Direct Content Negotiation**: Request RDF formats directly from the URI
2. **Link Following**: Follow `rdfs:seeAlso`, `owl:sameAs`, and similar links
3. **Well-Known Locations**: Check for common RDF locations (`.well-known/void`, etc.)
4. **Semantic Sitemaps**: Discover via sitemap.xml
5. **VoID Descriptions**: Use VoID (Vocabulary of Interlinked Datasets) descriptions

## MIME Type Configuration

### Common RDF MIME Types

```bash
# Turtle
sema-get <uri> --request-mimes text/turtle

# RDF/XML
sema-get <uri> --request-mimes application/rdf+xml

# JSON-LD
sema-get <uri> --request-mimes application/ld+json

# N-Triples
sema-get <uri> --request-mimes application/n-triples

# Multiple types (try in order)
sema-get <uri> --request-mimes text/turtle,application/rdf+xml,application/ld+json
```

## Output Formats

Supported output formats via `--format`:
- `turtle` / `ttl` - Turtle (default)
- `xml` / `rdf` - RDF/XML
- `json-ld` / `jsonld` - JSON-LD
- `nt` / `ntriples` - N-Triples
- `n3` - Notation3

## Discovery Tracing

Enable tracing to debug discovery process:

```bash
sema-get <uri> --trace discovery.log
```

Trace file includes:
- Attempted discovery techniques
- HTTP requests and responses
- Found URIs and their sources
- Success/failure of each technique

## Best Practices

1. **Specify MIME types** to prioritize preferred formats
2. **Use tracing** when debugging discovery issues
3. **Accept zero results** for optional discoveries that may not exist
4. **Store in named graphs** to track provenance of discovered data
5. **Configure timeouts** appropriately for slow-responding URIs

## Common Use Cases

### Discover Linked Data

```bash
sema-get https://dbpedia.org/resource/Python_(programming_language) \
  --output python.ttl
```

### Bulk Discovery

```bash
# Discover multiple resources
for uri in $(cat uris.txt); do
  sema-get "$uri" --output "discovered/$(basename $uri).ttl"
done
```

### Integration with Query

```bash
# Discover data then query it
sema-get https://example.org/resource/123 --output temp.ttl
sema-query --source temp.ttl --template_name analysis.sparql
```

## Troubleshooting

**No RDF data found:**
- Check that the URI is accessible
- Verify the URI supports content negotiation
- Try different MIME types with `--request-mimes`
- Enable tracing to see what was attempted

**Connection errors:**
- Verify network connectivity
- Check for firewalls or proxy settings
- Increase timeout if needed

**Format errors:**
- Ensure the requested format is supported by the source
- Try alternative MIME types
- Check trace logs for actual returned content types

## Integration with Other Services

### With sema-harvest

Discover and harvest in one workflow:

```bash
# Discover resources
sema-get <uri> --output discovered.ttl

# Harvest into store
sema-harvest --init discovered.ttl --config harvest.yaml
```

### With sema-bench

Orchestrate discovery tasks:

```yaml
# sembench.yaml
services:
  - name: discover_resources
    command: sema-get
    args:
      - https://example.org/dataset
      - --output
      - discovered/dataset.ttl
```

## Related Modules

- [Discovery Service](./discovery.py) - Core discovery implementation
- [Content Negotiation](../commons/web/conneg.py) - HTTP content negotiation
- [RDF Store](../commons/store/) - Triple store interface

## See Also

- Test files: `tests/discovery/` for usage examples
- [Linked Data principles](https://www.w3.org/DesignIssues/LinkedData.html)
- [Content Negotiation spec](https://www.w3.org/Protocols/rfc2616/rfc2616-sec12.html)