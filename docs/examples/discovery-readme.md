# Discovery Examples

Canonical source README:
<https://github.com/vliz-be-opsci/py-sema/blob/main/examples/discovery/README.md>

## What this example covers

- Discover RDF from resource URIs with `sema.discovery`.
- Control requested MIME types and output formats.
- Capture tracing logs and run post-discovery queries.

## Key assets

- URI list: `examples/discovery/resource_uris.txt`
- Templates: `examples/discovery/templates/extract.sparql`
- Local sample graph: `examples/discovery/data/local_discovered.ttl`

## Quick start

```bash
python -m sema.discovery "https://dbpedia.org/resource/Python_(programming_language)" \
	--output examples/discovery/discovered/python.ttl \
	--request-mimes text/turtle,application/ld+json
```

## Query the local sample graph

```bash
sema-query \
	--source examples/discovery/data/local_discovered.ttl \
	--template_folder examples/discovery/templates \
	--template_name extract.sparql \
	--output_location examples/discovery/results/local_people.csv
```

## Notes

- This example may require network access depending on source URIs.
- Use `--accept-zero` in batch loops when some URIs may fail discovery.
