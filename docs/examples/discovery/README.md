# sema-get discovery example assets

This folder provides ready-to-run assets referenced in `examples/discovery_example.py`.

## Contents
- `resource_uris.txt`: sample URIs for bulk discovery loops (DBpedia plus an unknown URI to pair with `--accept-zero`).
- `templates/extract.sparql`: simple FOAF query to use after discovery.
- `data/local_discovered.ttl`: a small local RDF sample you can query without hitting the network.
- `logging.yml`: optional logging configuration for `--logconf`.
- Output locations created for you: `discovered/`, `logs/`, and `results/`.

## How to try the examples
Run commands from `examples/discovery` so relative paths align with the examples in `discovery_example.py`.

### Basic discovery
Use the project virtualenv’s python to invoke the module directly (mirrors how the examples were tested):
```bash
python -m sema.discovery "https://dbpedia.org/resource/Python_(programming_language)" \
  --output discovered/python.ttl \
  --request-mimes text/turtle,application/ld+json

# Specify MIME priorities and JSON-LD output
python -m sema.discovery "https://dbpedia.org/resource/Python_(programming_language)" \
  --request-mimes text/turtle,application/ld+json \
  --output discovered/python.jsonld \
  --format json-ld
```

### Discovery with tracing and store targets
```bash
python -m sema.discovery "https://dbpedia.org/resource/Belgium" \
  --request-mimes text/turtle,application/ld+json \
  --output discovered/belgium.ttl \
  --trace logs/belgium_trace.txt \
  --logconf logging.yml

# Optional: send to a triple store (adjust URIs to your endpoint)
# python -m sema.discovery "https://example.org/resource/123" \
#   --read-uri http://localhost:7200/repositories/myrepo \
#   --write-uri http://localhost:7200/repositories/myrepo/statements \
#   --graph http://example.org/discovered/resource123
```

### Bulk discovery loop (from the example script)
```bash
for uri in $(cat resource_uris.txt); do
  fname=$(echo $uri | md5sum | cut -d' ' -f1)
  python -m sema.discovery "$uri" --output "discovered/${fname}.ttl" --accept-zero
done
```

### Discover then query
If you don’t want to rely on live HTTP discovery, use the local sample graph:
```bash
# Query the bundled sample graph
sema-query \
  --source data/local_discovered.ttl \
  --template_folder templates \
  --template_name extract.sparql \
  --output_location results/local_people.csv
```

To follow the exact flow from `discovery_example.py`, swap `data/local_discovered.ttl` with a file you obtained via `sema-get` (e.g., `discovered/python.ttl`).
